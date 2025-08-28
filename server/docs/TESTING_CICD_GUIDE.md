# Testing & CI/CD Integration Guide

## Testing Overview
The Flight Delay Prediction API includes a comprehensive test suite with 30 test cases covering all endpoints, validation, error handling, and integration scenarios. This guide covers testing procedures and CI/CD integration.

## Test Suite Structure

### Test Organization
```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                # Test configuration and fixtures
├── test_main.py               # Main application endpoints (6 tests)
├── test_airports.py           # Airport endpoints testing (7 tests)
├── test_predictions.py        # Prediction endpoints testing (8 tests)
└── test_integration.py        # End-to-end integration tests (9 tests)
```

### Test Categories

#### 1. Unit Tests
- **Model Service**: ML model loading and prediction logic
- **Airport Service**: Airport data management and lookup
- **Schema Validation**: Pydantic model validation
- **Utility Functions**: Helper functions and utilities

#### 2. Integration Tests
- **Endpoint Testing**: All API endpoints with various inputs
- **Error Handling**: Validation errors, 404s, and edge cases
- **Data Consistency**: Airport data consistency across endpoints
- **Service Integration**: Model + airport data integration

#### 3. Performance Tests
- **Response Time**: Endpoint response time validation
- **Load Testing**: Multiple concurrent requests
- **Memory Usage**: Service memory consumption
- **Throughput**: Requests per second capacity

## Running Tests

### Local Testing

#### Basic Test Execution
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_predictions.py

# Run specific test
pytest tests/test_predictions.py::TestPredictionEndpoints::test_predict_valid_request -v
```

#### Advanced Test Options
```bash
# Run tests with coverage
pip install pytest-cov
pytest --cov=. --cov-report=html --cov-report=term

# Run tests in parallel
pip install pytest-xdist
pytest -n auto

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "test_predict"
```

#### Test Output Examples
```bash
# Successful test run
pytest tests/ -v
================================ test session starts ================================
collected 30 items

tests/test_main.py::TestMainEndpoints::test_root_endpoint PASSED           [  3%]
tests/test_main.py::TestMainEndpoints::test_health_endpoint PASSED         [  6%]
# ... (all tests pass)
tests/test_integration.py::TestIntegration::test_performance_load PASSED   [100%]

========================= 30 passed, 135 warnings in 1.42s =========================
```

### Docker Testing
```bash
# Build test image
docker build -t flight-delay-api:test --target test .

# Run tests in container
docker run --rm flight-delay-api:test pytest tests/ -v

# Run with coverage
docker run --rm -v $(pwd)/coverage:/app/coverage flight-delay-api:test \
  pytest --cov=. --cov-report=html:/app/coverage
```

### Test Configuration

#### pytest.ini Configuration
```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]
```

#### Test Environment Variables
```bash
# Test-specific environment
export TEST_ENV=true
export LOG_LEVEL=error
export DISABLE_METRICS=true
```

## CI/CD Integration

### GitHub Actions

#### Basic CI Workflow
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-

    - name: Install dependencies
      working-directory: ./server
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio httpx

    - name: Run tests with coverage
      working-directory: ./server
      run: |
        pytest tests/ --cov=. --cov-report=xml --cov-report=html -v

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./server/coverage.xml
        flags: unittests
        name: codecov-umbrella

  security:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Security audit
      working-directory: ./server
      run: |
        pip install safety bandit
        safety check -r requirements.txt
        bandit -r . -x tests/

  docker:
    needs: [test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Build Docker image
      working-directory: ./server
      run: |
        docker build -t flight-delay-api:latest .

    - name: Test Docker image
      run: |
        docker run -d --name test-api -p 8080:8080 flight-delay-api:latest
        sleep 10
        curl -f http://localhost:8080/health || exit 1
        docker stop test-api && docker rm test-api

    - name: Login to Docker Hub
      if: github.event_name == 'push'
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}

    - name: Push to Docker Hub
      if: github.event_name == 'push'
      run: |
        docker tag flight-delay-api:latest yourusername/flight-delay-api:latest
        docker tag flight-delay-api:latest yourusername/flight-delay-api:${{ github.sha }}
        docker push yourusername/flight-delay-api:latest
        docker push yourusername/flight-delay-api:${{ github.sha }}

  deploy:
    needs: docker
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to staging
      run: |
        # Add deployment logic here
        echo "Deploying to staging environment"
        
    - name: Run smoke tests
      run: |
        # Add smoke tests here
        curl -f https://staging-api.yourdomain.com/health
        
    - name: Deploy to production
      if: success()
      run: |
        # Add production deployment logic
        echo "Deploying to production environment"
```

#### Advanced CI Features
```yaml
# .github/workflows/advanced-ci.yml
name: Advanced CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      working-directory: ./server
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio httpx pytest-benchmark

    - name: Run unit tests
      working-directory: ./server
      run: pytest tests/test_*.py -v --cov=. --cov-report=xml -m "not integration"

    - name: Run integration tests
      working-directory: ./server
      run: pytest tests/test_integration.py -v -m integration

    - name: Run performance tests
      working-directory: ./server
      run: pytest tests/ --benchmark-only --benchmark-json=benchmark.json

    - name: Security scan
      working-directory: ./server
      run: |
        pip install bandit safety
        bandit -r . -f json -o bandit-report.json || true
        safety check --json --output safety-report.json || true

    - name: Generate test report
      if: always()
      uses: dorny/test-reporter@v1
      with:
        name: Test Results
        path: 'server/test-results.xml'
        reporter: java-junit

  code-quality:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install linting tools
      run: |
        pip install black flake8 isort mypy

    - name: Code formatting check
      working-directory: ./server
      run: |
        black --check .
        isort --check-only .

    - name: Linting
      working-directory: ./server
      run: flake8 .

    - name: Type checking
      working-directory: ./server
      run: mypy . --ignore-missing-imports
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - test
  - security
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

test:
  stage: test
  image: python:3.11
  services:
    - redis:alpine
  cache:
    paths:
      - ~/.cache/pip/
  before_script:
    - cd server
    - pip install -r requirements.txt
    - pip install pytest pytest-cov pytest-asyncio httpx
  script:
    - pytest tests/ --cov=. --cov-report=xml --cov-report=html -v
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: server/coverage.xml
    paths:
      - server/htmlcov/
    expire_in: 1 week
  coverage: '/TOTAL.*\s+(\d+%)$/'

security:
  stage: security
  image: python:3.11
  before_script:
    - cd server
    - pip install safety bandit
  script:
    - safety check -r requirements.txt
    - bandit -r . -x tests/ -f json -o bandit-report.json
  artifacts:
    reports:
      sast: server/bandit-report.json
    expire_in: 1 week
  allow_failure: true

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - cd server
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:latest
  only:
    - main

deploy:staging:
  stage: deploy
  script:
    - echo "Deploying to staging"
    # Add staging deployment script
  environment:
    name: staging
    url: https://staging-api.yourdomain.com
  only:
    - main

deploy:production:
  stage: deploy
  script:
    - echo "Deploying to production"
    # Add production deployment script
  environment:
    name: production
    url: https://api.yourdomain.com
  when: manual
  only:
    - main
```

### Jenkins Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'flight-delay-api'
        REGISTRY = 'your-registry.com'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Test') {
            steps {
                dir('server') {
                    sh '''
                        python -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                        pip install pytest pytest-cov pytest-asyncio httpx
                        pytest tests/ --cov=. --cov-report=xml --junitxml=test-results.xml -v
                    '''
                }
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'server/test-results.xml'
                    publishCoverage adapters: [coberturaAdapter('server/coverage.xml')], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                dir('server') {
                    sh '''
                        . venv/bin/activate
                        pip install safety bandit
                        safety check -r requirements.txt || true
                        bandit -r . -x tests/ -f json -o bandit-report.json || true
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'server/bandit-report.json', allowEmptyArchive: true
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                branch 'main'
            }
            steps {
                dir('server') {
                    script {
                        def image = docker.build("${DOCKER_IMAGE}:${env.BUILD_ID}")
                        docker.withRegistry("https://${REGISTRY}", 'registry-credentials') {
                            image.push()
                            image.push('latest')
                        }
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Add staging deployment logic
                    sh 'echo "Deploying to staging"'
                }
            }
        }
        
        stage('Production Deployment') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
                script {
                    // Add production deployment logic
                    sh 'echo "Deploying to production"'
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        success {
            slackSend channel: '#deployments', 
                     color: 'good', 
                     message: "✅ Flight Delay API - Build ${env.BUILD_NUMBER} succeeded"
        }
        failure {
            slackSend channel: '#deployments', 
                     color: 'danger', 
                     message: "❌ Flight Delay API - Build ${env.BUILD_NUMBER} failed"
        }
    }
}
```

## Test Data Management

### Test Fixtures
```python
# tests/conftest.py - Test data fixtures
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def sample_airports():
    """Sample airport data for testing"""
    return [
        {"id": 1, "name": "Test Airport 1", "code": "TST", "city": "Test City", "state": "TC"},
        {"id": 2, "name": "Test Airport 2", "code": "TS2", "city": "Test City 2", "state": "T2"}
    ]

@pytest.fixture
def sample_prediction_requests():
    """Sample prediction requests for testing"""
    return [
        {"day_of_week": 1, "airport_id": 1},
        {"day_of_week": 7, "airport_id": 2},
        {"day_of_week": 3, "airport_id": 1}
    ]

@pytest.fixture
def invalid_requests():
    """Invalid request data for testing validation"""
    return [
        {"day_of_week": 0, "airport_id": 1},  # Invalid day
        {"day_of_week": 8, "airport_id": 1},  # Invalid day
        {"day_of_week": 1, "airport_id": 999}  # Invalid airport
    ]
```

### Mock Data
```python
# tests/mocks.py - Mock services for testing
class MockModelService:
    def predict(self, day_of_week: int, airport_id: int):
        return {
            "delayed": 0.3,
            "on_time": 0.7
        }
    
    def is_loaded(self):
        return True

class MockAirportService:
    def get_airport_by_id(self, airport_id: int):
        if airport_id == 999:
            return None
        return {
            "id": airport_id,
            "name": f"Test Airport {airport_id}",
            "code": f"T{airport_id:02d}",
            "city": "Test City",
            "state": "TC"
        }
```

## Performance Testing

### Load Testing with Locust
```python
# tests/load_test.py
from locust import HttpUser, task, between

class APILoadTest(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8080"
    
    def on_start(self):
        # Get list of airports for testing
        response = self.client.get("/airports")
        self.airports = response.json()["airports"]
    
    @task(3)
    def predict_delay(self):
        airport = self.airports[0]  # Use first airport
        self.client.post("/predict", json={
            "day_of_week": 1,
            "airport_id": airport["id"]
        })
    
    @task(1)
    def get_airports(self):
        self.client.get("/airports")
    
    @task(1)
    def health_check(self):
        self.client.get("/health")

# Run: locust -f tests/load_test.py --host=http://localhost:8080
```

### API Testing with Newman (Postman)
```json
{
  "info": {
    "name": "Flight Delay API Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{baseUrl}}/health"
      },
      "test": "pm.test('Health check returns 200', function () { pm.response.to.have.status(200); });"
    },
    {
      "name": "Get Airports",
      "request": {
        "method": "GET",
        "url": "{{baseUrl}}/airports"
      },
      "test": "pm.test('Returns airport list', function () { pm.expect(pm.response.json().airports).to.be.an('array'); });"
    },
    {
      "name": "Predict Delay",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/predict",
        "body": {
          "mode": "raw",
          "raw": "{\"day_of_week\": 1, \"airport_id\": 2}"
        }
      },
      "test": "pm.test('Prediction successful', function () { pm.response.to.have.status(200); });"
    }
  ]
}
```

## Quality Gates

### Test Coverage Requirements
```bash
# Minimum coverage thresholds
pytest --cov=. --cov-fail-under=80  # 80% minimum coverage

# Coverage by component
--cov-report=term-missing  # Show missing lines
--cov-report=html          # Generate HTML report
```

### Performance Thresholds
```python
# tests/test_performance.py
import pytest
import time

@pytest.mark.performance
def test_prediction_response_time(client, sample_request):
    start_time = time.time()
    response = client.post("/predict", json=sample_request)
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 0.1  # 100ms threshold

@pytest.mark.performance
def test_concurrent_requests(client):
    import asyncio
    import httpx
    
    async def make_request():
        async with httpx.AsyncClient() as aclient:
            response = await aclient.post(
                "http://localhost:8080/predict",
                json={"day_of_week": 1, "airport_id": 2}
            )
            return response.status_code
    
    # Test 10 concurrent requests
    loop = asyncio.get_event_loop()
    tasks = [make_request() for _ in range(10)]
    results = loop.run_until_complete(asyncio.gather(*tasks))
    
    assert all(status == 200 for status in results)
```

## Continuous Monitoring

### Application Metrics
```python
# utils/monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('api_active_connections', 'Active connections')
MODEL_PREDICTIONS = Counter('model_predictions_total', 'Total model predictions', ['airport'])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response
```

### Health Monitoring
```bash
# Kubernetes health checks
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

This comprehensive testing and CI/CD guide ensures your Flight Delay Prediction API maintains high quality, security, and reliability throughout its development lifecycle.
