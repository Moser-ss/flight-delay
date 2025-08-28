"""
Pydantic Models for Flight Delay Prediction API

Defines request and response schemas for API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class AirportInfo(BaseModel):
    """Airport information model."""
    id: int = Field(..., description="Unique airport identifier")
    name: str = Field(..., description="Full airport name")
    code: Optional[str] = Field(None, description="Airport code")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State abbreviation")

class AirportsResponse(BaseModel):
    """Response model for airports endpoint."""
    airports: List[AirportInfo] = Field(..., description="List of all airports")
    total: int = Field(..., description="Total number of airports")

class PredictionRequest(BaseModel):
    """Request model for flight delay prediction."""
    dayOfWeek: int = Field(
        ..., 
        ge=1, 
        le=7, 
        description="Day of week (1=Monday, 2=Tuesday, ..., 7=Sunday)"
    )
    airportId: int = Field(
        ..., 
        description="Airport ID from the airports list"
    )
    
    @validator('dayOfWeek')
    def validate_day_of_week(cls, v):
        if not isinstance(v, int) or v < 1 or v > 7:
            raise ValueError('dayOfWeek must be an integer between 1 and 7 (1=Monday, 7=Sunday)')
        return v
    
    @validator('airportId')
    def validate_airport_id(cls, v):
        if not isinstance(v, int):
            raise ValueError('airportId must be an integer')
        return v

class PredictionDetails(BaseModel):
    """Prediction details model."""
    delayProbability: float = Field(..., description="Probability of delay > 15 minutes (0-1)")
    isDelayed: bool = Field(..., description="Whether flight is predicted to be delayed")
    noDelayProbability: float = Field(..., description="Probability of no delay (0-1)")

class ModelInfo(BaseModel):
    """Model information model."""
    modelType: Optional[str] = Field(None, description="Type of machine learning model")
    accuracy: Optional[float] = Field(None, description="Model accuracy on test data")
    version: Optional[str] = Field(None, description="Model version")

class PredictionInput(BaseModel):
    """Input information for prediction."""
    dayOfWeek: int = Field(..., description="Day of week used for prediction")
    airportId: int = Field(..., description="Airport ID used for prediction")
    airport: AirportInfo = Field(..., description="Airport information")

class PredictionResponse(BaseModel):
    """Response model for flight delay prediction."""
    status: str = Field(..., description="Status of the prediction (success/error)")
    input: PredictionInput = Field(..., description="Input parameters used")
    prediction: PredictionDetails = Field(..., description="Prediction results")
    confidence: float = Field(..., description="Model confidence (0-1)")
    modelInfo: ModelInfo = Field(..., description="Information about the model used")

class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = Field("error", description="Status (always 'error')")
    error: str = Field(..., description="Error message")
    input: Optional[Dict[str, Any]] = Field(None, description="Input that caused the error")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    services: Optional[Dict[str, Any]] = Field(None, description="Service status details")

class ServiceStatus(BaseModel):
    """Service status model."""
    initialized: bool = Field(..., description="Whether services are initialized")
    model: Dict[str, Any] = Field(..., description="Model service status")
    airports: Dict[str, Any] = Field(..., description="Airport service status")

class APIInfo(BaseModel):
    """API information model."""
    message: str = Field(..., description="API welcome message")
    version: str = Field(..., description="API version")
    docs: str = Field(..., description="Documentation URL")
    redoc: str = Field(..., description="ReDoc documentation URL")
    endpoints: List[str] = Field(..., description="Available endpoints")
