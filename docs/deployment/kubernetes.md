# NEXUS Platform - Kubernetes Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the NEXUS Platform on Kubernetes, including service architecture, configuration management, scaling procedures, and troubleshooting.

## Prerequisites

### Kubernetes Cluster Requirements

- **Kubernetes Version**: 1.20+
- **Node Count**: Minimum 3 nodes
- **CPU**: 8+ cores total
- **Memory**: 16GB+ RAM total
- **Storage**: 100GB+ persistent storage

### Required Tools

- kubectl (Kubernetes CLI)
- Helm (Package manager)
- Docker (Image building)
- kubectx (Context switching)

## Service Architecture

### Core Services

1. **nexus-postgres** - PostgreSQL database
2. **nexus-redis** - Redis cache
3. **nexus-backend** - FastAPI backend service
4. **nexus-frenly-ai** - AI service
5. **nexus-frontend** - React frontend
6. **nexus-nginx** - Reverse proxy

### Service Dependencies

```
frontend → nginx → backend → postgres
                → redis
                → frenly-ai → postgres
                           → redis
```

## Configuration Management

### Namespace

All services are deployed in the `nexus-platform` namespace:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: nexus-platform
  labels:
    app: nexus
    environment: production
    version: v3.0.0
```

### ConfigMaps

Centralized configuration using ConfigMaps:

```yaml
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
  log_level: "info"
  cors_origins: "https://nexus.com,https://www.nexus.com"
```

### Secrets

Sensitive data stored in Kubernetes Secrets:

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

## Deployment Procedures

### 1. Create Namespace

```bash
kubectl create namespace nexus-platform
```

### 2. Create Secrets

```bash
# Create secrets from environment variables
kubectl create secret generic nexus-secrets \
  --from-literal=database_password="your_db_password" \
  --from-literal=redis_password="your_redis_password" \
  --from-literal=jwt_secret="your_jwt_secret" \
  --from-literal=openai_api_key="your_openai_key" \
  --from-literal=anthropic_api_key="your_anthropic_key" \
  --namespace=nexus-platform
```

### 3. Deploy Database

```bash
# Deploy PostgreSQL
kubectl apply -f k8s/unified-manifests.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=nexus-postgres -n nexus-platform --timeout=300s
```

### 4. Deploy Backend Services

```bash
# Deploy Redis
kubectl apply -f k8s/redis-deployment.yaml

# Deploy Backend
kubectl apply -f k8s/backend-deployment.yaml

# Deploy Frenly AI
kubectl apply -f k8s/frenly-ai-deployment.yaml
```

### 5. Deploy Frontend

```bash
# Deploy Frontend
kubectl apply -f k8s/frontend-deployment.yaml
```

### 6. Configure Ingress

```bash
# Deploy Ingress
kubectl apply -f k8s/ingress.yaml

# Verify ingress
kubectl get ingress -n nexus-platform
```

## Scaling Procedures

### Horizontal Pod Autoscaling (HPA)

The platform includes HPA for automatic scaling:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nexus-backend-hpa
  namespace: nexus-platform
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
```

### Manual Scaling

```bash
# Scale backend service
kubectl scale deployment nexus-backend --replicas=5 -n nexus-platform

# Scale frontend service
kubectl scale deployment nexus-frontend --replicas=3 -n nexus-platform
```

### Vertical Scaling

```bash
# Update resource limits
kubectl patch deployment nexus-backend -n nexus-platform -p '{"spec":{"template":{"spec":{"containers":[{"name":"backend","resources":{"limits":{"memory":"2Gi","cpu":"1000m"}}}]}}}}'
```

## Monitoring and Observability

### Health Checks

All services include comprehensive health checks:

```yaml
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
```

### Prometheus Integration

Services are annotated for Prometheus scraping:

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
```

### Logging

Centralized logging using Fluentd or similar:

```yaml
volumeMounts:
  - name: logs
    mountPath: /app/logs

volumes:
  - name: logs
    emptyDir: {}
```

## Troubleshooting

### Common Issues

#### 1. Pod Startup Failures

```bash
# Check pod status
kubectl get pods -n nexus-platform

# Check pod logs
kubectl logs -f deployment/nexus-backend -n nexus-platform

# Check pod events
kubectl describe pod <pod-name> -n nexus-platform
```

#### 2. Service Discovery Issues

```bash
# Check services
kubectl get services -n nexus-platform

# Test service connectivity
kubectl exec -it <pod-name> -n nexus-platform -- curl http://nexus-backend-service:80/health
```

#### 3. Database Connection Issues

```bash
# Check database pod
kubectl get pods -l app=nexus-postgres -n nexus-platform

# Check database logs
kubectl logs -f deployment/nexus-postgres -n nexus-platform

# Test database connection
kubectl exec -it <backend-pod> -n nexus-platform -- psql $DATABASE_URL
```

#### 4. Ingress Issues

```bash
# Check ingress status
kubectl get ingress -n nexus-platform

# Check ingress controller
kubectl get pods -n ingress-nginx

# Test ingress connectivity
curl -H "Host: api.nexus.com" http://<ingress-ip>/health
```

### Debugging Commands

#### Check Resource Usage

```bash
# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n nexus-platform

# Check resource quotas
kubectl describe quota -n nexus-platform
```

#### Check Network Connectivity

```bash
# Test DNS resolution
kubectl exec -it <pod-name> -n nexus-platform -- nslookup nexus-backend-service

# Test port connectivity
kubectl exec -it <pod-name> -n nexus-platform -- telnet nexus-backend-service 80
```

#### Check Configuration

```bash
# Check ConfigMaps
kubectl get configmaps -n nexus-platform
kubectl describe configmap nexus-config -n nexus-platform

# Check Secrets
kubectl get secrets -n nexus-platform
kubectl describe secret nexus-secrets -n nexus-platform
```

## Security Considerations

### Network Policies

Implement network policies for service isolation:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nexus-network-policy
  namespace: nexus-platform
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: nexus-platform
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: nexus-platform
```

### Pod Security Policies

Implement pod security policies:

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: nexus-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - "configMap"
    - "emptyDir"
    - "projected"
    - "secret"
    - "downwardAPI"
    - "persistentVolumeClaim"
```

### RBAC Configuration

Implement role-based access control:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: nexus-platform
  name: nexus-role
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps", "secrets"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

## Backup and Recovery

### Database Backup

```bash
# Create database backup
kubectl exec -it <postgres-pod> -n nexus-platform -- pg_dump -U nexus nexus > backup.sql

# Restore database
kubectl exec -i <postgres-pod> -n nexus-platform -- psql -U nexus nexus < backup.sql
```

### Configuration Backup

```bash
# Backup ConfigMaps
kubectl get configmaps -n nexus-platform -o yaml > configmaps-backup.yaml

# Backup Secrets
kubectl get secrets -n nexus-platform -o yaml > secrets-backup.yaml
```

### Persistent Volume Backup

```bash
# Create volume snapshot
kubectl create -f volume-snapshot.yaml

# Restore from snapshot
kubectl create -f volume-restore.yaml
```

## Performance Optimization

### Resource Optimization

- Set appropriate resource requests and limits
- Use node affinity for workload placement
- Implement pod disruption budgets
- Use horizontal pod autoscaling

### Network Optimization

- Use service mesh for traffic management
- Implement circuit breakers
- Configure load balancing
- Optimize DNS resolution

### Storage Optimization

- Use appropriate storage classes
- Implement storage quotas
- Use volume snapshots for backups
- Optimize I/O performance

## Maintenance Procedures

### Rolling Updates

```bash
# Update deployment
kubectl set image deployment/nexus-backend backend=nexus/backend:v3.1.0 -n nexus-platform

# Check rollout status
kubectl rollout status deployment/nexus-backend -n nexus-platform

# Rollback if needed
kubectl rollout undo deployment/nexus-backend -n nexus-platform
```

### Maintenance Windows

```bash
# Drain node for maintenance
kubectl drain <node-name> --ignore-daemonsets

# Uncordon node after maintenance
kubectl uncordon <node-name>
```

### Cleanup Procedures

```bash
# Delete unused resources
kubectl delete pods --field-selector=status.phase=Succeeded -n nexus-platform

# Clean up old images
kubectl delete pods --field-selector=status.phase=Failed -n nexus-platform
```

## Monitoring and Alerting

### Prometheus Metrics

- CPU and memory usage
- Request rates and latencies
- Error rates
- Custom business metrics

### Grafana Dashboards

- Service overview
- Resource utilization
- Application metrics
- Business KPIs

### Alerting Rules

- High error rates
- Resource exhaustion
- Service downtime
- Performance degradation

## Conclusion

This Kubernetes deployment guide provides comprehensive instructions for deploying, scaling, and maintaining the NEXUS Platform. Follow the procedures carefully and monitor the system continuously for optimal performance and reliability.
