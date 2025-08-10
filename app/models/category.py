"""Category model for book categories."""

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class PriceRange(BaseModel):
    """Price range for a category."""

    min: float = Field(..., ge=0, description="Minimum price in the category")
    max: float = Field(..., gt=0, description="Maximum price in the category")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "min": 10.00,
                "max": 59.99
            }
        }
    )


class Category(BaseModel):
    """Individual category model."""

    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly category identifier")
    book_count: int = Field(..., ge=0, description="Number of books in this category")
    avg_price: Optional[float] = Field(
        None, gt=0, description="Average price of books in this category"
    )
    avg_rating: Optional[float] = Field(
        None, ge=1, le=5, description="Average rating of books in this category"
    )
    price_range: Optional[PriceRange] = Field(
        None, description="Price range for books in this category"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Fiction",
                "slug": "fiction",
                "book_count": 65,
                "avg_price": 47.82,
                "avg_rating": 3.2,
                "price_range": {
                    "min": 10.00,
                    "max": 59.99
                }
            }
        }
    )


class CategoriesResponse(BaseModel):
    """Response model for categories endpoint."""

    categories: list[Category] = Field(..., description="List of categories")
    total_categories: int = Field(..., ge=0, description="Total number of categories")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "categories": [
                    {
                        "name": "Fiction",
                        "slug": "fiction",
                        "book_count": 65,
                        "avg_price": 47.82,
                        "avg_rating": 3.2,
                        "price_range": {
                            "min": 10.00,
                            "max": 59.99
                        }
                    },
                    {
                        "name": "Poetry",
                        "slug": "poetry",
                        "book_count": 19,
                        "avg_price": 32.15,
                        "avg_rating": 3.8,
                        "price_range": {
                            "min": 15.99,
                            "max": 51.77
                        }
                    }
                ],
                "total_categories": 50
            }
        }
    )
