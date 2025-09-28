/**
 * NEXUS Platform - Workflow Diagram Component
 * Visual representation of logical workflows and user journeys
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Chip,
  Grid,
  Paper,
  useTheme,
  alpha,
  Fade,
  Zoom
} from '@mui/material';
import {
  Login as LoginIcon,
  Dashboard as DashboardIcon,
  AccountBalance as AccountBalanceIcon,
  Receipt as ReceiptIcon,
  Analytics as AnalyticsIcon,
  Assessment as ReportsIcon,
  AdminPanelSettings as AdminIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  TrendingUp as TrendingUpIcon,
  Timeline as TimelineIcon,
  CheckCircle as CheckCircleIcon,
  ArrowForward as ArrowForwardIcon,
  Business as BusinessIcon,
  Memory as MemoryIcon
} from '@mui/icons-material';

interface WorkflowStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactElement;
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  features: string[];
  nextSteps: string[];
}

interface Workflow {
  id: string;
  title: string;
  description: string;
  steps: WorkflowStep[];
  category: 'authentication' | 'financial' | 'analytics' | 'administration' | 'user';
}

const WorkflowDiagram: React.FC = () => {
  const theme = useTheme();
  const [activeWorkflow, setActiveWorkflow] = useState<string>('authentication');
  const [activeStep, setActiveStep] = useState<number>(0);

  const workflows: Workflow[] = [
    {
      id: 'authentication',
      title: 'Authentication Workflow',
      description: 'Secure user authentication and onboarding process',
      category: 'authentication',
      steps: [
        {
          id: 'login',
          title: 'Login/Register',
          description: 'User authentication and account creation',
          icon: <LoginIcon />,
          color: 'primary',
          features: [
            'Email/Password Authentication',
            'Social Login Options',
            'Multi-Factor Authentication',
            'Account Recovery',
            'Terms & Conditions'
          ],
          nextSteps: ['Email Verification', 'Profile Setup', 'Dashboard Access']
        },
        {
          id: 'verification',
          title: 'Email Verification',
          description: 'Account verification and security confirmation',
          icon: <CheckCircleIcon />,
          color: 'success',
          features: [
            'Email Verification Link',
            'Security Confirmation',
            'Account Activation',
            'Welcome Email',
            'Security Setup'
          ],
          nextSteps: ['Profile Setup', 'Dashboard Onboarding', 'Feature Introduction']
        },
        {
          id: 'onboarding',
          title: 'Dashboard Onboarding',
          description: 'Introduction to platform features and capabilities',
          icon: <DashboardIcon />,
          color: 'info',
          features: [
            'Platform Tour',
            'Feature Introduction',
            'Quick Setup',
            'Sample Data',
            'Tutorial Videos'
          ],
          nextSteps: ['Profile Setup', 'Account Configuration', 'First Transactions']
        }
      ]
    },
    {
      id: 'financial',
      title: 'Financial Management Workflow',
      description: 'Complete financial lifecycle management process',
      category: 'financial',
      steps: [
        {
          id: 'accounts',
          title: 'Account Setup',
          description: 'Configure and manage financial accounts',
          icon: <AccountBalanceIcon />,
          color: 'primary',
          features: [
            'Bank Account Linking',
            'Investment Account Setup',
            'Asset Portfolio Configuration',
            'Account Verification',
            'Security Settings'
          ],
          nextSteps: ['Transaction Import', 'Account Monitoring', 'Balance Tracking']
        },
        {
          id: 'transactions',
          title: 'Transaction Management',
          description: 'Import, categorize, and analyze transactions',
          icon: <ReceiptIcon />,
          color: 'success',
          features: [
            'Transaction Import',
            'Smart Categorization',
            'Manual Review',
            'Duplicate Detection',
            'Data Validation'
          ],
          nextSteps: ['Analysis', 'Reporting', 'Optimization']
        },
        {
          id: 'analysis',
          title: 'Financial Analysis',
          description: 'Analyze spending patterns and financial health',
          icon: <AnalyticsIcon />,
          color: 'info',
          features: [
            'Spending Analysis',
            'Trend Identification',
            'Budget Analysis',
            'Goal Tracking',
            'Risk Assessment'
          ],
          nextSteps: ['Reporting', 'Optimization', 'Planning']
        },
        {
          id: 'reports',
          title: 'Report Generation',
          description: 'Generate comprehensive financial reports',
          icon: <ReportsIcon />,
          color: 'warning',
          features: [
            'Financial Statements',
            'Custom Reports',
            'Tax Documentation',
            'Performance Reports',
            'Export Options'
          ],
          nextSteps: ['Sharing', 'Archiving', 'Planning']
        }
      ]
    },
    {
      id: 'analytics',
      title: 'Analytics & Intelligence Workflow',
      description: 'Data-driven decision making and predictive analytics',
      category: 'analytics',
      steps: [
        {
          id: 'data-collection',
          title: 'Data Collection',
          description: 'Gather and process financial data',
          icon: <MemoryIcon />,
          color: 'primary',
          features: [
            'Real-time Data Sync',
            'Historical Data Import',
            'External Data Sources',
            'Data Validation',
            'Data Cleaning'
          ],
          nextSteps: ['Analysis', 'Modeling', 'Insights']
        },
        {
          id: 'performance',
          title: 'Performance Analysis',
          description: 'Analyze system and financial performance',
          icon: <SpeedIcon />,
          color: 'success',
          features: [
            'Performance Metrics',
            'System Health',
            'Resource Monitoring',
            'Bottleneck Identification',
            'Optimization Recommendations'
          ],
          nextSteps: ['Optimization', 'Scaling', 'Monitoring']
        },
        {
          id: 'trends',
          title: 'Trend Analysis',
          description: 'Identify patterns and trends in data',
          icon: <TrendingUpIcon />,
          color: 'info',
          features: [
            'Pattern Recognition',
            'Trend Identification',
            'Seasonal Analysis',
            'Market Insights',
            'Predictive Indicators'
          ],
          nextSteps: ['Predictions', 'Planning', 'Strategy']
        },
        {
          id: 'predictions',
          title: 'Predictive Modeling',
          description: 'AI-powered predictions and forecasting',
          icon: <TimelineIcon />,
          color: 'warning',
          features: [
            'AI Predictions',
            'Financial Forecasting',
            'Scenario Planning',
            'Risk Modeling',
            'Goal Projections'
          ],
          nextSteps: ['Planning', 'Strategy', 'Implementation']
        }
      ]
    },
    {
      id: 'administration',
      title: 'Administration Workflow',
      description: 'System administration and configuration management',
      category: 'administration',
      steps: [
        {
          id: 'user-management',
          title: 'User Management',
          description: 'Manage users, roles, and permissions',
          icon: <PersonIcon />,
          color: 'primary',
          features: [
            'User Creation',
            'Role Assignment',
            'Permission Management',
            'Access Control',
            'User Monitoring'
          ],
          nextSteps: ['Security', 'Configuration', 'Monitoring']
        },
        {
          id: 'system-config',
          title: 'System Configuration',
          description: 'Configure system settings and parameters',
          icon: <SettingsIcon />,
          color: 'success',
          features: [
            'System Settings',
            'Feature Toggles',
            'Integration Setup',
            'Performance Tuning',
            'Backup Configuration'
          ],
          nextSteps: ['Security', 'Monitoring', 'Testing']
        },
        {
          id: 'security',
          title: 'Security Management',
          description: 'Implement and monitor security measures',
          icon: <SecurityIcon />,
          color: 'error',
          features: [
            'Security Policies',
            'Access Controls',
            'Audit Logging',
            'Threat Detection',
            'Incident Response'
          ],
          nextSteps: ['Monitoring', 'Compliance', 'Reporting']
        },
        {
          id: 'monitoring',
          title: 'System Monitoring',
          description: 'Monitor system health and performance',
          icon: <MemoryIcon />,
          color: 'info',
          features: [
            'Health Monitoring',
            'Performance Tracking',
            'Alert Management',
            'Log Analysis',
            'Capacity Planning'
          ],
          nextSteps: ['Optimization', 'Scaling', 'Maintenance']
        }
      ]
    },
    {
      id: 'user',
      title: 'User Management Workflow',
      description: 'Personal account management and customization',
      category: 'user',
      steps: [
        {
          id: 'profile',
          title: 'Profile Management',
          description: 'Manage personal profile and information',
          icon: <PersonIcon />,
          color: 'primary',
          features: [
            'Personal Information',
            'Profile Picture',
            'Contact Details',
            'Preferences',
            'Privacy Settings'
          ],
          nextSteps: ['Settings', 'Security', 'Notifications']
        },
        {
          id: 'settings',
          title: 'Application Settings',
          description: 'Configure application preferences and options',
          icon: <SettingsIcon />,
          color: 'success',
          features: [
            'Display Settings',
            'Notification Preferences',
            'Language Selection',
            'Theme Configuration',
            'Data Management'
          ],
          nextSteps: ['Security', 'Notifications', 'Data']
        },
        {
          id: 'security',
          title: 'Security Settings',
          description: 'Manage security and authentication settings',
          icon: <SecurityIcon />,
          color: 'error',
          features: [
            'Password Management',
            'Two-Factor Authentication',
            'Login History',
            'Security Alerts',
            'Account Recovery'
          ],
          nextSteps: ['Notifications', 'Data', 'Support']
        }
      ]
    }
  ];

  const getCategoryColor = (category: string): 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' => {
    switch (category) {
      case 'authentication': return 'primary';
      case 'financial': return 'success';
      case 'analytics': return 'info';
      case 'administration': return 'warning';
      case 'user': return 'secondary';
      default: return 'primary';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'authentication': return <LoginIcon />;
      case 'financial': return <AccountBalanceIcon />;
      case 'analytics': return <AnalyticsIcon />;
      case 'administration': return <AdminIcon />;
      case 'user': return <PersonIcon />;
      default: return <BusinessIcon />;
    }
  };

  const currentWorkflow = workflows.find(w => w.id === activeWorkflow);

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          NEXUS Platform Workflows
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Visual representation of logical workflows and user journeys
        </Typography>
      </Box>

      {/* Workflow Selection */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {workflows.map((workflow) => (
          <Grid item xs={12} sm={6} md={4} key={workflow.id}>
            <Card
              sx={{
                cursor: 'pointer',
                border: activeWorkflow === workflow.id ? `2px solid ${theme.palette[getCategoryColor(workflow.category)].main}` : '1px solid',
                borderColor: activeWorkflow === workflow.id ? theme.palette[getCategoryColor(workflow.category)].main : 'divider',
                '&:hover': {
                  boxShadow: theme.shadows[4],
                  transform: 'translateY(-2px)'
                },
                transition: 'all 0.2s ease-in-out'
              }}
              onClick={() => {
                setActiveWorkflow(workflow.id);
                setActiveStep(0);
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  {getCategoryIcon(workflow.category)}
                  <Typography variant="h6" fontWeight="medium">
                    {workflow.title}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {workflow.description}
                </Typography>
                <Chip
                  label={`${workflow.steps.length} steps`}
                  size="small"
                  color={getCategoryColor(workflow.category)}
                  variant="outlined"
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Workflow Steps */}
      {currentWorkflow && (
        <Fade in={true} timeout={500}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Box sx={{ mb: 3, textAlign: 'center' }}>
              <Typography variant="h5" gutterBottom fontWeight="bold">
                {currentWorkflow.title}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                {currentWorkflow.description}
              </Typography>
            </Box>

            <Stepper activeStep={activeStep} orientation="vertical">
              {currentWorkflow.steps.map((step, index) => (
                <Step key={step.id}>
                  <StepLabel
                    StepIconComponent={() => (
                      <Zoom in={true} timeout={300 + index * 100}>
                        <Box
                          sx={{
                            width: 40,
                            height: 40,
                            borderRadius: '50%',
                            backgroundColor: theme.palette[step.color].main,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'white',
                            boxShadow: theme.shadows[2]
                          }}
                        >
                          {step.icon}
                        </Box>
                      </Zoom>
                    )}
                  >
                    <Typography variant="h6" fontWeight="medium">
                      {step.title}
                    </Typography>
                  </StepLabel>
                  <StepContent>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body1" paragraph>
                        {step.description}
                      </Typography>
                      
                      <Typography variant="subtitle2" gutterBottom fontWeight="medium">
                        Key Features:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                        {step.features.map((feature, featureIndex) => (
                          <Chip
                            key={featureIndex}
                            label={feature}
                            size="small"
                            color={step.color}
                            variant="outlined"
                          />
                        ))}
                      </Box>

                      <Typography variant="subtitle2" gutterBottom fontWeight="medium">
                        Next Steps:
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                        {step.nextSteps.map((nextStep, nextIndex) => (
                          <React.Fragment key={nextIndex}>
                            <Chip
                              label={nextStep}
                              size="small"
                              variant="filled"
                              sx={{ backgroundColor: alpha(theme.palette[step.color].main, 0.1) }}
                            />
                            {nextIndex < step.nextSteps.length - 1 && (
                              <ArrowForwardIcon fontSize="small" color="action" />
                            )}
                          </React.Fragment>
                        ))}
                      </Box>
                    </Box>

                    <Box sx={{ mb: 1 }}>
                      <Button
                        variant="contained"
                        onClick={() => setActiveStep(index + 1)}
                        disabled={index === currentWorkflow.steps.length - 1}
                        sx={{ mr: 1 }}
                      >
                        Next Step
                      </Button>
                      <Button
                        onClick={() => setActiveStep(index - 1)}
                        disabled={index === 0}
                      >
                        Previous
                      </Button>
                    </Box>
                  </StepContent>
                </Step>
              ))}
            </Stepper>

            {/* Workflow Summary */}
            <Box sx={{ mt: 4, p: 2, backgroundColor: alpha(theme.palette.primary.main, 0.05), borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom fontWeight="medium">
                Workflow Summary
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                This workflow consists of {currentWorkflow.steps.length} steps that guide users through the {currentWorkflow.title.toLowerCase()} process. 
                Each step builds upon the previous one, creating a logical and intuitive user experience.
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={`${currentWorkflow.steps.length} Total Steps`}
                  size="small"
                  color="primary"
                />
                <Chip
                  label={`${currentWorkflow.steps.reduce((acc, step) => acc + step.features.length, 0)} Features`}
                  size="small"
                  color="secondary"
                />
                <Chip
                  label="Progressive Enhancement"
                  size="small"
                  color="success"
                />
              </Box>
            </Box>
          </Paper>
        </Fade>
      )}
    </Box>
  );
};

export default WorkflowDiagram;
