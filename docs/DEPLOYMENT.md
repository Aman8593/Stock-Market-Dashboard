# 🚀 Stock Sage Deployment Guide

Complete deployment guide for Stock Sage application across different environments.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   External APIs │
                    │ • News API      │
                    │ • HuggingFace   │
                    │ • Alpha Vantage │
                    └─────────────────┘
```

## 🐳 Docker Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### Quick Start with Docker Compose

1. **Clone and Setup**

```bash
git clone <repository-url>
cd stock-sage
cp .env.example .env
# Edit .env with your API keys
```

2. **Build and Run**

```bash
docker-compose up --build -d
```

3. **Access Application**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Docker Compose Configuration

**docker-compose.yml**

```yaml
version: "3.8"

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://stocksage:password@db:5432/stocksage
      - HF_API_TOKEN=${HF_API_TOKEN}
      - NEWS_API_KEY=${NEWS_API_KEY}
      - ALPHAVANTAGE_KEY=${ALPHAVANTAGE_KEY}
    depends_on:
      - db
    volumes:
      - ./backend:/app
    command: uvicorn app:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=stocksage
      - POSTGRES_USER=stocksage
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Individual Dockerfiles

**Frontend Dockerfile**

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
```

**Backend Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS (Recommended)

1. **Create ECR Repositories**

```bash
aws ecr create-repository --repository-name stocksage-frontend
aws ecr create-repository --repository-name stocksage-backend
```

2. **Build and Push Images**

```bash
# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push frontend
docker build -t stocksage-frontend ./frontend
docker tag stocksage-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/stocksage-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/stocksage-frontend:latest

# Build and push backend
docker build -t stocksage-backend ./backend
docker tag stocksage-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/stocksage-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/stocksage-backend:latest
```

3. **Create ECS Task Definition**

```json
{
  "family": "stocksage-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/stocksage-frontend:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "essential": true
    },
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/stocksage-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://username:password@rds-endpoint:5432/stocksage"
        }
      ],
      "essential": true
    }
  ]
}
```

#### Using AWS Lambda (Serverless)

**Backend with Lambda**

```python
# lambda_handler.py
from mangum import Mangum
from app import app

handler = Mangum(app)
```

**Deploy with Serverless Framework**

```yaml
# serverless.yml
service: stocksage-backend

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  environment:
    HF_API_TOKEN: ${env:HF_API_TOKEN}
    NEWS_API_KEY: ${env:NEWS_API_KEY}

functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
    timeout: 30
    memorySize: 1024

plugins:
  - serverless-python-requirements
```

### Google Cloud Platform

#### Using Cloud Run

1. **Build and Deploy Backend**

```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/stocksage-backend ./backend
gcloud run deploy stocksage-backend \
  --image gcr.io/PROJECT-ID/stocksage-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

2. **Build and Deploy Frontend**

```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/stocksage-frontend ./frontend
gcloud run deploy stocksage-frontend \
  --image gcr.io/PROJECT-ID/stocksage-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Digital Ocean App Platform

**app.yaml**

```yaml
name: stocksage
services:
  - name: backend
    source_dir: /backend
    github:
      repo: your-username/stock-sage
      branch: main
    run_command: uvicorn app:app --host 0.0.0.0 --port 8080
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xxs
    envs:
      - key: HF_API_TOKEN
        value: ${HF_API_TOKEN}
      - key: NEWS_API_KEY
        value: ${NEWS_API_KEY}
    http_port: 8080

  - name: frontend
    source_dir: /frontend
    github:
      repo: your-username/stock-sage
      branch: main
    build_command: npm run build
    environment_slug: node-js
    instance_count: 1
    instance_size_slug: basic-xxs

databases:
  - name: stocksage-db
    engine: PG
    version: "15"
```

## 🔧 Environment Configuration

### Production Environment Variables

**Backend (.env)**

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/stocksage
REDIS_URL=redis://localhost:6379

# API Keys
HF_API_TOKEN=hf_your_huggingface_token
NEWS_API_KEY=your_news_api_key
ALPHAVANTAGE_KEY=your_alpha_vantage_key

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Performance
WORKERS=4
MAX_CONNECTIONS=100
CACHE_TTL=300
```

**Frontend (.env)**

```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_GOOGLE_CLIENT_ID=your_google_oauth_client_id
REACT_APP_ENVIRONMENT=production
```

## 🔒 Security Configuration

### SSL/TLS Setup

**Nginx Configuration**

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Rules

```bash
# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Allow SSH (change port if needed)
ufw allow 22/tcp

# Block direct access to backend
ufw deny 8000/tcp

# Enable firewall
ufw enable
```

## 📊 Monitoring and Logging

### Health Checks

**Backend Health Check**

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

### Logging Configuration

**Python Logging**

```python
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### Monitoring with Prometheus

**docker-compose.monitoring.yml**

```yaml
version: "3.8"

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 🔄 CI/CD Pipeline

### GitHub Actions

**.github/workflows/deploy.yml**

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend && python -m pytest
          cd frontend && npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          # Your deployment script here
          ./deploy.sh
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**

```bash
# Check database status
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up db -d
```

2. **API Rate Limits**

```bash
# Check rate limit status
curl -I http://localhost:8000/analyze/AAPL
# Look for X-RateLimit-* headers
```

3. **Memory Issues**

```bash
# Monitor memory usage
docker stats

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### Performance Optimization

1. **Enable Redis Caching**
2. **Use CDN for static assets**
3. **Implement database connection pooling**
4. **Add response compression**
5. **Optimize Docker image sizes**

## 📋 Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Health checks working
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] CI/CD pipeline tested
- [ ] Load testing completed
- [ ] Security scan passed
