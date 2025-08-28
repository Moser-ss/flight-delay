# Flight Delay Prediction API Documentation

## Overview
The Flight Delay Prediction API provides machine learning-powered predictions for flight delays based on day of the week and departure airport. Built with FastAPI, it offers high-performance endpoints with automatic OpenAPI documentation and validation.

## Base URL
- **Development**: `http://localhost:8080`
- **Production**: Configure based on deployment environment

## API Endpoints

### 1. Root Endpoint
**GET /**
```http
GET / HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "message": "Flight Delay Prediction API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### 2. Health Check
**GET /health**
```http
GET /health HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "initialized": true
  }
}
```

### 3. Get All Airports
**GET /airports**

Returns all available airports sorted alphabetically by name.

```http
GET /airports HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "airports": [
    {
      "id": 1,
      "name": "Albuquerque International Sunport",
      "code": "ABQ",
      "city": "Albuquerque",
      "state": "NM"
    },
    {
      "id": 2,
      "name": "Hartsfield-Jackson Atlanta International Airport",
      "code": "ATL",
      "city": "Atlanta",
      "state": "GA"
    }
    // ... additional airports
  ],
  "total": 70
}
```

### 4. Get Airport by ID
**GET /airports/{id}**

Returns details for a specific airport by ID.

```http
GET /airports/2 HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "id": 2,
  "name": "Hartsfield-Jackson Atlanta International Airport",
  "code": "ATL",
  "city": "Atlanta",
  "state": "GA"
}
```

**Error Response (404):**
```json
{
  "detail": "Airport not found"
}
```

### 5. Predict Flight Delay
**POST /predict**

Predicts the likelihood of flight delays based on day of week and departure airport.

```http
POST /predict HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "day_of_week": 1,
  "airport_id": 2
}
```

**Request Body Schema:**
```json
{
  "day_of_week": "integer (1-7, where 1=Monday, 7=Sunday)",
  "airport_id": "integer (valid airport ID from /airports endpoint)"
}
```

**Response:**
```json
{
  "prediction": {
    "delayed": 0.244,
    "on_time": 0.756
  },
  "confidence": 0.756,
  "model_info": {
    "version": "1.0",
    "features": ["day_of_week", "airport_id"]
  },
  "airport": {
    "id": 2,
    "name": "Hartsfield-Jackson Atlanta International Airport",
    "code": "ATL",
    "city": "Atlanta",
    "state": "GA"
  },
  "request_details": {
    "day_of_week": 1,
    "day_name": "Monday"
  }
}
```

**Validation Error Response (422):**
```json
{
  "detail": [
    {
      "type": "greater_equal",
      "loc": ["body", "day_of_week"],
      "msg": "Input should be greater than or equal to 1",
      "input": 0
    }
  ]
}
```

**Airport Not Found Error (404):**
```json
{
  "detail": "Airport not found"
}
```

### 6. Prediction Service Status
**GET /predict/status**

Returns the status of the prediction service and model information.

```http
GET /predict/status HTTP/1.1
Host: localhost:8080
```

**Response:**
```json
{
  "status": "ready",
  "model_loaded": true,
  "airports_loaded": 70,
  "model_info": {
    "version": "1.0",
    "features": ["day_of_week", "airport_id"]
  }
}
```

## Data Models

### Airport
```json
{
  "id": "integer - Unique airport identifier",
  "name": "string - Full airport name",
  "code": "string - IATA airport code (3 letters)",
  "city": "string - City name",
  "state": "string - State abbreviation"
}
```

### Prediction Request
```json
{
  "day_of_week": "integer - Day of week (1=Monday, 2=Tuesday, ..., 7=Sunday)",
  "airport_id": "integer - Valid airport ID from airports endpoint"
}
```

### Prediction Response
```json
{
  "prediction": {
    "delayed": "number - Probability of delay (0.0-1.0)",
    "on_time": "number - Probability of on-time (0.0-1.0)"
  },
  "confidence": "number - Model confidence (max probability)",
  "model_info": {
    "version": "string - Model version",
    "features": "array - List of features used"
  },
  "airport": "Airport object with full airport details",
  "request_details": {
    "day_of_week": "integer - Original day of week",
    "day_name": "string - Human-readable day name"
  }
}
```

## HTTP Status Codes

| Status Code | Description | Usage |
|-------------|-------------|-------|
| 200 | OK | Successful request |
| 404 | Not Found | Airport ID not found |
| 422 | Unprocessable Entity | Validation error (invalid input) |
| 500 | Internal Server Error | Server error |

## Day of Week Reference

| Value | Day |
|-------|-----|
| 1 | Monday |
| 2 | Tuesday |
| 3 | Wednesday |
| 4 | Thursday |
| 5 | Friday |
| 6 | Saturday |
| 7 | Sunday |

## Example Usage Scenarios

### 1. Get All Airports and Predict for Atlanta on Monday
```bash
# Get all airports
curl -X GET "http://localhost:8080/airports"

# Find Atlanta (ATL) - ID: 2
# Predict for Monday (day 1)
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d '{"day_of_week": 1, "airport_id": 2}'
```

### 2. Check Service Health Before Making Predictions
```bash
# Check overall health
curl -X GET "http://localhost:8080/health"

# Check prediction service status
curl -X GET "http://localhost:8080/predict/status"

# Make prediction if service is ready
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d '{"day_of_week": 5, "airport_id": 10}'
```

### 3. Validate Airport Before Prediction
```bash
# Check if airport exists
curl -X GET "http://localhost:8080/airports/25"

# If successful, make prediction
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d '{"day_of_week": 3, "airport_id": 25}'
```

## Error Handling

### Common Validation Errors
1. **Invalid day_of_week**: Must be 1-7
2. **Invalid airport_id**: Must exist in airports dataset
3. **Missing fields**: Both day_of_week and airport_id are required
4. **Wrong data types**: Fields must be integers

### Error Response Format
All errors return a consistent format:
```json
{
  "detail": "Error description or validation details array"
}
```

## CORS Support
The API includes CORS support for frontend applications:
- **Allow Origins**: All origins (`*`)
- **Allow Methods**: GET, POST, OPTIONS
- **Allow Headers**: All headers

## Rate Limiting
Currently no rate limiting is implemented. Consider adding rate limiting for production deployments.

## Interactive Documentation

### Swagger UI
Access interactive API documentation at:
- **URL**: `http://localhost:8080/docs`
- **Features**: Try endpoints directly, view schemas, see examples

### ReDoc
Access alternative documentation at:
- **URL**: `http://localhost:8080/redoc`
- **Features**: Clean documentation view, downloadable

### OpenAPI Schema
Access the raw OpenAPI schema at:
- **URL**: `http://localhost:8080/openapi.json`
- **Usage**: Generate client libraries, import into API tools

## Performance Characteristics
- **Airports endpoint**: < 50ms average response time
- **Prediction endpoint**: < 100ms average response time
- **Health endpoint**: < 10ms average response time
- **Concurrent requests**: Supports multiple simultaneous requests

## Security Considerations
1. **Input Validation**: All inputs are validated using Pydantic schemas
2. **Error Handling**: Graceful error responses without exposing internals
3. **CORS**: Configure appropriately for production (don't use `*` for origins)
4. **Rate Limiting**: Consider implementing for production use
5. **Authentication**: Add authentication/authorization as needed

## Client Integration Examples

### JavaScript/TypeScript
```javascript
// Get all airports
const airports = await fetch('http://localhost:8080/airports')
  .then(res => res.json());

// Make prediction
const prediction = await fetch('http://localhost:8080/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ day_of_week: 1, airport_id: 2 })
}).then(res => res.json());
```

### Python
```python
import httpx

# Get all airports
response = httpx.get('http://localhost:8080/airports')
airports = response.json()

# Make prediction
response = httpx.post('http://localhost:8080/predict', 
  json={'day_of_week': 1, 'airport_id': 2})
prediction = response.json()
```

### cURL
```bash
# Health check
curl http://localhost:8080/health

# Get airports
curl http://localhost:8080/airports

# Make prediction
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"day_of_week": 1, "airport_id": 2}'
```

## Troubleshooting

### Common Issues
1. **Server not starting**: Check Python environment and dependencies
2. **Model not loading**: Verify model files exist in `/server/models/`
3. **Airport data missing**: Ensure `airports.csv` is in `/server/data/`
4. **CORS errors**: Check CORS configuration for your frontend domain
5. **Validation errors**: Ensure request data matches schema requirements

### Debug Information
- **Logs**: Check terminal output for error messages
- **Health endpoint**: Use `/health` to verify service status
- **Prediction status**: Use `/predict/status` to check model loading
- **API docs**: Use `/docs` to test endpoints interactively

This API is designed to be reliable, fast, and easy to integrate into frontend applications or other services requiring flight delay predictions.
