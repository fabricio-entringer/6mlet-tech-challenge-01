import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.scraper_api import BooksScraperAPI
from scripts.history_logger import ScrapingHistoryLogger

from .utils import get_version

app_version = get_version()


# Pydantic models for API responses
class ScrapingRequest(BaseModel):
    """Request model for starting a scraping operation."""

    delay: Optional[float] = 0
    max_retries: Optional[int] = 3
    timeout: Optional[int] = 10


class ScrapingResponse(BaseModel):
    """Response model for scraping operation."""

    message: str
    task_id: Optional[str] = None
    status: str
    estimated_duration: Optional[str] = None


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


class StatusResponse(BaseModel):
    """Response model for scraping status."""

    is_running: bool
    task_id: Optional[str] = None
    message: str


# Global variable to track current scraping status
current_scraping_status = {"is_running": False, "task_id": None}


async def run_scraping_task(delay: float, max_retries: int, timeout: int) -> None:
    """
    Background task to run the scraping operation.

    Args:
        delay: Delay between requests in seconds
        max_retries: Maximum retry attempts
        timeout: Request timeout in seconds
    """
    try:
        current_scraping_status["is_running"] = True

        # Initialize a fresh scraper API instance for each task with default output directory
        api = BooksScraperAPI(delay=delay, max_retries=max_retries, timeout=timeout)

        # Run the scraping with default settings - always save CSV with default filename
        result = api.scrape_all_books(
            save_csv=True, csv_filename=None  # Use default filename from config
        )

        print(f"✅ Scraping completed: {result['total_books']} books scraped")

    except Exception as e:
        print(f"❌ Scraping failed: {e}")

    finally:
        current_scraping_status["is_running"] = False
        current_scraping_status["task_id"] = None


app = FastAPI(
    title="6MLET Tech Challenge 01 API",
    description="A FastAPI application for the FIAP 6MLET tech challenge 01",
    version=app_version,
)


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint that returns a welcome message.

    Returns:
        Dict[str, str]: A dictionary containing a welcome message
    """
    return {"message": "Welcome to 6MLET Tech Challenge 01 API"}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Dict[str, str]: A dictionary indicating the service status
    """
    return {"status": "healthy"}


@app.get("/version")
async def get_version() -> Dict[str, str]:
    """
    Version endpoint that returns the current application version.

    Returns:
        Dict[str, str]: A dictionary containing the current version
    """
    return {"version": app_version}


@app.post("/scraping/start", response_model=ScrapingResponse)
async def start_scraping(
    request: ScrapingRequest, background_tasks: BackgroundTasks
) -> ScrapingResponse:
    """
    Start a book scraping operation.

    This endpoint initiates a background scraping task that will extract all books
    from books.toscrape.com and save them to a CSV file with the default filename
    'books_data.csv' in the 'data' directory. The operation runs asynchronously
    and its progress can be monitored through the history endpoint.

    Args:
        request: Scraping configuration parameters (delay, max_retries, timeout)
        background_tasks: FastAPI background tasks manager

    Returns:
        ScrapingResponse: Status and details about the started scraping task

    Raises:
        HTTPException: If a scraping operation is already running
    """
    # Check if scraping is already running
    if current_scraping_status["is_running"]:
        raise HTTPException(
            status_code=409,
            detail="A scraping operation is already running. Please wait for it to complete.",
        )

    # Generate a simple task ID
    import uuid

    task_id = str(uuid.uuid4())[:8]
    current_scraping_status["task_id"] = task_id

    # Add the scraping task to background tasks with only the essential parameters
    background_tasks.add_task(
        run_scraping_task,
        delay=request.delay,
        max_retries=request.max_retries,
        timeout=request.timeout,
    )

    return ScrapingResponse(
        message="Scraping operation started successfully",
        task_id=task_id,
        status="RUNNING",
        estimated_duration="5-10 minutes (depending on network conditions)",
    )


@app.get("/scraping/history", response_model=HistoryResponse)
async def get_scraping_history(include_all: bool = False) -> HistoryResponse:
    """
    Get the execution history of scraping operations.

    This endpoint returns detailed information about all previous scraping
    operations including timestamps, duration, success/failure status,
    number of books scraped, and configuration details.

    Args:
        include_all: If True, includes all execution records in the response

    Returns:
        HistoryResponse: Complete history summary and optionally all execution records

    Raises:
        HTTPException: If there's an error reading the history file
    """
    try:
        history_logger = ScrapingHistoryLogger()
        summary = history_logger.get_history_summary()

        if "error" in summary:
            raise HTTPException(
                status_code=500, detail=f"Error reading history: {summary['error']}"
            )

        # Convert latest execution to model if it exists
        latest_execution = None
        if summary.get("latest_execution"):
            latest = summary["latest_execution"]
            latest_execution = ExecutionHistoryItem(**latest)

        # Prepare response
        response = HistoryResponse(
            total_executions=summary["total_executions"],
            successful_executions=summary["successful_executions"],
            failed_executions=summary["failed_executions"],
            partial_executions=summary["partial_executions"],
            total_books_scraped=summary["total_books_scraped"],
            latest_execution=latest_execution,
            history_file=summary["history_file"],
        )

        # If requested, include all execution records
        if include_all and summary["total_executions"] > 0:
            import csv

            executions = []
            try:
                with open(summary["history_file"], "r", encoding="utf-8") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        executions.append(ExecutionHistoryItem(**row))
                response.executions = executions
            except Exception as e:
                # If we can't read all records, just continue without them
                pass

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/scraping/status", response_model=StatusResponse)
async def get_scraping_status() -> StatusResponse:
    """
    Get the current status of scraping operations.

    Returns:
        StatusResponse containing current scraping status and task information
    """
    return StatusResponse(
        is_running=current_scraping_status["is_running"],
        task_id=current_scraping_status["task_id"],
        message=(
            "Scraping in progress"
            if current_scraping_status["is_running"]
            else "No active scraping operation"
        ),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
