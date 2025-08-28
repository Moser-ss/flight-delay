# Production Deployment Guide - Flight Delay Prediction API

## Overview
This guide covers deploying the Flight Delay Prediction API to production environments. The API is built with FastAPI and designed to be containerized and cloud-ready.

## Deployment Options

### 1. Docker Deployment (Recommended)

#### Create Dockerfile
```dockerfile
# /server/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Start application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### Build and Run Docker Image
```bash
# Build image
cd server
docker build -t flight-delay-api:latest .

# Run container
docker run -d \
  --name flight-delay-api \
  -p 8080:8080 \
  --restart unless-stopped \
  flight-delay-api:latest

# Test deployment
curl http://localhost:8080/health
```

#### Docker Compose (for local production testing)
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: ./server
    ports:
      - "8080:8080"
    environment:
      - ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl:ro
    depends_on:
      - api
    restart: unless-stopped
```

### 2. Cloud Platform Deployments

#### A. AWS Deployment

##### Using AWS ECS (Fargate)
```bash
# 1. Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker build -t flight-delay-api .
docker tag flight-delay-api:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/flight-delay-api:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/flight-delay-api:latest

# 2. Create ECS task definition
# 3. Create ECS service
# 4. Configure Application Load Balancer
```

##### ECS Task Definition Example
```json
{
  "family": "flight-delay-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "flight-delay-api",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/flight-delay-api:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/flight-delay-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

##### Using AWS Lambda (Serverless)
```python
# lambda_handler.py
from mangum import Mangum
from app import app

handler = Mangum(app)
```

```bash
# Install dependencies
pip install mangum

# Package for Lambda
zip -r flight-delay-api.zip . -x "tests/*" "*.pyc" "__pycache__/*"
```

#### B. Google Cloud Platform

##### Using Cloud Run
```bash
# 1. Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/flight-delay-api
gcloud run deploy flight-delay-api \
  --image gcr.io/PROJECT_ID/flight-delay-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1
```

##### Cloud Run Service Configuration
```yaml
# service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: flight-delay-api
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "100"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/flight-delay-api
        ports:
        - containerPort: 8080
        resources:
          limits:
            cpu: 1000m
            memory: 1Gi
        env:
        - name: ENV
          value: production
```

#### C. Microsoft Azure

##### Using Azure Container Instances
```bash
# Create resource group
az group create --name flight-delay-rg --location eastus

# Deploy container
az container create \
  --resource-group flight-delay-rg \
  --name flight-delay-api \
  --image flight-delay-api:latest \
  --dns-name-label flight-delay-api \
  --ports 8080 \
  --environment-variables ENV=production
```

##### Using Azure App Service
```bash
# Create App Service plan
az appservice plan create \
  --name flight-delay-plan \
  --resource-group flight-delay-rg \
  --sku B1 \
  --is-linux

# Create web app
az webapp create \
  --resource-group flight-delay-rg \
  --plan flight-delay-plan \
  --name flight-delay-api \
  --deployment-container-image-name flight-delay-api:latest
```

### 3. Traditional Server Deployment

#### Using systemd (Linux)
```ini
# /etc/systemd/system/flight-delay-api.service
[Unit]
Description=Flight Delay Prediction API
After=network.target

[Service]
Type=exec
User=flight-delay
Group=flight-delay
WorkingDirectory=/opt/flight-delay-api
Environment=PATH=/opt/flight-delay-api/venv/bin
ExecStart=/opt/flight-delay-api/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Setup service
sudo systemctl daemon-reload
sudo systemctl enable flight-delay-api
sudo systemctl start flight-delay-api
sudo systemctl status flight-delay-api
```

## Production Configuration

### Environment Variables
```bash
# Production environment variables
export ENV=production
export PORT=8080
export HOST=0.0.0.0
export LOG_LEVEL=info
export WORKERS=4

# Security settings
export ALLOWED_ORIGINS="https://yourdomain.com,https://api.yourdomain.com"
export API_KEY_HEADER="X-API-Key"  # Optional: for API key authentication

# Monitoring
export ENABLE_METRICS=true
export METRICS_PORT=9090
```

### Security Hardening

#### 1. Update CORS Configuration
```python
# app.py - Production CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

#### 2. Add Rate Limiting
```python
# requirements.txt - Add slowapi
slowapi==0.1.9
redis==4.5.4

# app.py - Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@router.post("/predict")
@limiter.limit("10/minute")
async def predict_delay(request: Request, prediction_request: PredictionRequest):
    # ... existing code
```

#### 3. Add Authentication (Optional)
```python
# models/auth.py
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != os.getenv("API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return credentials.credentials

# Apply to protected endpoints
@router.post("/predict", dependencies=[Depends(verify_api_key)])
async def predict_delay(prediction_request: PredictionRequest):
    # ... existing code
```

### Reverse Proxy Configuration

#### Nginx Configuration
```nginx
# /etc/nginx/sites-available/flight-delay-api
upstream flight_delay_api {
    server 127.0.0.1:8080;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # API proxy
    location / {
        proxy_pass http://flight_delay_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check endpoint (bypass rate limiting)
    location /health {
        proxy_pass http://flight_delay_api/health;
        access_log off;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/m;
    limit_req zone=api burst=20 nodelay;
}
```

## Monitoring and Logging

### 1. Application Logging
```python
# utils/logging.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

# app.py
from utils.logging import setup_logging
logger = setup_logging()
```

### 2. Health Checks
```python
# Enhanced health check
@app.get("/health")
async def health_check():
    try:
        # Test model loading
        model_status = model_service.is_loaded()
        # Test airport data
        airport_count = len(airport_service.get_all_airports())
        
        return {
            "status": "healthy" if model_status and airport_count > 0 else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "model_loaded": model_status,
                "airports_loaded": airport_count,
                "uptime": time.time() - start_time
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}
```

### 3. Metrics Collection
```python
# requirements.txt - Add prometheus client
prometheus-client==0.16.0

# utils/metrics.py
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Performance Optimization

### 1. Production Uvicorn Settings
```bash
# Multi-worker deployment
uvicorn app:app \
  --host 0.0.0.0 \
  --port 8080 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-log \
  --log-level info
```

### 2. Gunicorn with Uvicorn Workers
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn app:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8080 \
  --access-logfile - \
  --error-logfile -
```

### 3. Model Caching
```python
# services/model_service.py - Add caching
from functools import lru_cache

class ModelService:
    @lru_cache(maxsize=1000)
    def predict_cached(self, day_of_week: int, airport_id: int):
        # Cache predictions for repeated requests
        return self.predict(day_of_week, airport_id)
```

## Backup and Recovery

### 1. Model Backup Strategy
```bash
# Backup models and data
tar -czf flight-delay-backup-$(date +%Y%m%d).tar.gz \
  models/ data/ requirements.txt

# Upload to cloud storage
aws s3 cp flight-delay-backup-*.tar.gz s3://your-backup-bucket/
```

### 2. Database Backup (if using database)
```bash
# Example for PostgreSQL
pg_dump -h hostname -U username flight_delay_db > backup.sql

# Restore
psql -h hostname -U username flight_delay_db < backup.sql
```

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (`pytest tests/`)
- [ ] Security review completed
- [ ] Performance testing completed
- [ ] SSL certificates configured
- [ ] Monitoring setup configured
- [ ] Backup strategy implemented
- [ ] Environment variables configured
- [ ] CORS settings updated for production
- [ ] Rate limiting configured (if needed)

### Deployment
- [ ] Build and test Docker image
- [ ] Deploy to staging environment
- [ ] Run integration tests
- [ ] Deploy to production
- [ ] Verify health checks
- [ ] Test all endpoints
- [ ] Monitor logs and metrics

### Post-Deployment
- [ ] Monitor application performance
- [ ] Check error rates and logs
- [ ] Verify SSL/TLS configuration
- [ ] Test backup and recovery procedures
- [ ] Document deployment process
- [ ] Set up alerting and monitoring

## Troubleshooting Production Issues

### Common Production Issues

#### 1. High Memory Usage
```bash
# Monitor memory usage
docker stats flight-delay-api

# Optimize model loading
# Consider model quantization or compression
```

#### 2. Slow Response Times
```bash
# Check application metrics
curl http://localhost:8080/metrics

# Monitor database/model performance
# Consider adding caching
```

#### 3. SSL/TLS Issues
```bash
# Test SSL configuration
openssl s_client -connect api.yourdomain.com:443

# Check certificate expiry
openssl x509 -in cert.pem -text -noout | grep "Not After"
```

#### 4. Service Discovery Issues
```bash
# Health check debugging
curl -v http://localhost:8080/health

# Check service logs
docker logs flight-delay-api
journalctl -u flight-delay-api -f
```

## Scaling Considerations

### Horizontal Scaling
- **Load balancer**: Distribute traffic across multiple instances
- **Auto-scaling**: Scale based on CPU/memory/request metrics
- **Database**: Consider read replicas if using database
- **Caching**: Implement Redis/Memcached for model predictions

### Vertical Scaling
- **CPU**: Increase for compute-intensive predictions
- **Memory**: Increase for model loading and caching
- **Storage**: SSD for faster model loading

### Performance Targets
- **Response time**: < 200ms for predictions
- **Throughput**: 100+ requests/second per instance
- **Availability**: 99.9% uptime
- **Error rate**: < 0.1%

This deployment guide provides comprehensive instructions for moving your Flight Delay Prediction API from development to production. Choose the deployment option that best fits your infrastructure and requirements.
