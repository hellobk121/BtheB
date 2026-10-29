from app.core.config import load_env
from app.engines.llm.factory import get_llm


def test_env_file_values_reach_get_llm(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("CLAUDE_CLI_TIMEOUT=300\n", encoding="utf-8")
    env: dict[str, str] = {}
    load_env(env_file, env)
    assert get_llm(env).timeout == 300


def test_real_environment_wins_over_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("CLAUDE_CLI_TIMEOUT=300\n", encoding="utf-8")
    env = {"CLAUDE_CLI_TIMEOUT": "45"}
    load_env(env_file, env)
    assert get_llm(env).timeout == 45


def test_missing_env_file_is_fine(tmp_path):
    env: dict[str, str] = {}
    load_env(tmp_path / "nope.env", env)
    assert env == {}


def test_default_env_file_sits_at_repo_root():
    from app.core.config import DEFAULT_ENV_FILE

    assert DEFAULT_ENV_FILE.name == ".env"
    assert (DEFAULT_ENV_FILE.parent / "backend" / "pyproject.toml").is_file()
