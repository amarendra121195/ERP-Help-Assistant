from langchain_openai import OpenAIEmbeddings

from app.core import config


def get_embeddings():
    return OpenAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        timeout=config.LLM_TIMEOUT,
        max_retries=config.LLM_MAX_RETRIES,
    )
