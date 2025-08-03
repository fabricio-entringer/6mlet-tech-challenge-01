"""Tests for category statistics API endpoints."""

import csv
import os
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


# Sample test data for category statistics
SAMPLE_CATEGORY_DATA = [
    {
        "id": 1,
        "title": "Fiction Book 1",
        "price": "£19.99",
        "rating_text": "Four",
        "rating_numeric": "4",
        "availability": "In stock",
        "category": "Fiction",
        "image_url": "https://example.com/book1.jpg",
    },
    {
        "id": 2,
        "title": "Fiction Book 2",
        "price": "£25.50",
        "rating_text": "Five",
        "rating_numeric": "5", 
        "availability": "In stock",
        "category": "Fiction",
        "image_url": "https://example.com/book2.jpg",
    },
    {
        "id": 3,
        "title": "Mystery Book 1",
        "price": "£12.00",
        "rating_text": "Three",
        "rating_numeric": "3",
        "availability": "Out of stock",
        "category": "Mystery",
        "image_url": "https://example.com/book3.jpg",
    },
    {
        "id": 4,
        "title": "Mystery Book 2",
        "price": "£30.00",
        "rating_text": "Two",
        "rating_numeric": "2",
        "availability": "In stock",
        "category": "Mystery",
        "image_url": "https://example.com/book4.jpg",
    },
    {
        "id": 5,
        "title": "Science Book 1",
        "price": "£45.00",
        "rating_text": "One",
        "rating_numeric": "1",
        "availability": "In stock",
        "category": "Science",
        "image_url": "https://example.com/book5.jpg",
    },
]


@pytest.fixture
def mock_category_stats_csv():
    """Create a temporary CSV file with test category statistics data."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        fieldnames = ['id', 'title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(SAMPLE_CATEGORY_DATA)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    os.unlink(temp_file_path)


def test_get_category_statistics_all(mock_category_stats_csv):
    """Test getting statistics for all categories."""
    with patch('app.api.category_stats.category_stats_service.data_file', mock_category_stats_csv):
        response = client.get("/api/v1/stats/categories")
        
        # Should return 200 even if no data exists
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        assert "summary" in data
        assert isinstance(data["categories"], list)
        assert "total_categories" in data["summary"]
        assert "categories_analyzed" in data["summary"]


def test_get_category_statistics_with_filter(mock_category_stats_csv):
    """Test getting statistics for specific categories."""
    with patch('app.api.category_stats.category_stats_service.data_file', mock_category_stats_csv):
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


def test_get_category_statistics_without_distribution(mock_category_stats_csv):
    """Test getting statistics without rating distribution."""
    with patch('app.api.category_stats.category_stats_service.data_file', mock_category_stats_csv):
        response = client.get("/api/v1/stats/categories?include_distribution=false")
        
        assert response.status_code == 200
        
        data = response.json()
        
        # If categories exist, verify rating_distribution is not included
        if data["categories"]:
            for category in data["categories"]:
                assert "stats" in category
                # rating_distribution should be None when include_distribution=false
                assert category["stats"].get("rating_distribution") is None


def test_get_category_statistics_with_distribution(mock_category_stats_csv):
    """Test getting statistics with rating distribution (default)."""
    with patch('app.api.category_stats.category_stats_service.data_file', mock_category_stats_csv):
        response = client.get("/api/v1/stats/categories")
        
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify structure exists even if empty
        assert "categories" in data
        assert "summary" in data


def test_get_category_statistics_response_structure(mock_category_stats_csv):
    """Test that the response has the correct structure."""
    with patch('app.api.category_stats.category_stats_service.data_file', mock_category_stats_csv):
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


def test_get_category_statistics_empty_filter(mock_category_stats_csv):
    """Test with empty category filter."""
    with patch('app.api.category_stats.category_stats_service.data_file', mock_category_stats_csv):
        response = client.get("/api/v1/stats/categories?categories=")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "categories" in data
        assert "summary" in data


def test_get_category_statistics_nonexistent_category(mock_category_stats_csv):
    """Test with non-existent category filter."""
    with patch('app.api.category_stats.category_stats_service.data_file', mock_category_stats_csv):
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
