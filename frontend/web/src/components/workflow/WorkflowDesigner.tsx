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
  Transform,
  Notifications,
  Loop,
  Compare,
  Timer,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

interface TaskDefinition {
  task_id: string;
  name: string;
  task_type: string;
  config: Record<string, any>;
  inputs: string[];
  outputs: string[];
  conditions: string[];
  retry_count: number;
  timeout_seconds: number;
  dependencies: string[];
}

interface WorkflowDefinition {
  workflow_id: string;
  name: string;
  description: string;
  version: string;
  status: string;
  tasks: TaskDefinition[];
  variables: Record<string, any>;
  triggers: any[];
  created_at: string;
  updated_at: string;
  created_by: string;
}

interface WorkflowExecution {
  execution_id: string;
  workflow_id: string;
  status: string;
  started_at: string;
  completed_at?: string;
  task_executions: any[];
  variables: Record<string, any>;
  result?: any;
  error_message?: string;
  triggered_by: string;
}

const WorkflowDesigner: React.FC = () => {
  const [workflows, setWorkflows] = useState<WorkflowDefinition[]>([]);
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowDefinition | null>(null);
  const [isDesignerOpen, setIsDesignerOpen] = useState(false);
  const [isExecutionOpen, setIsExecutionOpen] = useState(false);
  const [isCreatingWorkflow, setIsCreatingWorkflow] = useState(false);
  const [newWorkflow, setNewWorkflow] = useState({
    name: '',
    description: '',
    tasks: [] as TaskDefinition[],
  });
  const [newTask, setNewTask] = useState({
    task_id: '',
    name: '',
    task_type: 'action',
    config: {},
    inputs: [],
    outputs: [],
    conditions: [],
    retry_count: 0,
    timeout_seconds: 300,
    dependencies: [],
  });
  const [isTaskDialogOpen, setIsTaskDialogOpen] = useState(false);
  const [engineStatus, setEngineStatus] = useState<any>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' | 'warning' | 'info' });
  const [loading, setLoading] = useState(false);

  const taskTypeIcons: Record<string, React.ReactElement> = {
    action: <CheckCircle />,
    condition: <Compare />,
    loop: <Loop />,
    parallel: <Timeline />,
    sequence: <Timeline />,
    timer: <Timer />,
    webhook: <Webhook />,
    api_call: <Api />,
    data_transform: <Transform />,
    notification: <Notifications />,
  };

  const taskTypeColors: Record<string, string> = {
    action: '#4caf50',
    condition: '#ff9800',
    loop: '#9c27b0',
    parallel: '#2196f3',
    sequence: '#00bcd4',
    timer: '#795548',
    webhook: '#e91e63',
    api_call: '#3f51b5',
    data_transform: '#ff5722',
    notification: '#607d8b',
  };

  const loadWorkflows = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/workflows/list');
      const data = await response.json();
      if (data.success) {
        setWorkflows(data.data.workflows);
      }
    } catch (error) {
      console.error('Error loading workflows:', error);
      setSnackbar({ open: true, message: 'Failed to load workflows', severity: 'error' });
    } finally {
      setLoading(false);
    }
  }, []);

  const loadExecutions = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/workflows/executions/list');
      const data = await response.json();
      if (data.success) {
        setExecutions(data.data.executions);
      }
    } catch (error) {
      console.error('Error loading executions:', error);
    }
  }, []);

  const loadEngineStatus = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/workflows/status');
      const data = await response.json();
      if (data.success) {
        setEngineStatus(data.data);
      }
    } catch (error) {
      console.error('Error loading engine status:', error);
    }
  }, []);

  useEffect(() => {
    loadWorkflows();
    loadExecutions();
    loadEngineStatus();
  }, [loadWorkflows, loadExecutions, loadEngineStatus]);

  const handleCreateWorkflow = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/workflows/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newWorkflow),
      });
      const data = await response.json();
      if (data.success) {
        setSnackbar({ open: true, message: 'Workflow created successfully', severity: 'success' });
        setIsCreatingWorkflow(false);
        setNewWorkflow({ name: '', description: '', tasks: [] });
        loadWorkflows();
      } else {
        setSnackbar({ open: true, message: data.message || 'Failed to create workflow', severity: 'error' });
      }
    } catch (error) {
      console.error('Error creating workflow:', error);
      setSnackbar({ open: true, message: 'Failed to create workflow', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteWorkflow = async (workflowId: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/workflows/execute/${workflowId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      const data = await response.json();
      if (data.success) {
        setSnackbar({ open: true, message: 'Workflow execution started', severity: 'success' });
        loadExecutions();
      } else {
        setSnackbar({ open: true, message: data.message || 'Failed to execute workflow', severity: 'error' });
      }
    } catch (error) {
      console.error('Error executing workflow:', error);
      setSnackbar({ open: true, message: 'Failed to execute workflow', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = () => {
    const taskId = `task_${Date.now()}`;
    const task: TaskDefinition = {
      ...newTask,
      task_id: taskId,
    };
    setNewWorkflow(prev => ({
      ...prev,
      tasks: [...prev.tasks, task],
    }));
    setIsTaskDialogOpen(false);
    setNewTask({
      task_id: '',
      name: '',
      task_type: 'action',
      config: {},
      inputs: [],
      outputs: [],
      conditions: [],
      retry_count: 0,
      timeout_seconds: 300,
      dependencies: [],
    });
  };

  const handleRemoveTask = (taskId: string) => {
    setNewWorkflow(prev => ({
      ...prev,
      tasks: prev.tasks.filter(task => task.task_id !== taskId),
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'paused': return 'warning';
      case 'draft': return 'default';
      default: return 'default';
    }
  };

  const getExecutionStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'primary';
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'cancelled': return 'warning';
      default: return 'default';
    }
  };

  const generateExecutionChartData = () => {
    const last24Hours = executions.filter(exec => {
      const execTime = new Date(exec.started_at);
      const now = new Date();
      return (now.getTime() - execTime.getTime()) <= 24 * 60 * 60 * 1000;
    });

    const hourlyData = Array.from({ length: 24 }, (_, i) => {
      const hour = new Date();
      hour.setHours(hour.getHours() - (23 - i));
      const hourStart = new Date(hour);
      hourStart.setMinutes(0, 0, 0);
      const hourEnd = new Date(hour);
      hourEnd.setMinutes(59, 59, 999);

      const executionsInHour = last24Hours.filter(exec => {
        const execTime = new Date(exec.started_at);
        return execTime >= hourStart && execTime <= hourEnd;
      });

      return {
        hour: hour.getHours(),
        executions: executionsInHour.length,
        completed: executionsInHour.filter(e => e.status === 'completed').length,
        failed: executionsInHour.filter(e => e.status === 'failed').length,
      };
    });

    return hourlyData;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Workflow Designer
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
        Design, manage, and execute enterprise workflows
      </Typography>

      {/* Engine Status */}
      {engineStatus && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Workflow Engine Status
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color={engineStatus.engine_running ? 'success.main' : 'error.main'}>
                  {engineStatus.engine_running ? '🟢' : '🔴'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Engine Status
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary.main">
                  {engineStatus.total_workflows}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Workflows
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="warning.main">
                  {engineStatus.active_executions}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Executions
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="success.main">
                  {engineStatus.completed_executions}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Completed
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Workflow Management */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Workflows</Typography>
              <Button
                variant="contained"
                startIcon={<Add />}
                onClick={() => setIsCreatingWorkflow(true)}
              >
                Create Workflow
              </Button>
            </Box>
            
            <Grid container spacing={2}>
              {workflows.map((workflow) => (
                <Grid item xs={12} sm={6} md={4} key={workflow.workflow_id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" noWrap>
                        {workflow.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {workflow.description}
                      </Typography>
                      <Box display="flex" gap={1} mb={1}>
                        <Chip
                          label={workflow.status}
                          color={getStatusColor(workflow.status) as any}
                          size="small"
                        />
                        <Chip
                          label={`${workflow.task_count} tasks`}
                          variant="outlined"
                          size="small"
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        Created: {new Date(workflow.created_at).toLocaleDateString()}
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button
                        size="small"
                        startIcon={<PlayArrow />}
                        onClick={() => handleExecuteWorkflow(workflow.workflow_id)}
                        disabled={loading}
                      >
                        Execute
                      </Button>
                      <Button
                        size="small"
                        startIcon={<Edit />}
                        onClick={() => {
                          setSelectedWorkflow(workflow);
                          setIsDesignerOpen(true);
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
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Executions
            </Typography>
            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
              {executions.slice(0, 10).map((execution) => (
                <Box key={execution.execution_id} sx={{ mb: 2, p: 1, border: 1, borderColor: 'divider', borderRadius: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" noWrap>
                      {execution.workflow_id}
                    </Typography>
                    <Chip
                      label={execution.status}
                      color={getExecutionStatusColor(execution.status) as any}
                      size="small"
                    />
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(execution.started_at).toLocaleString()}
                  </Typography>
                  {execution.error_message && (
                    <Typography variant="caption" color="error" display="block">
                      Error: {execution.error_message}
                    </Typography>
                  )}
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Execution Analytics */}
      <Paper sx={{ p: 2, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Execution Analytics (Last 24 Hours)
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={generateExecutionChartData()}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis />
            <RechartsTooltip />
            <Line type="monotone" dataKey="executions" stroke="#8884d8" strokeWidth={2} />
            <Line type="monotone" dataKey="completed" stroke="#82ca9d" strokeWidth={2} />
            <Line type="monotone" dataKey="failed" stroke="#ff7300" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </Paper>

      {/* Create Workflow Dialog */}
      <Dialog open={isCreatingWorkflow} onClose={() => setIsCreatingWorkflow(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Workflow</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Workflow Name"
            value={newWorkflow.name}
            onChange={(e) => setNewWorkflow(prev => ({ ...prev, name: e.target.value }))}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            value={newWorkflow.description}
            onChange={(e) => setNewWorkflow(prev => ({ ...prev, description: e.target.value }))}
            margin="normal"
            multiline
            rows={3}
          />
          
          <Divider sx={{ my: 2 }} />
          
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Tasks</Typography>
          <Button
              variant="outlined"
              startIcon={<Add />}
              onClick={() => setIsTaskDialogOpen(true)}
            >
              Add Task
          </Button>
          </Box>
          
          {newWorkflow.tasks.map((task, index) => (
            <Card key={task.task_id} sx={{ mb: 2 }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  {taskTypeIcons[task.task_type]}
                  <Typography variant="subtitle1">{task.name}</Typography>
                  <Chip
                    label={task.task_type}
                    size="small"
                    sx={{ backgroundColor: taskTypeColors[task.task_type], color: 'white' }}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  ID: {task.task_id}
                </Typography>
                {task.dependencies.length > 0 && (
                  <Typography variant="caption" color="text.secondary">
                    Dependencies: {task.dependencies.join(', ')}
                  </Typography>
                )}
              </CardContent>
              <CardActions>
                <IconButton size="small" onClick={() => handleRemoveTask(task.task_id)}>
                  <Delete />
                </IconButton>
              </CardActions>
            </Card>
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsCreatingWorkflow(false)}>Cancel</Button>
          <Button
            onClick={handleCreateWorkflow}
            variant="contained"
            disabled={!newWorkflow.name || loading}
          >
            Create Workflow
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Task Dialog */}
      <Dialog open={isTaskDialogOpen} onClose={() => setIsTaskDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Task</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Task Name"
            value={newTask.name}
            onChange={(e) => setNewTask(prev => ({ ...prev, name: e.target.value }))}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Task Type</InputLabel>
            <Select
              value={newTask.task_type}
              onChange={(e) => setNewTask(prev => ({ ...prev, task_type: e.target.value }))}
            >
              <MenuItem value="action">Action</MenuItem>
              <MenuItem value="condition">Condition</MenuItem>
              <MenuItem value="loop">Loop</MenuItem>
              <MenuItem value="parallel">Parallel</MenuItem>
              <MenuItem value="sequence">Sequence</MenuItem>
              <MenuItem value="timer">Timer</MenuItem>
              <MenuItem value="webhook">Webhook</MenuItem>
              <MenuItem value="api_call">API Call</MenuItem>
              <MenuItem value="data_transform">Data Transform</MenuItem>
              <MenuItem value="notification">Notification</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Timeout (seconds)"
            type="number"
            value={newTask.timeout_seconds}
            onChange={(e) => setNewTask(prev => ({ ...prev, timeout_seconds: parseInt(e.target.value) }))}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Retry Count"
              type="number"
            value={newTask.retry_count}
            onChange={(e) => setNewTask(prev => ({ ...prev, retry_count: parseInt(e.target.value) }))}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsTaskDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleAddTask}
            variant="contained"
            disabled={!newTask.name}
          >
            Add Task
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

export default WorkflowDesigner;