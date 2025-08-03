"""
Main data service that integrates CSV loading, caching, and validation.

This service provides a unified interface for all data operations with
automatic refresh capabilities and caching for improved performance.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from threading import Lock

from .csv_loader import CSVDataLoader
from .data_cache import DataCache
from .data_validator import DataValidator, ValidationResult
from ..models.book import Book


logger = logging.getLogger(__name__)


class DataService:
    """
    Main data service that provides unified access to book data with
    caching, validation, and refresh capabilities.
    """
    
    def __init__(self, data_file_path: Optional[str] = None):
        """
        Initialize the data service.
        
        Args:
            data_file_path: Path to the CSV data file. If None, uses default path.
        """
        self.csv_loader = CSVDataLoader(data_file_path)
        self.cache = DataCache()
        self.validator = DataValidator()
        
        self._lock = Lock()
        self._initialized = False
        self._last_validation_result: Optional[ValidationResult] = None
        
        # Initialize data on startup
        self._initialize_data()
    
    def _initialize_data(self) -> None:
        """Initialize data on service startup."""
        try:
            logger.info("Initializing data service...")
            self.refresh_data()
            self._initialized = True
            logger.info("Data service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize data service: {e}")
            # Don't raise exception - allow service to start even if data is not available
    
    def refresh_data(self, validate: bool = True) -> bool:
        """
        Refresh all cached data from the CSV file.
        
        Args:
            validate: Whether to run data validation before caching
            
        Returns:
            True if data was successfully refreshed, False otherwise
        """
        with self._lock:
            try:
                logger.info("Refreshing data from CSV...")
                
                # Load raw data first
                raw_data = self.csv_loader.load_raw_data(force_reload=True)
                
                if validate and raw_data:
                    # Validate data integrity
                    logger.info("Validating data integrity...")
                    validation_result = self.validator.validate_data_integrity(raw_data)
                    self._last_validation_result = validation_result
                    
                    if not validation_result.is_valid:
                        logger.warning(f"Data validation found issues: {len(validation_result.errors)} errors")
                        for error in validation_result.errors[:5]:  # Log first 5 errors
                            logger.warning(f"Validation error: {error}")
                    
                    if validation_result.warnings:
                        logger.info(f"Data validation found {len(validation_result.warnings)} warnings")
                
                # Load books with validation
                books = self.csv_loader.load_books_data(force_reload=True)
                
                # Update cache
                self.cache.update_books(books)
                
                logger.info(f"Data refreshed successfully: {len(books)} books cached")
                return True
                
            except Exception as e:
                logger.error(f"Error refreshing data: {e}")
                return False
    
    def get_books(self,
                  page: int = 1,
                  limit: int = 20,
                  category: Optional[str] = None,
                  sort: str = "title",
                  order: str = "asc",
                  min_price: Optional[float] = None,
                  max_price: Optional[float] = None,
                  min_rating: Optional[int] = None,
                  availability: Optional[str] = None) -> List[Book]:
        """
        Get books with filtering, sorting, and pagination using cached data.
        
        Args:
            page: Page number (1-based)
            limit: Number of items per page
            category: Category filter
            sort: Sort field
            order: Sort order (asc/desc)
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_rating: Minimum rating filter
            availability: Availability filter
            
        Returns:
            List of Book objects
        """
        # Use cached data for fast access
        books = self.cache.search_books(
            category=category,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            availability=availability
        )
        
        # Apply sorting
        books = self._apply_sorting(books, sort, order)
        
        # Apply pagination
        start_index = (page - 1) * limit
        end_index = start_index + limit
        
        return books[start_index:end_index]
    
    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """
        Get a book by ID using cached data.
        
        Args:
            book_id: Book ID
            
        Returns:
            Book object if found, None otherwise
        """
        return self.cache.get_book_by_id(book_id)
    
    def get_top_rated_books(self, limit: int = 10) -> List[Book]:
        """
        Get top-rated books using cached data.
        
        Args:
            limit: Maximum number of books to return
            
        Returns:
            List of top-rated Book objects
        """
        return self.cache.get_top_rated_books(limit)
    
    def get_books_by_price_range(self, min_price: float, max_price: float) -> List[Book]:
        """
        Get books within a price range using cached data.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            
        Returns:
            List of Book objects within price range
        """
        return self.cache.get_books_by_price_range(min_price, max_price)
    
    def get_categories(self) -> List[str]:
        """
        Get all available categories from cached data.
        
        Returns:
            Sorted list of category names
        """
        return self.cache.get_categories()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the data service.
        
        Returns:
            Dictionary with statistics
        """
        cache_stats = self.cache.get_statistics()
        loader_stats = self.csv_loader.get_cache_stats()
        validation_stats = self.validator.get_validation_stats()
        
        return {
            "service": {
                "initialized": self._initialized,
                "last_refresh": cache_stats.get("last_updated"),
                "data_file_path": loader_stats.get("data_file_path"),
                "file_exists": loader_stats.get("file_exists"),
            },
            "cache": cache_stats,
            "loader": loader_stats,
            "validation": validation_stats,
            "last_validation_result": (
                self._last_validation_result.to_dict() 
                if self._last_validation_result else None
            ),
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check of the data service.
        
        Returns:
            Dictionary with health status
        """
        try:
            stats = self.get_statistics()
            is_healthy = (
                self._initialized and
                not self.cache.is_empty() and
                stats["service"]["file_exists"]
            )
            
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "details": {
                    "initialized": self._initialized,
                    "cache_populated": not self.cache.is_empty(),
                    "total_books": self.cache.get_size(),
                    "file_exists": stats["service"]["file_exists"],
                    "last_updated": stats["cache"].get("last_updated"),
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "details": {
                    "error": str(e),
                    "initialized": self._initialized,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
    
    def validate_data_file(self) -> ValidationResult:
        """
        Validate the data file integrity.
        
        Returns:
            ValidationResult with file validation details
        """
        file_path = str(self.csv_loader.data_file_path)
        return self.validator.validate_file_integrity(file_path)
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
        self.csv_loader.clear_cache()
        logger.info("All caches cleared")
    
    def _apply_sorting(self, books: List[Book], sort_by: str, order: str) -> List[Book]:
        """Apply sorting to books list."""
        reverse = order.lower() == "desc"
        
        if sort_by == "title":
            return sorted(books, key=lambda x: x.title.lower(), reverse=reverse)
        elif sort_by == "price":
            return sorted(books, key=lambda x: x.price, reverse=reverse)
        elif sort_by == "rating":
            return sorted(books, key=lambda x: x.rating_numeric, reverse=reverse)
        elif sort_by == "availability":
            return sorted(books, key=lambda x: x.availability.lower(), reverse=reverse)
        elif sort_by == "category":
            return sorted(books, key=lambda x: x.category.lower(), reverse=reverse)
        else:
            # Default to title sorting
            return sorted(books, key=lambda x: x.title.lower(), reverse=reverse)


# Global data service instance
_data_service: Optional[DataService] = None
_service_lock = Lock()


def get_data_service() -> DataService:
    """
    Get the global data service instance (singleton pattern).
    
    Returns:
        DataService instance
    """
    global _data_service
    
    if _data_service is None:
        with _service_lock:
            if _data_service is None:
                _data_service = DataService()
    
    return _data_service


def refresh_global_data_service() -> bool:
    """
    Refresh the global data service.
    
    Returns:
        True if refresh was successful, False otherwise
    """
    service = get_data_service()
    return service.refresh_data()
