import pytest
import re
from pathlib import Path
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def get_project_version():
    """Get the version from pyproject.toml."""
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"
    
    with open(pyproject_path, "r") as f:
        content = f.read()
    
    # Find version in the [project] section
    version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if version_match:
        return version_match.group(1)
    
    raise ValueError("Could not find version in pyproject.toml")


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
    """Test the version endpoint returns current version from pyproject.toml."""
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()
    
    # Get expected version from pyproject.toml
    expected_version = get_project_version()
    assert response.json()["version"] == expected_version


@pytest.mark.asyncio
async def test_endpoints_content_type():
    """Test that endpoints return JSON content type."""
    response = client.get("/")
    assert response.headers["content-type"] == "application/json"

    response = client.get("/api/v1/health")
    assert response.headers["content-type"] == "application/json"
