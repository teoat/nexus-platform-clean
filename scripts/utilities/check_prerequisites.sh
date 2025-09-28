#!/bin/bash

# NEXUS Platform Prerequisites Check Script
# This script checks if all required tools are installed and configured

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker
check_docker() {
    log "Checking Docker installation..."
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        success "Docker is installed: $DOCKER_VERSION"
        
        # Check if Docker daemon is running
        if docker info >/dev/null 2>&1; then
            success "Docker daemon is running"
        else
            error "Docker daemon is not running. Please start Docker."
            return 1
        fi
    else
        error "Docker is not installed. Please install Docker first."
        return 1
    fi
}

# Check Docker Compose
check_docker_compose() {
    log "Checking Docker Compose installation..."
    if command_exists docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        success "Docker Compose is installed: $COMPOSE_VERSION"
    else
        error "Docker Compose is not installed. Please install Docker Compose first."
        return 1
    fi
}

# Check Kubernetes (optional)
check_kubernetes() {
    log "Checking Kubernetes installation..."
    if command_exists kubectl; then
        KUBECTL_VERSION=$(kubectl version --client --short 2>/dev/null | cut -d' ' -f3)
        success "kubectl is installed: $KUBECTL_VERSION"
        
        # Check if kubectl can connect to cluster
        if kubectl cluster-info >/dev/null 2>&1; then
            success "Kubernetes cluster is accessible"
        else
            warning "Kubernetes cluster is not accessible. You can still use Docker Compose."
        fi
    else
        warning "kubectl is not installed. Kubernetes deployment will not be available."
    fi
}

# Check Helm (optional)
check_helm() {
    log "Checking Helm installation..."
    if command_exists helm; then
        HELM_VERSION=$(helm version --short | cut -d' ' -f1)
        success "Helm is installed: $HELM_VERSION"
    else
        warning "Helm is not installed. Kubernetes deployment with Helm will not be available."
    fi
}

# Check OpenSSL
check_openssl() {
    log "Checking OpenSSL installation..."
    if command_exists openssl; then
        OPENSSL_VERSION=$(openssl version | cut -d' ' -f2)
        success "OpenSSL is installed: $OPENSSL_VERSION"
    else
        error "OpenSSL is not installed. Please install OpenSSL first."
        return 1
    fi
}

# Check curl
check_curl() {
    log "Checking curl installation..."
    if command_exists curl; then
        success "curl is installed"
    else
        error "curl is not installed. Please install curl first."
        return 1
    fi
}

# Check system resources
check_system_resources() {
    log "Checking system resources..."
    
    # Check available memory
    if command_exists free; then
        MEMORY_GB=$(free -g | awk 'NR==2{print $2}')
        if [ "$MEMORY_GB" -ge 8 ]; then
            success "Memory: ${MEMORY_GB}GB (recommended: 8GB+)"
        else
            warning "Memory: ${MEMORY_GB}GB (recommended: 8GB+)"
        fi
    fi
    
    # Check available disk space
    if command_exists df; then
        DISK_GB=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
        if [ "$DISK_GB" -ge 50 ]; then
            success "Disk space: ${DISK_GB}GB (recommended: 50GB+)"
        else
            warning "Disk space: ${DISK_GB}GB (recommended: 50GB+)"
        fi
    fi
}

# Check required files
check_required_files() {
    log "Checking required files..."
    
    REQUIRED_FILES=(
        "docker-compose.production.yml"
        "env.production"
        "nginx/nginx.production.conf"
        "Dockerfile.backend"
        "nexus_frontend/web/Dockerfile.production"
        "scripts/deploy_production.sh"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            success "Found: $file"
        else
            error "Missing: $file"
            return 1
        fi
    done
}

# Check ports
check_ports() {
    log "Checking required ports..."
    
    REQUIRED_PORTS=(80 443 8000 3000 5432 6379 9090 3001 9200 5601 16686)
    
    for port in "${REQUIRED_PORTS[@]}"; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            warning "Port $port is already in use"
        else
            success "Port $port is available"
        fi
    done
}

# Main function
main() {
    log "Starting prerequisites check for NEXUS Platform deployment..."
    
    local errors=0
    
    # Required checks
    check_docker || ((errors++))
    check_docker_compose || ((errors++))
    check_openssl || ((errors++))
    check_curl || ((errors++))
    check_required_files || ((errors++))
    
    # Optional checks
    check_kubernetes
    check_helm
    check_system_resources
    check_ports
    
    echo ""
    if [ $errors -eq 0 ]; then
        success "All required prerequisites are met! You can proceed with deployment."
        echo ""
        echo "Next steps:"
        echo "1. For Docker Compose: ./scripts/deploy_production.sh"
        echo "2. For Kubernetes: ./scripts/deploy_kubernetes.sh"
    else
        error "Some prerequisites are missing. Please install the required tools first."
        exit 1
    fi
}

# Run main function
main "$@"
