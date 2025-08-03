"""Tests for category statistics API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_get_category_statistics_all():
    """Test getting statistics for all categories."""
    response = client.get("/api/v1/stats/categories")
    
    # Should return 200 even if no data exists
    assert response.status_code == 200
    
    data = response.json()
    assert "categories" in data
    assert "summary" in data
    assert isinstance(data["categories"], list)
    assert "total_categories" in data["summary"]
    assert "categories_analyzed" in data["summary"]


def test_get_category_statistics_with_filter():
    """Test getting statistics for specific categories."""
    response = client.get("/api/v1/stats/categories?categories=Fiction,Mystery")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "categories" in data
    assert "summary" in data
    
    # If data exists, verify filtering works
    if data["categories"]:
        category_names = [cat["name"] for cat in data["categories"]]
        # Should only contain requested categories (case-insensitive)
        for name in category_names:
            assert name.lower() in ["fiction", "mystery"]


def test_get_category_statistics_without_distribution():
    """Test getting statistics without rating distribution."""
    response = client.get("/api/v1/stats/categories?include_distribution=false")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # If categories exist, verify rating_distribution is not included
    if data["categories"]:
        for category in data["categories"]:
            assert "stats" in category
            # rating_distribution should be None when include_distribution=false
            assert category["stats"].get("rating_distribution") is None


def test_get_category_statistics_with_distribution():
    """Test getting statistics with rating distribution (default)."""
    response = client.get("/api/v1/stats/categories")
    
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify structure exists even if empty
    assert "categories" in data
    assert "summary" in data


def test_get_category_statistics_response_structure():
    """Test that the response has the correct structure."""
    response = client.get("/api/v1/stats/categories")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    data = response.json()
    
    # Test top-level structure
    assert "categories" in data
    assert "summary" in data
    assert isinstance(data["categories"], list)
    assert isinstance(data["summary"], dict)
    
    # Test summary structure
    summary = data["summary"]
    assert "total_categories" in summary
    assert "categories_analyzed" in summary
    assert isinstance(summary["total_categories"], int)
    assert isinstance(summary["categories_analyzed"], int)
    
    # If categories exist, test category structure
    if data["categories"]:
        category = data["categories"][0]
        assert "name" in category
        assert "slug" in category
        assert "stats" in category
        
        # Test stats structure
        stats = category["stats"]
        assert "book_count" in stats
        assert isinstance(stats["book_count"], int)
        
        # Optional fields (may be None)
        if stats.get("avg_price") is not None:
            assert isinstance(stats["avg_price"], (int, float))
        
        if stats.get("avg_rating") is not None:
            assert isinstance(stats["avg_rating"], (int, float))
        
        if stats.get("price_range") is not None:
            assert "min" in stats["price_range"]
            assert "max" in stats["price_range"]
        
        if stats.get("rating_distribution") is not None:
            rating_dist = stats["rating_distribution"]
            for rating in ["one", "two", "three", "four", "five"]:
                assert rating in rating_dist
                assert isinstance(rating_dist[rating], int)
        
        if stats.get("availability") is not None:
            availability = stats["availability"]
            assert "in_stock" in availability
            assert "out_of_stock" in availability
            assert isinstance(availability["in_stock"], int)
            assert isinstance(availability["out_of_stock"], int)


def test_get_category_statistics_empty_filter():
    """Test with empty category filter."""
    response = client.get("/api/v1/stats/categories?categories=")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "categories" in data
    assert "summary" in data


def test_get_category_statistics_nonexistent_category():
    """Test with non-existent category filter."""
    response = client.get("/api/v1/stats/categories?categories=NonExistentCategory")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "categories" in data
    assert "summary" in data
    # Should return empty list for non-existent categories
    assert len(data["categories"]) == 0


@pytest.mark.asyncio
async def test_category_statistics_endpoint_content_type():
    """Test that the endpoint returns JSON content type."""
    response = client.get("/api/v1/stats/categories")
    assert response.headers["content-type"] == "application/json"
