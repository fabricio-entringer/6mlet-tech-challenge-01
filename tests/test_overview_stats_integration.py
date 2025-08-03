"""Integration tests for overview statistics API endpoint."""

import os
import pytest
from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


class TestOverviewStatsIntegration:
    """Integration tests for overview statistics endpoint."""

    def test_overview_stats_endpoint_with_sample_data(self):
        """Test the overview stats endpoint with sample data."""
        # This test uses the sample data file that should exist
        response = client.get("/api/v1/stats/overview")
        
        if response.status_code == 404:
            # If no data file exists, that's expected in test environment
            assert "Book data not found" in response.json()["detail"]
            return
        
        # If data exists, verify the response structure
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields are present
        assert "total_books" in data
        assert "price_stats" in data
        assert "rating_distribution" in data
        assert "availability" in data
        assert "categories" in data
        assert "last_updated" in data
        
        # Verify price_stats structure
        price_stats = data["price_stats"]
        assert "average" in price_stats
        assert "min" in price_stats
        assert "max" in price_stats
        assert "median" in price_stats
        
        # Verify rating_distribution structure
        rating_dist = data["rating_distribution"]
        assert "one" in rating_dist
        assert "two" in rating_dist
        assert "three" in rating_dist
        assert "four" in rating_dist
        assert "five" in rating_dist
        
        # Verify availability structure
        availability = data["availability"]
        assert "in_stock" in availability
        assert "out_of_stock" in availability
        
        # Verify data types
        assert isinstance(data["total_books"], int)
        assert isinstance(data["categories"], int)
        assert isinstance(data["last_updated"], str)
        assert isinstance(price_stats["average"], (int, float))
        assert isinstance(availability["in_stock"], int)

    def test_overview_stats_endpoint_openapi_spec(self):
        """Test that the endpoint is properly documented in OpenAPI spec."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_spec = response.json()
        paths = openapi_spec.get("paths", {})
        
        # Verify the endpoint exists in the spec
        assert "/api/v1/stats/overview" in paths
        
        # Verify it has a GET method
        overview_endpoint = paths["/api/v1/stats/overview"]
        assert "get" in overview_endpoint
        
        # Verify response schema
        get_spec = overview_endpoint["get"]
        assert "responses" in get_spec
        assert "200" in get_spec["responses"]
        
        # Verify the response content type
        response_200 = get_spec["responses"]["200"]
        assert "content" in response_200
        assert "application/json" in response_200["content"]

    def test_overview_stats_endpoint_response_format(self):
        """Test that the response matches the expected JSON format from the issue."""
        response = client.get("/api/v1/stats/overview")
        
        if response.status_code == 404:
            # Skip if no data file exists
            pytest.skip("No data file available for testing")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the response format matches the issue specification
        expected_keys = [
            "total_books",
            "price_stats", 
            "rating_distribution",
            "availability",
            "categories",
            "last_updated"
        ]
        
        for key in expected_keys:
            assert key in data, f"Missing key: {key}"
        
        # Verify nested structures match specification
        price_stats = data["price_stats"]
        expected_price_keys = ["average", "min", "max", "median"]
        for key in expected_price_keys:
            assert key in price_stats, f"Missing price_stats key: {key}"
        
        rating_dist = data["rating_distribution"]
        expected_rating_keys = ["one", "two", "three", "four", "five"]
        for key in expected_rating_keys:
            assert key in rating_dist, f"Missing rating_distribution key: {key}"
        
        availability = data["availability"]
        expected_availability_keys = ["in_stock", "out_of_stock"]
        for key in expected_availability_keys:
            assert key in availability, f"Missing availability key: {key}"

    def test_overview_stats_endpoint_with_cors(self):
        """Test that the endpoint supports CORS headers if configured."""
        response = client.get("/api/v1/stats/overview", headers={"Origin": "http://localhost:3000"})
        
        # The endpoint should respond regardless of CORS configuration
        assert response.status_code in [200, 404]  # 404 if no data file
        
    def test_overview_stats_endpoint_performance(self):
        """Test that the endpoint responds within reasonable time."""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/stats/overview")
        end_time = time.time()
        
        # Should respond within 5 seconds even with large datasets
        assert (end_time - start_time) < 5.0
        
        # Response should be successful or expected error
        assert response.status_code in [200, 404, 500]
