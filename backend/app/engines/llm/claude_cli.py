import subprocess
import tempfile

from app.engines.llm.base import LLMError, Message

_LABELS = {"system": "System", "user": "User", "assistant": "Assistant"}


class ClaudeCliLLM:
    """Chat-only `claude -p` call. For development and personal demos only."""

    def __init__(self, runner=subprocess.run, timeout: int = 120):
        self._runner = runner
        self.timeout = timeout

    def generate(self, messages: list[Message]) -> str:
        prompt = "\n\n".join(f"{_LABELS[m['role']]}: {m['content']}" for m in messages)
        args = [
            "claude", "-p", "--tools", "", "--no-session-persistence",
            "--safe-mode", "--strict-mcp-config", "--output-format", "text",
        ]
        try:
            result = self._runner(
                args,
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=tempfile.gettempdir(),
                timeout=self.timeout,
            )
        except FileNotFoundError as e:
            raise LLMError("claude CLI not found") from e
        except subprocess.TimeoutExpired as e:
            raise LLMError(f"claude CLI timed out after {self.timeout}s") from e
        except OSError as e:
            raise LLMError(f"claude CLI could not start: {type(e).__name__}") from e
        if result.returncode != 0:
            raise LLMError(f"claude CLI exited with code {result.returncode}")
        return result.stdout.strip()
