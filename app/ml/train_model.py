"""Script to train a real price prediction model."""

import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.ml.training_data import TrainingDataProcessor


def train_price_prediction_model():
    """Train a RandomForest model for book price prediction."""
    print("Starting model training...")
    
    # Load and prepare data
    print("Loading training data...")
    processor = TrainingDataProcessor()
    data = processor.get_training_data(test_size=0.2, random_state=42)
    
    print(f"Training samples: {data.split_info['train_size']}")
    print(f"Test samples: {data.split_info['test_size']}")
    
    # Train model
    print("\nTraining RandomForest model...")
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    
    model.fit(data.X_train, data.y_train)
    
    # Evaluate model
    print("\nEvaluating model...")
    train_predictions = model.predict(data.X_train)
    test_predictions = model.predict(data.X_test)
    
    # Calculate metrics
    train_r2 = r2_score(data.y_train, train_predictions)
    test_r2 = r2_score(data.y_test, test_predictions)
    train_mse = mean_squared_error(data.y_train, train_predictions)
    test_mse = mean_squared_error(data.y_test, test_predictions)
    train_mae = mean_absolute_error(data.y_train, train_predictions)
    test_mae = mean_absolute_error(data.y_test, test_predictions)
    
    print(f"\nModel Performance:")
    print(f"Training R² Score: {train_r2:.4f}")
    print(f"Test R² Score: {test_r2:.4f}")
    print(f"Training MSE: {train_mse:.4f}")
    print(f"Test MSE: {test_mse:.4f}")
    print(f"Training MAE: {train_mae:.4f}")
    print(f"Test MAE: {test_mae:.4f}")
    
    # Feature importance
    print("\nTop 10 Most Important Features:")
    feature_importance = sorted(
        zip(data.feature_names, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )
    for feature, importance in feature_importance[:10]:
        print(f"  {feature}: {importance:.4f}")
    
    # Save model
    model_path = Path(__file__).parent / "model.pkl"
    print(f"\nSaving model to {model_path}...")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    # Save model metadata
    metadata = {
        'model_type': 'RandomForestRegressor',
        'version': '1.0',
        'feature_names': data.feature_names,
        'feature_count': len(data.feature_names),
        'train_r2': test_r2,
        'test_mse': test_mse,
        'training_samples': data.split_info['train_size'],
        'test_samples': data.split_info['test_size']
    }
    
    metadata_path = Path(__file__).parent / "model_metadata.pkl"
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"Model training completed successfully!")
    print(f"Model saved to: {model_path}")
    print(f"Metadata saved to: {metadata_path}")
    
    return model, metadata


if __name__ == "__main__":
    train_price_prediction_model()