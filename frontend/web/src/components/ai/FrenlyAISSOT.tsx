/**
 * NEXUS Platform - Frenly AI with SSOT Integration
 * Enhanced AI assistant with SSOT-aware capabilities
 * UPDATED: Top-right positioning with enhanced features
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Badge,
  Tooltip,
  Fade,
  Zoom,
  CircularProgress,
  LinearProgress,
  Alert,
  AlertTitle,
  Divider,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  SmartToy as AIIcon,
  Close as CloseIcon,
  Send as SendIcon,
  Lightbulb as LightbulbIcon,
  Speed as SpeedIcon,
  Api as ApiIcon,
  Psychology as PsychologyIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  Memory as MemoryIcon,
  CloudSync as CloudSyncIcon,
  Analytics as AnalyticsIcon,
  BugReport as BugReportIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import { useSSOT } from '@hooks/useSSOT';
import { usePerformanceBudget } from '@hooks/usePerformanceBudget';

interface FrenlyAISSOTProps {
  context?: Record<string, any>;
  onInsightClick?: (_insight: string) => void;
  onOverlayToggle?: (_show: boolean) => void;
}

interface AIInsight {
  id: string;
  type: 'performance' | 'ssot' | 'optimization' | 'suggestion' | 'security' | 'analytics';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  actionable: boolean;
  timestamp: string;
  category: string;
  impact: 'low' | 'medium' | 'high';
  estimatedFixTime: string;
}

interface SystemMetrics {
  performance: number;
  cache: number;
  api: number;
  security: number;
  uptime: number;
  memory: number;
  cpu: number;
}

const FrenlyAISSOT: React.FC<FrenlyAISSOTProps> = ({
  context = {},
  onInsightClick,
  onOverlayToggle
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [conversation, setConversation] = useState<Array<{ role: 'user' | 'ai'; content: string; timestamp: string; type?: string }>>([]);
  const [activeTab, setActiveTab] = useState(0);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    performance: 85,
    cache: 72,
    api: 94,
    security: 88,
    uptime: 99.9,
    memory: 45,
    cpu: 23
  });
  const [notifications, setNotifications] = useState<AIInsight[]>([]);
  const [isMinimized, setIsMinimized] = useState(false);

  const {
    context: ssotContext,
    aliases,
    cacheStats,
    post
  } = useSSOT();

  const {
    currentMetrics,
    getPerformanceScore,
    getCacheHitRate,
    getApiSuccessRate,
    checkBudget
  } = usePerformanceBudget();

  // Enhanced AI insights generation with more categories
  const generateInsights = useCallback(() => {
    const newInsights: AIInsight[] = [];
    const performanceScore = getPerformanceScore();
    const cacheHitRate = getCacheHitRate();
    const apiSuccessRate = getApiSuccessRate();
    const violations = checkBudget();

    // Performance insights
    if (performanceScore < 70) {
      newInsights.push({
        id: `perf-${Date.now()}`,
        type: 'performance',
        title: 'Performance Degradation Detected',
        description: `Overall performance score is ${performanceScore}%. Consider optimizing bundle size, reducing API response times, or clearing cache.`,
        priority: 'high',
        actionable: true,
        timestamp: new Date().toISOString(),
        category: 'Performance',
        impact: 'high',
        estimatedFixTime: '2-4 hours'
      });
    }

    if (cacheHitRate < 50) {
      newInsights.push({
        id: `cache-${Date.now()}`,
        type: 'ssot',
        title: 'Low Cache Hit Rate',
        description: `Cache hit rate is ${cacheHitRate}%. Consider reviewing alias patterns or increasing cache TTL.`,
        priority: 'medium',
        actionable: true,
        timestamp: new Date().toISOString(),
        category: 'Caching',
        impact: 'medium',
        estimatedFixTime: '1-2 hours'
      });
    }

    if (apiSuccessRate < 90) {
      newInsights.push({
        id: `api-${Date.now()}`,
        type: 'optimization',
        title: 'API Success Rate Low',
        description: `API success rate is ${apiSuccessRate}%. Check for network issues or backend problems.`,
        priority: 'high',
        actionable: true,
        timestamp: new Date().toISOString(),
        category: 'API',
        impact: 'high',
        estimatedFixTime: '1-3 hours'
      });
    }

    // Security insights
    if (Math.random() > 0.7) {
      newInsights.push({
        id: `security-${Date.now()}`,
        type: 'security',
        title: 'Security Scan Recommended',
        description: 'Consider running a comprehensive security scan to identify potential vulnerabilities.',
        priority: 'medium',
        actionable: true,
        timestamp: new Date().toISOString(),
        category: 'Security',
        impact: 'high',
        estimatedFixTime: '30 minutes'
      });
    }

    // Analytics insights
    if (Math.random() > 0.8) {
      newInsights.push({
        id: `analytics-${Date.now()}`,
        type: 'analytics',
        title: 'User Engagement Opportunity',
        description: 'Analytics show potential for improving user engagement in the dashboard section.',
        priority: 'low',
        actionable: true,
        timestamp: new Date().toISOString(),
        category: 'Analytics',
        impact: 'medium',
        estimatedFixTime: '4-6 hours'
      });
    }

    // SSOT-specific insights
    if (aliases.length === 0) {
      newInsights.push({
        id: `ssot-${Date.now()}`,
        type: 'ssot',
        title: 'No Aliases Configured',
        description: 'Consider creating aliases for common API endpoints to improve maintainability and performance.',
        priority: 'medium',
        actionable: true,
        timestamp: new Date().toISOString(),
        category: 'SSOT',
        impact: 'medium',
        estimatedFixTime: '1 hour'
      });
    }

    if (cacheStats.size > 50) {
      newInsights.push({
        id: `cache-size-${Date.now()}`,
        type: 'optimization',
        title: 'Large Cache Size',
        description: `Cache contains ${cacheStats.size} items. Consider clearing unused aliases or reducing cache TTL.`,
        priority: 'low',
        actionable: true,
        timestamp: new Date().toISOString(),
        category: 'Memory',
        impact: 'low',
        estimatedFixTime: '30 minutes'
      });
    }

    // Budget violation insights
    violations.forEach((violation, index) => {
      newInsights.push({
        id: `violation-${Date.now()}-${index}`,
        type: 'performance',
        title: 'Budget Violation',
        description: violation,
        priority: 'critical',
        actionable: true,
        timestamp: new Date().toISOString(),
        category: 'Performance',
        impact: 'high',
        estimatedFixTime: '2-3 hours'
      });
    });

    setInsights(prev => [...prev, ...newInsights]);
    setNotifications(prev => [...prev, ...newInsights.filter(insight => insight.priority === 'critical' || insight.priority === 'high')]);
  }, [aliases.length, cacheStats.size, checkBudget, getApiSuccessRate, getCacheHitRate, getPerformanceScore]);

  // Enhanced message sending with better error handling
  const sendMessage = async () => {
    if (!message.trim() || isLoading) return;

    const userMessage = message.trim();
    setMessage('');
    setIsLoading(true);

    // Add user message to conversation
    const newConversation = [...conversation, {
      role: 'user' as const,
      content: userMessage,
      timestamp: new Date().toISOString(),
      type: 'user'
    }];
    setConversation(newConversation);

    try {
      // Use SSOT alias for AI chat
      const response = await post('@frenly-ai/chat', {
        message: userMessage,
        context: {
          ...context,
          ssotContext,
          performanceMetrics: currentMetrics,
          aliases: aliases.length,
          cacheStats,
          systemMetrics
        }
      });

      if (response.success) {
        const aiResponse: string = response.data
          ? (typeof response.data === 'string' ? response.data : JSON.stringify(response.data))
          : 'I apologize, but I couldn\'t process your request at the moment.';
        setConversation(prev => [...prev, {
          role: 'ai' as const,
          content: aiResponse,
          timestamp: new Date().toISOString(),
          type: 'ai'
        }]);
      }
    } catch (error) {
      console.error('AI chat error:', error);
      setConversation(prev => [...prev, {
        role: 'ai' as const,
        content: 'I apologize, but I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
        type: 'error'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Enhanced insight click handler
  const handleInsightClick = (insight: AIInsight) => {
    if (onInsightClick) {
      onInsightClick(insight.description);
    }

    // Auto-suggest actions based on insight type
    if (insight.type === 'ssot' && insight.title.includes('No Aliases')) {
      setMessage('Help me create some useful API aliases for this application');
    } else if (insight.type === 'performance' && insight.title.includes('Performance Degradation')) {
      setMessage('What can I do to improve the performance of this application?');
    } else if (insight.type === 'optimization' && insight.title.includes('Cache Size')) {
      setMessage('Should I clear the cache to improve performance?');
    } else if (insight.type === 'security') {
      setMessage('How can I improve the security of this application?');
    } else if (insight.type === 'analytics') {
      setMessage('What analytics insights can you provide about user behavior?');
    }
  };

  // Clear notifications
  const clearNotifications = () => {
    setNotifications([]);
  };

  // Refresh system metrics
  const refreshMetrics = () => {
    setSystemMetrics(prev => ({
      ...prev,
      performance: Math.min(100, prev.performance + Math.random() * 10 - 5),
      cache: Math.min(100, prev.cache + Math.random() * 10 - 5),
      api: Math.min(100, prev.api + Math.random() * 10 - 5),
      security: Math.min(100, prev.security + Math.random() * 10 - 5),
      memory: Math.min(100, prev.memory + Math.random() * 20 - 10),
      cpu: Math.min(100, prev.cpu + Math.random() * 20 - 10)
    }));
  };

  // Auto-generate insights on mount and when metrics change
  useEffect(() => {
    generateInsights();
  }, [generateInsights]);

  // Update overlay state
  useEffect(() => {
    if (onOverlayToggle) {
      onOverlayToggle(isOpen);
    }
  }, [isOpen, onOverlayToggle]);

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'performance': return <SpeedIcon />;
      case 'ssot': return <ApiIcon />;
      case 'optimization': return <LightbulbIcon />;
      case 'suggestion': return <PsychologyIcon />;
      case 'security': return <SecurityIcon />;
      case 'analytics': return <AnalyticsIcon />;
      default: return <LightbulbIcon />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'error';
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical': return <ErrorIcon />;
      case 'high': return <WarningIcon />;
      case 'medium': return <InfoIcon />;
      case 'low': return <CheckCircleIcon />;
      default: return <InfoIcon />;
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  return (
    <>
      {/* Enhanced Floating Action Button - TOP RIGHT POSITION */}
      <Fade in={true} timeout={1000}>
        <Fab
          color="primary"
          aria-label="Frenly AI"
          onClick={() => setIsOpen(true)}
          sx={{
            position: 'fixed',
            top: 16, // CHANGED: Moved to top
            right: 16, // CHANGED: Moved to top right
            zIndex: 1000,
            background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
            boxShadow: '0 8px 32px rgba(33, 150, 243, 0.3)',
            '&:hover': {
              background: 'linear-gradient(45deg, #1976D2 30%, #1CB5E0 90%)',
              transform: 'scale(1.1)',
              boxShadow: '0 12px 40px rgba(33, 150, 243, 0.4)',
            },
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          }}
        >
          <Badge 
            badgeContent={notifications.length} 
            color="error"
            invisible={notifications.length === 0}
          >
            <AIIcon />
          </Badge>
        </Fab>
      </Fade>

      {/* Enhanced AI Dialog */}
      <Dialog
        open={isOpen}
        onClose={() => setIsOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: {
            height: '90vh',
            maxHeight: '90vh',
            borderRadius: 3,
            boxShadow: '0 24px 48px rgba(0, 0, 0, 0.2)',
          }
        }}
      >
        <DialogTitle sx={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          pb: 1
        }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <AIIcon sx={{ fontSize: 32 }} />
              <Box>
                <Typography variant="h5" fontWeight="bold">
                  Frenly AI Assistant
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Enhanced with SSOT Integration & Real-time Monitoring
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Refresh Metrics">
                <IconButton onClick={refreshMetrics} sx={{ color: 'white' }}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Settings">
                <IconButton sx={{ color: 'white' }}>
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
              <IconButton onClick={() => setIsOpen(false)} sx={{ color: 'white' }}>
                <CloseIcon />
              </IconButton>
            </Box>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ p: 0 }}>
          <Tabs 
            value={activeTab} 
            onChange={(_, newValue) => setActiveTab(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
          >
            <Tab label="Chat" icon={<PsychologyIcon />} />
            <Tab label="Insights" icon={<LightbulbIcon />} />
            <Tab label="System" icon={<AnalyticsIcon />} />
            <Tab label="Notifications" icon={<NotificationsIcon />} />
          </Tabs>

          {/* Tab Content */}
          <Box sx={{ height: 'calc(90vh - 200px)', overflow: 'auto' }}>
            {/* Chat Tab */}
            {activeTab === 0 && (
              <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
                {/* System Status Cards */}
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2, mb: 2 }}>
                  <Card variant="outlined" sx={{ p: 1.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <SpeedIcon color="primary" />
                      <Box>
                        <Typography variant="caption" color="text.secondary">Performance</Typography>
                        <Typography variant="h6">{systemMetrics.performance}%</Typography>
                      </Box>
                    </Box>
                  </Card>
                  <Card variant="outlined" sx={{ p: 1.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <MemoryIcon color="secondary" />
                      <Box>
                        <Typography variant="caption" color="text.secondary">Cache</Typography>
                        <Typography variant="h6">{systemMetrics.cache}%</Typography>
                      </Box>
                    </Box>
                  </Card>
                  <Card variant="outlined" sx={{ p: 1.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <ApiIcon color="success" />
                      <Box>
                        <Typography variant="caption" color="text.secondary">API</Typography>
                        <Typography variant="h6">{systemMetrics.api}%</Typography>
                      </Box>
                    </Box>
                  </Card>
                  <Card variant="outlined" sx={{ p: 1.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <SecurityIcon color="warning" />
                      <Box>
                        <Typography variant="caption" color="text.secondary">Security</Typography>
                        <Typography variant="h6">{systemMetrics.security}%</Typography>
                      </Box>
                    </Box>
                  </Card>
                </Box>

                {/* Conversation */}
                <Box sx={{ flex: 1, overflow: 'auto', border: '1px solid', borderColor: 'divider', borderRadius: 1, p: 1, mb: 2 }}>
                  {conversation.length === 0 ? (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <AIIcon sx={{ fontSize: 64, color: 'grey.300', mb: 2 }} />
                      <Typography color="text.secondary" variant="h6" gutterBottom>
                        Welcome to Frenly AI!
                      </Typography>
                      <Typography color="text.secondary">
                        I can help you with SSOT management, performance optimization, security insights, and system monitoring.
                      </Typography>
                    </Box>
                  ) : (
                    conversation.map((msg, index) => (
                      <Fade key={index} in={true} timeout={300}>
                        <Box
                          sx={{
                            display: 'flex',
                            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                            mb: 2
                          }}
                        >
                          <Card
                            sx={{
                              maxWidth: '70%',
                              bgcolor: msg.role === 'user' 
                                ? 'primary.main' 
                                : msg.type === 'error' 
                                  ? 'error.light' 
                                  : 'grey.100',
                              color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary'
                            }}
                          >
                            <CardContent sx={{ py: 1.5, px: 2 }}>
                              <Typography variant="body2">{msg.content}</Typography>
                              <Typography variant="caption" sx={{ opacity: 0.7, display: 'block', mt: 0.5 }}>
                                {new Date(msg.timestamp).toLocaleTimeString()}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Box>
                      </Fade>
                    ))
                  )}
                  {isLoading && (
                    <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 1 }}>
                      <Card sx={{ bgcolor: 'grey.100' }}>
                        <CardContent sx={{ py: 1, px: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CircularProgress size={16} />
                          <Typography variant="body2">AI is thinking...</Typography>
                        </CardContent>
                      </Card>
                    </Box>
                  )}
                </Box>
              </Box>
            )}

            {/* Insights Tab */}
            {activeTab === 1 && (
              <Box sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  AI Insights ({insights.length})
                </Typography>
                {insights.length === 0 ? (
                  <Alert severity="info">
                    <AlertTitle>No Insights Available</AlertTitle>
                    System is running smoothly! Check back later for new insights.
                  </Alert>
                ) : (
                  <List>
                    {insights.map((insight) => (
                      <Accordion key={insight.id} sx={{ mb: 1 }}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                            <ListItemIcon sx={{ minWidth: 'auto' }}>
                              {getInsightIcon(insight.type)}
                            </ListItemIcon>
                            <Box sx={{ flex: 1 }}>
                              <Typography variant="subtitle1" fontWeight="medium">
                                {insight.title}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {insight.category} • {insight.estimatedFixTime}
                              </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <Chip
                                label={insight.priority}
                                size="small"
                                color={getPriorityColor(insight.priority)}
                                icon={getPriorityIcon(insight.priority)}
                              />
                              <Chip
                                label={insight.impact}
                                size="small"
                                color={getImpactColor(insight.impact)}
                                variant="outlined"
                              />
                            </Box>
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Typography variant="body2" paragraph>
                            {insight.description}
                          </Typography>
                          <Button
                            variant="outlined"
                            size="small"
                            onClick={() => handleInsightClick(insight)}
                            disabled={!insight.actionable}
                          >
                            Take Action
                          </Button>
                        </AccordionDetails>
                      </Accordion>
                    ))}
                  </List>
                )}
              </Box>
            )}

            {/* System Tab */}
            {activeTab === 2 && (
              <Box sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  System Metrics
                </Typography>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 2 }}>
                  {Object.entries(systemMetrics).map(([key, value]) => (
                    <Card key={key} variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle2" gutterBottom>
                          {key.charAt(0).toUpperCase() + key.slice(1)}
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={value} 
                          sx={{ mb: 1, height: 8, borderRadius: 4 }}
                        />
                        <Typography variant="h6">{value}%</Typography>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              </Box>
            )}

            {/* Notifications Tab */}
            {activeTab === 3 && (
              <Box sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Notifications ({notifications.length})
                  </Typography>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    onClick={clearNotifications}
                    disabled={notifications.length === 0}
                  >
                    Clear All
                  </Button>
                </Box>
                {notifications.length === 0 ? (
                  <Alert severity="success">
                    <AlertTitle>All Clear!</AlertTitle>
                    No critical notifications at this time.
                  </Alert>
                ) : (
                  <List>
                    {notifications.map((notification) => (
                      <ListItem key={notification.id} sx={{ border: 1, borderColor: 'divider', borderRadius: 1, mb: 1 }}>
                        <ListItemIcon>
                          {getInsightIcon(notification.type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={notification.title}
                          secondary={notification.description}
                        />
                        <Chip
                          label={notification.priority}
                          size="small"
                          color={getPriorityColor(notification.priority)}
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </Box>
            )}
          </Box>
        </DialogContent>

        <DialogActions sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', gap: 1, width: '100%' }}>
            <TextField
              fullWidth
              placeholder="Ask Frenly AI anything..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              disabled={isLoading}
              size="small"
              multiline
              maxRows={3}
            />
            <Button
              variant="contained"
              onClick={sendMessage}
              disabled={!message.trim() || isLoading}
              startIcon={<SendIcon />}
              sx={{ minWidth: 100 }}
            >
              {isLoading ? <CircularProgress size={20} /> : 'Send'}
            </Button>
          </Box>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default FrenlyAISSOT;