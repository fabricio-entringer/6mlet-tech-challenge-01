"""Health check response models."""

from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ComponentHealth(BaseModel):
    """Health status for individual components."""
    
    status: str = Field(..., description="Component health status: healthy, degraded, or unhealthy")
    details: Optional[str] = Field(None, description="Additional details about component health")
    last_checked: datetime = Field(..., description="Last time this component was checked")


class DataStats(BaseModel):
    """Statistics about the data in the system."""
    
    total_books: int = Field(..., ge=0, description="Total number of books in the system")
    total_categories: int = Field(..., ge=0, description="Total number of categories")
    last_updated: Optional[datetime] = Field(None, description="Last time data was updated")
    file_size_mb: Optional[float] = Field(None, description="Data file size in MB")


class SystemStats(BaseModel):
    """System resource statistics."""
    
    memory_usage_mb: float = Field(..., ge=0, description="Current memory usage in MB")
    memory_percent: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    disk_usage_percent: Optional[float] = Field(None, ge=0, le=100, description="Disk usage percentage")


class HealthResponse(BaseModel):
    """
    Response model for the enhanced health endpoint.
    
    Provides comprehensive health information for monitoring system status,
    component health, data statistics, and system resources.
    """
    
    status: str = Field(..., description="Overall health status (healthy, degraded, unhealthy)")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(..., description="Current timestamp")
    uptime: str = Field(..., description="Application uptime in human-readable format")
    components: Dict[str, ComponentHealth] = Field(..., description="Health status of individual components")
    data: DataStats = Field(..., description="Data statistics")
    system: SystemStats = Field(..., description="System resource statistics")
    api_info: Dict[str, str] = Field(..., description="API metadata and environment info")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2025-08-10T10:00:00Z",
                "uptime": "2h 30m 15s",
                "components": {
                    "api": {
                        "status": "healthy",
                        "details": "API service operational",
                        "last_checked": "2025-08-10T10:00:00Z"
                    },
                    "data_files": {
                        "status": "healthy", 
                        "details": "Data file operational with 1000 books",
                        "last_checked": "2025-08-10T10:00:00Z"
                    },
                    "memory": {
                        "status": "healthy",
                        "details": "Memory usage normal: 45.2%",
                        "last_checked": "2025-08-10T10:00:00Z"
                    }
                },
                "data": {
                    "total_books": 1000,
                    "total_categories": 50,
                    "last_updated": "2025-08-10T08:00:00Z",
                    "file_size_mb": 2.5
                },
                "system": {
                    "memory_usage_mb": 128.5,
                    "memory_percent": 45.2,
                    "disk_usage_percent": None
                },
                "api_info": {
                    "environment": "development",
                    "python_version": "3.12.11",
                    "endpoints_available": "21+"
                }
            }
        }
    )


class LegacyHealthResponse(BaseModel):
    """Legacy health response for backward compatibility."""
    
    status: str = Field(..., description="Service status: healthy or unhealthy")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy"
            }
        }
    )
