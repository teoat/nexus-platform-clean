#!/bin/bash

# NEXUS Platform - Health Check Script
# This script checks the health of all services

set -e

echo "🔍 Checking NEXUS Platform Services Health..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service health
check_service() {
    local service_name=$1
    local url=$2
    local port=$3

    echo -n "Checking $service_name... "

    if curl -f -s "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ Unhealthy${NC}"
        return 1
    fi
}

# Check if services are running
echo "📊 Service Status:"
echo "=================="

# Check API Gateway
check_service "API Gateway" "http://localhost:8000/health" "8000"

# Check User Service
check_service "User Service" "http://localhost:8001/health" "8001"

# Check Transaction Service
check_service "Transaction Service" "http://localhost:8002/health" "8002"

# Check Account Service
check_service "Account Service" "http://localhost:8003/health" "8003"

# Check Analytics Service
check_service "Analytics Service" "http://localhost:8004/health" "8004"

# Check File Service
check_service "File Service" "http://localhost:8005/health" "8005"

# Check Notification Service
check_service "Notification Service" "http://localhost:8006/health" "8006"

# Check Frontend
check_service "Frontend" "http://localhost:3000" "3000"

echo ""
echo "📋 Service URLs:"
echo "================"
echo "Frontend:        http://localhost:3000"
echo "API Gateway:     http://localhost:8000"
echo "User Service:    http://localhost:8001"
echo "Transaction:     http://localhost:8002"
echo "Account:         http://localhost:8003"
echo "Analytics:       http://localhost:8004"
echo "File Service:    http://localhost:8005"
echo "Notification:    http://localhost:8006"

echo ""
echo "📚 API Documentation:"
echo "===================="
echo "API Gateway:     http://localhost:8000/docs"
echo "User Service:    http://localhost:8001/docs"
echo "Transaction:     http://localhost:8002/docs"
echo "Account:         http://localhost:8003/docs"
echo "Analytics:       http://localhost:8004/docs"
echo "File Service:    http://localhost:8005/docs"
echo "Notification:    http://localhost:8006/docs"

echo ""
echo "🐳 Docker Status:"
echo "================"
docker-compose -f docker-compose.services.yml ps
