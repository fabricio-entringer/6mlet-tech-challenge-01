.PHONY: help venv install test run clean clean-logs lint commit bump activate docker-build docker-run docker-setup docker-stop docker-cleanup docker-logs docker-test docker-validate

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
	@echo "  docker-build        - Build Docker image"
	@echo "  docker-run          - Run Docker image directly (without compose)"
	@echo "  docker-setup        - Setup and start Docker environment"
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
docker-build:
	@echo "Building Docker image..."
	@if ! docker info >/dev/null 2>&1; then \
		echo "❌ Docker is not running. Please start Docker and try again."; \
		exit 1; \
	fi
	cd infra && docker build -t 6mlet-tech-challenge-01:latest -f Dockerfile ..
	@echo "✅ Docker image built successfully!"

docker-run:
	@echo "Running Docker image..."
	@if ! docker info >/dev/null 2>&1; then \
		echo "❌ Docker is not running. Please start Docker and try again."; \
		exit 1; \
	fi
	@if ! docker image inspect 6mlet-tech-challenge-01:latest >/dev/null 2>&1; then \
		echo "⚠️ Image not found. Building image first..."; \
		$(MAKE) docker-build; \
	fi
	@echo "Stopping any existing container..."
	-docker stop 6mlet-api 2>/dev/null
	-docker rm 6mlet-api 2>/dev/null
	@echo "Starting container on port 8000..."
	cd infra && docker run -d --rm -p 8000:8000 \
		--name 6mlet-api \
		-v $$(pwd)/../data:/app/data:ro \
		-v 6mlet-logs:/app/logs \
		-e ENVIRONMENT=production \
		-e LOG_LEVEL=info \
		6mlet-tech-challenge-01:latest
	@echo "✅ Container started successfully!"
	@echo "🌐 API available at: http://localhost:8000"
	@echo "🏥 Health check: http://localhost:8000/health"
	@echo "📚 API docs: http://localhost:8000/docs"
	@echo "ℹ️ Container is running in background. Use 'make docker-stop' to stop it."

docker-setup:
	@echo "Setting up Docker environment..."
	@if ! docker info >/dev/null 2>&1; then \
		echo "❌ Docker is not running. Please start Docker and try again."; \
		exit 1; \
	fi
	@if ! command -v docker-compose >/dev/null 2>&1; then \
		echo "❌ docker-compose is not installed. Please install it and try again."; \
		exit 1; \
	fi
	cd infra && if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from template"; \
		echo "⚠️ Please review and modify .env file as needed"; \
	fi
	cd infra && docker-compose up --build -d
	@echo "✅ Docker environment started!"
	@echo "🌐 API available at: http://localhost:8000"
	@echo "🏥 Health check: http://localhost:8000/health"
	@echo "📚 API docs: http://localhost:8000/docs"

docker-stop:
	@echo "Stopping Docker containers..."
	@if docker ps -q --filter "name=6mlet-api" | grep -q .; then \
		docker stop 6mlet-api; \
		echo "✅ Stopped direct container"; \
	fi
	@if docker-compose -f infra/docker-compose.yml ps -q >/dev/null 2>&1; then \
		cd infra && docker-compose down; \
		echo "✅ Stopped compose environment"; \
	fi

docker-cleanup:
	@echo "Cleaning up Docker resources..."
	$(MAKE) docker-stop
	@echo "Removing volumes..."
	-docker volume rm 6mlet-data 6mlet-logs 2>/dev/null
	@echo "Removing networks..."
	-docker network rm 6mlet-network 2>/dev/null
	@echo "Pruning unused images..."
	docker image prune -f
	@echo "✅ Cleanup completed!"

docker-logs:
	@echo "Showing Docker logs..."
	@if docker ps -q --filter "name=6mlet-api" | grep -q .; then \
		docker logs -f 6mlet-api; \
	elif docker-compose -f infra/docker-compose.yml ps -q >/dev/null 2>&1; then \
		cd infra && docker-compose logs -f api; \
	else \
		echo "❌ No running containers found"; \
	fi

docker-test:
	@echo "Running Docker environment tests..."
	@if docker-compose -f infra/docker-compose.yml ps -q >/dev/null 2>&1; then \
		cd infra && docker-compose exec api python -m pytest; \
	else \
		echo "❌ Docker compose environment not running. Start it first with 'make docker-setup'"; \
	fi

docker-validate:
	@echo "Validating Docker setup..."
	cd infra && ./validate-setup.sh

activate:
	@echo "To activate the virtual environment, run:"
	@echo "source venv/bin/activate"