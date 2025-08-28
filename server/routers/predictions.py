"""
Prediction Endpoints for Flight Delay Prediction API

Provides REST API endpoints for flight delay predictions.
"""

from fastapi import APIRouter, HTTPException, Depends
import logging

from models.schemas import (
    PredictionRequest, 
    PredictionResponse, 
    ErrorResponse, 
    PredictionDetails,
    ModelInfo,
    PredictionInput,
    AirportInfo
)
from models.prediction import prediction_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/predict",
    tags=["predictions"],
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)

async def get_prediction_service():
    """Dependency to ensure prediction service is initialized."""
    if not prediction_service._initialized:
        success = prediction_service.initialize()
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize prediction service"
            )
    return prediction_service

@router.post(
    "",
    response_model=PredictionResponse,
    summary="Predict flight delay",
    description="Predicts the probability of a flight delay for a given day of week and airport"
)
async def predict_flight_delay(
    request: PredictionRequest,
    service = Depends(get_prediction_service)
):
    """
    Predict flight delay probability.
    
    Args:
        request: Prediction request with dayOfWeek (1-7) and airportId
        
    Returns:
        PredictionResponse: Prediction results with probability and confidence
        
    Raises:
        HTTPException: If prediction fails or invalid input
    """
    try:
        logger.info(f"Prediction request: day={request.dayOfWeek}, airport={request.airportId}")
        
        # Make prediction
        result = service.predict_flight_delay(
            day_of_week=request.dayOfWeek,
            airport_id=request.airportId
        )
        
        # Check if prediction was successful
        if result["status"] != "success":
            error_detail = result.get("error", "Unknown prediction error")
            
            # Determine appropriate HTTP status code
            if "not found" in error_detail.lower():
                status_code = 404
            elif "invalid" in error_detail.lower() or "must be" in error_detail.lower():
                status_code = 400
            else:
                status_code = 500
                
            raise HTTPException(
                status_code=status_code,
                detail=error_detail
            )
        
        # Convert result to response model
        response = PredictionResponse(
            status="success",
            input=PredictionInput(
                dayOfWeek=result["input"]["dayOfWeek"],
                airportId=result["input"]["airportId"],
                airport=AirportInfo(
                    id=result["input"]["airport"]["name"] and result["input"]["airportId"] or 0,
                    name=result["input"]["airport"]["name"],
                    code=result["input"]["airport"]["code"],
                    city=result["input"]["airport"]["city"],
                    state=result["input"]["airport"]["state"]
                )
            ),
            prediction=PredictionDetails(
                delayProbability=result["prediction"]["delayProbability"],
                isDelayed=result["prediction"]["isDelayed"],
                noDelayProbability=result["prediction"]["noDelayProbability"]
            ),
            confidence=result["confidence"],
            modelInfo=ModelInfo(
                modelType=result["modelInfo"]["modelType"],
                accuracy=result["modelInfo"]["accuracy"],
                version=result["modelInfo"]["version"]
            )
        )
        
        logger.info(f"Prediction successful: {result['prediction']['delayProbability']:.3f}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in prediction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get(
    "/status",
    summary="Get prediction service status",
    description="Returns the status of the prediction service and its dependencies"
)
async def get_prediction_status(service = Depends(get_prediction_service)):
    """
    Get prediction service status.
    
    Returns:
        Service status information including model and airport data status
    """
    try:
        status = service.get_service_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting prediction status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service status: {str(e)}"
        )
