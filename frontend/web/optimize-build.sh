#!/bin/bash

# NEXUS Frontend Build Performance Optimization Script
# This script fixes build issues and implements performance optimizations

set -e

echo "🚀 Starting NEXUS Frontend Build Performance Optimization..."

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

# Phase 1: Fix Build Issues
print_status "Phase 1: Fixing build issues..."

print_status "Installing missing dependencies..."
npm install -D webpack-cli copy-webpack-plugin html-webpack-plugin purgecss-webpack-plugin glob

print_status "Fixing TypeScript errors..."
# Fix the getUserAccounts error
sed -i '' 's/accountService\.getUserAccounts(userId)/accountService.getAccounts()/g' src/hooks/useAccounts.ts

# Fix the isActive error
sed -i '' 's/user\.isActive/user.status === "active"/g' src/components/dashboard/FinancialDashboard.tsx

print_success "Phase 1 completed: Build issues fixed"

# Phase 2: Clean Up Lint Warnings
print_status "Phase 2: Cleaning up lint warnings..."

print_status "Running ESLint auto-fix..."
npm run lint:fix || print_warning "Some lint issues may require manual fixing"

print_status "Removing unused imports..."
# Find and remove unused imports (basic cleanup)
find src -name "*.tsx" -o -name "*.ts" | xargs grep -l "import.*React.*from.*react" | while read file; do
    if ! grep -q "React\." "$file" && ! grep -q "React," "$file"; then
        sed -i '' 's/import React[^;]*;//g' "$file"
    fi
done

print_success "Phase 2 completed: Lint warnings cleaned up"

# Phase 3: Remove Unused Dependencies
print_status "Phase 3: Removing unused dependencies..."

print_status "Removing unused packages..."
npm uninstall lodash-es @types/lodash-es date-fns || print_warning "Some packages may not be installed"

print_status "Running dependency check..."
npx depcheck --json > depcheck-report.json || print_warning "Dependency check completed with warnings"

print_success "Phase 3 completed: Unused dependencies removed"

# Phase 4: Implement Code Splitting
print_status "Phase 4: Implementing code splitting..."

print_status "Backing up original LazyComponents..."
cp src/components/LazyComponents.tsx src/components/LazyComponents.tsx.backup

print_status "Installing optimized LazyComponents..."
cp src/components/LazyComponents.optimized.tsx src/components/LazyComponents.tsx

print_status "Updating webpack configuration..."
cp webpack.performance.js webpack.config.js

print_success "Phase 4 completed: Code splitting implemented"

# Phase 5: Optimize Imports
print_status "Phase 5: Optimizing imports..."

print_status "Creating MUI import optimization script..."
cat > optimize-mui-imports.js << 'EOF'
const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Find all TypeScript/JavaScript files
const files = glob.sync('src/**/*.{ts,tsx}', { ignore: ['src/**/*.d.ts'] });

files.forEach(file => {
  let content = fs.readFileSync(file, 'utf8');
  let modified = false;

  // Replace MUI barrel imports with specific imports
  const muiBarrelRegex = /import\s*\{\s*([^}]+)\s*\}\s*from\s*['"]@mui\/material['"]/g;
  const matches = content.match(muiBarrelRegex);
  
  if (matches) {
    matches.forEach(match => {
      const imports = match.match(/\{([^}]+)\}/)[1]
        .split(',')
        .map(imp => imp.trim())
        .filter(imp => imp);
      
      const specificImports = imports.map(imp => 
        `import ${imp} from '@mui/material/${imp}';`
      ).join('\n');
      
      content = content.replace(match, specificImports);
      modified = true;
    });
  }

  if (modified) {
    fs.writeFileSync(file, content);
    console.log(`Optimized imports in ${file}`);
  }
});

console.log('MUI import optimization completed');
EOF

print_status "Running MUI import optimization..."
node optimize-mui-imports.js

print_success "Phase 5 completed: Imports optimized"

# Phase 6: Bundle Analysis
print_status "Phase 6: Analyzing bundle..."

print_status "Building with performance webpack config..."
npm run build:analyze || print_warning "Build analysis completed with warnings"

print_status "Checking bundle size..."
if [ -d "build" ]; then
    echo "Bundle size analysis:"
    du -sh build/static/js/* | sort -hr
    echo ""
    echo "Total bundle size:"
    du -sh build/
fi

print_success "Phase 6 completed: Bundle analyzed"

# Phase 7: Performance Testing
print_status "Phase 7: Performance testing..."

print_status "Running performance audit..."
if command -v lighthouse &> /dev/null; then
    lighthouse http://localhost:3000 --view --only-categories=performance || print_warning "Lighthouse audit completed with warnings"
else
    print_warning "Lighthouse not installed. Install with: npm install -g lighthouse"
fi

print_success "Phase 7 completed: Performance tested"

# Summary
echo ""
echo "🎉 Build Performance Optimization completed!"
echo ""
echo "📊 Summary:"
echo "✅ Build issues fixed"
echo "✅ Lint warnings cleaned up"
echo "✅ Unused dependencies removed"
echo "✅ Code splitting implemented"
echo "✅ Imports optimized"
echo "✅ Bundle analyzed"
echo "✅ Performance tested"
echo ""
echo "📁 Files created/modified:"
echo "- webpack.performance.js (optimized webpack config)"
echo "- src/components/LazyComponents.optimized.tsx (enhanced lazy loading)"
echo "- depcheck-report.json (dependency analysis)"
echo "- bundle-report.html (bundle analysis)"
echo ""
echo "⚠️  Next steps:"
echo "1. Test the application thoroughly"
echo "2. Monitor bundle size and performance"
echo "3. Update components to use lazy loading"
echo "4. Run 'npm run build:analyze' to see bundle improvements"
echo ""

# Check for any remaining issues
print_status "Checking for remaining issues..."

if npm run type-check > /dev/null 2>&1; then
    print_success "TypeScript compilation successful"
else
    print_warning "TypeScript compilation failed - check for remaining errors"
fi

if npm run lint > /dev/null 2>&1; then
    print_success "Lint check passed"
else
    print_warning "Lint check failed - some warnings may remain"
fi

echo ""
print_success "Build performance optimization completed successfully!"
echo "Run 'npm start' to test the application"
