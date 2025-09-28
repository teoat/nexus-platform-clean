# NEXUS Platform - Runbooks

## Overview

This document contains operational runbooks for the NEXUS Platform, providing step-by-step procedures for common operational tasks, incident response, and maintenance activities.

## Table of Contents

1. [Incident Response](#incident-response)
2. [Deployment Procedures](#deployment-procedures)
3. [Maintenance Tasks](#maintenance-tasks)
4. [Troubleshooting Procedures](#troubleshooting-procedures)
5. [Emergency Procedures](#emergency-procedures)

## Incident Response

### P1 - Critical Service Down

**Severity**: Critical
**Response Time**: 15 minutes
**Resolution Time**: 1 hour

#### Symptoms

- Service returns 5xx errors
- Health checks failing
- High error rate in monitoring

#### Immediate Actions

1. **Acknowledge Alert**

   ```bash
   # Check service status
   kubectl get pods -n nexus-platform
   kubectl get services -n nexus-platform
   ```

2. **Check Logs**

   ```bash
   # Get recent logs
   kubectl logs -f deployment/nexus-backend -n nexus-platform --tail=100
   kubectl logs -f deployment/nexus-frontend -n nexus-platform --tail=100
   ```

3. **Check Resource Usage**

   ```bash
   # Check resource usage
   kubectl top pods -n nexus-platform
   kubectl top nodes
   ```

4. **Check Database Connectivity**
   ```bash
   # Test database connection
   kubectl exec -it deployment/nexus-backend -n nexus-platform -- psql "$DATABASE_URL" -c "SELECT 1;"
   ```

#### Resolution Steps

1. **Restart Services**

   ```bash
   # Restart backend
   kubectl rollout restart deployment/nexus-backend -n nexus-platform

   # Restart frontend
   kubectl rollout restart deployment/nexus-frontend -n nexus-platform
   ```

2. **Scale Up Services**

   ```bash
   # Scale up backend
   kubectl scale deployment nexus-backend --replicas=5 -n nexus-platform

   # Scale up frontend
   kubectl scale deployment nexus-frontend --replicas=5 -n nexus-platform
   ```

3. **Check Load Balancer**

   ```bash
   # Check ingress status
   kubectl get ingress -n nexus-platform

   # Check Istio configuration
   istioctl analyze
   ```

#### Post-Incident Actions

1. **Document Incident**
   - Record timeline
   - Identify root cause
   - Document resolution steps

2. **Update Monitoring**
   - Review alert thresholds
   - Update runbooks if needed

3. **Follow-up**
   - Schedule post-mortem
   - Implement preventive measures

### P2 - High Error Rate

**Severity**: High
**Response Time**: 30 minutes
**Resolution Time**: 2 hours

#### Symptoms

- Error rate > 5%
- Increased response time
- User complaints

#### Investigation Steps

1. **Check Error Patterns**

   ```bash
   # Check error logs
   kubectl logs -f deployment/nexus-backend -n nexus-platform | grep ERROR

   # Check metrics
   curl -s http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~"5.."}[5m])
   ```

2. **Check Database Performance**

   ```bash
   # Check database connections
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -c "SELECT count(*) FROM pg_stat_activity;"

   # Check slow queries
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
   ```

3. **Check Redis Performance**

   ```bash
   # Check Redis status
   kubectl exec -it deployment/nexus-redis -n nexus-platform -- redis-cli info

   # Check Redis memory usage
   kubectl exec -it deployment/nexus-redis -n nexus-platform -- redis-cli info memory
   ```

#### Resolution Steps

1. **Optimize Database**

   ```bash
   # Analyze slow queries
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -c "ANALYZE;"

   # Check index usage
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -c "SELECT schemaname, tablename, attname, n_distinct, correlation FROM pg_stats WHERE schemaname = 'public';"
   ```

2. **Optimize Redis**

   ```bash
   # Clear Redis cache if needed
   kubectl exec -it deployment/nexus-redis -n nexus-platform -- redis-cli FLUSHDB

   # Check Redis configuration
   kubectl exec -it deployment/nexus-redis -n nexus-platform -- redis-cli CONFIG GET "*"
   ```

3. **Scale Services**

   ```bash
   # Scale up backend
   kubectl scale deployment nexus-backend --replicas=8 -n nexus-platform

   # Scale up frontend
   kubectl scale deployment nexus-frontend --replicas=8 -n nexus-platform
   ```

### P3 - Performance Degradation

**Severity**: Medium
**Response Time**: 1 hour
**Resolution Time**: 4 hours

#### Symptoms

- Response time > 2 seconds
- High CPU usage
- High memory usage

#### Investigation Steps

1. **Check Resource Usage**

   ```bash
   # Check CPU usage
   kubectl top pods -n nexus-platform

   # Check memory usage
   kubectl top pods -n nexus-platform --sort-by=memory
   ```

2. **Check Application Metrics**

   ```bash
   # Check response time
   curl -s http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

   # Check request rate
   curl -s http://prometheus:9090/api/v1/query?query=sum(rate(http_requests_total[5m]))
   ```

3. **Check Database Performance**

   ```bash
   # Check database connections
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -c "SELECT count(*) FROM pg_stat_activity;"

   # Check database size
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -c "SELECT pg_size_pretty(pg_database_size('nexus_platform'));"
   ```

#### Resolution Steps

1. **Optimize Resources**

   ```bash
   # Update resource limits
   kubectl patch deployment nexus-backend -n nexus-platform -p '{"spec":{"template":{"spec":{"containers":[{"name":"nexus-backend","resources":{"limits":{"cpu":"4","memory":"8Gi"}}}]}}}}'
   ```

2. **Scale Services**

   ```bash
   # Scale up backend
   kubectl scale deployment nexus-backend --replicas=6 -n nexus-platform

   # Scale up frontend
   kubectl scale deployment nexus-frontend --replicas=6 -n nexus-platform
   ```

3. **Optimize Database**

   ```bash
   # Vacuum database
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -c "VACUUM ANALYZE;"

   # Check for long-running queries
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
   ```

## Deployment Procedures

### Blue-Green Deployment

#### Pre-Deployment Checklist

- [ ] Backup current state
- [ ] Verify all tests pass
- [ ] Check resource availability
- [ ] Notify stakeholders

#### Deployment Steps

1. **Deploy to Blue Environment**

   ```bash
   # Create blue namespace
   kubectl create namespace nexus-platform-blue

   # Deploy blue environment
   kubectl apply -f k8s/manifests/ -n nexus-platform-blue

   # Update image tags
   kubectl set image deployment/nexus-backend nexus-backend=nexus-platform/backend:blue-v1.0.0 -n nexus-platform-blue
   ```

2. **Test Blue Environment**

   ```bash
   # Get blue service IP
   BLUE_IP=$(kubectl get service nexus-nginx -n nexus-platform-blue -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

   # Run health checks
   curl -f http://$BLUE_IP/health
   curl -f http://$BLUE_IP/api/health
   ```

3. **Switch Traffic**

   ```bash
   # Update Istio VirtualService
   kubectl patch virtualservice nexus-platform -n nexus-platform -p '{"spec":{"http":[{"route":[{"destination":{"host":"nexus-backend","subset":"blue"}}]}]}}'
   ```

4. **Cleanup Green Environment**
   ```bash
   # Scale down green environment
   kubectl scale deployment nexus-backend --replicas=0 -n nexus-platform
   kubectl scale deployment nexus-frontend --replicas=0 -n nexus-platform
   ```

#### Rollback Procedure

1. **Switch Traffic Back**

   ```bash
   # Switch traffic back to green
   kubectl patch virtualservice nexus-platform -n nexus-platform -p '{"spec":{"http":[{"route":[{"destination":{"host":"nexus-backend","subset":"green"}}]}]}}'
   ```

2. **Scale Up Green Environment**

   ```bash
   # Scale up green environment
   kubectl scale deployment nexus-backend --replicas=3 -n nexus-platform
   kubectl scale deployment nexus-frontend --replicas=3 -n nexus-platform
   ```

3. **Verify Rollback**

   ```bash
   # Check service status
   kubectl get pods -n nexus-platform

   # Run health checks
   curl -f http://$GREEN_IP/health
   ```

### Canary Deployment

#### Pre-Deployment Checklist

- [ ] Configure canary traffic percentage
- [ ] Set up monitoring for canary
- [ ] Prepare rollback plan

#### Deployment Steps

1. **Deploy Canary Version**

   ```bash
   # Deploy canary version
   kubectl apply -f k8s/canary/

   # Update image tags
   kubectl set image deployment/nexus-backend nexus-backend=nexus-platform/backend:canary-v1.0.0 -n nexus-platform
   ```

2. **Configure Traffic Splitting**

   ```bash
   # Set 10% traffic to canary
   kubectl patch virtualservice nexus-platform -n nexus-platform -p '{"spec":{"http":[{"route":[{"destination":{"host":"nexus-backend","subset":"canary","weight":10}},{"destination":{"host":"nexus-backend","subset":"stable","weight":90}}]}]}}'
   ```

3. **Monitor Canary**

   ```bash
   # Check canary metrics
   curl -s http://prometheus:9090/api/v1/query?query=rate(http_requests_total{subset="canary"}[5m])

   # Check error rate
   curl -s http://prometheus:9090/api/v1/query?query=rate(http_requests_total{subset="canary",status=~"5.."}[5m])
   ```

4. **Gradually Increase Traffic**

   ```bash
   # Increase to 25%
   kubectl patch virtualservice nexus-platform -n nexus-platform -p '{"spec":{"http":[{"route":[{"destination":{"host":"nexus-backend","subset":"canary","weight":25}},{"destination":{"host":"nexus-backend","subset":"stable","weight":75}}]}]}}'

   # Increase to 50%
   kubectl patch virtualservice nexus-platform -n nexus-platform -p '{"spec":{"http":[{"route":[{"destination":{"host":"nexus-backend","subset":"canary","weight":50}},{"destination":{"host":"nexus-backend","subset":"stable","weight":50}}]}]}}'

   # Increase to 100%
   kubectl patch virtualservice nexus-platform -n nexus-platform -p '{"spec":{"http":[{"route":[{"destination":{"host":"nexus-backend","subset":"canary","weight":100}}]}]}}'
   ```

## Maintenance Tasks

### Daily Tasks

1. **Check System Health**

   ```bash
   # Check pod status
   kubectl get pods -n nexus-platform

   # Check resource usage
   kubectl top pods -n nexus-platform

   # Check service status
   kubectl get services -n nexus-platform
   ```

2. **Check Logs**

   ```bash
   # Check error logs
   kubectl logs -f deployment/nexus-backend -n nexus-platform | grep ERROR

   # Check access logs
   kubectl logs -f deployment/nexus-nginx -n nexus-platform
   ```

3. **Check Monitoring**

   ```bash
   # Check Prometheus status
   kubectl get pods -n nexus-platform -l app=prometheus

   # Check Grafana status
   kubectl get pods -n nexus-platform -l app=grafana
   ```

### Weekly Tasks

1. **Database Maintenance**

   ```bash
   # Vacuum database
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -c "VACUUM ANALYZE;"

   # Check database size
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -c "SELECT pg_size_pretty(pg_database_size('nexus_platform'));"
   ```

2. **Backup Verification**

   ```bash
   # Check backup status
   kubectl logs -f deployment/nexus-backup -n nexus-platform

   # Verify backup integrity
   aws s3 ls s3://$S3_BUCKET/backups/
   ```

3. **Security Updates**

   ```bash
   # Check for security updates
   kubectl get pods -n nexus-platform -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}'

   # Update base images
   docker pull nexus-platform/backend:latest
   docker pull nexus-platform/frontend:latest
   ```

### Monthly Tasks

1. **Capacity Planning**

   ```bash
   # Check resource usage trends
   kubectl top nodes
   kubectl top pods -n nexus-platform

   # Check storage usage
   kubectl get pv
   kubectl get pvc -n nexus-platform
   ```

2. **Security Audit**

   ```bash
   # Run security scan
   trivy image nexus-platform/backend:latest
   trivy image nexus-platform/frontend:latest

   # Check RBAC
   kubectl get roles -n nexus-platform
   kubectl get rolebindings -n nexus-platform
   ```

3. **Performance Review**

   ```bash
   # Check performance metrics
   curl -s http://prometheus:9090/api/v1/query?query=histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[30d]))

   # Check error rates
   curl -s http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status=~"5.."}[30d])
   ```

## Emergency Procedures

### Complete Service Outage

1. **Immediate Response**

   ```bash
   # Check cluster status
   kubectl get nodes
   kubectl cluster-info

   # Check all pods
   kubectl get pods --all-namespaces
   ```

2. **Restart Services**

   ```bash
   # Restart all deployments
   kubectl rollout restart deployment/nexus-backend -n nexus-platform
   kubectl rollout restart deployment/nexus-frontend -n nexus-platform
   kubectl rollout restart deployment/nexus-nginx -n nexus-platform
   ```

3. **Check Dependencies**

   ```bash
   # Check database
   kubectl get pods -n nexus-platform -l app=postgres

   # Check Redis
   kubectl get pods -n nexus-platform -l app=redis
   ```

### Database Corruption

1. **Stop Services**

   ```bash
   # Scale down backend
   kubectl scale deployment nexus-backend --replicas=0 -n nexus-platform
   ```

2. **Restore Database**

   ```bash
   # Get latest backup
   LATEST_BACKUP=$(aws s3 ls s3://$S3_BUCKET/database/ | sort | tail -1 | awk '{print $4}')

   # Download backup
   aws s3 cp s3://$S3_BUCKET/database/$LATEST_BACKUP /tmp/backup.sql

   # Restore database
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -c "DROP DATABASE nexus_platform;"
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -c "CREATE DATABASE nexus_platform;"
   kubectl exec -it deployment/nexus-postgres -n nexus-platform -- psql -d nexus_platform -f /tmp/backup.sql
   ```

3. **Restart Services**
   ```bash
   # Scale up backend
   kubectl scale deployment nexus-backend --replicas=3 -n nexus-platform
   ```

### Security Breach

1. **Immediate Response**

   ```bash
   # Isolate affected pods
   kubectl delete pod <affected-pod> -n nexus-platform

   # Check for suspicious activity
   kubectl logs -f deployment/nexus-backend -n nexus-platform | grep -i "suspicious\|attack\|breach"
   ```

2. **Rotate Secrets**

   ```bash
   # Generate new secrets
   kubectl create secret generic nexus-secrets --from-literal=JWT_SECRET_KEY=$(openssl rand -base64 32) -n nexus-platform --dry-run=client -o yaml | kubectl apply -f -

   # Restart services
   kubectl rollout restart deployment/nexus-backend -n nexus-platform
   ```

3. **Update Security Policies**

   ```bash
   # Update network policies
   kubectl apply -f k8s/network-policies/

   # Update RBAC
   kubectl apply -f k8s/rbac/
   ```

## Contact Information

- **On-Call Engineer**: +1-555-0123
- **Escalation Manager**: +1-555-0124
- **Security Team**: security@nexusplatform.com
- **Slack**: #nexus-platform-alerts
