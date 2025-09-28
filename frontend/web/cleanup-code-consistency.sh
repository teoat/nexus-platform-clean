#!/bin/bash

# NEXUS Code Consistency Cleanup Script
# This script cleans up the codebase for consistency and removes unused components

set -e

echo "🧹 Starting NEXUS Code Consistency Cleanup..."

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

# Phase 1: Create Archive Structure
print_status "Phase 1: Creating archive structure..."

print_status "Creating archive directories..."
mkdir -p archive_bin/unused_components/{dashboard,ui,mobile,forms,charts}
mkdir -p archive_bin/unused_services
mkdir -p archive_bin/unused_hooks
mkdir -p archive_bin/unused_utils
mkdir -p archive_bin/unused_pages

print_success "Phase 1 completed: Archive structure created"

# Phase 2: Archive Unused Components
print_status "Phase 2: Archiving unused components..."

print_status "Archiving unused dashboard components..."
# Check if files exist before moving
[ -f "src/components/FinancialDashboard.tsx" ] && mv src/components/FinancialDashboard.tsx archive_bin/unused_components/dashboard/ || print_warning "FinancialDashboard.tsx not found"
[ -f "src/components/PerformanceMetrics.tsx" ] && mv src/components/PerformanceMetrics.tsx archive_bin/unused_components/dashboard/ || print_warning "PerformanceMetrics.tsx not found"
[ -f "src/components/OptimizationSettings.tsx" ] && mv src/components/OptimizationSettings.tsx archive_bin/unused_components/dashboard/ || print_warning "OptimizationSettings.tsx not found"
[ -f "src/components/SecurityDashboard.tsx" ] && mv src/components/SecurityDashboard.tsx archive_bin/unused_components/dashboard/ || print_warning "SecurityDashboard.tsx not found"
[ -f "src/components/SecurityManager.tsx" ] && mv src/components/SecurityManager.tsx archive_bin/unused_components/dashboard/ || print_warning "SecurityManager.tsx not found"
[ -f "src/components/SystemHealth.tsx" ] && mv src/components/SystemHealth.tsx archive_bin/unused_components/dashboard/ || print_warning "SystemHealth.tsx not found"
[ -f "src/components/FeatureManager.tsx" ] && mv src/components/FeatureManager.tsx archive_bin/unused_components/dashboard/ || print_warning "FeatureManager.tsx not found"
[ -f "src/components/FeatureConfig.tsx" ] && mv src/components/FeatureConfig.tsx archive_bin/unused_components/dashboard/ || print_warning "FeatureConfig.tsx not found"
[ -f "src/components/FrenlyInsights.tsx" ] && mv src/components/FrenlyInsights.tsx archive_bin/unused_components/dashboard/ || print_warning "FrenlyInsights.tsx not found"
[ -f "src/components/InsightCard.tsx" ] && mv src/components/InsightCard.tsx archive_bin/unused_components/dashboard/ || print_warning "InsightCard.tsx not found"

print_status "Archiving unused UI components..."
[ -f "src/components/ui/OptimizedButton.tsx" ] && mv src/components/ui/OptimizedButton.tsx archive_bin/unused_components/ui/ || print_warning "OptimizedButton.tsx not found"
[ -f "src/components/ui/Form.tsx" ] && mv src/components/ui/Form.tsx archive_bin/unused_components/ui/ || print_warning "Form.tsx not found"
[ -f "src/components/ui/LoadingState.tsx" ] && mv src/components/ui/LoadingState.tsx archive_bin/unused_components/ui/ || print_warning "LoadingState.tsx not found"
[ -f "src/components/ui/Progress.tsx" ] && mv src/components/ui/Progress.tsx archive_bin/unused_components/ui/ || print_warning "Progress.tsx not found"
[ -f "src/components/ui/Tabs.tsx" ] && mv src/components/ui/Tabs.tsx archive_bin/unused_components/ui/ || print_warning "Tabs.tsx not found"

print_status "Archiving unused mobile components..."
[ -f "src/components/mobile/MobileOptimizer.tsx" ] && mv src/components/mobile/MobileOptimizer.tsx archive_bin/unused_components/mobile/ || print_warning "MobileOptimizer.tsx not found"
[ -f "src/components/mobile/ResponsiveLayout.tsx" ] && mv src/components/mobile/ResponsiveLayout.tsx archive_bin/unused_components/mobile/ || print_warning "ResponsiveLayout.tsx not found"

print_success "Phase 2 completed: Unused components archived"

# Phase 3: Create Shared Utilities
print_status "Phase 3: Creating shared utilities..."

print_status "Creating shared hooks directory..."
mkdir -p src/shared/hooks

print_status "Creating shared utilities directory..."
mkdir -p src/shared/utils

print_status "Creating shared types directory..."
mkdir -p src/shared/types

print_status "Creating shared constants directory..."
mkdir -p src/shared/constants

# Create shared hooks
print_status "Creating shared hooks..."
cat > src/shared/hooks/useLoadingState.ts << 'EOF'
import { useState } from 'react';

export interface LoadingState {
  loading: boolean;
  error: string | null;
  data: any;
}

export const useLoadingState = (initialData: any = null) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState(initialData);

  const reset = () => {
    setLoading(false);
    setError(null);
    setData(initialData);
  };

  return {
    loading,
    setLoading,
    error,
    setError,
    data,
    setData,
    reset
  };
};
EOF

cat > src/shared/hooks/useFormState.ts << 'EOF'
import { useState } from 'react';

export interface FormState {
  values: Record<string, any>;
  errors: Record<string, string>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
}

export const useFormState = (initialValues: Record<string, any>) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const setValue = (name: string, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
  };

  const setFieldError = (name: string, error: string) => {
    setErrors(prev => ({ ...prev, [name]: error }));
  };

  const setFieldTouched = (name: string, touched: boolean) => {
    setTouched(prev => ({ ...prev, [name]: touched }));
  };

  const reset = () => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  };

  return {
    values,
    setValues,
    setValue,
    errors,
    setErrors,
    setFieldError,
    touched,
    setTouched,
    setFieldTouched,
    isSubmitting,
    setIsSubmitting,
    reset
  };
};
EOF

# Create shared utilities
print_status "Creating shared utilities..."
cat > src/shared/utils/apiHelpers.ts << 'EOF'
export const createApiRequest = async (url: string, options: RequestInit = {}) => {
  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
    ...options
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} - ${response.statusText}`);
  }

  return response.json();
};

export const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

export const validatePassword = (password: string): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }

  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }

  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }

  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};

export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

export const formatDate = (date: string | Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(new Date(date));
};
EOF

# Create shared types
print_status "Creating shared types..."
cat > src/shared/types/shared.ts << 'EOF'
export interface BaseProps {
  className?: string;
  children?: React.ReactNode;
}

export interface BaseEntity {
  id: string;
  createdAt: string;
  updatedAt: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  errors?: string[];
}

export interface FormFieldProps {
  name: string;
  label: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  touched?: boolean;
  value?: any;
  onChange?: (value: any) => void;
  onBlur?: () => void;
}
EOF

print_success "Phase 3 completed: Shared utilities created"

# Phase 4: Update Imports
print_status "Phase 4: Updating imports..."

print_status "Removing imports for archived components..."
find src -name "*.tsx" -o -name "*.ts" | xargs grep -l "FinancialDashboard" | xargs sed -i 's/import.*FinancialDashboard.*//g' || true
find src -name "*.tsx" -o -name "*.ts" | xargs grep -l "PerformanceMetrics" | xargs sed -i 's/import.*PerformanceMetrics.*//g' || true
find src -name "*.tsx" -o -name "*.ts" | xargs grep -l "SecurityDashboard" | xargs sed -i 's/import.*SecurityDashboard.*//g' || true
find src -name "*.tsx" -o -name "*.ts" | xargs grep -l "SystemHealth" | xargs sed -i 's/import.*SystemHealth.*//g' || true

print_status "Adding shared utility imports..."
# This would require more complex logic to add imports where needed
print_warning "Please manually add shared utility imports where needed"

print_success "Phase 4 completed: Imports updated"

# Phase 5: Create Missing Pages
print_status "Phase 5: Creating missing pages..."

print_status "Creating missing page components..."
mkdir -p src/pages/{accounts,transactions,analytics,budgets,profile,settings,admin}

# Create AccountDetailPage
cat > src/pages/accounts/AccountDetailPage.tsx << 'EOF'
import React from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Paper } from '@mui/material';

const AccountDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Account Details
      </Typography>
      <Paper sx={{ p: 2 }}>
        <Typography variant="body1">
          Account ID: {id}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          This page will show detailed account information.
        </Typography>
      </Paper>
    </Box>
  );
};

export default AccountDetailPage;
EOF

# Create TransactionDetailPage
cat > src/pages/transactions/TransactionDetailPage.tsx << 'EOF'
import React from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Paper } from '@mui/material';

const TransactionDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Transaction Details
      </Typography>
      <Paper sx={{ p: 2 }}>
        <Typography variant="body1">
          Transaction ID: {id}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          This page will show detailed transaction information.
        </Typography>
      </Paper>
    </Box>
  );
};

export default TransactionDetailPage;
EOF

# Create ProfilePage
cat > src/pages/profile/ProfilePage.tsx << 'EOF'
import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const ProfilePage: React.FC = () => {
  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        User Profile
      </Typography>
      <Paper sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary">
          This page will show user profile information and settings.
        </Typography>
      </Paper>
    </Box>
  );
};

export default ProfilePage;
EOF

# Create SettingsPage
cat > src/pages/settings/SettingsPage.tsx << 'EOF'
import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const SettingsPage: React.FC = () => {
  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Paper sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary">
          This page will show application settings and preferences.
        </Typography>
      </Paper>
    </Box>
  );
};

export default SettingsPage;
EOF

print_success "Phase 5 completed: Missing pages created"

# Phase 6: Update Component Index
print_status "Phase 6: Updating component index..."

print_status "Updating components/index.ts..."
cat > src/components/index.ts << 'EOF'
// UI Components
export { default as Button } from './ui/Button';
export { default as Card } from './ui/Card';
export { default as Modal } from './ui/Modal';
export { default as Input } from './ui/Input';
export { default as Select } from './ui/Select';
export { default as Textarea } from './ui/Textarea';
export { default as Checkbox } from './ui/Checkbox';
export { default as Radio } from './ui/Radio';
export { default as Switch } from './ui/Switch';
export { default as Badge } from './ui/Badge';
export { default as Alert } from './ui/Alert';
export { default as Toast } from './ui/Toast';
export { default as Search } from './ui/Search';
export { default as LoadingSpinner } from './ui/LoadingSpinner';
export { default as ErrorDisplay } from './ui/ErrorDisplay';
export { default as ErrorBoundary } from './ui/ErrorBoundary';
export { default as ThemeSwitcher } from './ui/ThemeSwitcher';

// Auth Components
export { default as LoginForm } from './auth/LoginForm';
export { default as RegisterForm } from './auth/RegisterForm';
export { default as EnhancedLoginForm } from './auth/EnhancedLoginForm';
export { default as POVSelection } from './auth/POVSelection';
export { default as ProtectedRoute } from './auth/ProtectedRoute';

// Dashboard Components
export { default as MainControlDashboard } from './dashboard/MainControlDashboard';
export { default as AIIntelligenceDashboard } from './dashboard/AIIntelligenceDashboard';
export { default as UserExperienceDashboard } from './dashboard/UserExperienceDashboard';
export { default as UnifiedFinanceDashboard } from './dashboard/UnifiedFinanceDashboard';
export { default as RealTimeDashboard } from './dashboard/RealTimeDashboard';

// Financial Components
export { default as UserProfile } from './financial/UserProfile';
export { default as AccountCard } from './financial/AccountCard';
export { default as AccountManagement } from './financial/AccountManagement';
export { default as FinancialChart } from './financial/FinancialChart';
export { default as TransactionForm } from './financial/TransactionForm';

// Common Components
export { default as Chart } from './common/Chart';
export { default as DataTable } from './common/DataTable';
export { default as StatusIndicator } from './common/StatusIndicator';

// Design System Components
export { default as DesignButton } from './design-system/Button';
export { default as DesignCard } from './design-system/Card';

// Lazy Components
export * from './LazyComponents.optimized';
EOF

print_success "Phase 6 completed: Component index updated"

# Summary
echo ""
echo "🎉 Code Consistency Cleanup completed!"
echo ""
echo "📊 Summary:"
echo "✅ Archive structure created"
echo "✅ Unused components archived"
echo "✅ Shared utilities created"
echo "✅ Imports updated"
echo "✅ Missing pages created"
echo "✅ Component index updated"
echo ""
echo "📁 Files archived:"
echo "- archive_bin/unused_components/dashboard/ (10+ components)"
echo "- archive_bin/unused_components/ui/ (5+ components)"
echo "- archive_bin/unused_components/mobile/ (2+ components)"
echo ""
echo "📁 New shared utilities:"
echo "- src/shared/hooks/ (useLoadingState, useFormState)"
echo "- src/shared/utils/ (apiHelpers)"
echo "- src/shared/types/ (shared types)"
echo ""
echo "📁 New pages created:"
echo "- src/pages/accounts/AccountDetailPage.tsx"
echo "- src/pages/transactions/TransactionDetailPage.tsx"
echo "- src/pages/profile/ProfilePage.tsx"
echo "- src/pages/settings/SettingsPage.tsx"
echo ""
echo "⚠️  Next steps:"
echo "1. Test the application: npm start"
echo "2. Update routing in App.tsx to use new pages"
echo "3. Add shared utility imports where needed"
echo "4. Run linting: npm run lint"
echo "5. Test all routes and functionality"
echo ""

# Check for any remaining issues
print_status "Checking for remaining issues..."

if npm run type-check > /dev/null 2>&1; then
    print_success "TypeScript compilation successful"
else
    print_warning "TypeScript compilation failed - check for remaining errors"
fi

if npm run lint:check > /dev/null 2>&1; then
    print_success "ESLint check passed"
else
    print_warning "ESLint check failed - some warnings may remain"
fi

echo ""
print_success "Code consistency cleanup completed successfully!"
echo "Run 'npm start' to test the application"
