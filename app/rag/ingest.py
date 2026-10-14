"""Builds the vector index from data/documents.

    python -m app.rag.ingest
"""
from app.core import config
from app.rag.loader import load_documents
from app.rag.splitter import split_documents
from app.rag.vector_store import rebuild_vector_store
from app.utils.cost import cost_usd, count_tokens


def build_index():
    documents = load_documents()
    chunks = split_documents(documents)
    rebuild_vector_store(chunks)

    tokens = sum(count_tokens(chunk.page_content) for chunk in chunks)
    cost = cost_usd(config.EMBEDDING_MODEL, tokens)
    print(f"Indexed {len(documents)} documents, {len(chunks)} chunks ({tokens} tokens, ~${cost:.5f})")

    for doc in documents:
        note = "  (superseded, not used)" if doc.metadata["superseded"] else ""
        print(f"  {doc.metadata['company']:<4} {doc.metadata['source']}{note}")


if __name__ == "__main__":
    build_index()
