#!/bin/bash

# NEXUS Platform - Deployment Management Script
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_NAME="nexus-platform"
ENVIRONMENT=${2:-development}

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Show usage
show_usage() {
    echo "NEXUS Platform - Deployment Management"
    echo "Usage: $0 <command> [environment]"
    echo ""
    echo "Commands:"
    echo "  start     - Start all services"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  status    - Show service status"
    echo "  logs      - Show service logs"
    echo "  build     - Build all images"
    echo "  clean     - Clean up containers and images"
    echo "  deploy    - Full deployment"
    echo "  scale     - Scale services"
    echo ""
    echo "Environments:"
    echo "  development (default)"
    echo "  production"
    echo ""
    echo "Examples:"
    echo "  $0 start development"
    echo "  $0 deploy production"
    echo "  $0 scale backend=3"
}

# Start services
start_services() {
    log "Starting NEXUS Platform services..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    elif [ "$ENVIRONMENT" = "development" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    else
        docker-compose up -d
    fi
    
    success "Services started"
}

# Stop services
stop_services() {
    log "Stopping NEXUS Platform services..."
    docker-compose down
    success "Services stopped"
}

# Restart services
restart_services() {
    log "Restarting NEXUS Platform services..."
    stop_services
    start_services
}

# Show status
show_status() {
    log "NEXUS Platform Service Status:"
    echo ""
    docker-compose ps
    echo ""
    
    # Check health endpoints
    log "Health Checks:"
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Backend API: http://localhost:8000"
    else
        error "Backend API: Not responding"
    fi
    
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        success "Frontend: http://localhost:3000"
    else
        error "Frontend: Not responding"
    fi
    
    if curl -f http://localhost:9090 > /dev/null 2>&1; then
        success "Prometheus: http://localhost:9090"
    else
        warning "Prometheus: Not responding"
    fi
    
    if curl -f http://localhost:3001 > /dev/null 2>&1; then
        success "Grafana: http://localhost:3001"
    else
        warning "Grafana: Not responding"
    fi
}

# Show logs
show_logs() {
    SERVICE=${3:-""}
    if [ -n "$SERVICE" ]; then
        docker-compose logs -f "$SERVICE"
    else
        docker-compose logs -f
    fi
}

# Build images
build_images() {
    log "Building NEXUS Platform images..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
    else
        docker-compose build --no-cache
    fi
    
    success "Images built"
}

# Clean up
clean_up() {
    log "Cleaning up NEXUS Platform..."
    
    # Stop and remove containers
    docker-compose down --volumes --remove-orphans
    
    # Remove images
    docker rmi $(docker images "nexus-platform*" -q) 2>/dev/null || true
    
    # Remove unused volumes
    docker volume prune -f
    
    # Remove unused networks
    docker network prune -f
    
    success "Cleanup completed"
}

# Full deployment
deploy() {
    log "Starting full NEXUS Platform deployment..."
    
    # Run validation first
    log "Running validation..."
    python3 scripts/frenly_validation_master.py
    
    if [ $? -ne 0 ]; then
        error "Validation failed. Deployment aborted."
        exit 1
    fi
    
    # Build and start
    build_images
    start_services
    
    # Wait for services
    log "Waiting for services to be ready..."
    sleep 30
    
    # Run health checks
    show_status
    
    success "Deployment completed!"
}

# Scale services
scale_services() {
    SERVICE_SCALE=${3:-""}
    if [ -z "$SERVICE_SCALE" ]; then
        error "Please specify service and scale (e.g., backend=3)"
        exit 1
    fi
    
    log "Scaling services: $SERVICE_SCALE"
    docker-compose up -d --scale "$SERVICE_SCALE"
    success "Services scaled"
}

# Main command handler
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$@"
        ;;
    build)
        build_images
        ;;
    clean)
        clean_up
        ;;
    deploy)
        deploy
        ;;
    scale)
        scale_services "$@"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
