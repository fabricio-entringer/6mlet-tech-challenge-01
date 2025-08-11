# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


### Added
- Initial FastAPI application with health check endpoints
- Root endpoint with welcome message
- Health check endpoint
- Version endpoint that returns current application version
- Virtual environment setup with venv
- Test suite using pytest with async support
- Commitizen for conventional commits and version management
- Makefile for common development tasks
- GitHub Actions CI/CD workflows
- Comprehensive documentation
- Modern Python dependencies (FastAPI 0.115.12, Uvicorn 0.34.3, Python 3.12+)
## v0.1.1 (2025-08-11)

## v0.1.0 (2025-08-11)

### Feat

- Add comprehensive HTTP API test suite and improve Docker workflow
- extract version from pyproject.toml for Docker image tagging
- enhance render deployment workflow with API-based deployment
- migrate deployment from Railway to Render.com
- add Docker image build and run commands to Makefile
- add .dockerignore to project root for Docker build optimization
- implement Docker containerization for FastAPI application
- Enhanced OpenAPI/Swagger documentation according to issue #26
- implement Issue #9 - CSV data loader with caching and validation
- complete Issue #8 - enhance data models with validation and examples
- implement comprehensive health endpoint for Issue #14
- implement GET /api/v1/stats/overview endpoint (issue #15)
- implement GET /api/v1/stats/categories endpoint
- implement price range filtering for books API
- implement top-rated books API endpoint
- implement books API endpoint with search functionality
- implement GET /api/v1/books endpoint with filtering, sorting, and pagination
- Add utility methods for price and rating conversion
- reorganize app structure with separate API and models directories
- **api**: implement books scraper system with REST endpoints
- **ci**: add branch protection workflow for master branch
- update issue templates to remove prefixes from titles
- update README with production URLs for API endpoints
- add GitHub Actions workflow for deploying to Railway
- enhance PR summary to include security and code quality results
- update license format and refine package finding configuration
- simplify PR build logic and update artifact upload action
- enhance PR summary with debug output and improve conditional checks
- add team member details to project overview in README
- add CODEOWNERS file to define repository ownership
- move version retrieval logic to a separate utils module
- enhance README and issue templates with detailed API documentation and contribution guidelines
- initial project setup with FastAPI, CI/CD workflows, and comprehensive documentation

### Fix

- update server endpoint configuration to use environment variables
- update health check error message and add CORS middleware for API
- update CI workflows to restrict branches and improve version handling in utils
- correct Docker health check endpoint and use run.py for startup
- remove test execution from deployment workflow
- Update OpenAPI URL in tests to match FastAPI configuration
- Replace Markdown with HTML formatting in Swagger documentation
- correct CI test failure for mock data expectations
- **workflow**: update PR build test to use new health endpoint
- **tests**: update test_main.py health endpoint test for new response format
- **health**: resolve GitHub workflow test failures
- resolve CI test failures in overview stats endpoint
- add mocking to category stats tests for CI compatibility
- Add sample_books_data.csv for CI/CD testing
- resolve CI/CD workflow issues
- update book ID handling in scraper and tests for consistency
- update quality check condition to allow for empty quality result
- enable verbose output for pytest in test command
- apply Black code formatting to resolve quality gate issues
- update application startup command in CI workflow
- **ci**: update branch protection workflow to allow all branches for pull requests
- reorder import statements for consistency in main and utils modules
- correct formatting and ensure consistent newline usage in main and utils modules

### Refactor

- simplify Docker setup to single unified image
- merge all .gitignore files into single root .gitignore
- remove redundant convert_rating_to_float function
- remove redundant category validation tests and update assertions in category retrieval test
- **workflow**: improve branch protection logic for pull requests
- **test**: clean up test_scraper_api to match actual API methods
