from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


def test_root_endpoint(client: TestClient):
    """Test 1: Root endpoint returns 200 and expected status payload."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert data["message"] == "Backend functioning well"
    assert "version" in data


def test_health_endpoint(client: TestClient):
    """Test 2: Health check endpoint returns healthy status and DB count."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["schemes_count"] == 12


def test_v1_health_endpoint(client: TestClient):
    """Test 2b: API v1 Health endpoint functions identically."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["schemes_count"] == 12


def test_database_connectivity_and_count(db_session: Session):
    """Test 3: Direct read-only database query verifies exact 12 schemes intact."""
    result = db_session.execute(text("SELECT COUNT(*) FROM schemes;")).scalar()
    assert result == 12, f"Expected exactly 12 schemes in the database, found {result}"
