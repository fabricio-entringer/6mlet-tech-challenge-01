"""Enhanced health check service for Issue #14."""

import os
import psutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple, Optional
import csv

from ..models.health_response import (
    HealthResponse,
    ComponentHealth,
    DataStats,
    SystemStats,
    LegacyHealthResponse
)
from ..utils import get_version


class HealthService:
    """Service for comprehensive health checks."""
    
    def __init__(self, data_file_path: Optional[Path] = None):
        """Initialize health service with startup time tracking."""
        self.startup_time = time.time()
        self.version = get_version()
        self.data_file_path = data_file_path or self._get_data_file_path()
    
    def _get_data_file_path(self) -> Path:
        """Get the path to the books data file."""
        current_dir = Path(__file__).parent.parent.parent
        return current_dir / "data" / "books_data.csv"
    
    def _format_uptime(self) -> str:
        """Format uptime in human-readable format."""
        uptime_seconds = int(time.time() - self.startup_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _check_data_file_health(self) -> Tuple[ComponentHealth, DataStats]:
        """Check the health of the CSV data file."""
        now = datetime.now(timezone.utc)
        
        try:
            if not self.data_file_path.exists():
                return (
                    ComponentHealth(
                        status="unhealthy",
                        details="Data file not found",
                        last_checked=now
                    ),
                    DataStats(
                        total_books=0,
                        total_categories=0,
                        last_updated=None,
                        file_size_mb=0.0
                    )
                )
            
            # Get file stats
            file_stats = self.data_file_path.stat()
            file_size_mb = file_stats.st_size / (1024 * 1024)
            last_modified = datetime.fromtimestamp(file_stats.st_mtime, tz=timezone.utc)
            
            # Read and analyze data
            total_books = 0
            categories = set()
            
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_books += 1
                    if 'category' in row and row['category']:
                        categories.add(row['category'])
            
            # Determine health status
            if total_books == 0:
                status = "degraded"
                details = "No data records found"
            elif total_books < 100:
                status = "degraded" 
                details = f"Low data count: {total_books} books"
            else:
                status = "healthy"
                details = f"Data file operational with {total_books} books"
            
            return (
                ComponentHealth(
                    status=status,
                    details=details,
                    last_checked=now
                ),
                DataStats(
                    total_books=total_books,
                    total_categories=len(categories),
                    last_updated=last_modified,
                    file_size_mb=round(file_size_mb, 2)
                )
            )
            
        except Exception as e:
            return (
                ComponentHealth(
                    status="unhealthy",
                    details=f"Error reading data file: {str(e)}",
                    last_checked=now
                ),
                DataStats(
                    total_books=0,
                    total_categories=0,
                    last_updated=None,
                    file_size_mb=0.0
                )
            )
    
    def _check_memory_health(self) -> Tuple[ComponentHealth, SystemStats]:
        """Check system memory health."""
        now = datetime.now(timezone.utc)
        
        try:
            # Get memory information
            memory = psutil.virtual_memory()
            process = psutil.Process()
            
            # Current process memory usage in MB
            process_memory_mb = process.memory_info().rss / (1024 * 1024)
            
            # System memory percentage
            memory_percent = memory.percent
            
            # Determine health status based on memory usage
            if memory_percent >= 90:
                status = "unhealthy"
                details = f"Critical memory usage: {memory_percent:.1f}%"
            elif memory_percent >= 75:
                status = "degraded"
                details = f"High memory usage: {memory_percent:.1f}%"
            else:
                status = "healthy"
                details = f"Memory usage normal: {memory_percent:.1f}%"
            
            return (
                ComponentHealth(
                    status=status,
                    details=details,
                    last_checked=now
                ),
                SystemStats(
                    memory_usage_mb=round(process_memory_mb, 2),
                    memory_percent=round(memory_percent, 1),
                    disk_usage_percent=None  # Could be added later if needed
                )
            )
            
        except Exception as e:
            return (
                ComponentHealth(
                    status="unhealthy",
                    details=f"Error checking memory: {str(e)}",
                    last_checked=now
                ),
                SystemStats(
                    memory_usage_mb=0.0,
                    memory_percent=0.0,
                    disk_usage_percent=None
                )
            )
    
    def _check_api_health(self) -> ComponentHealth:
        """Check API service health."""
        now = datetime.now(timezone.utc)
        
        # Simple health check - if we're here, the API is responding
        return ComponentHealth(
            status="healthy",
            details="API service operational",
            last_checked=now
        )
    
    async def get_comprehensive_health(self) -> HealthResponse:
        """Get comprehensive health status for the new /api/v1/health endpoint."""
        
        # Perform all health checks
        data_health, data_stats = self._check_data_file_health()
        memory_health, system_stats = self._check_memory_health()
        api_health = self._check_api_health()
        
        # Collect component statuses
        components = {
            "api": api_health,
            "data_files": data_health,
            "memory": memory_health
        }
        
        # Determine overall status
        component_statuses = [comp.status for comp in components.values()]
        
        if any(status == "unhealthy" for status in component_statuses):
            overall_status = "unhealthy"
        elif any(status == "degraded" for status in component_statuses):
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return HealthResponse(
            status=overall_status,
            version=self.version,
            timestamp=datetime.now(timezone.utc),
            uptime=self._format_uptime(),
            components=components,
            data=data_stats,
            system=system_stats,
            api_info={
                "environment": os.getenv("ENVIRONMENT", "development"),
                "python_version": f"{psutil.version_info}".replace("svn", ""),
                "endpoints_available": "21+"
            }
        )
    
    async def get_legacy_health(self) -> LegacyHealthResponse:
        """Get simple health status for backward compatibility."""
        # Perform basic checks to determine if system is operational
        data_health, _ = self._check_data_file_health()
        memory_health, _ = self._check_memory_health()
        
        # Simple logic: if critical components are not unhealthy, we're healthy
        if data_health.status == "unhealthy" or memory_health.status == "unhealthy":
            status = "unhealthy"
        else:
            status = "healthy"
        
        return LegacyHealthResponse(status=status)
