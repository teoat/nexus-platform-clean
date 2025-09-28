# NEXUS Platform - Consolidated Deployment & Operations Guide

**Status**: 🔒 **CONSOLIDATED** - Single Source of Truth for Deployment & Operations  
**Version**: 2.0  
**Last Updated**: 2025-01-27  
**Source**: Consolidated from multiple deployment and operations guides  
**Aligned with**: [Vision & Mission](01-vision-mission.md)

---

## 🎯 **DEPLOYMENT OVERVIEW**

The NEXUS Platform deployment system is designed to support the mission of **"revolutionizing financial examination through intelligent, role-based analysis"** by providing enterprise-grade deployment capabilities that ensure 99.9% uptime, 95%+ fraud detection accuracy, and seamless scalability for financial institutions worldwide.

### **Deployment Philosophy**

- **Zero-Downtime Deployments**: Seamless updates without service interruption
- **Enterprise Security**: Bank-grade security for financial data
- **High Availability**: 99.9% uptime with automatic failover
- **Scalability**: Auto-scaling to handle enterprise workloads
- **Compliance**: Built-in regulatory compliance features

---

## 🚀 **SYSTEM REQUIREMENTS**

### **Minimum Requirements**

#### **Development Environment**

- **CPU**: 4 cores (2.0 GHz)
- **RAM**: 8GB (16GB recommended)
- **Storage**: 50GB SSD
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Network**: 100 Mbps internet connection

#### **Production Environment**

- **CPU**: 8 cores (3.0 GHz)
- **RAM**: 32GB (64GB recommended)
- **Storage**: 500GB SSD (1TB recommended)
- **OS**: Ubuntu 20.04 LTS, RHEL 8+, CentOS 8+
- **Network**: 1 Gbps internet connection

### **Software Dependencies**

#### **Core Requirements**

- **Python**: 3.11+ (3.12 recommended)
- **Node.js**: 18+ (20+ recommended)
- **Docker**: 24.0+ with Docker Compose 2.0+
- **Kubernetes**: 1.28+ (for production)
- **PostgreSQL**: 15+ (16+ recommended)
- **Redis**: 7.0+ (7.2+ recommended)

#### **Development Tools**

- **Git**: 2.40+
- **VS Code**: Latest version with extensions
- **Docker Desktop**: Latest version
- **kubectl**: Latest version
- **Helm**: 3.12+

---

## 🐳 **DOCKER DEPLOYMENT**

### **Development Deployment**

#### **Quick Start (5 minutes)**

```bash
# Clone the repository
git clone https://github.com/nexus-platform/nexus.git
cd nexus

# Start development environment
docker-compose up -d

# Verify deployment
curl http://localhost:8080/health
```

#### **Development Configuration**

```yaml
# docker-compose.dev.yml
version: "3.8"
services:
  nexus-api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://nexus:password@db:5432/nexus_dev
      - REDIS_URL=redis://redis:6379
    volumes:
      - .:/app
      - /nexus_backend/node_modules
    depends_on:
      - db
      - redis

  nexus-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8080
    volumes:
      - ./frontend:/app
      - /nexus_backend/node_modules

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=nexus_dev
      - POSTGRES_USER=nexus
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7.2
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### **Production Deployment**

#### **Production Dockerfile**

```dockerfile
# Dockerfile.production
FROM python:3.11-slim as base

# Security hardening
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r nexus && useradd -r -g nexus nexus

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R nexus:nexus /app
USER nexus

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose port
EXPOSE 8080

# Start application
CMD ["python", "main.py"]
```

#### **Production Docker Compose**

```yaml
# docker-compose.production.yml
version: "3.8"
services:
  nexus-api:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "2.0"
          memory: 4G
        reservations:
          cpus: "1.0"
          memory: 2G
    restart: unless-stopped
    depends_on:
      - db
      - redis
    networks:
      - nexus-network

  nexus-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.production
    ports:
      - "80:80"
    environment:
      - REACT_APP_API_URL=${API_URL}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: "1.0"
          memory: 2G
    restart: unless-stopped
    networks:
      - nexus-network

  db:
    image: postgres:16
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 4G
    restart: unless-stopped
    networks:
      - nexus-network

  redis:
    image: redis:7.2-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 1G
    restart: unless-stopped
    networks:
      - nexus-network

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - nexus-api
      - nexus-frontend
    restart: unless-stopped
    networks:
      - nexus-network

volumes:
  postgres_data:
  redis_data:

networks:
  nexus-network:
    driver: bridge
```

---

## ☸️ **KUBERNETES DEPLOYMENT**

### **Namespace and Security**

```yaml
# k8s/production/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: nexus-production
  labels:
    name: nexus-production
    environment: production
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: nexus-quota
  namespace: nexus-production
spec:
  hard:
    requests.cpu: "8"
    requests.memory: 32Gi
    limits.cpu: "16"
    limits.memory: 64Gi
    persistentvolumeclaims: "10"
```

### **Secrets Management**

```yaml
# k8s/production/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: nexus-secrets
  namespace: nexus-production
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  redis-url: <base64-encoded-redis-url>
  jwt-secret: <base64-encoded-jwt-secret>
  encryption-key: <base64-encoded-encryption-key>
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: nexus-config
  namespace: nexus-production
data:
  NODE_ENV: "production"
  LOG_LEVEL: "info"
  MAX_CONNECTIONS: "100"
  TIMEOUT: "30"
```

### **Backend Deployment**

```yaml
# k8s/production/nexus-backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexus-backend
  namespace: nexus-production
  labels:
    app: nexus-backend
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nexus-backend
  template:
    metadata:
      labels:
        app: nexus-backend
        version: v1.0.0
    spec:
      containers:
        - name: nexus-backend
          image: nexus/backend:v1.0.0
          ports:
            - containerPort: 8080
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: nexus-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: nexus-secrets
                  key: redis-url
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: nexus-secrets
                  key: jwt-secret
          resources:
            requests:
              memory: "2Gi"
              cpu: "1"
            limits:
              memory: "4Gi"
              cpu: "2"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          volumeMounts:
            - name: app-logs
              mountPath: /nexus_backend/logs
      volumes:
        - name: app-logs
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: nexus-backend-service
  namespace: nexus-production
spec:
  selector:
    app: nexus-backend
  ports:
    - port: 8080
      targetPort: 8080
  type: ClusterIP
```

### **Frontend Deployment**

```yaml
# k8s/production/nexus-frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexus-frontend
  namespace: nexus-production
  labels:
    app: nexus-frontend
    version: v1.0.0
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nexus-frontend
  template:
    metadata:
      labels:
        app: nexus-frontend
        version: v1.0.0
    spec:
      containers:
        - name: nexus-frontend
          image: nexus/frontend:v1.0.0
          ports:
            - containerPort: 80
          env:
            - name: REACT_APP_API_URL
              value: "https://api.nexusplatform.com"
          resources:
            requests:
              memory: "1Gi"
              cpu: "0.5"
            limits:
              memory: "2Gi"
              cpu: "1"
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: nexus-frontend-service
  namespace: nexus-production
spec:
  selector:
    app: nexus-frontend
  ports:
    - port: 80
      targetPort: 80
  type: ClusterIP
```

### **Database Deployment**

```yaml
# k8s/production/database/postgres-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: nexus-production
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_DB
              value: "nexus_production"
            - name: POSTGRES_USER
              value: "nexus"
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: nexus-secrets
                  key: postgres-password
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
          resources:
            requests:
              memory: "2Gi"
              cpu: "1"
            limits:
              memory: "4Gi"
              cpu: "2"
  volumeClaimTemplates:
    - metadata:
        name: postgres-storage
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 100Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: nexus-production
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
  type: ClusterIP
```

### **Ingress Configuration**

```yaml
# k8s/production/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nexus-ingress
  namespace: nexus-production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - nexusplatform.com
        - api.nexusplatform.com
      secretName: nexus-tls
  rules:
    - host: nexusplatform.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nexus-frontend-service
                port:
                  number: 80
    - host: api.nexusplatform.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nexus-backend-service
                port:
                  number: 8080
```

---

## 🔧 **DEPLOYMENT AUTOMATION**

### **Deployment Scripts**

#### **Production Deployment Script**

```bash
#!/bin/bash
# deploy-production.sh

set -e

echo "🚀 Starting NEXUS Platform Production Deployment..."

# Configuration
NAMESPACE="nexus-production"
VERSION=${1:-"latest"}
ENVIRONMENT=${2:-"production"}

# Validate prerequisites
echo "📋 Validating prerequisites..."
kubectl version --client
docker version
helm version

# Create namespace
echo "📁 Creating namespace..."
kubectl apply -f k8s/production/namespace.yaml

# Apply secrets
echo "🔐 Applying secrets..."
kubectl apply -f k8s/production/secrets.yaml

# Deploy database
echo "🗄️ Deploying database..."
kubectl apply -f k8s/production/database/postgres-deployment.yaml

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s

# Deploy Redis
echo "🔴 Deploying Redis..."
kubectl apply -f k8s/production/redis/redis-deployment.yaml

# Deploy backend
echo "⚙️ Deploying backend..."
kubectl apply -f k8s/production/nexus-backend-deployment.yaml

# Deploy frontend
echo "🎨 Deploying frontend..."
kubectl apply -f k8s/production/nexus-frontend-deployment.yaml

# Apply ingress
echo "🌐 Applying ingress..."
kubectl apply -f k8s/production/ingress.yaml

# Wait for all pods to be ready
echo "⏳ Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod -l app=nexus-backend -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=nexus-frontend -n $NAMESPACE --timeout=300s

# Run health checks
echo "🏥 Running health checks..."
./scripts/health-check.sh

echo "✅ NEXUS Platform Production Deployment Complete!"
echo "🌐 Frontend: https://nexusplatform.com"
echo "🔌 API: https://api.nexusplatform.com"
```

#### **Health Check Script**

```bash
#!/bin/bash
# health-check.sh

set -e

echo "🏥 Running NEXUS Platform Health Checks..."

# Configuration
NAMESPACE="nexus-production"
API_URL="https://api.nexusplatform.com"
FRONTEND_URL="https://nexusplatform.com"

# Check pod status
echo "📊 Checking pod status..."
kubectl get pods -n $NAMESPACE

# Check service status
echo "🔌 Checking service status..."
kubectl get services -n $NAMESPACE

# Check API health
echo "🔍 Checking API health..."
curl -f $API_URL/health || {
    echo "❌ API health check failed"
    exit 1
}

# Check frontend health
echo "🎨 Checking frontend health..."
curl -f $FRONTEND_URL || {
    echo "❌ Frontend health check failed"
    exit 1
}

# Check database connectivity
echo "🗄️ Checking database connectivity..."
kubectl exec -n $NAMESPACE deployment/nexus-backend -- python -c "
import psycopg2
import os
conn = psycopg2.connect(os.environ['DATABASE_URL'])
print('✅ Database connection successful')
conn.close()
"

# Check Redis connectivity
echo "🔴 Checking Redis connectivity..."
kubectl exec -n $NAMESPACE deployment/nexus-backend -- python -c "
import redis
import os
r = redis.from_url(os.environ['REDIS_URL'])
r.ping()
print('✅ Redis connection successful')
"

echo "✅ All health checks passed!"
```

### **CI/CD Pipeline**

#### **GitHub Actions Workflow**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: nexus-platform

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          pytest tests/ --cov=nexus_backend/ --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG }}

      - name: Deploy to Kubernetes
        run: |
          ./scripts/deploy-production.sh latest production

      - name: Run health checks
        run: |
          ./scripts/health-check.sh
```

---

## 📊 **MONITORING & OBSERVABILITY**

### **Prometheus Configuration**

```yaml
# monitoring/prometheus-config.yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "nexus_rules.yml"

scrape_configs:
  - job_name: "nexus-backend"
    static_configs:
      - targets: ["nexus-backend-service:8080"]
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: "nexus-frontend"
    static_configs:
      - targets: ["nexus-frontend-service:80"]
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: "postgres"
    static_configs:
      - targets: ["postgres:5432"]
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: "redis"
    static_configs:
      - targets: ["redis:6379"]
    metrics_path: /metrics
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093
```

### **Grafana Dashboard**

```json
{
  "dashboard": {
    "title": "NEXUS Platform Monitoring",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "Active connections"
          }
        ]
      }
    ]
  }
}
```

### **Health Check Endpoints**

```python
# health_checker.py
from fastapi import FastAPI, HTTPException
import psycopg2
import redis
import os

app = FastAPI()

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }

    # Check database
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        conn.close()
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check Redis
    try:
        r = redis.from_url(os.environ['REDIS_URL'])
        r.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check external services
    # Add checks for external APIs, file systems, etc.

    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status

@app.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    # Check if application is ready to serve traffic
    return {"status": "ready"}
```

---

## 🔒 **SECURITY CONFIGURATION**

### **SSL/TLS Configuration**

```nginx
# nginx/nginx.conf
server {
    listen 443 ssl http2;
    server_name nexusplatform.com;

    ssl_certificate /etc/ssl/certs/nexus.crt;
    ssl_certificate_key /etc/ssl/private/nexus.key;

    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    location / {
        proxy_pass http://nexus-frontend-service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://nexus-backend-service:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **Network Policies**

```yaml
# k8s/production/network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nexus-network-policy
  namespace: nexus-production
spec:
  podSelector:
    matchLabels:
      app: nexus-backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: nexus-production
        - podSelector:
            matchLabels:
              app: nginx
      ports:
        - protocol: TCP
          port: 8080
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
```

---

## 🔄 **BACKUP & DISASTER RECOVERY**

### **Database Backup**

```bash
#!/bin/bash
# backup.sh

set -e

echo "💾 Starting database backup..."

# Configuration
NAMESPACE="nexus-production"
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="nexus_backup_${TIMESTAMP}.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
kubectl exec -n $NAMESPACE deployment/postgres -- pg_dump \
  -U nexus \
  -d nexus_production \
  > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Upload to cloud storage (AWS S3 example)
aws s3 cp $BACKUP_DIR/${BACKUP_FILE}.gz s3://nexus-backups/database/

# Clean up old backups (keep last 30 days)
find $BACKUP_DIR -name "nexus_backup_*.sql.gz" -mtime +30 -delete

echo "✅ Database backup completed: ${BACKUP_FILE}.gz"
```

### **Disaster Recovery**

```bash
#!/bin/bash
# restore.sh

set -e

echo "🔄 Starting disaster recovery..."

# Configuration
NAMESPACE="nexus-production"
BACKUP_FILE=${1:-"latest"}
BACKUP_DIR="/backups"

# Download backup from cloud storage
aws s3 cp s3://nexus-backups/database/${BACKUP_FILE}.gz $BACKUP_DIR/

# Decompress backup
gunzip $BACKUP_DIR/${BACKUP_FILE}.gz

# Restore database
kubectl exec -i -n $NAMESPACE deployment/postgres -- psql \
  -U nexus \
  -d nexus_production \
  < $BACKUP_DIR/${BACKUP_FILE}

echo "✅ Database restore completed"
```

---

## 📈 **SCALING & PERFORMANCE**

### **Horizontal Pod Autoscaler**

```yaml
# k8s/production/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nexus-backend-hpa
  namespace: nexus-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nexus-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### **Vertical Pod Autoscaler**

```yaml
# k8s/production/vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: nexus-backend-vpa
  namespace: nexus-production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nexus-backend
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
      - containerName: nexus-backend
        minAllowed:
          cpu: 100m
          memory: 128Mi
        maxAllowed:
          cpu: 2
          memory: 4Gi
```

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues**

#### **Pod Startup Issues**

```bash
# Check pod status
kubectl get pods -n nexus-production

# Check pod logs
kubectl logs -n nexus-production deployment/nexus-backend

# Check pod events
kubectl describe pod -n nexus-production <pod-name>
```

#### **Database Connection Issues**

```bash
# Check database status
kubectl exec -n nexus-production deployment/postgres -- pg_isready

# Check database logs
kubectl logs -n nexus-production deployment/postgres

# Test database connection
kubectl exec -n nexus-production deployment/nexus-backend -- python -c "
import psycopg2
import os
conn = psycopg2.connect(os.environ['DATABASE_URL'])
print('Database connection successful')
conn.close()
"
```

#### **Performance Issues**

```bash
# Check resource usage
kubectl top pods -n nexus-production

# Check node resources
kubectl top nodes

# Check HPA status
kubectl get hpa -n nexus-production
```

### **Debugging Commands**

```bash
# Get all resources
kubectl get all -n nexus-production

# Check ingress status
kubectl get ingress -n nexus-production

# Check secrets
kubectl get secrets -n nexus-production

# Check config maps
kubectl get configmaps -n nexus-production

# Port forward for local testing
kubectl port-forward -n nexus-production service/nexus-backend-service 8080:8080
```

---

## 📋 **MAINTENANCE PROCEDURES**

### **Regular Maintenance Tasks**

#### **Daily Tasks**

- [ ] Check system health and alerts
- [ ] Review error logs and metrics
- [ ] Verify backup completion
- [ ] Monitor resource usage

#### **Weekly Tasks**

- [ ] Review security logs
- [ ] Update dependencies
- [ ] Test disaster recovery procedures
- [ ] Performance analysis

#### **Monthly Tasks**

- [ ] Security audit
- [ ] Capacity planning review
- [ ] Update documentation
- [ ] Disaster recovery testing

### **Update Procedures**

```bash
# Rolling update
kubectl set image deployment/nexus-backend nexus-backend=nexus/backend:v1.1.0 -n nexus-production

# Check update status
kubectl rollout status deployment/nexus-backend -n nexus-production

# Rollback if needed
kubectl rollout undo deployment/nexus-backend -n nexus-production
```

---

## 🎯 **SUCCESS METRICS**

### **Deployment Metrics**

- **Deployment Time**: < 10 minutes for full deployment
- **Zero-Downtime**: 100% zero-downtime deployments
- **Rollback Time**: < 2 minutes for rollback
- **Health Check Time**: < 30 seconds for complete health check

### **Operational Metrics**

- **Uptime**: 99.9% system availability
- **Response Time**: < 200ms average API response
- **Error Rate**: < 0.1% error rate
- **Recovery Time**: < 4 hours for disaster recovery

### **Security Metrics**

- **Security Incidents**: Zero critical security breaches
- **Compliance**: 100% regulatory compliance
- **Vulnerability Response**: < 24 hours for critical vulnerabilities
- **Audit Success**: 100% audit compliance

---

**Last Updated**: 2025-01-27  
**Version**: 2.0  
**Maintainer**: NEXUS Development Team  
**Next Review**: 2025-02-27  
**Aligned with**: [Vision & Mission](01-vision-mission.md)
