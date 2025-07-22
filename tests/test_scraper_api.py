"""
Tests for the books scraper API module.

This module contains tests for the BooksScraperAPI class and its methods.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.scraper_api import BooksScraperAPI


class TestBooksScraperAPI(unittest.TestCase):
    """Test cases for the BooksScraperAPI class."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.api = BooksScraperAPI(
            delay=0.1,
            max_retries=2,
            timeout=5
        )
    
    def test_initialization(self) -> None:
        """Test API initialization."""
        self.assertEqual(self.api.delay, 0.1)
        self.assertEqual(self.api.max_retries, 2)
        self.assertEqual(self.api.timeout, 5)
        self.assertIsNone(self.api.scraper)
        self.assertIsNone(self.api.last_result)
    
    def test_initialization_with_defaults(self) -> None:
        """Test API initialization with default values."""
        api = BooksScraperAPI()
        self.assertEqual(api.delay, 1.0)  # Default from config
        self.assertEqual(api.max_retries, 3)  # Default from config
        self.assertEqual(api.timeout, 10)  # Default from config
    
    @patch('scripts.scraper_api.BooksScraper')
    def test_initialize_scraper(self, mock_scraper_class) -> None:
        """Test scraper initialization."""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        scraper = self.api._initialize_scraper()
        
        # Should create scraper with correct parameters
        mock_scraper_class.assert_called_once_with(
            delay=0.1,
            max_retries=2,
            timeout=5
        )
        
        # Should return the mock scraper
        self.assertEqual(scraper, mock_scraper)
        self.assertEqual(self.api.scraper, mock_scraper)
        
        # Second call should return existing scraper
        scraper2 = self.api._initialize_scraper()
        self.assertEqual(scraper2, mock_scraper)
        self.assertEqual(mock_scraper_class.call_count, 1)  # Should not create another
    
    @patch('scripts.scraper_api.BooksScraper')
    def test_scrape_all_books_success(self, mock_scraper_class) -> None:
        """Test successful scraping of all books."""
        # Setup mock scraper
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        # Mock data
        mock_books = [
            {"title": "Book 1", "category": "Fiction"},
            {"title": "Book 2", "category": "Science"}
        ]
        mock_stats = {
            "total_books": 2,
            "total_categories": 2,
            "categories_breakdown": {"Fiction": 1, "Science": 1}
        }
        
        mock_scraper.scrape_all_books.return_value = mock_books
        mock_scraper.get_statistics.return_value = mock_stats
        mock_scraper.save_to_csv.return_value = "data/books_data.csv"
        
        # Test scraping
        result = self.api.scrape_all_books()
        
        # Verify calls
        mock_scraper.scrape_all_books.assert_called_once()
        mock_scraper.get_statistics.assert_called_once()
        mock_scraper.save_to_csv.assert_called_once()
        
        # Verify result
        self.assertEqual(result["books"], mock_books)
        self.assertEqual(result["total_books"], 2)
        self.assertEqual(result["total_categories"], 2)
        self.assertEqual(result["statistics"], mock_stats)
        self.assertEqual(result["csv_file"], "data/books_data.csv")
        
        # Verify last_result is stored
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
    def test_scrape_sample(self, mock_scraper_class) -> None:
        """Test sample scraping functionality."""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        # Mock categories
        mock_categories = [
            {"name": "Fiction", "url": "http://example.com/fiction"},
            {"name": "Science", "url": "http://example.com/science"}
        ]
        
        # Mock category books (more than max_books to test limiting)
        fiction_books = [{"title": f"Fiction Book {i}", "category": "Fiction"} for i in range(30)]
        science_books = [{"title": f"Science Book {i}", "category": "Science"} for i in range(30)]
        
        mock_scraper._get_categories.return_value = mock_categories
        mock_scraper._scrape_category_pages.side_effect = [fiction_books, science_books]
        mock_scraper.get_statistics.return_value = {"total_books": 50}
        mock_scraper.save_to_csv.return_value = "data/sample_50_books.csv"
        
        # Test sample scraping
        result = self.api.scrape_sample(max_books=50)
        
        # Verify calls
        mock_scraper._get_categories.assert_called_once()
        self.assertEqual(mock_scraper._scrape_category_pages.call_count, 2)
        
        # Should limit to max_books
        self.assertEqual(result["total_books"], 50)
        self.assertEqual(len(result["books"]), 50)
    
    @patch('scripts.scraper_api.BooksScraper')
    def test_get_categories(self, mock_scraper_class) -> None:
        """Test getting categories."""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        mock_categories = [
            {"name": "Fiction", "url": "http://example.com/fiction"}
        ]
        mock_scraper._get_categories.return_value = mock_categories
        
        result = self.api.get_categories()
        
        mock_scraper._get_categories.assert_called_once()
        self.assertEqual(result, mock_categories)
    
    @patch('scripts.scraper_api.BooksScraper')
    def test_scrape_category_success(self, mock_scraper_class) -> None:
        """Test scraping a specific category."""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        # Mock categories
        mock_categories = [
            {"name": "Fiction", "url": "http://example.com/fiction"},
            {"name": "Science", "url": "http://example.com/science"}
        ]
        
        mock_books = [{"title": "Fiction Book", "category": "Fiction"}]
        mock_stats = {"total_books": 1}
        
        mock_scraper._get_categories.return_value = mock_categories
        mock_scraper._scrape_category_pages.return_value = mock_books
        mock_scraper.get_statistics.return_value = mock_stats
        mock_scraper.save_to_csv.return_value = "data/fiction_books.csv"
        
        # Test category scraping
        result = self.api.scrape_category("Fiction")
        
        # Verify calls
        mock_scraper._get_categories.assert_called_once()
        mock_scraper._scrape_category_pages.assert_called_once_with(
            "http://example.com/fiction", "Fiction"
        )
        
        # Verify result
        self.assertEqual(result["books"], mock_books)
        self.assertEqual(result["total_books"], 1)
        self.assertEqual(result["category"], "Fiction")
    
    @patch('scripts.scraper_api.BooksScraper')
    def test_scrape_category_not_found(self, mock_scraper_class) -> None:
        """Test scraping a non-existent category."""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        mock_categories = [
            {"name": "Fiction", "url": "http://example.com/fiction"}
        ]
        mock_scraper._get_categories.return_value = mock_categories
        
        # Test scraping non-existent category
        result = self.api.scrape_category("NonExistent")
        
        # Should return error
        self.assertIn("error", result)
        self.assertEqual(result["total_books"], 0)
        self.assertIn("NonExistent", result["error"])
    
    def test_get_last_result(self) -> None:
        """Test getting last result."""
        # Initially should be None
        self.assertIsNone(self.api.get_last_result())
        
        # Set a result
        test_result = {"books": [], "total_books": 0}
        self.api.last_result = test_result
        
        # Should return the result
        self.assertEqual(self.api.get_last_result(), test_result)
    
    def test_get_scraper_stats_no_scraper(self) -> None:
        """Test getting stats when no scraper exists."""
        result = self.api.get_scraper_stats()
        self.assertEqual(result, {})
    
    @patch('scripts.scraper_api.BooksScraper')
    def test_get_scraper_stats_with_data(self, mock_scraper_class) -> None:
        """Test getting stats when scraper has data."""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        mock_scraper.books_data = [{"title": "Test"}]
        mock_scraper.get_statistics.return_value = {"total_books": 1}
        
        # Initialize scraper
        self.api._initialize_scraper()
        
        result = self.api.get_scraper_stats()
        self.assertEqual(result, {"total_books": 1})


class TestAPICommandLine(unittest.TestCase):
    """Test cases for command line functionality."""
    
    @patch('sys.argv')
    @patch('scripts.scraper_api.BooksScraperAPI')
    def test_command_line_categories_mode(self, mock_api_class, mock_argv) -> None:
        """Test command line categories mode."""
        mock_argv = ['scraper_api.py', '--mode', 'categories']
        
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        mock_api.get_categories.return_value = [
            {"name": "Fiction", "url": "http://example.com/fiction"}
        ]
        
        # Import main function after setting up mocks
        from scripts.scraper_api import main
        
        # Should not raise an exception
        with patch('builtins.print'):
            try:
                main()
            except SystemExit:
                pass  # Expected for successful completion


if __name__ == "__main__":
    unittest.main(verbosity=2)
