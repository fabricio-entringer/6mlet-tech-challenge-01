"""Books API endpoints."""

import csv
import math
import os
from typing import Dict, List, Optional, Union

from fastapi import HTTPException, Query

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
from ..utils import convert_price_to_float


class BooksDataService:
    """Service for handling book data operations."""

    def __init__(self):
        """Initialize the service with data file path."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.data_file = os.path.join(project_root, "data", "books_data.csv")

    def _load_books_from_csv(self) -> List[Dict[str, str]]:
        """Load all books from CSV file."""
        books = []
        try:
            if not os.path.exists(self.data_file):
                return books

            with open(self.data_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    books.append(row)
        except FileNotFoundError:
            pass
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error reading books data: {str(e)}"
            )

        return books

    def _convert_book_data(self, book_row: Dict[str, str], row_index: int) -> Optional[Book]:
        """Convert CSV row to Book model."""
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
                id=int(book_row.get("id", 0)),
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
            # Skip invalid rows
            return None

    def _apply_filters(
        self, books: List[Book], filters: Dict[str, Union[str, float, int]]
    ) -> List[Book]:
        """Apply filtering to books list."""
        filtered_books = books.copy()

        # Filter by category
        if filters.get("category"):
            category_filter = filters["category"].lower()
            filtered_books = [
                book
                for book in filtered_books
                if book.category.lower() == category_filter
            ]

        # Filter by price range
        if filters.get("min_price") is not None:
            min_price = float(filters["min_price"])
            filtered_books = [
                book for book in filtered_books if book.price >= min_price
            ]

        if filters.get("max_price") is not None:
            max_price = float(filters["max_price"])
            filtered_books = [
                book for book in filtered_books if book.price <= max_price
            ]

        # Filter by rating
        if filters.get("min_rating") is not None:
            min_rating = int(filters["min_rating"])
            filtered_books = [
                book for book in filtered_books if book.rating_numeric >= min_rating
            ]

        # Filter by availability
        if filters.get("availability"):
            availability_filter = filters["availability"].lower()
            filtered_books = [
                book
                for book in filtered_books
                if availability_filter in book.availability.lower()
            ]

        return filtered_books

    def _apply_sorting(
        self, books: List[Book], sort_by: str, order: str
    ) -> List[Book]:
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
        Get books with filtering, sorting, and pagination.

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
        # Load books from CSV
        raw_books = self._load_books_from_csv()

        # Convert to Book models, filtering out invalid rows
        all_books = []
        for index, book_row in enumerate(raw_books, start=1):
            book = self._convert_book_data(book_row, index)
            if book:
                all_books.append(book)

        # Prepare filters
        filters = {}
        if category:
            filters["category"] = category
        if min_price is not None:
            filters["min_price"] = min_price
        if max_price is not None:
            filters["max_price"] = max_price
        if min_rating is not None:
            filters["min_rating"] = min_rating
        if availability:
            filters["availability"] = availability

        # Apply filters
        filtered_books = self._apply_filters(all_books, filters)

        # Apply sorting
        sorted_books = self._apply_sorting(filtered_books, sort, order)

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
        if filters:
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
        Get a single book by its ID.

        Args:
            book_id: The unique identifier of the book

        Returns:
            Book object if found, None otherwise
        """
        
        # Load books from CSV
        raw_books = self._load_books_from_csv()
        
        # Convert to Book models and find the one with matching ID
        for index, book_row in enumerate(raw_books, start=1):
            book = self._convert_book_data(book_row, index)
            if book and book.id == book_id:
                return book

        return None

    def get_top_rated_books(self, limit: int = 10) -> TopRatedBooksResponse:
        """
        Get top-rated books with highest ratings.

        Args:
            limit: Number of books to return (1-100, default: 10)

        Returns:
            TopRatedBooksResponse with top-rated books and metadata
        """
        # Load books from CSV
        raw_books = self._load_books_from_csv()

        # Convert to Book models, filtering out invalid rows
        all_books = []
        for index, book_row in enumerate(raw_books, start=1):
            book = self._convert_book_data(book_row, index)
            if book:
                all_books.append(book)

        # Filter books with ratings (exclude books with rating 0)
        books_with_ratings = [book for book in all_books if book.rating_numeric > 0]

        # Sort by rating (descending) and then by title (ascending) for ties
        sorted_books = sorted(
            books_with_ratings,
            key=lambda x: (-x.rating_numeric, x.title.lower())
        )

        # Apply limit
        top_books = sorted_books[:limit]

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
        Get books within a specific price range with statistics.

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
        # Load books from CSV
        raw_books = self._load_books_from_csv()

        # Convert to Book models, filtering out invalid rows
        all_books = []
        for index, book_row in enumerate(raw_books, start=1):
            book = self._convert_book_data(book_row, index)
            if book:
                all_books.append(book)

        # Apply price range filter
        price_filtered_books = [
            book for book in all_books 
            if min_price <= book.price <= max_price
        ]

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


# Initialize the data service
books_data_service = BooksDataService()


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

        return books_data_service.get_books(
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
        book = books_data_service.get_book_by_id(book_id)
        
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
        return books_data_service.get_top_rated_books(limit=limit)

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

        return books_data_service.get_books_by_price_range(
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
