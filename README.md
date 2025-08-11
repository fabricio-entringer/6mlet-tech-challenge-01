# 6MLET Tech Challenge #1

[![CI](https://github.com/fabricio-entringer/6mlet-tech-challenge-01/workflows/CI/badge.svg)](https://github.com/fabricio-entringer/6mlet-tech-challenge-01/actions)
[![Build and Test PR](https://github.com/fabricio-entringer/6mlet-tech-challenge-01/workflows/Build%20and%20Test%20PR/badge.svg)](https://github.com/fabricio-entringer/6mlet-tech-challenge-01/actions)

<div align="center">
  <img src="assets/app-image.png" alt="6MLET Tech Challenge 01 Application" width="400">
</div>

<br/>
Tech Challenge #1 - FIAP Machine Learning Engineering Postgraduate specialization course

## Overview

This project is a FastAPI application created for the 6MLET Tech Challenge - Delivery 01. It includes a simple REST API, comprehensive testing with pytest, version control using commitizen, and integrated machine learning capabilities.

> **📚 Consolidated Documentation**: This README now includes all documentation previously distributed across multiple README files in the project, providing a complete reference in one location.

This delivery is from **Group #3**, with the following team members:
- **Fabricio Entringer** 
- **Adriano Ribeiro** - [GitHub Profile](https://github.com/adrianoribeiro)

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
  - [Core Endpoints](#core-endpoints)
  - [API Documentation](#api-documentation)
  - [ML-Ready Endpoints](#ml-ready-endpoints)
- [Books Scraper System](#books-scraper-system)
  - [Scraper Features](#scraper-features)
  - [REST API Endpoints for Scraping](#rest-api-endpoints-for-scraping)
  - [Scraper API (Recommended)](#scraper-api-recommended)
  - [Basic Scraper Usage](#basic-scraper-usage)
  - [Scraper Configuration](#scraper-configuration)
  - [Data Schema](#data-schema)
  - [Error Handling](#error-handling)
  - [Troubleshooting](#troubleshooting)
- [Machine Learning Endpoints Documentation](#machine-learning-endpoints-documentation)
  - [ML Endpoints Overview](#ml-endpoints-overview)
  - [Feature Engineering](#feature-engineering)
  - [Training the Model](#training-the-model)
  - [ML Usage Examples](#ml-usage-examples)
  - [Integration with Data Science Workflows](#integration-with-data-science-workflows)
- [Testing](#testing)
- [HTTP API Testing](#http-api-testing)
- [CI/CD Workflows](#cicd-workflows)
- [Version Control with Commitizen](#version-control-with-commitizen)
- [Development Commands](#development-commands)
- [Contributing](#contributing)
- [Requirements](#requirements)
- [Architecture Plan](#architecture-plan)

## Features

- **FastAPI** web framework for building APIs
- **Uvicorn** ASGI server for running the application
- **pytest** for testing with async support
- **Commitizen** for conventional commits and version management
- **Web Scraping System** for automated book data collection from books.toscrape.com
  - CLI and programmatic interfaces
  - Comprehensive data extraction with pagination support
  - Robust error handling and retry mechanisms
  - Rate limiting and respectful crawling
  - CSV export functionality
  - Detailed logging and statistics

## Project Structure

```text
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── scripts/             # Web scraping and utility scripts
│   ├── __init__.py
│   ├── books_scraper.py # Main scraper implementation
│   ├── scraper_api.py   # API interface for CLI and programmatic use
│   ├── run_scraper.py   # CLI interface for scraper
│   ├── config.py        # Scraper configuration
│   └── README.md        # Scraper documentation
├── tests/
│   ├── __init__.py
│   ├── test_main.py     # API test cases
│   ├── test_books_scraper.py # Scraper test cases
│   └── test_scraper_api.py   # Scraper API test cases
├── data/                # Output directory for scraped data (gitignored)
├── logs/                # Log files directory (gitignored)
├── assets/              # Project assets
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project configuration
├── demo_api_usage.py    # API usage demonstration script
```

## Web Scraping System

The project includes a comprehensive web scraping system for extracting book data from [books.toscrape.com](https://books.toscrape.com/). The system provides both command-line and programmatic interfaces.

### Quick Start

```bash
# Scrape all books (recommended API interface)
python scripts/scraper_api.py

# Get available categories
python scripts/scraper_api.py --mode categories

# Scrape a specific category
python scripts/scraper_api.py --mode category --category "Fiction"

# Scrape a sample of books
python scripts/scraper_api.py --mode sample --max-books 50

# Demonstrate programmatic usage
python demo_api_usage.py
```

### Key Scraper Features

- **Complete Data Extraction**: Scrapes all books with pagination support
- **Multiple Interfaces**: CLI and programmatic API access
- **Comprehensive Data**: Title, price, rating, availability, category, image URL
- **Robust Error Handling**: Retry mechanisms and graceful error recovery
- **Rate Limiting**: Respectful crawling with configurable delays
- **Data Export**: CSV format with organized output
- **Detailed Logging**: Comprehensive logging and statistics
- **Flexible Usage**: Sample scraping, category-specific scraping, full scraping

For detailed documentation, see [`scripts/README.md`](scripts/README.md).

## Installation

1. Create and activate a virtual environment:

   ```bash
   make venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   make install
   ```

Alternatively, you can do it manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Application

1. Start the FastAPI server:

   ```bash
   python run.py
   ```

   Or using make:

   ```bash
   make run
   ```

2. The API will be available at: `http://localhost:8000`
3. Interactive API documentation: `http://localhost:8000/docs`
4. Alternative API documentation: `http://localhost:8000/redoc`

## API Endpoints

**🌐 Production URL**: <https://6mlet-tech-challenge-01.up.railway.app>

### Core Endpoints

- **`GET /`** - Root endpoint
  - **Description**: Returns a welcome message for the API
  - **Response**: `{"message": "Welcome to 6MLET Tech Challenge 01 API"}`
  - **Status Code**: 200
  - **Production**: <https://6mlet-tech-challenge-01.up.railway.app/>

- **`GET /health`** - Health check endpoint
  - **Description**: Returns the current health status of the service
  - **Response**: `{"status": "healthy"}`
  - **Status Code**: 200
  - **Production**: <https://6mlet-tech-challenge-01.up.railway.app/health>

- **`GET /version`** - Version endpoint
  - **Description**: Returns the current application version from pyproject.toml
  - **Response**: `{"version": "x.x.x"}`
  - **Status Code**: 200
  - **Production**: <https://6mlet-tech-challenge-01.up.railway.app/version>

### API Documentation

The FastAPI application automatically generates comprehensive API documentation using OpenAPI (Swagger) specifications:

- **Interactive Documentation (Swagger UI)**: `http://localhost:8000/docs`
  - Try out endpoints directly from the browser
  - View request/response schemas
  - Test API calls with real-time responses
  - **Production**: <https://6mlet-tech-challenge-01.up.railway.app/docs>

- **Alternative Documentation (ReDoc)**: `http://localhost:8000/redoc`
  - Clean, responsive documentation interface
  - Detailed endpoint descriptions and examples
  - Schema definitions and models
  - **Production**: <https://6mlet-tech-challenge-01.up.railway.app/redoc>

- **OpenAPI JSON Schema**: `http://localhost:8000/openapi.json`
  - Raw OpenAPI specification in JSON format
  - Can be imported into other API tools (Postman, Insomnia, etc.)
  - **Production**: <https://6mlet-tech-challenge-01.up.railway.app/openapi.json>

### ML-Ready Endpoints

The API includes machine learning endpoints designed for book price prediction:

- **`GET /api/v1/ml/features`** - Feature vectors for ML models
  - **Description**: Returns preprocessed features ready for machine learning
  - **Query Parameters**: 
    - `sample_size`: Number of samples to return
    - `shuffle`: Whether to shuffle the data
    - `include_metadata`: Include feature engineering metadata
  - **Response**: Feature vectors with normalization and one-hot encoding applied

- **`GET /api/v1/ml/training-data`** - Training data with train/test split
  - **Description**: Returns data ready for model training with sklearn
  - **Query Parameters**:
    - `test_size`: Proportion for test set (default: 0.2)
    - `random_state`: Random seed for reproducibility
  - **Response**: X_train, y_train, X_test, y_test arrays

- **`POST /api/v1/ml/predictions`** - Price prediction endpoint
  - **Description**: Predicts book price based on features
  - **Request Body**:
    ```json
    {
      "title": "Book Title",
      "category": "Fiction",
      "rating": 4,
      "availability": "In stock"
    }
    ```
  - **Response**: Predicted price with confidence interval

## Testing

Run tests using pytest:

```bash
pytest
```

Or using make:

```bash
make test
```

## HTTP API Testing

The project includes comprehensive HTTP request files for testing all API endpoints using VS Code's REST Client extension.

### Quick Start

1. **Install REST Client**: Install the [REST Client extension](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) for VS Code
2. **Navigate to tests**: Open any `.http` file in `tests/http-request/`
3. **Select environment**: Choose "local" or "prod" from VS Code's status bar
4. **Send requests**: Click "Send Request" above any HTTP request block

### Available Test Files

- **`core.http`** - Health checks, version, and basic endpoints
- **`books.http`** - Book management, search, and filtering
- **`categories.http`** - Category listing and statistics
- **`statistics.http`** - Analytics and reporting endpoints
- **`scraping.http`** - Web scraping operations
- **`machine-learning.http`** - ML features and predictions
- **`test-suite.http`** - Comprehensive workflow testing
- **`quick-reference.http`** - Common requests for quick testing

### Environment Configuration

The `http-client.env.json` file provides two environments:
- **`local`**: `http://localhost:8000` (development)
- **`prod`**: `https://sixmlet-tech-challenge-01-latest.onrender.com` (production)

Switch between environments using VS Code's environment selector in the status bar.

### Example Usage

```http
### Get all books with pagination
GET {{baseUrl}}/api/v1/books?page=1&limit=10
Accept: {{contentType}}

### Make a price prediction
POST {{baseUrl}}/api/v1/ml/predictions
Content-Type: {{contentType}}

{
  "title": "Python for Data Science",
  "category": "Technology",
  "rating": 5,
  "availability": "In stock"
}
```

## Books Scraper System

A comprehensive web scraping system to extract book data from [books.toscrape.com](https://books.toscrape.com/).

### Scraper Features

- ✅ **Complete Data Extraction**: Extracts all books from all categories with pagination support
- ✅ **Comprehensive Data Fields**: Captures title, price, rating, availability, category, and image URL
- ✅ **Robust Error Handling**: Implements retry mechanisms and graceful error recovery
- ✅ **Rate Limiting**: Respects website resources with configurable delays
- ✅ **CSV Export**: Stores data in well-structured CSV format
- ✅ **Detailed Logging**: Comprehensive logging for monitoring and debugging
- ✅ **Statistics**: Provides detailed statistics about scraped data
- ✅ **CLI Interface**: Easy-to-use command-line interface

### REST API Endpoints for Scraping

The system includes REST API endpoints for remote scraping operations:

#### Start the API Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Available Endpoints

1. **Start Scraping**: `POST /scraping/start`
   ```bash
   curl -X POST "http://localhost:8000/scraping/start" \
     -H "Content-Type: application/json" \
     -d '{"delay": 1.0, "csv_filename": "api_books.csv"}'
   ```

2. **Get History**: `GET /scraping/history`
   ```bash
   curl "http://localhost:8000/scraping/history"
   ```

3. **Check Status**: `GET /scraping/status`
   ```bash
   curl "http://localhost:8000/scraping/status"
   ```

### Scraper API (Recommended)

The `scraper_api.py` provides both command line and programmatic interfaces:

#### Command Line Interface

```bash
# Navigate to the scripts directory
cd scripts

# Scrape all books (default mode)
python scraper_api.py

# Get available categories
python scraper_api.py --mode categories

# Scrape a specific category
python scraper_api.py --mode category --category "Fiction"

# Scrape a sample of books
python scraper_api.py --mode sample --max-books 100

# Customize scraping parameters
python scraper_api.py --delay 0.5 --max-retries 2 --timeout 15

# Skip saving to CSV
python scraper_api.py --no-save

# Show help
python scraper_api.py --help
```

#### Programmatic Usage

```python
from scraper_api import BooksScraperAPI

# Create API instance
api = BooksScraperAPI(delay=1.0, max_retries=3, timeout=10)

# Scrape all books
result = api.scrape_all_books()
print(f"Scraped {result['total_books']} books")
print(f"Categories: {result['total_categories']}")
print(f"Data saved to: {result['csv_file']}")

# Get available categories
categories = api.get_categories()
for cat in categories:
    print(f"- {cat['name']}: {cat['url']}")

# Scrape a specific category
fiction_result = api.scrape_category("Fiction")
print(f"Fiction books: {fiction_result['total_books']}")

# Scrape a sample
sample_result = api.scrape_sample(max_books=50)
print(f"Sample: {sample_result['total_books']} books")

# Get last scraping statistics
stats = api.get_scraper_stats()
print(f"Statistics: {stats}")
```

### Basic Scraper Usage

Run the scraper with default settings:

```bash
python scripts/run_scraper.py
```

### Advanced Scraper Usage

Customize scraper behavior:

```bash
# Custom delay and output settings
python scripts/run_scraper.py --delay 2.0 --output my_data --filename custom_books.csv

# Enable verbose logging
python scripts/run_scraper.py --verbose

# Custom retry and timeout settings
python scripts/run_scraper.py --max-retries 5 --timeout 15
```

### Direct Scraper Usage

```python
from scripts.books_scraper import BooksScraper

# Initialize scraper
scraper = BooksScraper(delay=1.0)

# Scrape all books
books = scraper.scrape_all_books()

# Save to CSV
output_file = scraper.save_to_csv("my_books.csv", "output")

# Get statistics
stats = scraper.get_statistics()
print(f"Total books: {stats['total_books']}")
```

### Scraper Configuration

The scraper can be configured through various parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `delay` | 1.0 | Delay between requests (seconds) |
| `max_retries` | 3 | Maximum retry attempts for failed requests |
| `timeout` | 10 | Request timeout (seconds) |
| `output_dir` | "data" | Output directory for CSV files |

### Data Schema

The scraper extracts the following fields for each book:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Book title |
| `price` | string | Book price (with currency symbol) |
| `rating_text` | string | Textual rating (One, Two, Three, Four, Five) |
| `rating_numeric` | integer | Numeric rating (1-5) |
| `availability` | string | Availability status |
| `category` | string | Book category |
| `image_url` | string | URL to book cover image |

### Scraper Output

The scraper generates:

1. **CSV File**: `data/books_data.csv` (default) containing all book data
2. **Log File**: `logs/scraper.log` with detailed operation logs
3. **Console Output**: Real-time progress and statistics

#### Sample CSV Output

```csv
title,price,rating_text,rating_numeric,availability,category,image_url
"A Light in the Attic","£51.77","Three","3","In stock","Poetry","https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg"
"Tipping the Velvet","£53.74","One","1","In stock","Historical Fiction","https://books.toscrape.com/media/cache/26/0c/260c6ae16bce31c8f8c95daddd9f4a1c.jpg"
```

### Error Handling

The scraper implements robust error handling:

- **Network Errors**: Automatic retry with exponential backoff
- **Parsing Errors**: Graceful handling with error logging
- **Rate Limiting**: Configurable delays to respect server resources
- **Timeout Protection**: Prevents hanging requests

### Scraper Testing

Run the scraper test suite:

```bash
# Run all tests
python -m pytest tests/test_books_scraper.py -v

# Run with coverage
python -m pytest tests/test_books_scraper.py --cov=scripts.books_scraper

# Run integration tests (requires network access)
python -m pytest tests/test_books_scraper.py -m integration
```

### Logging

The scraper provides detailed logging:

- **INFO**: Progress updates and statistics
- **WARNING**: Recoverable errors and retries
- **ERROR**: Critical errors and failures

Log files are saved as `logs/scraper.log` and also displayed in the console.

### Best Practices

The scraper follows web scraping best practices:

1. **Respectful Crawling**: Implements delays between requests
2. **Error Recovery**: Robust retry mechanisms
3. **Resource Efficiency**: Reuses HTTP sessions
4. **User Agent**: Identifies itself appropriately
5. **Graceful Degradation**: Continues operation despite individual failures

### Performance

Typical performance metrics:

- **Speed**: ~1-2 seconds per page (with 1s delay)
- **Coverage**: 100% of available books
- **Reliability**: >99% success rate with retry logic
- **Memory**: Efficient streaming processing

### Limitations

- **Rate Limiting**: Respects 1-second delay by default
- **Network Dependent**: Requires stable internet connection
- **Site Structure**: Depends on current HTML structure of books.toscrape.com

### Troubleshooting

#### Common Issues

1. **Connection Errors**:
   - Check internet connection
   - Increase timeout settings
   - Verify website accessibility

2. **Incomplete Data**:
   - Check log files for specific errors
   - Verify HTML structure hasn't changed
   - Increase retry attempts

3. **Performance Issues**:
   - Reduce delay for faster scraping (if appropriate)
   - Monitor system resources
   - Check network latency

#### Debug Mode

Enable verbose logging for debugging:

```bash
python scripts/run_scraper.py --verbose
```

## CI/CD Workflows

This project includes comprehensive GitHub Actions workflows for continuous integration and deployment:

### Available Workflows

1. **CI Workflow** (`.github/workflows/ci.yml`)
   - Runs on every push and pull request to `main` and `develop` branches
   - Tests with Python 3.12
   - Runs the full test suite
   - Validates app import functionality

2. **Build and Test PR Workflow** (`.github/workflows/pr-build-test.yml`)
   - Comprehensive PR validation workflow
   - **Multi-version testing**: Tests with Python 3.11 and 3.12
   - **Build validation**: Creates and validates package builds
   - **Security scanning**: Runs `safety` and `bandit` security checks
   - **Code quality**: Validates formatting with `black`, import sorting with `isort`, and type checking with `mypy`
   - **Application testing**: Validates the application starts correctly and endpoints respond
   - **Summary report**: Provides a comprehensive summary of all checks

### Workflow Features

- **Dependency caching**: Speeds up workflow execution
- **Matrix testing**: Tests across multiple Python versions
- **Artifact storage**: Saves build artifacts for inspection
- **Status badges**: Available for README integration
- **PR template**: Standardized pull request template for consistency

### Status Badges

Add these badges to your repository by replacing `YOUR_USERNAME` with your GitHub username:

```markdown
[![CI](https://github.com/YOUR_USERNAME/6mlet-tech-challenge-01/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/6mlet-tech-challenge-01/actions)
[![Build and Test PR](https://github.com/YOUR_USERNAME/6mlet-tech-challenge-01/workflows/Build%20and%20Test%20PR/badge.svg)](https://github.com/YOUR_USERNAME/6mlet-tech-challenge-01/actions)
```

## Version Control with Commitizen

This project uses commitizen for conventional commits:

1. Make your changes
2. Stage your files: `git add .`
3. Create a conventional commit: `make commit` or `cz commit`
4. Bump version: `make bump` or `cz bump`

## Development Commands

This project includes a Makefile that provides convenient shortcuts for common development tasks. The Makefile automates environment setup, testing, running, and maintenance operations.

### Available Make Commands

#### Environment Setup

- **`make help`** - Display all available commands with descriptions
  ```bash
  make help
  ```

- **`make venv`** - Create a Python virtual environment
  ```bash
  make venv
  ```
  Creates a new virtual environment in the `venv/` directory using Python 3. After running this command, activate the environment with `source venv/bin/activate`.

- **`make install`** - Install project dependencies
  ```bash
  make install
  ```
  Automatically creates a virtual environment (if it doesn't exist), upgrades pip to the latest version, and installs all dependencies from `requirements.txt`. This is equivalent to running the installation steps manually but in one command.

#### Development Operations

- **`make test`** - Run the test suite
  ```bash
  make test
  ```
  Executes all tests using pytest within the virtual environment. Tests are located in the `tests/` directory and include unit tests for the FastAPI application.

- **`make run`** - Start the FastAPI development server
  ```bash
  make run
  ```
  Launches the FastAPI application using the `run.py` script. The server will be available at `http://localhost:8000` with automatic API documentation at `http://localhost:8000/docs`.

#### Maintenance

- **`make clean`** - Clean up generated files and cache
  ```bash
  make clean
  ```
  Removes Python cache files, bytecode files (`.pyc`), `__pycache__` directories, `.egg-info` directories, and pytest cache. Use this to clean up your workspace and resolve potential caching issues.

#### Version Control

- **`make commit`** - Create a conventional commit
  ```bash
  make commit
  ```
  Opens the commitizen interactive prompt to create a conventional commit. This ensures your commit messages follow the conventional commit format (feat, fix, docs, etc.).

- **`make bump`** - Bump project version
  ```bash
  make bump
  ```
  Automatically increments the project version based on conventional commits, updates version files, and creates a git tag.

### How the Makefile Works

The Makefile uses the `.PHONY` directive to declare targets that don't create files with the same name. Each command uses the virtual environment's Python interpreter (`venv/bin/python`) and pip (`venv/bin/pip`) to ensure commands run in the isolated environment.

Key features:
- **Dependency Management**: Commands like `install` depend on `venv`, ensuring the virtual environment exists before installing packages
- **Virtual Environment Isolation**: All Python commands use `venv/bin/` executables
- **Cross-Platform Compatibility**: Commands work on Unix-like systems (Linux, macOS)

### Usage Examples

1. **First-time setup**:
   ```bash
   make install  # Creates venv and installs dependencies
   source venv/bin/activate  # Activate the environment
   ```

2. **Daily development workflow**:
   ```bash
   make test     # Run tests before making changes
   make run      # Start the development server
   make clean    # Clean up when needed
   ```

3. **Version control workflow**:

   ```bash
   git add .
   make commit   # Create conventional commit
   make bump     # Bump version when ready for release
   ```

## Contributing

We welcome contributions to this project! Whether you want to report a bug, suggest an improvement, or contribute code, please use our issue templates to get started.

### 🐛 Report Issues

Found a bug or want to suggest an improvement? Please create an issue using our templates:

**[📝 Create New Issue](https://github.com/fabricio-entringer/6mlet-tech-challenge-01/issues/new/choose)**

Available issue types:
- **🐛 Bug Report** - Report bugs or unexpected behavior
- **🚀 Feature Request/Improvement** - Suggest new features or improvements
- **📋 Task** - Create tasks for project work or maintenance

### 📋 Issue Guidelines

When creating an issue, please:
- Use the appropriate template for your issue type
- Provide clear and detailed information
- Search existing issues to avoid duplicates
- Include relevant environment information for bugs
- Follow the project's code of conduct

## Requirements

- Python 3.12+
- FastAPI 0.115.12+
- Uvicorn 0.34.3+
- pytest 8.4.0+
- pytest-asyncio 1.0.0+
- httpx 0.28.1+
- commitizen 4.8.2+

### Web Scraping Dependencies

- requests 2.32.3+
- beautifulsoup4 4.12.3+
- lxml 5.2.2+
- pandas 2.2.2+

## Machine Learning Endpoints Documentation

This section provides detailed documentation for the machine learning endpoints available in the 6MLET Tech Challenge 01 API. These endpoints provide comprehensive functionality for working with book price prediction models.

### ML Endpoints Overview

The API provides three main ML endpoints for working with book price prediction models:

1. **Feature Engineering** - `/api/v1/ml/features`
2. **Training Data** - `/api/v1/ml/training-data`  
3. **Price Predictions** - `/api/v1/ml/predictions`

### 1. GET /api/v1/ml/features

Returns preprocessed feature vectors ready for machine learning models.

**Query Parameters:**
- `format`: Output format (default: "vector")
- `include_metadata`: Include metadata about features (default: true)
- `sample_size`: Number of samples to return (default: all)
- `shuffle`: Shuffle the data (default: false)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/ml/features?sample_size=10&shuffle=true"
```

**Example Response:**
```json
{
  "features": [
    {
      "book_id": "0",
      "feature_vector": {
        "rating": 0.75,
        "category_Science": 1.0,
        "category_Fiction": 0.0,
        "availability_in_stock": 1.0,
        "availability_out_of_stock": 0.0
      },
      "original_price": 45.17,
      "price_normalized": 0.703
    }
  ],
  "metadata": {
    "total_samples": 1000,
    "feature_names": ["rating", "category_Academic", "category_Fiction", "availability_in_stock"],
    "feature_count": 58
  }
}
```

### 2. GET /api/v1/ml/training-data

Returns data in sklearn-ready format with train/test split.

**Query Parameters:**
- `test_size`: Proportion for test set (default: 0.2)
- `random_state`: Random seed for reproducibility (default: 42)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/ml/training-data?test_size=0.3&random_state=123"
```

**Example Response:**
```json
{
  "X_train": [[0.75, 0, 0, 1], [0.5, 1, 0, 0]],
  "y_train": [0.703, 0.788],
  "X_test": [[0.5, 1, 0, 0], [1.0, 0, 1, 0]],
  "y_test": [0.539, 0.777],
  "feature_names": ["rating", "category_Academic", "category_Fiction", "availability_in_stock"],
  "split_info": {
    "train_size": 800,
    "test_size": 200,
    "test_ratio": 0.2
  }
}
```

### 3. POST /api/v1/ml/predictions

Makes price predictions for a book based on its features.

**Request Body:**
```json
{
  "title": "Python for Data Science",
  "category": "Science",
  "rating": 4,
  "availability": "In stock"
}
```

**Field Descriptions:**
- `title`: Book title (string) - used for logging, not for prediction
- `category`: Book category (string) - must be a valid category from the dataset
- `rating`: Book rating (integer, 1-5) - customer rating
- `availability`: Availability status (string) - e.g., "In stock", "Out of stock"

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/ml/predictions" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python for Data Science",
    "category": "Science",
    "rating": 4,
    "availability": "In stock"
  }'
```

**Example Response (with real model):**
```json
{
  "predicted_price": 26.87,
  "confidence_interval": {
    "lower": 22.84,
    "upper": 30.90
  },
  "feature_vector": {
    "rating": 0.75,
    "category_Science": 1.0,
    "category_Fiction": 0.0,
    "availability_in_stock": 1.0
  },
  "model_version": "1.0"
}
```

### Valid Categories

The following categories are available in the dataset:

Academic, Adult Fiction, Art, Autobiography, Biography, Business, Childrens, Christian, Christian Fiction, Classics, Contemporary, Crime, Cultural, Default, Erotica, Fantasy, Fiction, Food and Drink, Health, Historical, Historical Fiction, History, Horror, Humor, Music, Mystery, New Adult, Nonfiction, Novels, Paranormal, Parenting, Philosophy, Poetry, Politics, Psychology, Religion, Romance, Science, Science Fiction, Self Help, Sequential Art, Short Stories, Spirituality, Sports and Games, Suspense, Thriller, Travel, Womens Fiction, Young Adult

### Feature Engineering

The ML module processes raw book data into ML-ready features:

#### 1. Numeric Features:
- `rating`: Normalized rating (0-1)
- `price_normalized`: Target variable normalized (0-1)

#### 2. One-Hot Encoded Features:
- **Categories**: 50+ book categories (e.g., `category_Science`, `category_Fiction`)
- **Ratings**: 5 columns (`rating_One` to `rating_Five`)
- **Availability**: 2 columns (`availability_in_stock`, `availability_out_of_stock`)

#### 3. Data Cleaning:
- Invalid category "Add a comment" is reassigned to "Default"
- Preserves all data instead of removing invalid records

### Training the Model

Before using real predictions, train the model:

```bash
# Train the model (creates model.pkl and model_metadata.pkl)
python app/ml/train_model.py
```

### ML Usage Examples

#### Getting Feature Vectors
```bash
# Get a small sample of features with metadata
curl "http://localhost:8000/api/v1/ml/features?sample_size=10&include_metadata=true"

# Get all features without metadata
curl "http://localhost:8000/api/v1/ml/features?include_metadata=false"
```

#### Getting Training Data
```bash
# Standard train/test split (80/20)
curl "http://localhost:8000/api/v1/ml/training-data"

# Custom split (70/30) with specific random seed
curl "http://localhost:8000/api/v1/ml/training-data?test_size=0.3&random_state=42"
```

#### Making Predictions
```bash
# Science book prediction
curl -X POST "http://localhost:8000/api/v1/ml/predictions" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Machine Learning Fundamentals",
    "category": "Science",
    "rating": 5,
    "availability": "In stock"
  }'

# Fiction book prediction
curl -X POST "http://localhost:8000/api/v1/ml/predictions" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Adventure",
    "category": "Fiction", 
    "rating": 4,
    "availability": "Out of stock"
  }'

# Food & Drink book prediction
curl -X POST "http://localhost:8000/api/v1/ml/predictions" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn to Cook",
    "category": "Food and Drink",
    "rating": 3,
    "availability": "In stock"
  }'
```

### ML Module Structure

```
ml/
├── __init__.py              # Module exports
├── feature_engineering.py   # Feature transformation logic
├── training_data.py         # Training data preparation
├── prediction_service.py    # Prediction logic (mock)
├── models.py               # Pydantic models
├── train_model.py          # Model training script
└── README.md               # This documentation
```

### ML Requirements

- pandas
- numpy
- scikit-learn
- pydantic

### Integration with Data Science Workflows

The ML endpoints are designed to integrate seamlessly with common data science workflows:

```python
import requests
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# 1. Get training data from API
response = requests.get("http://localhost:8000/api/v1/ml/training-data")
data = response.json()

# 2. Train model locally
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(data["X_train"], data["y_train"])

# 3. Evaluate on test set
score = model.score(data["X_test"], data["y_test"])
print(f"Model R² Score: {score:.4f}")

# 4. Test with API predictions
prediction_response = requests.post(
    "http://localhost:8000/api/v1/ml/predictions",
    json={
        "title": "Advanced Python Programming",
        "category": "Science",
        "rating": 5,
        "availability": "In stock"
    }
)
prediction = prediction_response.json()
print(f"Predicted price: ${prediction['predicted_price']:.2f}")
```

### 📊 Pipeline Overview

```
[Website] → [Scraper] → [CSV] → [API] → [Users]
                           ↓
                      [ML Features]
```

**Data Flow**:
1. **Collection**: Python script scrapes books.toscrape.com
2. **Storage**: Data saved in CSV file format
3. **API**: FastAPI reads CSV and serves data via REST endpoints
4. **ML Ready**: Preprocessed features available for data scientists

### 🎯 Data Science Use Case

**Scenario**: A junior data scientist needs to build a book price prediction model.

**Workflow using our API**:

1. **Data Exploration**:
   ```python
   # Check available books
   GET /api/v1/books
   
   # Explore categories  
   GET /api/v1/categories
   
   # Get statistics
   GET /api/v1/stats/overview
   ```

2. **Model Training**:
   ```python
   # Get preprocessed training data
   GET /api/v1/ml/training-data
   
   # Returns X_train, y_train, X_test, y_test
   # Ready for sklearn models
   ```

3. **Model Testing**:
   ```python
   # Test predictions
   POST /api/v1/ml/predictions
   {
     "title": "Python for Data Science",
     "category": "Technology",
     "rating": 5,
     "availability": "In stock"
   }
   ```

### 🔧 ML Integration Plan

#### Current Features:
- ✅ Clean, structured data from 1000+ books
- ✅ Preprocessed features (normalized prices, one-hot encoded categories)
- ✅ Ready-to-use training/test splits
- ✅ Mock prediction endpoint for testing

#### Integration Example:

```python
import requests
from sklearn.ensemble import RandomForestRegressor

# 1. Data scientist fetches training data
response = requests.get("https://api.example.com/api/v1/ml/training-data")
data = response.json()

# 2. Train model locally
model = RandomForestRegressor()
model.fit(data["X_train"], data["y_train"])

# 3. Evaluate on test set
score = model.score(data["X_test"], data["y_test"])

# 4. Test with API predictions
prediction = requests.post("https://api.example.com/api/v1/ml/predictions", 
    json={"title": "New Book", "category": "Fiction", "rating": 4})
```

### 🏗️ System Architecture

```
┌─────────────────┐
│   Railway.app   │  ← Cloud deployment
└────────┬────────┘
         │
┌────────▼────────┐
│    FastAPI      │  ← REST API
├─────────────────┤
│   Endpoints:    │
│   - /books      │
│   - /categories │
│   - /search     │
│   - /ml/*       │
└────────┬────────┘
         │
┌────────▼────────┐
│   books.csv     │  ← Data storage
└─────────────────┘
```

### 💡 Practical Use Cases

**For ML Students and Beginners**:

1. **Price Analysis**: 
   - Which categories have higher prices?
   - Does rating correlate with price?
   - Availability impact on pricing

2. **Simple Prediction Models**:
   - Linear regression for price prediction
   - Decision trees for category classification
   - Feature importance analysis

3. **Data Science Exercises**:
   - Exploratory data analysis using API data
   - Create visualizations (price distributions, rating analysis)
   - Build and compare different ML models
   - Practice feature engineering

### 📈 Future Enhancements

Simple improvements for learning:
- Add more books through periodic scraping
- Implement model persistence
- Add database support (PostgreSQL)
- Create model comparison endpoints
- Add real-time predictions

---

**Summary**: This API serves as an educational tool providing real-world data for students to practice machine learning with a production-ready REST API! 🎓

## Documentation Consolidation

This README.md now serves as the comprehensive documentation hub for the entire project. The following documentation has been consolidated into this single document:

### Previously Separate Documentation Files:

1. **`scripts/README.md`** - Books Scraper System
   - Complete scraper documentation
   - CLI and API usage examples
   - Configuration and troubleshooting guides
   - Performance metrics and best practices

2. **`app/ml/README.md`** - Machine Learning Endpoints
   - ML API endpoints documentation
   - Feature engineering details
   - Training data preparation
   - Prediction service usage
   - Integration examples

### Benefits of Consolidation:

- ✅ **Single Source of Truth**: All documentation in one place
- ✅ **Better Navigation**: Comprehensive table of contents
- ✅ **Reduced Maintenance**: No duplicate information across files
- ✅ **Improved User Experience**: Everything accessible from main README
- ✅ **Better Search**: Single file to search through all documentation

### Individual Module Documentation:

While this README provides comprehensive coverage, individual modules may still contain:
- Code-level documentation in docstrings
- Inline comments for complex logic
- Module-specific technical details
- Development notes and TODOs

This consolidated approach ensures that users can find all essential information in one location while maintaining detailed technical documentation within the codebase itself.
