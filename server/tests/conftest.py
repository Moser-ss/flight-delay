"""
Test configuration and fixtures for the Flight Delay Prediction API tests.
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def sample_prediction_request():
    """Sample valid prediction request."""
    return {
        "dayOfWeek": 1,  # Monday
        "airportId": 10397  # Atlanta airport
    }

@pytest.fixture
def invalid_prediction_requests():
    """Sample invalid prediction requests for testing validation."""
    return [
        {"dayOfWeek": 0, "airportId": 10397},  # Invalid day (too low)
        {"dayOfWeek": 8, "airportId": 10397},  # Invalid day (too high)
        {"dayOfWeek": 1, "airportId": "invalid"},  # Invalid airport ID type
        {"dayOfWeek": "invalid", "airportId": 10397},  # Invalid day type
        {"airportId": 10397},  # Missing dayOfWeek
        {"dayOfWeek": 1},  # Missing airportId
        {},  # Empty request
        {"dayOfWeek": 1, "airportId": 99999},  # Non-existent airport
    ]
