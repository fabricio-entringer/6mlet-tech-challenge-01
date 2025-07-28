"""History response model."""

from typing import List, Optional

from pydantic import BaseModel

from .execution_history_item import ExecutionHistoryItem


class HistoryResponse(BaseModel):
    """Response model for execution history."""

    total_executions: int
    successful_executions: int
    failed_executions: int
    partial_executions: int
    total_books_scraped: int
    latest_execution: Optional[ExecutionHistoryItem] = None
    history_file: str
    executions: Optional[List[ExecutionHistoryItem]] = None
