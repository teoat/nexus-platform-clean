#!/bin/bash

# NEXUS Platform - Maintenance Automation Script
# Phase 5: Deployment & Monitoring Implementation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
MAINTENANCE_LOG="/var/log/nexus/maintenance.log"
BACKUP_DIR="/backups/nexus"
LOG_RETENTION_DAYS=30
BACKUP_RETENTION_DAYS=7
MONITORING_DATA_RETENTION_DAYS=30

# Create log directory
mkdir -p "$(dirname "$MAINTENANCE_LOG")"

# Logging function
log_maintenance() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$MAINTENANCE_LOG"
}

# Database maintenance
maintain_database() {
    log_info "🗄️ Performing database maintenance..."
    
    # Connect to database and perform maintenance
    docker-compose -f docker-compose.prod.yml exec -T postgres psql -U nexus_user -d nexus_platform << EOF
-- Update table statistics
ANALYZE;

-- Reindex tables
REINDEX DATABASE nexus_platform;

-- Clean up old logs
DELETE FROM nexus_security_events WHERE timestamp < NOW() - INTERVAL '30 days';
DELETE FROM nexus_performance_metrics WHERE timestamp < NOW() - INTERVAL '30 days';

-- Vacuum tables
VACUUM ANALYZE;
EOF
    
    log_success "Database maintenance completed"
}

# Redis maintenance
maintain_redis() {
    log_info "🔴 Performing Redis maintenance..."
    
    # Connect to Redis and perform maintenance
    docker-compose -f docker-compose.prod.yml exec -T redis redis-cli << EOF
-- Memory optimization
MEMORY PURGE

-- Clear expired keys
EVAL "return redis.call('del', unpack(redis.call('keys', '*:expired:*')))" 0

-- Get memory info
INFO memory
EOF
    
    log_success "Redis maintenance completed"
}

# Log rotation and cleanup
maintain_logs() {
    log_info "📝 Performing log maintenance..."
    
    # Rotate application logs
    find /var/log/nexus -name "*.log" -mtime +$LOG_RETENTION_DAYS -delete
    
    # Rotate Docker logs
    docker system prune -f --volumes
    
    # Rotate Nginx logs
    if [ -d "/var/log/nginx" ]; then
        find /var/log/nginx -name "*.log" -mtime +$LOG_RETENTION_DAYS -delete
    fi
    
    # Rotate system logs
    find /var/log -name "*.log" -mtime +$LOG_RETENTION_DAYS -delete 2>/dev/null || true
    
    log_success "Log maintenance completed"
}

# Backup maintenance
maintain_backups() {
    log_info "💾 Performing backup maintenance..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Create database backup
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="$BACKUP_DIR/nexus_backup_$timestamp.sql"
    
    docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U nexus_user nexus_platform > "$backup_file"
    
    # Compress backup
    gzip "$backup_file"
    
    # Remove old backups
    find "$BACKUP_DIR" -name "nexus_backup_*.sql.gz" -mtime +$BACKUP_RETENTION_DAYS -delete
    
    log_success "Backup maintenance completed"
}

# Monitoring data maintenance
maintain_monitoring() {
    log_info "📊 Performing monitoring data maintenance..."
    
    # Clean up old Prometheus data
    if docker-compose -f docker-compose.prod.yml ps prometheus | grep -q "Up"; then
        docker-compose -f docker-compose.prod.yml exec prometheus promtool tsdb cleanup --storage.tsdb.path=/prometheus
    fi
    
    # Clean up old Grafana data
    if docker-compose -f docker-compose.prod.yml ps grafana | grep -q "Up"; then
        docker-compose -f docker-compose.prod.yml exec grafana find /var/lib/grafana -name "*.db" -mtime +$MONITORING_DATA_RETENTION_DAYS -delete
    fi
    
    log_success "Monitoring data maintenance completed"
}

# Security maintenance
maintain_security() {
    log_info "🔒 Performing security maintenance..."
    
    # Update security packages
    if command -v apt-get &> /dev/null; then
        apt-get update && apt-get upgrade -y
    elif command -v yum &> /dev/null; then
        yum update -y
    fi
    
    # Scan for security vulnerabilities
    if command -v docker &> /dev/null; then
        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image nexus-backend:latest
    fi
    
    # Check for failed login attempts
    if [ -f "/var/log/auth.log" ]; then
        failed_logins=$(grep "Failed password" /var/log/auth.log | wc -l)
        if [ "$failed_logins" -gt 100 ]; then
            log_warning "High number of failed login attempts: $failed_logins"
        fi
    fi
    
    log_success "Security maintenance completed"
}

# Performance optimization
optimize_performance() {
    log_info "⚡ Performing performance optimization..."
    
    # Optimize Docker images
    docker image prune -f
    
    # Optimize Docker volumes
    docker volume prune -f
    
    # Optimize system memory
    echo 3 > /proc/sys/vm/drop_caches
    
    # Check disk space
    disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 80 ]; then
        log_warning "High disk usage: ${disk_usage}%"
    fi
    
    # Check memory usage
    memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$memory_usage" -gt 80 ]; then
        log_warning "High memory usage: ${memory_usage}%"
    fi
    
    log_success "Performance optimization completed"
}

# Health checks
perform_health_checks() {
    log_info "🏥 Performing health checks..."
    
    # Check Docker services
    if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        log_error "Some Docker services are not running"
        return 1
    fi
    
    # Check API health
    if ! curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_error "Backend API health check failed"
        return 1
    fi
    
    # Check database health
    if ! docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U nexus_user -d nexus_platform >/dev/null 2>&1; then
        log_error "Database health check failed"
        return 1
    fi
    
    # Check Redis health
    if ! docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping >/dev/null 2>&1; then
        log_error "Redis health check failed"
        return 1
    fi
    
    log_success "All health checks passed"
}

# Generate maintenance report
generate_report() {
    log_info "📋 Generating maintenance report..."
    
    report_file="/var/log/nexus/maintenance_report_$(date +%Y%m%d).txt"
    
    cat > "$report_file" << EOF
NEXUS Platform Maintenance Report
Generated: $(date)
=====================================

System Information:
- Hostname: $(hostname)
- Uptime: $(uptime)
- Disk Usage: $(df -h / | awk 'NR==2 {print $5}')
- Memory Usage: $(free -h | awk 'NR==2 {print $3 "/" $2}')

Docker Services Status:
$(docker-compose -f docker-compose.prod.yml ps)

Recent Maintenance Activities:
$(tail -20 "$MAINTENANCE_LOG")

Health Check Results:
$(perform_health_checks 2>&1)

EOF
    
    log_success "Maintenance report generated: $report_file"
}

# Main maintenance function
main() {
    local start_time=$(date +%s)
    
    log_maintenance "Starting maintenance routine"
    
    # Run maintenance tasks
    maintain_database
    maintain_redis
    maintain_logs
    maintain_backups
    maintain_monitoring
    maintain_security
    optimize_performance
    
    # Perform health checks
    if perform_health_checks; then
        log_success "All health checks passed"
    else
        log_error "Health checks failed"
        exit 1
    fi
    
    # Generate report
    generate_report
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_maintenance "Maintenance routine completed in ${duration}s"
    log_success "🎉 Maintenance completed successfully!"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --database-only    Only perform database maintenance"
        echo "  --logs-only        Only perform log maintenance"
        echo "  --backup-only      Only perform backup maintenance"
        echo "  --security-only    Only perform security maintenance"
        echo "  --health-only      Only perform health checks"
        echo "  --help             Show this help message"
        exit 0
        ;;
    --database-only)
        log_info "Running database maintenance only"
        maintain_database
        ;;
    --logs-only)
        log_info "Running log maintenance only"
        maintain_logs
        ;;
    --backup-only)
        log_info "Running backup maintenance only"
        maintain_backups
        ;;
    --security-only)
        log_info "Running security maintenance only"
        maintain_security
        ;;
    --health-only)
        log_info "Running health checks only"
        perform_health_checks
        ;;
    *)
        main "$@"
        ;;
esac
