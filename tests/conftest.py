"""shared pytest fixtures for the Moniepoint Analytics API test suite."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.main import app
from src.core.deps import get_db


def get_mock_db():
    """return a MagicMock standing in for a SQLAlchemy session."""

    return MagicMock(spec=Session)


@pytest.fixture
def mock_db():
    """fresh mock DB session for each test."""

    return get_mock_db()


@pytest.fixture
def client(mock_db):
    """
    testClient with the real db dependency overridden by a mock.
    no real database connection is needed to run these tests.
    """
    
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()