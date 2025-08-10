"""Main FastAPI application."""

from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query

from ..models import (
    BookResponse,
    BooksResponse,
    CategoriesResponse,
    CategoryStatsResponse,
    OverviewStatsResponse,
    HistoryResponse,
    ScrapingRequest,
    ScrapingResponse,
    StatusResponse,
    TopRatedBooksResponse,
    PriceRangeBooksResponse,
    HealthResponse,
)
from ..ml import (
    FeatureEngineer,
    TrainingDataProcessor, 
    PredictionService,
    MLFeaturesResponse,
    TrainingDataResponse,
    PredictionRequest,
    PredictionResponse
)
from ..utils import get_version
from . import books, categories, category_stats, overview_stats, core, scraping

app_version = get_version()

# Enhanced OpenAPI configuration according to issue #26
app = FastAPI(
    title="Books API",
    description="""
<h2>Tech Challenge - Books Catalog API</h2>

<p>A comprehensive REST API for managing and exploring a books catalog, built as part of the FIAP 6MLET tech challenge.</p>

<h3>Features</h3>

<ul>
<li><strong>Books Management:</strong> Browse, search, and filter books with advanced pagination</li>
<li><strong>Category Analytics:</strong> Get detailed statistics and insights by book categories</li>
<li><strong>Health Monitoring:</strong> Comprehensive system health checks with detailed metrics</li>
<li><strong>Data Scraping:</strong> Automated book data collection and management</li>
<li><strong>ML Pipeline:</strong> Machine learning features for price prediction and analysis</li>
<li><strong>Real-time Statistics:</strong> Overview and category-specific statistics</li>
</ul>

<h3>API Versioning</h3>

<p>This API follows semantic versioning. Current version includes:</p>
<ul>
<li>v1 endpoints for stable production use</li>
<li>Comprehensive error handling and validation</li>
<li>Rate limiting and performance optimization</li>
</ul>

<h3>Data Source</h3>

<p>Book data is collected through web scraping from books.toscrape.com and stored locally for fast access.</p>

<h3>Authentication</h3>

<p>Currently, this API does not require authentication. All endpoints are publicly accessible.</p>
<p>In a production environment, consider implementing:</p>
<ul>
<li>API key authentication</li>
<li>Rate limiting per user</li>
<li>OAuth2 integration</li>
</ul>

<h3>Error Handling</h3>

<p>The API uses standard HTTP status codes:</p>
<ul>
<li><strong>200:</strong> Success</li>
<li><strong>400:</strong> Bad Request - Invalid parameters</li>
<li><strong>404:</strong> Not Found - Resource doesn't exist</li>
<li><strong>422:</strong> Validation Error - Invalid request body</li>
<li><strong>500:</strong> Internal Server Error</li>
<li><strong>503:</strong> Service Unavailable - System unhealthy</li>
</ul>
    """,
    version=app_version,
    contact={
        "name": "Fabricio Entringer",
        "email": "fabricio.entringer@example.com",
        "url": "https://github.com/fabricio-entringer",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    terms_of_service="https://github.com/fabricio-entringer/6mlet-tech-challenge-01/blob/main/LICENSE",
    openapi_tags=[
        {
            "name": "Health",
            "description": "System health monitoring and status endpoints",
            "externalDocs": {
                "description": "Health Check Best Practices",
                "url": "https://microservices.io/patterns/observability/health-check-api.html"
            }
        },
        {
            "name": "Books",
            "description": "Book catalog operations: search, filter, and retrieve book information",
            "externalDocs": {
                "description": "Books API Documentation",
                "url": "https://github.com/fabricio-entringer/6mlet-tech-challenge-01#books-api"
            }
        },
        {
            "name": "Categories", 
            "description": "Book category management and analytics",
        },
        {
            "name": "Statistics",
            "description": "Data insights, analytics, and overview statistics",
        },
        {
            "name": "Scraping",
            "description": "Data collection and web scraping management",
            "externalDocs": {
                "description": "Web Scraping Ethics",
                "url": "https://blog.apify.com/web-scraping-ethics/"
            }
        },
        {
            "name": "Machine Learning",
            "description": "ML pipeline endpoints for feature engineering and price prediction",
            "externalDocs": {
                "description": "ML Pipeline Documentation", 
                "url": "https://github.com/fabricio-entringer/6mlet-tech-challenge-01/blob/main/app/ml/README.md"
            }
        },
        {
            "name": "Core",
            "description": "Core application endpoints and utilities",
        }
    ],
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.books.example.com",
            "description": "Production server"
        }
    ]
)


# Core endpoints
@app.get(
    "/",
    tags=["Core"],
    summary="API Welcome Message",
    description="Returns a welcome message with basic API information and available endpoints."
)
async def root():
    """
    Root endpoint that returns a welcome message.
    
    This endpoint provides basic information about the API and serves as a health check
    for the application's availability.
    """
    return await core.root()


@app.get(
    "/api/v1/health", 
    response_model=HealthResponse,
    tags=["Health"],
    summary="Comprehensive Health Check",
    description="""
Comprehensive health check endpoint that monitors all critical system components.

<strong>Components Monitored:</strong>
<ul>
<li>API service availability</li>
<li>Data file integrity and statistics</li>
<li>Memory usage and system resources</li>
<li>Application uptime and version info</li>
</ul>

<strong>Response Codes:</strong>
<ul>
<li>200: System healthy or degraded</li>
<li>503: System unhealthy (critical failures)</li>
</ul>
    """,
    responses={
        200: {
            "description": "System is healthy or degraded", 
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "timestamp": "2025-08-10T10:00:00Z",
                        "uptime": "2h 30m 15s",
                        "components": {
                            "api": {"status": "healthy", "details": "API service operational"},
                            "data_files": {"status": "healthy", "details": "Data file operational with 1000 books"},
                            "memory": {"status": "healthy", "details": "Memory usage normal: 45.2%"}
                        },
                        "data": {
                            "total_books": 1000,
                            "total_categories": 50,
                            "last_updated": "2025-08-10T08:00:00Z",
                            "file_size_mb": 2.5
                        },
                        "system": {
                            "memory_usage_mb": 128.5,
                            "memory_percent": 45.2
                        }
                    }
                }
            }
        },
        503: {
            "description": "System is unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "version": "1.0.0",
                        "components": {
                            "data_files": {"status": "unhealthy", "details": "Data file not found"}
                        }
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns detailed health information including:
    • Overall system status
    • Component health (API, data files, memory)
    • Data statistics (book count, categories)
    • System resource monitoring
    • API version and uptime information
    
    Returns 200 for healthy/degraded status, 503 for unhealthy status.
    """
    from fastapi import Response
    health_response = await core.health_check()
    
    # Return appropriate HTTP status based on health
    if health_response.status == "unhealthy":
        # Set status code to 503 but return the response directly
        return Response(
            content=health_response.model_dump_json(),
            status_code=503,
            media_type="application/json"
        )
    
    return health_response


@app.get(
    "/version",
    tags=["Core"], 
    summary="Application Version",
    description="Returns the current application version and build information."
)
async def get_version():
    """Version endpoint that returns the current application version."""
    return await core.get_version_endpoint()


# Scraping endpoints
@app.post(
    "/scraping/start", 
    response_model=ScrapingResponse,
    tags=["Scraping"],
    summary="Start Book Scraping Operation",
    description="""
Initiates a book scraping operation to collect data from books.toscrape.com.

<strong>Features:</strong>
<ul>
<li>Asynchronous background processing</li>
<li>Configurable scraping parameters</li>
<li>Progress tracking and status monitoring</li>
<li>Automatic data validation and storage</li>
</ul>

<strong>Process:</strong>
<ol>
<li>Validates scraping request parameters</li>
<li>Starts background scraping task</li>
<li>Returns operation ID for tracking</li>
<li>Updates data files upon completion</li>
</ol>
    """,
    responses={
        200: {
            "description": "Scraping operation started successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "started",
                        "operation_id": "scraping-2025-08-10-001",
                        "message": "Book scraping operation initiated"
                    }
                }
            }
        },
        400: {"description": "Invalid scraping parameters"},
        409: {"description": "Another scraping operation is already running"}
    }
)
async def start_scraping(
    request: ScrapingRequest, background_tasks: BackgroundTasks
) -> ScrapingResponse:
    """Start a book scraping operation."""
    return await scraping.start_scraping(request, background_tasks)


@app.get(
    "/scraping/history", 
    response_model=HistoryResponse,
    tags=["Scraping"],
    summary="Get Scraping Operation History",
    description="""
Retrieves the execution history of book scraping operations.

<strong>Information Provided:</strong>
<ul>
<li>Operation timestamps and duration</li>
<li>Success/failure status</li>
<li>Number of books scraped</li>
<li>Error messages (if any)</li>
<li>Performance metrics</li>
</ul>

<strong>Filtering:</strong>
<ul>
<li>Set 'include_all=true' to see all operations</li>
<li>Default shows only recent operations</li>
</ul>
    """,
    responses={
        200: {
            "description": "Scraping history retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "history": [
                            {
                                "operation_id": "scraping-2025-08-10-001",
                                "start_time": "2025-08-10T10:00:00Z",
                                "end_time": "2025-08-10T10:05:30Z",
                                "status": "completed",
                                "books_scraped": 1000,
                                "duration_seconds": 330
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def get_scraping_history(include_all: bool = False) -> HistoryResponse:
    """Get the execution history of scraping operations."""
    return await scraping.get_scraping_history(include_all)


@app.get(
    "/scraping/status", 
    response_model=StatusResponse,
    tags=["Scraping"],
    summary="Get Current Scraping Status",
    description="""
Returns the current status of any running scraping operations.

<strong>Status Information:</strong>
<ul>
<li>Operation state (idle, running, completed, failed)</li>
<li>Progress percentage (if running)</li>
<li>Estimated completion time</li>
<li>Current operation details</li>
<li>Last operation summary</li>
</ul>
    """,
    responses={
        200: {
            "description": "Scraping status retrieved successfully", 
            "content": {
                "application/json": {
                    "example": {
                        "status": "running",
                        "progress": 65,
                        "books_processed": 650,
                        "estimated_completion": "2025-08-10T10:05:00Z"
                    }
                }
            }
        }
    }
)
async def get_scraping_status() -> StatusResponse:
    """Get the current status of scraping operations."""
    return await scraping.get_scraping_status()


# Categories endpoints
@app.get(
    "/api/v1/categories", 
    response_model=CategoriesResponse,
    tags=["Categories"],
    summary="List All Book Categories",
    description="""
Retrieves all available book categories with optional statistics and sorting.

<strong>Features:</strong>
<ul>
<li>Flexible sorting (by name or book count)</li>
<li>Ascending/descending order</li>
<li>Optional price and rating statistics per category</li>
<li>Book count per category</li>
</ul>

<strong>Sorting Options:</strong>
<ul>
<li><code>name</code>: Alphabetical by category name</li>
<li><code>count</code>: By number of books in category</li>
</ul>

<strong>Statistics Include:</strong>
<ul>
<li>Average price per category</li>
<li>Average rating per category</li>
<li>Price ranges (min/max)</li>
<li>Book counts</li>
</ul>
    """,
    responses={
        200: {
            "description": "Categories retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "categories": [
                            {
                                "name": "Fiction",
                                "count": 250,
                                "avg_price": 25.99,
                                "avg_rating": 4.2,
                                "price_range": {"min": 9.99, "max": 59.99}
                            }
                        ],
                        "total_categories": 50,
                        "include_stats": True
                    }
                }
            }
        },
        400: {"description": "Invalid sorting parameters"}
    }
)
async def get_categories(
    sort: str = Query("name", description="Sort by 'name' or 'count'"),
    order: str = Query("asc", description="Sort order: 'asc' or 'desc'"),
    include_stats: bool = Query(True, description="Include statistics (price, rating)"),
) -> CategoriesResponse:
    """Get all book categories with optional statistics."""
    return await categories.get_categories(sort, order, include_stats)


@app.get(
    "/api/v1/stats/categories", 
    response_model=CategoryStatsResponse,
    tags=["Statistics"],
    summary="Get Detailed Category Statistics",
    description="""
Provides comprehensive statistical analysis for book categories.

<strong>Analytics Provided:</strong>
<ul>
<li>Price distribution and quartiles</li>
<li>Rating distribution across 1-5 stars</li>
<li>Availability statistics (in stock vs out of stock)</li>
<li>Book count trends</li>
<li>Category performance metrics</li>
</ul>

<strong>Filtering:</strong>
<ul>
<li>Filter by specific categories (comma-separated)</li>
<li>Include/exclude rating distribution data</li>
<li>Performance optimized for large datasets</li>
</ul>

<strong>Use Cases:</strong>
<ul>
<li>Business intelligence and reporting</li>
<li>Category performance analysis</li>
<li>Inventory planning</li>
<li>Price optimization insights</li>
</ul>
    """,
    responses={
        200: {
            "description": "Category statistics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "statistics": [
                            {
                                "category": "Fiction",
                                "total_books": 250,
                                "avg_price": 25.99,
                                "price_quartiles": [15.99, 22.50, 25.99, 35.50],
                                "rating_distribution": {
                                    "5": 45,
                                    "4": 89,
                                    "3": 76,
                                    "2": 25,
                                    "1": 15
                                }
                            }
                        ]
                    }
                }
            }
        },
        400: {"description": "Invalid category names provided"}
    }
)
async def get_category_statistics(
    categories: Optional[str] = Query(
        None, 
        description="Comma-separated list of category names to include (e.g., 'Fiction,Mystery')"
    ),
    include_distribution: bool = Query(
        True, 
        description="Include rating distribution in response"
    ),
) -> CategoryStatsResponse:
    """Get detailed statistics for book categories including metrics like average price, rating distribution, and book counts."""
    return await category_stats.get_category_statistics(categories, include_distribution)


@app.get(
    "/api/v1/stats/overview", 
    response_model=OverviewStatsResponse,
    tags=["Statistics"],
    summary="Get Comprehensive Overview Statistics",
    description="""
Provides high-level overview statistics for the entire book catalog.

<strong>Comprehensive Metrics:</strong>
<ul>
<li>Total books and categories count</li>
<li>Overall price statistics (avg, min, max, median)</li>
<li>Rating distribution across all books</li>
<li>Availability overview (stock status)</li>
<li>Data freshness indicators</li>
<li>Collection growth trends</li>
</ul>

<strong>Perfect For:</strong>
<ul>
<li>Dashboard displays</li>
<li>Executive reporting</li>
<li>API health monitoring</li>
<li>Data quality assessment</li>
<li>Business performance overview</li>
</ul>
    """,
    responses={
        200: {
            "description": "Overview statistics retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "total_books": 1000,
                        "total_categories": 50,
                        "price_stats": {
                            "average": 25.99,
                            "min": 9.99,
                            "max": 59.99,
                            "median": 24.50
                        },
                        "rating_distribution": {
                            "5_stars": 180,
                            "4_stars": 320,
                            "3_stars": 280,
                            "2_stars": 140,
                            "1_star": 80
                        },
                        "availability": {
                            "in_stock": 850,
                            "out_of_stock": 150
                        }
                    }
                }
            }
        }
    }
)
async def get_overview_statistics() -> OverviewStatsResponse:
    """Get comprehensive overview statistics for the book catalog including total counts, price metrics, rating distribution, availability stats, category count, and data freshness indicators."""
    return await overview_stats.get_overview_statistics()


# Books endpoints
@app.get(
    "/api/v1/books", 
    response_model=BooksResponse,
    tags=["Books"],
    summary="List Books with Advanced Filtering",
    description="""
Retrieve books with comprehensive filtering, sorting, and pagination capabilities.

<strong>Filtering Options:</strong>
<ul>
<li><strong>Category:</strong> Filter by book category</li>
<li><strong>Price Range:</strong> Set minimum and maximum price bounds</li>
<li><strong>Rating:</strong> Minimum rating filter (1-5 stars)</li>
<li><strong>Availability:</strong> Filter by stock status</li>
</ul>

<strong>Sorting Options:</strong>
<ul>
<li><code>title</code>: Alphabetical by book title</li>
<li><code>price</code>: By price (ascending/descending)</li>
<li><code>rating</code>: By customer rating</li>
<li><code>availability</code>: By stock status</li>
<li><code>category</code>: By category name</li>
</ul>

<strong>Pagination:</strong>
<ul>
<li>Efficient page-based pagination</li>
<li>Configurable page size (1-100 items)</li>
<li>Total count and pages in response</li>
</ul>

<strong>Performance:</strong>
<ul>
<li>Optimized for large catalogs</li>
<li>Indexed database queries</li>
<li>Response caching available</li>
</ul>
    """,
    responses={
        200: {
            "description": "Books retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": 1,
                                "title": "A Light in the Attic",
                                "price": 51.77,
                                "price_display": "£51.77",
                                "rating_text": "Three",
                                "rating_numeric": 3,
                                "availability": "In stock",
                                "category": "Poetry",
                                "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
                                "description": "A collection of poetry and drawings."
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "limit": 20,
                            "total": 1000,
                            "pages": 50
                        },
                        "filters_applied": {
                            "category": "Poetry",
                            "min_rating": 3
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid query parameters"},
        422: {"description": "Validation error in request parameters"}
    }
)
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


@app.get(
    "/api/v1/books/top-rated", 
    response_model=TopRatedBooksResponse,
    tags=["Books"],
    summary="Get Top-Rated Books",
    description="""
Retrieve the highest-rated books in the catalog.

<strong>Features:</strong>
<ul>
<li>Sorted by rating (5-star first)</li>
<li>Secondary sort by number of reviews</li>
<li>Configurable result count (1-100 books)</li>
<li>Includes rating metadata</li>
</ul>

<strong>Use Cases:</strong>
<ul>
<li>Featured book recommendations</li>
<li>Homepage highlights</li>
<li>Quality content curation</li>
<li>Customer satisfaction analysis</li>
</ul>

<strong>Response Metadata:</strong>
<ul>
<li>Number of books returned</li>
<li>Rating range in results</li>
<li>Average rating of returned books</li>
</ul>
    """,
    responses={
        200: {
            "description": "Top-rated books retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": 1,
                                "title": "Exceptional Book Title",
                                "rating_numeric": 5,
                                "price": 29.99,
                                "category": "Fiction"
                            }
                        ],
                        "metadata": {
                            "limit": 10,
                            "returned": 10,
                            "highest_rating": 5,
                            "lowest_rating": 4
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid limit parameter"}
    }
)
async def get_top_rated_books(
    limit: int = Query(10, ge=1, le=100, description="Number of books to return (1-100)")
) -> TopRatedBooksResponse:
    """Get the top-rated books."""
    return await books.get_top_rated_books(limit)


@app.get(
    "/api/v1/books/price-range", 
    response_model=PriceRangeBooksResponse,
    tags=["Books"],
    summary="Get Books by Price Range",
    description="""
Retrieve books within a specific price range with detailed statistics.

<strong>Features:</strong>
<ul>
<li>Inclusive price range filtering</li>
<li>Price distribution analysis</li>
<li>Pagination support</li>
<li>Sorting within price range</li>
<li>Statistical insights</li>
</ul>

<strong>Price Range Analysis:</strong>
<ul>
<li>Average price in range</li>
<li>Price distribution histogram</li>
<li>Number of books in range</li>
<li>Price quartiles</li>
</ul>

<strong>Perfect For:</strong>
<ul>
<li>Budget-conscious browsing</li>
<li>Price comparison analysis</li>
<li>Market research</li>
<li>Promotional planning</li>
</ul>
    """,
    responses={
        200: {
            "description": "Books in price range retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "price_range": {"min": 20.0, "max": 40.0},
                        "data": [],
                        "metadata": {
                            "count": 150,
                            "avg_price": 29.99,
                            "price_distribution": {
                                "20-25": 40,
                                "25-30": 60,
                                "30-35": 35,
                                "35-40": 15
                            }
                        },
                        "pagination": {
                            "page": 1,
                            "limit": 20,
                            "total": 150,
                            "pages": 8
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid price range parameters"},
        422: {"description": "Min price cannot be greater than max price"}
    }
)
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


@app.get(
    "/api/v1/books/{book_id}",
    tags=["Books"],
    summary="Get Book Details by ID",
    description="""
Retrieve complete details for a specific book using its unique identifier.

<strong>Returned Information:</strong>
<ul>
<li>Complete book metadata</li>
<li>Pricing information</li>
<li>Customer ratings and reviews</li>
<li>Availability status</li>
<li>Category classification</li>
<li>High-resolution images</li>
<li>Product codes (UPC)</li>
<li>Detailed descriptions</li>
</ul>

<strong>Error Handling:</strong>
<ul>
<li>Returns 404 if book not found</li>
<li>Validates book ID format</li>
<li>Provides helpful error messages</li>
</ul>
    """,
    responses={
        200: {
            "description": "Book details retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "A Light in the Attic",
                        "price": 51.77,
                        "price_display": "£51.77",
                        "rating_text": "Three",
                        "rating_numeric": 3,
                        "availability": "In stock",
                        "category": "Poetry",
                        "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
                        "description": "A collection of poetry and drawings.",
                        "upc": "a897fe39b1053632",
                        "reviews": "Great collection of poems!"
                    }
                }
            }
        },
        404: {
            "description": "Book not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Book with ID 999 not found"}
                }
            }
        },
        422: {"description": "Invalid book ID format"}
    }
)
async def get_book_by_id(book_id: int):
    """Get complete details for a specific book by ID."""
    return await books.get_book_by_id(book_id)


@app.post(
    "/api/v1/books/refresh",
    tags=["Books"],
    summary="Refresh Book Data Cache", 
    description="""
Refresh the book data cache from the CSV file without API downtime.

<strong>Operation Details:</strong>
<ul>
<li>Hot reload of book data</li>
<li>Zero-downtime refresh</li>
<li>Validates data integrity</li>
<li>Updates internal caches</li>
<li>Preserves API availability</li>
</ul>

<strong>When to Use:</strong>
<ul>
<li>After scraping operations complete</li>
<li>When data files are updated manually</li>
<li>For cache invalidation</li>
<li>During data synchronization</li>
</ul>

<strong>Safety Features:</strong>
<ul>
<li>Rollback on data validation errors</li>
<li>Atomic cache updates</li>
<li>Error logging and reporting</li>
</ul>
    """,
    responses={
        200: {
            "description": "Book data refreshed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Book data cache refreshed",
                        "books_loaded": 1000,
                        "categories_loaded": 50,
                        "refresh_timestamp": "2025-08-10T10:00:00Z"
                    }
                }
            }
        },
        500: {
            "description": "Error refreshing data",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to refresh book data: File not found"}
                }
            }
        }
    }
)
async def refresh_books_data():
    """Refresh book data cache from CSV file without API downtime."""
    return await books.refresh_books_data()

# ML Endpoints
@app.get(
    "/api/v1/ml/features", 
    response_model=MLFeaturesResponse,
    tags=["Machine Learning"],
    summary="Get ML Feature Vectors",
    description="""
Retrieve preprocessed feature vectors ready for machine learning models.

<strong>Feature Engineering Pipeline:</strong>
<ul>
<li>Numerical feature normalization (price, rating)</li>
<li>Categorical encoding (category, availability)</li>
<li>Text feature extraction (title processing)</li>
<li>Missing value imputation</li>
<li>Feature scaling and standardization</li>
</ul>

<strong>Supported Formats:</strong>
<ul>
<li>Vector format (default): Normalized feature arrays</li>
<li>Metadata included for feature interpretation</li>
</ul>

<strong>Sampling Options:</strong>
<ul>
<li>Full dataset or random sampling</li>
<li>Shuffling for training data preparation</li>
<li>Configurable sample sizes</li>
</ul>

<strong>Use Cases:</strong>
<ul>
<li>ML model training preparation</li>
<li>Feature analysis and selection</li>
<li>Data science exploration</li>
<li>Price prediction modeling</li>
</ul>
    """,
    responses={
        200: {
            "description": "ML features retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "features": [
                            {
                                "book_id": "1",
                                "feature_vector": {
                                    "price_normalized": 0.75,
                                    "rating_normalized": 0.6,
                                    "category_fiction": 1.0,
                                    "availability_in_stock": 1.0
                                },
                                "original_price": 25.99,
                                "price_normalized": 0.75
                            }
                        ],
                        "metadata": {
                            "total_samples": 1000,
                            "feature_names": ["price_normalized", "rating_normalized"],
                            "feature_count": 10,
                            "normalization": {
                                "price": {"min": 9.99, "max": 59.99}
                            }
                        }
                    }
                }
            }
        },
        404: {
            "description": "Book data not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Book data not found. Please run the scraper first to collect data."}
                }
            }
        },
        500: {"description": "Error generating features"}
    }
)
async def get_ml_features(
    format: str = "vector",
    include_metadata: bool = True,
    sample_size: Optional[int] = None,
    shuffle: bool = False
) -> MLFeaturesResponse:
    """
    Get feature vectors for ML models.
    
    This endpoint returns preprocessed features ready for machine learning models,
    specifically designed for book price prediction tasks.
    
    Args:
        format: Output format (currently only "vector" supported)
        include_metadata: Whether to include metadata about features
        sample_size: Number of samples to return (None for all)
        shuffle: Whether to shuffle the data
    
    Returns:
        MLFeaturesResponse with feature vectors and metadata
    """
    try:
        engineer = FeatureEngineer()
        features, metadata = engineer.get_features(sample_size=sample_size, shuffle=shuffle)
        
        return MLFeaturesResponse(
            features=features,
            metadata=metadata
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Book data not found. Please run the scraper first to collect data."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating features: {str(e)}"
        )


@app.get(
    "/api/v1/ml/training-data", 
    response_model=TrainingDataResponse,
    tags=["Machine Learning"],
    summary="Get ML Training Data",
    description="""
Retrieve data ready for machine learning model training with train/test splits.

<strong>Data Preparation Pipeline:</strong>
<ul>
<li>Feature extraction and engineering</li>
<li>Target variable preparation (price prediction)</li>
<li>Train/test splitting with stratification</li>
<li>Data validation and cleaning</li>
<li>Scikit-learn compatible format</li>
</ul>

<strong>Split Configuration:</strong>
<ul>
<li>Configurable test size (0.0-1.0)</li>
<li>Random state for reproducibility</li>
<li>Stratified sampling when applicable</li>
<li>Balanced class distribution</li>
</ul>

<strong>Output Format:</strong>
<ul>
<li>X_train, y_train: Training features and targets</li>
<li>X_test, y_test: Testing features and targets</li>
<li>Feature names in proper order</li>
<li>Split metadata and statistics</li>
</ul>

<strong>ML Framework Compatibility:</strong>
<ul>
<li>Scikit-learn ready</li>
<li>NumPy array format</li>
<li>Pandas DataFrame compatible</li>
<li>TensorFlow/PyTorch adaptable</li>
</ul>
    """,
    responses={
        200: {
            "description": "Training data prepared successfully",
            "content": {
                "application/json": {
                    "example": {
                        "X_train": [[0.75, 0.6, 1.0, 1.0], [0.45, 0.8, 0.0, 1.0]],
                        "y_train": [25.99, 18.50],
                        "X_test": [[0.65, 0.4, 1.0, 0.0]],
                        "y_test": [22.99],
                        "feature_names": ["price_norm", "rating_norm", "cat_fiction", "in_stock"],
                        "split_info": {
                            "train_size": 800,
                            "test_size": 200,
                            "test_ratio": 0.2
                        }
                    }
                }
            }
        },
        404: {"description": "Book data not found"},
        500: {"description": "Error generating training data"}
    }
)
async def get_training_data(
    test_size: float = 0.2,
    random_state: int = 42
) -> TrainingDataResponse:
    """
    Get training data ready for ML model training.
    
    This endpoint returns data in a format ready for scikit-learn or similar
    ML libraries, with train/test split already performed.
    
    Args:
        test_size: Proportion of data to use for testing (0.0-1.0)
        random_state: Random seed for reproducible splits
    
    Returns:
        TrainingDataResponse with X_train, y_train, X_test, y_test
    """
    try:
        # Create processor instance (this loads the CSV data automatically)
        processor = TrainingDataProcessor()
        # Process data: extract features, split into train/test, return sklearn-ready format
        return processor.get_training_data(test_size=test_size, random_state=random_state)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Book data not found. Please run the scraper first to collect data."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating training data: {str(e)}"
        )


@app.post(
    "/api/v1/ml/predictions", 
    response_model=PredictionResponse,
    tags=["Machine Learning"],
    summary="Make Price Predictions",
    description="""
Predict book prices based on book characteristics using ML models.

<strong>Prediction Features:</strong>
<ul>
<li>Title analysis and processing</li>
<li>Category-based pricing models</li>
<li>Rating influence on pricing</li>
<li>Availability impact assessment</li>
<li>Market trend considerations</li>
</ul>

<strong>Model Information:</strong>
<ul>
<li>Trained on historical book data</li>
<li>Continuous model updates</li>
<li>Cross-validated accuracy</li>
<li>Feature importance analysis</li>
<li>Confidence interval estimation</li>
</ul>

<strong>Input Requirements:</strong>
<ul>
<li>Book title (string)</li>
<li>Category (must match existing categories)</li>
<li>Rating (1-5 integer scale)</li>
<li>Availability status</li>
</ul>

<strong>Response Details:</strong>
<ul>
<li>Predicted price in original currency</li>
<li>Confidence intervals (when available)</li>
<li>Feature vector used for prediction</li>
<li>Model version for traceability</li>
</ul>

<strong>Note:</strong> This is currently a demonstration endpoint showing the API structure
for ML integration. In production, this would load trained models for real predictions.
    """,
    responses={
        200: {
            "description": "Price prediction completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "predicted_price": 24.99,
                        "confidence_interval": {
                            "lower": 22.50,
                            "upper": 27.48
                        },
                        "feature_vector": {
                            "title_length_norm": 0.6,
                            "category_fiction": 1.0,
                            "rating_norm": 0.8,
                            "availability_in_stock": 1.0
                        },
                        "model_version": "v1.0.0-demo"
                    }
                }
            }
        },
        400: {"description": "Invalid prediction request parameters"},
        422: {"description": "Validation error in request data"},
        500: {"description": "Error making prediction"}
    }
)
async def make_prediction(request: PredictionRequest) -> PredictionResponse:
    """
    Make price predictions for a book based on its features.
    
    Note: This is a mock endpoint that demonstrates the API structure.
    In a real implementation, this would load a trained model and make actual predictions.
    
    Args:
        request: Book features for prediction
    
    Returns:
        PredictionResponse with predicted price and feature vector
    """
    try:
        service = PredictionService()
        return service.predict(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error making prediction: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
