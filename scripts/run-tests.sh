#!/bin/bash
# Test Runner Script for NEXUS Platform
# Agent 4: Testing & Quality Agent Implementation

set -e

echo "🧪 Running NEXUS Platform Tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
FRONTEND_DIR="nexus_frontend/web"
BACKEND_DIR="nexus_backend"
TESTS_DIR="tests"
COVERAGE_THRESHOLD=80

# Function to print colored output
print_status() {
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

# Function to check if service is running
check_service() {
    local service=$1
    local port=$2

    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        print_success "$service is running on port $port"
        return 0
    else
        print_error "$service is not running on port $port"
        return 1
    fi
}

# Function to run frontend tests
run_frontend_tests() {
    print_status "Running frontend tests..."

    cd "$FRONTEND_DIR"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi

    # Run unit tests
    print_status "Running unit tests..."
    npm test -- --coverage --watchAll=false --passWithNoTests

    # Check coverage
    if [ -f "coverage/lcov.info" ]; then
        coverage_percent=$(grep -o 'lines.*: [0-9]*\.[0-9]*%' coverage/lcov-report/index.html | grep -o '[0-9]*\.[0-9]*%' | head -1 | sed 's/%//')
        if (( $(echo "$coverage_percent >= $COVERAGE_THRESHOLD" | bc -l) )); then
            print_success "Frontend coverage: $coverage_percent% (>= $COVERAGE_THRESHOLD%)"
        else
            print_warning "Frontend coverage: $coverage_percent% (< $COVERAGE_THRESHOLD%)"
        fi
    fi

    # Run E2E tests if Cypress is available
    if [ -f "cypress.config.js" ]; then
        print_status "Running E2E tests..."
        npx cypress run --headless
    fi

    cd ..
}

# Function to run backend tests
run_backend_tests() {
    print_status "Running backend tests..."

    # Check if Python virtual environment exists
    if [ ! -d "nexus_env" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv nexus_env
    fi

    # Activate virtual environment
    source nexus_env/bin/activate

    # Install dependencies
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt
    pip install pytest pytest-asyncio pytest-cov httpx

    # Run unit tests
    print_status "Running backend unit tests..."
    pytest tests/nexus_backend/ -v --cov=nexus_backend --cov-report=html --cov-report=term

    # Check coverage
    if [ -f "htmlcov/index.html" ]; then
        coverage_percent=$(grep -o 'total.*[0-9]*\.[0-9]*%' htmlcov/index.html | grep -o '[0-9]*\.[0-9]*%' | head -1 | sed 's/%//')
        if (( $(echo "$coverage_percent >= $COVERAGE_THRESHOLD" | bc -l) )); then
            print_success "Backend coverage: $coverage_percent% (>= $COVERAGE_THRESHOLD%)"
        else
            print_warning "Backend coverage: $coverage_percent% (< $COVERAGE_THRESHOLD%)"
        fi
    fi

    deactivate
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."

    # Check if services are running
    if ! check_service "Backend" 8001; then
        print_error "Backend service is not running. Please start the services first."
        return 1
    fi

    if ! check_service "Frontend" 3000; then
        print_error "Frontend service is not running. Please start the services first."
        return 1
    fi

    # Activate virtual environment
    source nexus_env/bin/activate

    # Install additional dependencies for integration tests
    pip install selenium websocket-client locust

    # Run integration tests
    print_status "Running frontend-backend integration tests..."
    pytest tests/integration/ -v

    deactivate
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running performance tests..."

    # Check if services are running
    if ! check_service "Backend" 8001; then
        print_error "Backend service is not running. Please start the services first."
        return 1
    fi

    # Activate virtual environment
    source nexus_env/bin/activate

    # Run performance tests
    print_status "Running load tests..."
    pytest tests/performance/ -v

    deactivate
}

# Function to run security tests
run_security_tests() {
    print_status "Running security tests..."

    # Check if services are running
    if ! check_service "Backend" 8001; then
        print_error "Backend service is not running. Please start the services first."
        return 1
    fi

    # Activate virtual environment
    source nexus_env/bin/activate

    # Install additional dependencies for security tests
    pip install PyJWT

    # Run security tests
    print_status "Running security tests..."
    pytest tests/security/ -v

    deactivate
}

# Function to generate test report
generate_test_report() {
    print_status "Generating test report..."

    # Create reports directory
    mkdir -p reports

    # Generate HTML report
    cat > reports/test-report.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>NEXUS Platform Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .success { color: green; }
        .warning { color: orange; }
        .error { color: red; }
        .coverage { background-color: #f9f9f9; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NEXUS Platform Test Report</h1>
        <p>Generated on: $(date)</p>
    </div>

    <div class="section">
        <h2>Test Summary</h2>
        <p>This report contains the results of all test suites run for the NEXUS Platform.</p>
    </div>

    <div class="section">
        <h2>Coverage Reports</h2>
        <div class="coverage">
            <h3>Frontend Coverage</h3>
            <p>Check <a href="../nexus_frontend/web/coverage/lcov-report/index.html">Frontend Coverage Report</a></p>
        </div>
        <div class="coverage">
            <h3>Backend Coverage</h3>
            <p>Check <a href="../htmlcov/index.html">Backend Coverage Report</a></p>
        </div>
    </div>

    <div class="section">
        <h2>Test Results</h2>
        <p>All test results are available in the respective test directories.</p>
    </div>
</body>
</html>
EOF

    print_success "Test report generated at reports/test-report.html"
}

# Main execution
main() {
    echo "🚀 Starting NEXUS Platform Test Suite..."
    echo ""

    # Parse command line arguments
    case "${1:-all}" in
        "frontend")
            run_frontend_tests
            ;;
        "backend")
            run_backend_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "performance")
            run_performance_tests
            ;;
        "security")
            run_security_tests
            ;;
        "all")
            run_frontend_tests
            run_backend_tests
            run_integration_tests
            run_performance_tests
            run_security_tests
            ;;
        "quick")
            run_frontend_tests
            run_backend_tests
            ;;
        *)
            echo "Usage: $0 [frontend|backend|integration|performance|security|all|quick]"
            echo ""
            echo "Options:"
            echo "  frontend     Run only frontend tests"
            echo "  backend      Run only backend tests"
            echo "  integration  Run only integration tests"
            echo "  performance  Run only performance tests"
            echo "  security     Run only security tests"
            echo "  all          Run all tests (default)"
            echo "  quick        Run only frontend and backend tests"
            exit 1
            ;;
    esac

    # Generate test report
    generate_test_report

    echo ""
    print_success "All tests completed successfully! 🎉"
    echo ""
    echo "📊 Test Reports:"
    echo "  - HTML Report: reports/test-report.html"
    echo "  - Frontend Coverage: nexus_frontend/web/coverage/lcov-report/index.html"
    echo "  - Backend Coverage: htmlcov/index.html"
    echo ""
    echo "🔧 To run specific test suites:"
    echo "  ./scripts/run-tests.sh frontend"
    echo "  ./scripts/run-tests.sh backend"
    echo "  ./scripts/run-tests.sh integration"
    echo "  ./scripts/run-tests.sh performance"
    echo "  ./scripts/run-tests.sh security"
}

# Run main function
main "$@"
