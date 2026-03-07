"""application configuration loaded from environment."""
from pathlib import Path
from pydantic import ValidationError
from pydantic_settings import BaseSettings

# Project root (folder containing pyproject.toml, src/, data/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """load from environment or .env in project root. ensuring no credentials in code."""

    database_url: str  # required: set in .env as DATABASE_URL (no default to avoid exposing credentials - our life, haha!!)
    data_dir: Path = _PROJECT_ROOT / "data"
    host: str = "0.0.0.0"
    port: int = 8080

    model_config = {
        "env_file": _PROJECT_ROOT / ".env",
        "env_file_encoding": "utf-8",
    }


# create a global settings instance with error handling.
try:
    settings = Settings()

except ValidationError as e:
    missing = [err["loc"][0] for err in e.errors() if err["type"] == "missing"]

    raise RuntimeError(
        "\n\n[CONFIG ERROR] Missing required environment variable(s): "
        f"{', '.join(str(f).upper() for f in missing)}\n"
        "Please copy '.env.example' to '.env' and fill in the required values.\n"
        "Example: DATABASE_URL=postgresql://user:password@localhost:5432/moniepoint_analytics\n"
    ) from None
