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
} from '@mui/material';
import {
  Psychology,
  Visibility,
  Mic,
  Analytics,
  AccountTree,
  Security,
  Refresh,
  CheckCircle,
  Error,
  Schedule,
  TrendingUp,
  Assessment,
  ExpandMore,
  PlayArrow,
  Stop,
  Settings,
} from '@mui/icons-material';
import { aiOrchestrationService } from '../../services/aiOrchestrationService';

interface AIRequest {
  requestId: string;
  modelType: 'nlp' | 'vision' | 'speech' | 'analytics' | 'workflow' | 'security';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: any;
  confidence?: number;
  processingTime?: number;
  modelVersion?: string;
  createdAt: string;
}

interface OrchestrationPlan {
  planId: string;
  strategy: 'sequential' | 'parallel' | 'conditional' | 'ensemble';
  tasks: AIRequest[];
  estimatedTime: number;
  progress: number;
}

interface OrchestratorStatus {
  orchestrator_running: boolean;
  active_requests: number;
  completed_responses: number;
  orchestration_plans: number;
  performance_metrics: {
    total_requests: number;
    successful_requests: number;
    failed_requests: number;
    average_processing_time: number;
  };
  available_models: Record<string, string[]>;
}

const AIOrchestrationDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [requests, setRequests] = useState<AIRequest[]>([]);
  const [plans, setPlans] = useState<OrchestrationPlan[]>([]);
  const [orchestratorStatus, setOrchestratorStatus] = useState<OrchestratorStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Request submission state
  const [selectedModelType, setSelectedModelType] = useState('nlp');
  const [inputData, setInputData] = useState('');
  const [operation, setOperation] = useState('sentiment');
  const [priority, setPriority] = useState(2);

  // Orchestration state
  const [orchestrationTasks, setOrchestrationTasks] = useState<Array<{
    modelType: string;
    inputData: string;
    operation: string;
    priority: number;
  }>>([]);
  const [orchestrationStrategy, setOrchestrationStrategy] = useState('sequential');

  // Dialog state
  const [resultDialog, setResultDialog] = useState(false);
  const [selectedResult, setSelectedResult] = useState<any>(null);

  useEffect(() => {
    loadOrchestratorStatus();
    loadRecentRequests();
    loadOrchestrationPlans();
  }, []);

  const loadOrchestratorStatus = async () => {
    try {
      const status = await aiOrchestrationService.getOrchestratorStatus();
      setOrchestratorStatus(status);
    } catch (error) {
      console.error('Failed to load orchestrator status:', error);
    }
  };

  const loadRecentRequests = async () => {
    try {
      setIsLoading(true);
      const recentRequests = await aiOrchestrationService.getRecentRequests();
      setRequests(recentRequests);
    } catch (error) {
      setError('Failed to load recent requests');
    } finally {
      setIsLoading(false);
    }
  };

  const loadOrchestrationPlans = async () => {
    try {
      const plans = await aiOrchestrationService.getOrchestrationPlans();
      setPlans(plans);
    } catch (error) {
      console.error('Failed to load orchestration plans:', error);
    }
  };

  const handleSubmitRequest = async () => {
    if (!inputData.trim()) return;

    try {
      setIsLoading(true);
      setError(null);

      const requestId = await aiOrchestrationService.submitRequest(
        selectedModelType,
        inputData,
        { operation },
        priority
      );

      // Poll for result
      await pollForResult(requestId);
    } catch (error) {
      setError(`Request submission failed: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateOrchestrationPlan = async () => {
    if (orchestrationTasks.length === 0) return;

    try {
      setIsLoading(true);
      setError(null);

      const planId = await aiOrchestrationService.createOrchestrationPlan(
        orchestrationTasks,
        orchestrationStrategy
      );

      // Poll for plan completion
      await pollForPlanCompletion(planId);
    } catch (error) {
      setError(`Orchestration plan creation failed: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const pollForResult = async (requestId: string) => {
    const maxAttempts = 30;
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const response = await aiOrchestrationService.getResponse(requestId);
        if (response && response.status === 'completed') {
          setSelectedResult(response);
          setResultDialog(true);
          loadRecentRequests();
          return;
        } else if (response && response.status === 'failed') {
          setError('Processing failed');
          return;
        }
      } catch (error) {
        console.error('Error polling for result:', error);
      }

      attempts++;
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    setError('Request timeout - processing took too long');
  };

  const pollForPlanCompletion = async (planId: string) => {
    const maxAttempts = 60;
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const status = await aiOrchestrationService.getPlanStatus(planId);
        if (status.progress === 1.0) {
          loadOrchestrationPlans();
          return;
        }
      } catch (error) {
        console.error('Error polling for plan completion:', error);
      }

      attempts++;
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    setError('Plan completion timeout');
  };

  const addOrchestrationTask = () => {
    setOrchestrationTasks([...orchestrationTasks, {
      modelType: 'nlp',
      inputData: '',
      operation: 'sentiment',
      priority: 2
    }]);
  };

  const removeOrchestrationTask = (index: number) => {
    setOrchestrationTasks(orchestrationTasks.filter((_, i) => i !== index));
  };

  const updateOrchestrationTask = (index: number, field: string, value: any) => {
    const updated = [...orchestrationTasks];
    updated[index] = { ...updated[index], [field]: value };
    setOrchestrationTasks(updated);
  };

  const getModelIcon = (modelType: string) => {
    switch (modelType) {
      case 'nlp':
        return <Psychology />;
      case 'vision':
        return <Visibility />;
      case 'speech':
        return <Mic />;
      case 'analytics':
        return <Analytics />;
      case 'workflow':
        return <AccountTree />;
      case 'security':
        return <Security />;
      default:
        return <Assessment />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'failed':
        return <Error color="error" />;
      case 'processing':
        return <Schedule color="warning" />;
      default:
        return <Schedule color="disabled" />;
    }
  };

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 4:
        return 'error';
      case 3:
        return 'warning';
      case 2:
        return 'info';
      default:
        return 'default';
    }
  };

  const renderSingleRequestTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Single AI Request
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Model Type</InputLabel>
            <Select
              value={selectedModelType}
              onChange={(e) => setSelectedModelType(e.target.value)}
            >
              <MenuItem value="nlp">Natural Language Processing</MenuItem>
              <MenuItem value="vision">Computer Vision</MenuItem>
              <MenuItem value="speech">Speech Processing</MenuItem>
              <MenuItem value="analytics">Analytics</MenuItem>
              <MenuItem value="workflow">Workflow</MenuItem>
              <MenuItem value="security">Security</MenuItem>
            </Select>
          </FormControl>

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Operation</InputLabel>
            <Select
              value={operation}
              onChange={(e) => setOperation(e.target.value)}
            >
              {selectedModelType === 'nlp' && (
                <>
                  <MenuItem value="sentiment">Sentiment Analysis</MenuItem>
                  <MenuItem value="classification">Text Classification</MenuItem>
                  <MenuItem value="ner">Named Entity Recognition</MenuItem>
                  <MenuItem value="summarize">Text Summarization</MenuItem>
                </>
              )}
              {selectedModelType === 'vision' && (
                <>
                  <MenuItem value="detect">Object Detection</MenuItem>
                  <MenuItem value="classify">Image Classification</MenuItem>
                  <MenuItem value="ocr">OCR</MenuItem>
                </>
              )}
              {selectedModelType === 'speech' && (
                <>
                  <MenuItem value="transcribe">Speech Recognition</MenuItem>
                  <MenuItem value="emotion">Emotion Analysis</MenuItem>
                </>
              )}
            </Select>
          </FormControl>

          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Priority</InputLabel>
            <Select
              value={priority}
              onChange={(e) => setPriority(Number(e.target.value))}
            >
              <MenuItem value={1}>Low</MenuItem>
              <MenuItem value={2}>Medium</MenuItem>
              <MenuItem value={3}>High</MenuItem>
              <MenuItem value={4}>Critical</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            multiline
            rows={6}
            label="Input Data"
            value={inputData}
            onChange={(e) => setInputData(e.target.value)}
            placeholder="Enter input data..."
          />

          <Button
            variant="contained"
            onClick={handleSubmitRequest}
            disabled={!inputData.trim() || isLoading}
            sx={{ mt: 2 }}
          >
            Submit Request
          </Button>
        </Grid>
      </Grid>
    </Box>
  );

  const renderOrchestrationTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        AI Orchestration
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Strategy</InputLabel>
            <Select
              value={orchestrationStrategy}
              onChange={(e) => setOrchestrationStrategy(e.target.value)}
            >
              <MenuItem value="sequential">Sequential</MenuItem>
              <MenuItem value="parallel">Parallel</MenuItem>
              <MenuItem value="conditional">Conditional</MenuItem>
              <MenuItem value="ensemble">Ensemble</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="outlined"
            onClick={addOrchestrationTask}
            sx={{ mb: 2 }}
          >
            Add Task
          </Button>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Typography variant="subtitle1" gutterBottom>
            Orchestration Tasks ({orchestrationTasks.length})
          </Typography>
          
          {orchestrationTasks.map((task, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={3}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Model</InputLabel>
                      <Select
                        value={task.modelType}
                        onChange={(e) => updateOrchestrationTask(index, 'modelType', e.target.value)}
                      >
                        <MenuItem value="nlp">NLP</MenuItem>
                        <MenuItem value="vision">Vision</MenuItem>
                        <MenuItem value="speech">Speech</MenuItem>
                        <MenuItem value="analytics">Analytics</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} md={3}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Operation</InputLabel>
                      <Select
                        value={task.operation}
                        onChange={(e) => updateOrchestrationTask(index, 'operation', e.target.value)}
                      >
                        <MenuItem value="sentiment">Sentiment</MenuItem>
                        <MenuItem value="classification">Classification</MenuItem>
                        <MenuItem value="detect">Detect</MenuItem>
                        <MenuItem value="transcribe">Transcribe</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      size="small"
                      label="Input Data"
                      value={task.inputData}
                      onChange={(e) => updateOrchestrationTask(index, 'inputData', e.target.value)}
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={2}>
                    <IconButton
                      onClick={() => removeOrchestrationTask(index)}
                      color="error"
                    >
                      <Error />
                    </IconButton>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          ))}

          <Button
            variant="contained"
            onClick={handleCreateOrchestrationPlan}
            disabled={orchestrationTasks.length === 0 || isLoading}
            sx={{ mt: 2 }}
          >
            Create Orchestration Plan
          </Button>
        </Grid>
      </Grid>
    </Box>
  );

  const renderMetricsTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Performance Metrics
      </Typography>
      
      {orchestratorStatus && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="primary">
                  {orchestratorStatus.performance_metrics.total_requests}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Requests
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="success.main">
                  {(
                    orchestratorStatus.performance_metrics.successful_requests / 
                    Math.max(orchestratorStatus.performance_metrics.total_requests, 1) * 100
                  ).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Success Rate
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="info.main">
                  {orchestratorStatus.performance_metrics.average_processing_time.toFixed(2)}s
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Processing Time
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="warning.main">
                  {orchestratorStatus.active_requests}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Requests
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Available Models
          </Typography>
          
          {orchestratorStatus && (
            <Grid container spacing={2}>
              {Object.entries(orchestratorStatus.available_models).map(([modelType, operations]) => (
                <Grid item xs={12} md={4} key={modelType}>
                  <Paper sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      {getModelIcon(modelType)}
                      <Typography variant="subtitle1" sx={{ ml: 1 }}>
                        {modelType.toUpperCase()}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {operations.length} operations available
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          )}
        </CardContent>
      </Card>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        AI Orchestration Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Orchestrator Status
              </Typography>
              <Chip
                label={orchestratorStatus?.orchestrator_running ? 'Running' : 'Stopped'}
                color={orchestratorStatus?.orchestrator_running ? 'success' : 'default'}
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Active Requests
              </Typography>
              <Typography variant="h4" color="primary">
                {orchestratorStatus?.active_requests || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Completed Responses
              </Typography>
              <Typography variant="h4" color="success.main">
                {orchestratorStatus?.completed_responses || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Orchestration Plans
              </Typography>
              <Typography variant="h4" color="info.main">
                {orchestratorStatus?.orchestration_plans || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {isLoading && <LinearProgress sx={{ mb: 3 }} />}

      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="Single Request" icon={<Assessment />} />
            <Tab label="Orchestration" icon={<AccountTree />} />
            <Tab label="Metrics" icon={<TrendingUp />} />
          </Tabs>
        </Box>

        {activeTab === 0 && renderSingleRequestTab()}
        {activeTab === 1 && renderOrchestrationTab()}
        {activeTab === 2 && renderMetricsTab()}
      </Card>

      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Recent Requests</Typography>
            <IconButton onClick={loadRecentRequests}>
              <Refresh />
            </IconButton>
          </Box>

          <List>
            {requests.map((request) => (
              <ListItem key={request.requestId}>
                <ListItemIcon>
                  {getModelIcon(request.modelType)}
                </ListItemIcon>
                <ListItemText
                  primary={`${request.modelType.toUpperCase()} - ${request.requestId}`}
                  secondary={`Status: ${request.status} | Confidence: ${request.confidence || 'N/A'} | Time: ${request.processingTime || 'N/A'}s`}
                />
                <ListItemIcon>
                  {getStatusIcon(request.status)}
                </ListItemIcon>
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>

      <Dialog open={resultDialog} onClose={() => setResultDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>AI Processing Result</DialogTitle>
        <DialogContent>
          {selectedResult && (
            <Box>
              <Typography variant="body1" gutterBottom>
                <strong>Model Type:</strong> {selectedResult.modelType}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Confidence:</strong> {selectedResult.confidence}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Processing Time:</strong> {selectedResult.processingTime}s
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Model Version:</strong> {selectedResult.modelVersion}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Result:</strong>
              </Typography>
              <Paper sx={{ p: 2, mt: 1 }}>
                <pre>{JSON.stringify(selectedResult.result, null, 2)}</pre>
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResultDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AIOrchestrationDashboard;
