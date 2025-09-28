#!/bin/bash

# NEXUS Platform Kubernetes Deployment Script
# Usage: ./k8s-deploy.sh [dev|staging|prod] [apply|delete|status]

set -e

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-dev}
ACTION=${2:-apply}
K8S_DIR="k8s-universal"

# Function to print status messages
print_status() {
    local status_type=$1
    local message=$2
    case "$status_type" in
        "INFO") echo -e "${BLUE}ℹ️  $message${NC}" ;;
        "PASS") echo -e "${GREEN}✅ $message${NC}" ;;
        "FAIL") echo -e "${RED}❌ $message${NC}" ;;
        "WARN") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        *) echo "$message" ;;
    esac
}

# Print header
echo -e "${BLUE}🚀 NEXUS Platform Kubernetes Deployment${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    print_status "FAIL" "Invalid environment: $ENVIRONMENT. Use: dev, staging, or prod"
    exit 1
fi

# Validate action
if [[ ! "$ACTION" =~ ^(apply|delete|status|logs)$ ]]; then
    print_status "FAIL" "Invalid action: $ACTION. Use: apply, delete, status, or logs"
    exit 1
fi

print_status "INFO" "Environment: $ENVIRONMENT"
print_status "INFO" "Action: $ACTION"
print_status "INFO" "K8s Directory: $K8S_DIR"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_status "FAIL" "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if kustomize is available
if ! command -v kustomize &> /dev/null; then
    print_status "WARN" "kustomize is not installed. Using kubectl kustomize instead."
    KUSTOMIZE_CMD="kubectl kustomize"
else
    KUSTOMIZE_CMD="kustomize build"
fi

# Function to apply manifests
apply_manifests() {
    print_status "INFO" "Applying Kubernetes manifests for $ENVIRONMENT environment..."
    
    local overlay_path="$K8S_DIR/overlays/$ENVIRONMENT"
    
    if [ ! -d "$overlay_path" ]; then
        print_status "FAIL" "Overlay directory not found: $overlay_path"
        exit 1
    fi
    
    # Generate manifests
    print_status "INFO" "Generating manifests with kustomize..."
    if $KUSTOMIZE_CMD "$overlay_path" > /tmp/nexus-manifests.yaml; then
        print_status "PASS" "Manifests generated successfully"
    else
        print_status "FAIL" "Failed to generate manifests"
        exit 1
    fi
    
    # Apply manifests
    print_status "INFO" "Applying manifests to Kubernetes cluster..."
    if kubectl apply -f /tmp/nexus-manifests.yaml; then
        print_status "PASS" "Manifests applied successfully"
    else
        print_status "FAIL" "Failed to apply manifests"
        exit 1
    fi
    
    # Wait for deployments
    print_status "INFO" "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment -l app.kubernetes.io/name=nexus-platform -n nexus-platform$([ "$ENVIRONMENT" != "prod" ] && echo "-$ENVIRONMENT" || echo "")
    
    print_status "PASS" "Deployment completed successfully!"
}

# Function to delete manifests
delete_manifests() {
    print_status "INFO" "Deleting Kubernetes manifests for $ENVIRONMENT environment..."
    
    local overlay_path="$K8S_DIR/overlays/$ENVIRONMENT"
    
    if [ ! -d "$overlay_path" ]; then
        print_status "FAIL" "Overlay directory not found: $overlay_path"
        exit 1
    fi
    
    # Generate manifests
    print_status "INFO" "Generating manifests with kustomize..."
    if $KUSTOMIZE_CMD "$overlay_path" > /tmp/nexus-manifests.yaml; then
        print_status "PASS" "Manifests generated successfully"
    else
        print_status "FAIL" "Failed to generate manifests"
        exit 1
    fi
    
    # Delete manifests
    print_status "INFO" "Deleting manifests from Kubernetes cluster..."
    if kubectl delete -f /tmp/nexus-manifests.yaml; then
        print_status "PASS" "Manifests deleted successfully"
    else
        print_status "WARN" "Some resources may not have been deleted (this is normal if they don't exist)"
    fi
    
    print_status "PASS" "Cleanup completed!"
}

# Function to show status
show_status() {
    print_status "INFO" "Showing status for $ENVIRONMENT environment..."
    
    local namespace="nexus-platform$([ "$ENVIRONMENT" != "prod" ] && echo "-$ENVIRONMENT" || echo "")"
    
    echo ""
    print_status "INFO" "Namespace: $namespace"
    echo ""
    
    # Show pods
    print_status "INFO" "Pods:"
    kubectl get pods -n "$namespace" -o wide
    
    echo ""
    print_status "INFO" "Services:"
    kubectl get services -n "$namespace"
    
    echo ""
    print_status "INFO" "Deployments:"
    kubectl get deployments -n "$namespace"
    
    echo ""
    print_status "INFO" "Ingress:"
    kubectl get ingress -n "$namespace"
}

# Function to show logs
show_logs() {
    print_status "INFO" "Showing logs for $ENVIRONMENT environment..."
    
    local namespace="nexus-platform$([ "$ENVIRONMENT" != "prod" ] && echo "-$ENVIRONMENT" || echo "")"
    
    echo ""
    print_status "INFO" "Backend logs:"
    kubectl logs -n "$namespace" -l app=nexus-backend --tail=50
    
    echo ""
    print_status "INFO" "Nginx logs:"
    kubectl logs -n "$namespace" -l app=nexus-nginx --tail=50
}

# Main execution
case "$ACTION" in
    "apply")
        apply_manifests
        ;;
    "delete")
        delete_manifests
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
esac

# Cleanup
rm -f /tmp/nexus-manifests.yaml

echo ""
print_status "PASS" "Operation completed successfully!"
