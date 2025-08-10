# Docker Containerization for 6MLET Tech Challenge 01

This directory contains Docker configuration files for containerizing the 6MLET Tech Challenge 01 FastAPI application.

## Files Overview

- `Dockerfile` - Docker build configuration for deployment
- `docker-compose.yml` - Docker Compose setup for running the application
- `.env.example` - Environment variables template
- `.dockerignore` - Files to exclude from Docker build context
- `docker-manage.sh` - Management script for Docker operations
- `validate-setup.sh` - Setup validation script

## Quick Start

### Setup Environment

1. **Copy environment file:**
   ```bash
   cd infra
   cp .env.example .env
   ```

2. **Start the application:**
   ```bash
   docker-compose up --build
   # or use the management script
   ./docker-manage.sh setup
   ```

3. **Access the application:**
   - API: http://localhost:8000
   - Health check: http://localhost:8000/health
   - API docs: http://localhost:8000/docs

## Architecture

### Single Image Build

The Dockerfile creates a production-ready image suitable for deployment in any environment:

- **Security optimized**: Runs as non-root user (`appuser`)
- **Minimal base image**: Python 3.12 slim for reduced attack surface
- **Layer optimized**: Dependencies cached separately for faster rebuilds
- **Health checks**: Built-in health monitoring

### Services

#### API Service
- Single image deployment suitable for any environment
- Environment-configurable behavior through variables
- Persistent data and logs through Docker volumes

#### Data Initialization Service
- Copies CSV data files to persistent volumes on first run
- Ensures data persistence across container restarts

### Volumes

- **data_volume**: Persistent storage for CSV data files
- **logs_volume**: Persistent storage for application logs

### Networks

- Custom bridge network for service communication
- Isolated from host network for security

## Environment Variables

### Core Settings
- `ENVIRONMENT`: `production` (default) or `development`
- `LOG_LEVEL`: `debug`, `info` (default), `warning`, `error`
- `DATA_PATH`: Path to CSV data files (`/app/data`)
- `API_HOST`: Host to bind to (`0.0.0.0`)
- `API_PORT`: Port to bind to (`8000`)

## Health Checks

The container includes health checks:
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start period**: 5 seconds
- **Retries**: 3

The health check calls the `/health` endpoint to verify the application is running.

## Security Features

- **Non-root user**: Application runs as `appuser`
- **Minimal base image**: Python 3.12 slim for reduced attack surface
- **Isolated network**: Custom Docker network
- **Environment variables**: Secure configuration management

## Management Commands

### Using Management Script
```bash
# Setup and start environment
./docker-manage.sh setup

# View logs
./docker-manage.sh logs

# Stop containers
./docker-manage.sh stop

# Clean up resources
./docker-manage.sh cleanup

# Backup data
./docker-manage.sh backup

# Restore data
./docker-manage.sh restore backup.tar.gz
```

### Using Make Commands
```bash
# Setup Docker environment
make docker-setup

# View logs
make docker-logs

# Stop containers
make docker-stop

# Clean up resources
make docker-cleanup

# Validate setup
make docker-validate
```

## Volume Management

### Data Persistence
```bash
# View volumes
docker volume ls | grep 6mlet

# Inspect volume
docker volume inspect 6mlet-data

# Backup data volume
docker run --rm -v 6mlet-data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz -C /data .

# Restore data volume
docker run --rm -v 6mlet-data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /data
```

### Log Management
```bash
# View logs
docker-compose logs -f api

# View log files in volume
docker run --rm -v 6mlet-logs:/logs alpine ls -la /logs
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change port in .env file
   API_PORT=8001
   ```

2. **Permission issues:**
   ```bash
   # Ensure proper ownership
   sudo chown -R $USER:$USER ../data ../logs
   ```

3. **Data not persisting:**
   ```bash
   # Check volume mounts
   docker-compose config
   ```

4. **Build failures:**
   ```bash
   # Clean build
   docker-compose down
   docker system prune -f
   docker-compose up --build
   ```

### Debugging

1. **Access container shell:**
   ```bash
   docker-compose exec api bash
   ```

2. **Check container logs:**
   ```bash
   docker-compose logs api
   ```

3. **Inspect container:**
   ```bash
   docker inspect 6mlet-api
   ```

## Performance Optimization

### Build Optimization
- Layer caching for dependencies
- `.dockerignore` excludes unnecessary files
- Optimized base image selection

### Runtime Optimization
- Non-root user for security
- Health checks ensure container reliability
- Persistent volumes for data

## Integration with Existing Project

The Docker setup integrates seamlessly with the existing project structure:

- **Source code**: Application code built into container image
- **Data files**: Persistent volumes for CSV data
- **Configuration**: Environment variables for different stages
- **Logging**: Persistent log storage

## Multi-Architecture Support

The Docker configuration supports multiple architectures:
- `amd64` (Intel/AMD)
- `arm64` (Apple Silicon, ARM servers)

To build for specific architecture:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -f infra/Dockerfile .
```

## Deployment Scenarios

### Local Development
- Quick setup with `docker-compose up`
- Environment variables for customization
- Persistent data storage

### Production Deployment
- Single image suitable for any container platform
- Security hardened with non-root user
- Health monitoring ready
- Configurable through environment variables

### Cloud Deployment
- Compatible with Docker-based platforms
- Environment variable configuration
- Persistent volume support
- Health check integration
