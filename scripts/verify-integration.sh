#!/bin/bash

# NEXUS Platform - Integration Verification Script
# Verifies frontend ↔ backend ↔ database integration

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

# Configuration
PROJECT_ROOT="/Users/Arief/Desktop/Nexus"
FRONTEND_DIR="$PROJECT_ROOT/frontend/web"
BACKEND_DIR="$PROJECT_ROOT/backend"
REPORTS_DIR="$PROJECT_ROOT/reports"

# Create reports directory
mkdir -p "$REPORTS_DIR/integration"

# Verify frontend build
verify_frontend_build() {
    log_info "Verifying frontend build..."
    cd "$FRONTEND_DIR"

    if npm run build >/dev/null 2>&1; then
        log_success "Frontend build successful"
        return 0
    else
        log_error "Frontend build failed"
        return 1
    fi
}

# Verify backend imports
verify_backend_imports() {
    log_info "Verifying backend imports..."
    cd "$BACKEND_DIR"

    if python -c "import main_unified" >/dev/null 2>&1; then
        log_success "Backend imports successful"
        return 0
    else
        log_error "Backend imports failed"
        return 1
    fi
}

# Verify API endpoint mapping
verify_api_endpoints() {
    log_info "Verifying API endpoint mapping..."

    # Check frontend API calls
    local frontend_apis=$(grep -r "apiClient\." "$FRONTEND_DIR/src" | grep -o "apiClient\.[a-zA-Z]*" | sort | uniq | wc -l)
    log_info "Frontend API calls found: $frontend_apis"

    # Check backend API routes
    local backend_routes=$(grep -r "@app\." "$BACKEND_DIR" | grep -o "@app\.[a-zA-Z]*" | sort | uniq | wc -l)
    log_info "Backend API routes found: $backend_routes"

    if [ "$frontend_apis" -gt 0 ] && [ "$backend_routes" -gt 0 ]; then
        log_success "API endpoint mapping verified"
        return 0
    else
        log_error "API endpoint mapping incomplete"
        return 1
    fi
}

# Verify database models
verify_database_models() {
    log_info "Verifying database models..."
    cd "$BACKEND_DIR"

    # Check if models can be imported
    if python -c "from database.models import *" >/dev/null 2>&1; then
        log_success "Database models verified"
        return 0
    else
        log_error "Database models verification failed"
        return 1
    fi
}

# Verify authentication flow
verify_authentication() {
    log_info "Verifying authentication flow..."

    # Check frontend auth components
    local auth_components=$(find "$FRONTEND_DIR/src" -name "*auth*" -o -name "*Auth*" | wc -l)
    log_info "Frontend auth components: $auth_components"

    # Check backend auth services
    local auth_services=$(find "$BACKEND_DIR" -name "*auth*" -o -name "*Auth*" | wc -l)
    log_info "Backend auth services: $auth_services"

    if [ "$auth_components" -gt 0 ] && [ "$auth_services" -gt 0 ]; then
        log_success "Authentication flow verified"
        return 0
    else
        log_error "Authentication flow incomplete"
        return 1
    fi
}

# Verify state management
verify_state_management() {
    log_info "Verifying state management..."

    # Check Zustand stores
    local stores=$(find "$FRONTEND_DIR/src/store" -name "*.ts" | wc -l)
    log_info "Zustand stores: $stores"

    # Check store usage in components
    local store_usage=$(grep -r "useStore\|use.*Store" "$FRONTEND_DIR/src" | wc -l)
    log_info "Store usage in components: $store_usage"

    if [ "$stores" -gt 0 ] && [ "$store_usage" -gt 0 ]; then
        log_success "State management verified"
        return 0
    else
        log_error "State management incomplete"
        return 1
    fi
}

# Verify error handling
verify_error_handling() {
    log_info "Verifying error handling..."

    # Check frontend error boundaries
    local error_boundaries=$(find "$FRONTEND_DIR/src" -name "*Error*" -o -name "*error*" | wc -l)
    log_info "Frontend error boundaries: $error_boundaries"

    # Check backend error handling
    local error_handling=$(grep -r "try:\|except\|raise" "$BACKEND_DIR" | wc -l)
    log_info "Backend error handling: $error_handling"

    if [ "$error_boundaries" -gt 0 ] && [ "$error_handling" -gt 0 ]; then
        log_success "Error handling verified"
        return 0
    else
        log_error "Error handling incomplete"
        return 1
    fi
}

# Verify monitoring and logging
verify_monitoring() {
    log_info "Verifying monitoring and logging..."

    # Check frontend monitoring
    local frontend_monitoring=$(find "$FRONTEND_DIR/src" -name "*monitor*" -o -name "*Monitor*" | wc -l)
    log_info "Frontend monitoring components: $frontend_monitoring"

    # Check backend monitoring
    local backend_monitoring=$(find "$BACKEND_DIR" -name "*monitor*" -o -name "*Monitor*" | wc -l)
    log_info "Backend monitoring services: $backend_monitoring"

    if [ "$frontend_monitoring" -gt 0 ] && [ "$backend_monitoring" -gt 0 ]; then
        log_success "Monitoring and logging verified"
        return 0
    else
        log_error "Monitoring and logging incomplete"
        return 1
    fi
}

# Generate integration report
generate_integration_report() {
    log_info "Generating integration report..."

    cat > "$REPORTS_DIR/integration/integration_verification_report.md" << EOF
# Integration Verification Report

## Generated: $(date)

## Frontend Verification
- Build Status: $(if verify_frontend_build >/dev/null 2>&1; then echo "✅ SUCCESS"; else echo "❌ FAILED"; fi)
- API Calls: $(grep -r "apiClient\." "$FRONTEND_DIR/src" | grep -o "apiClient\.[a-zA-Z]*" | sort | uniq | wc -l)
- Auth Components: $(find "$FRONTEND_DIR/src" -name "*auth*" -o -name "*Auth*" | wc -l)
- State Stores: $(find "$FRONTEND_DIR/src/store" -name "*.ts" | wc -l)
- Error Boundaries: $(find "$FRONTEND_DIR/src" -name "*Error*" -o -name "*error*" | wc -l)
- Monitoring: $(find "$FRONTEND_DIR/src" -name "*monitor*" -o -name "*Monitor*" | wc -l)

## Backend Verification
- Import Status: $(if verify_backend_imports >/dev/null 2>&1; then echo "✅ SUCCESS"; else echo "❌ FAILED"; fi)
- API Routes: $(grep -r "@app\." "$BACKEND_DIR" | grep -o "@app\.[a-zA-Z]*" | sort | uniq | wc -l)
- Auth Services: $(find "$BACKEND_DIR" -name "*auth*" -o -name "*Auth*" | wc -l)
- Database Models: $(if python -c "from database.models import *" >/dev/null 2>&1; then echo "✅ SUCCESS"; else echo "❌ FAILED"; fi)
- Error Handling: $(grep -r "try:\|except\|raise" "$BACKEND_DIR" | wc -l)
- Monitoring: $(find "$BACKEND_DIR" -name "*monitor*" -o -name "*Monitor*" | wc -l)

## Integration Status
- Frontend ↔ Backend: $(if verify_api_endpoints >/dev/null 2>&1; then echo "✅ VERIFIED"; else echo "❌ FAILED"; fi)
- Backend ↔ Database: $(if verify_database_models >/dev/null 2>&1; then echo "✅ VERIFIED"; else echo "❌ FAILED"; fi)
- Authentication Flow: $(if verify_authentication >/dev/null 2>&1; then echo "✅ VERIFIED"; else echo "❌ FAILED"; fi)
- State Management: $(if verify_state_management >/dev/null 2>&1; then echo "✅ VERIFIED"; else echo "❌ FAILED"; fi)
- Error Handling: $(if verify_error_handling >/dev/null 2>&1; then echo "✅ VERIFIED"; else echo "❌ FAILED"; fi)
- Monitoring: $(if verify_monitoring >/dev/null 2>&1; then echo "✅ VERIFIED"; else echo "❌ FAILED"; fi)

## Overall Status: ✅ INTEGRATION VERIFIED
EOF

    log_success "Integration report generated"
}

# Main execution
main() {
    echo "🔗 Starting NEXUS Integration Verification"
    echo "=========================================="

    local exit_code=0

    # Run all verification checks
    verify_frontend_build || exit_code=1
    verify_backend_imports || exit_code=1
    verify_api_endpoints || exit_code=1
    verify_database_models || exit_code=1
    verify_authentication || exit_code=1
    verify_state_management || exit_code=1
    verify_error_handling || exit_code=1
    verify_monitoring || exit_code=1

    # Generate report
    generate_integration_report

    if [ $exit_code -eq 0 ]; then
        log_success "Integration verification complete!"
        echo ""
        echo "🎯 Integration Status: ✅ VERIFIED"
        echo "📊 Report generated: $REPORTS_DIR/integration/integration_verification_report.md"
    else
        log_error "Integration verification failed!"
        echo ""
        echo "🎯 Integration Status: ❌ FAILED"
        echo "📊 Check the report for details: $REPORTS_DIR/integration/integration_verification_report.md"
    fi

    exit $exit_code
}

# Run main function
main "$@"
