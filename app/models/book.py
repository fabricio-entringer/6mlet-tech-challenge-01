"""Book model and related response models."""

from typing import List, Optional

from pydantic import BaseModel, Field


class Book(BaseModel):
    """Model representing a single book."""

    title: str = Field(..., description="Book title")
    price: float = Field(..., description="Book price in GBP")
    price_display: str = Field(..., description="Book price with currency symbol")
    rating_text: str = Field(..., description="Rating in text format (e.g., 'Four')")
    rating_numeric: int = Field(..., ge=1, le=5, description="Numeric rating from 1 to 5")
    availability: str = Field(..., description="Stock availability status")
    category: str = Field(..., description="Book category")
    image_url: str = Field(..., description="URL to book cover image")


class PaginationInfo(BaseModel):
    """Pagination metadata."""

    page: int = Field(..., ge=1, description="Current page number")
    limit: int = Field(..., ge=1, le=100, description="Number of items per page")
    total: int = Field(..., ge=0, description="Total number of items")
    pages: int = Field(..., ge=0, description="Total number of pages")


class BooksResponse(BaseModel):
    """Response model for the books endpoint."""

    data: List[Book] = Field(..., description="List of books")
    pagination: PaginationInfo = Field(..., description="Pagination information")
    filters_applied: Optional[dict] = Field(None, description="Applied filters summary")
