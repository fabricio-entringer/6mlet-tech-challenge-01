"""CSV data loader with validation and caching capabilities."""

import csv
import logging
import os
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from threading import RLock

from ..models.book import Book
from ..utils import convert_price_to_float


logger = logging.getLogger(__name__)


class CSVDataLoader:
    """Handles loading and processing of CSV data with caching and validation."""
    
    def __init__(self, data_file_path: Optional[str] = None):
        """
        Initialize CSV data loader.
        
        Args:
            data_file_path: Path to the CSV data file. If None, uses default path.
        """
        if data_file_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            self.data_file_path = Path(project_root) / "data" / "books_data.csv"
        else:
            self.data_file_path = Path(data_file_path)
            
        self._lock = RLock()
        self._cached_data: Optional[List[Dict[str, str]]] = None
        self._cached_books: Optional[List[Book]] = None
        self._last_modified: Optional[datetime] = None
        self._file_size: Optional[int] = None
        
    def _get_file_stats(self) -> tuple[Optional[datetime], Optional[int]]:
        """Get file modification time and size."""
        try:
            if not self.data_file_path.exists():
                return None, None
                
            stat = self.data_file_path.stat()
            modified_time = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            file_size = stat.st_size
            return modified_time, file_size
        except Exception as e:
            logger.error(f"Error getting file stats: {e}")
            return None, None
    
    def _should_reload_data(self) -> bool:
        """Check if data should be reloaded based on file modification time."""
        current_modified, current_size = self._get_file_stats()
        
        if current_modified is None or current_size is None:
            return False
            
        # Reload if we haven't cached data yet
        if self._cached_data is None:
            return True
            
        # Reload if file has been modified or size changed
        if (self._last_modified is None or 
            current_modified > self._last_modified or
            current_size != self._file_size):
            return True
            
        return False
    
    def _load_raw_csv_data(self) -> List[Dict[str, str]]:
        """Load raw CSV data from file."""
        raw_data = []
        
        try:
            if not self.data_file_path.exists():
                logger.warning(f"CSV file not found: {self.data_file_path}")
                return raw_data
                
            logger.info(f"Loading CSV data from: {self.data_file_path}")
            
            with open(self.data_file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_data.append(row)
                    
            logger.info(f"Loaded {len(raw_data)} rows from CSV")
            
        except FileNotFoundError:
            logger.warning(f"CSV file not found: {self.data_file_path}")
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
            
        return raw_data
    
    def _load_csv_with_pandas(self) -> Optional[pd.DataFrame]:
        """Load CSV data using pandas for efficient processing."""
        try:
            if not self.data_file_path.exists():
                logger.warning(f"CSV file not found: {self.data_file_path}")
                return None
                
            logger.info(f"Loading CSV data with pandas from: {self.data_file_path}")
            
            # Load with pandas for efficient processing
            df = pd.read_csv(self.data_file_path)
            
            # Basic data cleaning
            df = df.dropna(subset=['title'])  # Remove rows without title
            df['title'] = df['title'].astype(str).str.strip()
            
            # Clean price data
            df['price_numeric'] = df['price'].apply(lambda x: convert_price_to_float(str(x)) or 0.0)
            
            # Clean rating data
            df['rating_numeric'] = pd.to_numeric(df['rating_numeric'], errors='coerce').fillna(0)
            df['rating_numeric'] = df['rating_numeric'].astype(int)
            
            # Ensure rating is in valid range (1-5)
            df.loc[~df['rating_numeric'].between(1, 5), 'rating_numeric'] = 0
            
            logger.info(f"Processed {len(df)} rows with pandas")
            return df
            
        except Exception as e:
            logger.error(f"Error loading CSV with pandas: {e}")
            return None
    
    def _convert_book_data(self, book_row: Dict[str, str], row_index: int) -> Optional[Book]:
        """Convert CSV row to Book model with validation."""
        try:
            # Convert price to float
            price_float = convert_price_to_float(book_row.get("price", ""))
            if price_float is None:
                price_float = 0.0

            # Convert rating to int
            rating_numeric = int(book_row.get("rating_numeric", "0"))
            if not (1 <= rating_numeric <= 5):
                rating_numeric = 0
            
            return Book(
                id=int(book_row.get("id", row_index)),
                title=book_row.get("title", "").strip(),
                price=price_float,
                price_display=book_row.get("price", "£0.00"),
                rating_text=book_row.get("rating_text", "").strip(),
                rating_numeric=rating_numeric,
                availability=book_row.get("availability", "").strip(),
                category=book_row.get("category", "").strip(),
                image_url=book_row.get("image_url", "").strip(),
                description=book_row.get("description", "").strip() or None,
                upc=book_row.get("upc", "").strip() or None,
                reviews=book_row.get("reviews", "").strip() or None,
            )
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid book data at row {row_index}: {e}")
            return None
    
    def load_books_data(self, force_reload: bool = False) -> List[Book]:
        """
        Load books data with caching and automatic refresh.
        
        Args:
            force_reload: If True, forces reloading data from file regardless of cache status
            
        Returns:
            List of Book objects
        """
        with self._lock:
            # Check if we need to reload data
            if force_reload or self._should_reload_data():
                logger.info("Reloading CSV data...")
                
                # Load raw CSV data
                raw_data = self._load_raw_csv_data()
                
                # Convert to Book objects with validation
                books = []
                for index, book_row in enumerate(raw_data, start=1):
                    book = self._convert_book_data(book_row, index)
                    if book:
                        books.append(book)
                
                # Update cache
                self._cached_data = raw_data
                self._cached_books = books
                self._last_modified, self._file_size = self._get_file_stats()
                
                logger.info(f"Loaded {len(books)} valid books from {len(raw_data)} CSV rows")
                
            return self._cached_books or []
    
    def load_raw_data(self, force_reload: bool = False) -> List[Dict[str, str]]:
        """
        Load raw CSV data with caching.
        
        Args:
            force_reload: If True, forces reloading data from file regardless of cache status
            
        Returns:
            List of dictionaries representing CSV rows
        """
        with self._lock:
            # Load books first to populate cache
            self.load_books_data(force_reload)
            return self._cached_data or []
    
    def load_dataframe(self, force_reload: bool = False) -> Optional[pd.DataFrame]:
        """
        Load data as pandas DataFrame for efficient processing.
        
        Args:
            force_reload: If True, forces reloading data from file
            
        Returns:
            Pandas DataFrame or None if loading fails
        """
        # For pandas operations, always load fresh data to ensure consistency
        return self._load_csv_with_pandas()
    
    def refresh_data(self) -> bool:
        """
        Force refresh of cached data.
        
        Returns:
            True if data was successfully refreshed, False otherwise
        """
        try:
            self.load_books_data(force_reload=True)
            logger.info("Data cache refreshed successfully")
            return True
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cached data."""
        with self._lock:
            return {
                "cached_books_count": len(self._cached_books) if self._cached_books else 0,
                "cached_raw_rows_count": len(self._cached_data) if self._cached_data else 0,
                "last_modified": self._last_modified.isoformat() if self._last_modified else None,
                "file_size_bytes": self._file_size,
                "data_file_path": str(self.data_file_path),
                "file_exists": self.data_file_path.exists(),
            }
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        with self._lock:
            self._cached_data = None
            self._cached_books = None
            self._last_modified = None
            self._file_size = None
            logger.info("Data cache cleared")
