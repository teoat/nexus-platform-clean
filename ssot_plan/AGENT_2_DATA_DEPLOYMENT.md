# Agent 2: Data Schema & Deployment Implementation

## Unified Data Management & Deployment Orchestration

**Agent Role:** Data Schema & Deployment Specialist
**Focus:** Data management and deployment orchestration
**Timeline:** Days 1-5 (Phase 1)
**Dependencies:** None (parallel execution)

---

## 🎯 **Mission Statement**

Consolidate all data schemas and deployment configurations into a unified SSOT system, ensuring consistency across all environments and services.

---

## 📋 **Core Deliverables**

### **1. Unified Database Schema**

- **File:** `backend/database/schema.sql`
- **Purpose:** Single source of truth for all database structures
- **Features:**
  - PostgreSQL schema consolidation
  - Table definitions
  - Indexes and constraints
  - Triggers and functions
  - Migration scripts

### **2. Redis Schema Management**

- **File:** `backend/cache/redis_schema.json`
- **Purpose:** Centralized Redis data structure definitions
- **Features:**
  - Key naming conventions
  - Data type definitions
  - TTL policies
  - Cache invalidation rules
  - Performance optimization

### **3. Kubernetes Manifest Optimization**

- **File:** `k8s/unified-manifests.yaml`
- **Purpose:** Consolidated Kubernetes deployment configurations
- **Features:**
  - Service definitions
  - Deployment configurations
  - ConfigMaps and Secrets
  - Ingress rules
  - Resource limits

### **4. Docker Configuration Standardization**

- **File:** `docker-compose.unified.yml`
- **Purpose:** Unified Docker development and production setup
- **Features:**
  - Service definitions
  - Network configuration
  - Volume management
  - Environment variables
  - Health checks

### **5. Environment Management**

- **File:** `config/environments.yaml`
- **Purpose:** Centralized environment configuration
- **Features:**
  - Environment-specific settings
  - Secret management
  - Feature flags
  - Resource allocation
  - Monitoring configuration

---

## 🔧 **Implementation Tasks**

### **Task 2.1: Database Schema Consolidation (Day 1)**

```sql
-- Create: backend/database/schema.sql
-- NEXUS Platform - Unified Database Schema
-- Generated: 2025-01-27T12:30:00Z
-- Version: 1.0

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- User Roles and Permissions
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    PRIMARY KEY (user_id, role_id)
);

-- API Management
CREATE TABLE api_endpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    path VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    description TEXT,
    version VARCHAR(20) DEFAULT 'v1',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API Aliases
CREATE TABLE api_aliases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alias_name VARCHAR(255) NOT NULL,
    canonical_name VARCHAR(255) NOT NULL,
    context VARCHAR(100) NOT NULL,
    alias_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(alias_name, context)
);

-- SSOT Anchors
CREATE TABLE ssot_anchors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    anchor_id VARCHAR(255) UNIQUE NOT NULL,
    family VARCHAR(100) NOT NULL,
    description TEXT,
    format VARCHAR(50) NOT NULL,
    source_hint VARCHAR(500),
    owner VARCHAR(255),
    version VARCHAR(50) NOT NULL,
    centrality_score DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit Logging
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(255) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_api_endpoints_name ON api_endpoints(name);
CREATE INDEX idx_api_aliases_alias ON api_aliases(alias_name);
CREATE INDEX idx_api_aliases_context ON api_aliases(context);
CREATE INDEX idx_ssot_anchors_family ON ssot_anchors(family);
CREATE INDEX idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_changed_at ON audit_logs(changed_at);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_api_endpoints_updated_at BEFORE UPDATE ON api_endpoints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ssot_anchors_updated_at BEFORE UPDATE ON ssot_anchors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### **Task 2.2: Redis Schema Management (Day 2)**

```json
{
  "redis_schema": {
    "version": "1.0",
    "generated_at": "2025-01-27T12:30:00Z",
    "key_patterns": {
      "user_sessions": "session:{user_id}:{session_id}",
      "api_cache": "api:cache:{endpoint}:{params_hash}",
      "rate_limits": "rate_limit:{user_id}:{endpoint}",
      "ssot_cache": "ssot:cache:{anchor_id}:{version}",
      "alias_cache": "alias:cache:{alias}:{context}",
      "audit_logs": "audit:logs:{date}:{hour}"
    },
    "data_types": {
      "user_sessions": {
        "type": "hash",
        "ttl": "24h",
        "fields": {
          "user_id": "string",
          "session_data": "json",
          "created_at": "timestamp",
          "last_activity": "timestamp"
        }
      },
      "api_cache": {
        "type": "string",
        "ttl": "1h",
        "compression": "gzip",
        "format": "json"
      },
      "rate_limits": {
        "type": "string",
        "ttl": "1h",
        "value": "integer"
      },
      "ssot_cache": {
        "type": "hash",
        "ttl": "30m",
        "fields": {
          "content": "json",
          "version": "string",
          "checksum": "string",
          "cached_at": "timestamp"
        }
      }
    },
    "policies": {
      "eviction": "allkeys-lru",
      "maxmemory": "2gb",
      "persistence": "aof",
      "compression": true
    },
    "monitoring": {
      "slowlog": true,
      "latency_tracking": true,
      "memory_usage": true,
      "hit_ratio": true
    }
  }
}
```

### **Task 2.3: Kubernetes Manifest Optimization (Day 3)**

```yaml
# Create: k8s/unified-manifests.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: nexus-platform
  labels:
    app: nexus
    environment: production

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: nexus-config
  namespace: nexus-platform
data:
  database_url: "postgresql://nexus:password@postgres:5432/nexus"
  redis_url: "redis://redis:6379"
  api_base_url: "https://api.nexus.com"
  environment: "production"

---
apiVersion: v1
kind: Secret
metadata:
  name: nexus-secrets
  namespace: nexus-platform
type: Opaque
data:
  database_password: <base64-encoded>
  redis_password: <base64-encoded>
  jwt_secret: <base64-encoded>

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexus-backend
  namespace: nexus-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nexus-backend
  template:
    metadata:
      labels:
        app: nexus-backend
    spec:
      containers:
        - name: backend
          image: nexus/backend:latest
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              valueFrom:
                configMapKeyRef:
                  name: nexus-config
                  key: database_url
            - name: REDIS_URL
              valueFrom:
                configMapKeyRef:
                  name: nexus-config
                  key: redis_url
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: nexus-backend-service
  namespace: nexus-platform
spec:
  selector:
    app: nexus-backend
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nexus-ingress
  namespace: nexus-platform
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - api.nexus.com
      secretName: nexus-tls
  rules:
    - host: api.nexus.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nexus-backend-service
                port:
                  number: 80
```

### **Task 2.4: Docker Configuration Standardization (Day 4)**

```yaml
# Create: docker-compose.unified.yml
version: "3.8"

services:
  postgres:
    image: postgres:15-alpine
    container_name: nexus-postgres
    environment:
      POSTGRES_DB: nexus
      POSTGRES_USER: nexus
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-nexus123}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/database/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nexus"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: nexus-redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redis123}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: nexus-backend
    environment:
      DATABASE_URL: postgresql://nexus:${POSTGRES_PASSWORD:-nexus123}@postgres:5432/nexus
      REDIS_URL: redis://:${REDIS_PASSWORD:-redis123}@redis:6379
      API_BASE_URL: http://localhost:8000
      ENVIRONMENT: development
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - ./config:/app/config
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    container_name: nexus-frontend
    environment:
      REACT_APP_API_URL: http://localhost:8000
      REACT_APP_ENVIRONMENT: development
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    container_name: nexus-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: nexus-network
```

### **Task 2.5: Environment Management (Day 5)**

```yaml
# Create: config/environments.yaml
environments:
  development:
    database:
      host: localhost
      port: 5432
      name: nexus_dev
      user: nexus
      password: nexus123
      ssl: false
    redis:
      host: localhost
      port: 6379
      password: redis123
      db: 0
    api:
      base_url: http://localhost:8000
      timeout: 30
      retries: 3
    monitoring:
      enabled: true
      level: debug
      log_file: logs/nexus-dev.log
    features:
      ssot_aliasing: true
      audit_logging: true
      rate_limiting: false
      caching: true

  staging:
    database:
      host: staging-db.nexus.com
      port: 5432
      name: nexus_staging
      user: nexus
      password: ${STAGING_DB_PASSWORD}
      ssl: true
    redis:
      host: staging-redis.nexus.com
      port: 6379
      password: ${STAGING_REDIS_PASSWORD}
      db: 0
    api:
      base_url: https://staging-api.nexus.com
      timeout: 30
      retries: 3
    monitoring:
      enabled: true
      level: info
      log_file: /var/log/nexus/staging.log
    features:
      ssot_aliasing: true
      audit_logging: true
      rate_limiting: true
      caching: true

  production:
    database:
      host: prod-db.nexus.com
      port: 5432
      name: nexus_prod
      user: nexus
      password: ${PROD_DB_PASSWORD}
      ssl: true
    redis:
      host: prod-redis.nexus.com
      port: 6379
      password: ${PROD_REDIS_PASSWORD}
      db: 0
    api:
      base_url: https://api.nexus.com
      timeout: 30
      retries: 3
    monitoring:
      enabled: true
      level: warn
      log_file: /var/log/nexus/production.log
    features:
      ssot_aliasing: true
      audit_logging: true
      rate_limiting: true
      caching: true
      security_scanning: true

  secrets:
    database_passwords:
      development: "nexus123"
      staging: "${STAGING_DB_PASSWORD}"
      production: "${PROD_DB_PASSWORD}"
    redis_passwords:
      development: "redis123"
      staging: "${STAGING_REDIS_PASSWORD}"
      production: "${PROD_REDIS_PASSWORD}"
    jwt_secrets:
      development: "dev-jwt-secret"
      staging: "${STAGING_JWT_SECRET}"
      production: "${PROD_JWT_SECRET}"
```

---

## 📊 **Success Criteria**

### **Day 1 Success**

- [ ] Database schema consolidated
- [ ] All tables created
- [ ] Indexes optimized
- [ ] Triggers functional

### **Day 2 Success**

- [ ] Redis schema defined
- [ ] Key patterns established
- [ ] TTL policies configured
- [ ] Performance optimized

### **Day 3 Success**

- [ ] Kubernetes manifests optimized
- [ ] Services defined
- [ ] ConfigMaps created
- [ ] Ingress configured

### **Day 4 Success**

- [ ] Docker Compose unified
- [ ] Services orchestrated
- [ ] Health checks working
- [ ] Volumes configured

### **Day 5 Success**

- [ ] Environment management complete
- [ ] Secrets configured
- [ ] Feature flags working
- [ ] Monitoring active

---

## 🔍 **Validation Commands**

### **Test Database Schema**

```bash
# Copy and paste these commands
cd /Users/Arief/Desktop/Nexus
docker-compose -f docker-compose.unified.yml up postgres -d
sleep 10
psql -h localhost -U nexus -d nexus -f backend/database/schema.sql
psql -h localhost -U nexus -d nexus -c "\dt"
```

### **Test Redis Schema**

```bash
# Copy and paste these commands
cd /Users/Arief/Desktop/Nexus
docker-compose -f docker-compose.unified.yml up redis -d
sleep 5
redis-cli -h localhost -p 6379 -a redis123 ping
redis-cli -h localhost -p 6379 -a redis123 info memory
```

### **Test Kubernetes Manifests**

```bash
# Copy and paste these commands
cd /Users/Arief/Desktop/Nexus
kubectl apply -f k8s/unified-manifests.yaml --dry-run=client
kubectl get namespaces | grep nexus
kubectl get configmaps -n nexus-platform
```

### **Test Docker Compose**

```bash
# Copy and paste these commands
cd /Users/Arief/Desktop/Nexus
docker-compose -f docker-compose.unified.yml config
docker-compose -f docker-compose.unified.yml up -d
docker-compose -f docker-compose.unified.yml ps
```

---

## 📚 **Documentation Requirements**

### **Database Documentation**

- **File:** `docs/database/schema.md`
- **Content:**
  - Table definitions
  - Relationship diagrams
  - Index strategies
  - Migration procedures

### **Deployment Documentation**

- **File:** `docs/deployment/kubernetes.md`
- **Content:**
  - Service architecture
  - Configuration management
  - Scaling procedures
  - Troubleshooting

### **Environment Documentation**

- **File:** `docs/environment/configuration.md`
- **Content:**
  - Environment setup
  - Secret management
  - Feature flags
  - Monitoring configuration

---

## 🚨 **Error Handling**

### **Database Errors**

- Connection failures
- Schema validation errors
- Migration conflicts
- Performance issues

### **Deployment Errors**

- Resource constraints
- Configuration errors
- Service discovery failures
- Health check failures

### **Environment Errors**

- Missing secrets
- Configuration conflicts
- Feature flag issues
- Monitoring failures

---

## 🔒 **Security Considerations**

### **Database Security**

- Encrypted connections
- User access control
- Audit logging
- Backup encryption

### **Deployment Security**

- Secret management
- Network policies
- Resource limits
- Security scanning

### **Environment Security**

- Secret rotation
- Access control
- Audit trails
- Compliance monitoring

---

## 📈 **Performance Targets**

### **Database Performance**

- Query response: < 100ms
- Connection pool: 20-50 connections
- Index optimization: 95%+ hit rate
- Backup time: < 30 minutes

### **Deployment Performance**

- Pod startup: < 60 seconds
- Service discovery: < 5 seconds
- Health checks: < 10 seconds
- Scaling: < 2 minutes

### **Environment Performance**

- Configuration load: < 1 second
- Secret retrieval: < 500ms
- Feature flag check: < 10ms
- Monitoring overhead: < 5%

---

## 🎯 **Final Deliverables Checklist**

- [ ] `backend/database/schema.sql` - Unified database schema
- [ ] `backend/cache/redis_schema.json` - Redis schema management
- [ ] `k8s/unified-manifests.yaml` - Kubernetes configurations
- [ ] `docker-compose.unified.yml` - Docker orchestration
- [ ] `config/environments.yaml` - Environment management
- [ ] `docs/database/schema.md` - Database documentation
- [ ] `docs/deployment/kubernetes.md` - Deployment guide
- [ ] `docs/environment/configuration.md` - Environment guide

---

**Ready to implement? Copy the configurations and start building! 🚀**
