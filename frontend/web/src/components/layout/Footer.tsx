/**
 * NEXUS Platform - Footer Component
 * Comprehensive footer with sitemap, legal, contact, and version info
 */

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Link,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  IconButton,
  Collapse,
  Chip,
  useTheme,
  alpha
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Business as BusinessIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Analytics as AnalyticsIcon,
  AccountBalance as AccountBalanceIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  Assessment as ReportsIcon,
  AdminPanelSettings as AdminIcon,
  Login as LoginIcon,
  PersonAdd as RegisterIcon,
  Memory as MemoryIcon,
  AccountTree as AccountTreeIcon,
  Timeline as TimelineIcon,
  TrendingUp as TrendingUpIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  LocationOn as LocationIcon,
  GitHub as GitHubIcon,
  LinkedIn as LinkedInIcon,
  Twitter as TwitterIcon,
  Copyright as CopyrightIcon,
  Code as CodeIcon,
  BugReport as BugReportIcon,
  Help as HelpIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface FooterSection {
  title: string;
  icon: React.ReactElement;
  items: FooterItem[];
  collapsible?: boolean;
}

interface FooterItem {
  label: string;
  path?: string;
  href?: string;
  description?: string;
  badge?: string;
  external?: boolean;
}

const Footer: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [expandedSections, setExpandedSections] = useState<{ [key: string]: boolean }>({});

  const handleSectionToggle = (sectionTitle: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionTitle]: !prev[sectionTitle]
    }));
  };

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  const footerSections: FooterSection[] = [
    {
      title: 'Platform',
      icon: <BusinessIcon />,
      items: [
        { label: 'Dashboard', path: '/dashboard', description: 'Central command center' },
        { label: 'Analytics', path: '/analytics', description: 'Advanced analytics & insights' },
        { label: 'Reports', path: '/reports', description: 'Financial reports & documentation' },
        { label: 'Performance', path: '/analytics/performance', description: 'System performance metrics' }
      ]
    },
    {
      title: 'Financial',
      icon: <AccountBalanceIcon />,
      items: [
        { label: 'Accounts', path: '/accounts', description: 'Account management' },
        { label: 'Transactions', path: '/transactions', description: 'Transaction analysis' },
        { label: 'Reconciliation', path: '/reconciliation', description: 'Bank reconciliation' },
        { label: 'Fraud Detection', path: '/fraud-detection', description: 'AI-powered fraud analysis' }
      ]
    },
    {
      title: 'Intelligence',
      icon: <AnalyticsIcon />,
      items: [
        { label: 'AI Insights', path: '/ai-insights', description: 'Explainable AI insights' },
        { label: 'Trends', path: '/analytics/trends', description: 'Financial trend analysis' },
        { label: 'Predictions', path: '/analytics/predictions', description: 'Predictive modeling' },
        { label: 'Risk Assessment', path: '/risk-assessment', description: 'Comprehensive risk analysis' }
      ]
    },
    {
      title: 'System',
      icon: <MemoryIcon />,
      items: [
        { label: 'SSOT Manager', path: '/ssot', description: 'Single source of truth' },
        { label: 'Monitoring', path: '/monitoring', description: 'System monitoring' },
        { label: 'Audit Logs', path: '/audit-logs', description: 'Comprehensive audit trail' },
        { label: 'API Registry', path: '/api-registry', description: 'API documentation' }
      ]
    },
    {
      title: 'User',
      icon: <PersonIcon />,
      items: [
        { label: 'Profile', path: '/profile', description: 'User profile management' },
        { label: 'Settings', path: '/settings', description: 'Application settings' },
        { label: 'Security', path: '/security', description: 'Security settings' },
        { label: 'Preferences', path: '/preferences', description: 'User preferences' }
      ]
    },
    {
      title: 'Administration',
      icon: <AdminIcon />,
      items: [
        { label: 'User Management', path: '/admin/users', description: 'User administration' },
        { label: 'System Config', path: '/admin/config', description: 'System configuration' },
        { label: 'Security Policies', path: '/admin/security', description: 'Security management' },
        { label: 'Audit Trail', path: '/admin/audit', description: 'System audit trail' }
      ],
      collapsible: true
    }
  ];

  const legalSections = [
    { label: 'Privacy Policy', path: '/privacy' },
    { label: 'Terms of Service', path: '/terms' },
    { label: 'Cookie Policy', path: '/cookies' },
    { label: 'Data Protection', path: '/data-protection' },
    { label: 'Compliance', path: '/compliance' }
  ];

  const supportSections = [
    { label: 'Help Center', path: '/help' },
    { label: 'Documentation', path: '/docs' },
    { label: 'API Reference', path: '/api-docs' },
    { label: 'Status Page', href: 'https://status.nexus-platform.com', external: true },
    { label: 'Contact Support', path: '/support' }
  ];

  const socialLinks = [
    { label: 'GitHub', href: 'https://github.com/nexus-platform', icon: <GitHubIcon /> },
    { label: 'LinkedIn', href: 'https://linkedin.com/company/nexus-platform', icon: <LinkedInIcon /> },
    { label: 'Twitter', href: 'https://twitter.com/nexus_platform', icon: <TwitterIcon /> }
  ];

  const contactInfo = [
    { icon: <EmailIcon />, label: 'support@nexus-platform.com', href: 'mailto:support@nexus-platform.com' },
    { icon: <PhoneIcon />, label: '+1 (555) 123-4567', href: 'tel:+15551234567' },
    { icon: <LocationIcon />, label: 'San Francisco, CA', href: '#' }
  ];

  const renderFooterSection = (section: FooterSection) => {
    const isExpanded = expandedSections[section.title];
    const shouldCollapse = section.collapsible && !isExpanded;

    return (
      <Grid item xs={12} sm={6} md={4} lg={2} key={section.title}>
        <Box
          sx={{
            cursor: section.collapsible ? 'pointer' : 'default',
            '&:hover': section.collapsible ? { opacity: 0.8 } : {}
          }}
          onClick={() => section.collapsible && handleSectionToggle(section.title)}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            {section.icon}
            <Typography variant="h6" fontWeight="bold">
              {section.title}
            </Typography>
            {section.collapsible && (
              <IconButton size="small">
                {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            )}
          </Box>

          <Collapse in={!shouldCollapse}>
            <List dense>
              {section.items
                .filter(item => !item.path || !item.path.includes('/admin') || user)
                .map((item) => (
                  <ListItem
                    key={item.label}
                    button
                    onClick={() => {
                      if (item.path) {
                        handleNavigation(item.path);
                      } else if (item.href) {
                        window.open(item.href, item.external ? '_blank' : '_self');
                      }
                    }}
                    sx={{
                      px: 0,
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.primary.main, 0.05)
                      }
                    }}
                  >
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" fontWeight="medium">
                            {item.label}
                          </Typography>
                          {item.badge && (
                            <Chip label={item.badge} size="small" color="primary" variant="outlined" />
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
                ))}
            </List>
          </Collapse>
        </Box>
      </Grid>
    );
  };

  return (
    <Box
      component="footer"
      sx={{
        backgroundColor: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.100',
        borderTop: `1px solid ${theme.palette.divider}`,
        mt: 'auto'
      }}
    >
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Main Footer Content */}
        <Grid container spacing={4}>
          {/* Platform Sections */}
          {footerSections.map(renderFooterSection)}

          {/* Contact & Support */}
          <Grid item xs={12} sm={6} md={4} lg={2}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <HelpIcon />
              <Typography variant="h6" fontWeight="bold">
                Support
              </Typography>
            </Box>
            <List dense>
              {supportSections.map((item) => (
                <ListItem
                  key={item.label}
                  button
                  onClick={() => {
                    if (item.path) {
                      handleNavigation(item.path);
                    } else if (item.href) {
                      window.open(item.href, item.external ? '_blank' : '_self');
                    }
                  }}
                  sx={{ px: 0 }}
                >
                  <ListItemText
                    primary={
                      <Typography variant="body2" fontWeight="medium">
                        {item.label}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Grid>
        </Grid>

        <Divider sx={{ my: 3 }} />

        {/* Contact Information */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Contact Information
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {contactInfo.map((contact, index) => (
                <Box
                  key={index}
                  sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
                >
                  {contact.icon}
                  <Link
                    href={contact.href}
                    color="inherit"
                    sx={{ textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
                  >
                    {contact.label}
                  </Link>
                </Box>
              ))}
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom fontWeight="bold">
              Follow Us
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {socialLinks.map((social) => (
                <IconButton
                  key={social.label}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    color: 'text.secondary',
                    '&:hover': { color: 'primary.main' }
                  }}
                >
                  {social.icon}
                </IconButton>
              ))}
            </Box>
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        {/* Legal & Copyright */}
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <BusinessIcon color="primary" />
              <Typography variant="h6" fontWeight="bold">
                NEXUS Platform
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" paragraph>
              Forensic Financial Intelligence Platform for Advanced Audit, Reconciliation, and Fraud Detection
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {legalSections.map((legal) => (
                <Link
                  key={legal.label}
                  href={legal.path}
                  color="text.secondary"
                  sx={{ textDecoration: 'none', fontSize: '0.875rem' }}
                >
                  {legal.label}
                </Link>
              ))}
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <CopyrightIcon fontSize="small" />
              <Typography variant="body2" color="text.secondary">
                {new Date().getFullYear()} NEXUS Platform. All rights reserved.
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
              <Chip
                icon={<CodeIcon />}
                label="v2.1.0"
                size="small"
                color="primary"
                variant="outlined"
              />
              <Chip
                icon={<SecurityIcon />}
                label="SOC 2 Compliant"
                size="small"
                color="success"
                variant="outlined"
              />
              <Chip
                icon={<BugReportIcon />}
                label="Production Ready"
                size="small"
                color="info"
                variant="outlined"
              />
            </Box>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Footer;
