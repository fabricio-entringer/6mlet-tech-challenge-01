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


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns detailed health information including:
    - Overall system status
    - Component health (API, data files, memory)
    - Data statistics (book count, categories)
    - System resource monitoring
    - API version and uptime information
    
    Returns 200 for healthy/degraded status, 503 for unhealthy status.
    """
    health_response = await core.health_check()
    
    # Return appropriate HTTP status based on health
    if health_response.status == "unhealthy":
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=health_response.model_dump(mode='json'))
    
    return health_response


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


@app.get("/api/v1/stats/categories", response_model=CategoryStatsResponse)
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


@app.get("/api/v1/stats/overview", response_model=OverviewStatsResponse)
async def get_overview_statistics() -> OverviewStatsResponse:
    """Get comprehensive overview statistics for the book catalog including total counts, price metrics, rating distribution, availability stats, category count, and data freshness indicators."""
    return await overview_stats.get_overview_statistics()


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

# ML Endpoints
@app.get("/api/v1/ml/features", response_model=MLFeaturesResponse)
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


@app.get("/api/v1/ml/training-data", response_model=TrainingDataResponse)
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


@app.post("/api/v1/ml/predictions", response_model=PredictionResponse)
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
