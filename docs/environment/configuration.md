# NEXUS Platform - Environment Configuration Guide

## Overview

This guide provides comprehensive instructions for managing environment configurations across development, staging, and production environments, including secret management, feature flags, and monitoring configuration.

## Environment Structure

### Environment Types

1. **Development** - Local development environment
2. **Staging** - Pre-production testing environment
3. **Production** - Live production environment

### Configuration Hierarchy

```
config/
├── ssot/
│   └── environment.env          # Single source of truth
├── environments.yaml            # Environment-specific settings
├── development/
│   └── config.json             # Dev-specific configs
├── staging/
│   └── config.json             # Staging-specific configs
└── production/
    └── config.json             # Production-specific configs
```

## Environment Configuration

### Development Environment

```yaml
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
```

### Staging Environment

```yaml
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
```

### Production Environment

```yaml
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
```

## Secret Management

### Environment Variables

Sensitive data is managed through environment variables:

```bash
# Database passwords
STAGING_DB_PASSWORD=your_staging_password
PROD_DB_PASSWORD=your_production_password

# Redis passwords
STAGING_REDIS_PASSWORD=your_staging_redis_password
PROD_REDIS_PASSWORD=your_production_redis_password

# JWT secrets
STAGING_JWT_SECRET=your_staging_jwt_secret
PROD_JWT_SECRET=your_production_jwt_secret

# API keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Kubernetes Secrets

For Kubernetes deployments, secrets are managed through Kubernetes Secrets:

```yaml
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
  openai_api_key: <base64-encoded>
  anthropic_api_key: <base64-encoded>
```

### Docker Secrets

For Docker deployments, secrets are managed through Docker secrets:

```bash
# Create Docker secrets
echo "your_password" | docker secret create db_password -
echo "your_redis_password" | docker secret create redis_password -
echo "your_jwt_secret" | docker secret create jwt_secret -
```

## Feature Flags

### Feature Flag Configuration

Feature flags are managed through the environment configuration:

```yaml
features:
  ssot_aliasing: true # Enable SSOT aliasing system
  audit_logging: true # Enable audit logging
  rate_limiting: true # Enable rate limiting
  caching: true # Enable caching
  security_scanning: true # Enable security scanning
  ai_features: true # Enable AI features
  real_time_updates: true # Enable real-time updates
  advanced_analytics: true # Enable advanced analytics
```

### Dynamic Feature Flags

Feature flags can be toggled at runtime:

```python
# Python example
from config import get_feature_flag

if get_feature_flag('ai_features'):
    # Enable AI features
    pass

if get_feature_flag('real_time_updates'):
    # Enable real-time updates
    pass
```

### Feature Flag Management

```bash
# Enable feature flag
kubectl patch configmap nexus-config -n nexus-platform --patch '{"data":{"feature_ai_features":"true"}}'

# Disable feature flag
kubectl patch configmap nexus-config -n nexus-platform --patch '{"data":{"feature_ai_features":"false"}}'
```

## Monitoring Configuration

### Log Levels

Different log levels for different environments:

- **Development**: DEBUG - Detailed logging for debugging
- **Staging**: INFO - Informational logging for testing
- **Production**: WARN - Warning and error logging only

### Log Configuration

```yaml
monitoring:
  enabled: true
  level: info
  log_file: /var/log/nexus/nexus.log
  max_file_size: 100MB
  max_files: 10
  format: json
  include_stack_traces: true
```

### Metrics Configuration

```yaml
metrics:
  enabled: true
  port: 9090
  path: /metrics
  interval: 30s
  include_system_metrics: true
  include_business_metrics: true
```

### Alerting Configuration

```yaml
alerting:
  enabled: true
  webhook_url: https://hooks.slack.com/your-webhook
  channels:
    - general
    - alerts
  rules:
    - name: high_error_rate
      condition: error_rate > 5%
      severity: critical
    - name: high_cpu_usage
      condition: cpu_usage > 80%
      severity: warning
```

## Environment Setup Procedures

### 1. Development Environment Setup

```bash
# Clone repository
git clone https://github.com/nexus/platform.git
cd platform

# Copy environment file
cp config/ssot/environment.env .env

# Update development settings
nano .env

# Start services
docker-compose up -d

# Verify setup
curl http://localhost:8000/health
```

### 2. Staging Environment Setup

```bash
# Set environment variables
export STAGING_DB_PASSWORD="your_staging_password"
export STAGING_REDIS_PASSWORD="your_staging_redis_password"
export STAGING_JWT_SECRET="your_staging_jwt_secret"

# Deploy to staging
kubectl apply -f k8s/staging/

# Verify deployment
kubectl get pods -n nexus-staging
```

### 3. Production Environment Setup

```bash
# Set environment variables
export PROD_DB_PASSWORD="your_production_password"
export PROD_REDIS_PASSWORD="your_production_redis_password"
export PROD_JWT_SECRET="your_production_jwt_secret"

# Deploy to production
kubectl apply -f k8s/production/

# Verify deployment
kubectl get pods -n nexus-production
```

## Configuration Validation

### Environment Validation Script

```python
#!/usr/bin/env python3
import os
import yaml
import sys

def validate_environment():
    """Validate environment configuration"""
    required_vars = [
        'DATABASE_URL',
        'REDIS_URL',
        'JWT_SECRET_KEY',
        'API_BASE_URL'
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)

    print("Environment validation passed")

if __name__ == "__main__":
    validate_environment()
```

### Configuration Testing

```bash
# Test configuration
python scripts/validate_config.py

# Test database connection
python scripts/test_database.py

# Test Redis connection
python scripts/test_redis.py

# Test API endpoints
python scripts/test_api.py
```

## Security Considerations

### Secret Rotation

Regular rotation of secrets and passwords:

```bash
# Rotate database password
kubectl create secret generic nexus-secrets-new \
  --from-literal=database_password="new_password" \
  --namespace=nexus-platform

# Update deployment
kubectl patch deployment nexus-backend \
  --patch '{"spec":{"template":{"spec":{"containers":[{"name":"backend","env":[{"name":"DATABASE_PASSWORD","valueFrom":{"secretKeyRef":{"name":"nexus-secrets-new","key":"database_password"}}}]}]}}}}' \
  --namespace=nexus-platform
```

### Access Control

Implement proper access control for configuration:

```yaml
# RBAC for configuration access
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: nexus-platform
  name: config-manager
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list", "watch"]
```

### Audit Logging

Audit all configuration changes:

```yaml
audit:
  enabled: true
  log_config_changes: true
  log_secret_access: true
  retention_days: 90
```

## Troubleshooting

### Common Issues

#### 1. Missing Environment Variables

```bash
# Check environment variables
env | grep NEXUS

# Check Kubernetes secrets
kubectl get secrets -n nexus-platform
kubectl describe secret nexus-secrets -n nexus-platform
```

#### 2. Configuration Conflicts

```bash
# Check configuration
kubectl get configmaps -n nexus-platform
kubectl describe configmap nexus-config -n nexus-platform

# Compare configurations
kubectl get configmap nexus-config -n nexus-platform -o yaml > current-config.yaml
diff current-config.yaml expected-config.yaml
```

#### 3. Feature Flag Issues

```bash
# Check feature flags
kubectl get configmap nexus-config -n nexus-platform -o jsonpath='{.data.feature_*}'

# Test feature flag
curl -H "X-Feature-Flag: ai_features" http://api.nexus.com/health
```

### Debug Commands

```bash
# Check pod environment
kubectl exec -it <pod-name> -n nexus-platform -- env

# Check configuration files
kubectl exec -it <pod-name> -n nexus-platform -- cat /app/config/environment.env

# Check logs
kubectl logs -f <pod-name> -n nexus-platform
```

## Best Practices

### Configuration Management

1. Use environment variables for sensitive data
2. Keep configuration files in version control
3. Use configuration validation
4. Implement configuration drift detection
5. Regular configuration audits

### Secret Management

1. Rotate secrets regularly
2. Use strong, unique passwords
3. Implement secret encryption
4. Monitor secret access
5. Use least privilege access

### Feature Flags

1. Use feature flags for new features
2. Test feature flags in staging
3. Monitor feature flag usage
4. Clean up unused feature flags
5. Document feature flag behavior

### Monitoring

1. Monitor configuration changes
2. Alert on configuration errors
3. Track feature flag usage
4. Monitor secret access
5. Regular security audits

## Conclusion

This environment configuration guide provides comprehensive instructions for managing configurations across all environments. Follow the procedures carefully and implement proper security measures for optimal configuration management.
