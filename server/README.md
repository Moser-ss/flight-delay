# Flight Delay Prediction API - Setup & Development Guide

## Quick Start

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Git (for version control)

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd flight-delay

# Navigate to server directory
cd server

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Server
```bash
# From the /server directory
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

### 3. Verify Installation
```bash
# Test health endpoint
curl http://localhost:8080/health

# View interactive API docs
open http://localhost:8080/docs
```

## Project Structure

```
flight-delay/
├── server/                          # API server code
│   ├── app.py                      # Main FastAPI application
│   ├── requirements.txt            # Python dependencies
│   ├── pyproject.toml             # pytest configuration
│   ├── data/
│   │   └── airports.csv           # Airport data (70 airports)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── prediction.py          # Prediction logic
│   │   ├── schemas.py             # Pydantic data models
│   │   ├── model.pkl              # Trained ML model (primary)
│   │   ├── model.joblib           # Alternative model format
│   │   └── model_object.pkl       # Model metadata
│   ├── services/
│   │   ├── __init__.py
│   │   ├── airport_service.py     # Airport data management
│   │   └── model_service.py       # ML model operations
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── airports.py            # Airport endpoints
│   │   └── predictions.py         # Prediction endpoints
│   ├── utils/
│   │   └── __init__.py
│   ├── tests/                     # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py           # Test configuration
│   │   ├── test_main.py          # Main endpoint tests
│   │   ├── test_airports.py      # Airport endpoint tests
│   │   ├── test_predictions.py   # Prediction endpoint tests
│   │   └── test_integration.py   # Integration tests
│   └── docs/
│       └── API_DOCUMENTATION.md   # Complete API documentation
├── .github/
│   └── task-plan/                 # Project planning and summaries
└── data/                          # Original dataset (if available)
```

## Development Environment Setup

### Option 1: Local Development
```bash
# 1. Create virtual environment
python -m venv flight-delay-env
source flight-delay-env/bin/activate  # On Windows: flight-delay-env\Scripts\activate

# 2. Install dependencies
cd server
pip install -r requirements.txt

# 3. Install development dependencies (optional)
pip install pytest httpx pytest-asyncio  # For testing

# 4. Start development server
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

### Option 2: Using Dev Container (if available)
```bash
# Open in VS Code with Dev Container extension
# Container will automatically install Python and dependencies
cd server
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

## Development Commands

### Starting the Server
```bash
# Basic startup
python -m uvicorn app:app --host 0.0.0.0 --port 8080

# Development mode (auto-reload)
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload

# Custom port
python -m uvicorn app:app --host 0.0.0.0 --port 3000 --reload

# Enable debugging logs
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload --log-level debug
```

### Running Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_predictions.py

# Run with coverage (requires pytest-cov)
pip install pytest-cov
pytest --cov=. --cov-report=html
```

### Development Utilities
```bash
# Check Python version
python --version

# List installed packages
pip list

# Check for dependency issues
pip check

# Format code (requires black)
pip install black
black .

# Lint code (requires flake8)
pip install flake8
flake8 .
```

## Environment Variables

### Optional Configuration
```bash
# Set custom port
export PORT=3000

# Set debug mode
export DEBUG=true

# Set model path (if different)
export MODEL_PATH="/path/to/model.pkl"

# Set airport data path (if different)
export AIRPORT_DATA_PATH="/path/to/airports.csv"
```

### Using .env File (optional)
Create a `.env` file in the `/server` directory:
```env
PORT=8080
DEBUG=false
MODEL_PATH=models/model.pkl
AIRPORT_DATA_PATH=data/airports.csv
```

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with API info |
| GET | `/health` | Health check |
| GET | `/airports` | Get all airports |
| GET | `/airports/{id}` | Get specific airport |
| POST | `/predict` | Predict flight delay |
| GET | `/predict/status` | Prediction service status |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |
| GET | `/openapi.json` | OpenAPI schema |

## Testing Guide

### Manual Testing
```bash
# 1. Start server
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload

# 2. Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/airports
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"day_of_week": 1, "airport_id": 2}'
```

### Automated Testing
```bash
# Install test dependencies
pip install pytest httpx pytest-asyncio

# Run test suite
pytest tests/ -v

# Test specific functionality
pytest tests/test_predictions.py::TestPredictionEndpoints::test_predict_valid_request -v
```

### Interactive Testing
1. **Swagger UI**: Open `http://localhost:8080/docs`
2. **ReDoc**: Open `http://localhost:8080/redoc`
3. **Use the "Try it out" feature to test endpoints**

## Troubleshooting

### Common Issues

#### 1. Server Won't Start
```bash
# Check if port is already in use
lsof -i :8080  # On Linux/Mac
netstat -ano | findstr :8080  # On Windows

# Try different port
python -m uvicorn app:app --host 0.0.0.0 --port 3000 --reload
```

#### 2. Module Import Errors
```bash
# Ensure you're in the server directory
cd server

# Check Python path
python -c "import sys; print(sys.path)"

# Install missing dependencies
pip install -r requirements.txt
```

#### 3. Model Loading Issues
```bash
# Check if model files exist
ls -la models/

# Verify file permissions
chmod 644 models/*.pkl models/*.joblib

# Check Python version compatibility
python --version  # Should be 3.11+
```

#### 4. Airport Data Issues
```bash
# Check if airports.csv exists
ls -la data/airports.csv

# Verify file content
head data/airports.csv
wc -l data/airports.csv  # Should show 71 lines (70 airports + header)
```

#### 5. CORS Errors (Frontend Development)
```bash
# CORS is configured for all origins by default
# For production, update app.py CORS settings:
allow_origins=["http://localhost:3000", "https://yourdomain.com"]
```

### Debug Mode
```bash
# Start with debug logging
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload --log-level debug

# Check service status
curl http://localhost:8080/health
curl http://localhost:8080/predict/status
```

### Performance Monitoring
```bash
# Monitor response times
time curl http://localhost:8080/airports
time curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"day_of_week": 1, "airport_id": 2}'
```

## Development Workflow

### 1. Making Changes
```bash
# 1. Create feature branch
git checkout -b feature/new-endpoint

# 2. Make changes to code
# 3. Test changes
pytest tests/

# 4. Start server and test manually
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload

# 5. Commit changes
git add .
git commit -m "Add new endpoint"
```

### 2. Adding New Endpoints
1. **Create router**: Add new file in `/routers/`
2. **Define schemas**: Update `/models/schemas.py`
3. **Add logic**: Implement in appropriate service
4. **Include router**: Add to `app.py`
5. **Write tests**: Add test file in `/tests/`
6. **Test manually**: Use Swagger UI or curl

### 3. Code Style Guidelines
- **Follow PEP 8**: Use consistent Python styling
- **Type hints**: Add type annotations where helpful
- **Documentation**: Add docstrings for functions and classes
- **Error handling**: Use appropriate HTTP status codes
- **Testing**: Write tests for new functionality

## VS Code Development Setup

### Recommended Extensions
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.black-formatter",
    "ms-vscode.vscode-json",
    "humao.rest-client"
  ]
}
```

### VS Code Settings
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true
}
```

### REST Client Testing (VS Code)
Create `test-requests.http`:
```http
### Health Check
GET http://localhost:8080/health

### Get All Airports
GET http://localhost:8080/airports

### Predict Flight Delay
POST http://localhost:8080/predict
Content-Type: application/json

{
  "day_of_week": 1,
  "airport_id": 2
}
```

## Next Steps
1. **Production Deployment**: See `DEPLOYMENT_GUIDE.md`
2. **API Documentation**: See `docs/API_DOCUMENTATION.md`
3. **Testing Guide**: Run `pytest tests/ -v`
4. **Frontend Integration**: Use CORS-enabled endpoints

## Support
For issues or questions:
1. Check the troubleshooting section above
2. Review test files for usage examples
3. Use interactive docs at `/docs`
4. Check server logs for error details

Happy coding! 🚀
