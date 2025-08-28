"""
Tests for airport endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestAirportsEndpoints:
    """Test airport-related endpoints."""

    def test_get_all_airports(self, client: TestClient):
        """Test getting all airports."""
        response = client.get("/airports")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "airports" in data
        assert "total" in data
        
        airports = data["airports"]
        total = data["total"]
        
        # Should have airports
        assert isinstance(airports, list)
        assert len(airports) > 0
        assert total == len(airports)
        assert total == 70  # We know there are 70 airports
        
        # Check first airport structure
        first_airport = airports[0]
        required_fields = ["id", "name", "code", "city", "state"]
        for field in required_fields:
            assert field in first_airport
        
        # Check data types
        assert isinstance(first_airport["id"], int)
        assert isinstance(first_airport["name"], str)
        
        # Check alphabetical sorting by name
        airport_names = [airport["name"] for airport in airports]
        assert airport_names == sorted(airport_names), "Airports should be sorted alphabetically by name"

    def test_get_airport_by_id_valid(self, client: TestClient):
        """Test getting a specific airport by valid ID."""
        # Test with known airport ID (Atlanta)
        airport_id = 10397
        response = client.get(f"/airports/{airport_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        required_fields = ["id", "name", "code", "city", "state"]
        for field in required_fields:
            assert field in data
        
        # Check values
        assert data["id"] == airport_id
        assert isinstance(data["name"], str)
        assert len(data["name"]) > 0

    def test_get_airport_by_id_invalid(self, client: TestClient):
        """Test getting airport with invalid ID."""
        # Test with non-existent airport ID
        invalid_id = 99999
        response = client.get(f"/airports/{invalid_id}")
        
        assert response.status_code == 404
        data = response.json()
        
        # Should have error message
        assert "detail" in data
        assert str(invalid_id) in data["detail"]

    def test_get_airport_by_id_invalid_type(self, client: TestClient):
        """Test getting airport with invalid ID type."""
        # Test with non-integer ID
        response = client.get("/airports/invalid_id")
        
        assert response.status_code == 422  # Validation error

    def test_airports_endpoint_consistency(self, client: TestClient):
        """Test that individual airport endpoints are consistent with list endpoint."""
        # Get all airports
        all_response = client.get("/airports")
        assert all_response.status_code == 200
        all_airports = all_response.json()["airports"]
        
        # Test a few individual airports
        test_airports = all_airports[:3]  # Test first 3 airports
        
        for expected_airport in test_airports:
            airport_id = expected_airport["id"]
            individual_response = client.get(f"/airports/{airport_id}")
            
            assert individual_response.status_code == 200
            individual_airport = individual_response.json()
            
            # Should match the data from the list endpoint
            assert individual_airport["id"] == expected_airport["id"]
            assert individual_airport["name"] == expected_airport["name"]
            assert individual_airport["code"] == expected_airport["code"]
            assert individual_airport["city"] == expected_airport["city"]
            assert individual_airport["state"] == expected_airport["state"]

    def test_airports_data_quality(self, client: TestClient):
        """Test the quality and completeness of airport data."""
        response = client.get("/airports")
        assert response.status_code == 200
        
        airports = response.json()["airports"]
        
        # Check data quality
        for airport in airports:
            # ID should be positive integer
            assert airport["id"] > 0
            
            # Name should be non-empty string
            assert len(airport["name"]) > 0
            
            # Code can be None or non-empty string
            if airport["code"] is not None:
                assert len(airport["code"]) > 0
            
            # City can be None or non-empty string  
            if airport["city"] is not None:
                assert len(airport["city"]) > 0
            
            # State can be None or non-empty string
            if airport["state"] is not None:
                assert len(airport["state"]) > 0

    def test_airports_response_time(self, client: TestClient):
        """Test that airports endpoint responds quickly."""
        import time
        
        start_time = time.time()
        response = client.get("/airports")
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should respond within 1 second (generous for CI/testing)
        response_time = end_time - start_time
        assert response_time < 1.0, f"Response time {response_time:.3f}s exceeds 1 second"
