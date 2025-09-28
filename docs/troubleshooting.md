# NEXUS SSOT Troubleshooting Guide

This guide provides solutions for common issues encountered with the NEXUS Single Source of Truth (SSOT) system.

## Table of Contents

1. [API Registry Issues](#api-registry-issues)
2. [Alias Resolution Problems](#alias-resolution-problems)
3. [Database Connectivity Issues](#database-connectivity-issues)
4. [Deployment Failures](#deployment-failures)
5. [Performance Issues](#performance-issues)
6. [Security and Access Issues](#security-and-access-issues)
7. [Monitoring and Alerting](#monitoring-and-alerting)

## API Registry Issues

### Issue: API Registry Service Not Starting

**Symptoms:**

- SSOT registry service fails to start
- Error messages in logs about missing dependencies

**Solutions:**

1. Check if all dependencies are installed:

   ```bash
   pip install -r requirements.txt
   ```

2. Verify database connectivity:

   ```bash
   python -c "from backend.database import engine; engine.connect(); print('Database connected')"
   ```

3. Check configuration files:
   ```bash
   python scripts/validate_ssot.py config/alias_governance.yaml
   ```

### Issue: Alias Not Found Errors

**Symptoms:**

- 404 errors when resolving aliases
- "Alias does not exist" messages

**Solutions:**

1. Verify the alias exists in the registry:

   ```bash
   curl http://localhost:8000/api/aliases/user-profile
   ```

2. Check the context parameter:
   - Ensure context matches (frontend, backend, system)
   - Try different contexts if applicable

3. Review audit logs for recent changes:
   ```bash
   curl http://localhost:8000/api/audit?alias=user-profile
   ```

## Alias Resolution Problems

### Issue: Incorrect Endpoint Resolution

**Symptoms:**

- Aliases resolve to wrong endpoints
- Context-specific resolution not working

**Solutions:**

1. Check alias configuration:

   ```json
   {
     "alias": "user-profile",
     "canonical": "https://api.nexus.com/v1/users/profile",
     "context": "frontend"
   }
   ```

2. Verify context-aware resolution:

   ```python
   from ssot_registry import resolve_alias
   endpoint = resolve_alias("user-profile", context="frontend")
   ```

3. Update alias if canonical endpoint changed:
   ```bash
   curl -X PUT http://localhost:8000/api/aliases/user-profile \
     -H "Content-Type: application/json" \
     -d '{"canonical": "https://new-api.nexus.com/v1/users/profile"}'
   ```

### Issue: Temporary Alias Expired

**Symptoms:**

- Alias resolves but returns expired error
- Temporary aliases not working

**Solutions:**

1. Check expiration date:

   ```bash
   curl http://localhost:8000/api/aliases/temp-login
   ```

2. Extend expiration or create new alias:
   ```bash
   curl -X PUT http://localhost:8000/api/aliases/temp-login \
     -H "Content-Type: application/json" \
     -d '{"expires_at": "2025-01-28T12:00:00Z"}'
   ```

## Database Connectivity Issues

### Issue: Cannot Connect to Database

**Symptoms:**

- Database connection errors
- Migration failures

**Solutions:**

1. Check database credentials:

   ```bash
   python -c "import os; print(os.getenv('DATABASE_URL'))"
   ```

2. Verify database server status:

   ```bash
   docker ps | grep postgres
   ```

3. Test connection manually:
   ```bash
   psql $DATABASE_URL -c "SELECT 1;"
   ```

### Issue: Schema Migration Failures

**Symptoms:**

- Alembic migration errors
- Schema inconsistencies

**Solutions:**

1. Check current migration status:

   ```bash
   alembic current
   ```

2. Review migration history:

   ```bash
   alembic history
   ```

3. Rollback if necessary:
   ```bash
   alembic downgrade -1
   ```

## Deployment Failures

### Issue: Kubernetes Deployment Fails

**Symptoms:**

- Pods in CrashLoopBackOff
- Deployment not progressing

**Solutions:**

1. Check pod logs:

   ```bash
   kubectl logs <pod-name>
   ```

2. Verify resource limits:

   ```bash
   kubectl describe pod <pod-name>
   ```

3. Check image availability:
   ```bash
   docker pull <image-name>
   ```

### Issue: Docker Build Failures

**Symptoms:**

- Docker build errors
- Missing dependencies

**Solutions:**

1. Check Dockerfile syntax:

   ```bash
   docker build --no-cache -t nexus-app .
   ```

2. Verify base image:

   ```bash
   docker pull python:3.9-slim
   ```

3. Review build logs for specific errors

## Performance Issues

### Issue: Slow Alias Resolution

**Symptoms:**

- High response times for alias lookups
- Database query timeouts

**Solutions:**

1. Check database performance:

   ```sql
   EXPLAIN ANALYZE SELECT * FROM aliases WHERE alias = 'user-profile';
   ```

2. Implement caching:

   ```python
   from ssot_registry import get_cache
   cache = get_cache()
   cache.set('alias:user-profile', endpoint, ttl=300)
   ```

3. Optimize queries:
   - Add database indexes
   - Use connection pooling

### Issue: High Memory Usage

**Symptoms:**

- OutOfMemory errors
- System slowdown

**Solutions:**

1. Monitor memory usage:

   ```bash
   docker stats
   ```

2. Check for memory leaks:

   ```python
   import psutil  # pip install psutil if not available
   print(psutil.virtual_memory())
   ```

3. Optimize application code:
   - Reduce object creation
   - Implement proper cleanup

## Security and Access Issues

### Issue: Authentication Failures

**Symptoms:**

- 401 Unauthorized errors
- Access denied messages

**Solutions:**

1. Check API keys:

   ```bash
   curl -H "Authorization: Bearer <token>" http://localhost:8000/api/aliases
   ```

2. Verify user permissions:

   ```bash
   curl http://localhost:8000/api/user/permissions
   ```

3. Review security policies:
   ```yaml
   # Check security/ssot_policies.yaml
   policies:
     - name: "alias_access"
       roles: ["admin", "developer"]
   ```

### Issue: Audit Log Access Issues

**Symptoms:**

- Cannot access audit logs
- Permission denied for audit queries

**Solutions:**

1. Check user role:

   ```bash
   curl http://localhost:8000/api/user/role
   ```

2. Verify audit permissions:

   ```bash
   curl -H "Authorization: Bearer <admin-token>" http://localhost:8000/api/audit
   ```

3. Review RBAC configuration:
   ```yaml
   rbac:
     roles:
       admin:
         permissions: ["read_audit", "write_audit"]
   ```

## Monitoring and Alerting

### Issue: Alerts Not Triggering

**Symptoms:**

- No alerts for known issues
- Monitoring dashboards not updating

**Solutions:**

1. Check alert configuration:

   ```yaml
   # monitoring/ssot_metrics.yaml
   alerts:
     - name: "alias_resolution_time"
       threshold: 1000 # ms
       condition: ">"
   ```

2. Verify monitoring service:

   ```bash
   curl http://localhost:8000/health
   ```

3. Test alert manually:
   ```bash
   curl -X POST http://localhost:8000/api/alerts/test
   ```

### Issue: False Positives in Alerts

**Symptoms:**

- Too many false alerts
- Alert fatigue

**Solutions:**

1. Adjust alert thresholds:

   ```yaml
   alerts:
     - name: "error_rate"
       threshold: 0.05 # 5%
       condition: ">"
   ```

2. Add alert suppression:

   ```yaml
   suppress:
     - alert: "database_connection"
       duration: "5m"
   ```

3. Review alert history:
   ```bash
   curl http://localhost:8000/api/alerts/history
   ```

## Getting Help

If you cannot resolve an issue:

1. Check the audit logs for recent changes
2. Review the monitoring dashboards
3. Contact the platform team via Slack (#ssot-support)
4. Create a support ticket with detailed error logs

## Prevention

To prevent common issues:

- Regularly update configurations
- Monitor system performance
- Test changes in staging environment
- Keep documentation current
- Train team members on troubleshooting procedures
