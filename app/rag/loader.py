import re

import docx
from docx.table import Table
from langchain_core.documents import Document
from pypdf import PdfReader

from app.core import config
from app.core.companies import COMMON


def read_pdf(path):
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def read_docx(path):
    # keep tables in place so a table row stays next to its heading
    lines = []
    for block in docx.Document(path).iter_inner_content():
        if isinstance(block, Table):
            for row in block.rows:
                lines.append(" | ".join(cell.text.strip() for cell in row.cells))
        elif block.text.strip():
            lines.append(block.text.strip())
    return "\n".join(lines)


def read_txt(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="cp1252")


READERS = {".pdf": read_pdf, ".docx": read_docx, ".txt": read_txt}


def get_company(folder_name):
    # "Riverside Infra (C01)" -> "C01", "Common - All Companies" -> "ALL"
    match = re.search(r"\((C\d\d)\)", folder_name)
    return match.group(1) if match else COMMON


def is_superseded(path, text):
    return "(old)" in path.name.lower() or bool(re.search(r"\bsuperseded\b", text[:300], re.I))


def load_documents(folder=config.DOCUMENTS_DIR):
    documents = []
    for path in sorted(folder.rglob("*")):
        reader = READERS.get(path.suffix.lower())
        if not reader:
            continue

        text = reader(path).strip()
        metadata = {
            "source": path.name,
            "company": get_company(path.parent.name),
            "superseded": is_superseded(path, text),
        }
        documents.append(Document(page_content=text, metadata=metadata))
    return documents
