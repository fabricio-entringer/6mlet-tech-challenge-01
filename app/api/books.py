"""Books API endpoints."""

import csv
import math
import os
from typing import Dict, List, Optional, Union

from fastapi import HTTPException, Query

from ..models import Book, BooksResponse, PaginationInfo
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

    def _convert_book_data(self, book_row: Dict[str, str]) -> Optional[Book]:
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
                title=book_row.get("title", "").strip(),
                price=price_float,
                price_display=book_row.get("price", "£0.00"),
                rating_text=book_row.get("rating_text", "").strip(),
                rating_numeric=rating_numeric,
                availability=book_row.get("availability", "").strip(),
                category=book_row.get("category", "").strip(),
                image_url=book_row.get("image_url", "").strip(),
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
        for book_row in raw_books:
            book = self._convert_book_data(book_row)
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
