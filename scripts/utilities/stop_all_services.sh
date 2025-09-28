#!/bin/bash

# NEXUS Platform - Stop All Services
# This script stops all backend services and the frontend

set -e

echo "🛑 Stopping NEXUS Platform Services..."

# Stop services
echo "🐳 Stopping services with Docker Compose..."
docker-compose -f docker-compose.services.yml down

# Clean up volumes (optional)
read -p "🗑️  Do you want to remove all data volumes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing data volumes..."
    docker-compose -f docker-compose.services.yml down -v
    echo "✅ Data volumes removed"
fi

echo "✅ All services stopped successfully"
