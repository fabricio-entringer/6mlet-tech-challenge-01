"""Health check response models."""

from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ComponentHealth(BaseModel):
    """Health status for individual components."""
    
    status: str = Field(..., description="Component health status")
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
    """Response model for the enhanced health endpoint."""
    
    status: str = Field(..., description="Overall health status (healthy, degraded, unhealthy)")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(..., description="Current timestamp")
    uptime: str = Field(..., description="Application uptime")
    components: Dict[str, ComponentHealth] = Field(..., description="Health status of individual components")
    data: DataStats = Field(..., description="Data statistics")
    system: SystemStats = Field(..., description="System resource statistics")
    api_info: Dict[str, str] = Field(..., description="API metadata")


class LegacyHealthResponse(BaseModel):
    """Legacy health response for backward compatibility."""
    
    status: str = Field(..., description="Service status")
