"""Tests for the enhanced health endpoint (Issue #14)."""

import pytest
import os
import tempfile
import csv
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.api.main import app
from app.api.health import HealthService

client = TestClient(app)


class TestHealthEndpoint:
    """Test cases for the enhanced health endpoint."""

    def test_health_endpoint_exists(self):
        """Test that the new health endpoint exists and is accessible."""
        response = client.get("/api/v1/health")
        assert response.status_code in [200, 503]  # Either healthy or unhealthy

    def test_health_endpoint_response_structure(self):
        """Test that the health endpoint returns the expected response structure."""
        response = client.get("/api/v1/health")
        
        # Should be either 200 (healthy/degraded) or 503 (unhealthy)
        assert response.status_code in [200, 503]
        
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "uptime" in data
        assert "components" in data
        assert "data" in data
        assert "system" in data
        assert "api_info" in data
        
        # Check status values
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        
        # Check components structure
        components = data["components"]
        assert "api" in components
        assert "data_files" in components
        assert "memory" in components
        
        # Each component should have required fields
        for component in components.values():
            assert "status" in component
            assert "last_checked" in component
            # details is optional but if present should be a string

    @patch('app.api.health.HealthService._get_data_file_path')
    def test_health_endpoint_with_missing_data_file(self, mock_path):
        """Test health endpoint behavior when data file is missing."""
        # Mock a non-existent file path
        mock_path.return_value = Path("/nonexistent/path/books_data.csv")
        
        response = client.get("/api/v1/health")
        
        # Should still respond but may be degraded/unhealthy
        assert response.status_code in [200, 503]
        data = response.json()
        
        # For unhealthy response, data is in the detail field
        if response.status_code == 503:
            data = data["detail"]
        
        # Data component should reflect the missing file
        assert data["components"]["data_files"]["status"] in ["unhealthy", "degraded"]
        assert data["data"]["total_books"] == 0

    @patch('app.api.health.HealthService._get_data_file_path')
    def test_health_endpoint_with_valid_data_file(self, mock_path):
        """Test health endpoint with a valid data file."""
        # Create a temporary CSV file with sample data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url'])
            writer.writeheader()
            for i in range(150):  # More than 100 to ensure "healthy" status
                writer.writerow({
                    'id': i + 1,
                    'title': f'Book {i + 1}',
                    'price': '£20.00',
                    'rating_text': 'Four',
                    'rating_numeric': 4,
                    'availability': 'In stock',
                    'category': f'Category {(i % 5) + 1}',
                    'image_url': 'https://example.com/image.jpg'
                })
            
            temp_file_path = f.name

        try:
            mock_path.return_value = Path(temp_file_path)
            
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["components"]["data_files"]["status"] == "healthy"
            assert data["data"]["total_books"] == 150
            assert data["data"]["total_categories"] == 5
        finally:
            os.unlink(temp_file_path)

    def test_health_endpoint_performance(self):
        """Test that the health endpoint responds quickly."""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/health")
        end_time = time.time()
        
        # Should respond within 2 seconds
        assert end_time - start_time < 2.0
        assert response.status_code in [200, 503]

    def test_health_endpoint_uptime_format(self):
        """Test that uptime is formatted correctly."""
        response = client.get("/api/v1/health")
        data = response.json()
        
        uptime = data["uptime"]
        # Should be in format like "1h 30m 45s" or "30m 45s" or "45s"
        assert isinstance(uptime, str)
        assert len(uptime) > 0
        # Should contain 's' for seconds
        assert uptime.endswith('s')

    def test_health_endpoint_api_info(self):
        """Test that API info contains expected fields."""
        response = client.get("/api/v1/health")
        data = response.json()
        
        api_info = data["api_info"]
        assert "environment" in api_info
        assert "python_version" in api_info
        assert "endpoints_available" in api_info

    def test_health_endpoint_system_stats(self):
        """Test that system statistics are included."""
        response = client.get("/api/v1/health")
        data = response.json()
        
        system = data["system"]
        assert "memory_usage_mb" in system
        assert "memory_percent" in system
        assert isinstance(system["memory_usage_mb"], (int, float))
        assert isinstance(system["memory_percent"], (int, float))
        assert 0 <= system["memory_percent"] <= 100

    def test_health_endpoint_timestamp_format(self):
        """Test that timestamp is in proper ISO format."""
        response = client.get("/api/v1/health")
        data = response.json()
        
        timestamp_str = data["timestamp"]
        # Should be able to parse as ISO datetime
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        assert isinstance(timestamp, datetime)

    def test_health_endpoint_version_info(self):
        """Test that version information is included."""
        response = client.get("/api/v1/health")
        data = response.json()
        
        assert "version" in data
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    @patch('app.api.health.psutil.virtual_memory')
    def test_health_endpoint_high_memory_usage(self, mock_memory):
        """Test health endpoint behavior with high memory usage."""
        # Mock high memory usage (95%)
        mock_memory.return_value = MagicMock(percent=95.0)
        
        response = client.get("/api/v1/health")
        
        # Should be unhealthy due to high memory usage, but expect 503 status code
        assert response.status_code == 503
        
        # The response should contain the error details
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert detail["status"] == "unhealthy"
        assert detail["components"]["memory"]["status"] == "unhealthy"

    @patch('app.api.health.HealthService._get_data_file_path')
    @patch('app.api.health.psutil.virtual_memory')
    def test_health_endpoint_all_components_healthy(self, mock_memory, mock_path):
        """Test scenario where all components are healthy."""
        # Create a temporary valid data file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url'])
            writer.writeheader()
            for i in range(200):
                writer.writerow({
                    'id': i + 1,
                    'title': f'Book {i + 1}',
                    'price': '£25.00',
                    'rating_text': 'Five',
                    'rating_numeric': 5,
                    'availability': 'In stock',
                    'category': 'Fiction',
                    'image_url': 'https://example.com/image.jpg'
                })
            temp_file_path = f.name

        try:
            mock_path.return_value = Path(temp_file_path)
            mock_memory.return_value = MagicMock(percent=45.0)  # Normal memory usage
            
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert data["components"]["api"]["status"] == "healthy"
            assert data["components"]["data_files"]["status"] == "healthy"
            assert data["components"]["memory"]["status"] == "healthy"
        finally:
            os.unlink(temp_file_path)


class TestHealthService:
    """Test cases for the HealthService class."""

    def test_health_service_initialization(self):
        """Test that HealthService initializes correctly."""
        service = HealthService()
        assert hasattr(service, 'startup_time')
        assert hasattr(service, 'version')
        assert hasattr(service, 'data_file_path')

    def test_uptime_formatting(self):
        """Test uptime formatting with different durations."""
        service = HealthService()
        
        # Mock different uptime values
        with patch('time.time') as mock_time:
            # Test seconds only
            mock_time.return_value = service.startup_time + 45
            assert service._format_uptime() == "45s"
            
            # Test minutes and seconds
            mock_time.return_value = service.startup_time + 125  # 2m 5s
            assert service._format_uptime() == "2m 5s"
            
            # Test hours, minutes, and seconds
            mock_time.return_value = service.startup_time + 3665  # 1h 1m 5s
            assert service._format_uptime() == "1h 1m 5s"

    @pytest.mark.asyncio
    async def test_legacy_health_compatibility(self):
        """Test that legacy health check works for backward compatibility."""
        service = HealthService()
        
        # Test legacy health method exists and returns proper format
        legacy_health = await service.get_legacy_health()
        assert hasattr(legacy_health, 'status')
        assert legacy_health.status in ['healthy', 'unhealthy']


class TestHealthEndpointIntegration:
    """Integration tests for the health endpoint."""

    def test_health_endpoint_openapi_documentation(self):
        """Test that the health endpoint is documented in OpenAPI spec."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_spec = response.json()
        paths = openapi_spec.get("paths", {})
        
        # Check that /api/v1/health is documented
        assert "/api/v1/health" in paths
        health_endpoint = paths["/api/v1/health"]
        assert "get" in health_endpoint
        
        # Check response schema
        get_spec = health_endpoint["get"]
        assert "responses" in get_spec
        assert "200" in get_spec["responses"]

    def test_old_health_endpoint_removed(self):
        """Test that the old /health endpoint is no longer available."""
        response = client.get("/health")
        # Should return 404 since we removed the old endpoint
        assert response.status_code == 404
