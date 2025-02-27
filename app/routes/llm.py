# app/routes/llm.py

from fastapi import APIRouter

from app.dependencies import get_llm_service
from app.models.chat import Chat

router = APIRouter()


@router.post("/chat")
def chat(chat_request: Chat):
    answer = get_llm_service().chat(
        limit=chat_request.limit,
        query=chat_request.query,
        score_threshold=chat_request.score_threshold,
        filters=chat_request.filters,
        search=chat_request.search,
        conversation_id=chat_request.conversation_id
    )
    return answer

