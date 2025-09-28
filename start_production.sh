#!/bin/bash
# NEXUS Platform Production Startup Script

echo "🚀 Starting NEXUS Platform Production..."

# Set environment
export NODE_ENV=production
export PYTHONPATH=/Users/Arief/Desktop/Nexus

# Start Redis
echo "📦 Starting Redis..."
redis-server --daemonize yes

# Start Backend
echo "🔧 Starting Backend..."
cd /Users/Arief/Desktop/Nexus
python3 -m uvicorn backend.main_unified:app --host 0.0.0.0 --port 8000 --workers 4 &

# Start Frontend
echo "🌐 Starting Frontend..."
cd /Users/Arief/Desktop/Nexus/frontend/web
npm start &

echo "✅ NEXUS Platform Production started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
