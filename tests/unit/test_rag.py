from app.rag.loader import load_documents
from app.rag.retriever import access_filter
from app.rag.splitter import split_documents


def test_document_metadata():
    docs = {d.metadata["source"]: d.metadata for d in load_documents()}
    assert len(docs) == 9
    assert docs["Greenleaf Purchase Policy 2026.pdf"]["company"] == "C02"
    assert docs["GRN errors and solutions.txt"]["company"] == "ALL"
    assert docs["Riverside - PO Approval Matrix v1.0 (old).pdf"]["superseded"] is True
    assert docs["Riverside - PO Approval Matrix v2.0.docx"]["superseded"] is False


def test_docx_table_rows():
    docs = {d.metadata["source"]: d.page_content for d in load_documents()}
    assert "Plant Head / Project Manager | Up to 5,00,000" in docs["Riverside - PO Approval Matrix v2.0.docx"]


def test_chunk_header():
    for chunk in split_documents(load_documents()):
        assert chunk.page_content.startswith(f"Document: {chunk.metadata['source']} | Company: ")


def test_access_filter():
    assert access_filter(["C02", "C03"]) == {"$and": [
        {"company": {"$in": ["C02", "C03", "ALL"]}},
        {"superseded": {"$eq": False}},
    ]}
