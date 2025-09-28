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
} from '@mui/material';
import {
  Psychology,
  Visibility,
  Mic,
  Upload,
  Download,
  Refresh,
  CheckCircle,
  Error,
  Schedule,
  TrendingUp,
  Assessment,
} from '@mui/icons-material';
import { cognitiveService } from '../../services/cognitiveService';

interface CognitiveRequest {
  requestId: string;
  serviceType: 'nlp' | 'vision' | 'speech';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: any;
  confidence?: number;
  processingTime?: number;
  createdAt: string;
}

interface ServiceStatus {
  nlp: 'active' | 'inactive';
  vision: 'active' | 'inactive';
  speech: 'active' | 'inactive';
}

const CognitiveDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [requests, setRequests] = useState<CognitiveRequest[]>([]);
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus>({
    nlp: 'inactive',
    vision: 'inactive',
    speech: 'inactive',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // NLP State
  const [nlpText, setNlpText] = useState('');
  const [nlpOperation, setNlpOperation] = useState('sentiment');
  const [nlpCategories, setNlpCategories] = useState('');

  // Vision State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [visionOperation, setVisionOperation] = useState('detect');

  // Speech State
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [speechOperation, setSpeechOperation] = useState('transcribe');

  // Dialog State
  const [resultDialog, setResultDialog] = useState(false);
  const [selectedResult, setSelectedResult] = useState<any>(null);

  useEffect(() => {
    loadPlatformStatus();
    loadRecentRequests();
  }, []);

  const loadPlatformStatus = async () => {
    try {
      const status = await cognitiveService.getPlatformStatus();
      setServiceStatus(status.services);
    } catch (error) {
      console.error('Failed to load platform status:', error);
    }
  };

  const loadRecentRequests = async () => {
    try {
      setIsLoading(true);
      const recentRequests = await cognitiveService.getRecentRequests();
      setRequests(recentRequests);
    } catch (error) {
      setError('Failed to load recent requests');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNlpSubmit = async () => {
    if (!nlpText.trim()) return;

    try {
      setIsLoading(true);
      setError(null);

      let requestId: string;
      switch (nlpOperation) {
        case 'sentiment':
          requestId = await cognitiveService.analyzeSentiment(nlpText);
          break;
        case 'classify':
          const categories = nlpCategories.split(',').map(c => c.trim());
          requestId = await cognitiveService.classifyText(nlpText, categories);
          break;
        case 'entities':
          requestId = await cognitiveService.extractEntities(nlpText);
          break;
        case 'summarize':
          requestId = await cognitiveService.summarizeText(nlpText);
          break;
        default:
          throw new Error('Unknown NLP operation');
      }

      // Poll for result
      await pollForResult(requestId);
    } catch (error) {
      setError(`NLP processing failed: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVisionSubmit = async () => {
    if (!selectedFile) return;

    try {
      setIsLoading(true);
      setError(null);

      let requestId: string;
      switch (visionOperation) {
        case 'detect':
          requestId = await cognitiveService.detectObjects(selectedFile);
          break;
        case 'classify':
          requestId = await cognitiveService.classifyImage(selectedFile);
          break;
        case 'ocr':
          requestId = await cognitiveService.extractTextFromImage(selectedFile);
          break;
        default:
          throw new Error('Unknown Vision operation');
      }

      await pollForResult(requestId);
    } catch (error) {
      setError(`Vision processing failed: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSpeechSubmit = async () => {
    if (!audioFile) return;

    try {
      setIsLoading(true);
      setError(null);

      let requestId: string;
      switch (speechOperation) {
        case 'transcribe':
          requestId = await cognitiveService.transcribeAudio(audioFile);
          break;
        case 'emotion':
          requestId = await cognitiveService.analyzeAudioEmotion(audioFile);
          break;
        default:
          throw new Error('Unknown Speech operation');
      }

      await pollForResult(requestId);
    } catch (error) {
      setError(`Speech processing failed: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const pollForResult = async (requestId: string) => {
    const maxAttempts = 30;
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const response = await cognitiveService.getResponse(requestId);
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

  const getServiceIcon = (serviceType: string) => {
    switch (serviceType) {
      case 'nlp':
        return <Psychology />;
      case 'vision':
        return <Visibility />;
      case 'speech':
        return <Mic />;
      default:
        return <Assessment />;
    }
  };

  const renderNlpTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Natural Language Processing
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            multiline
            rows={6}
            label="Text Input"
            value={nlpText}
            onChange={(e) => setNlpText(e.target.value)}
            placeholder="Enter text to analyze..."
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Operation</InputLabel>
            <Select
              value={nlpOperation}
              onChange={(e) => setNlpOperation(e.target.value)}
            >
              <MenuItem value="sentiment">Sentiment Analysis</MenuItem>
              <MenuItem value="classify">Text Classification</MenuItem>
              <MenuItem value="entities">Entity Extraction</MenuItem>
              <MenuItem value="summarize">Text Summarization</MenuItem>
            </Select>
          </FormControl>

          {nlpOperation === 'classify' && (
            <TextField
              fullWidth
              label="Categories (comma-separated)"
              value={nlpCategories}
              onChange={(e) => setNlpCategories(e.target.value)}
              placeholder="positive, negative, neutral"
            />
          )}

          <Button
            variant="contained"
            onClick={handleNlpSubmit}
            disabled={!nlpText.trim() || isLoading}
            sx={{ mt: 2 }}
          >
            Process Text
          </Button>
        </Grid>
      </Grid>
    </Box>
  );

  const renderVisionTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Computer Vision
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Upload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Upload an image file
            </Typography>
            <input
              accept="image/*"
              style={{ display: 'none' }}
              id="vision-file-input"
              type="file"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            />
            <label htmlFor="vision-file-input">
              <Button variant="outlined" component="span">
                Choose Image
              </Button>
            </label>
            {selectedFile && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Selected: {selectedFile.name}
              </Typography>
            )}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Operation</InputLabel>
            <Select
              value={visionOperation}
              onChange={(e) => setVisionOperation(e.target.value)}
            >
              <MenuItem value="detect">Object Detection</MenuItem>
              <MenuItem value="classify">Image Classification</MenuItem>
              <MenuItem value="ocr">Text Extraction (OCR)</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="contained"
            onClick={handleVisionSubmit}
            disabled={!selectedFile || isLoading}
            sx={{ mt: 2 }}
          >
            Process Image
          </Button>
        </Grid>
      </Grid>
    </Box>
  );

  const renderSpeechTab = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Speech Processing
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Mic sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Upload an audio file
            </Typography>
            <input
              accept="audio/*"
              style={{ display: 'none' }}
              id="speech-file-input"
              type="file"
              onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
            />
            <label htmlFor="speech-file-input">
              <Button variant="outlined" component="span">
                Choose Audio
              </Button>
            </label>
            {audioFile && (
              <Typography variant="body2" sx={{ mt: 1 }}>
                Selected: {audioFile.name}
              </Typography>
            )}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Operation</InputLabel>
            <Select
              value={speechOperation}
              onChange={(e) => setSpeechOperation(e.target.value)}
            >
              <MenuItem value="transcribe">Speech Recognition</MenuItem>
              <MenuItem value="emotion">Emotion Analysis</MenuItem>
            </Select>
          </FormControl>

          <Button
            variant="contained"
            onClick={handleSpeechSubmit}
            disabled={!audioFile || isLoading}
            sx={{ mt: 2 }}
          >
            Process Audio
          </Button>
        </Grid>
      </Grid>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Cognitive Services Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Psychology sx={{ mr: 1 }} />
                <Typography variant="h6">NLP Service</Typography>
              </Box>
              <Chip
                label={serviceStatus.nlp}
                color={serviceStatus.nlp === 'active' ? 'success' : 'default'}
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Visibility sx={{ mr: 1 }} />
                <Typography variant="h6">Vision Service</Typography>
              </Box>
              <Chip
                label={serviceStatus.vision}
                color={serviceStatus.vision === 'active' ? 'success' : 'default'}
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Mic sx={{ mr: 1 }} />
                <Typography variant="h6">Speech Service</Typography>
              </Box>
              <Chip
                label={serviceStatus.speech}
                color={serviceStatus.speech === 'active' ? 'success' : 'default'}
                size="small"
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {isLoading && <LinearProgress sx={{ mb: 3 }} />}

      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
            <Tab label="NLP" icon={<Psychology />} />
            <Tab label="Vision" icon={<Visibility />} />
            <Tab label="Speech" icon={<Mic />} />
          </Tabs>
        </Box>

        {activeTab === 0 && renderNlpTab()}
        {activeTab === 1 && renderVisionTab()}
        {activeTab === 2 && renderSpeechTab()}
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
                  {getServiceIcon(request.serviceType)}
                </ListItemIcon>
                <ListItemText
                  primary={`${request.serviceType.toUpperCase()} - ${request.requestId}`}
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
        <DialogTitle>Processing Result</DialogTitle>
        <DialogContent>
          {selectedResult && (
            <Box>
              <Typography variant="body1" gutterBottom>
                <strong>Service:</strong> {selectedResult.serviceType}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Confidence:</strong> {selectedResult.confidence}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Processing Time:</strong> {selectedResult.processingTime}s
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

export default CognitiveDashboard;
