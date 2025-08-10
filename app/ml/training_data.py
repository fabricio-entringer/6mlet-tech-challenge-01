"""Training data processor for ML Endpoint 2: GET /api/v1/ml/training-data."""

import numpy as np
from typing import Dict

from .feature_engineering import FeatureEngineer
from .models import TrainingDataResponse


class TrainingDataProcessor:
    """Processor for training data - Endpoint 2."""
    
    def __init__(self, data_path: str = "data/books_data.csv"):
        """Initialize with feature engineer. We've re-used the FeatureEng to use the same transformation"""
        self.feature_engineer = FeatureEngineer(data_path)
    
    def get_training_data(self, test_size: float = 0.2, random_state: int = 42) -> TrainingDataResponse:
        """Get training data for Endpoint 2: GET /api/v1/ml/training-data."""
        from sklearn.model_selection import train_test_split
        return self._sklearn_split(test_size, random_state)
    
    def _sklearn_split(self, test_size: float, random_state: int) -> TrainingDataResponse:
        """Split using sklearn."""
        from sklearn.model_selection import train_test_split
        
        # Get all features from feature engineer
        features, metadata = self.feature_engineer.get_features()
        
        # Convert to matrix format
        X = [list(f.feature_vector.values()) for f in features]
        y = [f.price_normalized for f in features]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        return TrainingDataResponse(
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            feature_names=metadata.feature_names,
            split_info={
                'train_size': len(X_train),
                'test_size': len(X_test),
                'test_ratio': test_size,
                'random_state': random_state
            }
        )
    
