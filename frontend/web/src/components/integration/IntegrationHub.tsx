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
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Add,
  Edit,
  Delete,
  Save,
  Refresh,
  Settings,
  Timeline,
  CheckCircle,
  Error,
  Schedule,
  Webhook,
  Api,
  Dataset,
  Email,
  Sms,
  Chat,
  Microsoft,
  Cloud,
  Extension,
  IntegrationInstructions,
  Sync,
  Science,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

interface IntegrationConfig {
  integration_id: string;
  name: string;
  integration_type: string;
  status: string;
  config: Record<string, any>;
  webhook_url?: string;
  api_endpoints: string[];
  sync_direction: string;
  sync_frequency: number;
  retry_count: number;
  timeout_seconds: number;
  created_at: string;
  updated_at: string;
  created_by: string;
}

interface SyncJob {
  job_id: string;
  integration_id: string;
  status: string;
  started_at: string;
  completed_at?: string;
  records_processed: number;
  records_successful: number;
  records_failed: number;
  sync_direction: string;
  error_message?: string;
}

interface WebhookEvent {
  event_id: string;
  integration_id: string;
  event_type: string;
  received_at: string;
  processed: boolean;
  processed_at?: string;
  error_message?: string;
}

const IntegrationHub: React.FC = () => {
  const [integrations, setIntegrations] = useState<IntegrationConfig[]>([]);
  const [syncJobs, setSyncJobs] = useState<SyncJob[]>([]);
  const [webhookEvents, setWebhookEvents] = useState<WebhookEvent[]>([]);
  const [selectedIntegration, setSelectedIntegration] = useState<IntegrationConfig | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isTestDialogOpen, setIsTestDialogOpen] = useState(false);
  const [isSyncDialogOpen, setIsSyncDialogOpen] = useState(false);
  const [isCreatingIntegration, setIsCreatingIntegration] = useState(false);
  const [newIntegration, setNewIntegration] = useState({
    name: '',
    integration_type: 'rest_api',
    config: {},
    credentials: {},
    webhook_url: '',
    api_endpoints: [],
    sync_direction: 'outbound',
    sync_frequency: 300,
    retry_count: 3,
    timeout_seconds: 30,
  });
  const [hubStatus, setHubStatus] = useState<any>(null);
  const [integrationTypes, setIntegrationTypes] = useState<any[]>([]);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' | 'warning' | 'info' });
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [showCredentials, setShowCredentials] = useState<Record<string, boolean>>({});

  const integrationTypeIcons: Record<string, React.ReactElement> = {
    rest_api: <Api />,
    graphql: <Api />,
    webhook: <Webhook />,
    database: <Dataset />,
    message_queue: <Timeline />,
    file_system: <Settings />,
    email: <Email />,
    sms: <Sms />,
    slack: <Chat />,
    microsoft_teams: <Microsoft />,
    salesforce: <Cloud />,
    hubspot: <Cloud />,
    zapier: <Extension />,
    ifttt: <IntegrationInstructions />,
  };

  const integrationTypeColors: Record<string, string> = {
    rest_api: '#4caf50',
    graphql: '#e91e63',
    webhook: '#ff9800',
    database: '#2196f3',
    message_queue: '#9c27b0',
    file_system: '#795548',
    email: '#607d8b',
    sms: '#00bcd4',
    slack: '#4a154b',
    microsoft_teams: '#6264a7',
    salesforce: '#00a1e0',
    hubspot: '#ff7a59',
    zapier: '#ff4a00',
    ifttt: '#00c4cc',
  };

  const loadIntegrations = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/integrations/list');
      const data = await response.json();
      if (data.success) {
        setIntegrations(data.data.integrations);
      }
    } catch (error) {
      console.error('Error loading integrations:', error);
      setSnackbar({ open: true, message: 'Failed to load integrations', severity: 'error' });
    } finally {
      setLoading(false);
    }
  }, []);

  const loadSyncJobs = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/integrations/sync-jobs/list');
      const data = await response.json();
      if (data.success) {
        setSyncJobs(data.data.sync_jobs);
      }
    } catch (error) {
      console.error('Error loading sync jobs:', error);
    }
  }, []);

  const loadWebhookEvents = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/integrations/webhook-events/list');
      const data = await response.json();
      if (data.success) {
        setWebhookEvents(data.data.webhook_events);
      }
    } catch (error) {
      console.error('Error loading webhook events:', error);
    }
  }, []);

  const loadHubStatus = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/integrations/status');
      const data = await response.json();
      if (data.success) {
        setHubStatus(data.data);
      }
    } catch (error) {
      console.error('Error loading hub status:', error);
    }
  }, []);

  const loadIntegrationTypes = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/integrations/types');
      const data = await response.json();
      if (data.success) {
        setIntegrationTypes(data.data.integration_types);
      }
    } catch (error) {
      console.error('Error loading integration types:', error);
    }
  }, []);

  useEffect(() => {
    loadIntegrations();
    loadSyncJobs();
    loadWebhookEvents();
    loadHubStatus();
    loadIntegrationTypes();
  }, [loadIntegrations, loadSyncJobs, loadWebhookEvents, loadHubStatus, loadIntegrationTypes]);

  const handleCreateIntegration = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/integrations/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newIntegration),
      });
      const data = await response.json();
      if (data.success) {
        setSnackbar({ open: true, message: 'Integration created successfully', severity: 'success' });
        setIsCreateDialogOpen(false);
        setNewIntegration({
          name: '',
          integration_type: 'rest_api',
          config: {},
          credentials: {},
          webhook_url: '',
          api_endpoints: [],
          sync_direction: 'outbound',
          sync_frequency: 300,
          retry_count: 3,
          timeout_seconds: 30,
        });
        loadIntegrations();
      } else {
        setSnackbar({ open: true, message: data.message || 'Failed to create integration', severity: 'error' });
      }
    } catch (error) {
      console.error('Error creating integration:', error);
      setSnackbar({ open: true, message: 'Failed to create integration', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleTestIntegration = async (integrationId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/integrations/test/${integrationId}`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.success) {
        setSnackbar({ open: true, message: 'Integration test successful', severity: 'success' });
      } else {
        setSnackbar({ open: true, message: data.message || 'Integration test failed', severity: 'error' });
      }
    } catch (error) {
      console.error('Error testing integration:', error);
      setSnackbar({ open: true, message: 'Failed to test integration', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleSyncIntegration = async (integrationId: string, direction?: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/integrations/sync/${integrationId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ direction }),
      });
      const data = await response.json();
      if (data.success) {
        setSnackbar({ open: true, message: 'Sync job started successfully', severity: 'success' });
        loadSyncJobs();
      } else {
        setSnackbar({ open: true, message: data.message || 'Failed to start sync', severity: 'error' });
      }
    } catch (error) {
      console.error('Error starting sync:', error);
      setSnackbar({ open: true, message: 'Failed to start sync', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'pending': return 'warning';
      case 'testing': return 'info';
      case 'inactive': return 'default';
      default: return 'default';
    }
  };

  const getSyncStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'running': return 'primary';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  const generateSyncChartData = () => {
    const last24Hours = syncJobs.filter(job => {
      const jobTime = new Date(job.started_at);
      const now = new Date();
      return (now.getTime() - jobTime.getTime()) <= 24 * 60 * 60 * 1000;
    });

    const hourlyData = Array.from({ length: 24 }, (_, i) => {
      const hour = new Date();
      hour.setHours(hour.getHours() - (23 - i));
      const hourStart = new Date(hour);
      hourStart.setMinutes(0, 0, 0);
      const hourEnd = new Date(hour);
      hourEnd.setMinutes(59, 59, 999);

      const jobsInHour = last24Hours.filter(job => {
        const jobTime = new Date(job.started_at);
        return jobTime >= hourStart && jobTime <= hourEnd;
      });

      return {
        hour: hour.getHours(),
        jobs: jobsInHour.length,
        completed: jobsInHour.filter(j => j.status === 'completed').length,
        failed: jobsInHour.filter(j => j.status === 'failed').length,
        records: jobsInHour.reduce((sum, job) => sum + job.records_processed, 0),
      };
    });

    return hourlyData;
  };

  const generateWebhookChartData = () => {
    const last24Hours = webhookEvents.filter(event => {
      const eventTime = new Date(event.received_at);
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
        const eventTime = new Date(event.received_at);
        return eventTime >= hourStart && eventTime <= hourEnd;
      });

      return {
        hour: hour.getHours(),
        events: eventsInHour.length,
        processed: eventsInHour.filter(e => e.processed).length,
        failed: eventsInHour.filter(e => e.error_message).length,
      };
    });

    return hourlyData;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Integration Hub
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
        Enterprise integration management and third-party system connections
      </Typography>

      {/* Hub Status */}
      {hubStatus && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Integration Hub Status
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color={hubStatus.hub_running ? 'success.main' : 'error.main'}>
                  {hubStatus.hub_running ? '🟢' : '🔴'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Hub Status
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary.main">
                  {hubStatus.total_integrations}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Integrations
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="warning.main">
                  {hubStatus.total_sync_jobs}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Sync Jobs
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="info.main">
                  {hubStatus.total_webhook_events}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Webhook Events
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Main Content */}
      <Paper sx={{ p: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Integrations</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setIsCreateDialogOpen(true)}
          >
            Create Integration
          </Button>
        </Box>
        
        <Grid container spacing={2}>
          {integrations.map((integration) => (
            <Grid item xs={12} sm={6} md={4} key={integration.integration_id}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    {integrationTypeIcons[integration.integration_type]}
                    <Typography variant="h6" noWrap>
                      {integration.name}
                    </Typography>
                  </Box>
                  <Box display="flex" gap={1} mb={1}>
                    <Chip
                      label={integration.integration_type}
                      size="small"
                      sx={{ backgroundColor: integrationTypeColors[integration.integration_type], color: 'white' }}
                    />
                    <Chip
                      label={integration.status}
                      color={getStatusColor(integration.status) as any}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Sync: {integration.sync_direction} ({integration.sync_frequency}s)
                  </Typography>
                  {integration.webhook_url && (
                    <Typography variant="caption" color="text.secondary" display="block">
                      Webhook: {integration.webhook_url}
                    </Typography>
                  )}
                  <Typography variant="caption" color="text.secondary" display="block">
                    Created: {new Date(integration.created_at).toLocaleDateString()}
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    startIcon={<Science />}
                    onClick={() => handleTestIntegration(integration.integration_id)}
                    disabled={loading}
                  >
                    Test
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Sync />}
                    onClick={() => handleSyncIntegration(integration.integration_id)}
                    disabled={loading}
                  >
                    Sync
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Edit />}
                    onClick={() => {
                      setSelectedIntegration(integration);
                      setIsCreateDialogOpen(true);
                    }}
                  >
                    Edit
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Analytics */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Sync Jobs (Last 24 Hours)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={generateSyncChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <RechartsTooltip />
                <Line type="monotone" dataKey="jobs" stroke="#8884d8" strokeWidth={2} />
                <Line type="monotone" dataKey="completed" stroke="#82ca9d" strokeWidth={2} />
                <Line type="monotone" dataKey="failed" stroke="#ff7300" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Webhook Events (Last 24 Hours)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={generateWebhookChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <RechartsTooltip />
                <Bar dataKey="events" fill="#8884d8" />
                <Bar dataKey="processed" fill="#82ca9d" />
                <Bar dataKey="failed" fill="#ff7300" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Sync Jobs
            </Typography>
            <List>
              {syncJobs.slice(0, 5).map((job) => (
                <ListItem key={job.job_id}>
                  <ListItemIcon>
                    <Chip
                      label={job.status}
                      color={getSyncStatusColor(job.status) as any}
                      size="small"
                    />
                  </ListItemIcon>
                  <ListItemText
                    primary={job.integration_id}
                    secondary={
                      <Box>
                        <Typography variant="caption" display="block">
                          {new Date(job.started_at).toLocaleString()}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Records: {job.records_processed} | Success: {job.records_successful} | Failed: {job.records_failed}
                        </Typography>
                        {job.error_message && (
                          <Typography variant="caption" color="error" display="block">
                            Error: {job.error_message}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Webhook Events
            </Typography>
            <List>
              {webhookEvents.slice(0, 5).map((event) => (
                <ListItem key={event.event_id}>
                  <ListItemIcon>
                    <Badge
                      color={event.processed ? 'success' : 'warning'}
                      variant="dot"
                    >
                      <Webhook />
                    </Badge>
                  </ListItemIcon>
                  <ListItemText
                    primary={event.event_type}
                    secondary={
                      <Box>
                        <Typography variant="caption" display="block">
                          {new Date(event.received_at).toLocaleString()}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Integration: {event.integration_id}
                        </Typography>
                        {event.error_message && (
                          <Typography variant="caption" color="error" display="block">
                            Error: {event.error_message}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Create Integration Dialog */}
      <Dialog open={isCreateDialogOpen} onClose={() => setIsCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Integration</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Integration Name"
            value={newIntegration.name}
            onChange={(e) => setNewIntegration(prev => ({ ...prev, name: e.target.value }))}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Integration Type</InputLabel>
            <Select
              value={newIntegration.integration_type}
              onChange={(e) => setNewIntegration(prev => ({ ...prev, integration_type: e.target.value }))}
            >
              {integrationTypes.map((type) => (
                <MenuItem key={type.type} value={type.type}>
                  {type.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Webhook URL"
            value={newIntegration.webhook_url}
            onChange={(e) => setNewIntegration(prev => ({ ...prev, webhook_url: e.target.value }))}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Sync Direction</InputLabel>
            <Select
              value={newIntegration.sync_direction}
              onChange={(e) => setNewIntegration(prev => ({ ...prev, sync_direction: e.target.value }))}
            >
              <MenuItem value="inbound">Inbound</MenuItem>
              <MenuItem value="outbound">Outbound</MenuItem>
              <MenuItem value="bidirectional">Bidirectional</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Sync Frequency (seconds)"
            type="number"
            value={newIntegration.sync_frequency}
            onChange={(e) => setNewIntegration(prev => ({ ...prev, sync_frequency: parseInt(e.target.value) }))}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Retry Count"
            type="number"
            value={newIntegration.retry_count}
            onChange={(e) => setNewIntegration(prev => ({ ...prev, retry_count: parseInt(e.target.value) }))}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Timeout (seconds)"
            type="number"
            value={newIntegration.timeout_seconds}
            onChange={(e) => setNewIntegration(prev => ({ ...prev, timeout_seconds: parseInt(e.target.value) }))}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsCreateDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateIntegration}
            variant="contained"
            disabled={!newIntegration.name || loading}
          >
            Create Integration
          </Button>
        </DialogActions>
      </Dialog>

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

export default IntegrationHub;
