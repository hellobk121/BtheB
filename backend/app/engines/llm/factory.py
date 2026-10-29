import os
from typing import Mapping

from app.engines.llm.base import LLM
from app.engines.llm.claude_cli import ClaudeCliLLM


def get_llm(env: Mapping[str, str] = os.environ) -> LLM:
    backend = env.get("LLM_BACKEND", "cli")
    if backend == "cli":
        return ClaudeCliLLM(timeout=int(env.get("CLAUDE_CLI_TIMEOUT", "120")))
    if backend == "api":
        raise NotImplementedError("LLM_BACKEND=api is planned for M5")
    raise ValueError(f"unknown LLM_BACKEND: {backend!r} (expected 'cli' or 'api')")
