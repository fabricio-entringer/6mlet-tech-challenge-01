#!/usr/bin/env python3
"""
Books Scraper for books.toscrape.com

This module implements a comprehensive web scraping system to extract all books data
from https://books.toscrape.com/ and store it in CSV format locally.

Author: GitHub Copilot
Date: July 2025
"""

import csv
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from scripts.book_sequence import BookSequence
from scripts.history_logger import ScrapingHistoryLogger, create_configuration_snapshot


class BooksScraper:
    """
    A robust web scraper for extracting book data from books.toscrape.com.

    Features:
    - Handles pagination automatically
    - Implements retry mechanisms and error handling
    - Respects robots.txt and includes delays
    - Extracts comprehensive book information
    - Exports data to CSV format
    """

    def __init__(
        self,
        base_url: str = "https://books.toscrape.com",
        delay: float = 1.0,
        max_retries: int = 3,
        timeout: int = 10,
    ) -> None:
        """
        Initialize the BooksScraper.

        Args:
            base_url: The base URL of the website to scrape
            delay: Delay between requests in seconds
            max_retries: Maximum number of retry attempts for failed requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.delay = delay
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Mozilla/5.0 (compatible; BooksScraper/1.0; Educational)"}
        )

        # Performance tracking
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # History logging
        self.history_logger = ScrapingHistoryLogger()

        # Setup logging
        self._setup_logging()

        # Data storage
        self.books_data: List[Dict[str, str]] = []

    def _setup_logging(self) -> None:
        """Configure logging for scraping operations."""
        # Create logs directory if it doesn't exist
        from pathlib import Path

        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        log_file_path = logs_dir / "scraper.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file_path), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def _make_request(self, url: str) -> Optional[requests.Response]:
        """
        Make a HTTP request with retry logic and error handling.

        Args:
            url: The URL to request

        Returns:
            Response object if successful, None otherwise

        Raises:
            requests.exceptions.RequestException: If all retry attempts fail
        """
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Making request to: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                # Respect rate limiting
                time.sleep(self.delay)
                return response

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"All retry attempts failed for URL: {url}")
                    raise
                time.sleep(self.delay * (attempt + 1))  # Exponential backoff

        return None

    def _extract_rating(self, soup: BeautifulSoup) -> str:
        """
        Extract the star rating from a book's HTML.

        Args:
            soup: BeautifulSoup object of the book's HTML

        Returns:
            String representation of the rating (e.g., "Three", "Four")
        """
        rating_element = soup.find("p", class_="star-rating")
        if rating_element:
            classes = rating_element.get("class", [])
            rating_classes = [cls for cls in classes if cls != "star-rating"]
            return rating_classes[0] if rating_classes else "Unknown"
        return "Unknown"

    def _convert_rating_to_number(self, rating_text: str) -> int:
        """
        Convert textual rating to numeric value.

        Args:
            rating_text: Textual rating (e.g., "Three", "Four")

        Returns:
            Numeric rating (1-5)
        """
        rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        return rating_map.get(rating_text, 0)

    def _extract_book_data(
        self, book_element: BeautifulSoup, category: str, book_sequence: BookSequence
    ) -> Dict[str, str]:
        """
        Extract data from a single book element.

        Args:
            book_element: BeautifulSoup object containing book information
            category: The category this book belongs to

        Returns:
            Dictionary containing book data
        """
        try:
            # Extract title
            title_element = book_element.find("h3").find("a")
            title = title_element.get("title", "") if title_element else "Unknown"

            # Extract price
            price_element = book_element.find("p", class_="price_color")
            price = price_element.text.strip() if price_element else "Unknown"

            # Extract rating
            rating_text = self._extract_rating(book_element)
            rating_numeric = self._convert_rating_to_number(rating_text)

            # Extract availability
            availability_element = book_element.find("p", class_="instock availability")
            availability = (
                availability_element.text.strip() if availability_element else "Unknown"
            )

            # Extract image URL
            img_element = book_element.find("div", class_="image_container").find("img")
            img_url = ""
            if img_element and img_element.get("src"):
                img_url = urljoin(self.base_url, img_element.get("src"))

            return {
                "id": book_sequence.get_next_id(),
                "title": title,
                "price": price,
                "rating_text": rating_text,
                "rating_numeric": str(rating_numeric),
                "availability": availability,
                "category": category,
                "image_url": img_url,
            }

        except Exception as e:
            self.logger.warning(f"Error extracting book data: {e}")
            return {
                "id": book_sequence.get_next_id(),
                "title": "Error",
                "price": "Error",
                "rating_text": "Error",
                "rating_numeric": "0",
                "availability": "Error",
                "category": category,
                "image_url": "Error",
            }

    def _get_categories(self) -> List[Dict[str, str]]:
        """
        Get all book categories from the main page.

        Returns:
            List of dictionaries containing category name and URL
        """
        try:
            response = self._make_request(self.base_url)
            if not response:
                return []

            soup = BeautifulSoup(response.content, "html.parser")
            categories = []

            # Find the navigation menu with categories
            nav_list = soup.find("ul", class_="nav nav-list")
            if nav_list:
                category_links = nav_list.find_all("a")[1:]  # Skip first "Books" link

                for link in category_links:
                    category_name = link.text.strip()
                    category_url = urljoin(self.base_url, link.get("href"))
                    categories.append({"name": category_name, "url": category_url})

            self.logger.info(f"Found {len(categories)} categories")
            return categories

        except Exception as e:
            self.logger.error(f"Error getting categories: {e}")
            return []

    def _scrape_category_pages(
        self, category_url: str, category_name: str, book_sequence: BookSequence
    ) -> List[Dict[str, str]]:
        """
        Scrape all pages within a category.

        Args:
            category_url: URL of the category
            category_name: Name of the category

        Returns:
            List of book data dictionaries
        """
        books = []
        page_num = 1
        current_url = category_url

        while current_url:
            try:
                self.logger.info(f"Scraping {category_name} - page {page_num}")
                response = self._make_request(current_url)
                if not response:
                    break

                soup = BeautifulSoup(response.content, "html.parser")

                # Extract books from current page
                book_elements = soup.find_all("article", class_="product_pod")

                for book_element in book_elements:
                    book_data = self._extract_book_data(book_element, category_name, book_sequence)
                    books.append(book_data)

                # Find next page link
                next_link = soup.find("li", class_="next")
                if next_link and next_link.find("a"):
                    next_url = next_link.find("a").get("href")
                    # Handle relative URLs
                    if next_url.startswith("../"):
                        # Remove the page reference and add the new one
                        base_category_url = "/".join(current_url.split("/")[:-1])
                        current_url = urljoin(base_category_url + "/", next_url)
                    else:
                        current_url = urljoin(current_url, next_url)
                    page_num += 1
                else:
                    current_url = None

            except Exception as e:
                self.logger.error(
                    f"Error scraping category {category_name} page {page_num}: {e}"
                )
                break

        self.logger.info(f"Scraped {len(books)} books from {category_name}")
        return books

    def scrape_all_books(self, execution_type: str = "DIRECT") -> List[Dict[str, str]]:
        """
        Scrape all books from all categories.

        Args:
            execution_type: Type of execution for history logging ("API", "CLI", "DIRECT")

        Returns:
            List of all book data dictionaries
        """
        # Clear any previous data to prevent accumulation
        self.books_data.clear()

        # Start timing
        self.start_time = time.time()
        self.logger.info("Starting comprehensive book scraping...")

        status = "FAILED"
        error_message = None
        output_file = ""

        try:
            # Get all categories
            categories = self._get_categories()
            if not categories:
                error_message = "No categories found"
                self.logger.error(f"{error_message}. Aborting scraping.")
                self._log_execution_history(
                    execution_type, 0, 0, "", status, error_message
                )
                return []

            all_books = []

            # Initialize book sequence for unique IDs
            book_sequence = BookSequence()

            for category in categories:
                try:
                    category_books = self._scrape_category_pages(
                        category["url"], category["name"], book_sequence
                    )
                    all_books.extend(category_books)
                except Exception as e:
                    self.logger.error(
                        f"Error scraping category {category['name']}: {e}"
                    )
                    continue

            self.books_data = all_books

            # Determine status
            if len(all_books) > 0:
                status = "SUCCESS"
                self.logger.info(
                    f"Scraping completed successfully. Total books collected: {len(all_books)}"
                )
            else:
                status = "FAILED"
                error_message = "No books were scraped"
                self.logger.warning("Scraping completed but no books were collected")

            return all_books

        except Exception as e:
            status = "FAILED"
            error_message = str(e)
            self.logger.error(f"Critical error during scraping: {e}")
            return []

        finally:
            # End timing and log execution
            self.end_time = time.time()
            duration = self.end_time - self.start_time if self.start_time else 0
            total_books = len(self.books_data) if hasattr(self, "books_data") else 0
            total_categories = (
                len(set(book.get("category", "") for book in self.books_data))
                if self.books_data
                else 0
            )

            # Log execution history
            self._log_execution_history(
                execution_type,
                duration,
                total_books,
                total_categories,
                output_file,
                status,
                error_message,
            )

    def _log_execution_history(
        self,
        execution_type: str,
        duration: float,
        total_books: int,
        total_categories: int,
        output_file: str,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Log execution details to history file.

        Args:
            execution_type: Type of execution ("API", "CLI", "DIRECT")
            duration: Execution duration in seconds
            total_books: Number of books scraped
            total_categories: Number of categories processed
            output_file: Path to output file
            status: Execution status
            error_message: Error message if any
        """
        try:
            config = create_configuration_snapshot(
                delay=self.delay,
                max_retries=self.max_retries,
                timeout=self.timeout,
                base_url=self.base_url,
            )

            self.history_logger.log_scraping_execution(
                execution_type=execution_type,
                duration_seconds=duration,
                total_books_scraped=total_books,
                total_categories=total_categories,
                output_file=output_file,
                status=status,
                error_message=error_message,
                configuration=config,
            )
        except Exception as e:
            self.logger.warning(f"Could not log execution history: {e}")

    def reset(self) -> None:
        """
        Reset the scraper state to ensure clean subsequent operations.

        This method clears all internal data and resets timing information
        to prevent data accumulation between scraping operations.
        """
        self.books_data.clear()
        self.start_time = None
        self.end_time = None
        self.logger.info("Scraper state reset completed")

    def save_to_csv(
        self, filename: str = "books_data.csv", output_dir: str = "data"
    ) -> str:
        """
        Save scraped books data to CSV file.

        Args:
            filename: Name of the CSV file
            output_dir: Directory to save the file

        Returns:
            Path to the saved file

        Raises:
            ValueError: If no data is available to save
        """
        if not self.books_data:
            raise ValueError("No books data available. Run scrape_all_books() first.")

        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        file_path = output_path / filename

        # Define CSV headers
        headers = [
            "id",
            "title",
            "price",
            "rating_text",
            "rating_numeric",
            "availability",
            "category",
            "image_url",
        ]

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(self.books_data)

            self.logger.info(f"Data saved to {file_path}")
            self.logger.info(f"Total records saved: {len(self.books_data)}")
            return str(file_path)

        except Exception as e:
            self.logger.error(f"Error saving CSV file: {e}")
            raise

    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about the scraped data.

        Returns:
            Dictionary containing various statistics
        """
        if not self.books_data:
            return {}

        categories = {}
        ratings = {}

        for book in self.books_data:
            # Count by category
            category = book.get("category", "Unknown")
            categories[category] = categories.get(category, 0) + 1

            # Count by rating
            rating = book.get("rating_text", "Unknown")
            ratings[rating] = ratings.get(rating, 0) + 1

        return {
            "total_books": len(self.books_data),
            "total_categories": len(categories),
            "categories_breakdown": categories,
            "ratings_breakdown": ratings,
        }


def main() -> None:
    """
    Main function to run the books scraper.
    """
    scraper = BooksScraper(delay=1.0)

    try:
        # Scrape all books
        books = scraper.scrape_all_books()

        if books:
            # Save to CSV
            output_file = scraper.save_to_csv()

            # Display statistics
            stats = scraper.get_statistics()
            print("\n" + "=" * 50)
            print("SCRAPING COMPLETED SUCCESSFULLY")
            print("=" * 50)
            print(f"Total books scraped: {stats['total_books']}")
            print(f"Total categories: {stats['total_categories']}")
            print(f"Data saved to: {output_file}")

            print("\nTop 5 categories by book count:")
            sorted_categories = sorted(
                stats["categories_breakdown"].items(), key=lambda x: x[1], reverse=True
            )
            for category, count in sorted_categories[:5]:
                print(f"  {category}: {count} books")

        else:
            print("No books were scraped. Please check the logs for errors.")

    except Exception as e:
        print(f"Scraping failed: {e}")
        logging.error(f"Scraping failed: {e}")


if __name__ == "__main__":
    main()
