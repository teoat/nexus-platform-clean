#!/bin/bash

# NEXUS Platform - Quick Deploy Script
set -e

echo "🚀 NEXUS Platform - Quick Deploy"
echo "================================"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Check health
echo "🏥 Checking service health..."

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend: http://localhost:8000"
else
    echo "❌ Backend not responding"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend: http://localhost:3000"
else
    echo "❌ Frontend not responding"
fi

echo ""
echo "🎉 Quick deploy complete!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
