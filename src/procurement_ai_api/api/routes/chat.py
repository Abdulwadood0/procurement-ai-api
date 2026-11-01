from uuid import uuid4

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from procurement_ai_api.schemas.chat import ChatRequest
from procurement_ai_api.services.chat_service import stream_chat

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/")
async def chat(request: ChatRequest):

    thread_id = request.thread_id or str(uuid4())

    return StreamingResponse(
        stream_chat(request.question, thread_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )