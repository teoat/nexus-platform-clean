#!/bin/bash

# NEXUS Platform Monorepo Setup Script

set -e

echo "🚀 Setting up NEXUS Platform Monorepo..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version check passed"

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Install workspace dependencies
echo "📦 Installing workspace dependencies..."
npm run install:all

# Build shared packages
echo "🔨 Building shared packages..."
cd nexus_backend/shared
npm run build
cd ../..

# Build frontend
echo "🔨 Building frontend..."
npm run build:frontend

# Setup Python virtual environments for services
echo "🐍 Setting up Python services..."

# Transaction service
if [ -d "services/transaction_service" ]; then
    echo "Setting up transaction service..."
    cd services/transaction_service
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    cd ../..
fi

# Setup environment files
echo "📝 Setting up environment files..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "✅ Created .env file from template"
fi

# Setup git hooks
echo "🔗 Setting up git hooks..."
if [ -f "package.json" ] && grep -q "husky" package.json; then
    npx husky install
    echo "✅ Git hooks installed"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p .cache
mkdir -p .temp

echo "🎉 Monorepo setup complete!"
echo ""
echo "Available commands:"
echo "  npm run dev:frontend    - Start frontend development server"
echo "  npm run build:all       - Build all packages"
echo "  npm run test:all        - Run all tests"
echo "  npm run lint:all        - Run linting across all packages"
echo "  npm run start:services  - Start all microservices"
echo ""
echo "Happy coding! 🚀"
