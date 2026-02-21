"""SQLAlchemy engine, session factory, and declarative base."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from src.core.config import settings

# create SQLAlchemy engine and session factory.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,
)

# create session factory.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base for all SQLAlchemy models."""

    pass
