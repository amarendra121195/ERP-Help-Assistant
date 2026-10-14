from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.api.schemas import AskRequest, AskResponse
from app.services.access import UnknownUserError
from app.services.assistant import ask

router = APIRouter()

CHAT_PAGE = Path(__file__).resolve().parents[1] / "static" / "index.html"


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    # response_model keeps only answer, sources, route and usage
    try:
        return ask(request.user_id, request.question)
    except UnknownUserError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/", include_in_schema=False)
def chat_page():
    return FileResponse(CHAT_PAGE)
