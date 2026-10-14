import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

DOCUMENTS_DIR = ROOT_DIR / "data" / "documents"
VECTORSTORE_DIR = ROOT_DIR / "vectorstore"
LOG_FILE = ROOT_DIR / "logs" / "requests.jsonl"

SQL_SERVER_CONN = os.getenv(
    "SQL_SERVER_CONN",
    "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=arete_group;"
    "Trusted_Connection=yes;TrustServerCertificate=yes",
)
PO_TABLE = "dbo.purchase_order_lines"
ACCESS_TABLE = "dbo.user_access"

CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-5.6-luna")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
REASONING_EFFORT = os.getenv("REASONING_EFFORT", "")
LLM_TIMEOUT = 60
LLM_MAX_RETRIES = 2

# USD per 1M tokens (input, output) - from the OpenAI pricing page, Oct 2026
PRICES = {
    "gpt-5.6-luna": (0.20, 1.20),
    "gpt-6.1-sol": (2.00, 10.00),
    "gpt-6-luna": (0.10, 0.50),
    "text-embedding-3-large": (0.13, 0.0),
    "text-embedding-3-small": (0.02, 0.0),
}

COLLECTION_NAME = "erp_documents"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150
TOP_K = 4

MAX_TOOL_ROUNDS = 4
