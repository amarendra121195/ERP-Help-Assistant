import time
from datetime import date
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from app.core import config
from app.core.companies import company_label
from app.core.logger import log_request
from app.llm.chat_model import get_chat_model
from app.llm.prompts import REFUSAL_MESSAGE, SYSTEM_PROMPT
from app.services.access import blocked_companies, get_allowed_companies
from app.tools.registry import DATA_TOOLS, DOCUMENT_TOOLS, build_tools
from app.utils.cost import cost_usd, count_tokens

EMPTY_USAGE = {"input_tokens": 0, "output_tokens": 0, "embedding_tokens": 0, "cost_usd": 0.0}


def ask(user_id, question):
    start = time.time()
    allowed = get_allowed_companies(user_id)
    log = {"user_id": user_id, "question": question, "allowed_companies": allowed}

    # question is about a company the user can't see -> refuse without calling the LLM
    blocked = blocked_companies(question, allowed)
    if blocked:
        answer = REFUSAL_MESSAGE.format(
            blocked=", ".join(company_label(c) for c in blocked),
            allowed=", ".join(company_label(c) for c in allowed),
        )
        result = {"answer": answer, "sources": [], "route": "refused", "usage": dict(EMPTY_USAGE)}
        log_request({**log, **result, "tools_used": [], "documents_retrieved": [], "sql": [],
                     "latency_ms": int((time.time() - start) * 1000)})
        return result

    tools, trace = build_tools(allowed)
    run = run_agent(question, allowed, tools)
    answer, tools_used = run["answer"], run["tools_used"]

    route = get_route(tools_used)
    sources = get_sources(answer, trace.documents)
    if "data" in route and trace.queries:
        sources.append(f"SQL Server: arete_group.{config.PO_TABLE}")

    embedding_tokens = sum(count_tokens(t["args"].get("query", ""))
                           for t in tools_used if t["tool"] in DOCUMENT_TOOLS)
    cost = cost_usd(config.CHAT_MODEL, run["input_tokens"], run["output_tokens"])
    cost += cost_usd(config.EMBEDDING_MODEL, embedding_tokens)

    result = {
        "answer": answer,
        "sources": sources,
        "route": route,
        "usage": {
            "input_tokens": run["input_tokens"],
            "output_tokens": run["output_tokens"],
            "embedding_tokens": embedding_tokens,
            "cost_usd": round(cost, 6),
        },
    }
    log_request({
        **log, **result,
        "model": config.CHAT_MODEL,
        "tools_used": tools_used,
        "documents_retrieved": trace.documents,
        "sql": trace.queries,
        "latency_ms": int((time.time() - start) * 1000),
    })

    # extra fields for the evaluation; the API response model leaves them out
    result["documents_retrieved"] = trace.documents
    result["context"] = run["context"]
    return result


def run_agent(question, allowed, tools):
    tools_by_name = {t.name: t for t in tools}
    llm = get_chat_model()
    # first call must use a tool, so the answer always comes from the documents or the data
    llm_first = llm.bind_tools(tools, tool_choice="required")
    llm_with_tools = llm.bind_tools(tools)

    companies = ", ".join(company_label(c) for c in allowed)
    prompt = SYSTEM_PROMPT.format(today=date.today().isoformat(), companies=companies)
    messages = [SystemMessage(prompt), HumanMessage(question)]

    tools_used = []
    context = []  # tool outputs the LLM saw
    input_tokens = output_tokens = 0

    for i in range(config.MAX_TOOL_ROUNDS + 1):
        if i == 0:
            model = llm_first
        elif i < config.MAX_TOOL_ROUNDS:
            model = llm_with_tools
        else:
            model = llm  # last round, no tools - just answer

        response = model.invoke(messages)
        messages.append(response)
        if response.usage_metadata:
            input_tokens += response.usage_metadata["input_tokens"]
            output_tokens += response.usage_metadata["output_tokens"]

        if not response.tool_calls:
            break

        for call in response.tool_calls:
            tools_used.append({"tool": call["name"], "args": call["args"]})
            try:
                output = tools_by_name[call["name"]].invoke(call["args"])
            except Exception as e:
                # send the error back so the LLM can fix its arguments
                output = f"Tool error: {e}"
            context.append(str(output))
            messages.append(ToolMessage(content=str(output), tool_call_id=call["id"]))

    return {
        "answer": response.text.strip(),
        "tools_used": tools_used,
        "context": context,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }


def get_route(tools_used):
    names = {t["tool"] for t in tools_used}
    routes = []
    if names & DOCUMENT_TOOLS:
        routes.append("documents")
    if names & DATA_TOOLS:
        routes.append("data")
    return "+".join(routes) or "none"


def get_sources(answer, documents):
    # only the documents the answer actually mentions
    return [doc for doc in documents if doc in answer or Path(doc).stem in answer]
