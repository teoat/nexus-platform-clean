#!/bin/bash
# NEXUS Platform Monitoring Script
# This script provides monitoring and health checking capabilities

set -euo pipefail

# Configuration
NAMESPACE="nexus-platform"
MONITORING_NAMESPACE="monitoring"
LOG_FILE="/var/log/monitor.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    error "$1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if kubectl is available
    if ! command -v kubectl >/dev/null 2>&1; then
        error_exit "kubectl command not found. Please install kubectl."
    fi
    
    # Check if curl is available
    if ! command -v curl >/dev/null 2>&1; then
        error_exit "curl command not found. Please install curl."
    fi
    
    # Check if kubectl can connect to cluster
    if ! kubectl cluster-info >/dev/null 2>&1; then
        error_exit "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    fi
    
    success "Prerequisites check completed"
}

# Check pod status
check_pod_status() {
    log "Checking pod status..."
    
    local failed_pods=0
    
    # Check nexus-platform namespace
    while IFS= read -r line; do
        local pod_name=$(echo "$line" | awk '{print $1}')
        local status=$(echo "$line" | awk '{print $3}')
        local ready=$(echo "$line" | awk '{print $2}')
        
        if [ "$status" != "Running" ] || [ "$ready" != "1/1" ]; then
            error "Pod $pod_name is not running properly (Status: $status, Ready: $ready)"
            ((failed_pods++))
        else
            success "Pod $pod_name is running properly"
        fi
    done < <(kubectl get pods -n "$NAMESPACE" --no-headers)
    
    # Check monitoring namespace
    while IFS= read -r line; do
        local pod_name=$(echo "$line" | awk '{print $1}')
        local status=$(echo "$line" | awk '{print $3}')
        local ready=$(echo "$line" | awk '{print $2}')
        
        if [ "$status" != "Running" ] || [ "$ready" != "1/1" ]; then
            error "Pod $pod_name is not running properly (Status: $status, Ready: $ready)"
            ((failed_pods++))
        else
            success "Pod $pod_name is running properly"
        fi
    done < <(kubectl get pods -n "$MONITORING_NAMESPACE" --no-headers)
    
    if [ $failed_pods -eq 0 ]; then
        success "All pods are running properly"
    else
        error_exit "$failed_pods pods are not running properly"
    fi
}

# Check service status
check_service_status() {
    log "Checking service status..."
    
    local failed_services=0
    
    # Check nexus-platform services
    while IFS= read -r line; do
        local service_name=$(echo "$line" | awk '{print $1}')
        local cluster_ip=$(echo "$line" | awk '{print $3}')
        
        if [ "$cluster_ip" = "<none>" ]; then
            error "Service $service_name has no cluster IP"
            ((failed_services++))
        else
            success "Service $service_name is running (IP: $cluster_ip)"
        fi
    done < <(kubectl get services -n "$NAMESPACE" --no-headers)
    
    # Check monitoring services
    while IFS= read -r line; do
        local service_name=$(echo "$line" | awk '{print $1}')
        local cluster_ip=$(echo "$line" | awk '{print $3}')
        
        if [ "$cluster_ip" = "<none>" ]; then
            error "Service $service_name has no cluster IP"
            ((failed_services++))
        else
            success "Service $service_name is running (IP: $cluster_ip)"
        fi
    done < <(kubectl get services -n "$MONITORING_NAMESPACE" --no-headers)
    
    if [ $failed_services -eq 0 ]; then
        success "All services are running properly"
    else
        error_exit "$failed_services services are not running properly"
    fi
}

# Check resource usage
check_resource_usage() {
    log "Checking resource usage..."
    
    # Check pod resource usage
    echo "=== Pod Resource Usage ==="
    kubectl top pods -n "$NAMESPACE" 2>/dev/null || warning "Cannot get pod resource usage"
    echo ""
    
    # Check node resource usage
    echo "=== Node Resource Usage ==="
    kubectl top nodes 2>/dev/null || warning "Cannot get node resource usage"
    echo ""
    
    # Check for resource limits
    local over_limit_pods=0
    
    while IFS= read -r line; do
        local pod_name=$(echo "$line" | awk '{print $1}')
        local cpu_usage=$(echo "$line" | awk '{print $2}')
        local memory_usage=$(echo "$line" | awk '{print $3}')
        
        # Check if CPU usage is over 80%
        local cpu_percent=$(echo "$cpu_usage" | sed 's/m//' | awk '{print int($1/10)}')
        if [ "$cpu_percent" -gt 80 ]; then
            warning "Pod $pod_name CPU usage is high: $cpu_usage"
            ((over_limit_pods++))
        fi
        
        # Check if memory usage is over 80%
        local memory_percent=$(echo "$memory_usage" | sed 's/Mi//' | awk '{print int($1/100)}')
        if [ "$memory_percent" -gt 80 ]; then
            warning "Pod $pod_name memory usage is high: $memory_usage"
            ((over_limit_pods++))
        fi
    done < <(kubectl top pods -n "$NAMESPACE" --no-headers 2>/dev/null)
    
    if [ $over_limit_pods -eq 0 ]; then
        success "Resource usage is within normal limits"
    else
        warning "$over_limit_pods pods have high resource usage"
    fi
}

# Check application health
check_application_health() {
    log "Checking application health..."
    
    # Get service endpoints
    local backend_service=$(kubectl get service backend-service -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}')
    local frontend_service=$(kubectl get service frontend-service -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}')
    local nginx_service=$(kubectl get service nginx-service -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}')
    
    # Check backend health
    if [ -n "$backend_service" ]; then
        if kubectl exec -n "$NAMESPACE" deployment/backend-deployment -- curl -f http://localhost:8000/health >/dev/null 2>&1; then
            success "Backend health check passed"
        else
            error "Backend health check failed"
        fi
    else
        error "Backend service not found"
    fi
    
    # Check frontend health
    if [ -n "$frontend_service" ]; then
        if kubectl exec -n "$NAMESPACE" deployment/frontend-deployment -- curl -f http://localhost:80/health >/dev/null 2>&1; then
            success "Frontend health check passed"
        else
            error "Frontend health check failed"
        fi
    else
        error "Frontend service not found"
    fi
    
    # Check nginx health
    if [ -n "$nginx_service" ]; then
        if kubectl exec -n "$NAMESPACE" deployment/nginx -- curl -f http://localhost:80/health >/dev/null 2>&1; then
            success "Nginx health check passed"
        else
            error "Nginx health check failed"
        fi
    else
        error "Nginx service not found"
    fi
}

# Check database connectivity
check_database_connectivity() {
    log "Checking database connectivity..."
    
    # Check PostgreSQL connectivity
    if kubectl exec -n "$NAMESPACE" deployment/postgres -- pg_isready -U nexus -d nexus >/dev/null 2>&1; then
        success "PostgreSQL is ready"
    else
        error "PostgreSQL is not ready"
    fi
    
    # Check Redis connectivity
    if kubectl exec -n "$NAMESPACE" deployment/redis -- redis-cli ping >/dev/null 2>&1; then
        success "Redis is ready"
    else
        error "Redis is not ready"
    fi
}

# Check monitoring stack
check_monitoring_stack() {
    log "Checking monitoring stack..."
    
    # Check Prometheus
    if kubectl get pods -n "$MONITORING_NAMESPACE" -l app=prometheus | grep -q Running; then
        success "Prometheus is running"
    else
        error "Prometheus is not running"
    fi
    
    # Check Grafana
    if kubectl get pods -n "$MONITORING_NAMESPACE" -l app=grafana | grep -q Running; then
        success "Grafana is running"
    else
        error "Grafana is not running"
    fi
    
    # Check Alertmanager
    if kubectl get pods -n "$MONITORING_NAMESPACE" -l app=alertmanager | grep -q Running; then
        success "Alertmanager is running"
    else
        error "Alertmanager is not running"
    fi
}

# Check logs for errors
check_logs() {
    log "Checking logs for errors..."
    
    local error_count=0
    
    # Check backend logs
    if kubectl logs -n "$NAMESPACE" -l app=backend --tail=100 | grep -i error >/dev/null 2>&1; then
        warning "Errors found in backend logs"
        ((error_count++))
    else
        success "No errors found in backend logs"
    fi
    
    # Check frontend logs
    if kubectl logs -n "$NAMESPACE" -l app=frontend --tail=100 | grep -i error >/dev/null 2>&1; then
        warning "Errors found in frontend logs"
        ((error_count++))
    else
        success "No errors found in frontend logs"
    fi
    
    # Check nginx logs
    if kubectl logs -n "$NAMESPACE" -l app=nginx --tail=100 | grep -i error >/dev/null 2>&1; then
        warning "Errors found in nginx logs"
        ((error_count++))
    else
        success "No errors found in nginx logs"
    fi
    
    if [ $error_count -eq 0 ]; then
        success "No errors found in application logs"
    else
        warning "$error_count services have errors in their logs"
    fi
}

# Check security policies
check_security_policies() {
    log "Checking security policies..."
    
    # Check network policies
    local network_policies=$(kubectl get networkpolicies -n "$NAMESPACE" --no-headers | wc -l)
    if [ "$network_policies" -gt 0 ]; then
        success "Network policies are configured ($network_policies policies)"
    else
        warning "No network policies found"
    fi
    
    # Check RBAC policies
    local role_bindings=$(kubectl get rolebindings -n "$NAMESPACE" --no-headers | wc -l)
    if [ "$role_bindings" -gt 0 ]; then
        success "RBAC policies are configured ($role_bindings role bindings)"
    else
        warning "No RBAC policies found"
    fi
    
    # Check pod security policies
    local psp_count=$(kubectl get podsecuritypolicies --no-headers | wc -l)
    if [ "$psp_count" -gt 0 ]; then
        success "Pod security policies are configured ($psp_count policies)"
    else
        warning "No pod security policies found"
    fi
}

# Generate monitoring report
generate_report() {
    log "Generating monitoring report..."
    
    local report_file="/tmp/monitoring_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "NEXUS Platform Monitoring Report"
        echo "==============================="
        echo "Timestamp: $(date)"
        echo ""
        echo "=== Pod Status ==="
        kubectl get pods -n "$NAMESPACE" -o wide
        echo ""
        echo "=== Service Status ==="
        kubectl get services -n "$NAMESPACE"
        echo ""
        echo "=== Ingress Status ==="
        kubectl get ingress -n "$NAMESPACE"
        echo ""
        echo "=== Resource Usage ==="
        kubectl top pods -n "$NAMESPACE"
        echo ""
        echo "=== Node Status ==="
        kubectl top nodes
        echo ""
        echo "=== Monitoring Stack ==="
        kubectl get pods -n "$MONITORING_NAMESPACE"
        echo ""
        echo "=== Recent Events ==="
        kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -20
        echo ""
    } > "$report_file"
    
    success "Monitoring report generated: $report_file"
}

# Send alert
send_alert() {
    local alert_type="$1"
    local message="$2"
    
    if [ "${SEND_ALERTS:-false}" = "true" ]; then
        # Send to Slack
        if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
            curl -X POST -H 'Content-type: application/json' \
                --data "{\"text\":\"🚨 NEXUS Platform Alert: $alert_type - $message\"}" \
                "$SLACK_WEBHOOK_URL" 2>/dev/null || true
        fi
        
        # Send email
        if command -v mail >/dev/null 2>&1 && [ -n "${ALERT_EMAIL:-}" ]; then
            echo "$message" | mail -s "NEXUS Platform Alert: $alert_type" "$ALERT_EMAIL" 2>/dev/null || true
        fi
    fi
}

# Main monitoring function
monitor() {
    log "Starting NEXUS Platform monitoring..."
    
    # Check prerequisites
    check_prerequisites
    
    # Check pod status
    check_pod_status
    
    # Check service status
    check_service_status
    
    # Check resource usage
    check_resource_usage
    
    # Check application health
    check_application_health
    
    # Check database connectivity
    check_database_connectivity
    
    # Check monitoring stack
    check_monitoring_stack
    
    # Check logs for errors
    check_logs
    
    # Check security policies
    check_security_policies
    
    # Generate report
    generate_report
    
    success "NEXUS Platform monitoring completed successfully!"
}

# Continuous monitoring
monitor_continuous() {
    local interval="${1:-60}"
    
    log "Starting continuous monitoring (interval: ${interval}s)..."
    
    while true; do
        monitor
        sleep "$interval"
    done
}

# Show usage
usage() {
    echo "Usage: $0 [monitor|continuous|report] [options]"
    echo ""
    echo "Commands:"
    echo "  monitor                    - Run one-time monitoring check"
    echo "  continuous [interval]      - Run continuous monitoring (default interval: 60s)"
    echo "  report                     - Generate monitoring report only"
    echo ""
    echo "Environment Variables:"
    echo "  SEND_ALERTS               - Send alerts (default: false)"
    echo "  SLACK_WEBHOOK_URL         - Slack webhook URL"
    echo "  ALERT_EMAIL               - Email for alerts"
}

# Main script logic
case "${1:-monitor}" in
    monitor)
        monitor
        ;;
    continuous)
        monitor_continuous "${2:-60}"
        ;;
    report)
        generate_report
        ;;
    *)
        usage
        exit 1
        ;;
esac
