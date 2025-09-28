# NEXUS Platform Deployment Guide

This guide provides comprehensive instructions for deploying the NEXUS Platform in various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Development Deployment](#development-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Production Deployment](#production-deployment)
6. [Monitoring Setup](#monitoring-setup)
7. [Security Hardening](#security-hardening)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 50GB SSD minimum
- **CPU**: 4 cores minimum, 8 cores recommended

### Software Dependencies

- **Python 3.8+** - Backend runtime
- **Node.js 18+** - Frontend build tools
- **Docker 20.10+** - Containerization
- **Docker Compose 2.0+** - Multi-container orchestration
- **Kubernetes 1.24+** - Production orchestration (optional)
- **PostgreSQL 13+** - Primary database
- **Redis 6+** - Caching and sessions

### Network Requirements

- **Ports**: 8000 (API), 3000 (Frontend), 3001 (Monitoring), 5432 (PostgreSQL), 6379 (Redis)
- **Domain**: Configured DNS for production deployments
- **SSL/TLS**: Valid certificates for HTTPS

## Development Deployment

### Quick Start with Docker Compose

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-org/nexus-platform.git
   cd nexus-platform
   ```

2. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with development settings
   ```

3. **Start all services**

   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**

   ```bash
   # Check service status
   docker-compose ps

   # View logs
   docker-compose logs -f backend

   # Access applications
   curl http://localhost:8000/health
   curl http://localhost:3000/health
   ```

### Manual Development Setup

1. **Backend Setup**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main_unified.py
   ```

2. **Frontend Setup**

   ```bash
   cd frontend/web
   npm install
   npm start
   ```

3. **Database Setup**

   ```bash
   # Using Docker
   docker run -d --name nexus-db -p 5432:5432 \
     -e POSTGRES_DB=nexus -e POSTGRES_USER=nexus \
     -e POSTGRES_PASSWORD=secure_password postgres:13

   # Run migrations
   python setup_production_database.py
   ```

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Production Docker Compose**

   ```bash
   # Use production configuration
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Environment Configuration**

   ```bash
   # Create production environment file
   cp .env.production .env
   # Edit with production values
   ```

3. **SSL/TLS Setup**

   ```bash
   # Generate SSL certificates
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout ssl/nexus.key -out ssl/nexus.crt

   # Update nginx configuration
   cp nginx/ssl.conf nginx.conf
   ```

4. **Health Checks**
   ```bash
   # Verify all services are healthy
   curl https://your-domain.com/health
   curl https://your-domain.com/api/health
   ```

### Multi-Stage Docker Build

1. **Build optimized images**

   ```bash
   # Backend
   docker build -f Dockerfile.backend -t nexus-backend:prod .

   # Frontend
   docker build -f Dockerfile.frontend -t nexus-frontend:prod .

   # Monitoring
   docker build -f Dockerfile.monitoring -t nexus-monitoring:prod .
   ```

2. **Deploy with orchestration**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3.0+ (optional)

### Basic Deployment

1. **Apply base manifests**

   ```bash
   kubectl apply -f k8s/base/
   kubectl apply -f k8s/backend/
   kubectl apply -f k8s/frontend/
   kubectl apply -f k8s/monitoring/
   ```

2. **Verify deployment**
   ```bash
   kubectl get pods -n nexus
   kubectl get services -n nexus
   kubectl get ingress -n nexus
   ```

### Production Kubernetes Setup

1. **Namespace and RBAC**

   ```bash
   kubectl create namespace nexus-production
   kubectl apply -f k8s/rbac/
   ```

2. **Persistent Storage**

   ```bash
   kubectl apply -f k8s/storage/
   kubectl get pvc -n nexus-production
   ```

3. **Deploy with Helm** (if using Helm)
   ```bash
   helm install nexus ./helm/nexus \
     --namespace nexus-production \
     --set environment=production
   ```

### Scaling and High Availability

1. **Horizontal Pod Autoscaling**

   ```bash
   kubectl autoscale deployment nexus-backend \
     --cpu-percent=70 --min=3 --max=10 -n nexus-production
   ```

2. **Load Balancing**
   ```bash
   kubectl apply -f k8s/loadbalancer/
   kubectl get services -n nexus-production
   ```

## Production Deployment

### Security Hardening

1. **Apply security policies**

   ```bash
   kubectl apply -f security/hardening.yaml
   ```

2. **Configure secrets management**

   ```bash
   kubectl apply -f k8s/secrets/
   ```

3. **Enable network policies**
   ```bash
   kubectl apply -f k8s/network-policies/
   ```

### Performance Optimization

1. **Database optimization**

   ```bash
   # Run optimization scripts
   python scripts/database_optimization.py
   ```

2. **Caching configuration**

   ```bash
   # Configure Redis clustering
   kubectl apply -f k8s/redis-cluster/
   ```

3. **CDN Setup**
   ```bash
   # Configure CDN for static assets
   # Update nginx configuration for CDN integration
   ```

### Backup and Recovery

1. **Automated backups**

   ```bash
   kubectl apply -f k8s/backup/
   kubectl create cronjob backup-job --schedule="0 2 * * *" \
     --image=backup-image ./backup-script.sh
   ```

2. **Recovery procedures**

   ```bash
   # Restore from backup
   kubectl exec -it nexus-db-pod -- psql -U nexus -d nexus < backup.sql

   # Verify data integrity
   python scripts/validate_data_integrity.py
   ```

## Monitoring Setup

### Grafana Dashboards

1. **Access Grafana**

   ```bash
   # Default credentials: admin/admin
   open http://localhost:3001
   ```

2. **Import dashboards**

   ```bash
   # Import system monitoring dashboard
   curl -X POST http://localhost:3001/api/dashboards/import \
     -H "Content-Type: application/json" \
     -d @monitoring/grafana/dashboards/system-dashboard.json
   ```

3. **Configure alerts**
   ```bash
   # Import alert rules
   kubectl apply -f monitoring/prometheus/rules/
   ```

### Prometheus Metrics

1. **Access Prometheus**

   ```bash
   open http://localhost:9090
   ```

2. **Query metrics**

   ```bash
   # System metrics
   up{job="nexus-backend"}

   # Application metrics
   http_requests_total{status="200"}

   # Database metrics
   pg_stat_database_tup_returned
   ```

### ELK Stack Setup

1. **Deploy ELK stack**

   ```bash
   kubectl apply -f monitoring/elk/
   ```

2. **Configure log shipping**

   ```bash
   # Filebeat configuration
   kubectl apply -f monitoring/filebeat/
   ```

3. **Access Kibana**
   ```bash
   open http://localhost:5601
   ```

## Security Hardening

### Network Security

1. **Network policies**

   ```bash
   kubectl apply -f security/network-policies.yaml
   ```

2. **Firewall rules**
   ```bash
   # Configure cloud firewall
   # Allow only necessary ports: 80, 443, 22 (if needed)
   ```

### Access Control

1. **RBAC Configuration**

   ```bash
   kubectl apply -f security/rbac.yaml
   ```

2. **Pod Security Standards**
   ```bash
   kubectl apply -f security/pod-security-policies.yaml
   ```

### Security Scanning

1. **Run security scans**

   ```bash
   python security/security-scanner.py --target containers
   python security/security-scanner.py --target filesystem
   ```

2. **Vulnerability assessment**

   ```bash
   # Trivy container scanning
   trivy image nexus-backend:latest

   # ClamAV malware scanning
   clamscan -r /opt/nexus
   ```

## Troubleshooting

### Common Issues

1. **Service not starting**

   ```bash
   # Check logs
   docker-compose logs backend
   kubectl logs -f deployment/nexus-backend

   # Check resource usage
   kubectl top pods -n nexus
   ```

2. **Database connection issues**

   ```bash
   # Test database connectivity
   psql -h localhost -U nexus -d nexus

   # Check database logs
   kubectl logs -f deployment/nexus-db
   ```

3. **Performance issues**

   ```bash
   # Check resource allocation
   kubectl describe nodes

   # Monitor metrics
   curl http://localhost:9090/metrics
   ```

### Debug Commands

1. **Application debugging**

   ```bash
   # Enable debug logging
   export LOG_LEVEL=DEBUG

   # Check application health
   curl http://localhost:8000/health
   curl http://localhost:8000/api/health
   ```

2. **Network debugging**

   ```bash
   # Check service endpoints
   kubectl get endpoints -n nexus

   # Test service connectivity
   kubectl exec -it nexus-backend-pod -- curl http://nexus-db:5432
   ```

3. **Storage debugging**

   ```bash
   # Check persistent volumes
   kubectl get pv,pvc -n nexus

   # Check disk usage
   kubectl exec -it nexus-backend-pod -- df -h
   ```

### Recovery Procedures

1. **Service restart**

   ```bash
   kubectl rollout restart deployment/nexus-backend
   docker-compose restart backend
   ```

2. **Data recovery**

   ```bash
   # Restore from backup
   kubectl exec -it nexus-db-pod -- psql -U nexus -d nexus < /backup/backup.sql

   # Verify data integrity
   python scripts/validate_data_integrity.py
   ```

3. **Configuration rollback**

   ```bash
   # Rollback deployment
   kubectl rollout undo deployment/nexus-backend

   # Restore configuration
   git checkout HEAD -- config/
   ```

## Support

For additional support:

- **Documentation**: [NEXUS Docs](https://docs.nexus-platform.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/nexus-platform/issues)
- **Monitoring**: [Grafana Dashboard](http://your-domain.com:3001)

## Best Practices

1. **Always use production configurations in production**
2. **Regularly update dependencies and security patches**
3. **Monitor resource usage and scale accordingly**
4. **Implement proper backup and recovery procedures**
5. **Use secrets management for sensitive data**
6. **Regularly test disaster recovery procedures**
7. **Keep monitoring and alerting systems up to date**

---

**NEXUS Platform** - Comprehensive deployment guide for reliable and scalable operations.
