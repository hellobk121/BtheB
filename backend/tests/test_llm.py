import subprocess
from types import SimpleNamespace

import pytest

from app.engines.llm.base import LLMError
from app.engines.llm.claude_cli import ClaudeCliLLM
from app.engines.llm.factory import get_llm


class FakeRunner:
    """Records the subprocess.run call and returns a canned result or raises."""

    def __init__(self, stdout="ok", returncode=0, stderr="", raises=None):
        self.result = SimpleNamespace(stdout=stdout, returncode=returncode, stderr=stderr)
        self.raises = raises
        self.calls = []

    def __call__(self, args, **kwargs):
        self.calls.append((args, kwargs))
        if self.raises:
            raise self.raises
        return self.result


def test_generate_returns_stripped_stdout():
    llm = ClaudeCliLLM(runner=FakeRunner(stdout="  답변\n"))
    assert llm.generate([{"role": "user", "content": "q"}]) == "답변"


def test_prompt_goes_to_stdin_not_argv():
    runner = FakeRunner()
    ClaudeCliLLM(runner=runner).generate([{"role": "user", "content": "--help"}])
    args, kwargs = runner.calls[0]
    assert "--help" not in args
    assert "--help" in kwargs["input"]


def test_chat_only_flags_are_used():
    runner = FakeRunner()
    ClaudeCliLLM(runner=runner).generate([{"role": "user", "content": "q"}])
    args, _ = runner.calls[0]
    assert args[:2] == ["claude", "-p"]
    assert "--no-session-persistence" in args
    assert args[args.index("--tools") + 1] == ""


def test_system_and_history_are_in_prompt():
    runner = FakeRunner()
    ClaudeCliLLM(runner=runner).generate(
        [
            {"role": "system", "content": "SYS"},
            {"role": "user", "content": "U1"},
            {"role": "assistant", "content": "A1"},
            {"role": "user", "content": "U2"},
        ]
    )
    prompt = runner.calls[0][1]["input"]
    positions = [prompt.index(s) for s in ("SYS", "U1", "A1", "U2")]
    assert positions == sorted(positions)


def test_nonzero_exit_raises_llmerror():
    llm = ClaudeCliLLM(runner=FakeRunner(returncode=1, stderr="boom"))
    with pytest.raises(LLMError):
        llm.generate([{"role": "user", "content": "q"}])


def test_timeout_raises_llmerror():
    err = subprocess.TimeoutExpired(cmd="claude", timeout=1)
    with pytest.raises(LLMError):
        ClaudeCliLLM(runner=FakeRunner(raises=err)).generate([{"role": "user", "content": "q"}])


def test_missing_binary_raises_llmerror():
    with pytest.raises(LLMError):
        ClaudeCliLLM(runner=FakeRunner(raises=FileNotFoundError())).generate(
            [{"role": "user", "content": "q"}]
        )


def test_factory_defaults_to_cli():
    assert isinstance(get_llm({}), ClaudeCliLLM)


def test_factory_unknown_backend_raises():
    with pytest.raises(ValueError, match="x"):
        get_llm({"LLM_BACKEND": "x"})


def test_factory_api_not_implemented():
    with pytest.raises(NotImplementedError, match="M5"):
        get_llm({"LLM_BACKEND": "api"})


def test_subprocess_is_isolated_from_developer_context():
    import tempfile

    runner = FakeRunner()
    ClaudeCliLLM(runner=runner).generate([{"role": "user", "content": "q"}])
    args, kwargs = runner.calls[0]
    assert "--safe-mode" in args
    assert "--strict-mcp-config" in args
    assert kwargs["cwd"] == tempfile.gettempdir()


def test_undecodable_output_is_replaced_not_raised():
    runner = FakeRunner()
    ClaudeCliLLM(runner=runner).generate([{"role": "user", "content": "q"}])
    assert runner.calls[0][1]["errors"] == "replace"


def test_other_oserror_raises_llmerror():
    with pytest.raises(LLMError):
        ClaudeCliLLM(runner=FakeRunner(raises=PermissionError())).generate(
            [{"role": "user", "content": "q"}]
        )
