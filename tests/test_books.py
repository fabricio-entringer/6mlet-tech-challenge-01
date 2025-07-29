"""Tests for the books API endpoint."""

import csv
import json
import os
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


# Sample test data
SAMPLE_BOOKS_DATA = [
    {
        "title": "Test Book 1",
        "price": "£19.99",
        "rating_text": "Four",
        "rating_numeric": "4",
        "availability": "In stock",
        "category": "Fiction",
        "image_url": "https://example.com/book1.jpg",
    },
    {
        "title": "Test Book 2",
        "price": "£25.50",
        "rating_text": "Five",
        "rating_numeric": "5", 
        "availability": "In stock",
        "category": "Mystery",
        "image_url": "https://example.com/book2.jpg",
    },
    {
        "title": "Test Book 3",
        "price": "£12.00",
        "rating_text": "Three",
        "rating_numeric": "3",
        "availability": "Out of stock",
        "category": "Fiction",
        "image_url": "https://example.com/book3.jpg",
    },
    {
        "title": "Test Book 4",
        "price": "£35.99",
        "rating_text": "Two",
        "rating_numeric": "2",
        "availability": "In stock",
        "category": "Science",
        "image_url": "https://example.com/book4.jpg",
    },
]


@pytest.fixture
def mock_books_csv():
    """Create a temporary CSV file with test book data."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        fieldnames = ['title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(SAMPLE_BOOKS_DATA)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    os.unlink(temp_file_path)


def test_get_books_basic(mock_books_csv):
    """Test basic books endpoint functionality."""
    # Mock the data file path
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 4  # All test books
        
        # Check pagination structure
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 20
        assert pagination["total"] == 4
        assert pagination["pages"] == 1


def test_get_books_pagination(mock_books_csv):
    """Test books endpoint pagination."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        # Test with limit of 2
        response = client.get("/api/v1/books?page=1&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 2
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["total"] == 4
        assert data["pagination"]["pages"] == 2
        
        # Test second page
        response = client.get("/api/v1/books?page=2&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 2
        assert data["pagination"]["page"] == 2


def test_get_books_filtering_by_category(mock_books_csv):
    """Test books endpoint category filtering."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books?category=Fiction")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 2  # Two fiction books
        for book in data["data"]:
            assert book["category"] == "Fiction"
        
        # Check filters_applied is included
        assert "filters_applied" in data
        assert data["filters_applied"]["category"] == "Fiction"


def test_get_books_filtering_by_price_range(mock_books_csv):
    """Test books endpoint price range filtering."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        # Filter books between £15 and £30
        response = client.get("/api/v1/books?min_price=15&max_price=30")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include books with prices £19.99 and £25.50
        assert len(data["data"]) == 2
        for book in data["data"]:
            assert 15.0 <= book["price"] <= 30.0
        
        # Check filters_applied
        assert data["filters_applied"]["price_range"]["min"] == 15.0
        assert data["filters_applied"]["price_range"]["max"] == 30.0


def test_get_books_filtering_by_rating(mock_books_csv):
    """Test books endpoint rating filtering."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books?min_rating=4")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include books with rating 4 and 5
        assert len(data["data"]) == 2
        for book in data["data"]:
            assert book["rating_numeric"] >= 4
        
        assert data["filters_applied"]["min_rating"] == 4


def test_get_books_sorting_by_price(mock_books_csv):
    """Test books endpoint sorting by price."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        # Sort by price ascending
        response = client.get("/api/v1/books?sort=price&order=asc")
        
        assert response.status_code == 200
        data = response.json()
        
        prices = [book["price"] for book in data["data"]]
        assert prices == sorted(prices)  # Should be in ascending order
        
        # Sort by price descending
        response = client.get("/api/v1/books?sort=price&order=desc")
        
        assert response.status_code == 200
        data = response.json()
        
        prices = [book["price"] for book in data["data"]]
        assert prices == sorted(prices, reverse=True)  # Should be in descending order


def test_get_books_sorting_by_title(mock_books_csv):
    """Test books endpoint sorting by title."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books?sort=title&order=asc")
        
        assert response.status_code == 200
        data = response.json()
        
        titles = [book["title"] for book in data["data"]]
        assert titles == sorted(titles)  # Should be in alphabetical order


def test_get_books_sorting_by_rating(mock_books_csv):
    """Test books endpoint sorting by rating."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books?sort=rating&order=desc")
        
        assert response.status_code == 200
        data = response.json()
        
        ratings = [book["rating_numeric"] for book in data["data"]]
        assert ratings == sorted(ratings, reverse=True)


def test_get_books_combined_filters(mock_books_csv):
    """Test books endpoint with multiple filters combined."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        # Filter by category and price range
        response = client.get("/api/v1/books?category=Fiction&min_price=15&max_price=25&sort=price&order=asc")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only include Fiction books in price range
        assert len(data["data"]) == 1  # Only "Test Book 1" matches
        book = data["data"][0]
        assert book["category"] == "Fiction"
        assert 15.0 <= book["price"] <= 25.0
        
        # Check filters_applied
        filters = data["filters_applied"]
        assert filters["category"] == "Fiction"
        assert filters["price_range"]["min"] == 15.0
        assert filters["price_range"]["max"] == 25.0


def test_get_books_validation_errors():
    """Test books endpoint parameter validation."""
    # Test invalid page number
    response = client.get("/api/v1/books?page=0")
    assert response.status_code == 422
    
    # Test invalid limit
    response = client.get("/api/v1/books?limit=0")
    assert response.status_code == 422
    
    response = client.get("/api/v1/books?limit=101")
    assert response.status_code == 422
    
    # Test invalid sort field
    response = client.get("/api/v1/books?sort=invalid_field")
    assert response.status_code == 422
    
    # Test invalid order
    response = client.get("/api/v1/books?order=invalid_order")
    assert response.status_code == 422
    
    # Test invalid rating
    response = client.get("/api/v1/books?min_rating=6")
    assert response.status_code == 422
    
    response = client.get("/api/v1/books?min_rating=0")
    assert response.status_code == 422


def test_get_books_price_range_validation():
    """Test price range validation."""
    # Test min_price > max_price
    response = client.get("/api/v1/books?min_price=30&max_price=20")
    assert response.status_code == 400
    assert "min_price cannot be greater than max_price" in response.json()["detail"]


def test_get_books_empty_data():
    """Test books endpoint with empty data file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        # Create empty CSV with just headers
        fieldnames = ['title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        temp_file_path = f.name
    
    try:
        with patch('app.api.books.books_data_service.data_file', temp_file_path):
            response = client.get("/api/v1/books")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["data"] == []
            assert data["pagination"]["total"] == 0
            assert data["pagination"]["pages"] == 0
    finally:
        os.unlink(temp_file_path)


def test_get_books_nonexistent_data_file():
    """Test books endpoint when data file doesn't exist."""
    nonexistent_path = "/nonexistent/path/books_data.csv"
    
    with patch('app.api.books.books_data_service.data_file', nonexistent_path):
        response = client.get("/api/v1/books")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["data"] == []
        assert data["pagination"]["total"] == 0


def test_get_books_response_structure(mock_books_csv):
    """Test the structure of books response matches the API specification."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level structure
        assert set(data.keys()) == {"data", "pagination", "filters_applied"}
        
        # Check book structure
        if data["data"]:
            book = data["data"][0]
            expected_fields = {
                "title", "price", "price_display", "rating_text", 
                "rating_numeric", "availability", "category", "image_url"
            }
            assert set(book.keys()) == expected_fields
            
            # Check data types
            assert isinstance(book["title"], str)
            assert isinstance(book["price"], (int, float))
            assert isinstance(book["price_display"], str)
            assert isinstance(book["rating_text"], str)
            assert isinstance(book["rating_numeric"], int)
            assert isinstance(book["availability"], str)
            assert isinstance(book["category"], str)
            assert isinstance(book["image_url"], str)
        
        # Check pagination structure
        pagination = data["pagination"]
        expected_pagination_fields = {"page", "limit", "total", "pages"}
        assert set(pagination.keys()) == expected_pagination_fields
        
        # Check data types for pagination
        assert isinstance(pagination["page"], int)
        assert isinstance(pagination["limit"], int)
        assert isinstance(pagination["total"], int)
        assert isinstance(pagination["pages"], int)


@pytest.mark.asyncio
async def test_books_endpoint_content_type(mock_books_csv):
    """Test that books endpoint returns JSON content type."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books")
        assert response.headers["content-type"] == "application/json"
