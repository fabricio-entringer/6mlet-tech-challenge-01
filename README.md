# 6MLET Tech Challenge #1

[![CI](https://github.com/fabricio-entringer/6mlet-tech-challenge-01/workflows/CI/badge.svg)](https://github.com/fabricio-entringer/6mlet-tech-challenge-01/actions)
[![Build and Test PR](https://github.com/fabricio-entringer/6mlet-tech-challenge-01/workflows/Build%20and%20Test%20PR/badge.svg)](https://github.com/fabricio-entringer/6mlet-tech-challenge-01/actions)

<div align="center">
  <img src="assets/app-image.png" alt="6MLET Tech Challenge 01 Application" width="400">
</div>

Tech Challenge #1 - FIAP Machine Learning Engineering Postgraduate specialization course

## Overview

This project is a FastAPI application created for the 6MLET Tech Challenge - Delivery 01. It includes a simple REST API, comprehensive testing with pytest, and version control using commitizen.

This delivery is from **Group #3**, with the following team members:
- **Fabricio Entringer** 
- **Adriano Ribeiro** - [GitHub Profile](https://github.com/adrianoribeiro)

## Features

- **FastAPI** web framework for building APIs
- **Uvicorn** ASGI server for running the application
- **pytest** for testing with async support
- **Commitizen** for conventional commits and version management

## Project Structure

```
├── app/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── tests/
│   ├── __init__.py
│   └── test_main.py     # Test cases
├── assets/              # Project assets
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project configuration
├── pytest.ini          # Pytest configuration
├── run.py              # Application startup script
├── Makefile            # Common tasks
└── README.md           # This file
```

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

## Testing

Run tests using pytest:

```bash
pytest
```

Or using make:

```bash
make test
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
