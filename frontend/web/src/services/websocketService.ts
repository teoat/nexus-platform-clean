/**
 * NEXUS Platform - WebSocket Service
 * Real-time communication service with reconnection and error handling
 */

import React, { useState, useEffect, useCallback } from 'react';
import { handleError, ErrorType, ErrorSeverity } from '@utils/errorHandler';

export interface WebSocketMessage {
  type: string;
  data: Record<string, unknown>;
  timestamp: number;
  id?: string;
}

export interface WebSocketConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  timeout?: number;
}

export type WebSocketEventHandler = (message: WebSocketMessage) => void;
export type WebSocketStatusHandler = (
  status: 'connecting' | 'connected' | 'disconnected' | 'error'
) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private reconnectAttempts = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private heartbeatTimer: ReturnType<typeof setTimeout> | null = null;
  private messageHandlers = new Map<string, Set<WebSocketEventHandler>>();
  private statusHandlers = new Set<WebSocketStatusHandler>();
  private isConnecting = false;
  private lastHeartbeat = 0;

  constructor(config: WebSocketConfig) {
    this.config = {
      reconnectInterval: 5000,
      maxReconnectAttempts: 5,
      heartbeatInterval: 30000,
      timeout: 10000,
      ...config,
    };
  }

  public connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      if (this.isConnecting) {
        reject(new Error('Connection already in progress'));
        return;
      }

      this.isConnecting = true;
      this.notifyStatus('connecting');

      try {
        this.ws = new WebSocket(this.config.url);
        this.setupEventHandlers(resolve, reject);
        this.startHeartbeat();
      } catch (error) {
        this.isConnecting = false;
        this.notifyStatus('error');
        reject(error);
      }
    });
  }

  public disconnect(): void {
    this.stopHeartbeat();
    this.clearReconnectTimer();

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.notifyStatus('disconnected');
  }

  public send(message: WebSocketMessage): boolean {
    if (!this.isConnected()) {
      console.warn('WebSocket not connected. Message not sent:', message);
      return false;
    }

    try {
      this.ws!.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('WebSocket send error:', error);
      return false;
    }
  }

  public subscribe(
    eventType: string,
    handler: WebSocketEventHandler
  ): () => void {
    if (!this.messageHandlers.has(eventType)) {
      this.messageHandlers.set(eventType, new Set());
    }

    this.messageHandlers.get(eventType)!.add(handler);

    return () => {
      const handlers = this.messageHandlers.get(eventType);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.messageHandlers.delete(eventType);
        }
      }
    };
  }

  public onStatusChange(handler: WebSocketStatusHandler): () => void {
    this.statusHandlers.add(handler);

    return () => {
      this.statusHandlers.delete(handler);
    };
  }

  public isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  public getConnectionState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }

  public getReconnectAttempts(): number {
    return this.reconnectAttempts;
  }

  private setupEventHandlers(
    resolve: () => void,
    reject: (error: Error) => void
  ): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.lastHeartbeat = Date.now();
      this.notifyStatus('connected');
      resolve();
    };

    this.ws.onmessage = event => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    };

    this.ws.onclose = event => {
      this.isConnecting = false;
      this.stopHeartbeat();

      if (event.code !== 1000) {
        this.notifyStatus('error');
        this.attemptReconnect();
      } else {
        this.notifyStatus('disconnected');
      }
    };

    this.ws.onerror = error => {
      this.isConnecting = false;
      this.notifyStatus('error');
      console.error('WebSocket connection error:', error);
      reject(new Error('WebSocket connection failed'));
    };
  }

  private handleMessage(message: WebSocketMessage): void {
    const handlers = this.messageHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error('WebSocket message handler error:', error);
        }
      });
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts!) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    this.reconnectTimer = setTimeout(() => {
      this.connect().catch(error => {
        console.error('WebSocket reconnect error:', error);
      });
    }, this.config.reconnectInterval);
  }

  private startHeartbeat(): void {
    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) {
        this.send({
          type: 'heartbeat',
          data: { timestamp: Date.now() },
          timestamp: Date.now(),
        });
        this.lastHeartbeat = Date.now();
      }
    }, this.config.heartbeatInterval);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private notifyStatus(
    status: 'connecting' | 'connected' | 'disconnected' | 'error'
  ): void {
    this.statusHandlers.forEach(handler => {
      try {
        handler(status);
      } catch (error) {
        console.error('WebSocket status notification error:', error);
      }
    });
  }

  public destroy(): void {
    this.disconnect();
    this.messageHandlers.clear();
    this.statusHandlers.clear();
  }
}

// Default instance
const defaultConfig: WebSocketConfig = {
  url: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
};

export const websocketService = new WebSocketService(defaultConfig);

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState(WebSocket.CLOSED);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  useEffect(() => {
    const statusUnsubscribe = websocketService.onStatusChange(status => {
      setIsConnected(status === 'connected');
      setConnectionState(websocketService.getConnectionState());
      setReconnectAttempts(websocketService.getReconnectAttempts());
    });

    return () => {
      statusUnsubscribe();
    };
  }, []);

  const connect = useCallback(async () => {
    try {
      await websocketService.connect();
    } catch (error) {
      handleError(error, ErrorType.NETWORK);
    }
  }, []);

  const disconnect = useCallback(() => {
    websocketService.disconnect();
  }, []);

  const send = useCallback((message: Omit<WebSocketMessage, 'timestamp'>) => {
    const fullMessage: WebSocketMessage = {
      ...message,
      timestamp: Date.now(),
    };
    return websocketService.send(fullMessage);
  }, []);

  const subscribe = useCallback(
    (eventType: string, handler: WebSocketEventHandler) => {
      return websocketService.subscribe(eventType, handler);
    },
    []
  );

  return {
    isConnected,
    connectionState,
    reconnectAttempts,
    connect,
    disconnect,
    send,
    subscribe,
  };
};

export default websocketService;
