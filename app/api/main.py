"""Main FastAPI application."""

from fastapi import BackgroundTasks, FastAPI, Query

from ..models import (
    CategoriesResponse,
    HistoryResponse,
    ScrapingRequest,
    ScrapingResponse,
    StatusResponse,
)
from ..utils import get_version
from . import categories, core, scraping

app_version = get_version()

app = FastAPI(
    title="6MLET Tech Challenge 01 API",
    description="A FastAPI application for the FIAP 6MLET tech challenge 01",
    version=app_version,
)


# Core endpoints
@app.get("/")
async def root():
    """Root endpoint that returns a welcome message."""
    return await core.root()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return await core.health_check()


@app.get("/version")
async def get_version():
    """Version endpoint that returns the current application version."""
    return await core.get_version_endpoint()


# Scraping endpoints
@app.post("/scraping/start", response_model=ScrapingResponse)
async def start_scraping(
    request: ScrapingRequest, background_tasks: BackgroundTasks
) -> ScrapingResponse:
    """Start a book scraping operation."""
    return await scraping.start_scraping(request, background_tasks)


@app.get("/scraping/history", response_model=HistoryResponse)
async def get_scraping_history(include_all: bool = False) -> HistoryResponse:
    """Get the execution history of scraping operations."""
    return await scraping.get_scraping_history(include_all)


@app.get("/scraping/status", response_model=StatusResponse)
async def get_scraping_status() -> StatusResponse:
    """Get the current status of scraping operations."""
    return await scraping.get_scraping_status()


# Categories endpoints
@app.get("/api/v1/categories", response_model=CategoriesResponse)
async def get_categories(
    sort: str = Query("name", description="Sort by 'name' or 'count'"),
    order: str = Query("asc", description="Sort order: 'asc' or 'desc'"),
    include_stats: bool = Query(True, description="Include statistics (price, rating)"),
) -> CategoriesResponse:
    """Get all book categories with optional statistics."""
    return await categories.get_categories(sort, order, include_stats)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
