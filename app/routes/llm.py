# app/routes/llm.py
from typing import Generator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.dependencies import get_llm_service
from app.models.chat import Chat

router = APIRouter()


@router.post("/chat")
async def chat(chat_request: Chat):
    def generate() -> Generator[str, None, None]:
        for response in get_llm_service().chat(
                limit=chat_request.limit,
                query=chat_request.query,
                score_threshold=chat_request.score_threshold,
                filters=chat_request.filters,
                search=chat_request.search
        ):
            yield f"data: {response}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
