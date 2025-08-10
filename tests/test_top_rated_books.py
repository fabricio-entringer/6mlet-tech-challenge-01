"""
Tests for the top-rated books endpoint.

This module contains comprehensive tests for the top-rated books functionality,
including unit tests for the service layer and integration tests for the API endpoint.
"""

import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.api.books import BooksDataService
from app.api.main import app
from app.models import TopRatedBooksResponse, TopRatedMetadata


class TestTopRatedBooksService(unittest.TestCase):
    """Test cases for the top-rated books service functionality."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.service = BooksDataService()

    def create_test_csv_file(self, books_data: list, file_path: str) -> None:
        """Helper method to create a test CSV file with book data."""
        fieldnames = [
            "id", "title", "price", "rating_text", "rating_numeric", 
            "availability", "category", "image_url", "description", "upc", "reviews"
        ]
        
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(books_data)

    @patch.object(BooksDataService, '_load_books_from_csv')
    def test_get_top_rated_books_success(self, mock_load_books) -> None:
        """Test successful retrieval of top-rated books."""
        # Mock CSV data
        mock_books_data = [
            {
                "id": "1", "title": "Excellent Book", "price": "£15.99", 
                "rating_text": "Five", "rating_numeric": "5", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/1.jpg",
                "description": "Great book", "upc": "123", "reviews": "Good"
            },
            {
                "id": "2", "title": "Amazing Book", "price": "£12.99", 
                "rating_text": "Five", "rating_numeric": "5", "availability": "In stock",
                "category": "Non-Fiction", "image_url": "http://example.com/2.jpg",
                "description": "Amazing book", "upc": "124", "reviews": "Excellent"
            },
            {
                "id": "3", "title": "Good Book", "price": "£10.99", 
                "rating_text": "Four", "rating_numeric": "4", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/3.jpg",
                "description": "Good book", "upc": "125", "reviews": "Nice"
            },
            {
                "id": "4", "title": "Average Book", "price": "£8.99", 
                "rating_text": "Three", "rating_numeric": "3", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/4.jpg",
                "description": "Average book", "upc": "126", "reviews": "OK"
            },
            {
                "id": "5", "title": "No Rating Book", "price": "£5.99", 
                "rating_text": "Unknown", "rating_numeric": "0", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/5.jpg",
                "description": "No rating", "upc": "127", "reviews": "None"
            }
        ]
        mock_load_books.return_value = mock_books_data

        # Test with default limit
        result = self.service.get_top_rated_books()

        # Assertions
        self.assertIsInstance(result, TopRatedBooksResponse)
        self.assertEqual(len(result.data), 4)  # Should exclude the book with rating 0
        
        # Check sorting: rating descending, then title ascending
        self.assertEqual(result.data[0].title, "Amazing Book")  # Five rating, alphabetically first
        self.assertEqual(result.data[1].title, "Excellent Book")  # Five rating, alphabetically second
        self.assertEqual(result.data[2].title, "Good Book")  # Four rating
        self.assertEqual(result.data[3].title, "Average Book")  # Three rating

        # Check metadata
        self.assertEqual(result.metadata.limit, 10)
        self.assertEqual(result.metadata.returned, 4)
        self.assertEqual(result.metadata.highest_rating, 5)
        self.assertEqual(result.metadata.lowest_rating, 3)

    @patch.object(BooksDataService, '_load_books_from_csv')
    def test_get_top_rated_books_with_limit(self, mock_load_books) -> None:
        """Test top-rated books with custom limit."""
        # Mock CSV data with 5 books with ratings
        mock_books_data = [
            {
                "id": str(i), "title": f"Book {i}", "price": f"£{10+i}.99", 
                "rating_text": "Five", "rating_numeric": "5", "availability": "In stock",
                "category": "Fiction", "image_url": f"http://example.com/{i}.jpg",
                "description": f"Book {i}", "upc": str(100+i), "reviews": "Good"
            }
            for i in range(1, 6)
        ]
        mock_load_books.return_value = mock_books_data

        # Test with limit of 3
        result = self.service.get_top_rated_books(limit=3)

        # Assertions
        self.assertEqual(len(result.data), 3)
        self.assertEqual(result.metadata.returned, 3)
        self.assertEqual(result.metadata.limit, 3)

    @patch.object(BooksDataService, '_load_books_from_csv')
    def test_get_top_rated_books_no_rated_books(self, mock_load_books) -> None:
        """Test behavior when no books have ratings."""
        # Mock CSV data with no ratings
        mock_books_data = [
            {
                "id": "1", "title": "Book 1", "price": "£10.99", 
                "rating_text": "Unknown", "rating_numeric": "0", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/1.jpg",
                "description": "Book 1", "upc": "123", "reviews": "None"
            },
            {
                "id": "2", "title": "Book 2", "price": "£12.99", 
                "rating_text": "Unknown", "rating_numeric": "0", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/2.jpg",
                "description": "Book 2", "upc": "124", "reviews": "None"
            }
        ]
        mock_load_books.return_value = mock_books_data

        result = self.service.get_top_rated_books()

        # Assertions
        self.assertEqual(len(result.data), 0)
        self.assertEqual(result.metadata.returned, 0)
        self.assertEqual(result.metadata.highest_rating, 0)
        self.assertEqual(result.metadata.lowest_rating, 0)

    @patch.object(BooksDataService, '_load_books_from_csv')
    def test_get_top_rated_books_sorting_with_ties(self, mock_load_books) -> None:
        """Test sorting behavior when multiple books have the same rating."""
        # Mock CSV data with books having same ratings
        mock_books_data = [
            {
                "id": "1", "title": "Zebra Book", "price": "£15.99", 
                "rating_text": "Four", "rating_numeric": "4", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/1.jpg",
                "description": "Zebra book", "upc": "123", "reviews": "Good"
            },
            {
                "id": "2", "title": "Alpha Book", "price": "£12.99", 
                "rating_text": "Four", "rating_numeric": "4", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/2.jpg",
                "description": "Alpha book", "upc": "124", "reviews": "Good"
            },
            {
                "id": "3", "title": "Beta Book", "price": "£10.99", 
                "rating_text": "Four", "rating_numeric": "4", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/3.jpg",
                "description": "Beta book", "upc": "125", "reviews": "Good"
            }
        ]
        mock_load_books.return_value = mock_books_data

        result = self.service.get_top_rated_books()

        # Check that books with same rating are sorted alphabetically by title
        self.assertEqual(result.data[0].title, "Alpha Book")
        self.assertEqual(result.data[1].title, "Beta Book")
        self.assertEqual(result.data[2].title, "Zebra Book")

    @patch.object(BooksDataService, '_load_books_from_csv')
    def test_get_top_rated_books_mixed_ratings(self, mock_load_books) -> None:
        """Test with books having various ratings."""
        # Mock CSV data with mixed ratings
        mock_books_data = [
            {
                "id": "1", "title": "One Star", "price": "£5.99", 
                "rating_text": "One", "rating_numeric": "1", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/1.jpg",
                "description": "One star", "upc": "123", "reviews": "Poor"
            },
            {
                "id": "2", "title": "Five Stars", "price": "£25.99", 
                "rating_text": "Five", "rating_numeric": "5", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/2.jpg",
                "description": "Five stars", "upc": "124", "reviews": "Excellent"
            },
            {
                "id": "3", "title": "Three Stars", "price": "£15.99", 
                "rating_text": "Three", "rating_numeric": "3", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/3.jpg",
                "description": "Three stars", "upc": "125", "reviews": "OK"
            },
            {
                "id": "4", "title": "Two Stars", "price": "£10.99", 
                "rating_text": "Two", "rating_numeric": "2", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/4.jpg",
                "description": "Two stars", "upc": "126", "reviews": "Bad"
            }
        ]
        mock_load_books.return_value = mock_books_data

        result = self.service.get_top_rated_books()

        # Check rating order: 5, 3, 2, 1
        ratings = [book.rating_numeric for book in result.data]
        self.assertEqual(ratings, [5, 3, 2, 1])

    @patch.object(BooksDataService, '_load_books_from_csv')
    def test_get_top_rated_books_invalid_data(self, mock_load_books) -> None:
        """Test behavior with invalid book data."""
        # Mock CSV data with some invalid entries
        mock_books_data = [
            {
                "id": "1", "title": "Valid Book", "price": "£15.99", 
                "rating_text": "Four", "rating_numeric": "4", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/1.jpg",
                "description": "Valid book", "upc": "123", "reviews": "Good"
            },
            {
                "id": "", "title": "", "price": "invalid", 
                "rating_text": "", "rating_numeric": "invalid", "availability": "",
                "category": "", "image_url": "", "description": "", "upc": "", "reviews": ""
            },
            {
                "id": "3", "title": "Another Valid Book", "price": "£12.99", 
                "rating_text": "Three", "rating_numeric": "3", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/3.jpg",
                "description": "Another valid book", "upc": "125", "reviews": "OK"
            }
        ]
        mock_load_books.return_value = mock_books_data

        result = self.service.get_top_rated_books()

        # Should only return valid books
        self.assertEqual(len(result.data), 2)
        self.assertEqual(result.data[0].title, "Valid Book")
        self.assertEqual(result.data[1].title, "Another Valid Book")


class TestTopRatedBooksAPI(unittest.TestCase):
    """Test cases for the top-rated books API endpoint."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.client = TestClient(app)

    @patch.object(BooksDataService, '_load_books_from_csv')
    def test_top_rated_books_endpoint_success(self, mock_load_books) -> None:
        """Test successful API call to top-rated books endpoint."""
        # Mock CSV data
        mock_books_data = [
            {
                "id": "1", "title": "Best Book", "price": "£20.99", 
                "rating_text": "Five", "rating_numeric": "5", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/1.jpg",
                "description": "Best book", "upc": "123", "reviews": "Excellent"
            },
            {
                "id": "2", "title": "Good Book", "price": "£15.99", 
                "rating_text": "Four", "rating_numeric": "4", "availability": "In stock",
                "category": "Fiction", "image_url": "http://example.com/2.jpg",
                "description": "Good book", "upc": "124", "reviews": "Good"
            }
        ]
        mock_load_books.return_value = mock_books_data

        response = self.client.get("/api/v1/books/top-rated")

        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("data", data)
        self.assertIn("metadata", data)
        self.assertEqual(len(data["data"]), 2)
        self.assertEqual(data["metadata"]["returned"], 2)
        self.assertEqual(data["metadata"]["limit"], 10)
        self.assertEqual(data["metadata"]["highest_rating"], 5)
        self.assertEqual(data["metadata"]["lowest_rating"], 4)

    @patch.object(BooksDataService, '_load_books_from_csv')
    def test_top_rated_books_endpoint_with_limit(self, mock_load_books) -> None:
        """Test API call with custom limit parameter."""
        # Mock CSV data with multiple books
        mock_books_data = [
            {
                "id": str(i), "title": f"Book {i}", "price": f"£{10+i}.99", 
                "rating_text": "Five" if i <= 3 else "Four", "rating_numeric": "5" if i <= 3 else "4", 
                "availability": "In stock", "category": "Fiction", 
                "image_url": f"http://example.com/{i}.jpg",
                "description": f"Book {i}", "upc": str(100+i), "reviews": "Good"
            }
            for i in range(1, 6)
        ]
        mock_load_books.return_value = mock_books_data

        response = self.client.get("/api/v1/books/top-rated?limit=3")

        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["data"]), 3)
        self.assertEqual(data["metadata"]["limit"], 3)
        self.assertEqual(data["metadata"]["returned"], 3)

    def test_top_rated_books_endpoint_invalid_limit(self) -> None:
        """Test API call with invalid limit parameters."""
        # Test limit too low
        response = self.client.get("/api/v1/books/top-rated?limit=0")
        self.assertEqual(response.status_code, 422)

        # Test limit too high
        response = self.client.get("/api/v1/books/top-rated?limit=101")
        self.assertEqual(response.status_code, 422)

        # Test invalid limit type
        response = self.client.get("/api/v1/books/top-rated?limit=invalid")
        self.assertEqual(response.status_code, 422)

    @patch.object(BooksDataService, '_load_books_from_csv')
    def test_top_rated_books_endpoint_no_data(self, mock_load_books) -> None:
        """Test API behavior when no books are available."""
        mock_load_books.return_value = []

        response = self.client.get("/api/v1/books/top-rated")

        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["data"]), 0)
        self.assertEqual(data["metadata"]["returned"], 0)
        self.assertEqual(data["metadata"]["highest_rating"], 0)
        self.assertEqual(data["metadata"]["lowest_rating"], 0)

    @patch.object(BooksDataService, '_load_books_from_csv')
    def test_top_rated_books_endpoint_error_handling(self, mock_load_books) -> None:
        """Test API error handling."""
        # Mock an exception during data loading
        mock_load_books.side_effect = Exception("CSV file error")

        response = self.client.get("/api/v1/books/top-rated")

        # Should return 500 error
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("Internal server error", data["detail"])


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
