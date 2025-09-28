#!/bin/bash

# =============================================================================
# NEXUS Platform - Consolidated Stop Script
# =============================================================================
# This script consolidates all stop functionality into a single, comprehensive tool
# =============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE=${1:-all}
FORCE=${2:-false}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

stop_docker_services() {
    log_info "Stopping Docker services..."

    case $SERVICE in
        "frontend")
            docker-compose stop frontend
            ;;
        "backend")
            docker-compose stop backend postgres redis
            ;;
        "ai")
            docker-compose --profile ai stop frenly-ai
            ;;
        "monitoring")
            docker-compose --profile monitoring stop prometheus grafana node-exporter cadvisor
            ;;
        "all")
            docker-compose down
            ;;
    esac

    log_success "Docker services stopped"
}

stop_local_services() {
    log_info "Stopping local services..."

    # Stop Python processes
    pkill -f "python.*simple_server.py" || true
    pkill -f "python.*start_nexus" || true
    pkill -f "python.*launch_orchestrated" || true
    pkill -f "python.*deploy_production" || true

    # Stop Node.js processes
    pkill -f "npm start" || true
    pkill -f "react-scripts start" || true

    # Stop specific port processes
    if command -v lsof &> /dev/null; then
        # Stop processes on common ports
        for port in 3000 8000 8001 8002 9090 3001; do
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                log_info "Stopping process on port $port"
                lsof -ti:$port | xargs kill -9 2>/dev/null || true
            fi
        done
    fi

    log_success "Local services stopped"
}

cleanup_containers() {
    if [ "$FORCE" = "true" ]; then
        log_info "Force cleaning up containers..."
        docker-compose down --volumes --remove-orphans
        docker system prune -f
    else
        log_info "Cleaning up containers..."
        docker-compose down
    fi
}

cleanup_logs() {
    log_info "Cleaning up log files..."

    # Remove log files
    find "$PROJECT_ROOT" -name "*.log" -type f -delete 2>/dev/null || true
    find "$PROJECT_ROOT/logs" -name "*.log" -type f -delete 2>/dev/null || true

    # Remove PID files
    find "$PROJECT_ROOT" -name "*.pid" -type f -delete 2>/dev/null || true

    log_success "Log files cleaned up"
}

show_status() {
    log_info "Checking remaining services..."

    # Check for running Docker containers
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q nexus; then
        log_warning "Some Docker containers are still running:"
        docker ps --format "table {{.Names}}\t{{.Status}}" | grep nexus
    else
        log_success "No Docker containers running"
    fi

    # Check for processes on common ports
    if command -v lsof &> /dev/null; then
        for port in 3000 8000 8001 8002 9090 3001; do
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                log_warning "Process still running on port $port"
            fi
        done
    fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    echo -e "${PURPLE}🛑 NEXUS Platform - Stop Script${NC}"
    echo -e "${PURPLE}================================${NC}"

    log_info "Stopping NEXUS Platform services..."
    log_info "Service: $SERVICE"
    log_info "Force: $FORCE"

    stop_docker_services
    stop_local_services
    cleanup_containers
    cleanup_logs
    show_status

    log_success "NEXUS Platform stopped successfully!"
    echo -e "${CYAN}💡 To start the platform again, run: ./scripts/deploy.sh${NC}"
}

# Handle command line arguments
case "${1:-}" in
    "help"|"-h"|"--help")
        echo "Usage: $0 [SERVICE] [FORCE]"
        echo ""
        echo "SERVICE: frontend, backend, ai, monitoring, all (default: all)"
        echo "FORCE: true, false (default: false) - Force cleanup including volumes"
        echo ""
        echo "Examples:"
        echo "  $0 all false"
        echo "  $0 frontend false"
        echo "  $0 all true"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
