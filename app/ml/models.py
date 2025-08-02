"""Pydantic models for ML endpoints - Desafio 2."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class FeatureVector(BaseModel):
    """Individual feature vector for a book."""
    
    book_id: str = Field(..., description="Unique id for the book")
    # go to create_feature_vector to see more details
    feature_vector: Dict[str, float] = Field(..., description="Normalized feature vector")
    original_price: float = Field(..., description="Original price for reference")
    price_normalized: float = Field(..., description="Normalized price (target variable)")


class NormalizationInfo(BaseModel):
    """Normalization parameters for a feature."""
    
    min: float
    max: float
    mean: Optional[float] = None
    std: Optional[float] = None


class EncodingInfo(BaseModel):
    """Information about categorical encoding."""
    
    categories: List[str] = Field(..., description="List of unique categories")
    total_categories: int = Field(..., description="Total number of categories")


class FeatureMetadata(BaseModel):
    """Metadata about the feature engineering process."""
    
    total_samples: int = Field(..., description="Total number of samples")
    feature_names: List[str] = Field(..., description="List of all feature names")
    feature_count: int = Field(..., description="Total number of features")
    normalization: Dict[str, NormalizationInfo] = Field(..., description="Normalization parameters for each feature")
    encoding_info: EncodingInfo = Field(..., description="Information about categorical encoding")


class MLFeaturesResponse(BaseModel):
    """Response model for ML features endpoint."""
    
    features: List[FeatureVector] = Field(..., description="List of feature vectors")
    metadata: FeatureMetadata = Field(..., description="Metadata about features")


class TrainingDataResponse(BaseModel):
    """Response model for training data endpoint."""
    
    X_train: List[List[float]] = Field(..., description="Training features")
    y_train: List[float] = Field(..., description="Training targets")
    X_test: Optional[List[List[float]]] = Field(None, description="Test features")
    y_test: Optional[List[float]] = Field(None, description="Test targets")
    feature_names: List[str] = Field(..., description="Feature names in order")
    split_info: Dict[str, float] = Field(..., description="Information about train/test split")


class PredictionRequest(BaseModel):
    """Request model for prediction endpoint."""
    
    title: str = Field(..., description="Book title")
    category: str = Field(..., description="Book category")
    rating: int = Field(..., ge=1, le=5, description="Book rating (1-5)")
    availability: str = Field(..., description="Book availability status")


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint."""
    
    predicted_price: float = Field(..., description="Predicted price in original currency")
    confidence_interval: Optional[Dict[str, float]] = Field(None, description="Confidence interval if available")
    feature_vector: Dict[str, float] = Field(..., description="Generated feature vector")
    model_version: str = Field(..., description="Version of the model used")
    
    model_config = {"protected_namespaces": ()}