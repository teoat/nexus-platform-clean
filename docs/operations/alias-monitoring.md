# Alias Monitoring Operations Guide

## Overview

This guide provides comprehensive information for monitoring, troubleshooting, and maintaining the NEXUS SSOT alias management system in production environments.

## Monitoring Dashboard

### Key Metrics to Monitor

1. **System Health**
   - Registry uptime
   - Service availability
   - Error rates
   - Response times

2. **Alias Performance**
   - Resolution times
   - Cache hit rates
   - Throughput
   - Error breakdown

3. **Resource Usage**
   - Memory consumption
   - CPU usage
   - Disk space
   - Network I/O

## Health Checks

### Service Health Endpoint

```bash
# Check alias router health
curl -X GET "http://localhost:8000/api/alias/health"

# Expected response
{
  "status": "healthy",
  "service": "api-alias-router",
  "timestamp": 1640995200.0,
  "registry_anchors": 15,
  "registry_aliases": 45
}
```

### Registry Health Check

```bash
# Check registry statistics
curl -X GET "http://localhost:8000/api/alias/stats/registry"

# Expected response
{
  "total_anchors": 15,
  "total_aliases": 45,
  "active_aliases": 42,
  "alias_resolutions": 1500,
  "cache_size": 128
}
```

### Performance Metrics

```bash
# Check performance statistics
curl -X GET "http://localhost:8000/api/alias/stats/performance"

# Expected response
{
  "total_requests": 1500,
  "successful_requests": 1485,
  "failed_requests": 15,
  "average_response_time": 0.089,
  "error_breakdown": {
    "alias_not_found": 8,
    "timeout": 4,
    "internal_error": 3
  }
}
```

## Monitoring Scripts

### Health Check Script

```bash
#!/bin/bash
# health_check.sh

ALIAS_ROUTER_URL="http://localhost:8000/api/alias"
THRESHOLD_RESPONSE_TIME=0.5
THRESHOLD_ERROR_RATE=0.05

echo "🔍 NEXUS Alias Router Health Check"
echo "=================================="

# Check service health
echo "Checking service health..."
HEALTH_RESPONSE=$(curl -s -w "%{http_code}" "$ALIAS_ROUTER_URL/health")
HEALTH_CODE="${HEALTH_RESPONSE: -3}"
HEALTH_BODY="${HEALTH_RESPONSE%???}"

if [ "$HEALTH_CODE" = "200" ]; then
    echo "✅ Service is healthy"
    echo "$HEALTH_BODY" | jq '.'
else
    echo "❌ Service is unhealthy (HTTP $HEALTH_CODE)"
    exit 1
fi

# Check performance metrics
echo -e "\nChecking performance metrics..."
PERF_RESPONSE=$(curl -s "$ALIAS_ROUTER_URL/stats/performance")
TOTAL_REQUESTS=$(echo "$PERF_RESPONSE" | jq '.total_requests')
SUCCESSFUL_REQUESTS=$(echo "$PERF_RESPONSE" | jq '.successful_requests')
AVG_RESPONSE_TIME=$(echo "$PERF_RESPONSE" | jq '.average_response_time')

# Calculate error rate
if [ "$TOTAL_REQUESTS" -gt 0 ]; then
    ERROR_RATE=$(echo "scale=4; ($TOTAL_REQUESTS - $SUCCESSFUL_REQUESTS) / $TOTAL_REQUESTS" | bc)
    echo "Total requests: $TOTAL_REQUESTS"
    echo "Successful requests: $SUCCESSFUL_REQUESTS"
    echo "Error rate: $(echo "scale=2; $ERROR_RATE * 100" | bc)%"
    echo "Average response time: ${AVG_RESPONSE_TIME}s"
    
    # Check thresholds
    if (( $(echo "$AVG_RESPONSE_TIME > $THRESHOLD_RESPONSE_TIME" | bc -l) )); then
        echo "⚠️  Warning: High response time (${AVG_RESPONSE_TIME}s > ${THRESHOLD_RESPONSE_TIME}s)"
    fi
    
    if (( $(echo "$ERROR_RATE > $THRESHOLD_ERROR_RATE" | bc -l) )); then
        echo "⚠️  Warning: High error rate ($(echo "scale=2; $ERROR_RATE * 100" | bc)% > $(echo "scale=2; $THRESHOLD_ERROR_RATE * 100" | bc)%)"
    fi
else
    echo "ℹ️  No requests processed yet"
fi

echo -e "\n✅ Health check completed"
```

### Performance Monitoring Script

```bash
#!/bin/bash
# performance_monitor.sh

ALIAS_ROUTER_URL="http://localhost:8000/api/alias"
LOG_FILE="/var/log/nexus/alias_performance.log"
ALERT_EMAIL="alerts@nexus.internal"

# Function to log metrics
log_metrics() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local perf_data=$(curl -s "$ALIAS_ROUTER_URL/stats/performance")
    local registry_data=$(curl -s "$ALIAS_ROUTER_URL/stats/registry")
    
    echo "$timestamp,$perf_data,$registry_data" >> "$LOG_FILE"
}

# Function to check alerts
check_alerts() {
    local perf_data=$(curl -s "$ALIAS_ROUTER_URL/stats/performance")
    local total_requests=$(echo "$perf_data" | jq '.total_requests')
    local successful_requests=$(echo "$perf_data" | jq '.successful_requests')
    local avg_response_time=$(echo "$perf_data" | jq '.average_response_time')
    
    # Check error rate
    if [ "$total_requests" -gt 0 ]; then
        local error_rate=$(echo "scale=4; ($total_requests - $successful_requests) / $total_requests" | bc)
        
        if (( $(echo "$error_rate > 0.05" | bc -l) )); then
            echo "ALERT: High error rate detected: $(echo "scale=2; $error_rate * 100" | bc)%" | mail -s "NEXUS Alias Router Alert" "$ALERT_EMAIL"
        fi
        
        if (( $(echo "$avg_response_time > 1.0" | bc -l) )); then
            echo "ALERT: High response time detected: ${avg_response_time}s" | mail -s "NEXUS Alias Router Alert" "$ALERT_EMAIL"
        fi
    fi
}

# Main execution
log_metrics
check_alerts
```

## Troubleshooting

### Common Issues

#### 1. Alias Not Found (404)

**Symptoms:**
- HTTP 404 responses
- "Alias not found" errors

**Diagnosis:**
```bash
# Check if alias exists
curl -X GET "http://localhost:8000/api/alias/stats/registry" | jq '.total_aliases'

# Check specific alias
curl -X GET "http://localhost:8000/api/alias/nonexistent-alias" \
  -H "X-Context: frontend"
```

**Solutions:**
- Verify alias name and context
- Check if alias is active (not expired)
- Ensure proper context header

#### 2. High Response Times

**Symptoms:**
- Slow API responses
- Timeout errors

**Diagnosis:**
```bash
# Check performance metrics
curl -X GET "http://localhost:8000/api/alias/stats/performance" | jq '.average_response_time'

# Check cache hit rate
curl -X GET "http://localhost:8000/api/alias/stats/registry" | jq '.cache_size'
```

**Solutions:**
- Check target service health
- Verify network connectivity
- Review cache configuration
- Check system resources

#### 3. High Error Rates

**Symptoms:**
- Many failed requests
- 5xx HTTP responses

**Diagnosis:**
```bash
# Check error breakdown
curl -X GET "http://localhost:8000/api/alias/stats/performance" | jq '.error_breakdown'

# Check service logs
tail -f /var/log/nexus/alias_router.log
```

**Solutions:**
- Check target service availability
- Verify alias configurations
- Review governance rules
- Check system resources

#### 4. Cache Issues

**Symptoms:**
- Inconsistent responses
- Stale data

**Diagnosis:**
```bash
# Check cache statistics
curl -X GET "http://localhost:8000/api/alias/stats/registry" | jq '.cache_size'

# Clear cache (if supported)
curl -X POST "http://localhost:8000/api/alias/cache/clear"
```

**Solutions:**
- Restart the service to clear cache
- Check cache configuration
- Verify alias updates are propagated

### Log Analysis

#### Key Log Files

```bash
# Service logs
/var/log/nexus/alias_router.log
/var/log/nexus/ssot_registry.log

# Access logs
/var/log/nginx/access.log
/var/log/nginx/error.log

# System logs
/var/log/syslog
/var/log/messages
```

#### Log Analysis Commands

```bash
# Check for errors
grep -i "error\|exception\|failed" /var/log/nexus/alias_router.log

# Check response times
grep "response_time" /var/log/nexus/alias_router.log | awk '{print $NF}' | sort -n

# Check alias usage
grep "alias_resolution" /var/log/nexus/ssot_registry.log | wc -l

# Check cache performance
grep "cache" /var/log/nexus/alias_router.log | tail -20
```

## Performance Tuning

### Cache Configuration

```yaml
# config/alias_governance.yaml
performance:
  caching:
    enabled: true
    ttl: "5m"  # Adjust based on usage patterns
    max_size: 10000  # Increase for high-traffic systems
    cleanup_interval: "1h"
```

### Registry Optimization

```python
# Optimize registry settings
registry_config = {
    "cache_duration": 300,  # 5 minutes
    "max_cache_size": 10000,
    "cleanup_interval": 3600,  # 1 hour
    "audit_retention": 7 * 24 * 3600  # 7 days
}
```

### Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX idx_aliases_context ON aliases(context);
CREATE INDEX idx_aliases_alias ON aliases(alias);
CREATE INDEX idx_aliases_canonical ON aliases(canonical);
CREATE INDEX idx_aliases_status ON aliases(status);
CREATE INDEX idx_aliases_created_at ON aliases(created_at);
```

## Backup and Recovery

### Backup Procedures

```bash
#!/bin/bash
# backup_ssot.sh

BACKUP_DIR="/backups/nexus/ssot"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/ssot_backup_$DATE.tar.gz"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup registry data
tar -czf "$BACKUP_FILE" \
  config/ssot_registry.json \
  config/alias_governance.yaml \
  logs/

echo "Backup created: $BACKUP_FILE"

# Cleanup old backups (keep last 30 days)
find "$BACKUP_DIR" -name "ssot_backup_*.tar.gz" -mtime +30 -delete
```

### Recovery Procedures

```bash
#!/bin/bash
# restore_ssot.sh

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Stop services
systemctl stop nexus-alias-router
systemctl stop nexus-ssot-registry

# Extract backup
tar -xzf "$BACKUP_FILE" -C /

# Restart services
systemctl start nexus-ssot-registry
systemctl start nexus-alias-router

echo "Recovery completed"
```

## Maintenance Tasks

### Daily Tasks

```bash
#!/bin/bash
# daily_maintenance.sh

# Check service health
./health_check.sh

# Clean up expired aliases
curl -X POST "http://localhost:8000/api/alias/cleanup/expired"

# Backup registry data
./backup_ssot.sh

# Rotate logs
logrotate /etc/logrotate.d/nexus-alias-router
```

### Weekly Tasks

```bash
#!/bin/bash
# weekly_maintenance.sh

# Analyze performance metrics
./performance_monitor.sh

# Clean up old audit logs
find /var/log/nexus -name "*.log" -mtime +7 -delete

# Update governance rules (if needed)
# Review and update alias_governance.yaml

# Generate usage reports
curl -X GET "http://localhost:8000/api/alias/stats/performance" > /reports/weekly_performance.json
```

### Monthly Tasks

```bash
#!/bin/bash
# monthly_maintenance.sh

# Full system backup
./backup_ssot.sh

# Performance analysis
./performance_monitor.sh > /reports/monthly_performance.txt

# Security audit
./security_audit.sh

# Capacity planning
./capacity_analysis.sh
```

## Alerting

### Alert Conditions

1. **Critical Alerts**
   - Service down (HTTP 5xx)
   - High error rate (>5%)
   - High response time (>1s)
   - Disk space low (<10%)

2. **Warning Alerts**
   - Moderate error rate (>1%)
   - Moderate response time (>500ms)
   - Cache hit rate low (<90%)
   - Memory usage high (>80%)

### Alert Configuration

```yaml
# config/alerts.yaml
alerts:
  email:
    enabled: true
    smtp_server: "smtp.nexus.internal"
    recipients: ["alerts@nexus.internal", "ops@nexus.internal"]
  
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/nexus/alerts"
    channel: "#nexus-alerts"
  
  thresholds:
    error_rate: 0.05
    response_time: 1.0
    cache_hit_rate: 0.9
    memory_usage: 0.8
```

## Security Considerations

### Access Control

```bash
# Restrict access to admin endpoints
# Only allow from internal networks
iptables -A INPUT -p tcp --dport 8000 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j DROP
```

### Audit Logging

```bash
# Monitor audit logs for suspicious activity
grep -i "unauthorized\|permission\|denied" /var/log/nexus/audit.log

# Check for unusual patterns
awk '{print $1}' /var/log/nexus/access.log | sort | uniq -c | sort -nr
```

### Data Protection

```bash
# Encrypt sensitive data
gpg --symmetric --cipher-algo AES256 config/ssot_registry.json

# Secure backup storage
chmod 600 /backups/nexus/ssot/*
```

## Support and Escalation

### Support Contacts

- **Level 1**: NEXUS Operations Team
- **Level 2**: NEXUS Development Team
- **Level 3**: NEXUS Architecture Team

### Escalation Procedures

1. **Service Down**: Immediate escalation to Level 2
2. **Performance Issues**: Escalate to Level 2 within 1 hour
3. **Security Issues**: Immediate escalation to Level 3
4. **Data Loss**: Immediate escalation to Level 3

### Emergency Procedures

```bash
# Emergency service restart
systemctl restart nexus-alias-router
systemctl restart nexus-ssot-registry

# Emergency cache clear
curl -X POST "http://localhost:8000/api/alias/cache/clear"

# Emergency failover
# Switch to backup system if available
```

## Documentation Updates

This guide should be updated whenever:
- New monitoring tools are added
- Alert thresholds are changed
- Troubleshooting procedures are updated
- New issues are discovered and resolved

Keep this document current and accessible to all operations team members.
