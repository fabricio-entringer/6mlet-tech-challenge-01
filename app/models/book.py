"""Book model and related response models."""

from typing import List, Optional

from pydantic import BaseModel, Field


class Book(BaseModel):
    """Model representing a single book."""

    id: int = Field(..., description="Unique book identifier")
    title: str = Field(..., description="Book title")
    price: float = Field(..., description="Book price in GBP")
    price_display: str = Field(..., description="Book price with currency symbol")
    rating_text: str = Field(..., description="Rating in text format (e.g., 'Four')")
    rating_numeric: int = Field(..., ge=1, le=5, description="Numeric rating from 1 to 5")
    availability: str = Field(..., description="Stock availability status")
    category: str = Field(..., description="Book category")
    image_url: str = Field(..., description="URL to book cover image")
    description: Optional[str] = Field(None, description="Book description")
    upc: Optional[str] = Field(None, description="Universal Product Code")
    reviews: Optional[str] = Field(None, description="Customer reviews summary")


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


class TopRatedMetadata(BaseModel):
    """Metadata for the top-rated books response."""

    limit: int = Field(..., ge=1, le=100, description="Number of books requested")
    returned: int = Field(..., ge=0, description="Number of books returned")
    highest_rating: int = Field(..., ge=0, le=5, description="Highest rating in results")
    lowest_rating: int = Field(..., ge=0, le=5, description="Lowest rating in results")


class TopRatedBooksResponse(BaseModel):
    """Response model for the top-rated books endpoint."""

    data: List[Book] = Field(..., description="List of top-rated books")
    metadata: TopRatedMetadata = Field(..., description="Response metadata")


class BookResponse(BaseModel):
    """Response model for single book endpoint."""

    data: Book = Field(..., description="Book details")


class PriceRangeInfo(BaseModel):
    """Price range information."""
    
    min: float = Field(..., description="Minimum price")
    max: float = Field(..., description="Maximum price")


class PriceDistribution(BaseModel):
    """Price distribution statistics."""
    
    ranges: dict = Field(..., description="Price distribution by ranges")


class PriceRangeMetadata(BaseModel):
    """Metadata for the price-range response."""
    
    count: int = Field(..., ge=0, description="Number of books in the price range")
    avg_price: float = Field(..., ge=0, description="Average price of books in range")
    price_distribution: dict = Field(..., description="Price distribution statistics")


class PriceRangeBooksResponse(BaseModel):
    """Response model for the price-range books endpoint."""
    
    price_range: PriceRangeInfo = Field(..., description="Applied price range")
    data: List[Book] = Field(..., description="List of books within price range")
    metadata: PriceRangeMetadata = Field(..., description="Price range metadata")
    pagination: PaginationInfo = Field(..., description="Pagination information")
