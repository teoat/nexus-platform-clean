# NEXUS Platform Deployment Guide

This guide covers the deployment procedures for the NEXUS Platform across different environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Overview](#environment-overview)
- [Local Development](#local-development)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Monitoring Setup](#monitoring-setup)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Infrastructure Requirements

- **Kubernetes Cluster**: 1.24+ with 3+ nodes
- **PostgreSQL**: 15.x with high availability
- **Redis**: 7.x with clustering
- **Load Balancer**: AWS ALB/NLB or NGINX Ingress
- **Storage**: S3-compatible object storage
- **CDN**: CloudFront or similar
- **Monitoring**: Prometheus + Grafana stack

### Access Requirements

- AWS/GCP/Azure account with appropriate permissions
- Docker registry access (ECR/GCR/ACR)
- Kubernetes cluster admin access
- Database admin access
- DNS management access

### Tools Required

```bash
# Core tools
kubectl >= 1.24
helm >= 3.9
docker >= 20.10
awscli >= 2.0

# Additional tools
kustomize >= 4.5
stern >= 1.21
k9s >= 0.25
```

## Environment Overview

### Environment Matrix

| Environment | Purpose             | URL Pattern               | Retention | Backup    |
| ----------- | ------------------- | ------------------------- | --------- | --------- |
| Development | Feature development | dev.nexusplatform.com     | 30 days   | Daily     |
| Staging     | Integration testing | staging.nexusplatform.com | 90 days   | Daily     |
| Production  | Live system         | api.nexusplatform.com     | 1 year    | Hourly    |
| DR          | Disaster recovery   | dr.nexusplatform.com      | 1 year    | Real-time |

### Service Architecture

```
Internet
    ↓
[Load Balancer]
    ↓
[API Gateway] ← JWT Auth, Rate Limiting
    ↓
[Service Mesh - Istio]
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│ User Service    │ Transaction     │ Analytics       │
│ • Auth & Users  │ • Financial Tx  │ • Reporting     │
│ • Sessions      │ • Categories    │ • Insights      │
│ • Preferences   │ • Multi-currency│ • Predictions   │
└─────────────────┴─────────────────┴─────────────────┘
┌─────────────────┬─────────────────┬─────────────────┐
│ Audit Service   │ Notification    │ Backup Service  │
│ • Security Logs │ • Email/SMS     │ • Data Backup   │
│ • Compliance    │ • Push Notif.   │ • Recovery      │
│ • Audit Trails  │ • Templates     │ • Encryption    │
└─────────────────┴─────────────────┴─────────────────┘
```

## Local Development

### Quick Start with Docker Compose

```bash
# Clone repository
git clone https://github.com/your-org/nexus-platform.git
cd nexus-platform

# Start all services
docker-compose up -d

# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health  # user-service
curl http://localhost:8002/health  # transaction-service

# View logs
docker-compose logs -f api-gateway
```

### Development Environment Setup

```bash
# Create namespace
kubectl create namespace nexus-dev

# Deploy using kustomize
kubectl apply -k k8s/overlays/dev/

# Wait for deployments
kubectl wait --for=condition=available --timeout=300s \
  deployment/nexus-api-gateway -n nexus-dev

# Port forward for local access
kubectl port-forward -n nexus-dev svc/nexus-api-gateway 8000:80

# Check deployment status
kubectl get pods -n nexus-dev
kubectl get services -n nexus-dev
```

## Staging Deployment

### Automated Deployment (CI/CD)

Staging deployments are automatically triggered by GitHub Actions on pushes to the `develop` branch.

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-region: us-east-1

      - name: Deploy to EKS
        run: |
          aws eks update-kubeconfig --name nexus-staging
          kubectl apply -k k8s/overlays/staging/
          kubectl rollout status deployment/nexus-api-gateway -n nexus-staging
```

### Manual Staging Deployment

```bash
# Set kubectl context
aws eks update-kubeconfig --name nexus-staging

# Deploy infrastructure
kubectl apply -f k8s/infrastructure/staging/

# Deploy application
kubectl apply -k k8s/overlays/staging/

# Run database migrations
kubectl exec -n nexus-staging deployment/nexus-migration -- \
  alembic upgrade head

# Verify deployment
kubectl get pods -n nexus-staging
kubectl get ingress -n nexus-staging

# Run smoke tests
curl -f https://staging-api.nexusplatform.com/health
```

## Production Deployment

### Blue-Green Deployment Strategy

```bash
# Production deployment script
#!/bin/bash
set -e

ENVIRONMENT="production"
BLUE_GREEN="${1:-blue}"  # blue or green

echo "🚀 Starting $BLUE_GREEN deployment to $ENVIRONMENT"

# Deploy to blue/green environment
kubectl apply -k "k8s/overlays/$ENVIRONMENT-$BLUE_GREEN/"

# Wait for rollout
kubectl rollout status "deployment/nexus-api-gateway-$BLUE_GREEN" -n "nexus-$ENVIRONMENT"

# Run health checks
echo "🏥 Running health checks..."
kubectl exec -n "nexus-$ENVIRONMENT" "deployment/nexus-api-gateway-$BLUE_GREEN" -- \
  curl -f http://localhost/health

# Switch traffic (using ingress or service mesh)
if [ "$BLUE_GREEN" = "blue" ]; then
  kubectl apply -f k8s/ingress/production-green-to-blue.yaml
else
  kubectl apply -f k8s/ingress/production-blue-to-green.yaml
fi

# Monitor for 5 minutes
echo "📊 Monitoring deployment for 5 minutes..."
sleep 300

# Check error rates and latency
ERROR_RATE=$(kubectl exec -n "nexus-$ENVIRONMENT" deployment/prometheus -- \
  promql 'rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])')

if (( $(echo "$ERROR_RATE > 0.05" | bc -l) )); then
  echo "❌ High error rate detected: $ERROR_RATE"
  echo "🔄 Rolling back deployment..."
  # Rollback logic here
  exit 1
fi

echo "✅ Deployment successful!"
```

### Production Infrastructure Setup

#### 1. VPC and Networking

```hcl
# Terraform configuration
resource "aws_vpc" "nexus_prod" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = {
    Name = "nexus-production"
    Environment = "production"
  }
}

resource "aws_subnet" "private" {
  count = 3
  vpc_id = aws_vpc.nexus_prod.id
  cidr_block = "10.0.${count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "nexus-prod-private-${count.index}"
    "kubernetes.io/role/internal-elb" = "1"
  }
}
```

#### 2. EKS Cluster

```hcl
module "eks" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name = "nexus-production"
  cluster_version = "1.27"

  vpc_id = aws_vpc.nexus_prod.id
  subnet_ids = aws_subnet.private[*].id

  eks_managed_node_groups = {
    general = {
      desired_size = 3
      min_size = 3
      max_size = 10

      instance_types = ["m5.large"]
      capacity_type = "ON_DEMAND"
    }

    compute = {
      desired_size = 2
      min_size = 1
      max_size = 20

      instance_types = ["c5.xlarge"]
      capacity_type = "SPOT"

      taints = [{
        key = "workload"
        value = "compute"
        effect = "NO_SCHEDULE"
      }]
    }
  }
}
```

#### 3. RDS PostgreSQL

```hcl
resource "aws_db_instance" "nexus_postgres" {
  identifier = "nexus-production"
  engine = "postgres"
  engine_version = "15.4"
  instance_class = "db.r6g.large"

  allocated_storage = 100
  max_allocated_storage = 1000
  storage_type = "gp3"

  multi_az = true
  backup_retention_period = 30
  backup_window = "03:00-04:00"
  maintenance_window = "sun:04:00-sun:05:00"

  db_subnet_group_name = aws_db_subnet_group.nexus.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  username = "nexus_admin"
  password = data.aws_secretsmanager_secret_version.db_password.secret_string

  performance_insights_enabled = true
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_enhanced_monitoring.arn

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = {
    Name = "nexus-production-postgres"
    Environment = "production"
  }
}
```

#### 4. ElastiCache Redis

```hcl
resource "aws_elasticache_cluster" "nexus_redis" {
  cluster_id = "nexus-prod"
  engine = "redis"
  node_type = "cache.r6g.large"
  num_cache_nodes = 1
  parameter_group_name = "default.redis7"
  port = 6379

  subnet_group_name = aws_elasticache_subnet_group.nexus.name
  security_group_ids = [aws_security_group.redis.id]

  maintenance_window = "sun:05:00-sun:06:00"
  snapshot_window = "04:00-05:00"
  snapshot_retention_limit = 7

  tags = {
    Name = "nexus-production-redis"
    Environment = "production"
  }
}
```

### Database Migration

```bash
# Production database migration
kubectl exec -n nexus-production deployment/nexus-migration -- \
  bash -c "
    echo 'Running database migrations...'
    alembic upgrade head
    echo 'Migrations completed successfully'
  "

# Verify migration
kubectl exec -n nexus-production deployment/nexus-migration -- \
  bash -c "
    python -c '
    from NEXUS_app.database.connection import get_db
    db = next(get_db())
    result = db.execute(\"SELECT version_num FROM alembic_version\")
    print(f\"Current schema version: {result.fetchone()[0]}\")
    '
  "
```

## Monitoring Setup

### Prometheus and Grafana

```bash
# Install Prometheus stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword='secure-password'

# Install custom NEXUS dashboards
kubectl apply -f k8s/monitoring/dashboards/
```

### ELK Stack Setup

```bash
# Install ELK stack
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --create-namespace \
  --set replicas=3

helm install logstash elastic/logstash \
  --namespace logging \
  --set config='input { tcp { port => 5044 } } output { elasticsearch { hosts => [\"elasticsearch-master:9200\"] } }'

helm install kibana elastic/kibana \
  --namespace logging
```

### Application Monitoring

```bash
# Deploy APM agents
kubectl apply -f k8s/monitoring/apm/

# Configure metric collection
kubectl apply -f k8s/monitoring/metrics/

# Set up alerting rules
kubectl apply -f k8s/monitoring/alerts/
```

## Backup and Recovery

### Database Backup

```bash
# Automated backup job
kubectl apply -f k8s/backup/database-backup.yaml

# Manual backup
kubectl exec -n nexus-production deployment/nexus-backup -- \
  bash -c "
    pg_dump -h nexus-postgres -U nexus_admin nexus_prod > backup_$(date +%Y%m%d_%H%M%S).sql
    aws s3 cp backup_*.sql s3://nexus-backups/database/
  "
```

### Application Backup

```bash
# Configuration backup
kubectl exec -n nexus-production deployment/nexus-backup -- \
  bash -c "
    # Backup configurations
    kubectl get configmap -n nexus-production -o yaml > config_backup.yaml
    kubectl get secret -n nexus-production -o yaml > secrets_backup.yaml

    # Upload to S3
    aws s3 cp config_backup.yaml s3://nexus-backups/config/
    aws s3 cp secrets_backup.yaml s3://nexus-backups/config/
  "
```

### Disaster Recovery

```bash
# DR failover script
#!/bin/bash

PRIMARY_REGION="us-east-1"
DR_REGION="us-west-2"

echo "🔄 Initiating disaster recovery failover..."

# Promote DR database
aws rds failover-db-cluster \
  --db-cluster-identifier nexus-dr \
  --target-db-instance-identifier nexus-dr-instance

# Switch DNS to DR region
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456789 \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.nexusplatform.com",
        "Type": "CNAME",
        "TTL": 60,
        "ResourceRecords": [{"Value": "dr-api.nexusplatform.com"}]
      }
    }]
  }'

# Update Kubernetes context
aws eks update-kubeconfig --name nexus-dr --region $DR_REGION

# Scale up DR environment
kubectl scale deployment nexus-api-gateway --replicas=10 -n nexus-dr

echo "✅ Disaster recovery completed"
```

## Troubleshooting

### Common Deployment Issues

#### Pod CrashLoopBackOff

```bash
# Check pod logs
kubectl logs -n nexus-production deployment/nexus-user-service --previous

# Check pod events
kubectl describe pod -n nexus-production -l app=nexus-user-service

# Check resource limits
kubectl get pods -n nexus-production -o jsonpath='{.spec.containers[*].resources}'
```

#### Service Unavailable

```bash
# Check service endpoints
kubectl get endpoints -n nexus-production

# Test service connectivity
kubectl exec -n nexus-production deployment/nexus-api-gateway -- \
  curl -f http://nexus-user-service:8000/health

# Check network policies
kubectl get networkpolicies -n nexus-production
```

#### Database Connection Issues

```bash
# Check database connectivity
kubectl exec -n nexus-production deployment/nexus-user-service -- \
  python -c "
  import psycopg2
  try:
      conn = psycopg2.connect(os.environ['DATABASE_URL'])
      print('✅ Database connection successful')
  except Exception as e:
      print(f'❌ Database connection failed: {e}')
  "

# Check database logs
kubectl logs -n nexus-production -l app=postgres
```

#### High Memory Usage

```bash
# Check memory usage
kubectl top pods -n nexus-production

# Check memory limits
kubectl get pods -n nexus-production -o jsonpath='{.spec.containers[*].resources.limits.memory}'

# Force pod restart
kubectl rollout restart deployment/nexus-user-service -n nexus-production
```

### Performance Issues

#### High Latency

```bash
# Check response times
kubectl exec -n nexus-production deployment/prometheus -- \
  promql 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))'

# Check database query performance
kubectl exec -n nexus-production deployment/nexus-user-service -- \
  python -c "
  import time
  start = time.time()
  # Run slow query
  end = time.time()
  print(f'Query took: {end - start} seconds')
  "
```

#### High Error Rates

```bash
# Check error rates by service
kubectl exec -n nexus-production deployment/prometheus -- \
  promql 'rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m])'

# Check application logs
kubectl logs -n nexus-production -l app=nexus-user-service --tail=100
```

### Monitoring Commands

```bash
# Check cluster status
kubectl get nodes
kubectl cluster-info

# Monitor pod health
kubectl get pods -n nexus-production --field-selector=status.phase!=Running

# Check resource usage
kubectl top nodes
kubectl top pods -n nexus-production

# View logs
stern -n nexus-production nexus- --tail=50

# Debug pod
kubectl debug -n nexus-production pod/nexus-user-service-12345 -it --image=busybox
```

### Emergency Procedures

#### Emergency Rollback

```bash
# Immediate rollback to previous version
kubectl rollout undo deployment/nexus-api-gateway -n nexus-production

# Rollback database migration
kubectl exec -n nexus-production deployment/nexus-migration -- \
  alembic downgrade -1

# Notify team
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"🚨 Emergency rollback initiated"}' \
  $SLACK_WEBHOOK_URL
```

#### Emergency Scaling

```bash
# Scale up services during high load
kubectl scale deployment nexus-api-gateway --replicas=20 -n nexus-production
kubectl scale deployment nexus-user-service --replicas=15 -n nexus-production

# Enable horizontal pod autoscaling
kubectl apply -f k8s/hpa/emergency-hpa.yaml
```

---

## Support Contacts

- **Production Issues**: #prod-incidents (Slack)
- **DevOps On-Call**: devops-oncall@nexusplatform.com
- **Security Incidents**: security@nexusplatform.com
- **Customer Support**: support@nexusplatform.com

## Change Log

- **v1.0.0**: Initial deployment guide
- **v1.1.0**: Added blue-green deployment strategy
- **v1.2.0**: Enhanced monitoring and alerting setup
- **v1.3.0**: Added disaster recovery procedures
