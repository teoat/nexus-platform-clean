import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Error,
  Refresh,
  Analytics,
  Security,
  Speed,
  Memory,
} from '@mui/icons-material';
import { useMonitoringStore } from '../../store/monitoringStore';
import FrenlyInsights from '../ai/FrenlyInsights';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`monitoring-tabpanel-${index}`}
      aria-labelledby={`monitoring-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const OptimizedMonitoringDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const {
    metrics,
    alerts,
    performance,
    insights,
    isLoading,
    error,
    lastRefresh,
    fetchMetrics,
    fetchAlerts,
    fetchPerformance,
    fetchInsights,
    fetchAllData,
    acknowledgeAlert,
    clearError,
  } = useMonitoringStore();

  // Insights state management - implementing MON-001 TODO
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [insightsError, setInsightsError] = useState<string | null>(null);

  useEffect(() => {
    fetchAllData();
    // Load insights separately with proper state management
    loadInsights();
  }, []);

  const loadInsights = async () => {
    try {
      setInsightsLoading(true);
      setInsightsError(null);
      await fetchInsights();
    } catch (error: any) {
      setInsightsError(error.message || 'Failed to load insights');
    } finally {
      setInsightsLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchAllData();
    loadInsights();
  };

  const handleSendFrenlyMessage = (message: string) => {
    // Implementation for sending messages to Frenly AI
    console.log('Sending message to Frenly:', message);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <Warning color="error" />;
      case 'acknowledged': return <CheckCircle color="warning" />;
      case 'resolved': return <CheckCircle color="success" />;
      default: return <Error color="error" />;
    }
  };

  if (error) {
    return (
      <Alert
        severity="error"
        action={
          <IconButton size="small" onClick={clearError}>
            ×
          </IconButton>
        }
      >
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          System Monitoring Dashboard
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          {lastRefresh && (
            <Typography variant="body2" color="text.secondary">
              Last updated: {lastRefresh.toLocaleTimeString()}
            </Typography>
          )}
          <Tooltip title="Refresh all data">
            <IconButton onClick={handleRefresh} disabled={isLoading}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {isLoading && <LinearProgress sx={{ mb: 2 }} />}

      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab icon={<Analytics />} label="Overview" />
        <Tab icon={<Security />} label="Alerts" />
        <Tab icon={<Speed />} label="Performance" />
        <Tab icon={<Memory />} label="Insights" />
      </Tabs>

      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          {/* System Metrics */}
          <Grid item xs={12} md={6} lg={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h6">CPU Usage</Typography>
                    <Typography variant="h4" color="primary">
                      {metrics?.cpu || 0}%
                    </Typography>
                  </Box>
                  <Speed fontSize="large" color="primary" />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6} lg={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h6">Memory Usage</Typography>
                    <Typography variant="h4" color="secondary">
                      {metrics?.memory || 0}%
                    </Typography>
                  </Box>
                  <Memory fontSize="large" color="secondary" />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6} lg={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h6">Response Time</Typography>
                    <Typography variant="h4" color="success">
                      {performance?.responseTime || 0}ms
                    </Typography>
                  </Box>
                  <TrendingUp fontSize="large" color="success" />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6} lg={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h6">Uptime</Typography>
                    <Typography variant="h4" color="info">
                      {performance?.uptime || 0}%
                    </Typography>
                  </Box>
                  <CheckCircle fontSize="large" color="info" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Active Alerts ({alerts.length})
          </Typography>
          <List>
            {alerts.map((alert) => (
              <React.Fragment key={alert.id}>
                <ListItem
                  secondaryAction={
                    alert.status === 'active' && (
                      <IconButton
                        edge="end"
                        onClick={() => acknowledgeAlert(alert.id)}
                      >
                        <CheckCircle />
                      </IconButton>
                    )
                  }
                >
                  <ListItemIcon>
                    {getStatusIcon(alert.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={alert.title}
                    secondary={
                      <Box>
                        <Typography variant="body2">{alert.message}</Typography>
                        <Box mt={1}>
                          <Chip
                            label={alert.severity}
                            color={getSeverityColor(alert.severity) as any}
                            size="small"
                            sx={{ mr: 1 }}
                          />
                          <Chip
                            label={alert.status}
                            variant="outlined"
                            size="small"
                          />
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
                <Divider />
              </React.Fragment>
            ))}
          </List>
        </Paper>
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Metrics
                </Typography>
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Typography>Throughput</Typography>
                  <Typography>{performance?.throughput || 0} req/s</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between" mb={2}>
                  <Typography>Error Rate</Typography>
                  <Typography>{performance?.errorRate || 0}%</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography>Performance Score</Typography>
                  <Typography>{performance?.score || 0}/100</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <FrenlyInsights
              insights={insights}
              onSendMessage={handleSendFrenlyMessage}
              loading={insightsLoading}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Insights Summary
                </Typography>
                {insightsError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {insightsError}
                  </Alert>
                )}
                <Typography variant="body2" color="text.secondary">
                  Total insights: {insights.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  High priority: {insights.filter(i => i.priority === 'high').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Warnings: {insights.filter(i => i.type === 'warning').length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
};

export default OptimizedMonitoringDashboard;