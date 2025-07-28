"""Scraping request model."""

from typing import Optional
from pydantic import BaseModel


class ScrapingRequest(BaseModel):
    """Request model for starting a scraping operation."""

    delay: Optional[float] = 0
    max_retries: Optional[int] = 3
    timeout: Optional[int] = 10
