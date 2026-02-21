"""Application configuration loaded from environment."""
from pathlib import Path

from pydantic_settings import BaseSettings

# Project root (folder containing pyproject.toml, src/, data/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Load from environment or .env in project root. No credentials in code."""

    database_url: str  # required: set in .env as DATABASE_URL (no default to avoid exposing credentials - our life, haha!!)
    data_dir: Path = _PROJECT_ROOT / "data"
    host: str = "0.0.0.0"
    port: int = 8080

    model_config = {
        "env_file": _PROJECT_ROOT / ".env",
        "env_file_encoding": "utf-8",
    }

# create a global settings instance.
settings = Settings()
