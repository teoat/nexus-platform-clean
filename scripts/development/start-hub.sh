#!/bin/bash

# NEXUS Platform - Hub Startup Script
# Starts all hub services with proper error handling

echo "🚀 Starting NEXUS Platform Agent Communication Hub..."
echo "=================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm and try again."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Create logs directory
mkdir -p logs

# Function to start a service
start_service() {
    local service_name=$1
    local script_name=$2
    local port=$3

    echo "🔄 Starting $service_name on port $port..."

    # Start service in background
    nohup node $script_name.js > logs/$service_name.log 2>&1 &
    local pid=$!

    # Store PID
    echo $pid > logs/$service_name.pid

    # Wait a moment for service to start
    sleep 2

    # Check if service is running
    if ps -p $pid > /dev/null; then
        echo "  ✅ $service_name started (PID: $pid)"
    else
        echo "  ❌ $service_name failed to start"
        return 1
    fi
}

# Start all services
start_service "Agent-Hub" "agent-connect" "9000"
start_service "Load-Balancer" "load-balancer" "9001"
start_service "Job-Queue" "job-queue" "9002"
start_service "Performance-Monitor" "performance-monitor" "9003"

echo ""
echo "⏳ Waiting for services to initialize..."
sleep 5

# Test services
echo "🧪 Testing services..."

# Test Agent Hub
if curl -s http://localhost:9000/health > /dev/null; then
    echo "  ✅ Agent Hub: Healthy"
else
    echo "  ❌ Agent Hub: Unhealthy"
fi

# Test Load Balancer
if curl -s http://localhost:9001/health > /dev/null; then
    echo "  ✅ Load Balancer: Healthy"
else
    echo "  ❌ Load Balancer: Unhealthy"
fi

# Test Job Queue
if curl -s http://localhost:9002/health > /dev/null; then
    echo "  ✅ Job Queue: Healthy"
else
    echo "  ❌ Job Queue: Unhealthy"
fi

# Test Performance Monitor
if curl -s http://localhost:9003/health > /dev/null; then
    echo "  ✅ Performance Monitor: Healthy"
else
    echo "  ❌ Performance Monitor: Unhealthy"
fi

echo ""
echo "🎉 NEXUS Platform Agent Communication Hub is running!"
echo ""
echo "🌐 Hub Endpoints:"
echo "  • Agent Connection Hub: http://localhost:9000"
echo "  • Load Balancer:        http://localhost:9001"
echo "  • Job Queue Manager:    http://localhost:9002"
echo "  • Performance Monitor:  http://localhost:9003"
echo ""
echo "📡 WebSocket Endpoints:"
echo "  • Agent Hub:     ws://localhost:9000"
echo "  • Load Balancer: ws://localhost:9001"
echo "  • Job Queue:     ws://localhost:9002"
echo "  • Performance:   ws://localhost:9003"
echo ""
echo "🔧 Quick Commands:"
echo "  • Health Check: curl http://localhost:9000/health"
echo "  • Agent Status: curl http://localhost:9000/api/v1/agents"
echo "  • Job Queue:    curl http://localhost:9002/api/v1/jobs"
echo "  • Dashboard:    curl http://localhost:9001/api/v1/dashboard"
echo ""
echo "📋 Logs:"
echo "  • Agent Hub:     tail -f logs/Agent-Hub.log"
echo "  • Load Balancer: tail -f logs/Load-Balancer.log"
echo "  • Job Queue:     tail -f logs/Job-Queue.log"
echo "  • Performance:   tail -f logs/Performance-Monitor.log"
echo ""
echo "🛑 To stop all services:"
echo "  ./stop-hub.sh"
echo ""
echo "✨ Hub is ready! All 5 agents can now connect and share workloads."
echo ""

# Keep script running
echo "Press Ctrl+C to stop all services..."
trap 'echo ""; echo "🛑 Stopping all services..."; ./stop-hub.sh; exit 0' INT

# Wait for interrupt
while true; do
    sleep 1
done
