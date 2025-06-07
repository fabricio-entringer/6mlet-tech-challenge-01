import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns expected message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to 6MLET Tech Challenge 01 API"}


def test_health_check_endpoint():
    """Test the health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_version_endpoint():
    """Test the version endpoint returns current version."""
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()
    assert response.json()["version"] == "0.0.1"


@pytest.mark.asyncio
async def test_endpoints_content_type():
    """Test that endpoints return JSON content type."""
    response = client.get("/")
    assert response.headers["content-type"] == "application/json"

    response = client.get("/health")
    assert response.headers["content-type"] == "application/json"
