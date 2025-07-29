"""Main FastAPI application."""

from typing import Optional

from fastapi import BackgroundTasks, FastAPI, Query

from ..models import (
    BookResponse,
    BooksResponse,
    CategoriesResponse,
    HistoryResponse,
    ScrapingRequest,
    ScrapingResponse,
    StatusResponse,
    TopRatedBooksResponse,
    PriceRangeBooksResponse,
)
from ..utils import get_version
from . import books, categories, core, scraping

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


# Books endpoints
@app.get("/api/v1/books", response_model=BooksResponse)
async def get_books(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort: str = Query(
        "title",
        pattern="^(title|price|rating|availability|category)$",
        description="Sort field",
    ),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    min_rating: Optional[int] = Query(
        None, ge=1, le=5, description="Minimum rating filter (1-5)"
    ),
    availability: Optional[str] = Query(None, description="Availability filter"),
) -> BooksResponse:
    """Get all books with filtering, sorting, and pagination."""
    return await books.get_books(
        page, limit, category, sort, order, min_price, max_price, min_rating, availability
    )


@app.get("/api/v1/books/top-rated", response_model=TopRatedBooksResponse)
async def get_top_rated_books(
    limit: int = Query(10, ge=1, le=100, description="Number of books to return (1-100)")
) -> TopRatedBooksResponse:
    """Get the top-rated books."""
    return await books.get_top_rated_books(limit)


@app.get("/api/v1/books/price-range", response_model=PriceRangeBooksResponse)
async def get_books_by_price_range(
    min_price: float = Query(..., ge=0, description="Minimum price (inclusive)"),
    max_price: float = Query(..., ge=0, description="Maximum price (inclusive)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    sort: str = Query(
        "price",
        pattern="^(title|price|rating|availability|category)$",
        description="Sort field",
    ),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
) -> PriceRangeBooksResponse:
    """Get books within a specific price range with statistics."""
    return await books.get_books_by_price_range(
        min_price, max_price, page, limit, sort, order
    )


@app.get("/api/v1/books/{book_id}")
async def get_book_by_id(book_id: int):
    """Get complete details for a specific book by ID."""
    return await books.get_book_by_id(book_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
