from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.db.session import SessionLocal


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """FastAPI TestClient for executing API requests."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def db_session() -> Generator[Session, None, None]:
    """Read-only database session fixture for test assertions."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
