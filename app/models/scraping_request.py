"""Scraping request model."""

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ScrapingRequest(BaseModel):
    """
    Request model for starting a scraping operation.
    
    Configure scraping parameters for data collection from books.toscrape.com.
    All parameters are optional with sensible defaults for safe scraping.
    """

    delay: Optional[float] = Field(
        1.0, 
        ge=0, 
        le=10, 
        description="Delay between requests in seconds to respect server resources"
    )
    max_retries: Optional[int] = Field(
        3, 
        ge=0, 
        le=10, 
        description="Maximum retry attempts for failed requests"
    )
    timeout: Optional[int] = Field(
        10, 
        ge=1, 
        le=60, 
        description="Request timeout in seconds for each HTTP request"
    )
    csv_filename: Optional[str] = Field(
        "books_data.csv", 
        description="Output CSV filename for scraped data storage"
    )

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
