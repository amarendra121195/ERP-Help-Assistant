from langchain_chroma import Chroma

from app.core import config
from app.rag.embeddings import get_embeddings


def get_vector_store():
    return Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(config.VECTORSTORE_DIR),
    )


def rebuild_vector_store(chunks):
    # drop the old collection first so we don't get duplicates
    get_vector_store().delete_collection()
    get_vector_store().add_documents(chunks)
