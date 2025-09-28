#!/bin/bash
# Health Check Script for Optimized NEXUS Platform
# Agent 3: DevOps & Configuration Agent Implementation

set -e

echo "🏥 Performing health checks..."

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local name=$2
    local timeout=${3:-10}
    
    echo -n "Checking $name... "
    if curl -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAILED"
        return 1
    fi
}

# Function to check container health
check_container() {
    local container=$1
    local name=$2
    
    echo -n "Checking $name container... "
    if docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAILED"
        return 1
    fi
}

# Check containers
echo "📦 Container Health Checks:"
check_container "nexus-postgres-1" "PostgreSQL"
check_container "nexus-redis-1" "Redis"
check_container "nexus-backend-1" "Backend"
check_container "nexus-frontend-1" "Frontend"
check_container "nexus-nginx-1" "Nginx"
check_container "frenly-brain-1" "Frenly AI Brain"
check_container "unified-monitoring-1" "Unified Monitoring"

echo ""
echo "🌐 Service Health Checks:"

# Check service endpoints
check_endpoint "http://localhost:8001/health" "Backend API"
check_endpoint "http://localhost:3000" "Frontend"
check_endpoint "http://localhost:9090/-/healthy" "Prometheus"
check_endpoint "http://localhost:3001" "Grafana"
check_endpoint "http://localhost:8766/health" "Frenly AI Brain"

echo ""
echo "📊 Database Connectivity:"

# Check PostgreSQL
echo -n "Checking PostgreSQL connection... "
if docker exec nexus-postgres-1 pg_isready -U nexus_admin -d nexus_production > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# Check Redis
echo -n "Checking Redis connection... "
if docker exec nexus-redis-1 redis-cli ping > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

echo ""
echo "🔍 Detailed Service Status:"
docker compose -f docker-compose.optimized.yml --env-file env.optimized ps

echo ""
echo "📈 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

echo ""
echo "✅ Health check complete!"

