/**
 * NEXUS Platform - Site Map Component
 * Comprehensive navigation sitemap for easy access to all pages
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  Chip,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  useTheme,
  alpha
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  AccountBalance as AccountBalanceIcon,
  Receipt as ReceiptIcon,
  Analytics as AnalyticsIcon,
  AdminPanelSettings as AdminIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  Assessment as ReportsIcon,
  Login as LoginIcon,
  PersonAdd as RegisterIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  TrendingUp as TrendingUpIcon,
  Timeline as TimelineIcon,
  Business as BusinessIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Home as HomeIcon,
  AccountTree as AccountTreeIcon,
  AssessmentOutlined as AssessmentOutlinedIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface SiteMapItem {
  id: string;
  title: string;
  description: string;
  path: string;
  icon: React.ReactElement;
  category: 'main' | 'financial' | 'analytics' | 'admin' | 'user' | 'auth' | 'system';
  requiresAuth: boolean;
  badge?: string;
  children?: SiteMapItem[];
  features?: string[];
}

const SiteMap: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [expandedCategories, setExpandedCategories] = useState<{ [key: string]: boolean }>({});

  const siteMapItems: SiteMapItem[] = [
    // Main Dashboard
    {
      id: 'dashboard',
      title: 'Dashboard',
      description: 'Central command center for your financial intelligence',
      path: '/dashboard',
      icon: <DashboardIcon />,
      category: 'main',
      requiresAuth: true,
      features: [
        'Financial Health Overview',
        'Real-time Metrics',
        'Quick Actions',
        'AI Insights',
        'Recent Activity'
      ]
    },

    // Financial Management
    {
      id: 'accounts',
      title: 'Accounts',
      description: 'Manage all your financial accounts and assets',
      path: '/accounts',
      icon: <AccountBalanceIcon />,
      category: 'financial',
      requiresAuth: true,
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
      title: 'Transactions',
      description: 'View, categorize, and analyze all financial transactions',
      path: '/transactions',
      icon: <ReceiptIcon />,
      category: 'financial',
      requiresAuth: true,
      features: [
        'Transaction History',
        'Smart Categorization',
        'Search & Filter',
        'Transaction Analysis',
        'Export Capabilities'
      ]
    },
    {
      id: 'reports',
      title: 'Reports',
      description: 'Generate comprehensive financial reports and insights',
      path: '/reports',
      icon: <ReportsIcon />,
      category: 'financial',
      requiresAuth: true,
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
      title: 'Analytics',
      description: 'Advanced analytics and predictive insights',
      path: '/analytics',
      icon: <AnalyticsIcon />,
      category: 'analytics',
      requiresAuth: true,
      features: [
        'Financial Trends',
        'Spending Patterns',
        'Investment Performance',
        'Risk Analysis',
        'Predictive Modeling'
      ]
    },
    {
      id: 'performance',
      title: 'Performance',
      description: 'System performance metrics and optimization',
      path: '/analytics/performance',
      icon: <SpeedIcon />,
      category: 'analytics',
      requiresAuth: true,
      features: [
        'System Metrics',
        'Performance Monitoring',
        'Optimization Tips',
        'Resource Usage',
        'Speed Analysis'
      ]
    },
    {
      id: 'trends',
      title: 'Trends',
      description: 'Financial trends and pattern analysis',
      path: '/analytics/trends',
      icon: <TrendingUpIcon />,
      category: 'analytics',
      requiresAuth: true,
      features: [
        'Trend Analysis',
        'Pattern Recognition',
        'Market Insights',
        'Historical Data',
        'Forecasting'
      ]
    },
    {
      id: 'predictions',
      title: 'Predictions',
      description: 'AI-powered financial predictions and forecasting',
      path: '/analytics/predictions',
      icon: <TimelineIcon />,
      category: 'analytics',
      requiresAuth: true,
      features: [
        'AI Predictions',
        'Financial Forecasting',
        'Scenario Planning',
        'Risk Assessment',
        'Goal Tracking'
      ]
    },

    // Administration
    {
      id: 'admin',
      title: 'Administration',
      description: 'System administration and configuration',
      path: '/admin',
      icon: <AdminIcon />,
      category: 'admin',
      requiresAuth: true,
      badge: 'Pro',
      features: [
        'User Management',
        'System Configuration',
        'Security Settings',
        'Audit Logs',
        'Performance Monitoring'
      ]
    },

    // User Management
    {
      id: 'profile',
      title: 'Profile',
      description: 'Manage your personal profile and information',
      path: '/profile',
      icon: <PersonIcon />,
      category: 'user',
      requiresAuth: true,
      features: [
        'Personal Information',
        'Profile Settings',
        'Avatar Management',
        'Contact Details',
        'Preferences'
      ]
    },
    {
      id: 'settings',
      title: 'Settings',
      description: 'Application settings and preferences',
      path: '/settings',
      icon: <SettingsIcon />,
      category: 'user',
      requiresAuth: true,
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
      title: 'Security',
      description: 'Security settings and two-factor authentication',
      path: '/security',
      icon: <SecurityIcon />,
      category: 'user',
      requiresAuth: true,
      features: [
        'Password Management',
        'Two-Factor Authentication',
        'Login History',
        'Security Alerts',
        'Account Recovery'
      ]
    },

    // System Management
    {
      id: 'ssot',
      title: 'SSOT Manager',
      description: 'Single Source of Truth management system',
      path: '/ssot',
      icon: <AccountTreeIcon />,
      category: 'system',
      requiresAuth: true,
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
      title: 'System Monitoring',
      description: 'Real-time system monitoring and health checks',
      path: '/monitoring',
      icon: <MemoryIcon />,
      category: 'system',
      requiresAuth: true,
      features: [
        'System Health',
        'Resource Monitoring',
        'Error Tracking',
        'Performance Metrics',
        'Alert Management'
      ]
    },

    // Authentication
    {
      id: 'login',
      title: 'Login',
      description: 'Sign in to your NEXUS account',
      path: '/login',
      icon: <LoginIcon />,
      category: 'auth',
      requiresAuth: false,
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
      title: 'Register',
      description: 'Create a new NEXUS account',
      path: '/register',
      icon: <RegisterIcon />,
      category: 'auth',
      requiresAuth: false,
      features: [
        'Account Creation',
        'Email Verification',
        'Profile Setup',
        'Terms & Conditions',
        'Welcome Onboarding'
      ]
    }
  ];

  const handleCategoryToggle = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const handleItemClick = (path: string) => {
    navigate(path);
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'main': return 'primary';
      case 'financial': return 'success';
      case 'analytics': return 'info';
      case 'admin': return 'warning';
      case 'user': return 'secondary';
      case 'system': return 'error';
      case 'auth': return 'default';
      default: return 'default';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'main': return <HomeIcon />;
      case 'financial': return <AccountBalanceIcon />;
      case 'analytics': return <AnalyticsIcon />;
      case 'admin': return <AdminIcon />;
      case 'user': return <PersonIcon />;
      case 'system': return <MemoryIcon />;
      case 'auth': return <LoginIcon />;
      default: return <HomeIcon />;
    }
  };

  const groupedItems = siteMapItems.reduce((acc, item) => {
    if (!acc[item.category]) {
      acc[item.category] = [];
    }
    acc[item.category].push(item);
    return acc;
  }, {} as { [key: string]: SiteMapItem[] });

  const categoryLabels = {
    main: 'Main Dashboard',
    financial: 'Financial Management',
    analytics: 'Analytics & Intelligence',
    admin: 'Administration',
    user: 'User Management',
    system: 'System Management',
    auth: 'Authentication'
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          NEXUS Platform Sitemap
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Complete navigation guide to all platform features and pages
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {Object.entries(groupedItems).map(([category, items]) => (
          <Grid item xs={12} md={6} lg={4} key={category}>
            <Card 
              sx={{ 
                height: '100%',
                border: `2px solid ${alpha(theme.palette[getCategoryColor(category) as keyof typeof theme.palette].main || theme.palette.primary.main, 0.1)}`,
                '&:hover': {
                  borderColor: theme.palette[getCategoryColor(category) as keyof typeof theme.palette].main || theme.palette.primary.main,
                  boxShadow: theme.shadows[4]
                }
              }}
            >
              <CardContent>
                <Box 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 1, 
                    mb: 2,
                    cursor: 'pointer'
                  }}
                  onClick={() => handleCategoryToggle(category)}
                >
                  {getCategoryIcon(category)}
                  <Typography variant="h6" fontWeight="bold" sx={{ flex: 1 }}>
                    {categoryLabels[category as keyof typeof categoryLabels]}
                  </Typography>
                  <IconButton size="small">
                    {expandedCategories[category] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                </Box>

                <Collapse in={expandedCategories[category]}>
                  <List dense>
                    {items
                      .filter(item => !item.requiresAuth || user)
                      .map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                          <ListItem
                            key={item.id}
                            button
                            onClick={() => handleItemClick(item.path)}
                            sx={{
                              borderRadius: 1,
                              mb: 0.5,
                              backgroundColor: isActive ? alpha(theme.palette.primary.main, 0.1) : 'transparent',
                              '&:hover': {
                                backgroundColor: alpha(theme.palette.primary.main, 0.05)
                              }
                            }}
                          >
                            <ListItemIcon sx={{ color: isActive ? 'primary.main' : 'inherit' }}>
                              {item.icon}
                            </ListItemIcon>
                            <ListItemText
                              primary={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Typography variant="body2" fontWeight="medium">
                                    {item.title}
                                  </Typography>
                                  {item.badge && (
                                    <Chip 
                                      label={item.badge} 
                                      size="small" 
                                      color="primary" 
                                      variant="outlined"
                                    />
                                  )}
                                </Box>
                              }
                              secondary={
                                <Typography variant="caption" color="text.secondary">
                                  {item.description}
                                </Typography>
                              }
                            />
                          </ListItem>
                        );
                      })}
                  </List>
                </Collapse>

                {!expandedCategories[category] && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      {items.filter(item => !item.requiresAuth || user).length} pages available
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Quick Access Section */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom fontWeight="bold">
          Quick Access
        </Typography>
        <Grid container spacing={2}>
          {siteMapItems
            .filter(item => !item.requiresAuth || user)
            .slice(0, 6)
            .map((item) => (
              <Grid item xs={12} sm={6} md={4} key={item.id}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': {
                      boxShadow: theme.shadows[4],
                      transform: 'translateY(-2px)'
                    },
                    transition: 'all 0.2s ease-in-out'
                  }}
                  onClick={() => handleItemClick(item.path)}
                >
                  <CardActionArea>
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                        {item.icon}
                        <Typography variant="h6" fontWeight="medium">
                          {item.title}
                        </Typography>
                        {item.badge && (
                          <Chip 
                            label={item.badge} 
                            size="small" 
                            color="primary" 
                            variant="outlined"
                          />
                        )}
                      </Box>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {item.description}
                      </Typography>
                      {item.features && (
                        <Box>
                          <Typography variant="caption" fontWeight="medium" color="primary">
                            Key Features:
                          </Typography>
                          <Box sx={{ mt: 0.5 }}>
                            {item.features.slice(0, 3).map((feature, index) => (
                              <Chip
                                key={index}
                                label={feature}
                                size="small"
                                variant="outlined"
                                sx={{ mr: 0.5, mb: 0.5, fontSize: '0.7rem' }}
                              />
                            ))}
                            {item.features.length > 3 && (
                              <Typography variant="caption" color="text.secondary">
                                +{item.features.length - 3} more
                              </Typography>
                            )}
                          </Box>
                        </Box>
                      )}
                    </CardContent>
                  </CardActionArea>
                </Card>
              </Grid>
            ))}
        </Grid>
      </Box>
    </Box>
  );
};

export default SiteMap;
