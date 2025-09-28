import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  TextField,
  Chip,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
} from '@mui/material';
import {
  Settings,
  PlayArrow,
  Pause,
  Stop,
  Add,
  Edit,
  Delete,
  Refresh,
  CheckCircle,
  Error,
  Schedule,
  TrendingUp,
  Assessment,
  ExpandMore,
  Visibility,
  VisibilityOff,
  GetApp,
  Upload,
  Download,
} from '@mui/icons-material';
import { automationService } from '../../services/automationService';

interface AutomationRule {
  rule_id: string;
  name: string;
  description: string;
  automation_type: 'scheduled' | 'event_driven' | 'conditional' | 'ai_driven' | 'self_optimizing';
  trigger_type: 'time' | 'event' | 'condition' | 'ai_prediction' | 'user_action';
  enabled: boolean;
  priority: number;
  execution_count: number;
  success_count: number;
  failure_count: number;
  created_at: string;
  last_executed?: string;
}

interface AutomationExecution {
  execution_id: string;
  rule_id: string;
  status: 'active' | 'paused' | 'completed' | 'failed' | 'disabled';
  started_at: string;
  completed_at?: string;
  execution_time?: number;
  result?: any;
  error_message?: string;
}

interface AutomationMetrics {
  total_rules: number;
  active_rules: number;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  average_execution_time: number;
  automation_efficiency: number;
  last_updated: string;
}

const AutomationDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [rules, setRules] = useState<AutomationRule[]>([]);
  const [executions, setExecutions] = useState<AutomationExecution[]>([]);
  const [metrics, setMetrics] = useState<AutomationMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [templateDialogOpen, setTemplateDialogOpen] = useState(false);
  const [selectedRule, setSelectedRule] = useState<AutomationRule | null>(null);

  // Form states
  const [ruleForm, setRuleForm] = useState({
    name: '',
    description: '',
    automation_type: 'scheduled',
    trigger_type: 'time',
    enabled: true,
    priority: 1,
    trigger_config: {},
    actions: [],
    conditions: []
  });

  useEffect(() => {
    loadRules();
    loadExecutions();
    loadMetrics();
  }, []);

  const loadRules = async () => {
    try {
      setIsLoading(true);
      const response = await automationService.getRules();
      setRules(response.rules);
    } catch (error) {
      setError('Failed to load automation rules');
    } finally {
      setIsLoading(false);
    }
  };

  const loadExecutions = async () => {
    try {
      const response = await automationService.getExecutions();
      setExecutions(response.executions);
    } catch (error) {
      console.error('Failed to load executions:', error);
    }
  };

  const loadMetrics = async () => {
    try {
      const response = await automationService.getMetrics();
      setMetrics(response);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  };

  const handleCreateRule = async () => {
    try {
      setIsLoading(true);
      await automationService.createRule(ruleForm);
      setCreateDialogOpen(false);
      setRuleForm({
        name: '',
        description: '',
        automation_type: 'scheduled',
        trigger_type: 'time',
        enabled: true,
        priority: 1,
        trigger_config: {},
        actions: [],
        conditions: []
      });
      loadRules();
    } catch (error) {
      setError('Failed to create automation rule');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateRule = async (ruleId: string, updates: any) => {
    try {
      await automationService.updateRule(ruleId, updates);
      loadRules();
    } catch (error) {
      setError('Failed to update automation rule');
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    try {
      await automationService.deleteRule(ruleId);
      loadRules();
    } catch (error) {
      setError('Failed to delete automation rule');
    }
  };

  const handleExecuteRule = async (ruleId: string) => {
    try {
      await automationService.executeRule(ruleId);
      loadExecutions();
    } catch (error) {
      setError('Failed to execute automation rule');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'failed':
        return <Error color="error" />;
      case 'active':
        return <PlayArrow color="primary" />;
      case 'paused':
        return <Pause color="warning" />;
      default:
        return <Stop color="disabled" />;
    }
  };

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1:
        return 'error';
      case 2:
        return 'warning';
      case 3:
        return 'info';
      default:
        return 'default';
    }
  };

  const renderRulesTab = () => (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">Automation Rules</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<GetApp />}
            onClick={() => setTemplateDialogOpen(true)}
            sx={{ mr: 2 }}
          >
            Templates
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Rule
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {rules.map((rule) => (
          <Grid item xs={12} md={6} lg={4} key={rule.rule_id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" noWrap>
                    {rule.name}
                  </Typography>
                  <Box>
                    <Chip
                      label={rule.automation_type}
                      size="small"
                      color="primary"
                      sx={{ mr: 1 }}
                    />
                    <Chip
                      label={`Priority ${rule.priority}`}
                      size="small"
                      color={getPriorityColor(rule.priority) as any}
                    />
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {rule.description}
                </Typography>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={rule.enabled}
                        onChange={(e) => handleUpdateRule(rule.rule_id, { enabled: e.target.checked })}
                        size="small"
                      />
                    }
                    label="Enabled"
                  />
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Executions: {rule.execution_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Success: {rule.success_count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Failed: {rule.failure_count}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Button
                    size="small"
                    startIcon={<PlayArrow />}
                    onClick={() => handleExecuteRule(rule.rule_id)}
                  >
                    Execute
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Edit />}
                    onClick={() => {
                      setSelectedRule(rule);
                      setEditDialogOpen(true);
                    }}
                  >
                    Edit
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Delete />}
                    color="error"
                    onClick={() => handleDeleteRule(rule.rule_id)}
                  >
                    Delete
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderExecutionsTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Execution History
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Rule ID</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Started At</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Result</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {executions.map((execution) => (
              <TableRow key={execution.execution_id}>
                <TableCell>{execution.rule_id}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {getStatusIcon(execution.status)}
                    <Typography variant="body2" sx={{ ml: 1 }}>
                      {execution.status}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  {new Date(execution.started_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  {execution.execution_time ? `${execution.execution_time.toFixed(2)}s` : 'N/A'}
                </TableCell>
                <TableCell>
                  {execution.result ? (
                    <Tooltip title={JSON.stringify(execution.result, null, 2)}>
                      <Button size="small">View</Button>
                    </Tooltip>
                  ) : (
                    'N/A'
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderMetricsTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Automation Metrics
      </Typography>

      {metrics && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="primary">
                  {metrics.total_rules}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Rules
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="success.main">
                  {metrics.active_rules}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Rules
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="info.main">
                  {metrics.total_executions}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Executions
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="warning.main">
                  {(metrics.automation_efficiency * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Efficiency
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Performance Overview
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Successful Executions: {metrics?.successful_executions || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Failed Executions: {metrics?.failed_executions || 0}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Average Execution Time: {metrics?.average_execution_time.toFixed(2) || 0}s
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last Updated: {metrics ? new Date(metrics.last_updated).toLocaleString() : 'N/A'}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Intelligent Automation Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {isLoading && <LinearProgress sx={{ mb: 3 }} />}

      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Rules" icon={<Settings />} />
            <Tab label="Executions" icon={<Schedule />} />
            <Tab label="Metrics" icon={<TrendingUp />} />
          </Tabs>
        </Box>

        {activeTab === 0 && renderRulesTab()}
        {activeTab === 1 && renderExecutionsTab()}
        {activeTab === 2 && renderMetricsTab()}
      </Card>

      {/* Create Rule Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Automation Rule</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Rule Name"
                value={ruleForm.name}
                onChange={(e) => setRuleForm({ ...ruleForm, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Automation Type</InputLabel>
                <Select
                  value={ruleForm.automation_type}
                  onChange={(e) => setRuleForm({ ...ruleForm, automation_type: e.target.value })}
                >
                  <MenuItem value="scheduled">Scheduled</MenuItem>
                  <MenuItem value="event_driven">Event Driven</MenuItem>
                  <MenuItem value="conditional">Conditional</MenuItem>
                  <MenuItem value="ai_driven">AI Driven</MenuItem>
                  <MenuItem value="self_optimizing">Self Optimizing</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={ruleForm.description}
                onChange={(e) => setRuleForm({ ...ruleForm, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Trigger Type</InputLabel>
                <Select
                  value={ruleForm.trigger_type}
                  onChange={(e) => setRuleForm({ ...ruleForm, trigger_type: e.target.value })}
                >
                  <MenuItem value="time">Time</MenuItem>
                  <MenuItem value="event">Event</MenuItem>
                  <MenuItem value="condition">Condition</MenuItem>
                  <MenuItem value="ai_prediction">AI Prediction</MenuItem>
                  <MenuItem value="user_action">User Action</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Priority"
                value={ruleForm.priority}
                onChange={(e) => setRuleForm({ ...ruleForm, priority: parseInt(e.target.value) })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateRule} variant="contained">
            Create Rule
          </Button>
        </DialogActions>
      </Dialog>

      {/* Template Dialog */}
      <Dialog open={templateDialogOpen} onClose={() => setTemplateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Automation Templates</DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            Choose from pre-built automation templates to quickly create common automation rules.
          </Typography>
          {/* Template selection would go here */}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTemplateDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AutomationDashboard;
