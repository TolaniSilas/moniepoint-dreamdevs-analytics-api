"""sqlalchemy engine, session factory, and declarative base."""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.exc import OperationalError
from src.core.config import settings


# create SQLAlchemy engine and session factory.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,
)


# verify the database is reachable at startup (check if it is alive).
try:

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

except OperationalError as e:
    raise RuntimeError(
        "\n\n[DATABASE ERROR] Could not connect to the database.\n"
        "Please check that:\n"
        "  1. PostgreSQL is running\n"
        "  2. DATABASE_URL in your .env is correct\n"
        f"  Detail: {e.orig}\n"
    ) from None


# create session factory.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """Base for all SQLAlchemy models."""

    pass