"""Scraping API endpoints."""

import asyncio
import sys
import uuid
from pathlib import Path
from typing import Dict

from fastapi import BackgroundTasks, HTTPException

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.history_logger import ScrapingHistoryLogger
from scripts.scraper_api import BooksScraperAPI

from ..models import (
    ScrapingRequest,
    ScrapingResponse,
    HistoryResponse,
    StatusResponse,
    ExecutionHistoryItem,
)

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
