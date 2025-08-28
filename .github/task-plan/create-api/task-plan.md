# Flight Delay Prediction API - Task Plan

## Project Overview
Create a FastAPI-based API to serve flight delay predictions and airport data for the frontend application. The API will expose machine learning models created in the previous phase and provide structured data for user interaction.

## Technical Specifications
- **Framework**: FastAPI (https://fastapi.tiangolo.com/)
- **Runtime**: Python 3.11+
- **Port**: 8080
- **Location**: `/server` directory in repository root
- **Response Format**: JSON
- **Model Integration**: Direct loading from existing model files (`model.pkl`, `model.joblib`, `airports.csv`)

## Task Breakdown

### Phase 1: Project Initialization ✅
- [x] **Task 1.1**: Create `/server` directory structure
- [x] **Task 1.2**: Create Python virtual environment
- [x] **Task 1.3**: Install FastAPI dependencies
  ```bash
  pip install fastapi uvicorn pandas scikit-learn joblib
  pip install python-multipart  # For form data if needed
  ```
- [x] **Task 1.4**: Create `requirements.txt` file
- [x] **Task 1.5**: Set up project structure and main application file

### Phase 2: Model Integration ✅
- [x] **Task 2.1**: Analyze existing model files:
  - `model.pkl` (complete model with metadata)
  - `model.joblib` (alternative format)
  - `model_object.pkl` (lightweight version)
  - `airports.csv` (airport reference data)
- [x] **Task 2.2**: Create model loading service using joblib/pickle (native Python)
- [x] **Task 2.3**: Implement prediction function with direct model access
- [x] **Task 2.4**: Test model loading and prediction functionality

### Phase 3: Data Services ✅
- [x] **Task 3.1**: Create airport data service using pandas for CSV parsing
- [x] **Task 3.2**: Load and parse `airports.csv` file with pandas
- [x] **Task 3.3**: Implement airport list with IDs and names
- [x] **Task 3.4**: Sort airports alphabetically by name
- [x] **Task 3.5**: Create Pydantic models for request/response validation

### Phase 4: API Endpoints ✅
- [x] **Task 4.1**: Set up main FastAPI application (`app.py`)
- [x] **Task 4.2**: Configure CORS middleware for frontend integration
- [x] **Task 4.3**: Implement `/airports` endpoint
  - Method: GET
  - Response: `{ airports: [{ id, name }] }`
  - Sort: Alphabetical by name
- [x] **Task 4.4**: Implement `/predict` endpoint
  - Method: POST with JSON body
  - Input: `{ dayOfWeek: int, airportId: int }`
  - Response: `{ delayProbability: float, confidence: float }`
- [x] **Task 4.5**: Add Pydantic models for automatic input validation and documentation

### Phase 5: Server Configuration ✅
- [x] **Task 5.1**: Configure uvicorn server to listen on port 8080
- [x] **Task 5.2**: Add health check endpoint (`/health`)
- [x] **Task 5.3**: Implement graceful shutdown handling
- [x] **Task 5.4**: Add request logging middleware
- [x] **Task 5.5**: Configure automatic API documentation (OpenAPI/Swagger)

### Phase 6: Testing & Validation ❌
- [ ] **Task 6.1**: Test airports endpoint returns valid JSON
- [ ] **Task 6.2**: Test prediction endpoint with sample data
- [ ] **Task 6.3**: Validate day-of-week range (1-7 for Monday-Sunday)
- [ ] **Task 6.4**: Validate airport ID exists in dataset
- [ ] **Task 6.5**: Test error responses for invalid inputs
- [ ] **Task 6.6**: Verify CORS headers for frontend calls

### Phase 7: Documentation & Deployment ❌
- [ ] **Task 7.1**: Add API documentation comments
- [ ] **Task 7.2**: Create development startup instructions
- [ ] **Task 7.3**: Test port forwarding in dev container
- [ ] **Task 7.4**: Verify integration with existing models
- [ ] **Task 7.5**: Document API endpoints and expected responses

## Expected Directory Structure
```
server/
├── app.py                  # Main FastAPI application
├── requirements.txt        # Python dependencies
├── models/
│   ├── __init__.py
│   ├── prediction.py       # Model loading and prediction logic
│   └── schemas.py          # Pydantic models for request/response
├── services/
│   ├── __init__.py
│   ├── airport_service.py  # Airport data management
│   └── model_service.py    # ML model wrapper
├── routers/
│   ├── __init__.py
│   ├── airports.py         # Airport endpoints
│   └── predictions.py     # Prediction endpoints
└── utils/
    ├── __init__.py
    └── validators.py       # Input validation utilities
```

## API Endpoints Specification

### GET /airports
**Purpose**: Return list of all airports sorted alphabetically
**Response Format**:
```json
{
  "airports": [
    { "id": 10397, "name": "Hartsfield-Jackson Atlanta International" },
    { "id": 12892, "name": "Los Angeles International" }
  ]
}
```

### POST /predict
**Purpose**: Predict flight delay probability
**Request Body**:
```json
{
  "dayOfWeek": 1,     // 1-7 (Monday=1, Sunday=7)
  "airportId": 10397  // Valid airport ID from airports list
}
```
**Response Format**:
```json
{
  "delayProbability": 0.23,    // Probability of >15min delay (0-1)
  "confidence": 0.85,          // Model confidence (0-1)
  "airportId": 10397,
  "dayOfWeek": 1
}
```

## Integration Points
- **Models**: Load from `/model.pkl` (contains complete model with metadata)
- **Data**: Extract airport information from `/airports.csv`
- **Frontend**: CORS-enabled API calls from client application
- **Dev Container**: Port 8080 forwarding configuration

## Model Integration Strategy
Since both the model and API are now in Python, integration is straightforward:

### Direct Python Integration (Recommended)
- Load models directly using `joblib.load()` or `pickle.load()`
- Use pandas for CSV data processing
- Native Python environment - no inter-process communication needed
- Fast inference with direct memory access

### Model Loading Example
```python
import joblib
import pandas as pd
from fastapi import FastAPI

# Load model and data at startup
model = joblib.load("../model.pkl")
airports_df = pd.read_csv("../airports.csv")

# Direct prediction function
def predict_delay(day_of_week: int, airport_id: int) -> dict:
    # Transform inputs and predict
    prediction = model.predict([[day_of_week, airport_id]])
    confidence = model.predict_proba([[day_of_week, airport_id]]).max()
    return {
        "delayProbability": float(prediction[0]),
        "confidence": float(confidence)
    }
```

## Success Criteria
- [ ] ✅ FastAPI server runs on port 8080 with uvicorn
- [ ] ✅ `/airports` endpoint returns sorted airport list as JSON
- [ ] ✅ `/predict` endpoint accepts JSON body and returns delay prediction
- [ ] ✅ Direct model integration with joblib/pickle loading
- [ ] ✅ Pydantic validation prevents invalid requests
- [ ] ✅ CORS middleware configured for frontend integration
- [ ] ✅ Automatic API documentation available at `/docs`
- [ ] ✅ Error handling provides meaningful HTTP responses

## Notes
- Model expects: DayOfWeek (1-7) and OriginAirport_Model (1-70)
- Airport CSV contains mapping between actual airport IDs and model IDs
- FastAPI provides automatic API documentation at `/docs` and `/redoc`
- Use Pydantic models for request/response validation and documentation
- Test with sample data: Monday (1) + Airport ID 10 should work
- uvicorn will be used as the ASGI server: `uvicorn app:app --host 0.0.0.0 --port 8080`

## Progress Tracking
**Overall Progress**: 71% (5/7 phases completed)

**Last Updated**: August 28, 2025
**Status**: Phases 1-5 completed - Ready to begin Phase 6
