"""
Flight Delay Prediction Logic

Combines model and airport services to provide complete prediction functionality.
"""

import logging
from typing import Dict, Any, Tuple
from services.model_service import model_service
from services.airport_service import airport_service

logger = logging.getLogger(__name__)

class PredictionService:
    """Service that orchestrates model and airport data for predictions."""
    
    def __init__(self):
        """Initialize the prediction service."""
        self.model_service = model_service
        self.airport_service = airport_service
        self._initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize both model and airport services.
        
        Returns:
            True if both services loaded successfully
        """
        try:
            logger.info("Initializing prediction service...")
            
            # Load model
            model_loaded = self.model_service.load_model()
            if not model_loaded:
                logger.error("Failed to load model")
                return False
            
            # Load airports
            airports_loaded = self.airport_service.load_airports()
            if not airports_loaded:
                logger.error("Failed to load airports")
                return False
            
            self._initialized = True
            logger.info("Prediction service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize prediction service: {e}")
            return False
    
    def predict_flight_delay(self, day_of_week: int, airport_id: int) -> Dict[str, Any]:
        """
        Predict flight delay probability for a given day and airport.
        
        Args:
            day_of_week: Day of week (1=Monday, 7=Sunday)
            airport_id: Real airport ID from the airports dataset
            
        Returns:
            Complete prediction result with validation and metadata
        """
        if not self._initialized:
            raise RuntimeError("Prediction service not initialized. Call initialize() first.")
        
        try:
            # Validate inputs
            valid, error_msg = self._validate_prediction_inputs(day_of_week, airport_id)
            if not valid:
                return {
                    "status": "error",
                    "error": error_msg,
                    "input": {
                        "dayOfWeek": day_of_week,
                        "airportId": airport_id
                    }
                }
            
            # Get airport information
            airport_info = self.airport_service.get_airport_by_id(airport_id)
            if not airport_info:
                return {
                    "status": "error",
                    "error": f"Airport with ID {airport_id} not found",
                    "input": {
                        "dayOfWeek": day_of_week,
                        "airportId": airport_id
                    }
                }
            
            # Get model airport ID (encoded ID used by the model)
            model_airport_id = self.airport_service.get_model_airport_id(airport_id)
            if model_airport_id is None:
                return {
                    "status": "error",
                    "error": f"No model mapping found for airport ID {airport_id}",
                    "input": {
                        "dayOfWeek": day_of_week,
                        "airportId": airport_id
                    }
                }
            
            # Make prediction using model airport ID
            prediction_result = self.model_service.predict_delay(day_of_week, model_airport_id)
            
            # Enhance result with airport information
            enhanced_result = {
                "status": "success",
                "input": {
                    "dayOfWeek": day_of_week,
                    "airportId": airport_id,
                    "airport": {
                        "name": airport_info["name"],
                        "code": airport_info["code"],
                        "city": airport_info["city"],
                        "state": airport_info["state"]
                    }
                },
                "prediction": {
                    "delayProbability": prediction_result["prediction"]["delayProbability"],
                    "isDelayed": prediction_result["prediction"]["isDelayed"],
                    "noDelayProbability": prediction_result["prediction"]["noDelayProbability"]
                },
                "confidence": prediction_result["confidence"],
                "modelInfo": prediction_result["modelInfo"]
            }
            
            logger.info(f"Prediction completed for {airport_info['name']} on day {day_of_week}")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                "status": "error",
                "error": f"Internal prediction error: {str(e)}",
                "input": {
                    "dayOfWeek": day_of_week,
                    "airportId": airport_id
                }
            }
    
    def _validate_prediction_inputs(self, day_of_week: int, airport_id: int) -> Tuple[bool, str]:
        """
        Validate prediction inputs.
        
        Args:
            day_of_week: Day of week to validate
            airport_id: Airport ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate day of week
        if not isinstance(day_of_week, int) or day_of_week < 1 or day_of_week > 7:
            return False, "dayOfWeek must be an integer between 1 and 7 (1=Monday, 7=Sunday)"
        
        # Validate airport ID exists
        if not isinstance(airport_id, int):
            return False, "airportId must be an integer"
        
        if not self.airport_service.validate_airport_id(airport_id):
            return False, f"Airport with ID {airport_id} not found in dataset"
        
        return True, ""
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get status of all services.
        
        Returns:
            Dictionary with service status information
        """
        return {
            "initialized": self._initialized,
            "model": self.model_service.get_model_info(),
            "airports": self.airport_service.get_airports_summary()
        }


# Global prediction service instance
prediction_service = PredictionService()
