"""
Tests for prediction endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestPredictionEndpoints:
    """Test prediction-related endpoints."""

    def test_predict_valid_request(self, client: TestClient, sample_prediction_request):
        """Test prediction with valid request."""
        response = client.post("/predict", json=sample_prediction_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        required_fields = ["status", "input", "prediction", "confidence", "modelInfo"]
        for field in required_fields:
            assert field in data
        
        # Check status
        assert data["status"] == "success"
        
        # Check input echo
        input_data = data["input"]
        assert input_data["dayOfWeek"] == sample_prediction_request["dayOfWeek"]
        assert input_data["airportId"] == sample_prediction_request["airportId"]
        assert "airport" in input_data
        
        # Check airport info in input
        airport_info = input_data["airport"]
        assert "name" in airport_info
        assert "code" in airport_info
        assert "city" in airport_info
        assert "state" in airport_info
        
        # Check prediction details
        prediction = data["prediction"]
        assert "delayProbability" in prediction
        assert "isDelayed" in prediction
        assert "noDelayProbability" in prediction
        
        # Check probability values
        delay_prob = prediction["delayProbability"]
        no_delay_prob = prediction["noDelayProbability"]
        
        assert 0 <= delay_prob <= 1
        assert 0 <= no_delay_prob <= 1
        assert abs((delay_prob + no_delay_prob) - 1.0) < 0.001  # Should sum to 1
        
        # Check is_delayed consistency
        assert prediction["isDelayed"] == (delay_prob > 0.5)
        
        # Check confidence
        confidence = data["confidence"]
        assert 0 <= confidence <= 1
        assert confidence == max(delay_prob, no_delay_prob)
        
        # Check model info
        model_info = data["modelInfo"]
        assert "modelType" in model_info
        assert "accuracy" in model_info
        assert "version" in model_info

    def test_predict_invalid_requests(self, client: TestClient, invalid_prediction_requests):
        """Test prediction with various invalid requests."""
        for invalid_request in invalid_prediction_requests:
            response = client.post("/predict", json=invalid_request)
            
            # Should return validation error or not found
            assert response.status_code in [400, 404, 422], f"Failed for request: {invalid_request}"
            
            data = response.json()
            assert "detail" in data

    def test_predict_day_of_week_validation(self, client: TestClient):
        """Test day of week validation specifically."""
        base_request = {"dayOfWeek": 1, "airportId": 10397}
        
        # Test all valid days (1-7)
        for day in range(1, 8):
            request = base_request.copy()
            request["dayOfWeek"] = day
            response = client.post("/predict", json=request)
            assert response.status_code == 200
        
        # Test invalid days
        invalid_days = [0, 8, -1, 10]
        for day in invalid_days:
            request = base_request.copy()
            request["dayOfWeek"] = day
            response = client.post("/predict", json=request)
            assert response.status_code == 422  # Validation error

    def test_predict_airport_validation(self, client: TestClient):
        """Test airport ID validation."""
        # Get valid airport IDs first
        airports_response = client.get("/airports")
        assert airports_response.status_code == 200
        airports = airports_response.json()["airports"]
        valid_airport_ids = [airport["id"] for airport in airports]
        
        # Test with valid airport IDs
        for airport_id in valid_airport_ids[:5]:  # Test first 5
            request = {"dayOfWeek": 1, "airportId": airport_id}
            response = client.post("/predict", json=request)
            assert response.status_code == 200
        
        # Test with invalid airport ID
        invalid_airport_id = 99999
        request = {"dayOfWeek": 1, "airportId": invalid_airport_id}
        response = client.post("/predict", json=request)
        assert response.status_code == 404  # Not found

    def test_predict_response_consistency(self, client: TestClient):
        """Test that prediction responses are consistent for the same input."""
        request = {"dayOfWeek": 1, "airportId": 10397}
        
        # Make multiple requests
        responses = []
        for _ in range(3):
            response = client.post("/predict", json=request)
            assert response.status_code == 200
            responses.append(response.json())
        
        # All responses should be identical
        first_response = responses[0]
        for response in responses[1:]:
            assert response["prediction"]["delayProbability"] == first_response["prediction"]["delayProbability"]
            assert response["prediction"]["isDelayed"] == first_response["prediction"]["isDelayed"]
            assert response["confidence"] == first_response["confidence"]

    def test_predict_different_inputs(self, client: TestClient):
        """Test predictions with different valid inputs."""
        test_cases = [
            {"dayOfWeek": 1, "airportId": 10397},  # Monday, Atlanta
            {"dayOfWeek": 7, "airportId": 10397},  # Sunday, Atlanta
            {"dayOfWeek": 1, "airportId": 12892},  # Monday, LAX
            {"dayOfWeek": 5, "airportId": 11298},  # Friday, Dallas
        ]
        
        predictions = []
        for request in test_cases:
            response = client.post("/predict", json=request)
            assert response.status_code == 200
            
            data = response.json()
            predictions.append({
                "request": request,
                "delay_prob": data["prediction"]["delayProbability"],
                "is_delayed": data["prediction"]["isDelayed"]
            })
        
        # Predictions should potentially vary (not all identical)
        delay_probs = [p["delay_prob"] for p in predictions]
        assert len(set(delay_probs)) > 1 or len(delay_probs) == 1, "Some variation in predictions expected"

    def test_predict_status_endpoint(self, client: TestClient):
        """Test the prediction status endpoint."""
        response = client.get("/predict/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should contain service status information
        assert "initialized" in data
        assert isinstance(data["initialized"], bool)
        
        if data["initialized"]:
            assert "model" in data
            assert "airports" in data
            
            # Check model status
            model_status = data["model"]
            assert "status" in model_status
            
            # Check airports status
            airports_status = data["airports"]
            assert "status" in airports_status

    def test_predict_response_time(self, client: TestClient):
        """Test that prediction endpoint responds quickly."""
        import time
        
        request = {"dayOfWeek": 1, "airportId": 10397}
        
        start_time = time.time()
        response = client.post("/predict", json=request)
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should respond within 1 second
        response_time = end_time - start_time
        assert response_time < 1.0, f"Response time {response_time:.3f}s exceeds 1 second"

    def test_predict_error_handling(self, client: TestClient):
        """Test error handling in prediction endpoint."""
        # Test with wrong content type (should fail)
        response = client.post(
            "/predict", 
            data="{\"dayOfWeek\": 1, \"airportId\": 10397}",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == 422
        
        # Test with empty body
        response = client.post("/predict")
        assert response.status_code == 422
