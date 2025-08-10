"""Scraping response model."""

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ScrapingResponse(BaseModel):
    """Response model for scraping operation."""

    message: str = Field(..., description="Response message")
    task_id: Optional[str] = Field(None, description="Unique task identifier")
    status: str = Field(..., description="Current operation status")
    estimated_duration: Optional[str] = Field(None, description="Estimated completion time")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Scraping operation started successfully",
                "task_id": "scrape_20250803_142530",
                "status": "STARTED",
                "estimated_duration": "5-10 minutes"
            }
        }
    )
