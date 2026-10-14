from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    user_id: str = Field(examples=["U01"])
    question: str = Field(min_length=3, examples=["How do I create a purchase order against a project WBS?"])


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    embedding_tokens: int
    cost_usd: float


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    route: str  # documents, data, documents+data or refused
    usage: Usage
