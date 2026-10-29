from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, StringConstraints
from typing import Annotated

from app.engines.llm.base import LLM, LLMError


class ChatRequest(BaseModel):
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]


class ChatResponse(BaseModel):
    reply: str


def build_router(llm: LLM) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.post("/chat")
    def chat(req: ChatRequest) -> ChatResponse:
        try:
            reply = llm.generate([{"role": "user", "content": req.message}])
        except LLMError as e:
            raise HTTPException(status_code=502, detail=str(e)) from e
        return ChatResponse(reply=reply)

    return router
