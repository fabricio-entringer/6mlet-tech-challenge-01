from fastapi import FastAPI
from typing import Dict
from .utils import get_version

app_version = get_version()

app = FastAPI(
    title="6MLET Tech Challenge 01 API",
    description="A FastAPI application for the FIAP 6MLET tech challenge 01",
    version=app_version
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)