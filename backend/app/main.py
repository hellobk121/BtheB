from fastapi import FastAPI

from app.core.config import load_env
from app.engines.llm.base import LLM
from app.engines.llm.factory import get_llm
from app.features.chat.router import build_router


def create_app(llm: LLM | None = None) -> FastAPI:
    if llm is None:
        load_env()
    app = FastAPI(title="BtheB")
    app.include_router(build_router(llm or get_llm()))
    return app
