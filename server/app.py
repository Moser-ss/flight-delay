"""
Flight Delay Prediction API

FastAPI application for serving flight delay predictions and airport data.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from contextlib import asynccontextmanager

# Add current directory to path for imports
sys.path.append('.')

from routers import airports, predictions
from models.schemas import APIInfo, HealthResponse, ServiceStatus
from models.prediction import prediction_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting Flight Delay Prediction API...")
    
    # Initialize prediction service
    success = prediction_service.initialize()
    if success:
        logger.info("Prediction service initialized successfully")
    else:
        logger.error("Failed to initialize prediction service")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Flight Delay Prediction API...")

# Initialize FastAPI app with lifespan management
app = FastAPI(
    title="Flight Delay Prediction API",
    description="API for predicting flight delays and managing airport data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(airports.router)
app.include_router(predictions.router)

@app.get("/", response_model=APIInfo)
async def root():
    """Root endpoint returning basic API information."""
    return APIInfo(
        message="Flight Delay Prediction API",
        version="1.0.0",
        docs="/docs",
        redoc="/redoc",
        endpoints=[
            "/airports - Get all airports",
            "/airports/{id} - Get airport by ID", 
            "/predict - Predict flight delay",
            "/predict/status - Get prediction service status",
            "/health - Health check"
        ]
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with service status."""
    try:
        # Get service status
        if prediction_service._initialized:
            service_status = prediction_service.get_service_status()
            status = "healthy"
        else:
            service_status = {"error": "Prediction service not initialized"}
            status = "unhealthy"
        
        return HealthResponse(
            status=status,
            services=service_status
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            services={"error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
