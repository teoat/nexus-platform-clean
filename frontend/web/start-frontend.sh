#!/bin/bash

# NEXUS Frontend Startup Script
echo "🚀 Starting NEXUS Frontend..."

# Check if we're in the correct directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the frontend/web directory."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install dependencies"
        exit 1
    fi
fi

# Start the development server
echo "🌐 Starting development server on http://localhost:3000"
echo "📱 Agent Dashboard: http://localhost:3000/agent-dashboard"
echo "💰 Financial Dashboard: http://localhost:3000/dashboard"
echo "🔐 Login: http://localhost:3000/login"
echo "📝 Register: http://localhost:3000/register"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm start
