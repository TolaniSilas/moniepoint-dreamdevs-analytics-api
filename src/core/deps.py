"""shared dependencies for the API (the DB session)."""
from collections.abc import Generator
from sqlalchemy.orm import Session
from src.db.base import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """yield a database session; ensure it is closed after request."""

    # create a new session for the request.
    db = SessionLocal()

    # yield the session.
    try:
        yield db
    
    # ensure the session is closed after a request has been processsed, even if an error occurs.
    finally:
        db.close()
