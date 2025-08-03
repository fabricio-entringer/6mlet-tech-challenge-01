"""Core API endpoints."""

from typing import Dict

from ..utils import get_version

app_version = get_version()


async def root() -> Dict[str, str]:
    """
    Root endpoint that returns a welcome message.

    Returns:
        Dict[str, str]: A dictionary containing a welcome message
    """
    return {"message": "Welcome to 6MLET Tech Challenge 01 API"}


async def health_check():
    """
    Enhanced health check endpoint - delegates to health service.
    
    Returns comprehensive health information including system status,
    data availability, and component health.
    """
    # Create a new instance for each request to allow proper testing/mocking
    from .health import HealthService
    service = HealthService()
    return await service.get_comprehensive_health()


async def get_version_endpoint() -> Dict[str, str]:
    """
    Version endpoint that returns the current application version.

    Returns:
        Dict[str, str]: A dictionary containing the current version
    """
    return {"version": app_version}
