"""Feature engineering for ML Endpoint 1: GET /api/v1/ml/features."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from .models import FeatureVector, FeatureMetadata, NormalizationInfo, EncodingInfo
from ..data import get_data_service


class FeatureEngineer:
    """Feature engineering for book price prediction - Endpoint 1"""
    
    def __init__(self, data_path: str = "data/books_data.csv"):
        """Initialize feature engineer with data service."""
        self.data_path = Path(data_path)
        self.df = None
        self.categories = []
        self.price_stats = {}
        
        # Use the new data service for efficient data access
        self.data_service = get_data_service()
        self._load_data()
    
    def _load_data(self):
        """Load and preprocess data using the data service."""
        # Try to load data using the new data service first
        df = self.data_service.csv_loader.load_dataframe()
        
        if df is not None:
            self.df = df
            self._process_data_from_dataframe()
        else:
            # Fallback to original method if data service fails
            self._load_data_fallback()
    
    def _load_data_fallback(self):
        """Fallback data loading method."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        self.df = pd.read_csv(self.data_path)
        self._process_data_from_dataframe()
    
    def _process_data_from_dataframe(self):
        """Process data from pandas DataFrame."""
        # Extract numeric price from string (if not already done)
        if 'price_numeric' not in self.df.columns:
            self.df['price_numeric'] = self.df['price'].str.extract(r'([0-9.]+)').astype(float)
        
        # Fix invalid category
        # "Add a comment" changed to "Default" to preserve data instead of removing records
        invalid_count = (self.df['category'] == 'Add a comment').sum()
        if invalid_count > 0:
            self.df.loc[self.df['category'] == 'Add a comment', 'category'] = 'Default'
            print(f"Reassigned {invalid_count} invalid categories to 'Default'")
        
        # Get unique categories
        self.categories = sorted(self.df['category'].unique().tolist())
        
        self._calculate_stats()
    
    def _calculate_stats(self):
        """Calculate statistics for normalization."""
        self.price_stats = {
            'min': self.df['price_numeric'].min(),
            'max': self.df['price_numeric'].max(),
            'mean': self.df['price_numeric'].mean(),
            'std': self.df['price_numeric'].std()
        }
    
    def _normalize_value(self, value: float, stats: Dict[str, float]) -> float:
        """Normalize a value using min-max normalization."""
        if stats['max'] == stats['min']:
            return 0.5
        return (value - stats['min']) / (stats['max'] - stats['min'])
    
    def _one_hot_encode_category(self, category: str) -> Dict[str, int]:
        """One-hot encode category - create 1 column for every category found in the dataset."""
        encoding = {}
        for cat in self.categories:
            encoding[f'category_{cat}'] = 1 if cat == category else 0
        return encoding
    
    def _one_hot_encode_rating(self, rating: int) -> Dict[str, int]:
        """One-hot encode rating - create 5 columns (rating_One until rating_Five)."""
        rating_texts = ['One', 'Two', 'Three', 'Four', 'Five']
        encoding = {}
        for i, text in enumerate(rating_texts, 1):
            encoding[f'rating_{text}'] = 1 if i == rating else 0
        return encoding
    
    def _one_hot_encode_availability(self, availability: str) -> Dict[str, int]:
        """One-hot encode availability - Create 2 columns (in_stock e out_of_stock)."""
        is_in_stock = 'in stock' in availability.lower()
        return {
            'availability_in_stock': 1 if is_in_stock else 0,
            'availability_out_of_stock': 0 if is_in_stock else 1
        }
    
    # Apply all transformation
    def create_feature_vector(self, row: pd.Series) -> Dict[str, float]:
        """
        The heart of FE - transform raw data into a vector for a single book.
        
        BEFORE (Raw CSV data):
        row = {
            'title': 'Advanced Machine Learning Techniques',
            'rating_numeric': 4,
            'category': 'Science', 
            'availability': 'In stock'
        }
        
        AFTER (ML-ready features), as array for ML model:
        [0.75, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0]
         ^^^   ^^^^^^^^^^^^^^^^^ ^^^^^^^^^^ ^^^^
        rating   categories      ratings   avail
        
        Result: Text → Numbers, 1 book → ~13 features, Ready for ML training
        """
        features = {}
        
        # Numeric features (normalized)
        features['rating'] = self._normalize_value(row['rating_numeric'], {'min': 1, 'max': 5})
        
        # One-hot encoded features
        # Note: update() is used instead of manual loops for cleaner code
        # Merge all one-hot encoded features into the main dictionary
        features.update(self._one_hot_encode_category(row['category']))
        features.update(self._one_hot_encode_rating(row['rating_numeric']))
        features.update(self._one_hot_encode_availability(row['availability']))
        
        return features
    

    """
    This part is interesting, I discovered during the challenge implementation:
    For ML research, tabular format might be better. But for public APIs, metadata is important because:

        1. Other developers need to understand the data
        2. Production needs to reproduce processing
        3. Auditing needs to track transformations
    """
    def get_features(self, sample_size: Optional[int] = None, shuffle: bool = False) -> Tuple[List[FeatureVector], FeatureMetadata]:
        """Get feature vectors for Endpoint 1: GET /api/v1/ml/features."""
        df_sample = self.df.copy()
        
        # The shuffle part is optional
        if shuffle:
            df_sample = df_sample.sample(frac=1).reset_index(drop=True)
        
        if sample_size and sample_size < len(df_sample):
            df_sample = df_sample.head(sample_size)
        
        # Create feature vectors
        features = []
        for idx, row in df_sample.iterrows():
            feature_vector = self.create_feature_vector(row)
            
            feature_data = FeatureVector(
                book_id=str(idx),
                feature_vector=feature_vector,
                original_price=row['price_numeric'],
                price_normalized=self._normalize_value(row['price_numeric'], self.price_stats)
            )
            features.append(feature_data)
        
        # Create metadata
        if features:
            feature_names = list(features[0].feature_vector.keys())
        else:
            feature_names = []
        
        metadata = FeatureMetadata(
            total_samples=len(features),
            feature_names=feature_names,
            feature_count=len(feature_names),
            normalization={
                'price': NormalizationInfo(**self.price_stats),
                'rating': NormalizationInfo(min=1, max=5)
            },
            encoding_info=EncodingInfo(
                categories=self.categories,
                total_categories=len(self.categories)
            )
        )
        
        return features, metadata
    
    # Useful for prediction
    def create_feature_from_input(self, title: str, category: str, rating: int, availability: str) -> Dict[str, float]:
        """Create feature vector from user input (used by prediction service)."""
        # Create a fake row with the input data
        row = pd.Series({
            'title': title,
            'category': category,
            'rating_numeric': rating,
            'availability': availability
        })
        
        return self.create_feature_vector(row)