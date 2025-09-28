#!/bin/bash

# NEXUS Production Environment Deployment Script
# This script deploys the NEXUS platform to the production environment

set -e

# Configuration
ENVIRONMENT="production"
DOCKER_COMPOSE_FILE="docker-compose.yml"
NAMESPACE="nexus-prod"
KUBERNETES_MANIFESTS="k8s/unified-manifests.yaml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi

    # Check if kubectl is available
    if ! command -v kubectl > /dev/null 2>&1; then
        print_error "kubectl is not installed. Kubernetes deployment requires kubectl."
        exit 1
    fi

    # Check if we have access to the production cluster
    if ! kubectl cluster-info > /dev/null 2>&1; then
        print_error "Cannot access Kubernetes cluster. Please check your kubeconfig and cluster access."
        exit 1
    fi

    print_success "Prerequisites check completed"
}

# Function to build and push Docker images
build_and_push_images() {
    print_info "Building and pushing Docker images for $ENVIRONMENT environment..."

    # Set Docker registry (replace with your actual registry)
    DOCKER_REGISTRY="${DOCKER_REGISTRY:-your-registry.com/nexus}"

    # Build and tag images
    print_info "Building backend image..."
    docker build -f docker/backend/Dockerfile.production -t $DOCKER_REGISTRY/backend:latest -t $DOCKER_REGISTRY/backend:$(date +%Y%m%d-%H%M%S) .

    print_info "Building frontend image..."
    docker build -f docker/frontend/Dockerfile.production -t $DOCKER_REGISTRY/frontend:latest -t $DOCKER_REGISTRY/frontend:$(date +%Y%m%d-%H%M%S) .

    # Push images to registry
    print_info "Pushing images to registry..."
    docker push $DOCKER_REGISTRY/backend:latest
    docker push $DOCKER_REGISTRY/backend:$(date +%Y%m%d-%H%M%S)
    docker push $DOCKER_REGISTRY/frontend:latest
    docker push $DOCKER_REGISTRY/frontend:$(date +%Y%m%d-%H%M%S)

    print_success "Docker images built and pushed successfully"
}

# Function to deploy to Kubernetes
deploy_kubernetes() {
    print_info "Deploying to Kubernetes production environment..."

    # Create namespace if it doesn't exist
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

    # Apply Kubernetes manifests
    kubectl apply -f $KUBERNETES_MANIFESTS -n $NAMESPACE

    # Wait for deployments to be ready
    print_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=600s deployment --all -n $NAMESPACE

    print_success "Kubernetes deployment completed"
}

# Function to run database migrations
run_migrations() {
    print_info "Running database migrations..."

    # Get the migration job pod name
    MIGRATION_POD=$(kubectl get pods -n $NAMESPACE -l job-name=nexus-migration -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

    if [ -n "$MIGRATION_POD" ]; then
        print_info "Migration job already exists. Checking status..."
        kubectl wait --for=condition=complete --timeout=300s job/nexus-migration -n $NAMESPACE
    else
        print_info "Creating migration job..."
        kubectl create job nexus-migration --from=cronjob/nexus-migration -n $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
        kubectl wait --for=condition=complete --timeout=300s job/nexus-migration -n $NAMESPACE
    fi

    print_success "Database migrations completed"
}

# Function to run security checks
run_security_checks() {
    print_info "Running security checks..."

    # Run security scan on images
    ./scripts/docker-security-scan.sh

    # Check for security vulnerabilities in Kubernetes manifests
    if command -v kube-bench > /dev/null 2>&1; then
        print_info "Running Kubernetes security benchmark..."
        kube-bench run --targets=master,node --json > security-reports/kube-bench-$(date +%Y%m%d-%H%M%S).json
    fi

    print_success "Security checks completed"
}

# Function to run health checks
run_health_checks() {
    print_info "Running health checks..."

    # Get the ingress host
    INGRESS_HOST=$(kubectl get ingress nexus-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}')

    if [ -n "$INGRESS_HOST" ]; then
        print_info "Checking application health at https://$INGRESS_HOST"

        # Wait for ingress to be ready
        kubectl wait --for=condition=ready --timeout=300s ingress/nexus-ingress -n $NAMESPACE

        # Perform health check
        if curl -f -k https://$INGRESS_HOST/health > /dev/null 2>&1; then
            print_success "Application health check passed"
        else
            print_error "Application health check failed"
            exit 1
        fi
    else
        print_warning "Ingress host not found. Skipping health checks."
    fi

    print_success "Health checks completed"
}

# Function to display deployment summary
display_summary() {
    print_success "Production environment deployment completed!"
    echo ""
    echo "Production environment deployed:"
    echo "  - Environment: $ENVIRONMENT"
    echo "  - Kubernetes Namespace: $NAMESPACE"
    echo "  - Application URL: https://api.nexus.com"
    echo "  - Frontend URL: https://nexus.com"
    echo ""
    echo "To check deployment status:"
    echo "  kubectl get all -n $NAMESPACE"
    echo ""
    echo "To view logs:"
    echo "  kubectl logs -f deployment/nexus-backend -n $NAMESPACE"
    echo ""
    echo "To check pod status:"
    echo "  kubectl get pods -n $NAMESPACE"
    echo ""
    echo "Security reports available in: security-reports/"
}

# Function to create backup before deployment
create_backup() {
    print_info "Creating pre-deployment backup..."

    # Create backup using existing backup script
    if [ -f "scripts/backup_system.py" ]; then
        python scripts/backup_system.py --environment production --pre-deployment
    fi

    print_success "Pre-deployment backup created"
}

# Main deployment function
main() {
    print_info "Starting NEXUS production environment deployment..."

    # Confirm deployment
    read -p "Are you sure you want to deploy to PRODUCTION? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_error "Deployment cancelled by user"
        exit 1
    fi

    check_prerequisites
    create_backup
    build_and_push_images
    deploy_kubernetes
    run_migrations
    run_security_checks
    run_health_checks
    display_summary

    print_success "Production environment deployment completed successfully!"
}

# Run main function with all arguments
main "$@"
