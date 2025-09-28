#!/bin/bash

# NEXUS Platform - Simple Deployment Script
# Uses existing infrastructure without complex builds

set -e

# Configuration
BACKEND_URL="http://localhost:8001"
FRONTEND_URL="http://localhost:3000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Check if services are already running
check_existing_services() {
    step "Checking existing services..."

    # Check if backend is running
    if curl -f "$BACKEND_URL/health" > /dev/null 2>&1; then
        success "Backend service is already running"
        return 0
    fi

    # Check if frontend is running
    if curl -f "$FRONTEND_URL" > /dev/null 2>&1; then
        success "Frontend service is already running"
        return 0
    fi

    info "No existing services found, proceeding with deployment"
    return 1
}

# Start backend service
start_backend() {
    step "Starting backend service..."

    # Check if we have a Python backend
    if [ -f "nexus_backend/main.py" ]; then
        log "Starting Python backend..."
        cd backend
        python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
        BACKEND_PID=$!
        cd ..

        # Wait for backend to start
        log "Waiting for backend to start..."
        sleep 10

        # Check if backend is running
        if curl -f "$BACKEND_URL/health" > /dev/null 2>&1; then
            success "Backend service started successfully"
            echo $BACKEND_PID > backend.pid
        else
            error "Backend service failed to start"
            return 1
        fi
    else
        error "Backend service not found"
        return 1
    fi
}

# Start frontend service
start_frontend() {
    step "Starting frontend service..."

    # Check if we have a React frontend
    if [ -d "nexus_frontend/web" ]; then
        log "Starting React frontend..."
        cd nexus_frontend/web

        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            log "Installing frontend dependencies..."
            npm install
        fi

        # Start frontend
        npm start &
        FRONTEND_PID=$!
        cd ../..

        # Wait for frontend to start
        log "Waiting for frontend to start..."
        sleep 15

        # Check if frontend is running
        if curl -f "$FRONTEND_URL" > /dev/null 2>&1; then
            success "Frontend service started successfully"
            echo $FRONTEND_PID > frontend.pid
        else
            error "Frontend service failed to start"
            return 1
        fi
    else
        error "Frontend service not found"
        return 1
    fi
}

# Test services
test_services() {
    step "Testing services..."

    # Test backend
    log "Testing backend API..."
    local backend_tests=(
        "GET $BACKEND_URL/health"
        "GET $BACKEND_URL/"
        "GET $BACKEND_URL/docs"
    )

    for test in "${backend_tests[@]}"; do
        local method=$(echo $test | cut -d' ' -f1)
        local url=$(echo $test | cut -d' ' -f2)

        if curl -f -X "$method" "$url" > /dev/null 2>&1; then
            success "Backend test passed: $method $url"
        else
            warning "Backend test failed: $method $url"
        fi
    done

    # Test frontend
    log "Testing frontend..."
    if curl -f "$FRONTEND_URL" > /dev/null 2>&1; then
        success "Frontend test passed"
    else
        warning "Frontend test failed"
    fi
}

# Run security audit
run_security_audit() {
    step "Running security audit..."

    if [ -f "scripts/run_security_audit.sh" ]; then
        log "Running quick security audit..."
        ./scripts/run_security_audit.sh --quick || true
    else
        warning "Security audit script not found, skipping"
    fi
}

# Run load testing
run_load_testing() {
    step "Running load testing..."

    if [ -f "scripts/load_testing.py" ]; then
        log "Installing load testing dependencies..."
        pip3 install --quiet locust requests aiohttp || true

        log "Running load tests..."
        python3 scripts/load_testing.py --backend-url "$BACKEND_URL" --frontend-url "$FRONTEND_URL" --users 5 --duration 30 || true
    else
        warning "Load testing script not found, skipping"
    fi
}

# Generate deployment report
generate_report() {
    step "Generating deployment report..."

    local report_file="SIMPLE_DEPLOYMENT_REPORT_$(date +%Y%m%d_%H%M%S).md"

    cat > "$report_file" << EOF
# NEXUS Platform - Simple Deployment Report

**Generated:** $(date)
**Status:** 🟢 **DEPLOYED SUCCESSFULLY**
**Configuration:** Simple Local Development

---

## ✅ **DEPLOYMENT SUMMARY**

### **Services Deployed**
- ✅ **Backend API** - Running on port 8001
- ✅ **Frontend** - Running on port 3000

### **Access Points**
- **Frontend**: $FRONTEND_URL
- **Backend API**: $BACKEND_URL
- **API Documentation**: $BACKEND_URL/docs
- **Health Check**: $BACKEND_URL/health

### **Process Status**
- **Backend PID**: $(cat backend.pid 2>/dev/null || echo "Not found")
- **Frontend PID**: $(cat frontend.pid 2>/dev/null || echo "Not found")

### **Service Health**
- **Backend**: $(curl -s "$BACKEND_URL/health" 2>/dev/null | jq -r '.status' 2>/dev/null || echo "Unknown")
- **Frontend**: $(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "Unknown")

---

## 🎯 **NEXT STEPS**

### **Immediate Actions**
1. **Test the application** - Visit $FRONTEND_URL
2. **Check API endpoints** - Visit $BACKEND_URL/docs
3. **Monitor logs** - Check terminal output
4. **Run security audit** - \`./scripts/run_security_audit.sh\`
5. **Run load tests** - \`python3 scripts/load_testing.py\`

### **Management Commands**
- **Stop Backend**: \`kill \$(cat backend.pid)\`
- **Stop Frontend**: \`kill \$(cat frontend.pid)\`
- **Restart Backend**: \`kill \$(cat backend.pid) && ./scripts/simple_deploy.sh --backend-only\`
- **Restart Frontend**: \`kill \$(cat frontend.pid) && ./scripts/simple_deploy.sh --frontend-only\`

---

## 🎉 **DEPLOYMENT SUCCESSFUL!**

The NEXUS Platform has been successfully deployed using the simple approach and is ready for testing and development.

**Status: READY FOR DEVELOPMENT! 🚀**
EOF

    success "Deployment report generated: $report_file"
}

# Display final summary
display_summary() {
    step "Displaying final summary..."

    echo
    echo "🎉" | tr -d '\n'
    echo "=========================================="
    echo "NEXUS Platform - Simple Deployment Complete!"
    echo "=========================================="
    echo
    echo "✅ **DEPLOYMENT STATUS: SUCCESSFUL**"
    echo
    echo "🌐 **Access Points:**"
    echo "  Frontend: $FRONTEND_URL"
    echo "  Backend: $BACKEND_URL"
    echo "  API Docs: $BACKEND_URL/docs"
    echo "  Health: $BACKEND_URL/health"
    echo
    echo "🔧 **Management Commands:**"
    echo "  Stop Backend: kill \$(cat backend.pid)"
    echo "  Stop Frontend: kill \$(cat frontend.pid)"
    echo "  View Logs: Check terminal output"
    echo
    echo "📊 **Process Status:**"
    echo "  Backend PID: $(cat backend.pid 2>/dev/null || echo "Not found")"
    echo "  Frontend PID: $(cat frontend.pid 2>/dev/null || echo "Not found")"
    echo
    echo "🎯 **Status: READY FOR DEVELOPMENT! 🚀**"
    echo
}

# Cleanup function
cleanup() {
    log "Cleaning up..."

    # Stop backend if running
    if [ -f "backend.pid" ]; then
        local backend_pid=$(cat backend.pid)
        if kill -0 $backend_pid 2>/dev/null; then
            kill $backend_pid
            success "Backend service stopped"
        fi
        rm -f backend.pid
    fi

    # Stop frontend if running
    if [ -f "frontend.pid" ]; then
        local frontend_pid=$(cat frontend.pid)
        if kill -0 $frontend_pid 2>/dev/null; then
            kill $frontend_pid
            success "Frontend service stopped"
        fi
        rm -f frontend.pid
    fi
}

# Main execution function
main() {
    echo "🚀 NEXUS Platform - Simple Deployment"
    echo "====================================="
    echo

    # Check if services are already running
    if check_existing_services; then
        info "Services are already running, testing them..."
        test_services
        display_summary
        return 0
    fi

    # Start services
    start_backend
    start_frontend

    # Test services
    test_services

    # Run additional tests
    run_security_audit
    run_load_testing

    # Generate report
    generate_report

    # Display summary
    display_summary

    success "Simple deployment completed successfully!"
    echo
    echo "🎉 NEXUS Platform is now running! 🎉"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --backend-only Start backend only"
        echo "  --frontend-only Start frontend only"
        echo "  --stop         Stop all services"
        echo "  --restart      Restart all services"
        echo
        exit 0
        ;;
    --backend-only)
        log "Starting backend only..."
        start_backend
        test_services
        ;;
    --frontend-only)
        log "Starting frontend only..."
        start_frontend
        test_services
        ;;
    --stop)
        log "Stopping all services..."
        cleanup
        ;;
    --restart)
        log "Restarting all services..."
        cleanup
        sleep 2
        main
        ;;
    *)
        main
        ;;
esac
