/**
 * Monitoring Store
 * Manages unified monitoring data, alerts, and performance metrics
 */

import { create } from "zustand";
import { apiClient } from "../services/apiClient";

interface MonitoringMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  timestamp: string;
}

interface AlertData {
  id: string;
  title: string;
  message: string;
  severity: "low" | "medium" | "high" | "critical";
  status: "active" | "acknowledged" | "resolved";
  timestamp: string;
  source: string;
}

interface PerformanceData {
  responseTime: number;
  throughput: number;
  errorRate: number;
  uptime: number;
  score: number;
  timestamp: string;
}

interface InsightData {
  id: string;
  title: string;
  description: string;
  type: "warning" | "info" | "success" | "error";
  priority: "low" | "medium" | "high";
  timestamp: string;
  source: string;
}

interface MonitoringState {
  metrics: MonitoringMetrics | null;
  alerts: AlertData[];
  performance: PerformanceData | null;
  insights: InsightData[];
  isLoading: boolean;
  error: string | null;
  lastRefresh: Date | null;
  refreshInterval: number;
  fetchMetrics: () => Promise<void>;
  fetchAlerts: () => Promise<void>;
  fetchPerformance: () => Promise<void>;
  fetchInsights: () => Promise<void>;
  fetchAllData: () => Promise<void>;
  acknowledgeAlert: (alertId: string) => Promise<void>;
  setRefreshInterval: (interval: number) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
}

export const useMonitoringStore = create<MonitoringState>((set, get) => ({
  metrics: null,
  alerts: [],
  performance: null,
  insights: [],
  isLoading: false,
  error: null,
  lastRefresh: null,
  refreshInterval: 30000,

  fetchMetrics: async () => {
    try {
      set({ isLoading: true, error: null });
      const response = await apiClient.getMonitoringMetrics();
      set({
        metrics: response,
        isLoading: false,
        lastRefresh: new Date(),
      });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch metrics",
        isLoading: false,
      });
    }
  },

  fetchAlerts: async () => {
    try {
      set({ isLoading: true, error: null });
      const response = await apiClient.getAlerts();
      set({
        alerts: response,
        isLoading: false,
        lastRefresh: new Date(),
      });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch alerts",
        isLoading: false,
      });
    }
  },

  fetchPerformance: async () => {
    try {
      set({ isLoading: true, error: null });
      const response = await apiClient.getPerformanceMetrics();
      set({
        performance: response,
        isLoading: false,
        lastRefresh: new Date(),
      });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch performance data",
        isLoading: false,
      });
    }
  },

  fetchInsights: async () => {
    try {
      set({ isLoading: true, error: null });
      const insights = await apiClient.getMonitoringInsights();
      set({
        insights: insights as InsightData[],
        isLoading: false,
        lastRefresh: new Date(),
      });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch insights",
        isLoading: false,
      });
    }
  },

  fetchAllData: async () => {
    try {
      set({ isLoading: true, error: null });
      const [
        metricsResponse,
        alertsResponse,
        performanceResponse,
        insightsResponse,
      ] = await Promise.all([
        apiClient.getMonitoringMetrics(),
        apiClient.getAlerts(),
        apiClient.getPerformanceMetrics(),
        apiClient.getMonitoringInsights(),
      ]);
      set({
        metrics: metricsResponse,
        alerts: alertsResponse,
        performance: performanceResponse,
        insights: insightsResponse,
        isLoading: false,
        lastRefresh: new Date(),
      });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch monitoring data",
        isLoading: false,
      });
    }
  },

  acknowledgeAlert: async (alertId: string) => {
    try {
      await apiClient.acknowledgeAlert(alertId);
      set((state) => ({
        alerts: state.alerts.map((alert) =>
          alert.id === alertId
            ? { ...alert, status: "acknowledged" as const }
            : alert,
        ),
      }));
    } catch (error: any) {
      set({
        error: error.message || "Failed to acknowledge alert",
      });
    }
  },

  setRefreshInterval: (interval: number) => {
    set({ refreshInterval: interval });
  },

  clearError: () => {
    set({ error: null });
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },
}));

export const useMonitoringSelectors = () => {
  const state = useMonitoringStore();

  return {
    systemHealth: (() => {
      if (!state.metrics || !state.performance) return "unknown";

      const criticalAlerts = state.alerts.filter(
        (alert) => alert.severity === "critical" && alert.status === "active",
      );

      if (criticalAlerts.length > 0) return "critical";
      if (state.performance.errorRate > 5) return "warning";
      if (state.performance.score < 80) return "warning";

      return "healthy";
    })(),

    activeAlertsCount: state.alerts.filter((alert) => alert.status === "active")
      .length,
    criticalAlertsCount: state.alerts.filter(
      (alert) => alert.severity === "critical" && alert.status === "active",
    ).length,
    performanceScore: state.performance?.score || 0,
    responseTime: state.performance?.responseTime || 0,
    errorRate: state.performance?.errorRate || 0,
    resourceUsage: {
      cpu: state.metrics?.cpu || 0,
      memory: state.metrics?.memory || 0,
      disk: state.metrics?.disk || 0,
      network: state.metrics?.network || 0,
    },
  };
};

export type { MonitoringMetrics, AlertData, PerformanceData, InsightData };
