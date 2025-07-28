"""Execution history item model."""

from pydantic import BaseModel


class ExecutionHistoryItem(BaseModel):
    """Model for a single execution history item."""

    timestamp: str
    execution_type: str
    duration_seconds: str
    total_books_scraped: str
    total_categories: str
    output_file: str
    status: str
    error_message: str
    configuration: str
