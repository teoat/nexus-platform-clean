#!/bin/bash

# NEXUS Platform E2E Test Runner
# This script sets up and runs end-to-end tests with Playwright

set -e

echo "🚀 Starting NEXUS Platform E2E Tests..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 16+ to continue."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    print_error "Node.js version 16+ is required. Current version: $(node -v)"
    exit 1
fi

print_success "Node.js version: $(node -v)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm to continue."
    exit 1
fi

print_success "npm version: $(npm -v)"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    print_status "Installing E2E test dependencies..."
    npm install
    print_success "Dependencies installed successfully"
else
    print_status "Dependencies already installed"
fi

# Install Playwright browsers
print_status "Installing Playwright browsers..."
npx playwright install
print_success "Playwright browsers installed"

# Check if backend is running
print_status "Checking backend service..."
if curl -s http://localhost:8001/health > /dev/null; then
    print_success "Backend service is running"
else
    print_warning "Backend service is not running. Starting backend..."
    cd ../backend
    python start_server.py &
    BACKEND_PID=$!
    cd ../e2e-tests

    # Wait for backend to start
    print_status "Waiting for backend to start..."
    sleep 10

    if curl -s http://localhost:8001/health > /dev/null; then
        print_success "Backend service started successfully"
    else
        print_error "Failed to start backend service"
        exit 1
    fi
fi

# Check if frontend is running
print_status "Checking frontend service..."
if curl -s http://localhost:3000 > /dev/null; then
    print_success "Frontend service is running"
else
    print_warning "Frontend service is not running. Starting frontend..."
    cd ../nexus_frontend/web
    npm start &
    FRONTEND_PID=$!
    cd ../../e2e-tests

    # Wait for frontend to start
    print_status "Waiting for frontend to start..."
    sleep 15

    if curl -s http://localhost:3000 > /dev/null; then
        print_success "Frontend service started successfully"
    else
        print_error "Failed to start frontend service"
        exit 1
    fi
fi

# Create test results directory
mkdir -p test-results

# Run E2E tests
print_status "Running E2E tests..."

# Run tests based on command line arguments
if [ "$1" = "headed" ]; then
    print_status "Running tests in headed mode..."
    npm run test:headed
elif [ "$1" = "ui" ]; then
    print_status "Running tests in UI mode..."
    npm run test:ui
elif [ "$1" = "debug" ]; then
    print_status "Running tests in debug mode..."
    npm run test:debug
elif [ "$1" = "specific" ] && [ -n "$2" ]; then
    print_status "Running specific test: $2"
    npx playwright test "$2"
else
    print_status "Running all tests..."
    npm test
fi

# Check test results
if [ $? -eq 0 ]; then
    print_success "All E2E tests passed! 🎉"

    # Generate test report
    print_status "Generating test report..."
    npm run test:report

    print_success "Test report generated in test-results/"
else
    print_error "Some E2E tests failed! ❌"

    # Generate test report even on failure
    print_status "Generating test report..."
    npm run test:report

    print_warning "Check test-results/ for detailed failure information"
    exit 1
fi

# Cleanup background processes
if [ ! -z "$BACKEND_PID" ]; then
    print_status "Stopping backend service..."
    kill $BACKEND_PID 2>/dev/null || true
fi

if [ ! -z "$FRONTEND_PID" ]; then
    print_status "Stopping frontend service..."
    kill $FRONTEND_PID 2>/dev/null || true
fi

print_success "E2E test run completed!"

# Display summary
echo ""
echo "📊 Test Summary:"
echo "=================="
echo "✅ Tests completed"
echo "📁 Results: test-results/"
echo "📊 Report: test-results/results.html"
echo "📋 JSON: test-results/results.json"
echo "🧪 JUnit: test-results/results.xml"
echo ""
echo "🚀 NEXUS Platform E2E Tests Complete!"
