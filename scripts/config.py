"""
Configuration module for the books scraper.

This module contains configuration settings and constants used by the scraper.
"""

from typing import Dict, Any

# Scraper configuration
SCRAPER_CONFIG: Dict[str, Any] = {
    "base_url": "https://books.toscrape.com",
    "delay": 1.0,  # Delay between requests in seconds
    "max_retries": 3,  # Maximum retry attempts
    "timeout": 10,  # Request timeout in seconds
    "output_directory": "data",
    "logs_directory": "logs",
    "default_csv_filename": "books_data.csv",
    "log_filename": "scraper.log",
    "history_log_filename": "scraping_history.csv"
}

# User agent for requests
USER_AGENT = "Mozilla/5.0 (compatible; BooksScraper/1.0; Educational)"

# CSV column headers
CSV_HEADERS = [
    "title",
    "price", 
    "rating_text",
    "rating_numeric",
    "availability",
    "category",
    "image_url"
]

# Rating text to numeric mapping
RATING_MAPPING = {
    "One": 1,
    "Two": 2, 
    "Three": 3,
    "Four": 4,
    "Five": 5
}

# History log CSV headers
HISTORY_LOG_HEADERS = [
    "timestamp",
    "execution_type",  # "API" or "CLI"
    "duration_seconds",
    "total_books_scraped",
    "total_categories",
    "output_file",
    "status",  # "SUCCESS", "PARTIAL", "FAILED"
    "error_message",
    "configuration"  # JSON string with scraper config
]
