#!/bin/bash
# NEXUS Platform Backup Script
# This script handles automated backups of the NEXUS Platform

set -euo pipefail

# Configuration
BACKUP_DIR="/backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="/var/log/backup.log"

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

    # Check if pg_dump is available
    if ! command -v pg_dump >/dev/null 2>&1; then
        error_exit "pg_dump command not found. Please install PostgreSQL client tools."
    fi

    # Check if kubectl can connect to cluster
    if ! kubectl cluster-info >/dev/null 2>&1; then
        error_exit "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    fi

    # Create backup directory
    mkdir -p "$BACKUP_DIR"/{database,kubernetes,application,config}

    success "Prerequisites check completed"
}

# Backup database
backup_database() {
    log "Starting database backup..."

    local db_backup_dir="$BACKUP_DIR/database"
    local backup_file="nexus_db_backup_${TIMESTAMP}.sql.gz"

    # Get database connection details
    local db_host=$(kubectl get service postgres-service -n nexus-platform -o jsonpath='{.spec.clusterIP}')
    local db_port=$(kubectl get service postgres-service -n nexus-platform -o jsonpath='{.spec.ports[0].port}')
    local db_name="nexus"
    local db_user="nexus"

    # Get database password from secret
    local db_password=$(kubectl get secret nexus-secrets -n nexus-platform -o jsonpath='{.data.database-password}' | base64 -d)

    # Set PGPASSWORD environment variable
    export PGPASSWORD="$db_password"

    # Create database backup
    if pg_dump -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" \
        --verbose --no-password --format=plain --no-owner --no-privileges \
        | gzip > "$db_backup_dir/$backup_file" 2>> "$LOG_FILE"; then
        success "Database backup created: $backup_file"
    else
        error_exit "Failed to create database backup"
    fi

    # Verify backup integrity
    if gzip -t "$db_backup_dir/$backup_file"; then
        success "Database backup integrity verified"
    else
        error_exit "Database backup integrity check failed"
    fi

    # Get backup size
    local backup_size=$(du -h "$db_backup_dir/$backup_file" | cut -f1)
    log "Database backup size: $backup_size"
}

# Backup Kubernetes resources
backup_kubernetes() {
    log "Starting Kubernetes resources backup..."

    local k8s_backup_dir="$BACKUP_DIR/kubernetes"
    local backup_file="nexus_k8s_backup_${TIMESTAMP}.tar.gz"

    # Backup namespaces
    local namespaces=("nexus-platform" "monitoring")

    for namespace in "${namespaces[@]}"; do
        log "Backing up namespace: $namespace"

        # Create namespace directory
        mkdir -p "$k8s_backup_dir/$namespace"

        # Backup all resource types
        local resource_types=(
            "deployments"
            "services"
            "configmaps"
            "secrets"
            "persistentvolumeclaims"
            "networkpolicies"
            "rolebindings"
            "roles"
            "serviceaccounts"
            "horizontalpodautoscalers"
            "poddisruptionbudgets"
            "resourcequotas"
            "limitranges"
        )

        for resource_type in "${resource_types[@]}"; do
            if kubectl get "$resource_type" -n "$namespace" >/dev/null 2>&1; then
                kubectl get "$resource_type" -n "$namespace" -o yaml > "$k8s_backup_dir/$namespace/${resource_type}.yaml" 2>> "$LOG_FILE" || {
                    warning "Failed to backup $resource_type in namespace $namespace"
                }
            fi
        done
    done

    # Backup cluster-wide resources
    log "Backing up cluster-wide resources..."
    mkdir -p "$k8s_backup_dir/cluster"

    local cluster_resource_types=(
        "nodes"
        "persistentvolumes"
        "storageclasses"
        "clusterroles"
        "clusterrolebindings"
        "customresourcedefinitions"
    )

    for resource_type in "${cluster_resource_types[@]}"; do
        if kubectl get "$resource_type" >/dev/null 2>&1; then
            kubectl get "$resource_type" -o yaml > "$k8s_backup_dir/cluster/${resource_type}.yaml" 2>> "$LOG_FILE" || {
                warning "Failed to backup cluster resource $resource_type"
            }
        fi
    done

    # Create compressed archive
    if tar -czf "$k8s_backup_dir/$backup_file" -C "$k8s_backup_dir" . 2>> "$LOG_FILE"; then
        success "Kubernetes backup created: $backup_file"
    else
        error_exit "Failed to create Kubernetes backup archive"
    fi

    # Verify backup integrity
    if tar -tzf "$k8s_backup_dir/$backup_file" >/dev/null 2>&1; then
        success "Kubernetes backup integrity verified"
    else
        error_exit "Kubernetes backup integrity check failed"
    fi

    # Get backup size
    local backup_size=$(du -h "$k8s_backup_dir/$backup_file" | cut -f1)
    log "Kubernetes backup size: $backup_size"
}

# Backup application code
backup_application() {
    log "Starting application code backup..."

    local app_backup_dir="$BACKUP_DIR/application"
    local backup_file="nexus_app_backup_${TIMESTAMP}.tar.gz"

    # Create application backup
    if tar -czf "$app_backup_dir/$backup_file" \
        --exclude='node_modules' \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.env' \
        --exclude='*.log' \
        . 2>> "$LOG_FILE"; then
        success "Application backup created: $backup_file"
    else
        error_exit "Failed to create application backup"
    fi

    # Verify backup integrity
    if tar -tzf "$app_backup_dir/$backup_file" >/dev/null 2>&1; then
        success "Application backup integrity verified"
    else
        error_exit "Application backup integrity check failed"
    fi

    # Get backup size
    local backup_size=$(du -h "$app_backup_dir/$backup_file" | cut -f1)
    log "Application backup size: $backup_size"
}

# Backup configuration
backup_config() {
    log "Starting configuration backup..."

    local config_backup_dir="$BACKUP_DIR/config"
    local backup_file="nexus_config_backup_${TIMESTAMP}.tar.gz"

    # Create configuration backup
    if tar -czf "$config_backup_dir/$backup_file" \
        config/ \
        infrastructure/ \
        .github/ \
        *.yaml \
        *.yml \
        *.json \
        2>> "$LOG_FILE"; then
        success "Configuration backup created: $backup_file"
    else
        error_exit "Failed to create configuration backup"
    fi

    # Verify backup integrity
    if tar -tzf "$config_backup_dir/$backup_file" >/dev/null 2>&1; then
        success "Configuration backup integrity verified"
    else
        error_exit "Configuration backup integrity check failed"
    fi

    # Get backup size
    local backup_size=$(du -h "$config_backup_dir/$backup_file" | cut -f1)
    log "Configuration backup size: $backup_size"
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up old backups (older than $RETENTION_DAYS days)..."

    # Cleanup database backups
    find "$BACKUP_DIR/database" -name "nexus_db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

    # Cleanup Kubernetes backups
    find "$BACKUP_DIR/kubernetes" -name "nexus_k8s_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

    # Cleanup application backups
    find "$BACKUP_DIR/application" -name "nexus_app_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

    # Cleanup configuration backups
    find "$BACKUP_DIR/config" -name "nexus_config_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

    success "Old backups cleaned up"
}

# Upload backups to cloud storage
upload_to_cloud() {
    if [ "${UPLOAD_TO_CLOUD:-false}" = "true" ]; then
        log "Uploading backups to cloud storage..."

        # Upload to AWS S3
        if command -v aws >/dev/null 2>&1 && [ -n "${S3_BUCKET:-}" ]; then
            # Upload database backup
            if aws s3 cp "$BACKUP_DIR/database/nexus_db_backup_${TIMESTAMP}.sql.gz" "s3://${S3_BUCKET}/database-backups/" 2>> "$LOG_FILE"; then
                success "Database backup uploaded to S3"
            else
                warning "Failed to upload database backup to S3"
            fi

            # Upload Kubernetes backup
            if aws s3 cp "$BACKUP_DIR/kubernetes/nexus_k8s_backup_${TIMESTAMP}.tar.gz" "s3://${S3_BUCKET}/kubernetes-backups/" 2>> "$LOG_FILE"; then
                success "Kubernetes backup uploaded to S3"
            else
                warning "Failed to upload Kubernetes backup to S3"
            fi

            # Upload application backup
            if aws s3 cp "$BACKUP_DIR/application/nexus_app_backup_${TIMESTAMP}.tar.gz" "s3://${S3_BUCKET}/application-backups/" 2>> "$LOG_FILE"; then
                success "Application backup uploaded to S3"
            else
                warning "Failed to upload application backup to S3"
            fi

            # Upload configuration backup
            if aws s3 cp "$BACKUP_DIR/config/nexus_config_backup_${TIMESTAMP}.tar.gz" "s3://${S3_BUCKET}/config-backups/" 2>> "$LOG_FILE"; then
                success "Configuration backup uploaded to S3"
            else
                warning "Failed to upload configuration backup to S3"
            fi
        else
            warning "AWS CLI not found or S3_BUCKET not set, skipping cloud upload"
        fi
    fi
}

# Send notification
send_notification() {
    local status="$1"
    local message="$2"

    if [ "${SEND_NOTIFICATIONS:-false}" = "true" ]; then
        # Send to Slack
        if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
            curl -X POST -H 'Content-type: application/json' \
                --data "{\"text\":\"NEXUS Platform Backup $status: $message\"}" \
                "$SLACK_WEBHOOK_URL" 2>/dev/null || true
        fi

        # Send email
        if command -v mail >/dev/null 2>&1 && [ -n "${NOTIFICATION_EMAIL:-}" ]; then
            echo "$message" | mail -s "NEXUS Platform Backup $status" "$NOTIFICATION_EMAIL" 2>/dev/null || true
        fi
    fi
}

# Generate backup report
generate_report() {
    log "Generating backup report..."

    local report_file="$BACKUP_DIR/backup_report_${TIMESTAMP}.txt"

    {
        echo "NEXUS Platform Backup Report"
        echo "=========================="
        echo "Timestamp: $(date)"
        echo "Backup ID: $TIMESTAMP"
        echo ""
        echo "Database Backup:"
        echo "  File: nexus_db_backup_${TIMESTAMP}.sql.gz"
        echo "  Size: $(du -h "$BACKUP_DIR/database/nexus_db_backup_${TIMESTAMP}.sql.gz" 2>/dev/null | cut -f1 || echo "N/A")"
        echo ""
        echo "Kubernetes Backup:"
        echo "  File: nexus_k8s_backup_${TIMESTAMP}.tar.gz"
        echo "  Size: $(du -h "$BACKUP_DIR/kubernetes/nexus_k8s_backup_${TIMESTAMP}.tar.gz" 2>/dev/null | cut -f1 || echo "N/A")"
        echo ""
        echo "Application Backup:"
        echo "  File: nexus_app_backup_${TIMESTAMP}.tar.gz"
        echo "  Size: $(du -h "$BACKUP_DIR/application/nexus_app_backup_${TIMESTAMP}.tar.gz" 2>/dev/null | cut -f1 || echo "N/A")"
        echo ""
        echo "Configuration Backup:"
        echo "  File: nexus_config_backup_${TIMESTAMP}.tar.gz"
        echo "  Size: $(du -h "$BACKUP_DIR/config/nexus_config_backup_${TIMESTAMP}.tar.gz" 2>/dev/null | cut -f1 || echo "N/A")"
        echo ""
        echo "Total Backup Size:"
        echo "  $(du -sh "$BACKUP_DIR" | cut -f1)"
        echo ""
        echo "Backup Status: SUCCESS"
    } > "$report_file"

    success "Backup report generated: $report_file"
}

# Main backup function
backup() {
    log "Starting NEXUS Platform backup process..."

    # Check prerequisites
    check_prerequisites

    # Backup database
    backup_database

    # Backup Kubernetes resources
    backup_kubernetes

    # Backup application code
    backup_application

    # Backup configuration
    backup_config

    # Cleanup old backups
    cleanup_old_backups

    # Upload to cloud (optional)
    upload_to_cloud

    # Generate report
    generate_report

    # Send success notification
    send_notification "SUCCESS" "Backup completed successfully at $(date)"

    success "NEXUS Platform backup process completed successfully!"
}

# Restore function
restore() {
    local backup_type="$1"
    local backup_file="$2"

    log "Starting restore process for $backup_type from $backup_file..."

    case "$backup_type" in
        database)
            if [ ! -f "$BACKUP_DIR/database/$backup_file" ]; then
                error_exit "Database backup file not found: $backup_file"
            fi

            # Stop application services
            kubectl scale deployment backend-deployment --replicas=0 -n nexus-platform

            # Restore database
            gunzip -c "$BACKUP_DIR/database/$backup_file" | kubectl exec -i postgres-0 -n nexus-platform -- psql -U nexus -d nexus

            # Restart application services
            kubectl scale deployment backend-deployment --replicas=3 -n nexus-platform

            success "Database restored from: $backup_file"
            ;;
        kubernetes)
            if [ ! -f "$BACKUP_DIR/kubernetes/$backup_file" ]; then
                error_exit "Kubernetes backup file not found: $backup_file"
            fi

            # Extract backup
            tar -xzf "$BACKUP_DIR/kubernetes/$backup_file" -C /tmp/

            # Restore resources
            kubectl apply -f /tmp/nexus-platform/ -n nexus-platform
            kubectl apply -f /tmp/monitoring/ -n monitoring

            success "Kubernetes resources restored from: $backup_file"
            ;;
        application)
            if [ ! -f "$BACKUP_DIR/application/$backup_file" ]; then
                error_exit "Application backup file not found: $backup_file"
            fi

            # Extract backup
            tar -xzf "$BACKUP_DIR/application/$backup_file" -C /tmp/

            success "Application code restored from: $backup_file"
            ;;
        config)
            if [ ! -f "$BACKUP_DIR/config/$backup_file" ]; then
                error_exit "Configuration backup file not found: $backup_file"
            fi

            # Extract backup
            tar -xzf "$BACKUP_DIR/config/$backup_file" -C /tmp/

            success "Configuration restored from: $backup_file"
            ;;
        *)
            error_exit "Invalid backup type: $backup_type"
            ;;
    esac
}

# List available backups
list_backups() {
    log "Listing available backups..."

    echo "=== Database Backups ==="
    ls -la "$BACKUP_DIR/database/nexus_db_backup_*.sql.gz" 2>/dev/null || echo "No database backups found"
    echo ""

    echo "=== Kubernetes Backups ==="
    ls -la "$BACKUP_DIR/kubernetes/nexus_k8s_backup_*.tar.gz" 2>/dev/null || echo "No Kubernetes backups found"
    echo ""

    echo "=== Application Backups ==="
    ls -la "$BACKUP_DIR/application/nexus_app_backup_*.tar.gz" 2>/dev/null || echo "No application backups found"
    echo ""

    echo "=== Configuration Backups ==="
    ls -la "$BACKUP_DIR/config/nexus_config_backup_*.tar.gz" 2>/dev/null || echo "No configuration backups found"
    echo ""
}

# Show usage
usage() {
    echo "Usage: $0 [backup|restore|list] [options]"
    echo ""
    echo "Commands:"
    echo "  backup                    - Create full backup of NEXUS Platform"
    echo "  restore <type> <file>     - Restore from backup"
    echo "  list                      - List available backups"
    echo ""
    echo "Restore Types:"
    echo "  database                  - Restore database from backup"
    echo "  kubernetes               - Restore Kubernetes resources"
    echo "  application              - Restore application code"
    echo "  config                   - Restore configuration"
    echo ""
    echo "Environment Variables:"
    echo "  BACKUP_DIR               - Backup directory (default: /backups)"
    echo "  RETENTION_DAYS           - Backup retention days (default: 30)"
    echo "  UPLOAD_TO_CLOUD          - Upload to cloud storage (default: false)"
    echo "  S3_BUCKET                - S3 bucket for cloud storage"
    echo "  SEND_NOTIFICATIONS       - Send notifications (default: false)"
    echo "  SLACK_WEBHOOK_URL        - Slack webhook URL"
    echo "  NOTIFICATION_EMAIL       - Email for notifications"
}

# Main script logic
case "${1:-backup}" in
    backup)
        backup
        ;;
    restore)
        if [ $# -lt 3 ]; then
            error_exit "Usage: $0 restore <type> <file>"
        fi
        restore "$2" "$3"
        ;;
    list)
        list_backups
        ;;
    *)
        usage
        exit 1
        ;;
esac
