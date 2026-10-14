# ERP Help Assistant

A small assistant for a group that runs Microsoft Dynamics 365 Finance & Operations for three companies.
It answers two kinds of questions through one endpoint, `POST /ask`:

| Kind | Example | How it is answered |
|---|---|---|
| How-to and policy | "How do I create a purchase order against a project WBS?" | RAG over the documents (Chroma + OpenAI embeddings), naming the source file |
| Data | "What is the total value of open POs for Project Riverside?" | SQL query on the PO register in SQL Server. The numbers come from SQL, never from the LLM |

The LLM (OpenAI, through LangChain) decides which kind a question is by choosing a tool.
Every user sees only their own companies. Access is applied **inside** the document search and the SQL
queries, before the LLM sees anything.

Built with LangChain: `init_chat_model` from `langchain` loads the chat model (`gpt-5.6-luna`), and
`langchain-core`, `langchain-openai`, `langchain-chroma` and `langchain-text-splitters` do the rest. No LangGraph is
used. The `langchain` package installs `langgraph` as one of its own dependencies, but the code never imports it.

## How it works

```
POST /ask {user_id, question}                                    api/routes.py
   │
   ├─ 1. Access         services/access.py
   │     look up the user's companies in dbo.user_access (C01 / C02, C03 / All)
   │     question names a company they cannot see?  → polite refusal, nothing is searched
   │
   ├─ 2. Tools          tools/registry.py builds the tools for THIS user; the company filter is fixed inside each
   │     search_documents        tools/document_tools.py → rag/retriever.py (Chroma, user's companies + ALL, not superseded)
   │     get_po_total            tools/po_tools.py       → SQL SUM / COUNT
   │     list_purchase_orders    tools/po_tools.py       → SQL SELECT
   │     get_po_totals_grouped   tools/po_tools.py       → SQL GROUP BY vendor / company / project / status / ...
   │
   ├─ 3. Answer         services/assistant.py
   │     LLM (llm/chat_model.py + llm/prompts.py) picks a tool — its first reply must be a tool call —
   │     tools run, results go back, the LLM writes the answer from them only
   │
   └─ 4. Log            core/logger.py → logs/requests.jsonl
         user, route, tools + arguments, documents retrieved, SQL run, tokens, cost, latency
```

The documents are indexed once, before the API runs, by the RAG pipeline in `app/rag/`:

```
data/documents/  →  loader.py  →  splitter.py  →  embeddings.py  →  vector_store.py  →  vectorstore/
                    read PDF,      chunks with      OpenAI            Chroma on disk
                    Word, text;    document +       text-embedding-
                    tag company    company header   3-large
                                                                       retriever.py searches it at question time
```

The response:

```json
{
  "answer": "Total value of open POs for Project Riverside: **INR 33,34,200.00** (without GST) across **6 purchase orders**.",
  "sources": ["SQL Server: arete_group.dbo.purchase_order_lines"],
  "route": "data",
  "usage": {"input_tokens": 2355, "output_tokens": 84, "embedding_tokens": 0, "cost_usd": 0.000572}
}
```

`route` is `documents`, `data`, `documents+data`, or `refused` (the question named a company the user cannot see).
`sources` lists the documents the answer actually cites, or the SQL table for data answers.

## Project structure

```
Arete_Group/
├── app/
│   ├── main.py                     FastAPI entry point (uvicorn app.main:app)
│   ├── api/
│   │   ├── routes.py               POST /ask, GET /health, chat screen on GET /
│   │   └── schemas.py              request / response models
│   ├── core/
│   │   ├── config.py               all settings: paths, models, prices, chunk size; secrets come from .env
│   │   ├── companies.py            C01 / C02 / C03 and helpers to name them
│   │   └── logger.py               request log (logs/requests.jsonl)
│   ├── db/
│   │   └── sql_server.py           run_query(): parameterised SELECT on SQL Server
│   ├── rag/                        RAG pipeline, one step per file
│   │   ├── loader.py               read PDF / Word / text, tag company and superseded
│   │   ├── splitter.py             split into chunks
│   │   ├── embeddings.py           OpenAI embedding model
│   │   ├── vector_store.py         Chroma: open, rebuild
│   │   ├── retriever.py            search with the user's access filter
│   │   └── ingest.py               runs loader → splitter → vector store (python -m app.rag.ingest)
│   ├── tools/                      LangChain tools the LLM can call
│   │   ├── registry.py             build_tools(): all tools for one user
│   │   ├── document_tools.py       search_documents
│   │   ├── po_tools.py             get_po_total, list_purchase_orders, get_po_totals_grouped
│   │   ├── po_filters.py           tool arguments → SQL WHERE clause, status names, group-by columns
│   │   ├── schemas.py              tool arguments the LLM fills in
│   │   └── trace.py                documents and SQL used, for the log
│   ├── llm/
│   │   ├── chat_model.py           init_chat_model("gpt-5.6-luna")
│   │   └── prompts.py              system prompt and refusal message
│   ├── services/
│   │   ├── access.py               user → allowed companies; companies named in a question
│   │   └── assistant.py            ask(): access check, tool-calling loop, route, sources, cost
│   ├── utils/
│   │   ├── formatting.py           Indian number format (33,34,200)
│   │   └── cost.py                 token count and cost
│   └── static/index.html           simple chat screen
├── data/
│   ├── documents/                  the 9 documents, one folder per company + "Common - All Companies"
│   ├── sql/arete_group.sql         creates the database: user access (3 users) and PO register (40 lines)
│   └── Read me.txt                 data pack notes
├── tests/
│   ├── unit/                       19 fast tests, no OpenAI calls (pytest)
│   └── evaluation/
│       ├── questions.json          24 questions with expected answers and checks
│       ├── run_eval.py             runs the questions and prints the scores
│       ├── metrics.py              answer checks, retrieval hit rate / MRR, summary
│       ├── judge.py                faithfulness check with a second LLM
│       ├── report.py               writes report.md
│       └── report.md               latest result
├── .env.example                    copy to .env and add your key (.env is git-ignored)
├── Dockerfile, .dockerignore
├── pyproject.toml                  project info and pytest settings
└── requirements.txt
```

Imports go one way only: `api → services → tools / llm → rag / db → core / utils`. A lower package never imports a
higher one, so each part can be read and changed on its own.
Generated folders, all git-ignored: `vectorstore/` (Chroma index) and `logs/` (request log).

## How to change things

| I want to... | Change |
|---|---|
| Use another chat or embedding model | `CHAT_MODEL` / `EMBEDDING_MODEL` in `.env`, and its price in `app/core/config.py` → `PRICES`. After a new embedding model, run `python -m app.rag.ingest`. |
| Change how the assistant answers | `app/llm/prompts.py` |
| Add or update documents | Put the file in `data/documents/<company folder>/`, then `python -m app.rag.ingest` |
| Read a new file type (e.g. `.xlsx`) | Add a reader function to `READERS` in `app/rag/loader.py` |
| Change chunk size or how many chunks are retrieved | `CHUNK_SIZE`, `CHUNK_OVERLAP`, `TOP_K` in `app/core/config.py` |
| Add a company | `COMPANIES` and `COMPANY_KEYWORDS` in `app/core/companies.py`, and a folder `Name (C04)` in `data/documents/` |
| Add a new data question type | Write a tool in `app/tools/po_tools.py` (or a new file in `app/tools/`), add it in `app/tools/registry.py` and its name to `DATA_TOOLS` |
| Add a PO filter (e.g. buyer) | A field in `app/tools/schemas.py` → `POFilters` and a clause in `app/tools/po_filters.py` → `build_where` |
| Point to another database | `SQL_SERVER_CONN` in `.env`; table names in `app/core/config.py` |

## Setup and run

Needs Python 3.12, SQL Server, ODBC Driver 17 for SQL Server, and an OpenAI API key.

```powershell
# create the arete_group database with both tables (skips tables that already exist, never overwrites)
sqlcmd -S localhost -E -C -i data\sql\arete_group.sql

conda create -n erp_assistant python=3.12 -y
conda activate erp_assistant
pip install -r requirements.txt

copy .env.example .env               # then put your OPENAI_API_KEY in .env

python -m app.rag.ingest             # build the vector index (about $0.0003)
uvicorn app.main:app --reload        # API on http://127.0.0.1:8000, docs on /docs
```

Ask a question:

```powershell
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" `
     -d '{\"user_id\": \"U01\", \"question\": \"What is the total value of open POs for Project Riverside?\"}'
```

Tests:

```powershell
pytest -q                                   # 19 unit tests, no OpenAI cost (SQL Server must be running)
python -m tests.evaluation.run_eval         # 24 questions + all metrics (about $0.02)
python -m tests.evaluation.run_eval --ids 1,2,3
python -m tests.evaluation.run_eval --no-judge   # skip the faithfulness judge
```

### Settings (.env)

| Variable | Default | Meaning |
|---|---|---|
| `OPENAI_API_KEY` | (required) | Your OpenAI key. Never put it in code. |
| `CHAT_MODEL` | `gpt-5.6-luna` | Answering model, loaded with `init_chat_model`. |
| `EMBEDDING_MODEL` | `text-embedding-3-large` | Embedding model. Re-run `python -m app.rag.ingest` after changing it. |
| `REASONING_EFFORT` | `low` | Leave it empty for models that do not support reasoning effort. |
| `SQL_SERVER_CONN` | localhost, `arete_group`, Windows login | ODBC connection string. |
| `JUDGE_MODEL` | `gpt-6-luna` | Model that checks faithfulness in the evaluation. Kept different from `CHAT_MODEL`. |

The model is called through the OpenAI **Responses API** (`use_responses_api=True`). With `gpt-5.6-luna`, the
Chat Completions API rejects tools combined with `reasoning_effort`.

Prices used for the cost log are in `app/core/config.py` (checked on developers.openai.com on 2026-10-14):
`gpt-5.6-luna` $0.20 / $1.20 per million input / output tokens, `text-embedding-3-large` $0.13 per million.

## Evaluation

`tests/evaluation/questions.json` has 24 questions: the 7 from the brief plus 17 more. Each has a category
(documents 11, data 7, access 3, not available 3), an expected answer, and checks. Every expected figure was checked
with SQL directly against the database.

### Metrics

| Metric | How it is measured |
|---|---|
| **Accuracy** | A question passes only if all its checks pass. Reported overall and per category. |
| Route correct | The assistant used documents, data or refused, as expected. |
| Required facts present | Exact figures and key facts are in the answer, e.g. `33,34,200`. |
| Forbidden content absent | No old limits, other companies' figures, or numbers inside a refusal. |
| Correct sources cited | The right document is named; nothing is cited when there is no answer. |
| Retrieval hit rate | For document questions, the expected document was among the retrieved chunks. |
| Retrieval MRR | Mean of 1 / rank of the first expected document (1.0 = always ranked first). |
| Faithfulness | A second model (`gpt-6-luna`) reads the tool results and the answer and says whether every fact is backed by them. Questions refused before the LLM are not judged. |
| Time, tokens, cost | Per question and in total, for the assistant and the judge separately. |

### Result (`gpt-5.6-luna`, 14-Oct-2026)

| Metric | Result |
|---|---|
| **Accuracy** | **24 / 24 (100%)**: documents 11/11, data 7/7, access 3/3, not available 3/3 |
| Checks | route 22/22, facts 32/32, forbidden 8/8, sources 13/13 |
| Retrieval | hit rate 11/11, MRR 0.91 (two questions found their document at rank 2) |
| Faithfulness | **21 / 22 (95%)** |
| Answer time | 4.5 s average, 7.1 s slowest |
| Cost | $0.016 assistant + $0.003 judge for the whole run |

The full table, with every answer, is in [tests/evaluation/report.md](tests/evaluation/report.md).

- **Faithfulness found a real weakness.** The first run with the judge scored 17 / 22. Three answers added small
  details from general knowledge, for example "raise a ticket if the error continues". The other two flags were
  the judge's mistake: it did not know the company names, which the assistant gets in its prompt. The prompt now
  says "do not add advice, steps or details that the tool results do not state", and the judge now gets the
  company names. The one remaining flag (Q9) says "bank letter on the vendor's letterhead" where the SOP only
  says "on letterhead".
- In one run the model passed `status = any` for the PackWell question, so the total included a canceled line
  (INR 9,51,300 instead of 9,16,500). It said so in the answer, but it broke the rule that canceled lines are not
  PO value. That rule is now in the system prompt too, and the status-related questions then passed 3 runs in a row.
  A refused question costs nothing because no LLM call is made.
- With the earlier model, `gpt-6.1-sol`, the same 24 questions also scored 24 / 24, at about 10x the cost ($0.155).
- The first full run (on `gpt-6.1-sol`) scored 23 / 24, and reading the answers turned up two problems:
  - The RCM answer was correct but repeated the same table for each company. Fixed in the prompt: an
    "All companies" document is answered once.
  - On the Plant 2 Upgrade question (a C02 project, asked by a C01 user), the LLM added `company = C01` on its own,
    so the access check did not fire. The answer only said "not available"; nothing leaked, but it passed the test
    by luck. Fixed: the check now ignores the company filter, the refusal tests look for wording such as "do not
    have access", and an offline test covers this case.
- These are keyword checks, so I also read every answer. LLM output varies a little between runs, so a later run
  may differ.

## Optional extras

### Chat screen

With the API running, open http://127.0.0.1:8000/. Pick a test user, ask a question, and see the answer with its
route, sources, tokens and cost. It is a single HTML file, [app/static/index.html](app/static/index.html), with no
build step.

### Docker

> Written but **not built or run yet**: Docker Desktop was not running on the development laptop.

A Linux container cannot use Windows login for SQL Server, so it needs a SQL login. Enable TCP/IP and
"SQL Server and Windows Authentication mode" in SQL Server, then create a read-only login:

```sql
CREATE LOGIN erp_reader WITH PASSWORD = '<strong password>';
USE arete_group;
CREATE USER erp_reader FOR LOGIN erp_reader;
GRANT SELECT ON dbo.purchase_order_lines TO erp_reader;
GRANT SELECT ON dbo.user_access TO erp_reader;
```

In `.env`, point the connection at the host:

```
SQL_SERVER_CONN=DRIVER={ODBC Driver 18 for SQL Server};SERVER=host.docker.internal,1433;DATABASE=arete_group;UID=erp_reader;PWD=<password>;TrustServerCertificate=yes
```

```powershell
docker build -t erp-assistant .
docker run --rm -p 8000:8000 --env-file .env erp-assistant
```

`.env` is passed in at run time and never copied into the image (see `.dockerignore`).
The index is built when the container first starts.

### Deploying on Azure (notes)

| Part | On Azure |
|---|---|
| API | Push the image to Azure Container Registry and run it on **Azure Container Apps** (or App Service for Containers). |
| Secrets | **Key Vault** for the OpenAI key and DB settings, read through the app's **managed identity**. Nothing in code or in the image. |
| LLM | Keep OpenAI, or switch to **Azure OpenAI** so prompts stay in your tenant. That is a small change: `AzureChatOpenAI` / `AzureOpenAIEmbeddings` from the same `langchain-openai` package. |
| PO data | **Azure SQL Database**, filled from D365 F&O (Export to Data Lake / Synapse Link, or a scheduled data-entity export). Connect with the managed identity (`Authentication=ActiveDirectoryMsi` in ODBC Driver 18), so no password is needed, and grant read-only access. |
| Documents | Keep them in SharePoint or Blob Storage and re-run the ingest on a schedule. For more documents, replace Chroma with **Azure AI Search**, with `company` as a filterable field and the same access filter. |
| Users | Sign users in with **Microsoft Entra ID** and take the user from the token, not from the request body. Map users to companies from D365 security roles or the access table. |
| Logs | Send the JSON request log to **Application Insights / Log Analytics** to track cost, routes and refusals. |
| Network | Private endpoints for SQL and Key Vault; only the API is public, behind Entra ID sign-in. |

## Known limitations

- **The API trusts the `user_id` in the request**, as the brief specifies. Anyone who can reach the API can claim
  to be U03. In production the user must come from a sign-in (see the Azure notes).
- The data tools cover filters (project, vendor, status, company, dates) with totals, lists and group-by totals.
  A question outside that shape (for example "average unit price per item") gets "not available" rather than a
  guess. Adding a tool is the way to extend it.
- With only 9 short documents, retrieval uses plain similarity search (top 4 chunks), with no reranking.

## Data notes and assumptions

The data is not perfectly clean. What I found and what I assumed:

**Data source**
1. The PO register and user access list are read directly from SQL Server (`arete_group.dbo.purchase_order_lines`
   and `arete_group.dbo.user_access`), where they were provided. They are not copied into SQLite.
   `data/sql/arete_group.sql` recreates both tables with the same 40 PO lines and 3 users; it was tested on an empty
   database and matched the original row for row.
2. The data pack has **9** documents, not 10 as the brief says. The tenth file is `Read me.txt`, which is not indexed.
   The documents were moved from `ERP Assistant Data Pack/Documents` to `data/documents`, unchanged, with the same
   company folders.

**User access**
3. `companies_allowed` is free text: `C01`, `C02, C03`, `All`. It is split on commas, and `All` means every company.
   User IDs are not case-sensitive. An unknown user gets HTTP 403.
4. If a question names a company the user cannot see (`C01`, or the words Riverside / Greenleaf / Coastal), it is
   refused before any search. If it does not name the company (for example a project that belongs to another
   company), the data tools catch it: when nothing matches for the user but rows exist in the hidden companies,
   the tool returns ACCESS DENIED and the LLM refuses. Only a count of the hidden rows is read, never the rows.
   Telling the user "this belongs to a company you cannot see" is a small hint that the record exists. I accepted
   that because the brief asks for a polite refusal in exactly this case.
5. The keyword check is simple: a question that uses "coastal" or "riverside" in another sense is refused for a
   user without that company.

**PO data**
6. "Open PO" means `purchase_status = 'Open order'`. The statuses are Open order, Received, Invoiced and Canceled.
7. "PO value" is the sum of `line_amount_inr`, which is **without GST** (Read me). **Canceled lines are left out of
   totals** unless the user asks for canceled or all lines. Every figure the assistant gives says "without GST".
8. One vendor is spelled several ways, so vendors are grouped by `vendor_account`:
   V-00145 is `GUJARAT STEEL ROLLING PVT. LTD.`, `Gujarat Steel Rolling` and `Gujarat Steel Rolling Pvt Ltd`.
   The same applies to `PackWell` / `Packwell` (V-00322), `RackMaster Systems LLP` / `Rackmaster Systems` (V-00433)
   and `SHREE CEMENT TRADERS` (V-00112). Vendor name searches also ignore dots.
9. "Project Riverside" is the project **Riverside Towers** (RIL-PRJ-0007), found by project name. It is a different
   thing from the company Riverside Infra Ltd.
10. In this export every PO number has exactly one line (40 lines, 40 POs).
11. **Possible duplicate:** RIL/PO/26-27/00044 (12-Jul-2026, Mehul S) and RIL/PO/26-27/00041 (02-Aug-2026, Kiran P)
    have the same vendor, item, project, quantity (11 MT) and amount (INR 6,38,000). They have different PO numbers,
    so both are counted, but someone should check them.
12. 18 of 40 lines have no project. They count in company and vendor totals but not in project totals.
    A Coastal Retail line for packaged rice is booked to the "Store Expansion Ph-2" project, which looks odd,
    but it is used as given.

**Documents**
13. Riverside has two approval matrices. v1.0 is marked "(old)" and "SUPERSEDED" (plant head limit 3,00,000);
    v2.0 is current (5,00,000). The old one is indexed with `superseded = true` and left out of every search.
14. The approval limits in the policies include taxes, while PO register amounts exclude GST. The assistant does not
    compare the two.
15. Coastal Retail has no PO approval policy. Its store guidelines only give a **purchase requisition** limit
    (store manager up to 30,000). For a plant head question, C03 is answered as "not available".
16. Documents in "Common - All Companies" are tagged `ALL` and shown to everyone.
17. Word tables are read in place, next to their headings, so a row such as "Plant Head | Up to 5,00,000" keeps its
    context. Every chunk also starts with its document name and company.
18. The forwarded RCM mail contains the same text twice (forward plus original); the GRN notes contain a
    Hindi-English line. Both are indexed as they are.

**Cost**
19. The cost per request is approximate: chat tokens from the API response multiplied by the list price, plus
    search-query embedding tokens counted with tiktoken. The cached-input discount is ignored, so the real cost
    is the same or lower.
