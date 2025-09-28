/**
 * NEXUS Platform - Centralized Routing Registry (SSOT)
 * Single source of truth for all application routes
 */

export interface RouteConfig {
  id: string;
  path: string;
  title: string;
  description: string;
  category: 'main' | 'financial' | 'analytics' | 'admin' | 'user' | 'auth' | 'system' | 'forensic';
  requiresAuth: boolean;
  component: string;
  icon?: string;
  badge?: string;
  parent?: string;
  children?: string[];
  features?: string[];
  metadata?: {
    seo?: {
      title?: string;
      description?: string;
      keywords?: string[];
    };
    permissions?: string[];
    roles?: string[];
  };
}

export interface APIRouteConfig {
  id: string;
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  title: string;
  description: string;
  category: 'forensic' | 'financial' | 'analytics' | 'auth' | 'system' | 'admin';
  requiresAuth: boolean;
  parameters?: {
    query?: Record<string, { type: string; required: boolean; description: string }>;
    body?: Record<string, { type: string; required: boolean; description: string }>;
    path?: Record<string, { type: string; required: boolean; description: string }>;
  };
  responses?: Record<number, { description: string; schema?: any }>;
  examples?: {
    request?: any;
    response?: any;
  };
}

// Frontend Routes Registry
export const FRONTEND_ROUTES: RouteConfig[] = [
  // Main Dashboard
  {
    id: 'dashboard',
    path: '/dashboard',
    title: 'Dashboard',
    description: 'Central command center for financial intelligence',
    category: 'main',
    requiresAuth: true,
    component: 'Dashboard',
    icon: 'Dashboard',
    features: [
      'Financial Health Overview',
      'Real-time Metrics',
      'Quick Actions',
      'AI Insights',
      'Recent Activity'
    ],
    metadata: {
      seo: {
        title: 'NEXUS Dashboard - Financial Intelligence Platform',
        description: 'Comprehensive financial dashboard with real-time analytics and AI insights',
        keywords: ['dashboard', 'financial', 'analytics', 'intelligence', 'nexus']
      }
    }
  },

  // Financial Management
  {
    id: 'accounts',
    path: '/accounts',
    title: 'Accounts',
    description: 'Manage all financial accounts and assets',
    category: 'financial',
    requiresAuth: true,
    component: 'Accounts',
    icon: 'AccountBalance',
    features: [
      'Bank Account Management',
      'Investment Tracking',
      'Asset Portfolio',
      'Account Aggregation',
      'Balance Monitoring'
    ]
  },
  {
    id: 'transactions',
    path: '/transactions',
    title: 'Transactions',
    description: 'View, categorize, and analyze all financial transactions',
    category: 'financial',
    requiresAuth: true,
    component: 'Transactions',
    icon: 'Receipt',
    features: [
      'Transaction History',
      'Smart Categorization',
      'Search & Filter',
      'Transaction Analysis',
      'Export Capabilities'
    ]
  },
  {
    id: 'reconciliation',
    path: '/reconciliation',
    title: 'Bank Reconciliation',
    description: 'Automated bank statement reconciliation and matching',
    category: 'forensic',
    requiresAuth: true,
    component: 'Reconciliation',
    icon: 'AccountBalance',
    badge: 'Forensic',
    features: [
      'Automated Matching',
      'Discrepancy Detection',
      'Audit Trail',
      'Exception Handling',
      'Compliance Reporting'
    ]
  },
  {
    id: 'fraud-detection',
    path: '/fraud-detection',
    title: 'Fraud Detection',
    description: 'AI-powered fraud detection and analysis',
    category: 'forensic',
    requiresAuth: true,
    component: 'FraudDetection',
    icon: 'Security',
    badge: 'AI',
    features: [
      'Pattern Recognition',
      'Anomaly Detection',
      'Risk Scoring',
      'Alert Management',
      'Investigation Tools'
    ]
  },
  {
    id: 'reports',
    path: '/reports',
    title: 'Reports',
    description: 'Generate comprehensive financial reports and insights',
    category: 'financial',
    requiresAuth: true,
    component: 'Reports',
    icon: 'Assessment',
    features: [
      'Financial Statements',
      'Custom Reports',
      'Tax Reports',
      'Performance Analysis',
      'PDF Export'
    ]
  },

  // Analytics & Intelligence
  {
    id: 'analytics',
    path: '/analytics',
    title: 'Analytics',
    description: 'Advanced analytics and predictive insights',
    category: 'analytics',
    requiresAuth: true,
    component: 'Analytics',
    icon: 'Analytics',
    features: [
      'Financial Trends',
      'Spending Patterns',
      'Investment Performance',
      'Risk Analysis',
      'Predictive Modeling'
    ]
  },
  {
    id: 'ai-insights',
    path: '/ai-insights',
    title: 'AI Insights',
    description: 'Explainable AI insights and recommendations',
    category: 'analytics',
    requiresAuth: true,
    component: 'AIInsights',
    icon: 'Psychology',
    badge: 'AI',
    features: [
      'Explainable AI',
      'Smart Recommendations',
      'Pattern Analysis',
      'Predictive Insights',
      'Natural Language Queries'
    ]
  },
  {
    id: 'risk-assessment',
    path: '/risk-assessment',
    title: 'Risk Assessment',
    description: 'Comprehensive risk analysis and mitigation',
    category: 'forensic',
    requiresAuth: true,
    component: 'RiskAssessment',
    icon: 'Security',
    badge: 'Forensic',
    features: [
      'Risk Scoring',
      'Threat Analysis',
      'Mitigation Strategies',
      'Compliance Checks',
      'Risk Monitoring'
    ]
  },

  // System Management
  {
    id: 'ssot',
    path: '/ssot',
    title: 'SSOT Manager',
    description: 'Single source of truth management system',
    category: 'system',
    requiresAuth: true,
    component: 'SSOTManager',
    icon: 'AccountTree',
    features: [
      'Data Management',
      'Alias Configuration',
      'Cache Management',
      'Data Validation',
      'Sync Monitoring'
    ]
  },
  {
    id: 'monitoring',
    path: '/monitoring',
    title: 'System Monitoring',
    description: 'Real-time system monitoring and health checks',
    category: 'system',
    requiresAuth: true,
    component: 'SystemDashboard',
    icon: 'Memory',
    features: [
      'System Health',
      'Resource Monitoring',
      'Error Tracking',
      'Performance Metrics',
      'Alert Management'
    ]
  },
  {
    id: 'audit-logs',
    path: '/audit-logs',
    title: 'Audit Logs',
    description: 'Comprehensive audit trail and logging',
    category: 'forensic',
    requiresAuth: true,
    component: 'AuditLogs',
    icon: 'History',
    badge: 'Forensic',
    features: [
      'Activity Logging',
      'Change Tracking',
      'Compliance Reports',
      'Forensic Analysis',
      'Data Integrity'
    ]
  },

  // User Management
  {
    id: 'profile',
    path: '/profile',
    title: 'Profile',
    description: 'Manage your personal profile and information',
    category: 'user',
    requiresAuth: true,
    component: 'Profile',
    icon: 'Person',
    features: [
      'Personal Information',
      'Profile Picture',
      'Contact Details',
      'Preferences',
      'Privacy Settings'
    ]
  },
  {
    id: 'settings',
    path: '/settings',
    title: 'Settings',
    description: 'Application settings and preferences',
    category: 'user',
    requiresAuth: true,
    component: 'Settings',
    icon: 'Settings',
    features: [
      'General Settings',
      'Notification Preferences',
      'Display Options',
      'Privacy Settings',
      'Data Management'
    ]
  },
  {
    id: 'security',
    path: '/security',
    title: 'Security',
    description: 'Security settings and two-factor authentication',
    category: 'user',
    requiresAuth: true,
    component: 'Security',
    icon: 'Security',
    features: [
      'Password Management',
      'Two-Factor Authentication',
      'Login History',
      'Security Alerts',
      'Account Recovery'
    ]
  },

  // Administration
  {
    id: 'admin',
    path: '/admin',
    title: 'Administration',
    description: 'System administration and configuration',
    category: 'admin',
    requiresAuth: true,
    component: 'Admin',
    icon: 'AdminPanelSettings',
    badge: 'Pro',
    features: [
      'User Management',
      'System Configuration',
      'Security Settings',
      'Audit Logs',
      'Performance Monitoring'
    ]
  },

  // Authentication
  {
    id: 'login',
    path: '/login',
    title: 'Login',
    description: 'Sign in to your NEXUS account',
    category: 'auth',
    requiresAuth: false,
    component: 'LoginPage',
    icon: 'Login',
    features: [
      'Secure Authentication',
      'Remember Me',
      'Password Recovery',
      'Social Login',
      'Multi-Factor Auth'
    ]
  },
  {
    id: 'register',
    path: '/register',
    title: 'Register',
    description: 'Create a new NEXUS account',
    category: 'auth',
    requiresAuth: false,
    component: 'RegisterPage',
    icon: 'PersonAdd',
    features: [
      'Account Creation',
      'Email Verification',
      'Profile Setup',
      'Terms & Conditions',
      'Welcome Onboarding'
    ]
  }
];

// API Routes Registry
export const API_ROUTES: APIRouteConfig[] = [
  // Forensic Analysis APIs
  {
    id: 'forensic-analysis',
    path: '/api/v1/forensic/analyze',
    method: 'POST',
    title: 'Forensic Analysis',
    description: 'Perform comprehensive forensic analysis on financial data',
    category: 'forensic',
    requiresAuth: true,
    parameters: {
      body: {
        data: { type: 'object', required: true, description: 'Financial data to analyze' },
        analysis_type: { type: 'string', required: true, description: 'Type of analysis to perform' },
        options: { type: 'object', required: false, description: 'Analysis configuration options' }
      }
    },
    responses: {
      200: { description: 'Analysis completed successfully' },
      400: { description: 'Invalid input data' },
      401: { description: 'Authentication required' },
      500: { description: 'Analysis failed' }
    }
  },
  {
    id: 'fraud-detection',
    path: '/api/v1/forensic/fraud-detection',
    method: 'POST',
    title: 'Fraud Detection',
    description: 'Detect potential fraud patterns in financial data',
    category: 'forensic',
    requiresAuth: true,
    parameters: {
      body: {
        transactions: { type: 'array', required: true, description: 'Transaction data to analyze' },
        rules: { type: 'array', required: false, description: 'Custom fraud detection rules' },
        sensitivity: { type: 'number', required: false, description: 'Detection sensitivity level' }
      }
    }
  },
  {
    id: 'reconciliation',
    path: '/api/v1/forensic/reconciliation',
    method: 'POST',
    title: 'Bank Reconciliation',
    description: 'Reconcile bank statements with internal records',
    category: 'forensic',
    requiresAuth: true,
    parameters: {
      body: {
        bank_statement: { type: 'object', required: true, description: 'Bank statement data' },
        internal_records: { type: 'array', required: true, description: 'Internal transaction records' },
        matching_rules: { type: 'object', required: false, description: 'Custom matching rules' }
      }
    }
  },

  // Financial APIs
  {
    id: 'accounts',
    path: '/api/v1/financial/accounts',
    method: 'GET',
    title: 'Get Accounts',
    description: 'Retrieve all financial accounts',
    category: 'financial',
    requiresAuth: true,
    parameters: {
      query: {
        type: { type: 'string', required: false, description: 'Account type filter' },
        status: { type: 'string', required: false, description: 'Account status filter' },
        limit: { type: 'number', required: false, description: 'Number of results to return' },
        offset: { type: 'number', required: false, description: 'Number of results to skip' }
      }
    }
  },
  {
    id: 'transactions',
    path: '/api/v1/financial/transactions',
    method: 'GET',
    title: 'Get Transactions',
    description: 'Retrieve financial transactions with filtering',
    category: 'financial',
    requiresAuth: true,
    parameters: {
      query: {
        account_id: { type: 'string', required: false, description: 'Filter by account ID' },
        date_from: { type: 'string', required: false, description: 'Start date filter' },
        date_to: { type: 'string', required: false, description: 'End date filter' },
        category: { type: 'string', required: false, description: 'Transaction category filter' },
        amount_min: { type: 'number', required: false, description: 'Minimum amount filter' },
        amount_max: { type: 'number', required: false, description: 'Maximum amount filter' }
      }
    }
  },

  // Analytics APIs
  {
    id: 'analytics-trends',
    path: '/api/v1/analytics/trends',
    method: 'GET',
    title: 'Get Trends',
    description: 'Retrieve financial trend analysis',
    category: 'analytics',
    requiresAuth: true,
    parameters: {
      query: {
        period: { type: 'string', required: true, description: 'Analysis period' },
        metric: { type: 'string', required: true, description: 'Trend metric to analyze' },
        granularity: { type: 'string', required: false, description: 'Data granularity' }
      }
    }
  },
  {
    id: 'ai-insights',
    path: '/api/v1/analytics/ai-insights',
    method: 'POST',
    title: 'Get AI Insights',
    description: 'Generate AI-powered insights and recommendations',
    category: 'analytics',
    requiresAuth: true,
    parameters: {
      body: {
        query: { type: 'string', required: true, description: 'Natural language query' },
        context: { type: 'object', required: false, description: 'Additional context data' },
        options: { type: 'object', required: false, description: 'AI analysis options' }
      }
    }
  },

  // System APIs
  {
    id: 'system-health',
    path: '/api/v1/system/health',
    method: 'GET',
    title: 'System Health',
    description: 'Get system health status and metrics',
    category: 'system',
    requiresAuth: true
  },
  {
    id: 'audit-logs',
    path: '/api/v1/system/audit-logs',
    method: 'GET',
    title: 'Get Audit Logs',
    description: 'Retrieve system audit logs',
    category: 'system',
    requiresAuth: true,
    parameters: {
      query: {
        user_id: { type: 'string', required: false, description: 'Filter by user ID' },
        action: { type: 'string', required: false, description: 'Filter by action type' },
        date_from: { type: 'string', required: false, description: 'Start date filter' },
        date_to: { type: 'string', required: false, description: 'End date filter' }
      }
    }
  }
];

// Route validation and helper functions
export const validateRoute = (path: string): boolean => {
  return FRONTEND_ROUTES.some(route => route.path === path);
};

export const getRouteByPath = (path: string): RouteConfig | undefined => {
  return FRONTEND_ROUTES.find(route => route.path === path);
};

export const getRoutesByCategory = (category: string): RouteConfig[] => {
  return FRONTEND_ROUTES.filter(route => route.category === category);
};

export const getAPIRouteByPath = (path: string, method: string): APIRouteConfig | undefined => {
  return API_ROUTES.find(route => route.path === path && route.method === method);
};

export const generateSitemap = (): any => {
  return {
    frontend: FRONTEND_ROUTES.map(route => ({
      id: route.id,
      path: route.path,
      title: route.title,
      description: route.description,
      category: route.category,
      requiresAuth: route.requiresAuth
    })),
    api: API_ROUTES.map(route => ({
      id: route.id,
      path: route.path,
      method: route.method,
      title: route.title,
      description: route.description,
      category: route.category,
      requiresAuth: route.requiresAuth
    }))
  };
};

export const generateSitemapXML = (): string => {
  const baseUrl = process.env.REACT_APP_BASE_URL || 'https://nexus-platform.com';
  
  const frontendUrls = FRONTEND_ROUTES
    .filter(route => !route.requiresAuth) // Only public routes for SEO
    .map(route => `  <url>
    <loc>${baseUrl}${route.path}</loc>
    <lastmod>${new Date().toISOString()}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>`);

  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${frontendUrls.join('\n')}
</urlset>`;
};

export default {
  FRONTEND_ROUTES,
  API_ROUTES,
  validateRoute,
  getRouteByPath,
  getRoutesByCategory,
  getAPIRouteByPath,
  generateSitemap,
  generateSitemapXML
};
