"""Data cache manager for in-memory storage and fast access."""

import logging
from datetime import datetime, timezone
from threading import Lock, RLock
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

from ..models.book import Book


logger = logging.getLogger(__name__)


class DataCache:
    """
    In-memory cache for book data with automatic refresh capabilities.
    Thread-safe implementation for concurrent access.
    """
    
    def __init__(self):
        """Initialize the data cache."""
        self._lock = RLock()  # Reentrant lock for nested operations
        
        # Core data storage
        self._books: List[Book] = []
        self._books_by_id: Dict[int, Book] = {}
        self._books_by_category: Dict[str, List[Book]] = defaultdict(list)
        
        # Cache metadata
        self._last_updated: Optional[datetime] = None
        self._total_books: int = 0
        self._categories: Set[str] = set()
        
        # Statistics
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        
    def update_books(self, books: List[Book]) -> None:
        """
        Update the cache with new book data.
        
        Args:
            books: List of Book objects to cache
        """
        with self._lock:
            logger.info(f"Updating cache with {len(books)} books")
            
            # Clear existing data
            self._books.clear()
            self._books_by_id.clear()
            self._books_by_category.clear()
            self._categories.clear()
            
            # Populate cache
            for book in books:
                self._books.append(book)
                self._books_by_id[book.id] = book
                self._books_by_category[book.category].append(book)
                self._categories.add(book.category)
            
            # Update metadata
            self._total_books = len(books)
            self._last_updated = datetime.now(timezone.utc)
            
            logger.info(f"Cache updated: {self._total_books} books, {len(self._categories)} categories")
    
    def get_all_books(self) -> List[Book]:
        """
        Get all cached books.
        
        Returns:
            List of all Book objects in cache
        """
        with self._lock:
            self._cache_hits += 1
            return self._books.copy()
    
    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """
        Get a book by its ID.
        
        Args:
            book_id: The book ID to lookup
            
        Returns:
            Book object if found, None otherwise
        """
        with self._lock:
            if book_id in self._books_by_id:
                self._cache_hits += 1
                return self._books_by_id[book_id]
            else:
                self._cache_misses += 1
                return None
    
    def get_books_by_category(self, category: str) -> List[Book]:
        """
        Get all books in a specific category.
        
        Args:
            category: Category name (case-sensitive)
            
        Returns:
            List of Book objects in the category
        """
        with self._lock:
            if category in self._books_by_category:
                self._cache_hits += 1
                return self._books_by_category[category].copy()
            else:
                self._cache_misses += 1
                return []
    
    def get_categories(self) -> List[str]:
        """
        Get all available categories.
        
        Returns:
            Sorted list of category names
        """
        with self._lock:
            self._cache_hits += 1
            return sorted(list(self._categories))
    
    def search_books(self, 
                    category: Optional[str] = None,
                    min_price: Optional[float] = None,
                    max_price: Optional[float] = None,
                    min_rating: Optional[int] = None,
                    availability: Optional[str] = None) -> List[Book]:
        """
        Search books with multiple filters.
        
        Args:
            category: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_rating: Minimum rating filter
            availability: Availability filter (partial match)
            
        Returns:
            List of Book objects matching the filters
        """
        with self._lock:
            self._cache_hits += 1
            
            # Start with all books or books from specific category
            if category:
                books = self.get_books_by_category(category)
            else:
                books = self._books.copy()
            
            # Apply filters
            filtered_books = books
            
            if min_price is not None:
                filtered_books = [book for book in filtered_books if book.price >= min_price]
                
            if max_price is not None:
                filtered_books = [book for book in filtered_books if book.price <= max_price]
                
            if min_rating is not None:
                filtered_books = [book for book in filtered_books if book.rating_numeric >= min_rating]
                
            if availability is not None:
                availability_lower = availability.lower()
                filtered_books = [book for book in filtered_books 
                                if availability_lower in book.availability.lower()]
            
            return filtered_books
    
    def get_top_rated_books(self, limit: int = 10) -> List[Book]:
        """
        Get top-rated books from cache.
        
        Args:
            limit: Maximum number of books to return
            
        Returns:
            List of top-rated Book objects
        """
        with self._lock:
            self._cache_hits += 1
            
            # Filter books with ratings
            books_with_ratings = [book for book in self._books if book.rating_numeric > 0]
            
            # Sort by rating (descending) and then by title (ascending) for ties
            sorted_books = sorted(
                books_with_ratings,
                key=lambda x: (-x.rating_numeric, x.title.lower())
            )
            
            return sorted_books[:limit]
    
    def get_books_by_price_range(self, min_price: float, max_price: float) -> List[Book]:
        """
        Get books within a specific price range.
        
        Args:
            min_price: Minimum price (inclusive)
            max_price: Maximum price (inclusive)
            
        Returns:
            List of Book objects within the price range
        """
        with self._lock:
            self._cache_hits += 1
            
            return [book for book in self._books 
                   if min_price <= book.price <= max_price]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics and metadata.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            return {
                "total_books": self._total_books,
                "total_categories": len(self._categories),
                "categories": sorted(list(self._categories)),
                "last_updated": self._last_updated.isoformat() if self._last_updated else None,
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "cache_hit_ratio": (self._cache_hits / (self._cache_hits + self._cache_misses) 
                                  if (self._cache_hits + self._cache_misses) > 0 else 0.0),
                "is_populated": self._total_books > 0,
            }
    
    def clear(self) -> None:
        """Clear all cached data."""
        with self._lock:
            self._books.clear()
            self._books_by_id.clear()
            self._books_by_category.clear()
            self._categories.clear()
            
            self._total_books = 0
            self._last_updated = None
            
            logger.info("Data cache cleared")
    
    def is_empty(self) -> bool:
        """Check if cache is empty."""
        with self._lock:
            return self._total_books == 0
    
    def get_size(self) -> int:
        """Get the number of books in cache."""
        with self._lock:
            return self._total_books
