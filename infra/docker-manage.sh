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

# Function to setup development environment
setup_dev() {
    print_status "Setting up development environment..."
    
    # Copy environment file if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "Please review and modify .env file as needed"
    else
        print_warning ".env file already exists"
    fi
    
    # Build and start development containers
    print_status "Building and starting development containers..."
    docker-compose up --build -d
    
    print_success "Development environment started!"
    print_status "API available at: http://localhost:${API_PORT:-8000}"
    print_status "Health check: http://localhost:${API_PORT:-8000}/health"
    print_status "API docs: http://localhost:${API_PORT:-8000}/docs"
}

# Function to setup production environment
setup_prod() {
    print_status "Setting up production environment..."
    
    # Copy production environment file if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.production .env
        print_success "Created .env file from production template"
        print_warning "Please review and modify .env file with production values"
    else
        print_warning ".env file already exists"
    fi
    
    # Build and start production containers
    print_status "Building and starting production containers..."
    docker-compose -f docker-compose.prod.yml up --build -d
    
    print_success "Production environment started!"
    print_status "API available at: http://localhost:8080"
}

# Function to stop all containers
stop_all() {
    print_status "Stopping all containers..."
    
    # Stop development containers
    if docker-compose ps -q >/dev/null 2>&1; then
        docker-compose down
        print_success "Development containers stopped"
    fi
    
    # Stop production containers
    if docker-compose -f docker-compose.prod.yml ps -q >/dev/null 2>&1; then
        docker-compose -f docker-compose.prod.yml down
        print_success "Production containers stopped"
    fi
}

# Function to clean up Docker resources
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    # Stop containers
    stop_all
    
    # Remove volumes
    docker volume rm 6mlet-data 6mlet-logs 2>/dev/null || true
    docker volume rm 6mlet-data-prod 6mlet-logs-prod 2>/dev/null || true
    
    # Remove networks
    docker network rm 6mlet-network 6mlet-network-prod 2>/dev/null || true
    
    # Prune unused images
    docker image prune -f
    
    print_success "Cleanup completed!"
}

# Function to show logs
show_logs() {
    local service=${1:-api}
    local env=${2:-dev}
    
    print_status "Showing logs for $service ($env environment)..."
    
    if [ "$env" = "prod" ]; then
        docker-compose -f docker-compose.prod.yml logs -f $service
    else
        docker-compose logs -f $service
    fi
}

# Function to backup data
backup_data() {
    local backup_dir="backups"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="data_backup_$timestamp.tar.gz"
    
    print_status "Creating data backup..."
    
    # Create backup directory if it doesn't exist
    mkdir -p $backup_dir
    
    # Backup development data
    if docker volume ls | grep -q 6mlet-data; then
        docker run --rm -v 6mlet-data:/data -v $(pwd)/$backup_dir:/backup alpine \
            tar czf /backup/dev_$backup_file -C /data .
        print_success "Development data backed up to $backup_dir/dev_$backup_file"
    fi
    
    # Backup production data
    if docker volume ls | grep -q 6mlet-data-prod; then
        docker run --rm -v 6mlet-data-prod:/data -v $(pwd)/$backup_dir:/backup alpine \
            tar czf /backup/prod_$backup_file -C /data .
        print_success "Production data backed up to $backup_dir/prod_$backup_file"
    fi
}

# Function to restore data
restore_data() {
    local backup_file=$1
    local env=${2:-dev}
    
    if [ -z "$backup_file" ]; then
        print_error "Please provide backup file path"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_status "Restoring data from $backup_file ($env environment)..."
    
    local volume_name="6mlet-data"
    if [ "$env" = "prod" ]; then
        volume_name="6mlet-data-prod"
    fi
    
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
    echo "  setup-dev                 Setup development environment"
    echo "  setup-prod                Setup production environment"
    echo "  stop                      Stop all containers"
    echo "  cleanup                   Clean up all Docker resources"
    echo "  logs [service] [env]      Show logs (default: api, dev)"
    echo "  backup                    Backup data volumes"
    echo "  restore [file] [env]      Restore data from backup (default: dev)"
    echo "  help                      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup-dev             # Start development environment"
    echo "  $0 setup-prod            # Start production environment"
    echo "  $0 logs api dev           # Show development API logs"
    echo "  $0 logs api prod          # Show production API logs"
    echo "  $0 restore backup.tar.gz  # Restore development data"
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
        setup-dev)
            setup_dev
            ;;
        setup-prod)
            setup_prod
            ;;
        stop)
            stop_all
            ;;
        cleanup)
            cleanup
            ;;
        logs)
            show_logs "$2" "$3"
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$2" "$3"
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
