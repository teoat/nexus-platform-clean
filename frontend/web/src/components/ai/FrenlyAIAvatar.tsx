import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Box, IconButton, Tooltip, Badge, Chip, Typography } from '@mui/material';
import { SmartToy, Chat, Insights, Settings } from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

interface FrenlyAIAvatarProps {
  context?: Record<string, any>;
  onInsightClick?: (_insight: any) => void;
  onOverlayToggle?: (_show: boolean) => void;
  className?: string;
}

interface AIInsight {
  id: string;
  title: string;
  description: string;
  type: 'warning' | 'info' | 'success' | 'error';
  priority: 'low' | 'medium' | 'high';
  timestamp: string;
  source: string;
}

const FrenlyAIAvatar: React.FC<FrenlyAIAvatarProps> = ({
  context = {},
  onInsightClick = () => {},
  onOverlayToggle = () => {},
  className = ""
}) => {
  const theme = useTheme();
  const [mood, setMood] = useState<'idle' | 'thinking' | 'speaking' | 'listening'>('idle');
  const [isVisible] = useState(true);

  const [speechBubble, setSpeechBubble] = useState('');
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);

  
   const wsRef = useRef<WebSocket | null>(null);
   const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
   const animationTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

   const connectWebSocket = useCallback(() => {
    try {
      const wsUrl = process.env.REACT_APP_AI_WS_URL || 'ws://localhost:8001/ws';
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('Frenly AI WebSocket connected');
        setIsConnected(true);
        setMood('idle');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      wsRef.current.onclose = () => {
        console.log('Frenly AI WebSocket disconnected');
        setIsConnected(false);
        setMood('idle');
        // Attempt to reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 5000);
      };

      wsRef.current.onerror = (error) => {
        console.error('Frenly AI WebSocket error:', error);
        setIsConnected(false);
      };
     } catch (error) {
       console.error('Error connecting to Frenly AI WebSocket:', error);
       setIsConnected(false);
     }
   }, []);

      

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'insight':
        setInsights(prev => [data.insight, ...prev.slice(0, 4)]);
        setSpeechBubble(data.insight.title);
        setMood('speaking');
        setTimeout(() => setMood('idle'), 3000);
        break;
      case 'response':
        setSpeechBubble(data.message);
        setMood('speaking');
        setTimeout(() => setMood('idle'), 3000);
        break;
      case 'thinking':
        setMood('thinking');
        break;
      case 'listening':
        setMood('listening');
        break;
      case 'status':
        setIsConnected(data.connected);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const sendMessage = (message: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'message',
        message,
        context,
        timestamp: new Date().toISOString()
      }));
    }
  };

  const toggleOverlay = () => {
    const newShowOverlay = !showOverlay;
    setShowOverlay(newShowOverlay);
    onOverlayToggle(newShowOverlay);
  };

  const handleInsightClick = (insight: AIInsight) => {
    onInsightClick(insight);
    setSpeechBubble(insight.description);
    setMood('speaking');
    setTimeout(() => setMood('idle'), 3000);
  };

  const getMoodColor = () => {
    switch (mood) {
      case 'thinking':
        return theme.palette.warning.main;
      case 'speaking':
        return theme.palette.success.main;
      case 'listening':
        return theme.palette.info.main;
      default:
        return theme.palette.primary.main;
    }
  };

  const getMoodAnimation = () => {
    switch (mood) {
      case 'thinking':
        return 'pulse 1s infinite';
      case 'speaking':
        return 'bounce 0.5s infinite';
      case 'listening':
        return 'glow 2s infinite';
      default:
        return 'none';
    }
  };

  if (!isVisible) return null;

  return (
    <Box
      className={`frenly-ai-avatar ${className}`}
      sx={{
        position: 'fixed',
        bottom: 20,
        right: 20,
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'flex-end',
        gap: 1
      }}
    >
      {/* Speech Bubble */}
      {speechBubble && (
        <Box
          sx={{
            backgroundColor: theme.palette.background.paper,
            color: theme.palette.text.primary,
            padding: 2,
            borderRadius: 2,
            maxWidth: 300,
            boxShadow: theme.shadows[4],
            border: `1px solid ${theme.palette.divider}`,
            position: 'relative',
            mb: 1,
            '&::after': {
              content: '""',
              position: 'absolute',
              bottom: -8,
              right: 20,
              width: 0,
              height: 0,
              borderLeft: '8px solid transparent',
              borderRight: '8px solid transparent',
              borderTop: `8px solid ${theme.palette.background.paper}`,
            }
          }}
        >
          {speechBubble}
        </Box>
      )}

      {/* Insights */}
      {insights.length > 0 && (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            gap: 1,
            mb: 1,
            maxWidth: 300
          }}
        >
          {insights.slice(0, 3).map((insight) => (
            <Chip
              key={insight.id}
              label={insight.title}
              color={insight.type === 'error' ? 'error' : insight.type === 'warning' ? 'warning' : 'primary'}
              size="small"
              onClick={() => handleInsightClick(insight)}
              sx={{ cursor: 'pointer' }}
            />
          ))}
        </Box>
      )}

      {/* Avatar */}
      <Box
        sx={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}
      >
        {/* Status Indicator */}
        <Box
          sx={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            backgroundColor: isConnected ? theme.palette.success.main : theme.palette.error.main,
            animation: isConnected ? 'pulse 2s infinite' : 'none'
          }}
        />

        {/* Main Avatar Button */}
        <Tooltip title={isConnected ? "Frenly AI - Connected" : "Frenly AI - Disconnected"}>
          <IconButton
            onClick={toggleOverlay}
            sx={{
              width: 56,
              height: 56,
              backgroundColor: getMoodColor(),
              color: 'white',
              animation: getMoodAnimation(),
              '&:hover': {
                backgroundColor: getMoodColor(),
                transform: 'scale(1.1)',
              },
              transition: 'all 0.3s ease',
            }}
          >
            <SmartToy sx={{ fontSize: 28 }} />
          </IconButton>
        </Tooltip>

        {/* Action Buttons */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            gap: 0.5
          }}
        >
          <Tooltip title="Chat">
            <IconButton
              size="small"
              onClick={() => sendMessage('Hello!')}
              sx={{
                backgroundColor: theme.palette.background.paper,
                color: theme.palette.text.primary,
                '&:hover': {
                  backgroundColor: theme.palette.action.hover,
                }
              }}
            >
              <Chat fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Insights">
            <Badge badgeContent={insights.length} color="error">
              <IconButton
                size="small"
                onClick={() => setShowOverlay(!showOverlay)}
                sx={{
                  backgroundColor: theme.palette.background.paper,
                  color: theme.palette.text.primary,
                  '&:hover': {
                    backgroundColor: theme.palette.action.hover,
                  }
                }}
              >
                <Insights fontSize="small" />
              </IconButton>
            </Badge>
          </Tooltip>

          <Tooltip title="Settings">
            <IconButton
              size="small"
              onClick={() => {/* TODO: Open settings */}}
              sx={{
                backgroundColor: theme.palette.background.paper,
                color: theme.palette.text.primary,
                '&:hover': {
                  backgroundColor: theme.palette.action.hover,
                }
              }}
            >
              <Settings fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Overlay */}
      {showOverlay && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: 1001,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          onClick={() => setShowOverlay(false)}
        >
          <Box
            sx={{
              backgroundColor: theme.palette.background.paper,
              borderRadius: 2,
              padding: 3,
              maxWidth: 600,
              maxHeight: '80vh',
              overflow: 'auto',
              boxShadow: theme.shadows[8],
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <Typography variant="h6" gutterBottom>
              Frenly AI Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              AI-powered insights and assistance for your financial management.
            </Typography>
            
            {/* Insights List */}
            {insights.length > 0 ? (
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  Recent Insights
                </Typography>
                {insights.map((insight) => (
                  <Box
                    key={insight.id}
                    sx={{
                      padding: 2,
                      margin: 1,
                      border: `1px solid ${theme.palette.divider}`,
                      borderRadius: 1,
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: theme.palette.action.hover,
                      }
                    }}
                    onClick={() => handleInsightClick(insight)}
                  >
                    <Typography variant="subtitle2" color={insight.type}>
                      {insight.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {insight.description}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(insight.timestamp).toLocaleString()}
                    </Typography>
                  </Box>
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No insights available. Frenly AI will provide insights as you use the platform.
              </Typography>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default FrenlyAIAvatar;
