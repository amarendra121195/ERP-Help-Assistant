from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core import config
from app.core.companies import company_label


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)

    # add document name and company on top of each chunk, otherwise a chunk like
    # "Plant Head | Up to 5,00,000" doesn't say which company it belongs to
    for chunk in chunks:
        source = chunk.metadata["source"]
        company = company_label(chunk.metadata["company"])
        chunk.page_content = f"Document: {source} | Company: {company}\n{chunk.page_content}"

    return chunks
