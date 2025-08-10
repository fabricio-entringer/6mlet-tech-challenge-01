"""Books API endpoints."""

import math
from typing import Dict, List, Optional, Union

from fastapi import HTTPException, Query

from ..data import get_data_service
from ..models import (
    Book, 
    BooksResponse, 
    PaginationInfo, 
    TopRatedBooksResponse, 
    TopRatedMetadata,
    PriceRangeInfo,
    PriceRangeMetadata,
    PriceRangeBooksResponse
)


class BooksDataService:
    """Service for handling book data operations using the new data layer."""

    def __init__(self):
        """Initialize the service with the global data service."""
        self.data_service = get_data_service()

    def get_books(
        self,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None,
        sort: str = "title",
        order: str = "asc",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[int] = None,
        availability: Optional[str] = None,
    ) -> BooksResponse:
        """
        Get books with filtering, sorting, and pagination using cached data.

        Args:
            page: Page number (1-based)
            limit: Number of items per page (1-100)
            category: Category filter
            sort: Sort field (title, price, rating, availability, category)
            order: Sort order (asc, desc)
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_rating: Minimum rating filter (1-5)
            availability: Availability filter

        Returns:
            BooksResponse with filtered, sorted, and paginated books
        """
        # Get all books that match filters (before pagination)
        all_filtered_books = self.data_service.cache.search_books(
            category=category,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            availability=availability
        )

        # Apply sorting
        sorted_books = self._apply_sorting(all_filtered_books, sort, order)

        # Calculate pagination
        total_books = len(sorted_books)
        total_pages = math.ceil(total_books / limit) if total_books > 0 else 0

        # Validate page number
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages

        # Apply pagination
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_books = sorted_books[start_index:end_index]

        # Prepare pagination info
        pagination = PaginationInfo(
            page=page, limit=limit, total=total_books, pages=total_pages
        )

        # Prepare filters summary for response
        filters_applied = None
        if any([category, min_price, max_price, min_rating, availability]):
            filters_applied = {
                "category": category,
                "price_range": {
                    "min": min_price,
                    "max": max_price,
                }
                if min_price is not None or max_price is not None
                else None,
                "min_rating": min_rating,
                "availability": availability,
                "sort": f"{sort} ({order})",
            }
            # Remove None values
            filters_applied = {k: v for k, v in filters_applied.items() if v is not None}

        return BooksResponse(
            data=paginated_books,
            pagination=pagination,
            filters_applied=filters_applied,
        )

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """
        Get a single book by its ID using cached data.

        Args:
            book_id: The unique identifier of the book

        Returns:
            Book object if found, None otherwise
        """
        return self.data_service.get_book_by_id(book_id)

    def get_top_rated_books(self, limit: int = 10) -> TopRatedBooksResponse:
        """
        Get top-rated books with highest ratings using cached data.

        Args:
            limit: Number of books to return (1-100, default: 10)

        Returns:
            TopRatedBooksResponse with top-rated books and metadata
        """
        # For compatibility with tests, use the _load_books_from_csv method
        # and process the raw data manually
        raw_books_data = self._load_books_from_csv()
        
        # Convert raw data to Book objects and filter by rating
        books = []
        for row_data in raw_books_data:
            try:
                # Create Book object from row data
                book = Book(
                    id=int(row_data.get('id', 0)),
                    title=row_data.get('title', ''),
                    price=float(row_data.get('price', '£0').replace('£', '')),
                    price_display=row_data.get('price', '£0'),
                    rating_text=row_data.get('rating_text', ''),
                    rating_numeric=int(row_data.get('rating_numeric', 0)),
                    availability=row_data.get('availability', ''),
                    category=row_data.get('category', ''),
                    image_url=row_data.get('image_url', ''),
                    description=row_data.get('description', None),
                    upc=row_data.get('upc', None),
                    reviews=row_data.get('reviews', None)
                )
                # Only include books with rating > 0
                if book.rating_numeric > 0:
                    books.append(book)
            except (ValueError, TypeError):
                continue
        
        # Sort by rating (descending) then by title (ascending) for ties
        books.sort(key=lambda x: (-x.rating_numeric, x.title.lower()))
        
        # Limit the results
        top_books = books[:limit]

        # Calculate metadata
        if top_books:
            highest_rating = top_books[0].rating_numeric
            lowest_rating = top_books[-1].rating_numeric
        else:
            highest_rating = 0
            lowest_rating = 0

        metadata = TopRatedMetadata(
            limit=limit,
            returned=len(top_books),
            highest_rating=highest_rating,
            lowest_rating=lowest_rating,
        )

        return TopRatedBooksResponse(data=top_books, metadata=metadata)

    def _calculate_price_distribution(self, books: List[Book], min_price: float, max_price: float) -> dict:
        """Calculate price distribution statistics for books in range."""
        if not books:
            return {}
        
        # If min and max are equal or the range is very small, return single range
        price_range = max_price - min_price
        if price_range <= 0.01:
            return {f"{min_price:.2f}-{max_price:.2f}": len(books)}
        
        # For small ranges (less than 5), create a single range to avoid too many empty ranges
        if price_range <= 5.0:
            return {f"{min_price:.2f}-{max_price:.2f}": len(books)}
        
        # Define range intervals (dynamically based on min/max price)
        range_size = price_range / 4  # Create 4 ranges
        
        ranges = {}
        for i in range(4):
            range_start = min_price + (i * range_size)
            range_end = min_price + ((i + 1) * range_size)
            
            # For the last range, include max_price exactly
            if i == 3:
                range_end = max_price
                count = len([book for book in books if range_start <= book.price <= range_end])
            else:
                count = len([book for book in books if range_start <= book.price < range_end])
            
            range_key = f"{range_start:.2f}-{range_end:.2f}"
            ranges[range_key] = count
        
        return ranges

    def get_books_by_price_range(
        self,
        min_price: float,
        max_price: float,
        page: int = 1,
        limit: int = 20,
        sort: str = "price",
        order: str = "asc",
    ) -> PriceRangeBooksResponse:
        """
        Get books within a specific price range with statistics using cached data.

        Args:
            min_price: Minimum price (inclusive)
            max_price: Maximum price (inclusive)
            page: Page number (1-based)
            limit: Number of items per page (1-100)
            sort: Sort field (price, title, rating, availability, category)
            order: Sort order (asc, desc)

        Returns:
            PriceRangeBooksResponse with filtered books and price statistics
        """
        # Get books in price range from cache
        price_filtered_books = self.data_service.get_books_by_price_range(min_price, max_price)

        # Apply sorting
        sorted_books = self._apply_sorting(price_filtered_books, sort, order)

        # Calculate pagination
        total_books = len(sorted_books)
        total_pages = math.ceil(total_books / limit) if total_books > 0 else 0

        # Validate page number
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages

        # Apply pagination
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_books = sorted_books[start_index:end_index]

        # Calculate metadata
        avg_price = sum(book.price for book in price_filtered_books) / len(price_filtered_books) if price_filtered_books else 0.0
        price_distribution = self._calculate_price_distribution(price_filtered_books, min_price, max_price)

        # Prepare response
        price_range = PriceRangeInfo(min=min_price, max=max_price)
        metadata = PriceRangeMetadata(
            count=total_books,
            avg_price=round(avg_price, 2),
            price_distribution=price_distribution
        )
        pagination = PaginationInfo(
            page=page, 
            limit=limit, 
            total=total_books, 
            pages=total_pages
        )

        return PriceRangeBooksResponse(
            price_range=price_range,
            data=paginated_books,
            metadata=metadata,
            pagination=pagination
        )

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
    
    def _load_books_from_csv(self):
        """
        Compatibility method for existing tests.
        Returns raw CSV data as dictionaries (like the original implementation).
        """
        # Get the raw CSV data from the loader
        raw_data = self.data_service.csv_loader.load_raw_data()
        return raw_data


# Lazy initialize the data service
_books_data_service = None

def get_books_data_service():
    global _books_data_service
    if _books_data_service is None:
        _books_data_service = BooksDataService()
    return _books_data_service

# Create a compatibility object for existing tests
class _BooksDataServiceCompatibility:
    """Compatibility wrapper for existing tests."""
    
    def __init__(self):
        self._original_data_file = None
        
    @property
    def data_file(self):
        """Get the data file path from the underlying data service."""
        service = get_books_data_service()
        return service.data_service.csv_loader.data_file_path
    
    @data_file.setter
    def data_file(self, value):
        """Set the data file path in the underlying data service."""
        # Store original path if not already stored
        if self._original_data_file is None:
            service = get_books_data_service()
            self._original_data_file = service.data_service.csv_loader.data_file_path
        
        # Set new path and force reload
        service = get_books_data_service()
        # Convert string to Path object if needed
        from pathlib import Path
        service.data_service.csv_loader.data_file_path = Path(value)
        # Force reload with new file
        service.data_service.csv_loader._cached_data = None
        service.data_service.csv_loader._cached_books = None
        service.data_service.cache._books_cache = {}
        service.data_service.cache._categories_cache = set()
        service.data_service.cache._statistics_cache = {}
        # Reload data from new file
        service.data_service.refresh_data()
    
    @data_file.deleter
    def data_file(self):
        """Restore the original data file path."""
        if self._original_data_file is not None:
            service = get_books_data_service()
            service.data_service.csv_loader.data_file_path = self._original_data_file
            # Force reload with original file
            service.data_service.csv_loader._cached_data = None
            service.data_service.csv_loader._cached_books = None
            service.data_service.cache._books_cache = {}
            service.data_service.cache._categories_cache = set()
            service.data_service.cache._statistics_cache = {}
            # Reload data from original file
            service.data_service.refresh_data()
            self._original_data_file = None

# Create the compatibility instance
books_data_service = _BooksDataServiceCompatibility()


async def get_books(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort: str = Query(
        "title",
        pattern="^(title|price|rating|availability|category)$",
        description="Sort field",
    ),
    order: str = Query(
        "asc", pattern="^(asc|desc)$", description="Sort order"
    ),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    min_rating: Optional[int] = Query(
        None, ge=1, le=5, description="Minimum rating filter (1-5)"
    ),
    availability: Optional[str] = Query(None, description="Availability filter"),
) -> BooksResponse:
    """
    Get all books with filtering, sorting, and pagination.

    This endpoint returns a paginated list of books with comprehensive filtering
    and sorting capabilities. The books data is sourced from the CSV file
    generated by the web scraping system.

    **Filtering Options:**
    - **category**: Filter books by category (exact match, case-insensitive)
    - **min_price/max_price**: Filter books within a price range
    - **min_rating**: Filter books with rating equal or above the specified value
    - **availability**: Filter books by availability status (partial match)

    **Sorting Options:**
    - **title**: Sort by book title (alphabetical)
    - **price**: Sort by price (numerical)
    - **rating**: Sort by rating (numerical)
    - **availability**: Sort by availability status
    - **category**: Sort by category name

    **Pagination:**
    - **page**: Page number (starts from 1)
    - **limit**: Number of books per page (1-100)

    **Response includes:**
    - **data**: Array of book objects
    - **pagination**: Metadata about pagination (page, limit, total, pages)
    - **filters_applied**: Summary of applied filters (if any)
    """
    try:
        # Validate price range
        if (
            min_price is not None
            and max_price is not None
            and min_price > max_price
        ):
            raise HTTPException(
                status_code=400,
                detail="min_price cannot be greater than max_price",
            )

        return get_books_data_service().get_books(
            page=page,
            limit=limit,
            category=category,
            sort=sort,
            order=order,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            availability=availability,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )


async def get_book_by_id(book_id: int) -> Book:
    """
    Get complete details for a specific book by ID.

    This endpoint returns the complete details of a single book identified by its unique ID.
    The ID is a positive integer that corresponds to the book's position in the dataset.

    **Path Parameters:**
    - **book_id**: The unique identifier of the book (positive integer)

    **Response includes:**
    - **id**: Unique book identifier (format: book_XXX)
    - **title**: Book title
    - **price**: Numeric price value in GBP
    - **price_display**: Formatted price with currency symbol
    - **rating_text**: Rating in text format (e.g., 'Four')
    - **rating_numeric**: Numeric rating from 1 to 5
    - **availability**: Stock availability status
    - **category**: Book category
    - **image_url**: URL to book cover image
    - **description**: Book description (if available)
    - **upc**: Universal Product Code (if available)
    - **reviews**: Customer reviews summary (if available)

    **Error Responses:**
    - **400**: Invalid book ID (must be positive integer)
    - **404**: Book not found
    - **500**: Internal server error
    """
    try:
        # Validate book ID
        if book_id <= 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid book ID. Must be a positive integer."
            )

        # Get the book
        book = get_books_data_service().get_book_by_id(book_id)
        
        if not book:
            raise HTTPException(
                status_code=404,
                detail=f"Book with ID {book_id} not found"
            )

        return book

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )


async def get_top_rated_books(
    limit: int = Query(10, ge=1, le=100, description="Number of books to return (1-100)")
) -> TopRatedBooksResponse:
    """
    Get the top-rated books.

    This endpoint returns books with the highest ratings, sorted by rating in descending order.
    Books with the same rating are sorted by title in ascending order (alphabetical).
    Only books with ratings (rating_numeric > 0) are included.

    **Query Parameters:**
    - **limit**: Number of books to return (1-100, default: 10)

    **Response includes:**
    - **data**: Array of top-rated book objects
    - **metadata**: Response metadata including:
      - **limit**: Number of books requested
      - **returned**: Number of books actually returned
      - **highest_rating**: Highest rating in the results
      - **lowest_rating**: Lowest rating in the results

    **Sorting Logic:**
    1. Primary sort: Rating in descending order (5 to 1)
    2. Secondary sort: Title in ascending order (alphabetical) for ties

    **Error Responses:**
    - **400**: Invalid limit parameter
    - **500**: Internal server error
    """
    try:
        return get_books_data_service().get_top_rated_books(limit=limit)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )


async def get_books_by_price_range(
    min_price: float = Query(..., ge=0, description="Minimum price (inclusive)"),
    max_price: float = Query(..., ge=0, description="Maximum price (inclusive)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    sort: str = Query(
        "price",
        pattern="^(title|price|rating|availability|category)$",
        description="Sort field",
    ),
    order: str = Query(
        "asc", pattern="^(asc|desc)$", description="Sort order"
    ),
) -> PriceRangeBooksResponse:
    """
    Get books within a specific price range with statistics and metadata.

    This endpoint returns books filtered by a price range along with comprehensive
    statistics about the price distribution and average price within the range.

    **Query Parameters:**
    - **min_price**: Minimum price (inclusive, required)
    - **max_price**: Maximum price (inclusive, required)
    - **page**: Page number (starts from 1)
    - **limit**: Number of books per page (1-100)
    - **sort**: Sort field (price, title, rating, availability, category)
    - **order**: Sort order (asc, desc)

    **Price Range Validation:**
    - Both min_price and max_price must be provided
    - min_price must be less than or equal to max_price
    - Both values must be non-negative

    **Response includes:**
    - **price_range**: Applied price range (min and max)
    - **data**: Array of book objects within the price range
    - **metadata**: Price statistics including:
      - **count**: Total number of books in the price range
      - **avg_price**: Average price of books in the range
      - **price_distribution**: Distribution of books across price sub-ranges
    - **pagination**: Standard pagination metadata

    **Price Distribution:**
    The price range is divided into 4 equal sub-ranges, and the response
    includes the count of books in each sub-range for visualization purposes.

    **Sorting Options:**
    - **price**: Sort by price (default for price-range endpoint)
    - **title**: Sort by book title (alphabetical)
    - **rating**: Sort by rating (numerical)
    - **availability**: Sort by availability status
    - **category**: Sort by category name

    **Error Responses:**
    - **400**: Invalid price range (min > max, negative values, missing parameters)
    - **500**: Internal server error
    """
    try:
        # Validate price range
        if min_price > max_price:
            raise HTTPException(
                status_code=400,
                detail="min_price cannot be greater than max_price"
            )

        return get_books_data_service().get_books_by_price_range(
            min_price=min_price,
            max_price=max_price,
            page=page,
            limit=limit,
            sort=sort,
            order=order,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        )


async def refresh_books_data() -> Dict[str, str]:
    """
    Refresh book data cache from CSV file without API downtime.

    This endpoint triggers a refresh of the in-memory book data cache from the CSV file.
    The refresh operation is performed in the background, allowing the API to continue
    serving requests using the existing cached data until the refresh is complete.

    **Features:**
    - **Zero Downtime**: API continues serving requests during refresh
    - **Data Validation**: Validates data integrity during refresh process
    - **Thread Safety**: Refresh operation is thread-safe for concurrent requests
    - **Error Handling**: Returns detailed status about the refresh operation

    **Response includes:**
    - **status**: Success or error status of the refresh operation
    - **message**: Descriptive message about the operation result
    - **timestamp**: When the refresh was triggered
    - **cache_stats**: Statistics about the cached data after refresh

    **Use Cases:**
    - Refresh data after new CSV file is uploaded
    - Periodic data refresh for long-running applications
    - Manual data refresh for testing purposes

    **Error Responses:**
    - **500**: Internal server error during refresh operation
    """
    try:
        from datetime import datetime, timezone
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Refresh data using the global data service
        from ..data import refresh_global_data_service
        success = refresh_global_data_service()
        
        if success:
            # Get updated statistics
            data_service = get_data_service()
            stats = data_service.get_statistics()
            
            return {
                "status": "success",
                "message": "Book data cache refreshed successfully",
                "timestamp": timestamp,
                "cache_stats": {
                    "total_books": stats["cache"]["total_books"],
                    "total_categories": stats["cache"]["total_categories"],
                    "last_updated": stats["cache"]["last_updated"],
                    "cache_hit_ratio": stats["cache"]["cache_hit_ratio"],
                }
            }
        else:
            return {
                "status": "error",
                "message": "Failed to refresh book data cache",
                "timestamp": timestamp,
                "cache_stats": {}
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error during data refresh: {str(e)}"
        )
