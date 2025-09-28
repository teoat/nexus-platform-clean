#!/bin/bash

# =============================================================================
# NEXUS Platform - Development Environment Script
# =============================================================================
# This script provides a comprehensive development environment setup
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
ACTION=${1:-start}
SERVICE=${2:-all}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

start_backend() {
    log_info "Starting Backend Server..."

    if check_port 8000; then
        log_warning "Backend already running on port 8000"
        return 0
    fi

    cd "$PROJECT_ROOT"

    # Activate virtual environment if it exists
    if [ -d "nexus_env" ]; then
        source nexus_env/bin/activate
    fi

    # Start backend
    python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid

    # Wait for backend to start
    sleep 5

    if check_port 8000; then
        log_success "Backend started successfully on http://localhost:8000"
    else
        log_error "Failed to start backend"
        return 1
    fi
}

start_frontend() {
    log_info "Starting Frontend Server..."

    if check_port 3000; then
        log_warning "Frontend already running on port 3000"
        return 0
    fi

    cd "$PROJECT_ROOT/nexus_frontend/web"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log_info "Installing frontend dependencies..."
        npm install
    fi

    # Start frontend
    npm start &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend.pid

    # Wait for frontend to start
    sleep 10

    if check_port 3000; then
        log_success "Frontend started successfully on http://localhost:3000"
    else
        log_error "Failed to start frontend"
        return 1
    fi
}

start_database() {
    log_info "Starting Database Services..."

    cd "$PROJECT_ROOT"
    docker-compose up -d postgres redis

    # Wait for services to be ready
    sleep 10

    log_success "Database services started"
}

test_services() {
    log_info "Testing Services..."

    # Test backend
    if curl -s http://localhost:8000/health > /dev/null; then
        log_success "Backend API: OK"
    else
        log_error "Backend API: Failed"
        return 1
    fi

    # Test frontend
    if curl -s http://localhost:3000 > /dev/null; then
        log_success "Frontend: OK"
    else
        log_error "Frontend: Failed"
        return 1
    fi

    # Test database
    if docker-compose exec postgres pg_isready -U ${POSTGRES_USER:-nexus_admin} > /dev/null 2>&1; then
        log_success "Database: OK"
    else
        log_error "Database: Failed"
        return 1
    fi
}

show_status() {
    echo -e "\n${CYAN}🎯 NEXUS Platform Development Status${NC}"
    echo -e "${CYAN}====================================${NC}"
    echo -e "🔧 Environment: Development"
    echo -e "📍 Frontend: http://localhost:3000"
    echo -e "📍 Backend API: http://localhost:8000"
    echo -e "📍 API Docs: http://localhost:8000/docs"
    echo -e "📍 Health Check: http://localhost:8000/health"
    echo ""
    echo -e "📋 Available Commands:"
    echo -e "  • Test API: curl http://localhost:8000/health"
    echo -e "  • View Users: curl http://localhost:8000/api/users"
    echo -e "  • View Accounts: curl http://localhost:8000/api/accounts"
    echo -e "  • View Dashboard: curl http://localhost:8000/api/dashboard"
    echo ""
    echo -e "🛠️  Management Commands:"
    echo -e "  • Stop Platform: ./scripts/dev.sh stop"
    echo -e "  • Restart: ./scripts/dev.sh restart"
    echo -e "  • Test: ./scripts/dev.sh test"
    echo -e "  • Logs: tail -f logs/*.log"
    echo -e "====================================${NC}"
}

stop_services() {
    log_info "Stopping NEXUS Platform..."

    # Stop backend
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        kill $BACKEND_PID 2>/dev/null || true
        rm -f backend.pid
    fi

    # Stop frontend
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        kill $FRONTEND_PID 2>/dev/null || true
        rm -f frontend.pid
    fi

    # Stop Docker services
    docker-compose down

    # Kill any remaining processes
    pkill -f "uvicorn.*backend.main" || true
    pkill -f "npm start" || true

    log_success "Platform stopped"
}

install_dependencies() {
    log_info "Installing Dependencies..."

    # Backend dependencies
    if [ -f "requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        pip install -r requirements.txt
    fi

    # Frontend dependencies
    if [ -f "nexus_frontend/web/package.json" ]; then
        log_info "Installing Node.js dependencies..."
        cd "$PROJECT_ROOT/nexus_frontend/web"
        npm install
    fi

    log_success "Dependencies installed"
}

setup_environment() {
    log_info "Setting up Development Environment..."

    # Create necessary directories
    mkdir -p logs
    mkdir -p data
    mkdir -p backups

    # Set up environment file
    if [ ! -f ".env" ]; then
        log_info "Creating .env file for development..."
        cat > .env << 'EOF'
# Development Environment
DEBUG=true
ENVIRONMENT=development
NODE_ENV=development
LOG_LEVEL=DEBUG

# Database
POSTGRES_DB=nexus_development
POSTGRES_USER=nexus_admin
POSTGRES_PASSWORD=dev_password_123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=dev_redis_password_123

# Security (Development keys - DO NOT USE IN PRODUCTION)
JWT_SECRET_KEY=dev_jwt_secret_key_for_development_only
ENCRYPTION_KEY=dev_encryption_key_32_chars_long
SECRET_KEY=dev_secret_key_for_development

# API
API_V1_STR=/api/v1
PROJECT_NAME=NEXUS Platform
VERSION=2.0.0

# Frontend
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WEBSOCKET_URL=ws://localhost:8000/ws
EOF
    fi

    log_success "Development environment set up"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    case $ACTION in
        "start")
            echo -e "${PURPLE}🚀 NEXUS Platform - Development Environment${NC}"
            echo -e "${PURPLE}===========================================${NC}"

            setup_environment
            start_database
            start_backend
            start_frontend

            if test_services; then
                show_status
            else
                log_error "Some services failed to start properly"
                exit 1
            fi
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            main start
            ;;
        "test")
            test_services
            ;;
        "install")
            install_dependencies
            ;;
        "setup")
            setup_environment
            install_dependencies
            ;;
        *)
            echo "Usage: $0 [ACTION] [SERVICE]"
            echo ""
            echo "ACTIONS:"
            echo "  start   - Start development environment (default)"
            echo "  stop    - Stop development environment"
            echo "  restart - Restart development environment"
            echo "  test    - Test running services"
            echo "  install - Install dependencies"
            echo "  setup   - Set up development environment"
            echo ""
            echo "SERVICES: all, frontend, backend, database"
            echo ""
            echo "Examples:"
            echo "  $0 start"
            echo "  $0 stop"
            echo "  $0 restart frontend"
            exit 1
            ;;
    esac
}

main "$@"
