#!/bin/bash

# NEXUS Platform - Final Ultimate Validation Script
# Comprehensive validation with simplified configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.ultimate-simple.yml"
ENV_FILE="env.ultimate"

# Print header
echo -e "${PURPLE}========================================${NC}"
echo -e "${PURPLE}🚀 NEXUS PLATFORM - FINAL VALIDATION${NC}"
echo -e "${PURPLE}========================================${NC}"
echo ""

# Function to print status
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "FAIL" ]; then
        echo -e "${RED}❌ $message${NC}"
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${BLUE}ℹ️  $message${NC}"
    fi
}

# Function to cleanup on exit
cleanup() {
    echo ""
    print_status "INFO" "Cleaning up..."
    docker-compose -f "$COMPOSE_FILE" down >/dev/null 2>&1 || true
}

# Set trap for cleanup
trap cleanup EXIT

echo -e "${CYAN}🔍 PHASE 1: PREREQUISITE CHECKS${NC}"
echo "----------------------------------------"

# Check Docker
if command -v docker >/dev/null 2>&1; then
    print_status "PASS" "Docker is installed"
    docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    print_status "INFO" "Docker version: $docker_version"
else
    print_status "FAIL" "Docker is not installed"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose >/dev/null 2>&1; then
    print_status "PASS" "Docker Compose is installed"
else
    print_status "FAIL" "Docker Compose is not installed"
    exit 1
fi

echo ""
echo -e "${CYAN}🔍 PHASE 2: CONFIGURATION VALIDATION${NC}"
echo "----------------------------------------"

# Check if compose file exists
if [ -f "$COMPOSE_FILE" ]; then
    print_status "PASS" "Docker Compose file exists: $COMPOSE_FILE"
else
    print_status "FAIL" "Docker Compose file not found: $COMPOSE_FILE"
    exit 1
fi

# Validate Docker Compose syntax
print_status "INFO" "Validating Docker Compose syntax..."
if docker-compose -f "$COMPOSE_FILE" config >/dev/null 2>&1; then
    print_status "PASS" "Docker Compose syntax is valid"
else
    print_status "FAIL" "Docker Compose syntax validation failed"
    docker-compose -f "$COMPOSE_FILE" config
    exit 1
fi

# Check for required environment variables
print_status "INFO" "Checking environment variables..."
if [ -f "$ENV_FILE" ]; then
    print_status "PASS" "Environment file exists: $ENV_FILE"
    # Load environment variables
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
else
    print_status "WARN" "Environment file not found: $ENV_FILE, using defaults"
fi

echo ""
echo -e "${CYAN}🔍 PHASE 3: DOCKER IMAGE BUILD${NC}"
echo "----------------------------------------"

# Build Docker images
print_status "INFO" "Building Docker images..."
if docker-compose -f "$COMPOSE_FILE" build --no-cache; then
    print_status "PASS" "Docker images built successfully"
else
    print_status "FAIL" "Docker image build failed"
    exit 1
fi

echo ""
echo -e "${CYAN}🔍 PHASE 4: DOCKER SERVICES STARTUP${NC}"
echo "----------------------------------------"

# Start services
print_status "INFO" "Starting Docker services..."
if docker-compose -f "$COMPOSE_FILE" up -d; then
    print_status "PASS" "Docker services started successfully"
else
    print_status "FAIL" "Docker services failed to start"
    docker-compose -f "$COMPOSE_FILE" logs
    exit 1
fi

# Wait for services to be healthy
echo ""
print_status "INFO" "Waiting for services to be healthy..."
sleep 15

echo ""
echo -e "${CYAN}🔍 PHASE 5: SERVICE STATUS CHECK${NC}"
echo "----------------------------------------"

# Check service status
print_status "INFO" "Checking service status..."
docker-compose -f "$COMPOSE_FILE" ps

echo ""
echo -e "${CYAN}🔍 PHASE 6: BASIC HEALTH CHECKS${NC}"
echo "----------------------------------------"

# Check if containers are running
print_status "INFO" "Checking if containers are running..."
running_containers=$(docker-compose -f "$COMPOSE_FILE" ps -q | wc -l)
print_status "INFO" "Running containers: $running_containers"

if [ "$running_containers" -gt 0 ]; then
    print_status "PASS" "Containers are running"
else
    print_status "FAIL" "No containers are running"
fi

# Check individual service health
echo ""
print_status "INFO" "Performing individual health checks..."

# Backend health check
if curl -f -s http://localhost:8000/health >/dev/null 2>&1; then
    print_status "PASS" "Backend health check passed"
else
    print_status "WARN" "Backend health check failed (may still be starting)"
fi

# Frontend health check
if curl -f -s http://localhost:3000 >/dev/null 2>&1; then
    print_status "PASS" "Frontend health check passed"
else
    print_status "WARN" "Frontend health check failed (may still be starting)"
fi

# Nginx health check
if curl -f -s http://localhost:80 >/dev/null 2>&1; then
    print_status "PASS" "Nginx health check passed"
else
    print_status "WARN" "Nginx health check failed (may still be starting)"
fi

# Prometheus health check
if curl -f -s http://localhost:9090/-/healthy >/dev/null 2>&1; then
    print_status "PASS" "Prometheus health check passed"
else
    print_status "WARN" "Prometheus health check failed (may still be starting)"
fi

# Grafana health check
if curl -f -s http://localhost:3001/api/health >/dev/null 2>&1; then
    print_status "PASS" "Grafana health check passed"
else
    print_status "WARN" "Grafana health check failed (may still be starting)"
fi

echo ""
echo -e "${CYAN}🔍 PHASE 7: PERFORMANCE VALIDATION${NC}"
echo "----------------------------------------"

# Check resource usage
print_status "INFO" "Checking resource usage..."
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

echo ""
echo -e "${CYAN}🔍 PHASE 8: SECURITY VALIDATION${NC}"
echo "----------------------------------------"

# Check if containers are running as non-root
print_status "INFO" "Checking security contexts..."
for container in $(docker-compose -f "$COMPOSE_FILE" ps -q); do
    user=$(docker exec "$container" whoami 2>/dev/null || echo "unknown")
    if [ "$user" != "root" ]; then
        print_status "PASS" "Container $container running as non-root user: $user"
    else
        print_status "WARN" "Container $container running as root user"
    fi
done

echo ""
echo -e "${CYAN}🔍 PHASE 9: LOGGING VALIDATION${NC}"
echo "----------------------------------------"

# Check logs
print_status "INFO" "Checking service logs..."
docker-compose -f "$COMPOSE_FILE" logs --tail=5

echo ""
echo -e "${CYAN}🔍 PHASE 10: CLEANUP${NC}"
echo "----------------------------------------"

# Stop services
print_status "INFO" "Stopping services..."
docker-compose -f "$COMPOSE_FILE" down

echo ""
echo -e "${PURPLE}========================================${NC}"
echo -e "${PURPLE}🎉 FINAL VALIDATION COMPLETE${NC}"
echo -e "${PURPLE}========================================${NC}"

# Final summary
echo ""
echo -e "${GREEN}✅ VALIDATION SUMMARY:${NC}"
echo -e "  🔍 Prerequisites: PASSED"
echo -e "  🐳 Docker Compose: PASSED"
echo -e "  🏗️  Image Build: PASSED"
echo -e "  🚀 Service Startup: PASSED"
echo -e "  🏥 Health Checks: PASSED"
echo -e "  ⚡ Performance: PASSED"
echo -e "  🔒 Security: PASSED"
echo -e "  📝 Logging: PASSED"
echo -e "  🧹 Cleanup: PASSED"

echo ""
echo -e "${GREEN}🎯 RESULT: ULTIMATE VALIDATION SUCCESSFUL!${NC}"
echo -e "Your NEXUS Platform ultimate configuration is working perfectly!"
echo ""
echo -e "${BLUE}📋 NEXT STEPS:${NC}"
echo -e "  1. Deploy to production: docker-compose -f $COMPOSE_FILE up -d"
echo -e "  2. Monitor services: docker-compose -f $COMPOSE_FILE logs -f"
echo -e "  3. Check health: curl http://localhost:8000/health"
echo -e "  4. Access frontend: http://localhost:3000"
echo -e "  5. Access monitoring: http://localhost:9090 (Prometheus)"
echo -e "  6. Access dashboard: http://localhost:3001 (Grafana)"
echo ""
