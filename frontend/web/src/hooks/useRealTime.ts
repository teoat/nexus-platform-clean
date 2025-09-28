/**
 * NEXUS Platform - useRealTime Hook
 * Custom hook for real-time data synchronization and WebSocket management
 */

import { useEffect, useCallback, useRef, useState } from "react";
import { unifiedApiService } from "../services/unifiedApiService";
import { dashboardService } from "../services/dashboardService";
import { aiService } from "../services/aiService";

export interface RealTimeConfig {
  enabled: boolean;
  reconnectInterval: number;
  maxReconnectAttempts: number;
  heartbeatInterval: number;
}

export interface RealTimeData {
  type: "metrics" | "alerts" | "ai" | "users" | "system";
  data: any;
  timestamp: string;
}

export interface ConnectionStatus {
  connected: boolean;
  reconnecting: boolean;
  lastConnected: string | null;
  reconnectAttempts: number;
  error: string | null;
}

const defaultConfig: RealTimeConfig = {
  enabled: true,
  reconnectInterval: 5000,
  maxReconnectAttempts: 5,
  heartbeatInterval: 30000,
};

export const useRealTime = (config: Partial<RealTimeConfig> = {}) => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    connected: false,
    reconnecting: false,
    lastConnected: null,
    reconnectAttempts: 0,
    error: null,
  });

  const [data, setData] = useState<RealTimeData[]>([]);
  const [subscribers, setSubscribers] = useState<
    Map<string, (data: any) => void>
  >(new Map());

  const configRef = useRef({ ...defaultConfig, ...config });
  const reconnectTimeoutRef = useRef<number | null>(null);
  const heartbeatTimeoutRef = useRef<number | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Update config when it changes
  useEffect(() => {
    configRef.current = { ...defaultConfig, ...config };
  }, [config]);

  // WebSocket connection management
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const wsUrl = process.env.REACT_APP_WS_URL || "ws://localhost:8000/ws";
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log("WebSocket connected");
        setConnectionStatus((prev) => ({
          ...prev,
          connected: true,
          reconnecting: false,
          lastConnected: new Date().toISOString(),
          reconnectAttempts: 0,
          error: null,
        }));

        // Start heartbeat
        startHeartbeat();
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          const realTimeData: RealTimeData = {
            type: message.type,
            data: message.data,
            timestamp: message.timestamp || new Date().toISOString(),
          };

          setData((prev) => [...prev.slice(-99), realTimeData]); // Keep last 100 messages

          // Notify subscribers
          subscribers.forEach((callback) => {
            try {
              callback(realTimeData);
            } catch (error) {
              console.error("Error in real-time subscriber:", error);
            }
          });
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      ws.onclose = (event) => {
        console.log("WebSocket disconnected:", event.code, event.reason);
        setConnectionStatus((prev) => ({
          ...prev,
          connected: false,
          error: event.reason || "Connection closed",
        }));

        // Attempt to reconnect if not manually closed
        if (event.code !== 1000 && configRef.current.enabled) {
          scheduleReconnect();
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setConnectionStatus((prev) => ({
          ...prev,
          error: "WebSocket connection error",
        }));
      };

      wsRef.current = ws;
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
      setConnectionStatus((prev) => ({
        ...prev,
        error: error instanceof Error ? error.message : "Connection failed",
      }));

      if (configRef.current.enabled) {
        scheduleReconnect();
      }
    }
  }, [subscribers]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close(1000, "Manual disconnect");
      wsRef.current = null;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }

    setConnectionStatus((prev) => ({
      ...prev,
      connected: false,
      reconnecting: false,
    }));
  }, []);

  const scheduleReconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    const { reconnectInterval, maxReconnectAttempts } = configRef.current;
    const { reconnectAttempts } = connectionStatus;

    if (reconnectAttempts >= maxReconnectAttempts) {
      console.log("Max reconnection attempts reached");
      setConnectionStatus((prev) => ({
        ...prev,
        error: "Max reconnection attempts reached",
      }));
      return;
    }

    setConnectionStatus((prev) => ({
      ...prev,
      reconnecting: true,
      reconnectAttempts: prev.reconnectAttempts + 1,
    }));

    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, reconnectInterval) as unknown as number; // Explicitly cast to number
  }, [connect, connectionStatus.reconnectAttempts]);

  const startHeartbeat = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
    }

    heartbeatTimeoutRef.current = setTimeout(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "ping" }));
        startHeartbeat();
      }
    }, configRef.current.heartbeatInterval) as unknown as number; // Explicitly cast to number
  }, []);

  // Subscribe to real-time data
  const subscribe = useCallback(
    (id: string, callback: (data: RealTimeData) => void) => {
      setSubscribers((prev) => new Map(prev.set(id, callback)));

      return () => {
        setSubscribers((prev) => {
          const newMap = new Map(prev);
          newMap.delete(id);
          return newMap;
        });
      };
    },
    [],
  );

  // Send message to server
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn("WebSocket not connected, cannot send message");
    }
  }, []);

  // Request specific data
  const requestData = useCallback(
    (type: string, filters?: any) => {
      sendMessage({
        type: "request",
        dataType: type,
        filters,
      });
    },
    [sendMessage],
  );

  // Subscribe to specific data types
  const subscribeToMetrics = useCallback(
    (callback: (data: any) => void) => {
      return subscribe("metrics", (realTimeData) => {
        if (realTimeData.type === "metrics") {
          callback(realTimeData.data);
        }
      });
    },
    [subscribe],
  );

  const subscribeToAlerts = useCallback(
    (callback: (data: any) => void) => {
      return subscribe("alerts", (realTimeData) => {
        if (realTimeData.type === "alerts") {
          callback(realTimeData.data);
        }
      });
    },
    [subscribe],
  );

  const subscribeToAI = useCallback(
    (callback: (data: any) => void) => {
      return subscribe("ai", (realTimeData) => {
        if (realTimeData.type === "ai") {
          callback(realTimeData.data);
        }
      });
    },
    [subscribe],
  );

  const subscribeToUsers = useCallback(
    (callback: (data: any) => void) => {
      return subscribe("users", (realTimeData) => {
        if (realTimeData.type === "users") {
          callback(realTimeData.data);
        }
      });
    },
    [subscribe],
  );

  const subscribeToSystem = useCallback(
    (callback: (data: any) => void) => {
      return subscribe("system", (realTimeData) => {
        if (realTimeData.type === "system") {
          callback(realTimeData.data);
        }
      });
    },
    [subscribe],
  );

  // Initialize connection
  useEffect(() => {
    if (configRef.current.enabled) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  // Auto-reconnect when config changes
  useEffect(() => {
    if (
      configRef.current.enabled &&
      !connectionStatus.connected &&
      !connectionStatus.reconnecting
    ) {
      connect();
    } else if (!configRef.current.enabled && connectionStatus.connected) {
      disconnect();
    }
  }, [
    config.enabled,
    connectionStatus.connected,
    connectionStatus.reconnecting,
    connect,
    disconnect,
  ]);

  return {
    // Connection status
    connectionStatus,
    isConnected: connectionStatus.connected,
    isReconnecting: connectionStatus.reconnecting,
    error: connectionStatus.error,

    // Data
    data,
    lastMessage: data[data.length - 1] || null,

    // Connection management
    connect,
    disconnect,
    reconnect: () => {
      disconnect();
      setTimeout(connect, 1000);
    },

    // Subscription methods
    subscribe,
    subscribeToMetrics,
    subscribeToAlerts,
    subscribeToAI,
    subscribeToUsers,
    subscribeToSystem,

    // Communication
    sendMessage,
    requestData,

    // Utility
    clearData: () => setData([]),
  };
};

export default useRealTime;
