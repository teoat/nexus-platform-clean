/**
 * NEXUS Platform - useAI Hook
 * Custom hook for AI functionality and state management
 */

import { useEffect, useCallback, useMemo } from 'react';
import { useAIStore } from '../store/aiStore';
import { aiService } from '../services/aiService';
import { TrainingConfig, PredictionRequest } from '../store/aiStore';

export const useAI = () => {
  const {
    // State
    metrics,
    models,
    insights,
    trainingStatus,
    config,
    selectedModel,
    selectedTimeRange,
    autoRefresh,
    refreshInterval,
    lastUpdated,
    metricsLoading,
    modelsLoading,
    insightsLoading,
    trainingLoading,
    configLoading,
    metricsError,
    modelsError,
    insightsError,
    trainingError,
    configError,

    // Actions
    fetchMetrics,
    fetchModels,
    fetchInsights,
    fetchConfig,
    updateConfig,
    selectModel,
    setTimeRange,
    setAutoRefresh,
    setRefreshInterval,
    clearAllErrors,
  } = useAIStore();

  // Initial data fetch
  const fetchAllData = useCallback(async () => {
    try {
      await Promise.all([
        fetchMetrics(),
        fetchModels(),
        fetchInsights(),
        fetchConfig(),
      ]);
    } catch (error) {
      console.error('Error fetching AI data:', error);
    }
  }, [fetchMetrics, fetchModels, fetchInsights, fetchConfig]);

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchAllData();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchAllData]); // Added fetchAllData to dependencies

  // Initial data fetch
  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  const handleStartTraining = useCallback(async (config: TrainingConfig) => {
    try {
      // TODO: Implement training start
      console.log('Starting training with config:', config);
    } catch (error) {
      console.error('Error starting training:', error);
    }
  }, []);

  const handleMakePrediction = useCallback(
    async (request: PredictionRequest) => {
      try {
        // TODO: Implement prediction
        console.log('Making prediction with request:', request);
      } catch (error) {
        console.error('Error making prediction:', error);
      }
    },
    []
  );

  const handleSendMessage = useCallback(
    async (message: string, context?: Record<string, any>) => {
      try {
        const response = await aiService.sendMessage(message, context);
        return response;
      } catch (error) {
        console.error('Error sending message:', error);
        throw error;
      }
    },
    []
  );

  const handleGetInsights = useCallback(async () => {
    try {
      const insights = await aiService.getInsights();
      return insights;
    } catch (error) {
      console.error('Error getting insights:', error);
      throw error;
    }
  }, []);

  // Computed values
  const systemHealth = useMemo(() => {
    if (!metrics) return 'unknown';

    const { modelAccuracy, inferenceSpeed, memoryUsage } = metrics;

    if (modelAccuracy < 70 || inferenceSpeed > 1000 || memoryUsage > 90)
      return 'critical';
    if (modelAccuracy < 85 || inferenceSpeed > 500 || memoryUsage > 70)
      return 'warning';
    return 'healthy';
  }, [metrics]);

  const activeInsights = useMemo(() => {
    return insights.filter(
      insight => insight.priority === 'high' || insight.priority === 'medium'
    );
  }, [insights]);

  const isLoading =
    metricsLoading ||
    modelsLoading ||
    insightsLoading ||
    trainingLoading ||
    configLoading;
  const hasError =
    metricsError ||
    modelsError ||
    insightsError ||
    trainingError ||
    configError;

  const systemStatus = useMemo(() => {
    if (isLoading) return 'loading';
    if (hasError) return 'error';
    if (systemHealth === 'critical') return 'critical';
    if (systemHealth === 'warning') return 'warning';
    return 'healthy';
  }, [isLoading, hasError, systemHealth]);

  return {
    // State
    metrics,
    models,
    insights,
    trainingStatus,
    config,
    selectedModel,
    selectedTimeRange,
    autoRefresh,
    refreshInterval,
    lastUpdated,
    isLoading,
    hasError,

    // Computed values
    systemHealth,
    activeInsights,
    systemStatus,

    // Actions
    fetchMetrics,
    fetchModels,
    fetchInsights,
    fetchConfig,
    updateConfig,
    selectModel,
    setTimeRange,
    setAutoRefresh,
    setRefreshInterval,
    clearAllErrors,
    fetchAllData,
    handleStartTraining,
    handleMakePrediction,
    handleSendMessage,
    handleGetInsights,
  };
};

export default useAI;
