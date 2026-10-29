from typing import Literal, Protocol, TypedDict


class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMError(Exception):
    """The LLM backend could not produce an answer."""


class LLM(Protocol):
    def generate(self, messages: list[Message]) -> str: ...
