import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Divider,
  Alert,
  Snackbar,
  Tooltip,
  Fab,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  LinearProgress,
  Badge,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Shield,
  Warning,
  CheckCircle,
  Error,
  Info,
  Timeline,
  Assessment,
  Policy,
  Assignment,
  VerifiedUser,
  Lock,
  Visibility,
  VisibilityOff,
  Refresh,
  PlayArrow,
  Stop,
  Settings,
  Notifications,
  Dashboard,
  Analytics,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

interface SecurityStatus {
  framework_running: boolean;
  total_policies: number;
  enabled_policies: number;
  total_audit_events: number;
  recent_audit_events: number;
  total_alerts: number;
  unacknowledged_alerts: number;
  total_compliance_checks: number;
  compliant_checks: number;
  compliance_score: number;
}

interface AuditEvent {
  event_id: string;
  event_type: string;
  user_id?: string;
  resource_id?: string;
  action: string;
  details: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  timestamp: string;
  success: boolean;
  risk_score: number;
}

interface SecurityAlert {
  alert_id: string;
  threat_level: string;
  alert_type: string;
  title: string;
  description: string;
  source: string;
  details: Record<string, any>;
  timestamp: string;
  acknowledged: boolean;
  resolved: boolean;
  assigned_to?: string;
}

interface ComplianceCheck {
  check_id: string;
  standard: string;
  check_name: string;
  description: string;
  requirements: string[];
  status: string;
  last_check: string;
  next_check: string;
  results: Record<string, any>;
  violations: string[];
}

const SecurityDashboard: React.FC = () => {
  const [securityStatus, setSecurityStatus] = useState<SecurityStatus | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [securityAlerts, setSecurityAlerts] = useState<SecurityAlert[]>([]);
  const [complianceChecks, setComplianceChecks] = useState<ComplianceCheck[]>([]);
  const [activeTab, setActiveTab] = useState(0);
  const [isLoggingEvent, setIsLoggingEvent] = useState(false);
  const [isAcknowledgingAlert, setIsAcknowledgingAlert] = useState(false);
  const [isRunningComplianceCheck, setIsRunningComplianceCheck] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' | 'warning' | 'info' });
  const [loading, setLoading] = useState(false);

  const threatLevelColors: Record<string, string> = {
    info: '#2196f3',
    low: '#4caf50',
    medium: '#ff9800',
    high: '#f44336',
    critical: '#9c27b0',
  };

  const complianceStatusColors: Record<string, string> = {
    compliant: '#4caf50',
    non_compliant: '#f44336',
    pending: '#ff9800',
    error: '#9c27b0',
  };

  const loadSecurityStatus = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/security/status');
      const data = await response.json();
      if (data.success) {
        setSecurityStatus(data.data);
      }
    } catch (error) {
      console.error('Error loading security status:', error);
      setSnackbar({ open: true, message: 'Failed to load security status', severity: 'error' });
    } finally {
      setLoading(false);
    }
  }, []);

  const loadAuditEvents = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/security/audit/events?limit=50');
      const data = await response.json();
      if (data.success) {
        setAuditEvents(data.data.events);
      }
    } catch (error) {
      console.error('Error loading audit events:', error);
    }
  }, []);

  const loadSecurityAlerts = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/security/alerts?limit=50');
      const data = await response.json();
      if (data.success) {
        setSecurityAlerts(data.data.alerts);
      }
    } catch (error) {
      console.error('Error loading security alerts:', error);
    }
  }, []);

  const loadComplianceChecks = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/security/compliance/checks');
      const data = await response.json();
      if (data.success) {
        setComplianceChecks(data.data.checks);
      }
    } catch (error) {
      console.error('Error loading compliance checks:', error);
    }
  }, []);

  useEffect(() => {
    loadSecurityStatus();
    loadAuditEvents();
    loadSecurityAlerts();
    loadComplianceChecks();
  }, [loadSecurityStatus, loadAuditEvents, loadSecurityAlerts, loadComplianceChecks]);

  const handleLogAuditEvent = async (eventData: {
    event_type: string;
    action: string;
    user_id?: string;
    resource_id?: string;
    details?: Record<string, any>;
    ip_address?: string;
    user_agent?: string;
    success?: boolean;
  }) => {
    try {
      setIsLoggingEvent(true);
      const response = await fetch('/api/v1/security/audit/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(eventData),
      });
      const data = await response.json();
      if (data.success) {
        setSnackbar({ open: true, message: 'Audit event logged successfully', severity: 'success' });
        loadAuditEvents();
      } else {
        setSnackbar({ open: true, message: data.message || 'Failed to log audit event', severity: 'error' });
      }
    } catch (error) {
      console.error('Error logging audit event:', error);
      setSnackbar({ open: true, message: 'Failed to log audit event', severity: 'error' });
    } finally {
      setIsLoggingEvent(false);
    }
  };

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      setIsAcknowledgingAlert(true);
      const response = await fetch(`/api/v1/security/alerts/${alertId}/acknowledge`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        setSnackbar({ open: true, message: 'Alert acknowledged successfully', severity: 'success' });
        loadSecurityAlerts();
      } else {
        setSnackbar({ open: true, message: data.message || 'Failed to acknowledge alert', severity: 'error' });
      }
    } catch (error) {
      console.error('Error acknowledging alert:', error);
      setSnackbar({ open: true, message: 'Failed to acknowledge alert', severity: 'error' });
    } finally {
      setIsAcknowledgingAlert(false);
    }
  };

  const handleResolveAlert = async (alertId: string) => {
    try {
      const response = await fetch(`/api/v1/security/alerts/${alertId}/resolve`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        setSnackbar({ open: true, message: 'Alert resolved successfully', severity: 'success' });
        loadSecurityAlerts();
      } else {
        setSnackbar({ open: true, message: data.message || 'Failed to resolve alert', severity: 'error' });
      }
    } catch (error) {
      console.error('Error resolving alert:', error);
      setSnackbar({ open: true, message: 'Failed to resolve alert', severity: 'error' });
    }
  };

  const handleRunComplianceCheck = async (checkId: string) => {
    try {
      setIsRunningComplianceCheck(true);
      const response = await fetch(`/api/v1/security/compliance/checks/${checkId}/run`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        setSnackbar({ open: true, message: 'Compliance check completed', severity: 'success' });
        loadComplianceChecks();
      } else {
        setSnackbar({ open: true, message: data.message || 'Failed to run compliance check', severity: 'error' });
      }
    } catch (error) {
      console.error('Error running compliance check:', error);
      setSnackbar({ open: true, message: 'Failed to run compliance check', severity: 'error' });
    } finally {
      setIsRunningComplianceCheck(false);
    }
  };

  const generateAuditChartData = () => {
    const last24Hours = auditEvents.filter(event => {
      const eventTime = new Date(event.timestamp);
      const now = new Date();
      return (now.getTime() - eventTime.getTime()) <= 24 * 60 * 60 * 1000;
    });

    const hourlyData = Array.from({ length: 24 }, (_, i) => {
      const hour = new Date();
      hour.setHours(hour.getHours() - (23 - i));
      const hourStart = new Date(hour);
      hourStart.setMinutes(0, 0, 0);
      const hourEnd = new Date(hour);
      hourEnd.setMinutes(59, 59, 999);

      const eventsInHour = last24Hours.filter(event => {
        const eventTime = new Date(event.timestamp);
        return eventTime >= hourStart && eventTime <= hourEnd;
      });

      return {
        hour: hour.getHours(),
        events: eventsInHour.length,
        successful: eventsInHour.filter(e => e.success).length,
        failed: eventsInHour.filter(e => !e.success).length,
        highRisk: eventsInHour.filter(e => e.risk_score > 0.7).length,
      };
    });

    return hourlyData;
  };

  const generateComplianceChartData = () => {
    const complianceData = complianceChecks.map(check => ({
      name: check.check_name,
      status: check.status,
      violations: check.violations.length,
    }));

    return complianceData;
  };

  const generateThreatLevelData = () => {
    const threatData = securityAlerts.reduce((acc, alert) => {
      acc[alert.threat_level] = (acc[alert.threat_level] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(threatData).map(([level, count]) => ({
      name: level,
      value: count,
      color: threatLevelColors[level] || '#666',
    }));
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Security Dashboard
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
        Zero Trust Security Framework and Compliance Monitoring
      </Typography>

      {/* Security Status */}
      {securityStatus && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Security Framework Status
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color={securityStatus.framework_running ? 'success.main' : 'error.main'}>
                  {securityStatus.framework_running ? '🟢' : '🔴'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Framework Status
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary.main">
                  {securityStatus.total_policies}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Security Policies
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="warning.main">
                  {securityStatus.unacknowledged_alerts}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Unacknowledged Alerts
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="success.main">
                  {securityStatus.compliance_score.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Compliance Score
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Main Content */}
      <Paper sx={{ p: 2 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 2 }}>
          <Tab label="Audit Events" icon={<Assignment />} />
          <Tab label="Security Alerts" icon={<Warning />} />
          <Tab label="Compliance" icon={<VerifiedUser />} />
          <Tab label="Analytics" icon={<Analytics />} />
        </Tabs>

        {/* Audit Events Tab */}
        {activeTab === 0 && (
          <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Recent Audit Events</Typography>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadAuditEvents}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Event Type</TableCell>
                    <TableCell>Action</TableCell>
                    <TableCell>User</TableCell>
                    <TableCell>Success</TableCell>
                    <TableCell>Risk Score</TableCell>
                    <TableCell>Timestamp</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {auditEvents.slice(0, 20).map((event) => (
                    <TableRow key={event.event_id}>
                      <TableCell>
                        <Chip
                          label={event.event_type}
                          size="small"
                          color={event.success ? 'success' : 'error'}
                        />
                      </TableCell>
                      <TableCell>{event.action}</TableCell>
                      <TableCell>{event.user_id || 'N/A'}</TableCell>
                      <TableCell>
                        {event.success ? (
                          <CheckCircle color="success" />
                        ) : (
                          <Error color="error" />
                        )}
                      </TableCell>
                      <TableCell>
                        <LinearProgress
                          variant="determinate"
                          value={event.risk_score * 100}
                          color={event.risk_score > 0.7 ? 'error' : event.risk_score > 0.4 ? 'warning' : 'success'}
                        />
                        <Typography variant="caption">
                          {(event.risk_score * 100).toFixed(1)}%
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {new Date(event.timestamp).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* Security Alerts Tab */}
        {activeTab === 1 && (
          <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Security Alerts</Typography>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadSecurityAlerts}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>
            
            <Grid container spacing={2}>
              {securityAlerts.slice(0, 12).map((alert) => (
                <Grid item xs={12} sm={6} md={4} key={alert.alert_id}>
                  <Card>
                    <CardContent>
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        <Chip
                          label={alert.threat_level}
                          size="small"
                          sx={{ backgroundColor: threatLevelColors[alert.threat_level], color: 'white' }}
                        />
                        {alert.acknowledged && <CheckCircle color="success" />}
                        {alert.resolved && <CheckCircle color="success" />}
                      </Box>
                      <Typography variant="h6" noWrap>
                        {alert.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {alert.description}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Source: {alert.source}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {new Date(alert.timestamp).toLocaleString()}
                      </Typography>
                    </CardContent>
                    <CardActions>
                      {!alert.acknowledged && (
                        <Button
                          size="small"
                          onClick={() => handleAcknowledgeAlert(alert.alert_id)}
                          disabled={isAcknowledgingAlert}
                        >
                          Acknowledge
                        </Button>
                      )}
                      {!alert.resolved && (
                        <Button
                          size="small"
                          onClick={() => handleResolveAlert(alert.alert_id)}
                        >
                          Resolve
                        </Button>
                      )}
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Compliance Tab */}
        {activeTab === 2 && (
          <Box>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Compliance Checks</Typography>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadComplianceChecks}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>
            
            <Grid container spacing={2}>
              {complianceChecks.map((check) => (
                <Grid item xs={12} sm={6} md={4} key={check.check_id}>
                  <Card>
                    <CardContent>
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        <Chip
                          label={check.status}
                          size="small"
                          sx={{ backgroundColor: complianceStatusColors[check.status], color: 'white' }}
                        />
                        <Chip
                          label={check.standard}
                          variant="outlined"
                          size="small"
                        />
                      </Box>
                      <Typography variant="h6" noWrap>
                        {check.check_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {check.description}
                      </Typography>
                      {check.violations.length > 0 && (
                        <Alert severity="error" sx={{ mb: 1 }}>
                          {check.violations.length} violations found
                        </Alert>
                      )}
                      <Typography variant="caption" color="text.secondary" display="block">
                        Last check: {new Date(check.last_check).toLocaleString()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        Next check: {new Date(check.next_check).toLocaleString()}
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button
                        size="small"
                        startIcon={<PlayArrow />}
                        onClick={() => handleRunComplianceCheck(check.check_id)}
                        disabled={isRunningComplianceCheck}
                      >
                        Run Check
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Analytics Tab */}
        {activeTab === 3 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Security Analytics
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Audit Events (Last 24 Hours)
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={generateAuditChartData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="hour" />
                      <YAxis />
                      <RechartsTooltip />
                      <Line type="monotone" dataKey="events" stroke="#8884d8" strokeWidth={2} />
                      <Line type="monotone" dataKey="successful" stroke="#82ca9d" strokeWidth={2} />
                      <Line type="monotone" dataKey="failed" stroke="#ff7300" strokeWidth={2} />
                      <Line type="monotone" dataKey="highRisk" stroke="#ff0000" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>

              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Threat Level Distribution
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={generateThreatLevelData()}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {generateThreatLevelData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>

              <Grid item xs={12}>
                <Paper sx={{ p: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Compliance Status
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={generateComplianceChartData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <RechartsTooltip />
                      <Bar dataKey="violations" fill="#ff7300" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            </Grid>
          </Box>
        )}
      </Paper>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SecurityDashboard;
