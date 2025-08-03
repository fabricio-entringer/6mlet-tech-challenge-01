import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns expected message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to 6MLET Tech Challenge 01 API"}


def test_health_check_endpoint():
    """Test the enhanced health check endpoint returns comprehensive health status."""
    response = client.get("/api/v1/health")
    assert response.status_code in [200, 503]  # Either healthy or unhealthy
    
    data = response.json()
    
    # For 503 responses, the data is in the detail field
    if response.status_code == 503:
        data = data["detail"]
    
    # Check required fields in response
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data
    assert "uptime" in data
    assert "components" in data
    assert "data" in data
    assert "system" in data
    assert "api_info" in data
    
    # Status should be one of the valid values
    assert data["status"] in ["healthy", "degraded", "unhealthy"]


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

    response = client.get("/api/v1/health")
    assert response.headers["content-type"] == "application/json"
