"""Scraping request model."""

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ScrapingRequest(BaseModel):
    """Request model for starting a scraping operation."""

    delay: Optional[float] = Field(1.0, ge=0, le=10, description="Delay between requests in seconds")
    max_retries: Optional[int] = Field(3, ge=0, le=10, description="Maximum retry attempts")
    timeout: Optional[int] = Field(10, ge=1, le=60, description="Request timeout in seconds")
    csv_filename: Optional[str] = Field("books_data.csv", description="Output CSV filename")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "delay": 1.0,
                "max_retries": 3,
                "timeout": 10,
                "csv_filename": "books_data.csv"
            }
        }
    )
