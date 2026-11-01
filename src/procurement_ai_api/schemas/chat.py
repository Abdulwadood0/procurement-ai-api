from pydantic import BaseModel

class ChatRequest(BaseModel):
    question: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    thread_id: str
    answer: str
