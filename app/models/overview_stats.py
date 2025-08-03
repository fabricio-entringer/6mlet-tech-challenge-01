"""Overview statistics models for the API."""

from typing import Dict
from pydantic import BaseModel, Field


class PriceStats(BaseModel):
    """Price statistics for the dataset."""
    
    average: float = Field(..., description="Average price of all books")
    min: float = Field(..., description="Minimum price in the dataset")
    max: float = Field(..., description="Maximum price in the dataset")
    median: float = Field(..., description="Median price of all books")


class RatingDistributionStats(BaseModel):
    """Rating distribution statistics."""
    
    one: int = Field(0, description="Number of 1-star books")
    two: int = Field(0, description="Number of 2-star books")  
    three: int = Field(0, description="Number of 3-star books")
    four: int = Field(0, description="Number of 4-star books")
    five: int = Field(0, description="Number of 5-star books")


class AvailabilityOverview(BaseModel):
    """Availability overview statistics."""
    
    in_stock: int = Field(..., description="Number of books in stock")
    out_of_stock: int = Field(..., description="Number of books out of stock")


class OverviewStatsResponse(BaseModel):
    """Response model for overview statistics endpoint."""
    
    total_books: int = Field(..., description="Total number of books in the catalog")
    price_stats: PriceStats = Field(..., description="Price statistics")
    rating_distribution: RatingDistributionStats = Field(..., description="Rating distribution across all books")
    availability: AvailabilityOverview = Field(..., description="Availability statistics")
    categories: int = Field(..., description="Total number of categories")
    last_updated: str = Field(..., description="Timestamp of when the data was last updated")
