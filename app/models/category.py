"""Category model for book categories."""

from typing import Optional

from pydantic import BaseModel, Field


class PriceRange(BaseModel):
    """Price range for a category."""
    
    min: float = Field(..., description="Minimum price in the category")
    max: float = Field(..., description="Maximum price in the category")


class Category(BaseModel):
    """Individual category model."""
    
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly category identifier")
    book_count: int = Field(..., description="Number of books in this category")
    avg_price: Optional[float] = Field(None, description="Average price of books in this category")
    avg_rating: Optional[float] = Field(None, description="Average rating of books in this category")
    price_range: Optional[PriceRange] = Field(None, description="Price range for books in this category")


class CategoriesResponse(BaseModel):
    """Response model for categories endpoint."""
    
    categories: list[Category] = Field(..., description="List of categories")
    total_categories: int = Field(..., description="Total number of categories")
