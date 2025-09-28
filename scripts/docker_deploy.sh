#!/bin/bash

# NEXUS Platform - Docker Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="nexus-platform"
ENVIRONMENT=${1:-production}
LOG_FILE="docker_deploy_$(date +%Y%m%d_%H%M%S).log"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
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

# Check if Docker is running
check_docker() {
    log "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    success "Docker is running"
}

# Check if Docker Compose is available
check_docker_compose() {
    log "Checking Docker Compose..."
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    success "Docker Compose is available"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    mkdir -p logs data/ssl monitoring/grafana/dashboards monitoring/grafana/datasources
    success "Directories created"
}

# Build images
build_images() {
    log "Building Docker images..."
    
    if [ "$ENVIRONMENT" = "development" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml build
    else
        docker-compose build --no-cache
    fi
    
    success "Images built successfully"
}

# Start services
start_services() {
    log "Starting services..."
    
    if [ "$ENVIRONMENT" = "development" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    else
        docker-compose up -d
    fi
    
    success "Services started"
}

# Wait for services to be healthy
wait_for_services() {
    log "Waiting for services to be healthy..."
    
    # Wait for database
    log "Waiting for PostgreSQL..."
    timeout 60 bash -c 'until docker exec nexus-postgres pg_isready -U nexus_user -d nexus_platform; do sleep 2; done'
    success "PostgreSQL is ready"
    
    # Wait for Redis
    log "Waiting for Redis..."
    timeout 30 bash -c 'until docker exec nexus-redis redis-cli ping; do sleep 2; done'
    success "Redis is ready"
    
    # Wait for backend
    log "Waiting for Backend API..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/health; do sleep 2; done'
    success "Backend API is ready"
    
    # Wait for frontend
    log "Waiting for Frontend..."
    timeout 60 bash -c 'until curl -f http://localhost:3000; do sleep 2; done'
    success "Frontend is ready"
}

# Run health checks
run_health_checks() {
    log "Running health checks..."
    
    # Backend health check
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Backend health check passed"
    else
        error "Backend health check failed"
        return 1
    fi
    
    # Frontend health check
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        success "Frontend health check passed"
    else
        error "Frontend health check failed"
        return 1
    fi
    
    # API endpoints check
    if curl -f http://localhost:8000/api/v1/ssot/aliases > /dev/null 2>&1; then
        success "SSOT API check passed"
    else
        warning "SSOT API check failed (may be expected)"
    fi
    
    success "All health checks completed"
}

# Display service information
display_info() {
    echo ""
    echo "🎉 NEXUS Platform Deployment Complete!"
    echo "======================================"
    echo ""
    echo "📊 Services Status:"
    echo "  ✅ Backend API: http://localhost:8000"
    echo "  ✅ Frontend UI: http://localhost:3000"
    echo "  ✅ API Docs: http://localhost:8000/docs"
    echo "  ✅ Prometheus: http://localhost:9090"
    echo "  ✅ Grafana: http://localhost:3001"
    echo ""
    echo "🔧 Management Commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart: docker-compose restart"
    echo "  Scale: docker-compose up -d --scale backend=3"
    echo ""
    echo "📝 Logs: $LOG_FILE"
    echo "🕐 Deployed at: $(date)"
    echo ""
}

# Cleanup function
cleanup() {
    if [ $? -ne 0 ]; then
        error "Deployment failed. Cleaning up..."
        docker-compose down
        exit 1
    fi
}

# Main deployment function
main() {
    log "Starting NEXUS Platform Docker deployment..."
    log "Environment: $ENVIRONMENT"
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    check_docker
    check_docker_compose
    create_directories
    build_images
    start_services
    wait_for_services
    run_health_checks
    display_info
    
    success "Deployment completed successfully!"
}

# Run main function
main "$@"
