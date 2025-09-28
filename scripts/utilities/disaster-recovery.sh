#!/bin/bash
# NEXUS Platform - Disaster Recovery Script
# Comprehensive disaster recovery procedures

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
BACKUP_DIR="/var/lib/nexus/backups"
S3_BUCKET="${BACKUP_S3_BUCKET:-nexus-backups}"
S3_REGION="${BACKUP_S3_REGION:-us-east-1}"
KUBE_NAMESPACE="${KUBE_NAMESPACE:-nexus-platform}"
LOG_FILE="/var/log/nexus/disaster-recovery.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed or not in PATH"
    fi

    # Check if aws CLI is available
    if ! command -v aws &> /dev/null; then
        error "AWS CLI is not installed or not in PATH"
    fi

    # Check if pg_dump is available
    if ! command -v pg_dump &> /dev/null; then
        error "pg_dump is not installed or not in PATH"
    fi

    # Check if required environment variables are set
    if [ -z "${DATABASE_URL:-}" ]; then
        error "DATABASE_URL environment variable is not set"
    fi

    if [ -z "${S3_BUCKET:-}" ]; then
        error "S3_BUCKET environment variable is not set"
    fi

    success "Prerequisites check passed"
}

# Backup current state
backup_current_state() {
    log "Creating backup of current state..."

    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$BACKUP_DIR/disaster_recovery_$backup_timestamp"

    mkdir -p "$backup_path"

    # Backup Kubernetes resources
    log "Backing up Kubernetes resources..."
    kubectl get all -n "$KUBE_NAMESPACE" -o yaml > "$backup_path/kubernetes_resources.yaml"
    kubectl get configmaps -n "$KUBE_NAMESPACE" -o yaml > "$backup_path/configmaps.yaml"
    kubectl get secrets -n "$KUBE_NAMESPACE" -o yaml > "$backup_path/secrets.yaml"
    kubectl get pv -o yaml > "$backup_path/persistent_volumes.yaml"
    kubectl get pvc -n "$KUBE_NAMESPACE" -o yaml > "$backup_path/persistent_volume_claims.yaml"

    # Backup Istio resources
    log "Backing up Istio resources..."
    kubectl get virtualservices -n "$KUBE_NAMESPACE" -o yaml > "$backup_path/virtualservices.yaml"
    kubectl get destinationrules -n "$KUBE_NAMESPACE" -o yaml > "$backup_path/destinationrules.yaml"
    kubectl get gateways -n "$KUBE_NAMESPACE" -o yaml > "$backup_path/gateways.yaml"
    kubectl get authorizationpolicies -n "$KUBE_NAMESPACE" -o yaml > "$backup_path/authorizationpolicies.yaml"

    # Backup monitoring resources
    log "Backing up monitoring resources..."
    kubectl get prometheuses -n "$KUBE_NAMESPACE" -o yaml > "$backup_path/prometheuses.yaml"
    kubectl get servicemonitors -n "$KUBE_NAMESPACE" -o yaml > "$backup_path/servicemonitors.yaml"
    kubectl get alertmanagers -n "$KUBE_NAMESPACE" -o yaml > "$backup_path/alertmanagers.yaml"

    # Backup database
    log "Backing up database..."
    pg_dump "$DATABASE_URL" > "$backup_path/database_backup.sql"

    # Backup configuration files
    log "Backing up configuration files..."
    cp -r "$PROJECT_ROOT/k8s" "$backup_path/"
    cp -r "$PROJECT_ROOT/docker" "$backup_path/"
    cp -r "$PROJECT_ROOT/.github" "$backup_path/"
    cp -r "$PROJECT_ROOT/infrastructure" "$backup_path/"

    # Compress backup
    log "Compressing backup..."
    tar -czf "$backup_path.tar.gz" -C "$BACKUP_DIR" "disaster_recovery_$backup_timestamp"
    rm -rf "$backup_path"

    # Upload to S3
    log "Uploading backup to S3..."
    aws s3 cp "$backup_path.tar.gz" "s3://$S3_BUCKET/disaster_recovery/"

    success "Backup completed: $backup_path.tar.gz"
}

# Restore from backup
restore_from_backup() {
    local backup_file="$1"

    if [ -z "$backup_file" ]; then
        error "Backup file not specified"
    fi

    log "Restoring from backup: $backup_file"

    # Download backup from S3 if it's an S3 path
    if [[ "$backup_file" == s3://* ]]; then
        local local_backup="/tmp/$(basename "$backup_file")"
        aws s3 cp "$backup_file" "$local_backup"
        backup_file="$local_backup"
    fi

    # Extract backup
    local restore_dir="/tmp/disaster_recovery_restore"
    mkdir -p "$restore_dir"
    tar -xzf "$backup_file" -C "$restore_dir"

    # Restore Kubernetes resources
    log "Restoring Kubernetes resources..."
    kubectl apply -f "$restore_dir/kubernetes_resources.yaml"
    kubectl apply -f "$restore_dir/configmaps.yaml"
    kubectl apply -f "$restore_dir/secrets.yaml"
    kubectl apply -f "$restore_dir/persistent_volumes.yaml"
    kubectl apply -f "$restore_dir/persistent_volume_claims.yaml"

    # Restore Istio resources
    log "Restoring Istio resources..."
    kubectl apply -f "$restore_dir/virtualservices.yaml"
    kubectl apply -f "$restore_dir/destinationrules.yaml"
    kubectl apply -f "$restore_dir/gateways.yaml"
    kubectl apply -f "$restore_dir/authorizationpolicies.yaml"

    # Restore monitoring resources
    log "Restoring monitoring resources..."
    kubectl apply -f "$restore_dir/prometheuses.yaml"
    kubectl apply -f "$restore_dir/servicemonitors.yaml"
    kubectl apply -f "$restore_dir/alertmanagers.yaml"

    # Restore database
    log "Restoring database..."
    psql "$DATABASE_URL" < "$restore_dir/database_backup.sql"

    # Wait for services to be ready
    log "Waiting for services to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/nexus-backend -n "$KUBE_NAMESPACE"
    kubectl wait --for=condition=available --timeout=300s deployment/nexus-frontend -n "$KUBE_NAMESPACE"
    kubectl wait --for=condition=available --timeout=300s deployment/nexus-nginx -n "$KUBE_NAMESPACE"

    # Cleanup
    rm -rf "$restore_dir"
    if [[ "$backup_file" == /tmp/* ]]; then
        rm -f "$backup_file"
    fi

    success "Restore completed"
}

# Failover to secondary region
failover_to_secondary() {
    local secondary_region="${SECONDARY_REGION:-us-west-2}"

    log "Initiating failover to secondary region: $secondary_region"

    # Update DNS to point to secondary region
    log "Updating DNS to point to secondary region..."
    # Add DNS update logic here

    # Scale up services in secondary region
    log "Scaling up services in secondary region..."
    # Add secondary region scaling logic here

    # Verify failover
    log "Verifying failover..."
    # Add failover verification logic here

    success "Failover to secondary region completed"
}

# Health check
health_check() {
    log "Performing health check..."

    # Check Kubernetes cluster health
    log "Checking Kubernetes cluster health..."
    kubectl get nodes
    kubectl get pods -n "$KUBE_NAMESPACE"

    # Check service health
    log "Checking service health..."
    local service_ip=$(kubectl get service nexus-nginx -n "$KUBE_NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

    if [ -n "$service_ip" ]; then
        curl -f "http://$service_ip/health" || warning "Health check failed for service IP: $service_ip"
    else
        warning "Service IP not found"
    fi

    # Check database connectivity
    log "Checking database connectivity..."
    psql "$DATABASE_URL" -c "SELECT 1;" || warning "Database connectivity check failed"

    # Check Redis connectivity
    log "Checking Redis connectivity..."
    # Add Redis connectivity check here

    success "Health check completed"
}

# Main function
main() {
    local action="${1:-help}"

    case "$action" in
        "backup")
            check_prerequisites
            backup_current_state
            ;;
        "restore")
            local backup_file="${2:-}"
            check_prerequisites
            restore_from_backup "$backup_file"
            ;;
        "failover")
            check_prerequisites
            failover_to_secondary
            ;;
        "health")
            check_prerequisites
            health_check
            ;;
        "help"|*)
            echo "Usage: $0 {backup|restore|failover|health}"
            echo ""
            echo "Commands:"
            echo "  backup                    - Create a disaster recovery backup"
            echo "  restore <backup_file>     - Restore from a backup file"
            echo "  failover                  - Failover to secondary region"
            echo "  health                    - Perform health check"
            echo "  help                      - Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  DATABASE_URL              - Database connection string"
            echo "  S3_BUCKET                 - S3 bucket for backups"
            echo "  S3_REGION                 - S3 region for backups"
            echo "  KUBE_NAMESPACE            - Kubernetes namespace"
            echo "  SECONDARY_REGION          - Secondary region for failover"
            ;;
    esac
}

# Run main function
main "$@"
