"""Category statistics models for the API."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class RatingDistribution(BaseModel):
    """Rating distribution for a category."""
    
    one: int = Field(0, description="Number of 1-star books")
    two: int = Field(0, description="Number of 2-star books")
    three: int = Field(0, description="Number of 3-star books")
    four: int = Field(0, description="Number of 4-star books")
    five: int = Field(0, description="Number of 5-star books")


class AvailabilityStats(BaseModel):
    """Availability statistics for a category."""
    
    in_stock: int = Field(0, description="Number of books in stock")
    out_of_stock: int = Field(0, description="Number of books out of stock")


class CategoryStatistics(BaseModel):
    """Detailed statistics for a single category."""
    
    book_count: int = Field(..., description="Total number of books in category")
    avg_price: Optional[float] = Field(None, description="Average price of books")
    price_range: Optional[Dict[str, float]] = Field(None, description="Min and max prices")
    avg_rating: Optional[float] = Field(None, description="Average rating of books")
    rating_distribution: Optional[RatingDistribution] = Field(None, description="Distribution of ratings")
    availability: Optional[AvailabilityStats] = Field(None, description="Availability statistics")


class CategoryStatsItem(BaseModel):
    """Category with its statistics."""
    
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly category identifier")
    stats: CategoryStatistics = Field(..., description="Category statistics")


class StatsSummary(BaseModel):
    """Summary information for the statistics response."""
    
    total_categories: int = Field(..., description="Total number of categories in database")
    categories_analyzed: int = Field(..., description="Number of categories included in this response")


class CategoryStatsResponse(BaseModel):
    """Response model for category statistics endpoint."""
    
    categories: List[CategoryStatsItem] = Field(..., description="List of categories with statistics")
    summary: StatsSummary = Field(..., description="Summary information")
