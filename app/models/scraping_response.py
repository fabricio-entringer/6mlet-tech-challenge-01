"""Scraping response model."""

from typing import Optional

from pydantic import BaseModel


class ScrapingResponse(BaseModel):
    """Response model for scraping operation."""

    message: str
    task_id: Optional[str] = None
    status: str
    estimated_duration: Optional[str] = None
