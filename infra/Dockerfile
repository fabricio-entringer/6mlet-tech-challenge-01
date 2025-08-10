# Multi-stage Docker build for 6MLET Tech Challenge 01
# Python 3.12 slim base image for optimal size and security

# Base stage with common dependencies
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-asyncio httpx commitizen

# Copy application code
COPY . .

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application with hot reloading
CMD ["python", "run.py"]

# Production stage
FROM base as production

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application code
COPY . .

# Create directories for data and logs with proper ownership
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application in production mode
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
