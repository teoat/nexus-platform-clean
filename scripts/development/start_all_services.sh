#!/bin/bash

# NEXUS Platform - Start All Services
# This script starts all backend services and the frontend

set -e

echo "🚀 Starting NEXUS Platform Services..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p data/files

# Set permissions
chmod 755 data/postgres
chmod 755 data/redis
chmod 755 data/files

# Start services
echo "🐳 Starting services with Docker Compose..."
docker-compose -f docker-compose.services.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check API Gateway
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API Gateway is healthy"
else
    echo "❌ API Gateway is not responding"
fi

# Check User Service
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ User Service is healthy"
else
    echo "❌ User Service is not responding"
fi

# Check Transaction Service
if curl -f http://localhost:8002/health > /dev/null 2>&1; then
    echo "✅ Transaction Service is healthy"
else
    echo "❌ Transaction Service is not responding"
fi

# Check Account Service
if curl -f http://localhost:8003/health > /dev/null 2>&1; then
    echo "✅ Account Service is healthy"
else
    echo "❌ Account Service is not responding"
fi

# Check Analytics Service
if curl -f http://localhost:8004/health > /dev/null 2>&1; then
    echo "✅ Analytics Service is healthy"
else
    echo "❌ Analytics Service is not responding"
fi

# Check File Service
if curl -f http://localhost:8005/health > /dev/null 2>&1; then
    echo "✅ File Service is healthy"
else
    echo "❌ File Service is not responding"
fi

# Check Notification Service
if curl -f http://localhost:8006/health > /dev/null 2>&1; then
    echo "✅ Notification Service is healthy"
else
    echo "❌ Notification Service is not responding"
fi

# Check Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 NEXUS Platform is now running!"
echo ""
echo "📊 Service URLs:"
echo "   Frontend:        http://localhost:3000"
echo "   API Gateway:     http://localhost:8000"
echo "   User Service:    http://localhost:8001"
echo "   Transaction:     http://localhost:8002"
echo "   Account:         http://localhost:8003"
echo "   Analytics:       http://localhost:8004"
echo "   File Service:    http://localhost:8005"
echo "   Notification:    http://localhost:8006"
echo ""
echo "📚 API Documentation:"
echo "   API Gateway:     http://localhost:8000/docs"
echo "   User Service:    http://localhost:8001/docs"
echo "   Transaction:     http://localhost:8002/docs"
echo "   Account:         http://localhost:8003/docs"
echo "   Analytics:       http://localhost:8004/docs"
echo "   File Service:    http://localhost:8005/docs"
echo "   Notification:    http://localhost:8006/docs"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose -f docker-compose.services.yml down"
echo ""
echo "📋 To view logs:"
echo "   docker-compose -f docker-compose.services.yml logs -f"
