# Faithfulness check: an LLM reads the tool results and the answer, and says whether
# every fact in the answer is backed by the tool results. A different model from the
# assistant is used so it doesn't grade its own answers.
import os

from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

from app.core import config
from app.core.companies import COMPANIES
from app.utils.cost import cost_usd

JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gpt-6-luna")

PROMPT = """You are checking the answer of an ERP help assistant.

Question:
{question}

The assistant also knows the company names: {companies}

Tool results the assistant used:
{context}

Answer:
{answer}

Is every fact in the answer (numbers, limits, names, steps, document names) supported by the tool results?
Saying the information is not available is supported when the tool results do not contain it.
Saying the user has no access is supported when a tool result says ACCESS DENIED."""


class Verdict(BaseModel):
    faithful: bool = Field(description="True if every fact in the answer is supported by the tool results")
    reason: str = Field(description="One short sentence. Name any claim that is not supported.")


def get_judge():
    llm = init_chat_model(
        JUDGE_MODEL,
        model_provider="openai",
        use_responses_api=True,
        timeout=config.LLM_TIMEOUT,
        max_retries=config.LLM_MAX_RETRIES,
    )
    return llm.with_structured_output(Verdict, include_raw=True)


def judge_answer(judge, question, answer, context):
    # returns (faithful, reason, cost); faithful is None when there is nothing to judge
    if not context:
        return None, "refused before the LLM, nothing to judge", 0.0

    companies = ", ".join(f"{code} = {name}" for code, name in COMPANIES.items())
    prompt = PROMPT.format(question=question, companies=companies,
                           context="\n\n---\n\n".join(context), answer=answer)
    out = judge.invoke(prompt)

    usage = out["raw"].usage_metadata or {}
    cost = cost_usd(JUDGE_MODEL, usage.get("input_tokens", 0), usage.get("output_tokens", 0))

    verdict = out["parsed"]
    if verdict is None:
        return None, "judge reply could not be read", cost
    return verdict.faithful, verdict.reason, cost
