# NEXUS SSOT Quick Start Commands

## Copy-Paste Implementation Guide

**Generated:** 2025-01-27T12:30:00Z
**Version:** 1.0
**Platform:** NEXUS

---

## 🚀 **Quick Start Overview**

This guide provides copy-paste commands for implementing the NEXUS SSOT system with dynamic API aliasing. Three agents can work in parallel with zero dependencies.

---

## 🤖 **Agent 1: SSOT Core & API Registry**

### **Setup Commands**

```bash
# Copy and paste these commands
cd /Users/Arief/Desktop/Nexus

# Create SSOT registry directory
mkdir -p backend/services
mkdir -p backend/routes
mkdir -p config
mkdir -p tests

# Install dependencies
pip install fastapi uvicorn aiohttp pydantic sqlalchemy psycopg2-binary redis

# Create SSOT registry
cat > backend/services/ssot_registry.py << 'EOF'
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class OperationType(Enum):
    QUERY = "query"
    PROPOSE_CHANGE = "propose_change"
    EXECUTE_ACTION = "execute_action"
    AUDIT = "audit"

@dataclass
class SSOTQuery:
    query_type: str
    context: str
    parameters: Dict[str, Any]
    timestamp: datetime
    requester: str

@dataclass
class SSOTResponse:
    success: bool
    data: Any
    message: str
    timestamp: datetime
    operation_id: str

class SSOTRegistry:
    def __init__(self):
        self.anchors = {}
        self.aliases = {}
        self.contexts = {}
        self.audit_log = []

    def register_anchor(self, anchor_id: str, config: dict):
        """Register a new SSOT anchor"""
        self.anchors[anchor_id] = {
            **config,
            "registered_at": datetime.utcnow().isoformat()
        }
        self._log_operation("register_anchor", anchor_id, config)

    def add_alias(self, alias: str, canonical: str, context: str, config: dict):
        """Add a new alias for an anchor"""
        if context not in self.aliases:
            self.aliases[context] = {}

        self.aliases[context][alias] = {
            "canonical": canonical,
            "context": context,
            "created_at": datetime.utcnow().isoformat(),
            **config
        }
        self._log_operation("add_alias", alias, {"canonical": canonical, "context": context})

    def resolve_alias(self, alias: str, context: str) -> Optional[str]:
        """Resolve alias to canonical name"""
        if context in self.aliases and alias in self.aliases[context]:
            return self.aliases[context][alias]["canonical"]
        return None

    def validate_alias(self, alias: str, context: str) -> bool:
        """Validate alias against governance rules"""
        # Basic validation rules
        if len(alias) < 3 or len(alias) > 50:
            return False
        if not alias.replace("-", "").replace("_", "").isalnum():
            return False
        return True

    def _log_operation(self, operation: str, target: str, details: dict):
        """Log operation for audit"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "target": target,
            "details": details
        }
        self.audit_log.append(log_entry)
EOF

# Create API alias router
cat > backend/routes/api_alias_router.py << 'EOF'
from fastapi import APIRouter, HTTPException
from backend.services.ssot_registry import SSOTRegistry

router = APIRouter()
registry = SSOTRegistry()

@router.get("/{alias_path:path}")
async def route_alias_request(alias_path: str, context: str = "default"):
    """Route alias requests to canonical endpoints"""
    try:
        canonical = registry.resolve_alias(alias_path, context)
        if not canonical:
            raise HTTPException(status_code=404, detail="Alias not found")

        # In a real implementation, this would forward to the canonical endpoint
        return {
            "alias": alias_path,
            "canonical": canonical,
            "context": context,
            "message": "Alias resolved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/aliases")
async def create_alias(alias: str, canonical: str, context: str, description: str):
    """Create a new alias"""
    try:
        if not registry.validate_alias(alias, context):
            raise HTTPException(status_code=400, detail="Invalid alias format")

        registry.add_alias(alias, canonical, context, {"description": description})
        return {"message": "Alias created successfully", "alias": alias}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
EOF

# Create governance configuration
cat > config/alias_governance.yaml << 'EOF'
alias_governance:
  version: "1.0"
  rules:
    uniqueness:
      within_context: true
      across_contexts: false
    naming:
      pattern: "^[a-z0-9-]+$"
      min_length: 3
      max_length: 50
    expiration:
      temporary_aliases: true
      default_ttl: "90d"
      max_ttl: "1y"

  contexts:
    system:
      permissions: ["ssot_maintainers"]
      approval_required: true
    application:
      permissions: ["team_approval"]
      approval_required: true
    frenly_ai:
      permissions: ["ai_team"]
      approval_required: true
    migration:
      permissions: ["temporary_only"]
      approval_required: false
      auto_expire: true

  audit:
    log_all_changes: true
    retention_period: "7y"
    external_storage: "s3://nexus-audit-logs"
EOF

# Create tests
cat > tests/test_ssot_registry.py << 'EOF'
import pytest
from backend.services.ssot_registry import SSOTRegistry

def test_register_anchor():
    registry = SSOTRegistry()
    config = {
        "id": "user-api",
        "family": "api",
        "description": "User management API",
        "format": "openapi-3.0.yaml"
    }
    registry.register_anchor("user-api", config)
    assert "user-api" in registry.anchors

def test_add_alias():
    registry = SSOTRegistry()
    registry.register_anchor("user-api", {})
    registry.add_alias("user-management", "user-api", "frontend", {})
    assert registry.resolve_alias("user-management", "frontend") == "user-api"

def test_alias_validation():
    registry = SSOTRegistry()
    assert registry.validate_alias("valid-alias", "frontend") == True
    assert registry.validate_alias("invalid_alias!", "frontend") == False
EOF

# Test the implementation
python3 -m pytest tests/test_ssot_registry.py -v
python3 -c "from backend.services.ssot_registry import SSOTRegistry; print('SSOT Registry imported successfully')"
```

---

## 🤖 **Agent 2: Data Schema & Deployment**

### **Setup Commands**

```bash
# Copy and paste these commands
cd /Users/Arief/Desktop/Nexus

# Create database schema
mkdir -p backend/database
cat > backend/database/schema.sql << 'EOF'
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
EOF

# Create Redis schema
mkdir -p backend/cache
cat > backend/cache/redis_schema.json << 'EOF'
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
EOF

# Create Kubernetes manifests
mkdir -p k8s
cat > k8s/unified-manifests.yaml << 'EOF'
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
EOF

# Create Docker Compose
cat > docker-compose.unified.yml << 'EOF'
version: '3.8'

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

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: nexus-network
EOF

# Create environment configuration
mkdir -p config
cat > config/environments.yaml << 'EOF'
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
EOF

# Test the implementation
docker-compose -f docker-compose.unified.yml config
kubectl apply -f k8s/unified-manifests.yaml --dry-run=client
```

---

## 🤖 **Agent 3: Automation & Frenly AI**

### **Setup Commands**

```bash
# Copy and paste these commands
cd /Users/Arief/Desktop/Nexus

# Create Frenly AI SSOT operator
mkdir -p frenly_ai/backend
mkdir -p frenly_ai/tests
mkdir -p .github/workflows
mkdir -p monitoring
mkdir -p security

cat > frenly_ai/backend/ssot_operator.py << 'EOF'
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class OperationType(Enum):
    QUERY = "query"
    PROPOSE_CHANGE = "propose_change"
    EXECUTE_ACTION = "execute_action"
    AUDIT = "audit"

@dataclass
class SSOTQuery:
    query_type: str
    context: str
    parameters: Dict[str, Any]
    timestamp: datetime
    requester: str

@dataclass
class SSOTResponse:
    success: bool
    data: Any
    message: str
    timestamp: datetime
    operation_id: str

class FrenlySSOTOperator:
    def __init__(self, ssot_registry_url: str, api_key: str):
        self.ssot_registry_url = ssot_registry_url
        self.api_key = api_key
        self.operation_log = []
        self.alias_cache = {}
        self.context_mappings = {
            "frenly_ai": "ai_operations",
            "system": "system_operations",
            "migration": "migration_operations"
        }

    async def query_ssot(self, query: SSOTQuery) -> SSOTResponse:
        """Query SSOT registry with context-aware resolution"""
        try:
            # Resolve aliases based on context
            resolved_query = await self._resolve_aliases(query)

            # Execute query against SSOT registry
            result = await self._execute_query(resolved_query)

            # Log operation for audit
            await self._log_operation(query, result)

            return SSOTResponse(
                success=True,
                data=result,
                message="Query executed successfully",
                timestamp=datetime.utcnow(),
                operation_id=self._generate_operation_id()
            )
        except Exception as e:
            return SSOTResponse(
                success=False,
                data=None,
                message=f"Query failed: {str(e)}",
                timestamp=datetime.utcnow(),
                operation_id=self._generate_operation_id()
            )

    async def propose_change(self, change_type: str, target: str,
                           changes: Dict[str, Any], context: str) -> SSOTResponse:
        """Propose changes to SSOT (requires human approval)"""
        try:
            # Validate change proposal
            validation_result = await self._validate_change_proposal(
                change_type, target, changes, context
            )

            if not validation_result["valid"]:
                return SSOTResponse(
                    success=False,
                    data=None,
                    message=f"Change proposal invalid: {validation_result['reason']}",
                    timestamp=datetime.utcnow(),
                    operation_id=self._generate_operation_id()
                )

            # Create change proposal
            proposal = {
                "id": self._generate_operation_id(),
                "type": change_type,
                "target": target,
                "changes": changes,
                "context": context,
                "proposed_by": "frenly_ai",
                "proposed_at": datetime.utcnow().isoformat(),
                "status": "pending_approval"
            }

            # Submit proposal for human review
            await self._submit_proposal(proposal)

            return SSOTResponse(
                success=True,
                data=proposal,
                message="Change proposal submitted for review",
                timestamp=datetime.utcnow(),
                operation_id=proposal["id"]
            )
        except Exception as e:
            return SSOTResponse(
                success=False,
                data=None,
                message=f"Change proposal failed: {str(e)}",
                timestamp=datetime.utcnow(),
                operation_id=self._generate_operation_id()
            )

    async def _resolve_aliases(self, query: SSOTQuery) -> SSOTQuery:
        """Resolve aliases based on context"""
        # Implementation for alias resolution
        return query

    async def _execute_query(self, query: SSOTQuery) -> Any:
        """Execute query against SSOT registry"""
        # Implementation for query execution
        return {"result": "query_executed"}

    async def _log_operation(self, query: SSOTQuery, result: Any):
        """Log operation for audit trail"""
        operation_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation_type": query.query_type,
            "context": query.context,
            "parameters": query.parameters,
            "result": result,
            "requester": query.requester
        }
        self.operation_log.append(operation_log)

    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        return f"frenly_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(str(self.operation_log))}"

    async def _validate_change_proposal(self, change_type: str, target: str,
                                      changes: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Validate change proposal"""
        return {"valid": True, "reason": "Valid proposal"}

    async def _submit_proposal(self, proposal: Dict[str, Any]):
        """Submit proposal for human review"""
        # Implementation for proposal submission
        pass
EOF

# Create SSOT integration layer
cat > frenly_ai/backend/ssot_integration.py << 'EOF'
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

class SSOTIntegrationLayer:
    def __init__(self, ssot_registry_url: str, api_key: str):
        self.ssot_registry_url = ssot_registry_url
        self.api_key = api_key
        self.session = None
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_anchor(self, anchor_id: str, context: str = "default") -> Optional[Dict]:
        """Get SSOT anchor by ID with context-aware alias resolution"""
        try:
            # Check cache first
            cache_key = f"{anchor_id}:{context}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.utcnow().timestamp() - timestamp < self.cache_ttl:
                    return cached_data

            # Query SSOT registry
            async with self.session.get(
                f"{self.ssot_registry_url}/anchors/{anchor_id}",
                params={"context": context}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Cache the result
                    self.cache[cache_key] = (data, datetime.utcnow().timestamp())
                    return data
                else:
                    return None
        except Exception as e:
            print(f"Error getting anchor {anchor_id}: {e}")
            return None

    async def resolve_alias(self, alias: str, context: str) -> Optional[str]:
        """Resolve alias to canonical name"""
        try:
            async with self.session.get(
                f"{self.ssot_registry_url}/aliases/{alias}",
                params={"context": context}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("canonical_name")
                else:
                    return None
        except Exception as e:
            print(f"Error resolving alias {alias}: {e}")
            return None
EOF

# Create CI/CD pipeline
cat > .github/workflows/ssot_automation.yml << 'EOF'
name: SSOT Automation Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

env:
  NEXUS_ENV: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}

jobs:
  ssot-validation:
    name: SSOT Validation
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r backend/requirements.txt

    - name: Validate SSOT Manifest
      run: |
        python3 scripts/validate_ssot.py ssot_plan/ssot_manifest_proposal.yaml

    - name: Verify Lockfiles
      run: |
        python3 scripts/verify_lockfiles.py ssot_plan/locks

    - name: Check Alias Consistency
      run: |
        python3 scripts/check_alias_consistency.py

  frenly-ai-integration:
    name: Frenly AI Integration
    runs-on: ubuntu-latest
    needs: ssot-validation
    steps:
    - uses: actions/checkout@v4

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install Frenly AI dependencies
      run: |
        pip install -r frenly_ai/requirements.txt

    - name: Test SSOT Operator
      run: |
        python3 -m pytest frenly_ai/tests/test_ssot_operator.py -v

    - name: Test SSOT Integration
      run: |
        python3 -m pytest frenly_ai/tests/test_ssot_integration.py -v

  deployment-orchestration:
    name: Deployment Orchestration
    runs-on: ubuntu-latest
    needs: [ssot-validation, frenly-ai-integration]
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v4

    - name: Setup kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'

    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/unified-manifests.yaml
        kubectl rollout status deployment/nexus-backend -n nexus-platform
EOF

# Create monitoring configuration
cat > monitoring/ssot_metrics.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: ssot-metrics-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    rule_files:
      - "ssot_rules.yml"

    scrape_configs:
      - job_name: 'ssot-registry'
        static_configs:
          - targets: ['ssot-registry:8000']
        metrics_path: '/metrics'
        scrape_interval: 30s

      - job_name: 'frenly-ai-operator'
        static_configs:
          - targets: ['frenly-ai-operator:8000']
        metrics_path: '/metrics'
        scrape_interval: 30s

  ssot_rules.yml: |
    groups:
      - name: ssot_alerts
        rules:
          - alert: SSOTRegistryDown
            expr: up{job="ssot-registry"} == 0
            for: 1m
            labels:
              severity: critical
            annotations:
              summary: "SSOT Registry is down"
              description: "SSOT Registry has been down for more than 1 minute"

          - alert: HighAliasResolutionLatency
            expr: alias_resolution_duration_seconds > 0.1
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "High alias resolution latency"
              description: "Alias resolution is taking longer than 100ms"
EOF

# Create security policies
cat > security/ssot_policies.yaml << 'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: ssot-security-policies
  namespace: nexus-platform
data:
  security_policies.yaml: |
    version: "1.0"
    generated_at: "2025-01-27T12:30:00Z"

    access_control:
      ssot_registry:
        read: ["nexus-platform-team", "nexus-ai-team"]
        write: ["nexus-platform-team"]
        admin: ["nexus-platform-team"]

      alias_management:
        read: ["all_team_members"]
        write: ["code_owners"]
        admin: ["nexus-platform-team"]

      frenly_ai_operations:
        read: ["nexus-ai-team", "nexus-platform-team"]
        write: ["nexus-ai-team"]
        admin: ["nexus-platform-team"]

    audit_requirements:
      log_all_changes: true
      retention_period: "7y"
      external_storage: "s3://nexus-audit-logs"
      immutable_logs: true
      encryption: true

    security_scanning:
      vulnerability_scanning:
        enabled: true
        schedule: "0 2 * * *"  # Daily at 2 AM
        severity_threshold: "high"
        auto_remediate: false

      dependency_scanning:
        enabled: true
        schedule: "0 3 * * *"  # Daily at 3 AM
        check_updates: true
        auto_update: false
EOF

# Create tests
cat > frenly_ai/tests/test_ssot_operator.py << 'EOF'
import pytest
from frenly_ai.backend.ssot_operator import FrenlySSOTOperator, SSOTQuery
from datetime import datetime

def test_ssot_operator_initialization():
    operator = FrenlySSOTOperator("http://localhost:8000", "test-key")
    assert operator.ssot_registry_url == "http://localhost:8000"
    assert operator.api_key == "test-key"

def test_ssot_query_creation():
    query = SSOTQuery(
        query_type="test",
        context="frenly_ai",
        parameters={"test": "value"},
        timestamp=datetime.utcnow(),
        requester="test_user"
    )
    assert query.query_type == "test"
    assert query.context == "frenly_ai"

@pytest.mark.asyncio
async def test_query_ssot():
    operator = FrenlySSOTOperator("http://localhost:8000", "test-key")
    query = SSOTQuery(
        query_type="test",
        context="frenly_ai",
        parameters={"test": "value"},
        timestamp=datetime.utcnow(),
        requester="test_user"
    )

    response = await operator.query_ssot(query)
    assert response.success == True
    assert response.message == "Query executed successfully"
EOF

# Test the implementation
python3 -m pytest frenly_ai/tests/test_ssot_operator.py -v
python3 -c "from frenly_ai.backend.ssot_operator import FrenlySSOTOperator; print('SSOT Operator imported successfully')"
```

---

## 🔍 **Validation Commands**

### **Test All Systems**

```bash
# Copy and paste these commands
cd /Users/Arief/Desktop/Nexus

# Test SSOT validation
python3 scripts/validate_ssot.py ssot_plan/ssot_manifest_proposal.yaml
python3 scripts/verify_lockfiles.py ssot_plan/locks

# Test database schema
docker-compose -f docker-compose.unified.yml up postgres -d
sleep 10
psql -h localhost -U nexus -d nexus -f backend/database/schema.sql

# Test Redis schema
docker-compose -f docker-compose.unified.yml up redis -d
sleep 5
redis-cli -h localhost -p 6379 -a redis123 ping

# Test Kubernetes manifests
kubectl apply -f k8s/unified-manifests.yaml --dry-run=client

# Test Frenly AI
python3 -m pytest frenly_ai/tests/test_ssot_operator.py -v
```

---

## 📊 **Success Metrics**

### **Agent 1 Success**

- [ ] SSOT registry operational
- [ ] API aliasing working
- [ ] Governance rules enforced
- [ ] Audit logging active

### **Agent 2 Success**

- [ ] Database schema consolidated
- [ ] Redis schema configured
- [ ] Kubernetes manifests optimized
- [ ] Docker Compose unified

### **Agent 3 Success**

- [ ] Frenly AI SSOT operator
- [ ] CI/CD pipeline consolidated
- [ ] Monitoring configured
- [ ] Security policies enforced

---

## 🎯 **Final Checklist**

- [ ] All three agents have completed their tasks
- [ ] SSOT system is operational
- [ ] Dynamic API aliasing is working
- [ ] Frenly AI is operating as SSOT operator
- [ ] All validation commands pass
- [ ] Documentation is complete

---

**Ready to implement? Copy the commands and start building! 🚀**
