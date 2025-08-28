"""
Airport Data Service for Flight Delay Prediction API

Handles loading and serving airport data from the CSV file.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

class AirportService:
    """Service for loading and managing airport data."""
    
    def __init__(self, airports_path: str = "../airports.csv"):
        """
        Initialize the airport service.
        
        Args:
            airports_path: Path to the airports CSV file
        """
        self.airports_path = Path(airports_path)
        self.airports_df = None
        self._airports_cache = None
        
    def load_airports(self) -> bool:
        """
        Load airports data from CSV file.
        
        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading airports data from {self.airports_path}")
            
            # Load the CSV file
            self.airports_df = pd.read_csv(self.airports_path)
            
            # Clean and validate data
            self.airports_df = self.airports_df.dropna(subset=['AirportID', 'AirportName'])
            
            # Sort by airport name for consistent ordering
            self.airports_df = self.airports_df.sort_values('AirportName')
            
            logger.info(f"Loaded {len(self.airports_df)} airports successfully")
            
            # Clear cache to force refresh
            self._airports_cache = None
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load airports data: {e}")
            return False
    
    @lru_cache(maxsize=1)
    def get_all_airports(self) -> List[Dict[str, Any]]:
        """
        Get all airports as a list of dictionaries, sorted alphabetically by name.
        
        Returns:
            List of airport dictionaries with id and name
        """
        if self.airports_df is None:
            raise RuntimeError("Airports data not loaded. Call load_airports() first.")
        
        # Convert to list of dictionaries
        airports_list = []
        for _, row in self.airports_df.iterrows():
            airport = {
                'id': int(row['AirportID']),
                'name': str(row['AirportName']),
                'code': str(row['AirportCode']) if pd.notna(row['AirportCode']) else None,
                'city': str(row['CityName']) if pd.notna(row['CityName']) else None,
                'state': str(row['State']) if pd.notna(row['State']) else None
            }
            airports_list.append(airport)
        
        # Sort by name (already sorted in load_airports, but ensure consistency)
        airports_list.sort(key=lambda x: x['name'])
        
        logger.debug(f"Returning {len(airports_list)} airports")
        return airports_list
    
    def get_airport_by_id(self, airport_id: int) -> Optional[Dict[str, Any]]:
        """
        Get airport information by ID.
        
        Args:
            airport_id: The airport ID to search for
            
        Returns:
            Airport dictionary or None if not found
        """
        if self.airports_df is None:
            raise RuntimeError("Airports data not loaded. Call load_airports() first.")
        
        airport_row = self.airports_df[self.airports_df['AirportID'] == airport_id]
        
        if airport_row.empty:
            return None
        
        row = airport_row.iloc[0]
        return {
            'id': int(row['AirportID']),
            'name': str(row['AirportName']),
            'code': str(row['AirportCode']) if pd.notna(row['AirportCode']) else None,
            'city': str(row['CityName']) if pd.notna(row['CityName']) else None,
            'state': str(row['State']) if pd.notna(row['State']) else None,
            'modelId': int(row['ModelAirportID']) if pd.notna(row['ModelAirportID']) else None
        }
    
    def get_model_airport_id(self, airport_id: int) -> Optional[int]:
        """
        Get the model airport ID for a given real airport ID.
        This is needed for model predictions since the model was trained with encoded IDs.
        
        Args:
            airport_id: The real airport ID
            
        Returns:
            Model airport ID or None if not found
        """
        if self.airports_df is None:
            raise RuntimeError("Airports data not loaded. Call load_airports() first.")
        
        airport_row = self.airports_df[self.airports_df['AirportID'] == airport_id]
        
        if airport_row.empty:
            return None
        
        model_id = airport_row.iloc[0]['ModelAirportID']
        return int(model_id) if pd.notna(model_id) else None
    
    def validate_airport_id(self, airport_id: int) -> bool:
        """
        Check if an airport ID exists in the dataset.
        
        Args:
            airport_id: Airport ID to validate
            
        Returns:
            True if airport exists, False otherwise
        """
        if self.airports_df is None:
            return False
        
        return not self.airports_df[self.airports_df['AirportID'] == airport_id].empty
    
    def get_airports_summary(self) -> Dict[str, Any]:
        """
        Get summary information about the airports dataset.
        
        Returns:
            Dictionary with dataset summary information
        """
        if self.airports_df is None:
            return {"status": "Airports data not loaded"}
        
        return {
            "status": "loaded",
            "totalAirports": len(self.airports_df),
            "columns": list(self.airports_df.columns),
            "dataTypes": {col: str(dtype) for col, dtype in self.airports_df.dtypes.items()},
            "sampleAirports": self.get_all_airports()[:5]  # First 5 airports as sample
        }


# Global airport service instance
airport_service = AirportService()
