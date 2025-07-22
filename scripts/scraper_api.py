#!/usr/bin/env python3
"""
Books Scraper API Module

This module provides a simple API interface for the books scraper.

Usage:
    from scripts.scraper_api import BooksScraperAPI
    
    api = BooksScraperAPI()
    result = api.scrape_all_books()
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.books_scraper import BooksScraper
from scripts.config import SCRAPER_CONFIG


class BooksScraperAPI:
    """
    Simple API interface for scraping all books from books.toscrape.com.
    
    This class provides a simplified interface for scraping all books
    both programmatically and from command line.
    """
    
    def __init__(
        self,
        delay: float = None,
        max_retries: int = None,
        timeout: int = None,
        output_dir: str = None,
        logs_dir: str = None
    ) -> None:
        """
        Initialize the Books Scraper API.
        
        Args:
            delay: Delay between requests in seconds (default from config)
            max_retries: Maximum retry attempts (default from config)
            timeout: Request timeout in seconds (default from config)
            output_dir: Output directory for CSV files (default from config)
            logs_dir: Logs directory (default from config)
        """
        self.delay = delay or SCRAPER_CONFIG["delay"]
        self.max_retries = max_retries or SCRAPER_CONFIG["max_retries"]
        self.timeout = timeout or SCRAPER_CONFIG["timeout"]
        self.output_dir = output_dir or SCRAPER_CONFIG["output_directory"]
        self.logs_dir = logs_dir or SCRAPER_CONFIG.get("logs_directory", "logs")
        
        self.scraper = None
        self.last_result = None
    
    def _initialize_scraper(self) -> BooksScraper:
        """Initialize and return a fresh BooksScraper instance."""
        # Always create a fresh scraper instance to avoid data accumulation
        self.scraper = BooksScraper(
            delay=self.delay,
            max_retries=self.max_retries,
            timeout=self.timeout
        )
        return self.scraper
    
    def scrape_all_books(self, save_csv: bool = True, csv_filename: str = None) -> Dict[str, Union[List[Dict], str, int]]:
        """
        Scrape all books from the website.
        
        Args:
            save_csv: Whether to automatically save results to CSV
            csv_filename: Custom CSV filename (default: books_data.csv)
            
        Returns:
            Dictionary containing:
                - books: List of book data dictionaries
                - total_books: Total number of books scraped
                - total_categories: Total number of categories
                - csv_file: Path to saved CSV file (if save_csv=True)
                - statistics: Detailed statistics
        """
        scraper = self._initialize_scraper()
        
        # Perform scraping with API execution type
        books = scraper.scrape_all_books(execution_type="API")
        
        # Get statistics
        stats = scraper.get_statistics()
        
        # Prepare result
        result = {
            "books": books,
            "total_books": len(books),
            "total_categories": stats.get("total_categories", 0),
            "statistics": stats
        }
        
        # Save to CSV if requested
        if save_csv and books:
            filename = csv_filename or SCRAPER_CONFIG["default_csv_filename"]
            csv_path = scraper.save_to_csv(filename, self.output_dir)
            result["csv_file"] = csv_path
        
        self.last_result = result
        return result
    

    
    def get_last_result(self) -> Optional[Dict]:
        """Get the result of the last scraping operation."""
        return self.last_result
