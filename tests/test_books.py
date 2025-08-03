"""Tests for the books API endpoint."""

import csv
import json
import os
import tempfile
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.data.csv_loader import CSVDataLoader

from app import app

client = TestClient(app)


# Sample test data
SAMPLE_BOOKS_DATA = [
    {
        "id": 1,
        "title": "Test Book 1",
        "price": "£19.99",
        "rating_text": "Four",
        "rating_numeric": "4",
        "availability": "In stock",
        "category": "Fiction",
        "image_url": "https://example.com/book1.jpg",
    },
    {
        "id": 2,
        "title": "Test Book 2",
        "price": "£25.50",
        "rating_text": "Five",
        "rating_numeric": "5", 
        "availability": "In stock",
        "category": "Mystery",
        "image_url": "https://example.com/book2.jpg",
    },
    {
        "id": 3,
        "title": "Test Book 3",
        "price": "£12.00",
        "rating_text": "Three",
        "rating_numeric": "3",
        "availability": "Out of stock",
        "category": "Fiction",
        "image_url": "https://example.com/book3.jpg",
    },
    {
        "id": 4,
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
        fieldnames = ['id', 'title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(SAMPLE_BOOKS_DATA)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    os.unlink(temp_file_path)


def test_get_books_basic(mock_books_csv):
    """Test basic books endpoint functionality."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) <= 5  # We limited to 5 books
        
        # Check pagination structure
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 5
        assert pagination["total"] == 4  # Mock data has exactly 4 books
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
        fieldnames = ['id', 'title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url']
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
                "id", "title", "price", "price_display", "rating_text", 
                "rating_numeric", "availability", "category", "image_url",
                "description", "upc", "reviews"
            }
            assert set(book.keys()) == expected_fields
            
            # Check data types
            assert isinstance(book["id"], int)
            assert isinstance(book["title"], str)
            assert isinstance(book["price"], (int, float))
            assert isinstance(book["price_display"], str)
            assert isinstance(book["rating_text"], str)
            assert isinstance(book["rating_numeric"], int)
            assert isinstance(book["availability"], str)
            assert isinstance(book["category"], str)
            assert isinstance(book["image_url"], str)
            # Optional fields can be None or strings
            assert book["description"] is None or isinstance(book["description"], str)
            assert book["upc"] is None or isinstance(book["upc"], str)
            assert book["reviews"] is None or isinstance(book["reviews"], str)
        
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


def test_get_book_by_id_success(mock_books_csv):
    """Test getting a single book by ID successfully."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books/1")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that we get a single book object
        assert "id" in data
        assert "title" in data
        assert "price" in data
        assert "category" in data
        
        # Check that the ID matches
        assert data["id"] == 1
        
        # Check that all required fields are present
        expected_fields = {
            "id", "title", "price", "price_display", "rating_text", 
            "rating_numeric", "availability", "category", "image_url",
            "description", "upc", "reviews"
        }
        assert set(data.keys()) == expected_fields


def test_get_book_by_id_not_found(mock_books_csv):
    """Test getting a book by ID that doesn't exist."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "Book with ID 999 not found" in data["detail"]


def test_get_book_by_id_invalid_format():
    """Test getting a book with invalid ID format."""
    # Test invalid negative ID
    response = client.get("/api/v1/books/-1")
    assert response.status_code == 400
    data = response.json()
    assert "Invalid book ID. Must be a positive integer." in data["detail"]
    
    # Test zero ID (should be invalid)
    response = client.get("/api/v1/books/0")
    assert response.status_code == 400
    data = response.json()
    assert "Invalid book ID. Must be a positive integer." in data["detail"]
    
    # Test non-numeric ID (FastAPI will return 422 for this)
    response = client.get("/api/v1/books/abc")
    assert response.status_code == 422


def test_get_book_by_id_specific_book(mock_books_csv):
    """Test getting a specific book by ID and verify its content."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books/2")
        
        assert response.status_code == 200
        book = response.json()
        
        # This should correspond to the second book in SAMPLE_BOOKS_DATA
        assert book["id"] == 2
        assert book["title"] == "Test Book 2"
        assert book["price"] == 25.50
        assert book["rating_numeric"] == 5
        assert book["category"] == "Mystery"


def test_get_book_by_id_boundary_cases(mock_books_csv):
    """Test boundary cases for book ID."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        # Test first book
        response = client.get("/api/v1/books/1")
        assert response.status_code == 200
        
        # Test last book (we have 4 sample books)
        response = client.get("/api/v1/books/4")
        assert response.status_code == 200
        
        # Test beyond available books
        response = client.get("/api/v1/books/5")
        assert response.status_code == 404


def test_get_book_by_id_empty_data_file():
    """Test getting a book by ID when data file is empty."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        # Create empty CSV with just headers
        fieldnames = ['id', 'title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        temp_file_path = f.name
    
    try:
        with patch('app.api.books.books_data_service.data_file', temp_file_path):
            response = client.get("/api/v1/books/1")
            
            assert response.status_code == 404
            data = response.json()
            assert "Book with ID 1 not found" in data["detail"]
    finally:
        os.unlink(temp_file_path)


def test_get_book_by_id_nonexistent_data_file():
    """Test getting a book by ID when data file doesn't exist."""
    nonexistent_path = "/nonexistent/path/books_data.csv"
    
    with patch('app.api.books.books_data_service.data_file', nonexistent_path):
        response = client.get("/api/v1/books/1")
        
        assert response.status_code == 404
        data = response.json()
        assert "Book with ID 1 not found" in data["detail"]


def test_get_top_rated_books_success(mock_books_csv):
    """Test getting top-rated books successfully."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books/top-rated")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "data" in data
        assert "metadata" in data
        assert isinstance(data["data"], list)
        
        # Check metadata structure
        metadata = data["metadata"]
        expected_metadata_fields = {"limit", "returned", "highest_rating", "lowest_rating"}
        assert set(metadata.keys()) == expected_metadata_fields
        
        # Should return books sorted by rating descending
        ratings = [book["rating_numeric"] for book in data["data"]]
        assert ratings == sorted(ratings, reverse=True)
        
        # Default limit should be 10
        assert metadata["limit"] == 10
        # Should return 4 books (all from sample data have ratings)
        assert metadata["returned"] == 4
        assert metadata["highest_rating"] == 5
        assert metadata["lowest_rating"] == 2


def test_get_top_rated_books_with_limit(mock_books_csv):
    """Test getting top-rated books with custom limit."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books/top-rated?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 2
        assert data["metadata"]["limit"] == 2
        assert data["metadata"]["returned"] == 2
        
        # Should get the top 2 rated books
        ratings = [book["rating_numeric"] for book in data["data"]]
        assert ratings[0] >= ratings[1]  # First should be >= second


def test_get_top_rated_books_sorting_with_ties(mock_books_csv):
    """Test that books with same rating are sorted by title."""
    # Create sample data with books having same ratings
    books_with_ties = [
        {
            "id": 1,
            "title": "Zebra Book",
            "price": "£15.99",
            "rating_text": "Four",
            "rating_numeric": "4",
            "availability": "In stock",
            "category": "Fiction",
            "image_url": "https://example.com/zebra.jpg",
        },
        {
            "id": 2,
            "title": "Alpha Book",
            "price": "£12.99",
            "rating_text": "Four",
            "rating_numeric": "4",
            "availability": "In stock",
            "category": "Fiction",
            "image_url": "https://example.com/alpha.jpg",
        },
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        fieldnames = ['id', 'title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books_with_ties)
        temp_file_path = f.name
    
    try:
        with patch('app.api.books.books_data_service.data_file', temp_file_path):
            response = client.get("/api/v1/books/top-rated")
            
            assert response.status_code == 200
            data = response.json()
            
            # Books with same rating should be sorted alphabetically by title
            assert data["data"][0]["title"] == "Alpha Book"
            assert data["data"][1]["title"] == "Zebra Book"
    finally:
        os.unlink(temp_file_path)


def test_get_top_rated_books_excludes_no_rating():
    """Test that books without ratings are excluded."""
    books_with_no_rating = [
        {
            "id": 1,
            "title": "Rated Book",
            "price": "£15.99",
            "rating_text": "Four",
            "rating_numeric": "4",
            "availability": "In stock",
            "category": "Fiction",
            "image_url": "https://example.com/rated.jpg",
        },
        {
            "id": 2,
            "title": "Unrated Book",
            "price": "£12.99",
            "rating_text": "Unknown",
            "rating_numeric": "0",
            "availability": "In stock",
            "category": "Fiction",
            "image_url": "https://example.com/unrated.jpg",
        },
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        fieldnames = ['id', 'title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books_with_no_rating)
        temp_file_path = f.name
    
    try:
        with patch('app.api.books.books_data_service.data_file', temp_file_path):
            response = client.get("/api/v1/books/top-rated")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should only return the book with rating
            assert len(data["data"]) == 1
            assert data["data"][0]["title"] == "Rated Book"
            assert data["metadata"]["returned"] == 1
    finally:
        os.unlink(temp_file_path)


def test_get_top_rated_books_validation_errors():
    """Test top-rated books endpoint parameter validation."""
    # Test limit too low
    response = client.get("/api/v1/books/top-rated?limit=0")
    assert response.status_code == 422
    
    # Test limit too high
    response = client.get("/api/v1/books/top-rated?limit=101")
    assert response.status_code == 422
    
    # Test invalid limit type
    response = client.get("/api/v1/books/top-rated?limit=invalid")
    assert response.status_code == 422


def test_get_top_rated_books_empty_data():
    """Test top-rated books endpoint with empty data."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        fieldnames = ['id', 'title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        temp_file_path = f.name
    
    try:
        with patch('app.api.books.books_data_service.data_file', temp_file_path):
            response = client.get("/api/v1/books/top-rated")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["data"] == []
            assert data["metadata"]["returned"] == 0
            assert data["metadata"]["highest_rating"] == 0
            assert data["metadata"]["lowest_rating"] == 0
    finally:
        os.unlink(temp_file_path)


def test_get_top_rated_books_response_structure(mock_books_csv):
    """Test the structure of top-rated books response."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books/top-rated")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level structure
        assert set(data.keys()) == {"data", "metadata"}
        
        # Check book structure (same as regular books endpoint)
        if data["data"]:
            book = data["data"][0]
            expected_fields = {
                "id", "title", "price", "price_display", "rating_text", 
                "rating_numeric", "availability", "category", "image_url",
                "description", "upc", "reviews"
            }
            assert set(book.keys()) == expected_fields
        
        # Check metadata structure
        metadata = data["metadata"]
        expected_metadata_fields = {"limit", "returned", "highest_rating", "lowest_rating"}
        assert set(metadata.keys()) == expected_metadata_fields
        
        # Check data types for metadata
        assert isinstance(metadata["limit"], int)
        assert isinstance(metadata["returned"], int)
        assert isinstance(metadata["highest_rating"], int)
        assert isinstance(metadata["lowest_rating"], int)


def test_get_books_by_price_range_success(mock_books_csv):
    """Test getting books by price range successfully."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books/price-range?min_price=15&max_price=30")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "price_range" in data
        assert "data" in data
        assert "metadata" in data
        assert "pagination" in data
        
        # Check price_range structure
        price_range = data["price_range"]
        assert price_range["min"] == 15.0
        assert price_range["max"] == 30.0
        
        # Check that all returned books are within the price range
        for book in data["data"]:
            assert 15.0 <= book["price"] <= 30.0
        
        # Should return 2 books (£19.99 and £25.50)
        assert len(data["data"]) == 2
        
        # Check metadata structure
        metadata = data["metadata"]
        assert "count" in metadata
        assert "avg_price" in metadata
        assert "price_distribution" in metadata
        assert metadata["count"] == 2


def test_get_books_by_price_range_metadata(mock_books_csv):
    """Test price range metadata calculations."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books/price-range?min_price=10&max_price=40")
        
        assert response.status_code == 200
        data = response.json()
        
        metadata = data["metadata"]
        
        # Should return 3 books (£12.00, £19.99, £25.50, £35.99)
        assert metadata["count"] == 4
        
        # Check average price calculation
        expected_avg = (12.00 + 19.99 + 25.50 + 35.99) / 4
        assert abs(metadata["avg_price"] - expected_avg) < 0.01
        
        # Check price distribution exists
        assert isinstance(metadata["price_distribution"], dict)
        assert len(metadata["price_distribution"]) == 4  # 4 ranges


def test_get_books_by_price_range_pagination(mock_books_csv):
    """Test price range endpoint with pagination."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        # Get first page with limit of 1
        response = client.get("/api/v1/books/price-range?min_price=10&max_price=40&page=1&limit=1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 1
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 1
        assert pagination["total"] == 4
        assert pagination["pages"] == 4
        
        # Get second page
        response = client.get("/api/v1/books/price-range?min_price=10&max_price=40&page=2&limit=1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 1
        assert data["pagination"]["page"] == 2


def test_get_books_by_price_range_sorting(mock_books_csv):
    """Test price range endpoint sorting."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        # Sort by price ascending (default)
        response = client.get("/api/v1/books/price-range?min_price=10&max_price=40&sort=price&order=asc")
        
        assert response.status_code == 200
        data = response.json()
        
        prices = [book["price"] for book in data["data"]]
        assert prices == sorted(prices)
        
        # Sort by price descending
        response = client.get("/api/v1/books/price-range?min_price=10&max_price=40&sort=price&order=desc")
        
        assert response.status_code == 200
        data = response.json()
        
        prices = [book["price"] for book in data["data"]]
        assert prices == sorted(prices, reverse=True)
        
        # Sort by title
        response = client.get("/api/v1/books/price-range?min_price=10&max_price=40&sort=title&order=asc")
        
        assert response.status_code == 200
        data = response.json()
        
        titles = [book["title"] for book in data["data"]]
        assert titles == sorted(titles)


def test_get_books_by_price_range_exact_boundaries(mock_books_csv):
    """Test price range with exact boundary values."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        # Test with exact book price as boundary
        response = client.get("/api/v1/books/price-range?min_price=19.99&max_price=19.99")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return exactly one book
        assert len(data["data"]) == 1
        assert data["data"][0]["price"] == 19.99
        assert data["metadata"]["count"] == 1


def test_get_books_by_price_range_no_results(mock_books_csv):
    """Test price range with no matching books."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        # Price range with no books
        response = client.get("/api/v1/books/price-range?min_price=100&max_price=200")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 0
        assert data["metadata"]["count"] == 0
        assert data["metadata"]["avg_price"] == 0.0
        assert data["pagination"]["total"] == 0
        assert data["pagination"]["pages"] == 0


def test_get_books_by_price_range_validation():
    """Test price range endpoint parameter validation."""
    # Test missing min_price
    response = client.get("/api/v1/books/price-range?max_price=30")
    assert response.status_code == 422
    
    # Test missing max_price
    response = client.get("/api/v1/books/price-range?min_price=10")
    assert response.status_code == 422
    
    # Test negative prices
    response = client.get("/api/v1/books/price-range?min_price=-5&max_price=30")
    assert response.status_code == 422  # FastAPI validates negative numbers at Query level
    
    response = client.get("/api/v1/books/price-range?min_price=10&max_price=-5")
    assert response.status_code == 422  # FastAPI validates negative numbers at Query level
    
    # Test min_price > max_price
    response = client.get("/api/v1/books/price-range?min_price=30&max_price=20")
    assert response.status_code == 400
    assert "min_price cannot be greater than max_price" in response.json()["detail"]
    
    # Test invalid page number
    response = client.get("/api/v1/books/price-range?min_price=10&max_price=30&page=0")
    assert response.status_code == 422
    
    # Test invalid limit
    response = client.get("/api/v1/books/price-range?min_price=10&max_price=30&limit=0")
    assert response.status_code == 422
    
    response = client.get("/api/v1/books/price-range?min_price=10&max_price=30&limit=101")
    assert response.status_code == 422
    
    # Test invalid sort field
    response = client.get("/api/v1/books/price-range?min_price=10&max_price=30&sort=invalid")
    assert response.status_code == 422
    
    # Test invalid order
    response = client.get("/api/v1/books/price-range?min_price=10&max_price=30&order=invalid")
    assert response.status_code == 422


def test_get_books_by_price_range_edge_cases(mock_books_csv):
    """Test price range endpoint edge cases."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        # Test with zero as min_price
        response = client.get("/api/v1/books/price-range?min_price=0&max_price=15")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return one book (£12.00)
        assert len(data["data"]) == 1
        assert data["data"][0]["price"] == 12.00
        
        # Test with very large max_price
        response = client.get("/api/v1/books/price-range?min_price=0&max_price=1000")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return all books
        assert len(data["data"]) == 4
        assert data["metadata"]["count"] == 4


def test_get_books_by_price_range_price_distribution(mock_books_csv):
    """Test price distribution calculation."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books/price-range?min_price=10&max_price=40")
        
        assert response.status_code == 200
        data = response.json()
        
        price_distribution = data["metadata"]["price_distribution"]
        
        # Should have 4 ranges
        assert len(price_distribution) == 4
        
        # Each range should be a string key with integer count
        for range_key, count in price_distribution.items():
            assert isinstance(range_key, str)
            assert isinstance(count, int)
            assert count >= 0
            assert "-" in range_key  # Should be in format "min-max"
        
        # Total count across ranges should equal total books
        total_distributed = sum(price_distribution.values())
        assert total_distributed == data["metadata"]["count"]


def test_get_books_by_price_range_equal_min_max(mock_books_csv):
    """Test price range where min equals max."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        # This should work but may return no books if no exact price match
        response = client.get("/api/v1/books/price-range?min_price=15.50&max_price=15.50")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return empty results since no book has exactly £15.50
        assert len(data["data"]) == 0
        assert data["metadata"]["count"] == 0


def test_get_books_by_price_range_response_structure(mock_books_csv):
    """Test the structure of price range response matches specification."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books/price-range?min_price=10&max_price=30")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check top-level structure
        expected_top_level = {"price_range", "data", "metadata", "pagination"}
        assert set(data.keys()) == expected_top_level
        
        # Check price_range structure
        price_range = data["price_range"]
        assert set(price_range.keys()) == {"min", "max"}
        assert isinstance(price_range["min"], (int, float))
        assert isinstance(price_range["max"], (int, float))
        
        # Check metadata structure
        metadata = data["metadata"]
        expected_metadata_fields = {"count", "avg_price", "price_distribution"}
        assert set(metadata.keys()) == expected_metadata_fields
        assert isinstance(metadata["count"], int)
        assert isinstance(metadata["avg_price"], (int, float))
        assert isinstance(metadata["price_distribution"], dict)
        
        # Check pagination structure (same as other endpoints)
        pagination = data["pagination"]
        expected_pagination_fields = {"page", "limit", "total", "pages"}
        assert set(pagination.keys()) == expected_pagination_fields
        
        # Check book structure (same as other endpoints)
        if data["data"]:
            book = data["data"][0]
            expected_book_fields = {
                "id", "title", "price", "price_display", "rating_text", 
                "rating_numeric", "availability", "category", "image_url",
                "description", "upc", "reviews"
            }
            assert set(book.keys()) == expected_book_fields


def test_get_books_by_price_range_empty_data():
    """Test price range endpoint with empty data file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        fieldnames = ['id', 'title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        temp_file_path = f.name
    
    try:
        with patch('app.api.books.books_data_service.data_file', temp_file_path):
            response = client.get("/api/v1/books/price-range?min_price=10&max_price=30")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["data"] == []
            assert data["metadata"]["count"] == 0
            assert data["metadata"]["avg_price"] == 0.0
            assert data["metadata"]["price_distribution"] == {}
            assert data["pagination"]["total"] == 0
    finally:
        os.unlink(temp_file_path)


def test_get_books_by_price_range_nonexistent_file():
    """Test price range endpoint when data file doesn't exist."""
    nonexistent_path = "/nonexistent/path/books_data.csv"
    
    with patch('app.api.books.books_data_service.data_file', nonexistent_path):
        response = client.get("/api/v1/books/price-range?min_price=10&max_price=30")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["data"] == []
        assert data["metadata"]["count"] == 0


@pytest.mark.asyncio
async def test_price_range_endpoint_content_type(mock_books_csv):
    """Test that price range endpoint returns JSON content type."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books/price-range?min_price=10&max_price=30")
        assert response.headers["content-type"] == "application/json"


def test_get_books_by_price_range_default_sort(mock_books_csv):
    """Test that price range endpoint defaults to sorting by price."""
    with patch('app.api.books.books_data_service.data_file', mock_books_csv):
        response = client.get("/api/v1/books/price-range?min_price=10&max_price=40")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be sorted by price ascending by default
        prices = [book["price"] for book in data["data"]]
        assert prices == sorted(prices)


def test_get_books_by_price_range_single_book_range():
    """Test price range that matches exactly one book."""
    single_book_data = [
        {
            "id": 1,
            "title": "Single Book",
            "price": "£20.00",
            "rating_text": "Four",
            "rating_numeric": "4",
            "availability": "In stock",
            "category": "Fiction",
            "image_url": "https://example.com/single.jpg",
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        fieldnames = ['id', 'title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(single_book_data)
        temp_file_path = f.name
    
    try:
        with patch('app.api.books.books_data_service.data_file', temp_file_path):
            response = client.get("/api/v1/books/price-range?min_price=19&max_price=21")
            
            assert response.status_code == 200
            data = response.json()
            
            assert len(data["data"]) == 1
            assert data["data"][0]["title"] == "Single Book"
            assert data["metadata"]["count"] == 1
            assert data["metadata"]["avg_price"] == 20.0
            
            # Price distribution should have one range with count 1 for a small range
            price_distribution = data["metadata"]["price_distribution"]
            assert len(price_distribution) == 1  # Small range should create single distribution
            assert sum(price_distribution.values()) == 1
    finally:
        os.unlink(temp_file_path)
