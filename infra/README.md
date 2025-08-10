# Docker Containerization for 6MLET Tech Challenge 01

This directory contains Docker configuration files for containerizing the 6MLET Tech Challenge 01 FastAPI application.

## Files Overview

- `Dockerfile` - Multi-stage Docker build configuration
- `docker-compose.yml` - Development environment setup
- `docker-compose.prod.yml` - Production environment setup
- `.env.example` - Environment variables template
- `.env.production` - Production environment template
- `.dockerignore` - Files to exclude from Docker build context
- `.gitignore` - Files to ignore in git for this directory

## Quick Start

### Development Environment

1. **Copy environment file:**
   ```bash
   cd infra
   cp .env.example .env
   ```

2. **Start development environment:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - API: http://localhost:8000
   - Health check: http://localhost:8000/health
   - API docs: http://localhost:8000/docs

### Production Environment

1. **Copy and configure production environment:**
   ```bash
   cd infra
   cp .env.production .env
   # Edit .env with proper production values
   ```

2. **Start production environment:**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

3. **Access the application:**
   - API: http://localhost:8080

## Architecture

### Multi-Stage Build

The Dockerfile uses multi-stage builds with two targets:

#### Development Stage
- Hot reloading enabled
- Development dependencies included
- Runs as root for easier development
- Includes test dependencies

#### Production Stage
- Optimized for security and performance
- Runs as non-root user (`appuser`)
- Multi-worker deployment with Uvicorn
- Resource limits configured

### Services

#### API Service
- **Development**: Hot reloading, source code mounted as volume
- **Production**: Optimized build, resource limits, multiple workers

#### Data Initialization Service
- Copies CSV data files to persistent volumes on first run
- Ensures data persistence across container restarts

### Volumes

- **data_volume**: Persistent storage for CSV data files
- **logs_volume**: Persistent storage for application logs
- **Source code mounts** (dev only): Enable hot reloading

### Networks

- Custom bridge network for service communication
- Isolated from host network for security

## Environment Variables

### Core Settings
- `ENVIRONMENT`: `development` or `production`
- `LOG_LEVEL`: `debug`, `info`, `warning`, `error`
- `DATA_PATH`: Path to CSV data files (`/app/data`)
- `API_HOST`: Host to bind to (`0.0.0.0`)
- `API_PORT`: Port to bind to (`8000`)

### Development Settings
- `HOT_RELOAD`: Enable hot reloading (`true`)
- `DEBUG`: Enable debug mode (`true`)

### Production Settings
- `WORKERS`: Number of Uvicorn workers (`4`)

## Health Checks

Both development and production containers include health checks:
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start period**: 5 seconds
- **Retries**: 3

The health check calls the `/health` endpoint to verify the application is running.

## Security Features

### Production Security
- **Non-root user**: Application runs as `appuser`
- **Read-only data**: Data volume mounted read-only in production
- **Resource limits**: Memory and CPU limits configured
- **Minimal base image**: Python 3.12 slim for reduced attack surface

### Development Security
- Isolated network
- No sensitive data in images
- Environment variables for configuration

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

2. **Permission issues (development):**
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
   # Development
   docker-compose exec api bash
   
   # Production
   docker-compose -f docker-compose.prod.yml exec api bash
   ```

2. **Check container logs:**
   ```bash
   docker-compose logs api
   ```

3. **Inspect container:**
   ```bash
   docker inspect 6mlet-api-dev
   ```

## Performance Optimization

### Build Optimization
- Multi-stage builds reduce final image size
- Layer caching for dependencies
- `.dockerignore` excludes unnecessary files

### Runtime Optimization
- Production uses multiple Uvicorn workers
- Resource limits prevent resource exhaustion
- Health checks ensure container reliability

## Integration with Existing Project

The Docker setup integrates seamlessly with the existing project structure:

- **Source code**: Mounted as volumes in development
- **Data files**: Persistent volumes for CSV data
- **Configuration**: Environment variables for different stages
- **Testing**: Development container includes test dependencies
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
- Hot reloading enabled
- Source code mounted
- Debug logging
- Development dependencies

### Staging/Testing
- Production-like configuration
- Persistent data storage
- Health monitoring
- Resource limits

### Production
- Optimized security
- Multiple workers
- Resource constraints
- Monitoring ready
