"""Application configuration loaded from environment."""
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Load from environment or .env."""

    database_url: str = "postgresql://postgres:postgres@localhost:5432/moniepoint_analytics"
    data_dir: Path = Path(__file__).resolve().parent.parent.parent / "data"
    host: str = "0.0.0.0"
    port: int = 8080

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
