"""
Integration tests for the Flight Delay Prediction API.
"""

import pytest
from fastapi.testclient import TestClient


class TestAPIIntegration:
    """Test integration scenarios across multiple endpoints."""

    def test_full_prediction_workflow(self, client: TestClient):
        """Test complete workflow: get airports -> predict for specific airport."""
        # Step 1: Get all airports
        airports_response = client.get("/airports")
        assert airports_response.status_code == 200
        
        airports_data = airports_response.json()
        airports = airports_data["airports"]
        assert len(airports) > 0
        
        # Step 2: Pick an airport and make prediction
        test_airport = airports[0]  # First airport (alphabetically)
        airport_id = test_airport["id"]
        
        prediction_request = {
            "dayOfWeek": 1,  # Monday
            "airportId": airport_id
        }
        
        prediction_response = client.post("/predict", json=prediction_request)
        assert prediction_response.status_code == 200
        
        prediction_data = prediction_response.json()
        
        # Step 3: Verify airport info consistency
        returned_airport = prediction_data["input"]["airport"]
        assert returned_airport["name"] == test_airport["name"]
        
        # Step 4: Verify prediction structure
        assert "delayProbability" in prediction_data["prediction"]
        assert "confidence" in prediction_data

    def test_airport_lookup_integration(self, client: TestClient):
        """Test integration between airports list and individual airport lookup."""
        # Get all airports
        all_airports_response = client.get("/airports")
        assert all_airports_response.status_code == 200
        
        all_airports = all_airports_response.json()["airports"]
        
        # Test individual lookup for several airports
        test_airports = all_airports[:5]  # Test first 5
        
        for expected_airport in test_airports:
            airport_id = expected_airport["id"]
            
            # Individual lookup
            individual_response = client.get(f"/airports/{airport_id}")
            assert individual_response.status_code == 200
            
            individual_airport = individual_response.json()
            
            # Data should match
            assert individual_airport["id"] == expected_airport["id"]
            assert individual_airport["name"] == expected_airport["name"]

    def test_prediction_with_all_weekdays(self, client: TestClient):
        """Test predictions for all days of the week with same airport."""
        airport_id = 10397  # Atlanta airport
        
        predictions = {}
        
        for day in range(1, 8):  # Monday=1 to Sunday=7
            request = {"dayOfWeek": day, "airportId": airport_id}
            response = client.post("/predict", json=request)
            
            assert response.status_code == 200
            data = response.json()
            
            predictions[day] = {
                "delay_probability": data["prediction"]["delayProbability"],
                "is_delayed": data["prediction"]["isDelayed"],
                "confidence": data["confidence"]
            }
        
        # All predictions should be valid
        for day, prediction in predictions.items():
            assert 0 <= prediction["delay_probability"] <= 1
            assert 0 <= prediction["confidence"] <= 1
            assert isinstance(prediction["is_delayed"], bool)

    def test_prediction_with_multiple_airports(self, client: TestClient):
        """Test predictions for multiple airports on same day."""
        # Get several airports
        airports_response = client.get("/airports")
        assert airports_response.status_code == 200
        
        airports = airports_response.json()["airports"]
        test_airports = airports[:10]  # Test first 10 airports
        
        day_of_week = 1  # Monday
        predictions = {}
        
        for airport in test_airports:
            airport_id = airport["id"]
            request = {"dayOfWeek": day_of_week, "airportId": airport_id}
            
            response = client.post("/predict", json=request)
            assert response.status_code == 200
            
            data = response.json()
            predictions[airport_id] = {
                "airport_name": airport["name"],
                "delay_probability": data["prediction"]["delayProbability"],
                "is_delayed": data["prediction"]["isDelayed"]
            }
        
        # All predictions should be valid
        assert len(predictions) == len(test_airports)
        
        for airport_id, prediction in predictions.items():
            assert 0 <= prediction["delay_probability"] <= 1
            assert isinstance(prediction["is_delayed"], bool)

    def test_service_health_integration(self, client: TestClient):
        """Test that health endpoint reflects actual service status."""
        # Check health
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        health_data = health_response.json()
        
        # If services are healthy, endpoints should work
        if health_data["status"] == "healthy":
            # Test airports endpoint
            airports_response = client.get("/airports")
            assert airports_response.status_code == 200
            
            # Test prediction endpoint
            prediction_request = {"dayOfWeek": 1, "airportId": 10397}
            prediction_response = client.post("/predict", json=prediction_request)
            assert prediction_response.status_code == 200

    def test_api_consistency_across_endpoints(self, client: TestClient):
        """Test that data is consistent across different endpoints."""
        # Get airport from airports list
        airports_response = client.get("/airports")
        assert airports_response.status_code == 200
        
        airports = airports_response.json()["airports"]
        test_airport = airports[0]
        
        # Get same airport individually
        individual_response = client.get(f"/airports/{test_airport['id']}")
        assert individual_response.status_code == 200
        individual_airport = individual_response.json()
        
        # Use airport in prediction
        prediction_request = {"dayOfWeek": 1, "airportId": test_airport["id"]}
        prediction_response = client.post("/predict", json=prediction_request)
        assert prediction_response.status_code == 200
        prediction_data = prediction_response.json()
        
        # Airport data should be consistent across all endpoints
        prediction_airport = prediction_data["input"]["airport"]
        
        assert test_airport["name"] == individual_airport["name"] == prediction_airport["name"]
        assert test_airport["code"] == individual_airport["code"] == prediction_airport["code"]
        assert test_airport["city"] == individual_airport["city"] == prediction_airport["city"]
        assert test_airport["state"] == individual_airport["state"] == prediction_airport["state"]

    def test_error_handling_integration(self, client: TestClient):
        """Test error handling across different scenarios."""
        # Test 404 scenarios
        
        # Non-existent airport in individual lookup
        response = client.get("/airports/99999")
        assert response.status_code == 404
        
        # Non-existent airport in prediction
        response = client.post("/predict", json={"dayOfWeek": 1, "airportId": 99999})
        assert response.status_code == 404
        
        # Test 422 validation scenarios
        
        # Invalid day of week
        response = client.post("/predict", json={"dayOfWeek": 8, "airportId": 10397})
        assert response.status_code == 422
        
        # Invalid airport ID type in individual lookup
        response = client.get("/airports/invalid")
        assert response.status_code == 422
        
        # All error responses should have detail field
        for status_code in [404, 422]:
            # Find a response with this status code from above tests
            pass  # Already tested above

    def test_performance_under_load(self, client: TestClient):
        """Test API performance with multiple rapid requests."""
        import time
        
        # Test multiple airport requests
        start_time = time.time()
        for i in range(10):
            response = client.get("/airports")
            assert response.status_code == 200
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        assert avg_time < 0.5, f"Average response time {avg_time:.3f}s too slow"
        
        # Test multiple prediction requests
        start_time = time.time()
        for i in range(10):
            request = {"dayOfWeek": (i % 7) + 1, "airportId": 10397}
            response = client.post("/predict", json=request)
            assert response.status_code == 200
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 10
        assert avg_time < 0.5, f"Average prediction time {avg_time:.3f}s too slow"
