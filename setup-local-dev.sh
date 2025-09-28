#!/bin/bash

# NEXUS Platform - Local Development Setup Script
# Phase 1: Critical Build Fixes Implementation

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

# Check if Docker is running
check_docker() {
    log_info "Checking Docker status..."
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    log_success "Docker is running"
}

# Check if Docker Compose is available
check_docker_compose() {
    log_info "Checking Docker Compose..."
    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        log_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    log_success "Docker Compose is available"
}

# Clean up existing containers and volumes
cleanup() {
    log_info "Cleaning up existing containers and volumes..."
    
    # Stop and remove containers
    docker-compose -f docker-compose.local.yml down --remove-orphans 2>/dev/null || true
    
    # Remove volumes if requested
    if [ "$1" = "--clean-volumes" ]; then
        log_warning "Removing all volumes (this will delete all data)..."
        docker volume prune -f
        docker-compose -f docker-compose.local.yml down -v 2>/dev/null || true
    fi
    
    log_success "Cleanup completed"
}

# Build and start services
start_services() {
    log_info "Building and starting services..."
    
    # Build images
    log_info "Building Docker images..."
    docker-compose -f docker-compose.local.yml build --no-cache
    
    # Start services
    log_info "Starting services..."
    docker-compose -f docker-compose.local.yml up -d
    
    log_success "Services started successfully"
}

# Wait for services to be healthy
wait_for_services() {
    log_info "Waiting for services to be healthy..."
    
    # Wait for PostgreSQL
    log_info "Waiting for PostgreSQL..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose -f docker-compose.local.yml exec -T postgres pg_isready -U nexus_user -d nexus_platform >/dev/null 2>&1; then
            log_success "PostgreSQL is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "PostgreSQL failed to start within 60 seconds"
        return 1
    fi
    
    # Wait for Redis
    log_info "Waiting for Redis..."
    timeout=30
    while [ $timeout -gt 0 ]; do
        if docker-compose -f docker-compose.local.yml exec -T redis redis-cli ping >/dev/null 2>&1; then
            log_success "Redis is ready"
            break
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "Redis failed to start within 30 seconds"
        return 1
    fi
    
    # Wait for Backend
    log_info "Waiting for Backend API..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            log_success "Backend API is ready"
            break
        fi
        sleep 3
        timeout=$((timeout - 3))
    done
    
    if [ $timeout -le 0 ]; then
        log_error "Backend API failed to start within 60 seconds"
        return 1
    fi
    
    # Wait for Frontend
    log_info "Waiting for Frontend..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:3000 >/dev/null 2>&1; then
            log_success "Frontend is ready"
            break
        fi
        sleep 3
        timeout=$((timeout - 3))
    done
    
    if [ $timeout -le 0 ]; then
        log_warning "Frontend may not be ready yet, but continuing..."
    fi
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Run migrations using the migration service
    if docker-compose -f docker-compose.local.yml run --rm migration; then
        log_success "Database migrations completed successfully"
    else
        log_error "Database migrations failed"
        return 1
    fi
}

# Test services
test_services() {
    log_info "Testing services..."
    
    # Test Backend API
    log_info "Testing Backend API..."
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        log_success "Backend API health check passed"
    else
        log_error "Backend API health check failed"
        return 1
    fi
    
    # Test Frontend
    log_info "Testing Frontend..."
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        log_success "Frontend is accessible"
    else
        log_warning "Frontend may not be fully ready yet"
    fi
    
    # Test Database connection
    log_info "Testing Database connection..."
    if docker-compose -f docker-compose.local.yml exec -T postgres psql -U nexus_user -d nexus_platform -c "SELECT 1;" >/dev/null 2>&1; then
        log_success "Database connection test passed"
    else
        log_error "Database connection test failed"
        return 1
    fi
}

# Show service status
show_status() {
    log_info "Service Status:"
    echo ""
    
    # Show running containers
    docker-compose -f docker-compose.local.yml ps
    
    echo ""
    log_info "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Docs: http://localhost:8000/docs"
    echo "  PostgreSQL: localhost:5432"
    echo "  Redis: localhost:6379"
    echo ""
    
    log_info "Useful Commands:"
    echo "  View logs: docker-compose -f docker-compose.local.yml logs -f [service]"
    echo "  Stop services: docker-compose -f docker-compose.local.yml down"
    echo "  Restart service: docker-compose -f docker-compose.local.yml restart [service]"
    echo "  Access database: docker-compose -f docker-compose.local.yml exec postgres psql -U nexus_user -d nexus_platform"
    echo ""
}

# Main function
main() {
    log_info "Starting NEXUS Platform Local Development Setup"
    log_info "Phase 1: Critical Build Fixes Implementation"
    echo ""
    
    # Parse command line arguments
    CLEAN_VOLUMES=false
    SKIP_MIGRATIONS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean-volumes)
                CLEAN_VOLUMES=true
                shift
                ;;
            --skip-migrations)
                SKIP_MIGRATIONS=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --clean-volumes    Remove all volumes and data"
                echo "  --skip-migrations  Skip database migrations"
                echo "  --help            Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Run setup steps
    check_docker
    check_docker_compose
    
    if [ "$CLEAN_VOLUMES" = true ]; then
        cleanup --clean-volumes
    else
        cleanup
    fi
    
    start_services
    wait_for_services
    
    if [ "$SKIP_MIGRATIONS" = false ]; then
        run_migrations
    fi
    
    test_services
    show_status
    
    log_success "NEXUS Platform Local Development Setup Complete!"
    log_info "You can now access the application at http://localhost:3000"
}

# Run main function
main "$@"
