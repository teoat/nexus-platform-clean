/**
 * NEXUS Platform - Performance Monitoring Dashboard
 * Real-time performance monitoring with SSOT integration
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { usePerformanceBudget } from '@hooks/usePerformanceBudget';
import { useSSOT } from '@hooks/useSSOT';

const PerformanceDashboard: React.FC = () => {
  const {
     budget,
     currentMetrics,
     checkBudget,
     trackCacheSize,
     getPerformanceScore,
     getCacheHitRate,
     getApiSuccessRate
  } = usePerformanceBudget();

  const { cacheStats } = useSSOT();
  const [violations, setViolations] = useState<string[]>([]);
  const [settingsOpen, setSettingsOpen] = useState(false);

  // Update violations when metrics change
  useEffect(() => {
    const newViolations = checkBudget();
    setViolations(newViolations);
  }, [currentMetrics, budget, checkBudget]);

  // Update cache size from SSOT
  useEffect(() => {
    trackCacheSize(cacheStats.size);
  }, [cacheStats.size, trackCacheSize]);

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

  const MetricCard: React.FC<{
    title: string;
    value: string | number;
    maxValue: number;
    unit?: string;
    isTime?: boolean;
    isBytes?: boolean;
  }> = ({ title, value, maxValue, unit = '', isTime = false, isBytes = false }) => {
    const percentage = Math.min((Number(value) / maxValue) * 100, 100);
    const isOverBudget = percentage > 100;
    
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="h6" component="div">
              {title}
            </Typography>
            <Chip
              label={isOverBudget ? 'Over Budget' : 'Within Budget'}
              color={isOverBudget ? 'error' : 'success'}
              size="small"
            />
          </Box>
          <Typography variant="h4" component="div" sx={{ mb: 1 }}>
            {isTime ? formatTime(Number(value)) : isBytes ? formatBytes(Number(value)) : value}
            {unit && ` ${unit}`}
          </Typography>
          <LinearProgress
            variant="determinate"
            value={percentage}
            color={isOverBudget ? 'error' : 'primary'}
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Budget: {isTime ? formatTime(maxValue) : isBytes ? formatBytes(maxValue) : maxValue}{unit}
          </Typography>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Performance Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={() => window.location.reload()}
          >
            Refresh
          </Button>
          <IconButton onClick={() => setSettingsOpen(true)}>
            <SettingsIcon />
          </IconButton>
        </Box>
      </Box>

      {/* Performance Score */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography variant="h6">Overall Performance Score</Typography>
            <Chip
              label={`${performanceScore}/100`}
              color={getScoreColor(performanceScore)}
              size="medium"
            />
          </Box>
          <LinearProgress
            variant="determinate"
            value={performanceScore}
            color={getScoreColor(performanceScore)}
            sx={{ height: 12, borderRadius: 6 }}
          />
        </CardContent>
      </Card>

      {/* Violations Alert */}
      {violations.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Performance Budget Violations ({violations.length})
          </Typography>
          <ul>
            {violations.map((violation, index) => (
              <li key={index}>{violation}</li>
            ))}
          </ul>
        </Alert>
      )}

      {/* Metrics Grid */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Bundle Size"
            value={currentMetrics.bundleSize}
            maxValue={budget.maxBundleSize}
            isBytes
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Load Time"
            value={currentMetrics.loadTime}
            maxValue={budget.maxLoadTime}
            isTime
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Memory Usage"
            value={currentMetrics.memoryUsage}
            maxValue={budget.maxMemoryUsage}
            isBytes
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="API Response Time"
            value={currentMetrics.apiResponseTime}
            maxValue={budget.maxApiResponseTime}
            isTime
          />
        </Grid>
      </Grid>

      {/* SSOT-Specific Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Cache Size"
            value={currentMetrics.cacheSize}
            maxValue={budget.maxCacheSize}
            unit="items"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Alias Resolution"
            value={currentMetrics.aliasResolutionTime}
            maxValue={budget.maxAliasResolutionTime}
            isTime
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cache Hit Rate
              </Typography>
              <Typography variant="h4" color="primary">
                {cacheHitRate}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {currentMetrics.ssotCacheHits} hits / {currentMetrics.ssotCacheHits + currentMetrics.ssotCacheMisses} total
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                API Success Rate
              </Typography>
              <Typography variant="h4" color="primary">
                {apiSuccessRate}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {currentMetrics.totalApiCalls - currentMetrics.failedApiCalls} / {currentMetrics.totalApiCalls} calls
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Metrics Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Detailed Metrics
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Metric</TableCell>
                  <TableCell>Current Value</TableCell>
                  <TableCell>Budget</TableCell>
                  <TableCell>Status</TableCell>
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
                </TableRow>
                <TableRow>
                  <TableCell>Cache Size</TableCell>
                  <TableCell>{currentMetrics.cacheSize} items</TableCell>
                  <TableCell>{budget.maxCacheSize} items</TableCell>
                  <TableCell>
                    <Chip
                      icon={currentMetrics.cacheSize > budget.maxCacheSize ? <ErrorIcon /> : <CheckCircleIcon />}
                      label={currentMetrics.cacheSize > budget.maxCacheSize ? 'Over Budget' : 'Within Budget'}
                      color={currentMetrics.cacheSize > budget.maxCacheSize ? 'error' : 'success'}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell>Alias Resolution Time</TableCell>
                  <TableCell>{formatTime(currentMetrics.aliasResolutionTime)}</TableCell>
                  <TableCell>{formatTime(budget.maxAliasResolutionTime)}</TableCell>
                  <TableCell>
                    <Chip
                      icon={currentMetrics.aliasResolutionTime > budget.maxAliasResolutionTime ? <ErrorIcon /> : <CheckCircleIcon />}
                      label={currentMetrics.aliasResolutionTime > budget.maxAliasResolutionTime ? 'Over Budget' : 'Within Budget'}
                      color={currentMetrics.aliasResolutionTime > budget.maxAliasResolutionTime ? 'error' : 'success'}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Performance Budget Settings</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Adjust performance budgets to match your application requirements.
          </Typography>
          {/* Add budget adjustment controls here */}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Cancel</Button>
          <Button onClick={() => setSettingsOpen(false)} variant="contained">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PerformanceDashboard;
