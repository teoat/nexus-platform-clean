/**
 * NEXUS Platform - Main Header Component
 * Comprehensive navigation with logo, sitemap, and logical workflows
 */

import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip,
  Avatar,
  Tooltip,
  Collapse,
  useTheme,
  useMediaQuery,
  alpha
} from '@mui/material';
import {
  Menu as MenuIcon,
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
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Business as BusinessIcon,
  TrendingUp as TrendingUpIcon,
  Timeline as TimelineIcon,
  ExitToApp as ExitToAppIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon: React.ReactElement;
  description: string;
  category: 'main' | 'financial' | 'analytics' | 'admin' | 'user' | 'auth';
  requiresAuth: boolean;
  badge?: string | number;
  children?: NavigationItem[];
}

const Header: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  
  const [mobileOpen, setMobileOpen] = useState(false);
  const [expandedMenus, setExpandedMenus] = useState<{ [key: string]: boolean }>({});
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  // Navigation structure with logical workflows
  const navigationItems: NavigationItem[] = [
    // Main Dashboard
    {
      id: 'dashboard',
      label: 'Dashboard',
      path: '/dashboard',
      icon: <DashboardIcon />,
      description: 'Overview of your financial health and system status',
      category: 'main',
      requiresAuth: true
    },
    
    // Financial Management Workflow
    {
      id: 'financial',
      label: 'Financial',
      path: '/financial',
      icon: <AccountBalanceIcon />,
      description: 'Complete financial management suite',
      category: 'financial',
      requiresAuth: true,
      children: [
        {
          id: 'accounts',
          label: 'Accounts',
          path: '/accounts',
          icon: <AccountBalanceIcon />,
          description: 'Manage your bank accounts, investments, and assets',
          category: 'financial',
          requiresAuth: true
        },
        {
          id: 'transactions',
          label: 'Transactions',
          path: '/transactions',
          icon: <ReceiptIcon />,
          description: 'View and categorize all your financial transactions',
          category: 'financial',
          requiresAuth: true
        },
        {
          id: 'reports',
          label: 'Reports',
          path: '/reports',
          icon: <ReportsIcon />,
          description: 'Generate comprehensive financial reports and insights',
          category: 'financial',
          requiresAuth: true
        }
      ]
    },

    // Analytics & Intelligence Workflow
    {
      id: 'analytics',
      label: 'Analytics',
      path: '/analytics',
      icon: <AnalyticsIcon />,
      description: 'Advanced analytics and predictive insights',
      category: 'analytics',
      requiresAuth: true,
      children: [
        {
          id: 'performance',
          label: 'Performance',
          path: '/analytics/performance',
          icon: <SpeedIcon />,
          description: 'System performance metrics and optimization',
          category: 'analytics',
          requiresAuth: true
        },
        {
          id: 'trends',
          label: 'Trends',
          path: '/analytics/trends',
          icon: <TrendingUpIcon />,
          description: 'Financial trends and pattern analysis',
          category: 'analytics',
          requiresAuth: true
        },
        {
          id: 'predictions',
          label: 'Predictions',
          path: '/analytics/predictions',
          icon: <TimelineIcon />,
          description: 'AI-powered financial predictions and forecasting',
          category: 'analytics',
          requiresAuth: true
        }
      ]
    },

    // Administration Workflow
    {
      id: 'admin',
      label: 'Admin',
      path: '/admin',
      icon: <AdminIcon />,
      description: 'System administration and configuration',
      category: 'admin',
      requiresAuth: true,
      badge: 'Pro'
    },

    // User Management Workflow
    {
      id: 'user',
      label: 'Profile',
      path: '/profile',
      icon: <PersonIcon />,
      description: 'Manage your profile and preferences',
      category: 'user',
      requiresAuth: true,
      children: [
        {
          id: 'settings',
          label: 'Settings',
          path: '/settings',
          icon: <SettingsIcon />,
          description: 'Application settings and preferences',
          category: 'user',
          requiresAuth: true
        },
        {
          id: 'security',
          label: 'Security',
          path: '/security',
          icon: <SecurityIcon />,
          description: 'Security settings and two-factor authentication',
          category: 'user',
          requiresAuth: true
        }
      ]
    }
  ];

  // Authentication items
  const authItems: NavigationItem[] = [
    {
      id: 'login',
      label: 'Login',
      path: '/login',
      icon: <LoginIcon />,
      description: 'Sign in to your account',
      category: 'auth',
      requiresAuth: false
    },
    {
      id: 'register',
      label: 'Register',
      path: '/register',
      icon: <RegisterIcon />,
      description: 'Create a new account',
      category: 'auth',
      requiresAuth: false
    }
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuToggle = (itemId: string) => {
    setExpandedMenus(prev => ({
      ...prev,
      [itemId]: !prev[itemId]
    }));
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    setMobileOpen(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const renderNavigationItem = (item: NavigationItem, isMobile: boolean = false) => {
    const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedMenus[item.id];

    if (isMobile) {
      return (
        <Box key={item.id}>
          <ListItem
            button
            onClick={() => hasChildren ? handleMenuToggle(item.id) : handleNavigation(item.path)}
            sx={{
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
              primary={item.label}
              secondary={item.description}
            />
            {item.badge && (
              <Chip 
                label={item.badge} 
                size="small" 
                color="primary" 
                variant="outlined"
              />
            )}
            {hasChildren && (isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />)}
          </ListItem>
          
          {hasChildren && (
            <Collapse in={isExpanded} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                {item.children!.map((child) => (
                  <ListItem
                    key={child.id}
                    button
                    onClick={() => handleNavigation(child.path)}
                    sx={{
                      pl: 4,
                      backgroundColor: location.pathname === child.path ? alpha(theme.palette.primary.main, 0.1) : 'transparent',
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.primary.main, 0.05)
                      }
                    }}
                  >
                    <ListItemIcon sx={{ color: location.pathname === child.path ? 'primary.main' : 'inherit' }}>
                      {child.icon}
                    </ListItemIcon>
                    <ListItemText 
                      primary={child.label}
                      secondary={child.description}
                    />
                  </ListItem>
                ))}
              </List>
            </Collapse>
          )}
        </Box>
      );
    }

    return (
      <Box key={item.id} sx={{ position: 'relative' }}>
        <Button
          color="inherit"
          onClick={() => hasChildren ? handleMenuToggle(item.id) : handleNavigation(item.path)}
          startIcon={item.icon}
          endIcon={hasChildren ? (isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />) : undefined}
          sx={{
            color: isActive ? 'primary.light' : 'inherit',
            fontWeight: isActive ? 600 : 400,
            '&:hover': {
              backgroundColor: alpha(theme.palette.primary.main, 0.1)
            }
          }}
        >
          {item.label}
          {item.badge && (
            <Chip 
              label={item.badge} 
              size="small" 
              color="primary" 
              variant="outlined"
              sx={{ ml: 1, height: 20, fontSize: '0.7rem' }}
            />
          )}
        </Button>
        
        {hasChildren && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <Box
              sx={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                backgroundColor: theme.palette.background.paper,
                boxShadow: theme.shadows[4],
                borderRadius: 1,
                zIndex: 1000,
                minWidth: 300
              }}
            >
              {item.children!.map((child) => (
                <Box
                  key={child.id}
                  onClick={() => handleNavigation(child.path)}
                  sx={{
                    p: 2,
                    cursor: 'pointer',
                    borderBottom: `1px solid ${theme.palette.divider}`,
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.05)
                    },
                    '&:last-child': {
                      borderBottom: 'none'
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {child.icon}
                    <Box>
                      <Typography variant="subtitle2" fontWeight="medium">
                        {child.label}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {child.description}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              ))}
            </Box>
          </Collapse>
        )}
      </Box>
    );
  };

  const drawer = (
    <Box sx={{ width: 280 }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BusinessIcon color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h6" fontWeight="bold">
            NEXUS
          </Typography>
        </Box>
        <Typography variant="caption" color="text.secondary">
          Financial Intelligence Platform
        </Typography>
      </Box>
      
      <List sx={{ px: 1, py: 2 }}>
        {user ? (
          <>
            {navigationItems.map((item) => renderNavigationItem(item, true))}
            <Divider sx={{ my: 2 }} />
            <ListItem button onClick={handleLogout}>
              <ListItemIcon>
                <ExitToAppIcon />
              </ListItemIcon>
              <ListItemText primary="Logout" />
            </ListItem>
          </>
        ) : (
          authItems.map((item) => renderNavigationItem(item, true))
        )}
      </List>
    </Box>
  );

  return (
    <>
      <AppBar 
        position="sticky" 
        elevation={0}
        sx={{
          backgroundColor: theme.palette.mode === 'dark' ? 'grey.900' : 'white',
          borderBottom: `1px solid ${theme.palette.divider}`,
          backdropFilter: 'blur(10px)',
          backgroundImage: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)'
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 1, sm: 2 } }}>
          {/* Logo and Brand */}
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1, 
              cursor: 'pointer',
              '&:hover': { opacity: 0.8 }
            }}
            onClick={() => navigate('/')}
          >
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 'bold',
                fontSize: '1.2rem'
              }}
            >
              N
            </Box>
            <Box>
              <Typography 
                variant="h6" 
                fontWeight="bold"
                sx={{ 
                  color: theme.palette.mode === 'dark' ? 'white' : 'text.primary',
                  lineHeight: 1
                }}
              >
                NEXUS
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'text.secondary',
                  fontSize: '0.7rem',
                  lineHeight: 1
                }}
              >
                Financial Intelligence
              </Typography>
            </Box>
          </Box>

          {/* Desktop Navigation */}
          {!isMobile && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {user ? (
                <>
                  {navigationItems.map((item) => renderNavigationItem(item))}
                  
                  {/* User Profile Menu */}
                  <Tooltip title="Profile & Settings">
                    <IconButton onClick={handleProfileMenuOpen}>
                      <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                        {user.email?.charAt(0).toUpperCase()}
                      </Avatar>
                    </IconButton>
                  </Tooltip>
                  
                  <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleProfileMenuClose}
                    PaperProps={{
                      sx: { minWidth: 200 }
                    }}
                  >
                    <MenuItem onClick={() => { handleNavigation('/profile'); handleProfileMenuClose(); }}>
                      <ListItemIcon><PersonIcon /></ListItemIcon>
                      <ListItemText primary="Profile" />
                    </MenuItem>
                    <MenuItem onClick={() => { handleNavigation('/settings'); handleProfileMenuClose(); }}>
                      <ListItemIcon><SettingsIcon /></ListItemIcon>
                      <ListItemText primary="Settings" />
                    </MenuItem>
                    <Divider />
                    <MenuItem onClick={handleLogout}>
                      <ListItemIcon><ExitToAppIcon /></ListItemIcon>
                      <ListItemText primary="Logout" />
                    </MenuItem>
                  </Menu>
                </>
              ) : (
                authItems.map((item) => (
                  <Button
                    key={item.id}
                    color="inherit"
                    onClick={() => handleNavigation(item.path)}
                    startIcon={item.icon}
                    sx={{
                      color: theme.palette.mode === 'dark' ? 'white' : 'text.primary',
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.primary.main, 0.1)
                      }
                    }}
                  >
                    {item.label}
                  </Button>
                ))
              )}
            </Box>
          )}

          {/* Mobile Menu Button */}
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
            >
              <MenuIcon />
            </IconButton>
          )}
        </Toolbar>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        anchor="right"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: 280,
          },
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2 }}>
          <Typography variant="h6">Navigation</Typography>
          <IconButton onClick={handleDrawerToggle}>
            <CloseIcon />
          </IconButton>
        </Box>
        {drawer}
      </Drawer>
    </>
  );
};

export default Header;
