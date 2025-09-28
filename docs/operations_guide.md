# NEXUS Platform Operations Guide

## Overview

This operations guide provides procedures for maintaining, monitoring, and troubleshooting the NEXUS Platform in production environments.

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Monitoring and Alerting](#monitoring-and-alerting)
3. [Incident Response](#incident-response)
4. [Maintenance Procedures](#maintenance-procedures)
5. [Backup and Recovery](#backup-and-recovery)
6. [Performance Optimization](#performance-optimization)
7. [Security Operations](#security-operations)
8. [Compliance and Auditing](#compliance-and-auditing)

## Daily Operations

### Morning Checklist

#### System Health Verification

```bash
# Check application health
curl -f https://api.nexusplatform.com/health

# Check database connectivity
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1"

# Check Redis connectivity
redis-cli -h $REDIS_HOST ping

# Check Elasticsearch health
curl -f https://$ES_HOST:9200/_cluster/health

# Check queue health
curl -f https://api.nexusplatform.com/health/queue
```

#### Resource Monitoring

```bash
# Check system resources
top -b -n1 | head -20

# Check disk usage
df -h | grep -E "(Filesystem|/)"

# Check memory usage
free -h

# Check network connectivity
ping -c 3 google.com
```

#### Application Metrics Review

- Response times (should be <500ms for 95% of requests)
- Error rates (should be <1%)
- Throughput (monitor for unusual spikes/drops)
- Database connection pools
- Cache hit rates

### Log Review

```bash
# Check application logs for errors
tail -f /var/log/nexus/application.log | grep -i error

# Check security logs
tail -f /var/log/nexus/security.log

# Check audit logs
tail -f /var/log/nexus/audit.log

# Check system logs
journalctl -u nexus-backend -n 50 --no-pager
```

### Alert Review

- Review overnight alerts in monitoring dashboard
- Check for false positives
- Escalate critical alerts to on-call engineer
- Document any recurring issues

## Monitoring and Alerting

### Key Metrics to Monitor

#### Application Metrics

- **Response Time**: P95 response time by endpoint
- **Error Rate**: 5xx errors as percentage of total requests
- **Throughput**: Requests per second
- **Active Users**: Concurrent authenticated users
- **Transaction Volume**: Financial transactions per minute

#### Infrastructure Metrics

- **CPU Usage**: Per instance and cluster average
- **Memory Usage**: RAM utilization with swap monitoring
- **Disk I/O**: Read/write operations per second
- **Network I/O**: Bandwidth utilization
- **Database Connections**: Active connection count

#### Business Metrics

- **Transaction Success Rate**: Successful vs failed transactions
- **User Registration Rate**: New user signups per hour
- **Payment Processing**: Payment success/failure rates
- **Fraud Detection**: Suspicious activity alerts

### Alert Configuration

#### Critical Alerts (Page immediately)

```yaml
# Application down
- alert: ApplicationDown
  expr: up{job="nexus-backend"} == 0
  for: 5m
  labels:
    severity: critical

# High error rate
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
  for: 5m
  labels:
    severity: critical

# Database connection issues
- alert: DatabaseConnectionsHigh
  expr: pg_stat_activity_count > 80
  for: 5m
  labels:
    severity: critical
```

#### Warning Alerts (Review within 30 minutes)

```yaml
# Response time degradation
- alert: ResponseTimeDegraded
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
  for: 10m
  labels:
    severity: warning

# Disk space low
- alert: DiskSpaceLow
  expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) < 0.1
  for: 5m
  labels:
    severity: warning
```

### Monitoring Dashboards

#### Grafana Dashboards

1. **System Overview**: CPU, memory, disk, network
2. **Application Performance**: Response times, throughput, error rates
3. **Database Performance**: Connection pools, slow queries, replication lag
4. **Business Metrics**: User activity, transaction volumes, revenue
5. **Security Dashboard**: Failed logins, suspicious activity, compliance status

#### Custom Queries

```sql
-- Slow queries (>1 second)
SELECT query, total_time, calls, mean_time
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY mean_time DESC
LIMIT 10;

-- Active user sessions
SELECT usename, client_addr, state, query_start
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;

-- Cache hit rate
SELECT sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_hit_ratio
FROM pg_statio_user_tables;
```

## Incident Response

### Incident Classification

#### Severity Levels

- **SEV-1 (Critical)**: Complete system outage, data loss, security breach
- **SEV-2 (High)**: Major functionality broken, significant performance degradation
- **SEV-3 (Medium)**: Minor functionality issues, intermittent problems
- **SEV-4 (Low)**: Cosmetic issues, minor inconveniences

#### Response Times

- **SEV-1**: Response within 15 minutes, resolution within 4 hours
- **SEV-2**: Response within 30 minutes, resolution within 8 hours
- **SEV-3**: Response within 2 hours, resolution within 24 hours
- **SEV-4**: Response within 4 hours, resolution within 72 hours

### Incident Response Process

#### 1. Detection and Assessment

```bash
# Gather initial information
date
whoami
hostname

# Check system status
systemctl status nexus-backend
docker ps
ps aux | grep nexus

# Check recent logs
tail -n 100 /var/log/nexus/application.log
journalctl -u nexus-backend --since "1 hour ago"
```

#### 2. Containment

```bash
# Stop accepting new requests (if needed)
kubectl scale deployment nexus-backend --replicas=0

# Isolate affected components
docker pause affected_container

# Implement temporary fixes
# e.g., restart services, clear caches, etc.
```

#### 3. Investigation

```bash
# Collect detailed logs
tar czf incident_logs_$(date +%Y%m%d_%H%M%S).tar.gz /var/log/nexus/

# Database forensics
psql -c "SELECT * FROM audit_log WHERE created_at > now() - interval '1 hour'"

# Network analysis
tcpdump -i eth0 -w incident_traffic.pcap -c 10000

# Memory analysis
gcore $(pgrep nexus-backend)
```

#### 4. Resolution

```bash
# Apply fixes
kubectl apply -f fixed_deployment.yaml

# Rollback if needed
kubectl rollout undo deployment/nexus-backend

# Database fixes
psql -f fix_script.sql
```

#### 5. Recovery

```bash
# Restore from backup if needed
./scripts/restore_from_backup.sh

# Validate system health
curl -f https://api.nexusplatform.com/health

# Gradually increase traffic
kubectl scale deployment nexus-backend --replicas=1
kubectl scale deployment nexus-backend --replicas=3
```

#### 6. Post-Incident Review

- Document incident timeline
- Identify root cause
- Implement preventive measures
- Update runbooks and procedures

### Common Incident Scenarios

#### Application Crash

```bash
# Check crash logs
coredumpctl list
coredumpctl info <crash_id>

# Restart application
systemctl restart nexus-backend

# Check for memory leaks
valgrind --tool=memcheck python main.py
```

#### Database Connection Issues

```bash
# Check database status
psql -c "SELECT version()"
psql -c "SELECT * FROM pg_stat_activity"

# Restart database if needed
systemctl restart postgresql

# Check connection pool
python -c "import psycopg2; psycopg2.connect(os.environ['DATABASE_URL'])"
```

#### High CPU Usage

```bash
# Identify high CPU processes
ps aux --sort=-%cpu | head -10

# Profile application
python -m cProfile -s cumtime main.py

# Check for infinite loops or memory leaks
py-spy top --pid $(pgrep nexus-backend)
```

## Maintenance Procedures

### Weekly Maintenance

#### Security Updates

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Update Python packages
pip install --upgrade -r requirements.txt

# Update Docker images
docker-compose pull
docker-compose up -d

# Restart services
systemctl restart nexus-backend
```

#### Database Maintenance

```bash
# Vacuum and analyze
psql -c "VACUUM ANALYZE"

# Reindex if needed
psql -c "REINDEX DATABASE nexus_prod"

# Update statistics
psql -c "ANALYZE"
```

#### Log Rotation

```bash
# Rotate application logs
logrotate -f /etc/logrotate.d/nexus

# Archive old logs
find /var/log/nexus -name "*.log.*" -mtime +30 -delete

# Compress current logs
gzip /var/log/nexus/*.log.1
```

### Monthly Maintenance

#### Performance Optimization

```bash
# Database optimization
psql -f scripts/optimize_database.sql

# Cache optimization
redis-cli FLUSHDB ASYNC

# Elasticsearch optimization
curl -X POST "localhost:9200/_forcemerge?max_num_segments=1"
```

#### Capacity Planning

- Review resource utilization trends
- Plan for scaling requirements
- Update infrastructure as code
- Review backup retention policies

### Quarterly Maintenance

#### Comprehensive Testing

```bash
# Run full test suite
python scripts/run_comprehensive_tests.py

# Load testing
python scripts/run_performance_tests.sh

# Security scanning
python scripts/run_automated_security_scan.sh

# Disaster recovery testing
python scripts/test_backup_restore.py
```

#### Compliance Audits

- Review access controls
- Audit user permissions
- Check data retention policies
- Validate encryption standards

## Backup and Recovery

### Backup Verification

```bash
# Test backup integrity
gunzip -c backup_file.sql.gz | head -10

# Test restore procedure
createdb nexus_test_restore
psql -d nexus_test_restore < backup_file.sql
psql -d nexus_test_restore -c "SELECT COUNT(*) FROM users"
dropdb nexus_test_restore
```

### Recovery Time Objectives

- **RTO (Recovery Time Objective)**: 4 hours for full service restoration
- **RPO (Recovery Point Objective)**: 1 hour data loss tolerance

### Disaster Recovery Testing

```bash
# Simulate failure scenarios
# 1. Application server failure
kubectl delete pod nexus-backend-xyz

# 2. Database failure
systemctl stop postgresql

# 3. Network partition
iptables -A INPUT -s affected_ip -j DROP

# 4. Full region failure (AWS)
aws ec2 stop-instances --instance-ids $INSTANCE_ID
```

## Performance Optimization

### Application Optimization

#### Code Profiling

```bash
# Profile application performance
python -m cProfile -o profile_output.prof main.py
snakeviz profile_output.prof

# Memory profiling
python -m memory_profiler main.py

# Line-by-line profiling
kernprof -l -v main.py
```

#### Database Optimization

```sql
-- Identify slow queries
SELECT query, total_time, calls, mean_time
FROM pg_stat_statements
WHERE mean_time > 1000
ORDER BY total_time DESC
LIMIT 10;

-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_transactions_user_date
ON transactions (user_id, created_at DESC);

-- Optimize table bloat
VACUUM FULL transactions;
```

#### Cache Optimization

```bash
# Monitor cache hit rates
redis-cli info | grep keyspace_hits
redis-cli info | grep keyspace_misses

# Optimize cache keys
# Use consistent naming conventions
# Implement cache warming strategies
```

### Infrastructure Optimization

#### Auto-scaling Configuration

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nexus-backend-hpa
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

#### Resource Limits

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: nexus-backend
      resources:
        requests:
          memory: "512Mi"
          cpu: "250m"
        limits:
          memory: "1Gi"
          cpu: "500m"
```

## Security Operations

### Daily Security Monitoring

```bash
# Check for suspicious logins
grep "failed.*login" /var/log/nexus/security.log | tail -10

# Monitor for unusual traffic patterns
netstat -antp | grep :443 | wc -l

# Check for security alerts
tail -f /var/log/nexus/security.log | grep -i "alert\|warning"
```

### Security Incident Response

#### Compromised Account Detection

```bash
# Check for unusual login patterns
SELECT user_id, COUNT(*) as login_count, array_agg(client_ip) as ips
FROM login_attempts
WHERE created_at > now() - interval '1 hour'
GROUP BY user_id
HAVING COUNT(*) > 10;

# Lock suspicious accounts
UPDATE users SET status = 'locked' WHERE user_id = $SUSPICIOUS_USER_ID;
```

#### DDoS Attack Response

```bash
# Enable rate limiting
iptables -A INPUT -p tcp --dport 443 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT

# Block attacking IPs
iptables -A INPUT -s $ATTACKER_IP -j DROP

# Scale up infrastructure
kubectl scale deployment nexus-backend --replicas=10
```

### Security Audits

#### Automated Security Scans

```bash
# Run daily security scans
python scripts/run_automated_security_scan.sh

# Weekly comprehensive audit
python scripts/security_audit.py

# Monthly compliance check
python scripts/compliance_check.py
```

## Compliance and Auditing

### Regulatory Compliance

#### GDPR Compliance

- Data subject access requests
- Right to erasure procedures
- Data breach notification protocols
- Consent management

#### PCI DSS Compliance

- Cardholder data protection
- Security assessment procedures
- Incident response planning
- Regular vulnerability scanning

### Audit Logging

#### Audit Events to Monitor

- User authentication events
- Administrative actions
- Data access and modifications
- Security policy changes
- System configuration changes

#### Audit Log Analysis

```sql
-- Daily audit summary
SELECT
    DATE(created_at) as audit_date,
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users
FROM audit_log
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY DATE(created_at), event_type
ORDER BY audit_date DESC, event_count DESC;

-- Suspicious activity detection
SELECT user_id, event_type, COUNT(*) as frequency
FROM audit_log
WHERE created_at > now() - interval '1 hour'
    AND event_type IN ('failed_login', 'permission_denied', 'suspicious_activity')
GROUP BY user_id, event_type
HAVING COUNT(*) > 5;
```

### Compliance Reporting

#### Monthly Compliance Reports

- Access control effectiveness
- Data encryption verification
- Security incident summary
- Audit log review results
- Compliance test results

#### Annual Compliance Audits

- Third-party security assessment
- Penetration testing results
- Code security review
- Infrastructure security audit
- Compliance certification renewal

---

## Emergency Contacts

### On-Call Engineers

- **Primary**: +1-800-NEXUS-911
- **Secondary**: +1-800-NEXUS-912
- **Management**: +1-800-NEXUS-999

### External Resources

- **AWS Support**: 1-888-280-4331
- **CloudFlare**: support@cloudflare.com
- **Security Team**: security@nexusplatform.com

### Escalation Matrix

| Severity | Response Time | Escalation Path             |
| -------- | ------------- | --------------------------- |
| Critical | 15 minutes    | On-call → Manager → C-suite |
| High     | 30 minutes    | On-call → Senior Engineer   |
| Medium   | 2 hours       | Next business day           |
| Low      | 4 hours       | Weekly review               |

For additional procedures, visit https://docs.nexusplatform.com/operations
