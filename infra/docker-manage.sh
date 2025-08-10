#!/bin/bash

# Docker Management Scripts for 6MLET Tech Challenge 01
# Collection of utility scripts for managing Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if docker-compose is available
check_compose() {
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "docker-compose is not installed. Please install it and try again."
        exit 1
    fi
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    
    docker build -t 6mlet-tech-challenge-01:latest -f Dockerfile ..
    
    print_success "Docker image built successfully!"
    print_status "Image: 6mlet-tech-challenge-01:latest"
}

# Function to run Docker image directly
run_image() {
    print_status "Running Docker image directly..."
    
    # Check if image exists
    if ! docker image inspect 6mlet-tech-challenge-01:latest >/dev/null 2>&1; then
        print_warning "Image not found. Building image first..."
        build_image
    fi
    
    # Stop any existing container with the same name
    docker stop 6mlet-api 2>/dev/null || true
    docker rm 6mlet-api 2>/dev/null || true
    
    # Run the container
    print_status "Starting container on port 8000..."
    docker run --rm -p 8000:8000 \
        --name 6mlet-api \
        -v $(pwd)/../data:/app/data:ro \
        -v 6mlet-logs:/app/logs \
        -e ENVIRONMENT=production \
        -e LOG_LEVEL=info \
        6mlet-tech-challenge-01:latest &
    
    print_success "Container started successfully!"
    print_status "API available at: http://localhost:8000"
    print_status "Health check: http://localhost:8000/health"
    print_status "API docs: http://localhost:8000/docs"
    print_warning "Container is running in the background. Use 'docker stop 6mlet-api' to stop it."
}

# Function to setup environment
setup() {
    print_status "Setting up Docker environment..."
    
    # Copy environment file if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "Please review and modify .env file as needed"
    else
        print_warning ".env file already exists"
    fi
    
    # Build and start containers
    print_status "Building and starting containers..."
    docker-compose up --build -d
    
    print_success "Docker environment started!"
    print_status "API available at: http://localhost:${API_PORT:-8000}"
    print_status "Health check: http://localhost:${API_PORT:-8000}/health"
    print_status "API docs: http://localhost:${API_PORT:-8000}/docs"
}

# Function to setup production environment
setup_prod() {
    print_status "Setting up production environment..."
    setup
}

# Function to stop all containers
stop_all() {
    print_status "Stopping all containers..."
    
    # Stop containers
    if docker-compose ps -q >/dev/null 2>&1; then
        docker-compose down
        print_success "Containers stopped"
    fi
}

# Function to clean up Docker resources
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    # Stop containers
    stop_all
    
    # Remove volumes
    docker volume rm 6mlet-data 6mlet-logs 2>/dev/null || true
    
    # Remove networks
    docker network rm 6mlet-network 2>/dev/null || true
    
    # Prune unused images
    docker image prune -f
    
    print_success "Cleanup completed!"
}

# Function to show logs
show_logs() {
    local service=${1:-api}
    
    print_status "Showing logs for $service..."
    docker-compose logs -f $service
}

# Function to backup data
backup_data() {
    local backup_dir="backups"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="data_backup_$timestamp.tar.gz"
    
    print_status "Creating data backup..."
    
    # Create backup directory if it doesn't exist
    mkdir -p $backup_dir
    
    # Backup data
    if docker volume ls | grep -q 6mlet-data; then
        docker run --rm -v 6mlet-data:/data -v $(pwd)/$backup_dir:/backup alpine \
            tar czf /backup/$backup_file -C /data .
        print_success "Data backed up to $backup_dir/$backup_file"
    fi
}

# Function to restore data
restore_data() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        print_error "Please provide backup file path"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_status "Restoring data from $backup_file..."
    
    local volume_name="6mlet-data"
    
    docker run --rm -v $volume_name:/data -v $(pwd):/backup alpine \
        tar xzf /backup/$backup_file -C /data
    
    print_success "Data restored to $volume_name"
}

# Function to show help
show_help() {
    echo "Docker Management Script for 6MLET Tech Challenge 01"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build                     Build Docker image"
    echo "  run                       Run Docker image directly (without compose)"
    echo "  setup                     Setup Docker environment with compose"
    echo "  stop                      Stop all containers"
    echo "  cleanup                   Clean up all Docker resources"
    echo "  logs [service]            Show logs (default: api)"
    echo "  backup                    Backup data volumes"
    echo "  restore [file]            Restore data from backup"
    echo "  help                      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build                 # Build Docker image"
    echo "  $0 run                   # Run image directly"
    echo "  $0 setup                 # Start with Docker Compose"
    echo "  $0 logs api              # Show API logs"
    echo "  $0 restore backup.tar.gz # Restore data"
    echo ""
}

# Main script logic
main() {
    # Change to infra directory
    cd "$(dirname "$0")"
    
    # Check prerequisites
    check_docker
    check_compose
    
    # Parse command
    case "$1" in
        build)
            build_image
            ;;
        run)
            run_image
            ;;
        setup|setup-dev|setup-prod)
            setup
            ;;
        stop)
            stop_all
            ;;
        cleanup)
            cleanup
            ;;
        logs)
            show_logs "$2"
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$2"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
