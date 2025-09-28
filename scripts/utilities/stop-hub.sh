#!/bin/bash

# NEXUS Platform - Hub Stop Script
# Stops all hub services gracefully

echo "🛑 Stopping NEXUS Platform Agent Communication Hub..."
echo "=================================================="

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file="logs/$service_name.pid"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null; then
            echo "🔄 Stopping $service_name (PID: $pid)..."
            kill $pid
            sleep 2

            # Force kill if still running
            if ps -p $pid > /dev/null; then
                echo "  ⚠️ Force stopping $service_name..."
                kill -9 $pid
            fi

            echo "  ✅ $service_name stopped"
        else
            echo "  ℹ️ $service_name was not running"
        fi
        rm -f "$pid_file"
    else
        echo "  ℹ️ No PID file found for $service_name"
    fi
}

# Stop all services
stop_service "Agent-Hub"
stop_service "Load-Balancer"
stop_service "Job-Queue"
stop_service "Performance-Monitor"

# Clean up any remaining processes
echo "🧹 Cleaning up remaining processes..."
pkill -f "agent-connect.js" 2>/dev/null || true
pkill -f "load-balancer.js" 2>/dev/null || true
pkill -f "job-queue.js" 2>/dev/null || true
pkill -f "performance-monitor.js" 2>/dev/null || true

echo ""
echo "✅ All services stopped successfully!"
echo "📋 Logs are available in the logs/ directory"
echo ""
