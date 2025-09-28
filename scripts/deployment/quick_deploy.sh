#!/bin/bash

# NEXUS Platform Quick Deploy Script
# This script provides an interactive deployment experience

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

info() {
    echo -e "${PURPLE}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ️${NC} $1"
}

# Banner
show_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    NEXUS PLATFORM                           ║"
    echo "║                Quick Deployment Script                      ║"
    echo "║                                                              ║"
    echo "║  🚀 Production-Ready Financial Management Platform         ║"
    echo "║  📊 Advanced Monitoring & Analytics                         ║"
    echo "║  🔒 Enterprise Security & Compliance                        ║"
    echo "║  ⚡ Auto-scaling & High Availability                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    local errors=0

    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        ((errors++))
    else
        success "Docker is installed"
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        ((errors++))
    else
        success "Docker Compose is installed"
    fi

    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        ((errors++))
    else
        success "Docker daemon is running"
    fi

    if [ $errors -gt 0 ]; then
        error "Please install the missing prerequisites first"
        exit 1
    fi
}

# Show deployment options
show_options() {
    echo ""
    info "Choose your deployment method:"
    echo ""
    echo "1. 🐳 Docker Compose (Recommended for development/small production)"
    echo "   - Quick setup"
    echo "   - Single server deployment"
    echo "   - Easy to manage"
    echo ""
    echo "2. ☸️  Kubernetes (Recommended for enterprise production)"
    echo "   - Scalable deployment"
    echo "   - High availability"
    echo "   - Enterprise features"
    echo ""
    echo "3. 🔍 Check Prerequisites Only"
    echo ""
    echo "4. ❌ Exit"
    echo ""
}

# Deploy with Docker Compose
deploy_docker_compose() {
    log "Deploying with Docker Compose..."

    # Check if env.production exists
    if [ ! -f "env.production" ]; then
        warning "env.production not found. Creating from template..."
        cp env.production env.production
    fi

    # Make deployment script executable
    chmod +x scripts/deploy_production.sh

    # Run deployment
    ./scripts/deploy_production.sh

    success "Docker Compose deployment completed!"

    echo ""
    info "Access your NEXUS Platform:"
    echo "  🌐 Frontend: https://nexus.local"
    echo "  🔌 API: https://api.nexus.local"
    echo "  📊 Monitoring: https://monitoring.nexus.local"
    echo ""
    echo "To view logs: docker-compose -f docker-compose.production.yml logs -f"
    echo "To stop: docker-compose -f docker-compose.production.yml down"
}

# Deploy with Kubernetes
deploy_kubernetes() {
    log "Deploying with Kubernetes..."

    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed. Please install kubectl first."
        return 1
    fi

    # Check if helm is available
    if ! command -v helm &> /dev/null; then
        error "Helm is not installed. Please install Helm first."
        return 1
    fi

    # Check if kubectl can connect to cluster
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        return 1
    fi

    # Make deployment script executable
    chmod +x scripts/deploy_kubernetes.sh

    # Run deployment
    ./scripts/deploy_kubernetes.sh

    success "Kubernetes deployment completed!"

    echo ""
    info "Access your NEXUS Platform:"
    echo "  🌐 Frontend: https://nexus.local"
    echo "  🔌 API: https://api.nexus.local"
    echo "  📊 Monitoring: https://monitoring.nexus.local"
    echo ""
    echo "To view logs: kubectl logs -f deployment/nexus-backend -n nexus"
    echo "To check status: kubectl get pods -n nexus"
}

# Check prerequisites only
check_prerequisites_only() {
    log "Running comprehensive prerequisites check..."

    chmod +x scripts/check_prerequisites.sh
    ./scripts/check_prerequisites.sh
}

# Main menu
main_menu() {
    while true; do
        show_options
        read -p "Enter your choice (1-4): " choice

        case $choice in
            1)
                check_prerequisites
                deploy_docker_compose
                break
                ;;
            2)
                check_prerequisites
                deploy_kubernetes
                break
                ;;
            3)
                check_prerequisites_only
                ;;
            4)
                log "Exiting..."
                exit 0
                ;;
            *)
                warning "Invalid choice. Please enter 1-4."
                ;;
        esac
    done
}

# Main function
main() {
    show_banner

    # Check if we're in the right directory
    if [ ! -f "docker-compose.production.yml" ]; then
        error "Please run this script from the NEXUS Platform root directory"
        exit 1
    fi

    main_menu
}

# Run main function
main "$@"
