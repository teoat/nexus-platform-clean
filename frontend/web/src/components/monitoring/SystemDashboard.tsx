/**
 * NEXUS Platform - Comprehensive System Dashboard
 * Unified monitoring dashboard for all system components
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Alert,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Api as ApiIcon,
  Psychology as PsychologyIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon
} from '@mui/icons-material';
import { useSSOT } from '@hooks/useSSOT';
import { usePerformanceBudget } from '@hooks/usePerformanceBudget';

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
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const SystemDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [alerts, setAlerts] = useState<Array<{ id: string; type: 'error' | 'warning' | 'info'; message: string; timestamp: string }>>([]);

  const {
    context: ssotContext,
    aliases,
    cacheStats,
    isLoading: ssotLoading,
    error: ssotError,
    refreshAliases,
    clearCache
  } = useSSOT();

  const {
    budget,
    currentMetrics,
    checkBudget,
     getPerformanceScore,
     getCacheHitRate,
     getApiSuccessRate,
     trackCacheSize
  } = usePerformanceBudget();

  // Update last refresh time
  const handleRefresh = () => {
    setLastUpdate(new Date());
    refreshAliases();
    // Trigger performance metrics update
    window.location.reload();
  };

  // Generate alerts based on system state
  useEffect(() => {
    const newAlerts: Array<{ id: string; type: 'error' | 'warning' | 'info'; message: string; timestamp: string }> = [];
    
    const violations = checkBudget();
    violations.forEach((violation, index) => {
      newAlerts.push({
        id: `violation-${Date.now()}-${index}`,
        type: 'error',
        message: violation,
        timestamp: new Date().toISOString()
      });
    });

    if (ssotError) {
      newAlerts.push({
        id: `ssot-error-${Date.now()}`,
        type: 'error',
        message: `SSOT Error: ${ssotError}`,
        timestamp: new Date().toISOString()
      });
    }

    if (getPerformanceScore() < 70) {
      newAlerts.push({
        id: `performance-${Date.now()}`,
        type: 'warning',
        message: `Performance score is ${getPerformanceScore()}% - below recommended threshold`,
        timestamp: new Date().toISOString()
      });
    }

    if (getCacheHitRate() < 50) {
      newAlerts.push({
        id: `cache-${Date.now()}`,
        type: 'warning',
        message: `Cache hit rate is ${getCacheHitRate()}% - consider optimizing alias patterns`,
        timestamp: new Date().toISOString()
      });
    }

    if (getApiSuccessRate() < 90) {
      newAlerts.push({
        id: `api-${Date.now()}`,
        type: 'error',
        message: `API success rate is ${getApiSuccessRate()}% - check for backend issues`,
        timestamp: new Date().toISOString()
      });
    }

    setAlerts(newAlerts);
  }, [checkBudget, ssotError, getPerformanceScore, getCacheHitRate, getApiSuccessRate]);

  const performanceScore = getPerformanceScore();
  const cacheHitRate = getCacheHitRate();
  const apiSuccessRate = getApiSuccessRate();

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTime = (ms: number) => {
    return `${ms.toFixed(0)}ms`;
  };

  // Overview Tab
  const OverviewTab = () => (
    <Grid container spacing={3}>
      {/* System Status Cards */}
      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <SpeedIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Performance</Typography>
            </Box>
            <Typography variant="h4" color={getScoreColor(performanceScore)}>
              {performanceScore}%
            </Typography>
            <LinearProgress
              variant="determinate"
              value={performanceScore}
              color={getScoreColor(performanceScore)}
              sx={{ mt: 1, height: 8, borderRadius: 4 }}
            />
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <MemoryIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">Cache</Typography>
            </Box>
            <Typography variant="h4" color={cacheHitRate >= 50 ? 'success.main' : 'warning.main'}>
              {cacheHitRate}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {cacheStats.size} items cached
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <ApiIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">API Health</Typography>
            </Box>
            <Typography variant="h4" color={apiSuccessRate >= 90 ? 'success.main' : 'error.main'}>
              {apiSuccessRate}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {currentMetrics.totalApiCalls} total calls
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <PsychologyIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6">SSOT</Typography>
            </Box>
            <Typography variant="h4" color="primary">
              {aliases.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {ssotContext} context
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Alerts ({alerts.length})
              </Typography>
              {alerts.slice(0, 5).map((alert) => (
                <Alert
                  key={alert.id}
                  severity={alert.type}
                  sx={{ mb: 1 }}
                  action={
                    <Chip
                      label={new Date(alert.timestamp).toLocaleTimeString()}
                      size="small"
                      variant="outlined"
                    />
                  }
                >
                  {alert.message}
                </Alert>
              ))}
            </CardContent>
          </Card>
        </Grid>
      )}

      {/* Quick Actions */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={handleRefresh}
                disabled={ssotLoading}
              >
                Refresh All
              </Button>
              <Button
                variant="outlined"
                onClick={clearCache}
                disabled={cacheStats.size === 0}
              >
                Clear Cache
              </Button>
              <Button
                variant="outlined"
                href="/ssot"
              >
                Manage Aliases
              </Button>
              <Button
                variant="outlined"
                href="/performance"
              >
                Performance Details
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // Performance Tab
  const PerformanceTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance Metrics
            </Typography>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Metric</TableCell>
                    <TableCell>Current</TableCell>
                    <TableCell>Budget</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Trend</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Bundle Size</TableCell>
                    <TableCell>{formatBytes(currentMetrics.bundleSize)}</TableCell>
                    <TableCell>{formatBytes(budget.maxBundleSize)}</TableCell>
                    <TableCell>
                      <Chip
                        icon={currentMetrics.bundleSize > budget.maxBundleSize ? <ErrorIcon /> : <CheckCircleIcon />}
                        label={currentMetrics.bundleSize > budget.maxBundleSize ? 'Over Budget' : 'Within Budget'}
                        color={currentMetrics.bundleSize > budget.maxBundleSize ? 'error' : 'success'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <TrendingUpIcon color="error" />
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Load Time</TableCell>
                    <TableCell>{formatTime(currentMetrics.loadTime)}</TableCell>
                    <TableCell>{formatTime(budget.maxLoadTime)}</TableCell>
                    <TableCell>
                      <Chip
                        icon={currentMetrics.loadTime > budget.maxLoadTime ? <ErrorIcon /> : <CheckCircleIcon />}
                        label={currentMetrics.loadTime > budget.maxLoadTime ? 'Over Budget' : 'Within Budget'}
                        color={currentMetrics.loadTime > budget.maxLoadTime ? 'error' : 'success'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <TrendingDownIcon color="success" />
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Memory Usage</TableCell>
                    <TableCell>{formatBytes(currentMetrics.memoryUsage)}</TableCell>
                    <TableCell>{formatBytes(budget.maxMemoryUsage)}</TableCell>
                    <TableCell>
                      <Chip
                        icon={currentMetrics.memoryUsage > budget.maxMemoryUsage ? <ErrorIcon /> : <CheckCircleIcon />}
                        label={currentMetrics.memoryUsage > budget.maxMemoryUsage ? 'Over Budget' : 'Within Budget'}
                        color={currentMetrics.memoryUsage > budget.maxMemoryUsage ? 'error' : 'success'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <TrendingUpIcon color="warning" />
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>API Response Time</TableCell>
                    <TableCell>{formatTime(currentMetrics.apiResponseTime)}</TableCell>
                    <TableCell>{formatTime(budget.maxApiResponseTime)}</TableCell>
                    <TableCell>
                      <Chip
                        icon={currentMetrics.apiResponseTime > budget.maxApiResponseTime ? <ErrorIcon /> : <CheckCircleIcon />}
                        label={currentMetrics.apiResponseTime > budget.maxApiResponseTime ? 'Over Budget' : 'Within Budget'}
                        color={currentMetrics.apiResponseTime > budget.maxApiResponseTime ? 'error' : 'success'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <TrendingDownIcon color="success" />
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  // SSOT Tab
  const SSOTTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              SSOT Context: {ssotContext}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip label={`${aliases.length} aliases`} color="primary" />
              <Chip label={`${cacheStats.size} cached`} color="secondary" />
            </Box>
            <Typography variant="body2" color="text.secondary">
              Last updated: {lastUpdate.toLocaleTimeString()}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Cache Statistics
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText
                  primary="Cache Size"
                  secondary={`${cacheStats.size} items`}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Cache Hit Rate"
                  secondary={`${cacheHitRate}%`}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Alias Resolution Time"
                  secondary={formatTime(currentMetrics.aliasResolutionTime)}
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Active Aliases
            </Typography>
            {aliases.length > 0 ? (
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Alias</TableCell>
                      <TableCell>Canonical</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {aliases.slice(0, 10).map((alias, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <code>@{alias.alias || alias.name}</code>
                        </TableCell>
                        <TableCell>
                          <code>{alias.canonical}</code>
                        </TableCell>
                        <TableCell>
                          <Chip label={alias.type || 'application'} size="small" />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={alias.status || 'active'}
                            color={alias.status === 'active' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Typography color="text.secondary">
                No aliases configured in this context
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          System Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh All Data">
            <IconButton onClick={handleRefresh} disabled={ssotLoading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Settings">
            <IconButton>
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Overview" icon={<DashboardIcon />} />
          <Tab label="Performance" icon={<SpeedIcon />} />
          <Tab label="SSOT" icon={<ApiIcon />} />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <OverviewTab />
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        <PerformanceTab />
      </TabPanel>
      <TabPanel value={tabValue} index={2}>
        <SSOTTab />
      </TabPanel>
    </Box>
  );
};

export default SystemDashboard;
