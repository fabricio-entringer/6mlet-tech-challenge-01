.PHONY: help venv install test run clean clean-logs lint commit bump activate docker-setup-dev docker-setup-prod docker-stop docker-cleanup docker-logs docker-test docker-validate

help:
	@echo "Available commands:"
	@echo ""
	@echo "Development commands:"
	@echo "  venv         - Create virtual environment"
	@echo "  install      - Install dependencies in virtual environment"
	@echo "  test         - Run tests"
	@echo "  run          - Start the FastAPI server"
	@echo "  clean        - Clean cache files and build artifacts"
	@echo "  clean-logs   - Clean log files"
	@echo "  commit       - Create a conventional commit using commitizen"
	@echo "  bump         - Bump version using commitizen"
	@echo "  activate     - Show command to activate virtual environment"
	@echo ""
	@echo "Docker commands:"
	@echo "  docker-setup-dev    - Setup and start Docker development environment"
	@echo "  docker-setup-prod   - Setup and start Docker production environment"
	@echo "  docker-stop         - Stop all Docker containers"
	@echo "  docker-cleanup      - Clean up all Docker resources"
	@echo "  docker-logs         - Show Docker container logs"
	@echo "  docker-test         - Test Docker setup"
	@echo "  docker-validate     - Validate Docker configuration"

venv:
	python3 -m venv venv
	@echo "Virtual environment created successfully!"
	@echo "To activate it, run: source venv/bin/activate"
	
install: venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements.txt

test:
	venv/bin/pytest -v

run:
	venv/bin/python run.py

clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.egg" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .tox
	rm -rf build
	rm -rf dist
	rm -rf htmlcov
	find . -name ".coverage*" -delete
	find . -name ".DS_Store" -delete
	find . -name "Thumbs.db" -delete
	find . -name "*.tmp" -delete
	find . -name "*.temp" -delete

clean-logs:
	rm -rf logs/*.log

commit:
	venv/bin/cz commit

bump:
	venv/bin/cz bump

# Docker commands
docker-setup-dev:
	@echo "Setting up Docker development environment..."
	cd infra && ./docker-manage.sh setup-dev

docker-setup-prod:
	@echo "Setting up Docker production environment..."
	cd infra && ./docker-manage.sh setup-prod

docker-stop:
	@echo "Stopping Docker containers..."
	cd infra && ./docker-manage.sh stop

docker-cleanup:
	@echo "Cleaning up Docker resources..."
	cd infra && ./docker-manage.sh cleanup

docker-logs:
	@echo "Showing Docker logs..."
	cd infra && ./docker-manage.sh logs

docker-test:
	@echo "Running Docker environment tests..."
	cd infra && docker-compose exec api python -m pytest

docker-validate:
	@echo "Validating Docker setup..."
	cd infra && ./validate-setup.sh

activate:
	@echo "To activate the virtual environment, run:"
	@echo "source venv/bin/activate"