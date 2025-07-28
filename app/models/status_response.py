"""Status response model."""

from typing import Optional
from pydantic import BaseModel


class StatusResponse(BaseModel):
    """Response model for scraping status."""

    is_running: bool
    task_id: Optional[str] = None
    message: str
