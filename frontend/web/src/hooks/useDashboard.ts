/**
 * NEXUS Platform - useDashboard Hook
 * Custom hook for dashboard functionality and state management
 */

import { useEffect, useCallback, useMemo } from "react";
import { useDashboardStore } from "../store/dashboardStore";
import { dashboardService } from "../services/dashboardService";

export const useDashboard = () => {
  const {
    // State
    metrics,
    services,
    alerts,
    performanceData,
    selectedTimeRange,
    autoRefresh,
    refreshInterval,
    lastUpdated,
    isRealTimeEnabled,

    // Loading states
    metricsLoading,
    servicesLoading,
    alertsLoading,
    performanceLoading,

    // Error states
    metricsError,
    servicesError,
    alertsError,
    performanceError,

    // Actions
    fetchMetrics,
    fetchServices,
    fetchAlerts,
    fetchPerformanceData,
    setTimeRange,
    setAutoRefresh,
    setRefreshInterval,
    refreshAll,
    startRealTimeUpdates,
    stopRealTimeUpdates,
    clearAllErrors,
  } = useDashboardStore();

  // Initialize data on mount
  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  // Auto-refresh effect
  useEffect(() => {
    if (autoRefresh && !isRealTimeEnabled) {
      startRealTimeUpdates();
    } else if (!autoRefresh && isRealTimeEnabled) {
      stopRealTimeUpdates();
    }

    return () => {
      if (isRealTimeEnabled) {
        stopRealTimeUpdates();
      }
    };
  }, [
    autoRefresh,
    isRealTimeEnabled,
    startRealTimeUpdates,
    stopRealTimeUpdates,
  ]);

  // Computed values
  const systemHealth = useMemo(() => {
    if (!metrics) return "unknown";

    const { cpu = 0, memory = 0, errorRate = 0 } = metrics; // Provide default values

    if (cpu > 90 || memory > 90 || errorRate > 5) return "critical";
    if (cpu > 70 || memory > 70 || errorRate > 2) return "warning";
    return "healthy";
  }, [metrics]);

  const criticalAlerts = useMemo(() => {
    return alerts.filter(
      (alert) => alert.severity === "critical" && !alert.resolved,
    );
  }, [alerts]);

  const serviceStatus = useMemo(() => {
    const statusCounts = services.reduce(
      (acc, service) => {
        acc[service.status] = (acc[service.status] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>,
    );

    return {
      running: statusCounts.running || 0,
      stopped: statusCounts.stopped || 0,
      error: statusCounts.error || 0,
      warning: statusCounts.warning || 0,
      total: services.length,
    };
  }, [services]);

  const performanceTrends = useMemo(() => {
    if (performanceData.length < 2) return null;

    const latest = performanceData[performanceData.length - 1];
    const previous = performanceData[performanceData.length - 2];

    return {
      cpu: latest.cpu - previous.cpu,
      memory: latest.memory - previous.memory,
      requests: latest.requests - previous.requests,
      errors: latest.errors - previous.errors,
    };
  }, [performanceData]);

  // Action handlers
  const handleTimeRangeChange = useCallback(
    (timeRange: "1h" | "24h" | "7d" | "30d") => {
      setTimeRange(timeRange);
    },
    [setTimeRange],
  );

  const handleAutoRefreshToggle = useCallback(
    (enabled: boolean) => {
      setAutoRefresh(enabled);
    },
    [setAutoRefresh],
  );

  const handleRefreshIntervalChange = useCallback(
    (interval: number) => {
      setRefreshInterval(interval);
    },
    [setRefreshInterval],
  );

  const handleRefresh = useCallback(() => {
    refreshAll();
  }, [refreshAll]);

  const handleAcknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      await dashboardService.acknowledgeAlert(alertId);
      // The store will handle the state update
    } catch (error) {
      console.error("Failed to acknowledge alert:", error);
    }
  }, []);

  const handleResolveAlert = useCallback(async (alertId: string) => {
    try {
      await dashboardService.resolveAlert(alertId);
      // The store will handle the state update
    } catch (error) {
      console.error("Failed to resolve alert:", error);
    }
  }, []);

  const handleRestartService = useCallback(async (serviceName: string) => {
    try {
      await dashboardService.restartService(serviceName);
      // The store will handle the state update
    } catch (error) {
      console.error("Failed to restart service:", error);
    }
  }, []);

  const handleClearCache = useCallback(async () => {
    try {
      await dashboardService.clearCache();
      // Refresh data after cache clear
      refreshAll();
    } catch (error) {
      console.error("Failed to clear cache:", error);
    }
  }, [refreshAll]);

  const handleExportData = useCallback(
    async (format: "json" | "csv" | "xlsx" = "json") => {
      try {
        const response = await dashboardService.exportData(format);
        // Handle download URL
        if (response.data.downloadUrl) {
          window.open(response.data.downloadUrl, "_blank");
        }
      } catch (error) {
        console.error("Failed to export data:", error);
      }
    },
    [],
  );

  // Health check
  const healthCheck = useCallback(async () => {
    try {
      const response = await dashboardService.healthCheck();
      return response.data;
    } catch (error) {
      console.error("Health check failed:", error);
      return null;
    }
  }, []);

  // Loading state
  const isLoading =
    metricsLoading || servicesLoading || alertsLoading || performanceLoading;

  // Error state
  const hasError = !!(
    metricsError ||
    servicesError ||
    alertsError ||
    performanceError
  );

  // Error messages
  const errorMessages = useMemo(() => {
    const errors: string[] = [];
    if (metricsError) errors.push(`Metrics: ${metricsError}`);
    if (servicesError) errors.push(`Services: ${servicesError}`);
    if (alertsError) errors.push(`Alerts: ${alertsError}`);
    if (performanceError) errors.push(`Performance: ${performanceError}`);
    return errors;
  }, [metricsError, servicesError, alertsError, performanceError]);

  return {
    // Data
    metrics,
    services,
    alerts,
    performanceData,
    lastUpdated,

    // Computed values
    systemHealth,
    criticalAlerts,
    serviceStatus,
    performanceTrends,

    // UI state
    selectedTimeRange,
    autoRefresh,
    refreshInterval,
    isRealTimeEnabled,

    // Loading and error states
    isLoading,
    hasError,
    errorMessages,
    metricsLoading,
    servicesLoading,
    alertsLoading,
    performanceLoading,

    // Actions
    handleTimeRangeChange,
    handleAutoRefreshToggle,
    handleRefreshIntervalChange,
    handleRefresh,
    handleAcknowledgeAlert,
    handleResolveAlert,
    handleRestartService,
    handleClearCache,
    handleExportData,
    healthCheck,
    clearAllErrors,

    // Direct store actions
    fetchMetrics,
    fetchServices,
    fetchAlerts,
    fetchPerformanceData,
  };
};

export default useDashboard;
