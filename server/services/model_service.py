"""
Model Service for Flight Delay Prediction

Handles loading and serving the machine learning model for flight delay predictions.
"""

import pickle
import joblib
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd

logger = logging.getLogger(__name__)

class ModelService:
    """Service for loading and using the flight delay prediction model."""
    
    def __init__(self, model_path: str = "../models/model.pkl"):
        """
        Initialize the model service.
        
        Args:
            model_path: Path to the model file
        """
        self.model_path = Path(model_path)
        self.model_data = None
        self.model_object = None
        self.features = None
        self.metadata = {}
        
    def load_model(self) -> bool:
        """
        Load the model from the specified path.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading model from {self.model_path}")
            
            # Load the model data
            with open(self.model_path, 'rb') as f:
                self.model_data = pickle.load(f)
            
            # Extract model components
            self.model_object = self.model_data['model_object']
            self.features = self.model_data.get('features', ['DayOfWeek', 'OriginAirport_Model'])
            
            # Store metadata
            self.metadata = {
                'model_type': self.model_data.get('model_type'),
                'accuracy': self.model_data.get('accuracy'),
                'version': self.model_data.get('model_version', '1.0'),
                'export_date': self.model_data.get('export_date'),
                'training_samples': self.model_data.get('training_samples'),
                'features': self.features
            }
            
            logger.info(f"Model loaded successfully: {self.metadata['model_type']}")
            logger.info(f"Model accuracy: {self.metadata['accuracy']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def predict_delay(self, day_of_week: int, airport_id: int) -> Dict[str, Any]:
        """
        Predict flight delay probability.
        
        Args:
            day_of_week: Day of week (1=Monday, 7=Sunday)
            airport_id: Airport model ID (1-70)
            
        Returns:
            Dict containing prediction results
        """
        if self.model_object is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Prepare input data
            input_data = [[day_of_week, airport_id]]
            
            # Make prediction
            prediction = self.model_object.predict(input_data)[0]
            probabilities = self.model_object.predict_proba(input_data)[0]
            
            # Extract probabilities
            no_delay_prob = float(probabilities[0])
            delay_prob = float(probabilities[1])
            confidence = float(max(probabilities))
            
            result = {
                'input': {
                    'dayOfWeek': day_of_week,
                    'airportId': airport_id
                },
                'prediction': {
                    'isDelayed': bool(prediction == 1),
                    'delayProbability': delay_prob,
                    'noDelayProbability': no_delay_prob
                },
                'confidence': confidence,
                'modelInfo': {
                    'modelType': self.metadata.get('model_type'),
                    'accuracy': self.metadata.get('accuracy'),
                    'version': self.metadata.get('version')
                }
            }
            
            logger.debug(f"Prediction made for day={day_of_week}, airport={airport_id}: {delay_prob:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction failed: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model metadata and information.
        
        Returns:
            Dict containing model information
        """
        if self.model_object is None:
            return {"status": "Model not loaded"}
        
        return {
            "status": "loaded",
            "metadata": self.metadata,
            "inputFeatures": self.features,
            "supportedValues": {
                "dayOfWeek": "1-7 (1=Monday, 7=Sunday)",
                "airportId": "1-70 (model encoded airport IDs)"
            }
        }
    
    def validate_inputs(self, day_of_week: int, airport_id: int) -> Tuple[bool, str]:
        """
        Validate input parameters.
        
        Args:
            day_of_week: Day of week to validate
            airport_id: Airport ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate day of week
        if not isinstance(day_of_week, int) or day_of_week < 1 or day_of_week > 7:
            return False, "dayOfWeek must be an integer between 1 and 7 (1=Monday, 7=Sunday)"
        
        # Validate airport ID (based on model documentation)
        if not isinstance(airport_id, int) or airport_id < 1 or airport_id > 70:
            return False, "airportId must be an integer between 1 and 70"
        
        return True, ""


# Global model service instance
model_service = ModelService()
