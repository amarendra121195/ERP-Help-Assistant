from app.core import config
from app.core.companies import COMMON
from app.rag.vector_store import get_vector_store


def access_filter(companies):
    # user's companies + common docs, and skip old versions
    return {"$and": [
        {"company": {"$in": companies + [COMMON]}},
        {"superseded": {"$eq": False}},
    ]}


def retrieve(query, companies, k=config.TOP_K):
    return get_vector_store().similarity_search(query, k=k, filter=access_filter(companies))
