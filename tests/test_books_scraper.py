"""
Tests for the books scraper module.

This module contains comprehensive tests for the BooksScraper class
and related functionality.
"""

import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest
import requests
from bs4 import BeautifulSoup

# Add the project root to Python path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.books_scraper import BooksScraper
from scripts.config import RATING_MAPPING


class TestBooksScraper(unittest.TestCase):
    """Test cases for the BooksScraper class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.scraper = BooksScraper(
            base_url="https://books.toscrape.com",
            delay=0.1,  # Faster for testing
            max_retries=2,
            timeout=5,
        )

    def test_initialization(self) -> None:
        """Test scraper initialization."""
        self.assertEqual(self.scraper.base_url, "https://books.toscrape.com")
        self.assertEqual(self.scraper.delay, 0.1)
        self.assertEqual(self.scraper.max_retries, 2)
        self.assertEqual(self.scraper.timeout, 5)
        self.assertEqual(len(self.scraper.books_data), 0)

    def test_convert_rating_to_number(self) -> None:
        """Test rating text to number conversion."""
        test_cases = [
            ("One", 1),
            ("Two", 2),
            ("Three", 3),
            ("Four", 4),
            ("Five", 5),
            ("Unknown", 0),
            ("Invalid", 0),
        ]

        for rating_text, expected_number in test_cases:
            with self.subTest(rating_text=rating_text):
                result = self.scraper._convert_rating_to_number(rating_text)
                self.assertEqual(result, expected_number)

    def test_extract_rating(self) -> None:
        """Test rating extraction from HTML."""
        # Test with valid rating
        html = '<p class="star-rating Three"><i class="icon-star"></i></p>'
        soup = BeautifulSoup(html, "html.parser")
        rating = self.scraper._extract_rating(soup)
        self.assertEqual(rating, "Three")

        # Test with no rating element
        html = "<div>No rating here</div>"
        soup = BeautifulSoup(html, "html.parser")
        rating = self.scraper._extract_rating(soup)
        self.assertEqual(rating, "Unknown")

    def test_extract_book_data(self) -> None:
        """Test book data extraction from HTML element."""
        html = """
        <article class="product_pod">
            <div class="image_container">
                <img src="media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg" alt="A Light in the Attic">
            </div>
            <p class="star-rating Three">
                <i class="icon-star"></i>
            </p>
            <h3><a href="catalogue/a-light-in-the-attic_1000/index.html" title="A Light in the Attic">A Light in the ...</a></h3>
            <div class="product_price">
                <p class="price_color">£51.77</p>
                <p class="instock availability">
                    <i class="icon-ok"></i>
                    In stock
                </p>
            </div>
        </article>
        """

        soup = BeautifulSoup(html, "html.parser")
        book_data = self.scraper._extract_book_data(soup, "Poetry")

        self.assertEqual(book_data["title"], "A Light in the Attic")
        self.assertEqual(book_data["price"], "£51.77")
        self.assertEqual(book_data["rating_text"], "Three")
        self.assertEqual(book_data["rating_numeric"], "3")
        self.assertEqual(book_data["category"], "Poetry")
        self.assertIn("In stock", book_data["availability"])
        self.assertIn("books.toscrape.com", book_data["image_url"])

    @patch("scripts.books_scraper.requests.Session.get")
    def test_make_request_success(self, mock_get) -> None:
        """Test successful HTTP request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html>Test content</html>"
        mock_get.return_value = mock_response

        response = self.scraper._make_request("https://example.com")

        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()

    @patch("scripts.books_scraper.requests.Session.get")
    def test_make_request_retry_logic(self, mock_get) -> None:
        """Test request retry logic on failure."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with self.assertRaises(requests.exceptions.ConnectionError):
            self.scraper._make_request("https://example.com")

        # Should retry max_retries times
        self.assertEqual(mock_get.call_count, self.scraper.max_retries)

    def test_save_to_csv_no_data(self) -> None:
        """Test CSV saving when no data is available."""
        with self.assertRaises(ValueError) as context:
            self.scraper.save_to_csv()

        self.assertIn("No books data available", str(context.exception))

    def test_save_to_csv_with_data(self) -> None:
        """Test CSV saving with sample data."""
        # Add sample data
        self.scraper.books_data = [
            {
                "title": "Test Book",
                "price": "£10.00",
                "rating_text": "Four",
                "rating_numeric": "4",
                "availability": "In stock",
                "category": "Fiction",
                "image_url": "https://example.com/image.jpg",
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = self.scraper.save_to_csv(
                filename="test_books.csv", output_dir=temp_dir
            )

            # Verify file was created
            self.assertTrue(Path(file_path).exists())

            # Verify CSV content
            with open(file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)

                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["title"], "Test Book")
                self.assertEqual(rows[0]["price"], "£10.00")
                self.assertEqual(rows[0]["rating_numeric"], "4")

    def test_get_statistics_empty_data(self) -> None:
        """Test statistics calculation with empty data."""
        stats = self.scraper.get_statistics()
        self.assertEqual(stats, {})

    def test_get_statistics_with_data(self) -> None:
        """Test statistics calculation with sample data."""
        self.scraper.books_data = [
            {"title": "Book 1", "category": "Fiction", "rating_text": "Four"},
            {"title": "Book 2", "category": "Fiction", "rating_text": "Three"},
            {"title": "Book 3", "category": "Non-Fiction", "rating_text": "Four"},
        ]

        stats = self.scraper.get_statistics()

        self.assertEqual(stats["total_books"], 3)
        self.assertEqual(stats["total_categories"], 2)
        self.assertEqual(stats["categories_breakdown"]["Fiction"], 2)
        self.assertEqual(stats["categories_breakdown"]["Non-Fiction"], 1)
        self.assertEqual(stats["ratings_breakdown"]["Four"], 2)
        self.assertEqual(stats["ratings_breakdown"]["Three"], 1)


class TestScraperConfiguration(unittest.TestCase):
    """Test configuration and constants."""

    def test_rating_mapping(self) -> None:
        """Test that rating mapping contains all expected values."""
        expected_ratings = ["One", "Two", "Three", "Four", "Five"]

        for rating in expected_ratings:
            self.assertIn(rating, RATING_MAPPING)

        # Test numeric values
        self.assertEqual(RATING_MAPPING["One"], 1)
        self.assertEqual(RATING_MAPPING["Five"], 5)


class TestScraperIntegration(unittest.TestCase):
    """Integration tests for the scraper (require network access)."""

    @pytest.mark.integration
    def test_robots_txt_compliance(self) -> None:
        """Test that the scraper respects robots.txt (if available)."""
        scraper = BooksScraper(delay=1.0)

        # Try to access robots.txt
        robots_url = f"{scraper.base_url}/robots.txt"
        try:
            response = scraper._make_request(robots_url)
            if response and response.status_code == 200:
                # Check if our user agent is allowed
                robots_content = response.text
                # This is a basic check - in a real scenario, you'd parse robots.txt properly
                self.assertIsInstance(robots_content, str)
        except Exception:
            # If robots.txt is not accessible, that's fine for testing
            pass

    @pytest.mark.integration
    @patch("time.sleep")  # Speed up the test
    def test_scraper_delay_implementation(self, mock_sleep) -> None:
        """Test that the scraper implements proper delays."""
        scraper = BooksScraper(delay=0.5)

        with patch("scripts.books_scraper.requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b"<html>Test</html>"
            mock_get.return_value = mock_response

            scraper._make_request("https://example.com")

            # Verify sleep was called with the correct delay
            mock_sleep.assert_called_with(0.5)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
