"""Load local configuration explicitly; never print or serialize credentials."""
import os
from pathlib import Path
from dotenv import load_dotenv

DEFAULT_MODEL = "gpt-5.4-mini"


def load_config(env_file: str | Path = ".env") -> str:
    # Deployment environment wins over the developer's local file.
    # Disable interpolation so dollar signs in secrets remain literal.
    load_dotenv(dotenv_path=env_file, override=False, interpolate=False)
    return os.environ.get("OPENAI_MODEL", "").strip() or DEFAULT_MODEL
