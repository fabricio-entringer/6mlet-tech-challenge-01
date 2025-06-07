from fastapi import FastAPI
from typing import Dict
import tomllib
import os

# Get version from pyproject.toml
def get_version() -> str:
    """Get version from pyproject.toml file."""
    try:
        # Get the project root directory (parent of app directory)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        pyproject_path = os.path.join(project_root, "pyproject.toml")
        
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            return pyproject_data.get("project", {}).get("version", "0.1.0")
    except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError):
        # Fallback version if file is not found or version is not in file
        return "0.1.0"

version = get_version()

app = FastAPI(
    title="6MLET Tech Challenge 01 API",
    description="A FastAPI application for the FIAP 6MLET tech challenge 01",
    version=version
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
    return {"version": version}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)