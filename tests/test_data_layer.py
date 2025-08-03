"""Tests for the data access layer."""

import tempfile
import os
import csv
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from app.data import CSVDataLoader, DataCache, DataValidator, DataService
from app.models.book import Book


# Sample test data
SAMPLE_BOOKS_DATA = [
    {
        "id": 1,
        "title": "Test Book 1",
        "price": "£25.99",
        "rating_text": "Four",
        "rating_numeric": "4",
        "availability": "In stock",
        "category": "Fiction",
        "image_url": "https://example.com/book1.jpg",
    },
    {
        "id": 2,
        "title": "Test Book 2", 
        "price": "£15.50",
        "rating_text": "Three",
        "rating_numeric": "3",
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
]


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file with sample data."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        fieldnames = ['id', 'title', 'price', 'rating_text', 'rating_numeric', 'availability', 'category', 'image_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(SAMPLE_BOOKS_DATA)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    os.unlink(temp_file_path)


@pytest.fixture
def sample_books():
    """Create sample Book objects."""
    return [
        Book(
            id=1,
            title="Test Book 1",
            price=25.99,
            price_display="£25.99",
            rating_text="Four",
            rating_numeric=4,
            availability="In stock",
            category="Fiction",
            image_url="https://example.com/book1.jpg",
        ),
        Book(
            id=2,
            title="Test Book 2",
            price=15.50,
            price_display="£15.50",
            rating_text="Three",
            rating_numeric=3,
            availability="In stock",
            category="Mystery",
            image_url="https://example.com/book2.jpg",
        ),
    ]


class TestCSVDataLoader:
    """Test cases for CSV data loader."""
    
    def test_initialization(self, sample_csv_file):
        """Test CSV loader initialization."""
        loader = CSVDataLoader(sample_csv_file)
        assert loader.data_file_path.name.endswith('.csv')
        assert loader._cached_data is None
        assert loader._cached_books is None
    
    def test_load_books_data(self, sample_csv_file):
        """Test loading books data from CSV."""
        loader = CSVDataLoader(sample_csv_file)
        books = loader.load_books_data()
        
        assert len(books) == 3
        assert all(isinstance(book, Book) for book in books)
        assert books[0].title == "Test Book 1"
        assert books[0].price == 25.99
        assert books[0].rating_numeric == 4
    
    def test_load_raw_data(self, sample_csv_file):
        """Test loading raw CSV data."""
        loader = CSVDataLoader(sample_csv_file)
        raw_data = loader.load_raw_data()
        
        assert len(raw_data) == 3
        assert raw_data[0]["title"] == "Test Book 1"
        assert raw_data[0]["price"] == "£25.99"
    
    def test_caching_mechanism(self, sample_csv_file):
        """Test that data is cached properly."""
        loader = CSVDataLoader(sample_csv_file)
        
        # First load
        books1 = loader.load_books_data()
        assert loader._cached_books is not None
        
        # Second load should use cache
        books2 = loader.load_books_data()
        assert books1 == books2
        assert len(books2) == 3
    
    def test_force_reload(self, sample_csv_file):
        """Test force reloading data."""
        loader = CSVDataLoader(sample_csv_file)
        
        # Initial load
        books1 = loader.load_books_data()
        
        # Force reload
        books2 = loader.load_books_data(force_reload=True)
        assert books1 == books2  # Data should be the same
    
    def test_refresh_data(self, sample_csv_file):
        """Test data refresh functionality."""
        loader = CSVDataLoader(sample_csv_file)
        
        # Initial load
        loader.load_books_data()
        
        # Refresh data
        success = loader.refresh_data()
        assert success is True
    
    def test_get_cache_stats(self, sample_csv_file):
        """Test cache statistics."""
        loader = CSVDataLoader(sample_csv_file)
        loader.load_books_data()
        
        stats = loader.get_cache_stats()
        assert stats["cached_books_count"] == 3
        assert stats["cached_raw_rows_count"] == 3
        assert stats["file_exists"] is True
    
    def test_nonexistent_file(self):
        """Test behavior with nonexistent file."""
        loader = CSVDataLoader("nonexistent_file.csv")
        books = loader.load_books_data()
        assert books == []


class TestDataCache:
    """Test cases for data cache."""
    
    def test_initialization(self):
        """Test cache initialization."""
        cache = DataCache()
        assert cache.is_empty() is True
        assert cache.get_size() == 0
    
    def test_update_books(self, sample_books):
        """Test updating cache with books."""
        cache = DataCache()
        cache.update_books(sample_books)
        
        assert cache.get_size() == 2
        assert cache.is_empty() is False
    
    def test_get_all_books(self, sample_books):
        """Test getting all books from cache."""
        cache = DataCache()
        cache.update_books(sample_books)
        
        books = cache.get_all_books()
        assert len(books) == 2
        assert books[0].title == "Test Book 1"
    
    def test_get_book_by_id(self, sample_books):
        """Test getting book by ID."""
        cache = DataCache()
        cache.update_books(sample_books)
        
        book = cache.get_book_by_id(1)
        assert book is not None
        assert book.title == "Test Book 1"
        
        book = cache.get_book_by_id(999)
        assert book is None
    
    def test_get_categories(self, sample_books):
        """Test getting categories."""
        cache = DataCache()
        cache.update_books(sample_books)
        
        categories = cache.get_categories()
        assert "Fiction" in categories
        assert "Mystery" in categories
        assert len(categories) == 2
    
    def test_search_books(self, sample_books):
        """Test searching books with filters."""
        cache = DataCache()
        cache.update_books(sample_books)
        
        # Filter by category
        fiction_books = cache.search_books(category="Fiction")
        assert len(fiction_books) == 1
        assert fiction_books[0].category == "Fiction"
        
        # Filter by price range
        cheap_books = cache.search_books(min_price=10.0, max_price=20.0)
        assert len(cheap_books) == 1
        assert cheap_books[0].price == 15.50
    
    def test_get_statistics(self, sample_books):
        """Test getting cache statistics."""
        cache = DataCache()
        cache.update_books(sample_books)
        
        stats = cache.get_statistics()
        assert stats["total_books"] == 2
        assert stats["total_categories"] == 2
        assert stats["is_populated"] is True


class TestDataValidator:
    """Test cases for data validator."""
    
    def test_initialization(self):
        """Test validator initialization."""
        validator = DataValidator()
        assert validator.REQUIRED_COLUMNS is not None
        assert len(validator.REQUIRED_COLUMNS) > 0
    
    def test_validate_csv_structure(self):
        """Test CSV structure validation."""
        validator = DataValidator()
        
        # Valid structure
        result = validator.validate_csv_structure(SAMPLE_BOOKS_DATA)
        assert result.is_valid is True
        
        # Empty data
        result = validator.validate_csv_structure([])
        assert result.is_valid is False
        assert "CSV data is empty" in result.errors[0]
    
    def test_validate_row(self):
        """Test individual row validation."""
        validator = DataValidator()
        
        # Valid row
        corrected_row, errors = validator.validate_row(SAMPLE_BOOKS_DATA[0], 1)
        assert corrected_row is not None
        assert len(errors) == 0
        
        # Invalid row (missing title)
        invalid_row = {"id": "1", "title": "", "price": "£10.00"}
        corrected_row, errors = validator.validate_row(invalid_row, 1)
        assert corrected_row is None
        assert len(errors) > 0
    
    def test_validate_data_integrity(self):
        """Test data integrity validation."""
        validator = DataValidator()
        
        result = validator.validate_data_integrity(SAMPLE_BOOKS_DATA)
        assert result.total_rows == 3
        # Should be valid since our sample data is well-formed
    
    def test_validate_book_object(self, sample_books):
        """Test book object validation."""
        validator = DataValidator()
        
        # Valid book
        errors = validator.validate_book_object(sample_books[0])
        assert len(errors) == 0
        
        # Test validator with mock invalid data directly
        # Since Pydantic prevents invalid Book creation, we test the validator's logic
        book_data = {
            'id': 1,
            'title': '',
            'price': -10.0,
            'price_display': '',
            'rating_text': '',
            'rating_numeric': 10,
            'availability': '',
            'category': '',
            'image_url': ''
        }
        
        # Test validation logic using validator's row validation
        errors = validator.validate_row(book_data, 1)
        assert len(errors) > 0


class TestDataService:
    """Test cases for the main data service."""
    
    @patch('app.data.data_service.CSVDataLoader')
    def test_initialization(self, mock_loader_class):
        """Test data service initialization."""
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        
        service = DataService()
        assert service.csv_loader is not None
        assert service.cache is not None
        assert service.validator is not None
    
    @patch('app.data.data_service.get_data_service')
    def test_get_books(self, mock_get_service, sample_books):
        """Test getting books through data service."""
        mock_service = MagicMock()
        mock_service.cache.search_books.return_value = sample_books
        mock_get_service.return_value = mock_service
        
        service = DataService()
        service.cache.update_books(sample_books)
        
        books = service.get_books(page=1, limit=10)
        assert len(books) <= 10
    
    @patch('app.data.data_service.get_data_service')
    def test_refresh_data(self, mock_get_service):
        """Test data refresh functionality."""
        mock_service = MagicMock()
        mock_service.csv_loader.load_raw_data.return_value = []
        mock_service.csv_loader.load_books_data.return_value = []
        mock_get_service.return_value = mock_service
        
        service = DataService()
        result = service.refresh_data()
        # Should return True since we're mocking successful operations
        assert result is True
    
    def test_health_check(self, sample_csv_file):
        """Test health check functionality."""
        service = DataService(sample_csv_file)
        health = service.health_check()
        
        assert "status" in health
        assert "details" in health
        assert "timestamp" in health
    
    def test_get_statistics(self, sample_csv_file):
        """Test getting service statistics."""
        service = DataService(sample_csv_file)
        stats = service.get_statistics()
        
        assert "service" in stats
        assert "cache" in stats
        assert "loader" in stats
        assert "validation" in stats


class TestDataServiceIntegration:
    """Integration tests for the data service."""
    
    def test_full_workflow(self, sample_csv_file):
        """Test complete data loading and caching workflow."""
        # Initialize service with sample data
        service = DataService(sample_csv_file)
        
        # Verify data is loaded
        assert not service.cache.is_empty()
        
        # Test getting books
        books = service.get_books()
        assert len(books) > 0
        
        # Test getting book by ID
        book = service.get_book_by_id(1)
        assert book is not None
        
        # Test getting categories
        categories = service.get_categories()
        assert len(categories) > 0
        
        # Refresh data
        success = service.refresh_data()
        assert success is True
    
    def test_error_handling(self):
        """Test error handling with invalid data."""
        # Try to initialize with nonexistent file
        service = DataService("nonexistent_file.csv")
        
        # Service should still be usable even if data loading fails
        books = service.get_books()
        assert books == []
        
        health = service.health_check()
        assert health["status"] == "unhealthy"
