"""Prediction service for ML Endpoint 3: POST /api/v1/ml/predictions."""

import pickle
from pathlib import Path
import numpy as np
from .feature_engineering import FeatureEngineer
from .models import PredictionRequest, PredictionResponse


class PredictionService:
    """Service for book price predictions - Endpoint 3."""
    
    def __init__(self, data_path: str = "data/books_data.csv"):
        """Initialize with feature engineer and load model."""
        self.feature_engineer = FeatureEngineer(data_path)
        self.model = None
        self.model_metadata = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained model and metadata."""
        model_path = Path(__file__).parent / "model.pkl"
        metadata_path = Path(__file__).parent / "model_metadata.pkl"
        
        try:
            # Load model
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load metadata
            with open(metadata_path, 'rb') as f:
                self.model_metadata = pickle.load(f)
                self.model_version = self.model_metadata.get('version', '1.0')
            
            print(f"Model loaded successfully: {self.model_version}")
        except FileNotFoundError:
            print("Warning: No trained model found. Using mock predictions.")
            self.model = None
            self.model_version = "mock-1.0"
    
    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Make price prediction for Endpoint 3: POST /api/v1/ml/predictions."""
        
        # Generate feature vector using same process as training
        feature_vector = self.feature_engineer.create_feature_from_input(
            title=request.title,
            category=request.category,
            rating=request.rating,
            availability=request.availability
        )
        
        # Use real model if available, otherwise use mock
        if self.model is not None:
            predicted_price = self._real_prediction(feature_vector)
        else:
            predicted_price = self._mock_prediction(request)
        
        # Generate confidence interval (±15% for simplicity)
        confidence_interval = {
            "lower": round(predicted_price * 0.85, 2),
            "upper": round(predicted_price * 1.15, 2)
        }
        
        return PredictionResponse(
            predicted_price=predicted_price,
            confidence_interval=confidence_interval,
            feature_vector=feature_vector,
            model_version=self.model_version
        )
    
    def _mock_prediction(self, request: PredictionRequest) -> float:
        """
        Mock prediction logic.
        
        In production, this would be replaced with:
        1. Load trained model: model = joblib.load('trained_model.pkl')
        2. Apply features: X = np.array([list(feature_vector.values())])
        3. Predict: prediction = model.predict(X)[0]
        4. Denormalize: real_price = denormalize_price(prediction)
        """
        base_price = 25.0
        
        # Rating influences price
        rating_factor = request.rating * 2.5
        
        # Some categories are more expensive
        category_factor = 1.2 if request.category in ['Business', 'Science'] else 1.0
        
        # Calculate final price
        predicted_price = base_price + rating_factor * category_factor
        
        return round(predicted_price, 2)
    
    def load_trained_model(self, model_path: str):
        """
        Load a trained model for production use.
        
        Example:
            service = PredictionService()
            service.load_trained_model('models/price_predictor.pkl')
        """
        # TODO: Implement when real model is available
        # import joblib
        # self.model = joblib.load(model_path)
        # self.model_version = f"trained-{model_path.split('/')[-1]}"
        pass
    
    def _real_prediction(self, feature_vector: dict) -> float:
        """Real prediction using trained model."""
        # Convert feature vector to array format
        X = np.array([list(feature_vector.values())])
        
        # Make prediction (returns normalized price)
        prediction_normalized = self.model.predict(X)[0]
        
        # Denormalize to get real price
        return self._denormalize_price(prediction_normalized)
    
    def _denormalize_price(self, normalized_price: float) -> float:
        """Convert normalized price back to real price."""
        price_stats = self.feature_engineer.price_stats
        return normalized_price * (price_stats['max'] - price_stats['min']) + price_stats['min']