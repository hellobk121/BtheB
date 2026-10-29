from fastapi.testclient import TestClient

from app.engines.llm.base import LLMError
from app.main import create_app


class FakeLLM:
    def __init__(self, reply="안녕", error=None):
        self.reply = reply
        self.error = error
        self.calls = []

    def generate(self, messages):
        self.calls.append(messages)
        if self.error:
            raise self.error
        return self.reply


def make_client(llm):
    return TestClient(create_app(llm))


def test_health_ok():
    r = make_client(FakeLLM()).get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_chat_returns_reply():
    llm = FakeLLM(reply="안녕")
    r = make_client(llm).post("/chat", json={"message": "hi"})
    assert r.status_code == 200
    assert r.json() == {"reply": "안녕"}
    assert llm.calls[0][-1] == {"role": "user", "content": "hi"}


def test_chat_rejects_blank_message():
    llm = FakeLLM()
    r = make_client(llm).post("/chat", json={"message": "   "})
    assert r.status_code == 422
    assert llm.calls == []


def test_chat_rejects_too_long_message():
    llm = FakeLLM()
    r = make_client(llm).post("/chat", json={"message": "a" * 4001})
    assert r.status_code == 422
    assert llm.calls == []


def test_chat_llm_error_returns_502_without_traceback():
    r = make_client(FakeLLM(error=LLMError("claude CLI timed out after 120s"))).post(
        "/chat", json={"message": "hi"}
    )
    assert r.status_code == 502
    assert "Traceback" not in r.text
    assert "timed out" in r.json()["detail"]
