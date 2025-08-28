"""
Tests for the main FastAPI application endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestMainEndpoints:
    """Test main application endpoints."""

    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint returns API information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "redoc" in data
        assert "endpoints" in data
        
        # Check values
        assert data["message"] == "Flight Delay Prediction API"
        assert data["version"] == "1.0.0"
        assert data["docs"] == "/docs"
        assert data["redoc"] == "/redoc"
        assert isinstance(data["endpoints"], list)
        assert len(data["endpoints"]) > 0

    def test_health_endpoint(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "timestamp" in data
        
        # Status should be either healthy or unhealthy
        assert data["status"] in ["healthy", "unhealthy"]
        
        # Timestamp should be a valid ISO format string
        assert isinstance(data["timestamp"], str)
        
        # If services are included, check structure
        if "services" in data:
            services = data["services"]
            if isinstance(services, dict) and "initialized" in services:
                assert isinstance(services["initialized"], bool)

    def test_docs_endpoint(self, client: TestClient):
        """Test that API documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_endpoint(self, client: TestClient):
        """Test that ReDoc documentation is available."""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_schema(self, client: TestClient):
        """Test that OpenAPI schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # Check that our endpoints are documented
        paths = schema["paths"]
        assert "/" in paths
        assert "/health" in paths
        assert "/airports" in paths
        assert "/predict" in paths

    def test_cors_headers(self, client: TestClient):
        """Test that CORS headers are properly configured."""
        # Test preflight request
        response = client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        })
        
        # CORS should allow the request
        assert response.status_code == 200
        
        # Check CORS headers in actual request
        response = client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers
