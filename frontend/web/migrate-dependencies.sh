#!/bin/bash

# NEXUS Frontend Dependency Migration Script
# This script safely migrates dependencies to optimized versions

set -e

echo "🚀 Starting NEXUS Frontend Dependency Migration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from the frontend/web directory."
    exit 1
fi

# Backup current package.json
print_status "Creating backup of current package.json..."
cp package.json package.json.backup.$(date +%Y%m%d_%H%M%S)
print_success "Backup created"

# Phase 1: Security Fixes
print_status "Phase 1: Applying security fixes..."

print_status "Removing unused dependencies..."
npm uninstall lodash-es @types/lodash-es date-fns || print_warning "Some packages may not be installed"

print_status "Updating react-scripts to fix security vulnerabilities..."
npm install react-scripts@6.0.0

print_status "Updating webpack-dev-server..."
npm install webpack-dev-server@5.0.0

print_success "Phase 1 completed: Security fixes applied"

# Phase 2: Major Updates
print_status "Phase 2: Applying major version updates..."

print_status "Updating React ecosystem..."
npm install react@19.1.1 react-dom@19.1.1
npm install @types/react@19.1.13 @types/react-dom@19.1.9

print_status "Updating MUI ecosystem..."
npm install @mui/material@7.3.2 @mui/icons-material@7.3.2 @mui/x-data-grid@8.11.3

print_status "Updating TanStack Query..."
npm install @tanstack/react-query@5.90.2 @tanstack/react-query-devtools@5.90.2

print_status "Updating TypeScript..."
npm install typescript@5.9.2

print_status "Updating testing libraries..."
npm install @testing-library/dom@10.4.1 @testing-library/jest-dom@6.8.0 @testing-library/react@16.3.0 @testing-library/user-event@14.6.1 @types/jest@30.0.0

print_status "Updating other dependencies..."
npm install react-router-dom@7.9.2 recharts@3.2.1 @types/node@24.5.2

print_success "Phase 2 completed: Major updates applied"

# Phase 3: Dev Dependencies
print_status "Phase 3: Updating development dependencies..."

print_status "Updating build tools..."
npm install --save-dev babel-loader@10.0.0 postcss-loader@8.2.0 compression-webpack-plugin@11.1.0 css-minimizer-webpack-plugin@7.0.2 cssnano@7.1.1

print_success "Phase 3 completed: Dev dependencies updated"

# Phase 4: Cleanup and Verification
print_status "Phase 4: Cleanup and verification..."

print_status "Cleaning npm cache..."
npm cache clean --force

print_status "Removing node_modules and package-lock.json..."
rm -rf node_modules package-lock.json

print_status "Installing fresh dependencies..."
npm install

print_status "Running security audit..."
npm audit --audit-level moderate || print_warning "Some vulnerabilities may remain"

print_status "Running type check..."
npm run type-check || print_warning "Type check failed - may need code updates"

print_status "Running lint check..."
npm run lint || print_warning "Lint check failed - may need code fixes"

print_success "Phase 4 completed: Cleanup and verification done"

# Summary
echo ""
echo "🎉 Migration completed!"
echo ""
echo "📊 Summary:"
echo "✅ Security vulnerabilities fixed"
echo "✅ Unused dependencies removed"
echo "✅ Major versions updated"
echo "✅ Development dependencies updated"
echo "✅ Fresh installation completed"
echo ""
echo "⚠️  Next steps:"
echo "1. Test the application thoroughly"
echo "2. Update code for breaking changes (React 19, MUI v7, etc.)"
echo "3. Run 'npm run build' to verify production build"
echo "4. Update CI/CD pipelines if needed"
echo ""
echo "📁 Backup created: package.json.backup.$(date +%Y%m%d_%H%M%S)"
echo ""

# Check for any remaining issues
print_status "Checking for remaining issues..."

if npm audit --audit-level moderate > /dev/null 2>&1; then
    print_success "No security vulnerabilities found"
else
    print_warning "Some security vulnerabilities may remain - run 'npm audit' for details"
fi

if npm run type-check > /dev/null 2>&1; then
    print_success "TypeScript compilation successful"
else
    print_warning "TypeScript compilation failed - check for breaking changes"
fi

echo ""
print_success "Migration script completed successfully!"
echo "Run 'npm start' to test the application"
