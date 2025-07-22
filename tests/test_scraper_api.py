#!/usr/bin/env python3
"""
Tests for the Books Scraper API module.

This module contains comprehensive tests for the BooksScraperAPI class
including initialization, scraping operations, and error handling.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.scraper_api import BooksScraperAPI


class TestBooksScraperAPI(unittest.TestCase):
    """Test cases for BooksScraperAPI class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.api = BooksScraperAPI(
            delay=0.1,
            max_retries=2,
            timeout=5,
            output_dir="test_data",
            logs_dir="test_logs"
        )

    def test_initialization(self) -> None:
        """Test API initialization with custom parameters."""
        self.assertEqual(self.api.delay, 0.1)
        self.assertEqual(self.api.max_retries, 2)
        self.assertEqual(self.api.timeout, 5)
        self.assertEqual(self.api.output_dir, "test_data")
        self.assertEqual(self.api.logs_dir, "test_logs")
        self.assertIsNone(self.api.scraper)
        self.assertIsNone(self.api.last_result)

    def test_initialization_with_defaults(self) -> None:
        """Test API initialization with default parameters."""
        api = BooksScraperAPI()
        
        # Should use values from config
        self.assertEqual(api.delay, 1.0)
        self.assertEqual(api.max_retries, 3)
        self.assertEqual(api.timeout, 10)
        self.assertEqual(api.output_dir, "data")
        self.assertEqual(api.logs_dir, "logs")

    @patch('scripts.scraper_api.BooksScraper')
    def test_initialize_scraper(self, mock_scraper_class) -> None:
        """Test scraper initialization."""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper

        # Test first call
        scraper = self.api._initialize_scraper()

        # Should create scraper with correct parameters
        mock_scraper_class.assert_called_with(
            delay=0.1,
            max_retries=2,
            timeout=5
        )

        # Should return the mock scraper
        self.assertEqual(scraper, mock_scraper)
        self.assertEqual(self.api.scraper, mock_scraper)

        # Test second call - should create a new instance (fresh scraper each time)
        scraper2 = self.api._initialize_scraper()
        self.assertEqual(scraper2, mock_scraper)
        # Should have called the constructor twice (always creates fresh instance)
        self.assertEqual(mock_scraper_class.call_count, 2)

    @patch('scripts.scraper_api.BooksScraper')
    def test_scrape_all_books_success(self, mock_scraper_class) -> None:
        """Test successful scraping of all books."""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper

        # Mock successful scraping
        mock_books = [
            {"title": "Book 1", "price": "£10.00", "category": "Fiction"},
            {"title": "Book 2", "price": "£15.00", "category": "Science"}
        ]
        mock_stats = {"total_books": 2, "total_categories": 2}

        mock_scraper.scrape_all_books.return_value = mock_books
        mock_scraper.get_statistics.return_value = mock_stats
        mock_scraper.save_to_csv.return_value = "test_data/books_data.csv"

        # Test scraping
        result = self.api.scrape_all_books()

        # Verify scraper method calls
        mock_scraper.scrape_all_books.assert_called_once_with(execution_type="API")
        mock_scraper.get_statistics.assert_called_once()
        mock_scraper.save_to_csv.assert_called_once_with("books_data.csv", "test_data")

        # Verify result structure
        self.assertEqual(result["books"], mock_books)
        self.assertEqual(result["total_books"], 2)
        self.assertEqual(result["total_categories"], 2)
        self.assertEqual(result["csv_file"], "test_data/books_data.csv")
        self.assertEqual(result["statistics"], mock_stats)

        # Should store last result
        self.assertEqual(self.api.last_result, result)

    @patch('scripts.scraper_api.BooksScraper')
    def test_scrape_all_books_no_save(self, mock_scraper_class) -> None:
        """Test scraping without saving to CSV."""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper

        mock_books = [{"title": "Book 1"}]
        mock_stats = {"total_books": 1}

        mock_scraper.scrape_all_books.return_value = mock_books
        mock_scraper.get_statistics.return_value = mock_stats

        # Test scraping without saving
        result = self.api.scrape_all_books(save_csv=False)

        # Should not call save_to_csv
        mock_scraper.save_to_csv.assert_not_called()

        # Should not have csv_file in result
        self.assertNotIn("csv_file", result)

    @patch('scripts.scraper_api.BooksScraper')
    def test_scrape_all_books_custom_filename(self, mock_scraper_class) -> None:
        """Test scraping with custom CSV filename."""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper

        mock_books = [{"title": "Book 1"}]
        mock_stats = {"total_books": 1}

        mock_scraper.scrape_all_books.return_value = mock_books
        mock_scraper.get_statistics.return_value = mock_stats
        mock_scraper.save_to_csv.return_value = "test_data/custom.csv"

        # Test scraping with custom filename
        result = self.api.scrape_all_books(csv_filename="custom.csv")

        # Should call save_to_csv with custom filename
        mock_scraper.save_to_csv.assert_called_once_with("custom.csv", "test_data")

    def test_get_last_result(self) -> None:
        """Test getting the last result."""
        # Initially should be None
        self.assertIsNone(self.api.get_last_result())

        # Set a result and test
        test_result = {"books": [], "total_books": 0}
        self.api.last_result = test_result
        
        self.assertEqual(self.api.get_last_result(), test_result)


if __name__ == "__main__":
    unittest.main()
