"""
Airport Endpoints for Flight Delay Prediction API

Provides REST API endpoints for airport data.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from models.schemas import AirportsResponse, AirportInfo, ErrorResponse
from services.airport_service import airport_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/airports",
    tags=["airports"],
    responses={404: {"model": ErrorResponse}},
)

async def get_airport_service():
    """Dependency to ensure airport service is initialized."""
    if airport_service.airports_df is None:
        success = airport_service.load_airports()
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to load airport data"
            )
    return airport_service

@router.get(
    "",
    response_model=AirportsResponse,
    summary="Get all airports",
    description="Returns a list of all airports sorted alphabetically by name"
)
async def get_airports(service = Depends(get_airport_service)):
    """
    Get all airports sorted alphabetically by name.
    
    Returns:
        AirportsResponse: List of airports with id, name, code, city, and state
    """
    try:
        airports_list = service.get_all_airports()
        
        # Convert to AirportInfo models
        airport_models = [
            AirportInfo(
                id=airport["id"],
                name=airport["name"],
                code=airport["code"],
                city=airport["city"],
                state=airport["state"]
            )
            for airport in airports_list
        ]
        
        logger.info(f"Returning {len(airport_models)} airports")
        
        return AirportsResponse(
            airports=airport_models,
            total=len(airport_models)
        )
        
    except Exception as e:
        logger.error(f"Error getting airports: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve airports: {str(e)}"
        )

@router.get(
    "/{airport_id}",
    response_model=AirportInfo,
    summary="Get airport by ID",
    description="Returns detailed information about a specific airport"
)
async def get_airport_by_id(
    airport_id: int,
    service = Depends(get_airport_service)
):
    """
    Get airport information by ID.
    
    Args:
        airport_id: The airport ID to look up
        
    Returns:
        AirportInfo: Airport details
        
    Raises:
        HTTPException: If airport not found
    """
    try:
        airport_data = service.get_airport_by_id(airport_id)
        
        if airport_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Airport with ID {airport_id} not found"
            )
        
        return AirportInfo(
            id=airport_data["id"],
            name=airport_data["name"],
            code=airport_data["code"],
            city=airport_data["city"],
            state=airport_data["state"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting airport {airport_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve airport: {str(e)}"
        )
