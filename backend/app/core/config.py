import os
from pathlib import Path
from typing import MutableMapping

from dotenv import dotenv_values

DEFAULT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


def load_env(path: Path = DEFAULT_ENV_FILE, environ: MutableMapping[str, str] = os.environ) -> None:
    """Fill `environ` from a .env file without overriding values that are already set."""
    for key, value in dotenv_values(path).items():
        if value is not None:
            environ.setdefault(key, value)
