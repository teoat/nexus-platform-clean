/**
 * NEXUS Platform - AI Store
 * Zustand store for AI system state management
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { aiService, AIInsight, AIConfiguration } from '../services/aiService';

export interface AIMetrics {
  totalRequests: number;
  successfulRequests: number;
  averageResponseTime: number;
  errorRate: number;
  lastActivity: string;
  activeModels: string[];
  memoryUsage: number;
  cpuUsage: number;
  modelAccuracy: number;
  inferenceSpeed: number;
  trainingProgress: number;
  totalPredictions: number;
  learningRate: number;
  confidence: number;
}

export interface AIModel {
  id: string;
  name: string;
  provider: string;
  version: string;
  status: 'active' | 'inactive' | 'training' | 'error';
  capabilities: string[];
  performance: {
    accuracy: number;
    speed: number;
    memory: number;
  };
  lastUpdated: string;
}

export interface TrainingConfig {
  modelId: string;
  dataset: string;
  epochs: number;
  batchSize: number;
  learningRate: number;
  validationSplit: number;
}

export interface PredictionRequest {
  modelId: string;
  input: Record<string, any>;
  context?: Record<string, any>;
}

export interface AIState {
  // AI Metrics
  metrics: AIMetrics | null;
  metricsLoading: boolean;
  metricsError: string | null;

  // Models
  models: AIModel[];
  modelsLoading: boolean;
  modelsError: string | null;
  selectedModel: AIModel | null;

  // Insights
  insights: AIInsight[];
  insightsLoading: boolean;
  insightsError: string | null;

  // Training
  trainingStatus: Record<string, any>;
  trainingLoading: boolean;
  trainingError: string | null;

  // Configuration
  config: AIConfiguration | null;
  configLoading: boolean;
  configError: string | null;

  // UI state
  selectedTimeRange: '1h' | '24h' | '7d' | '30d';
  autoRefresh: boolean;
  refreshInterval: number;
  lastUpdated: string | null;

  // Real-time updates
  realTimeEnabled: boolean;
  isConnected: boolean;
}

export interface AIActions {
  // Metrics actions
  fetchMetrics: () => Promise<void>;
  setMetrics: (metrics: AIMetrics) => void;
  clearMetricsError: () => void;

  // Models actions
  fetchModels: () => Promise<void>;
  setModels: (models: AIModel[]) => void;
  clearModelsError: () => void;
  selectModel: (model: AIModel | null) => void;

  // Insights actions
  fetchInsights: () => Promise<void>;
  setInsights: (insights: AIInsight[]) => void;
  clearInsightsError: () => void;

  // Training actions
  startTraining: (config: TrainingConfig) => Promise<void>;
  setTrainingStatus: (trainingId: string, status: any) => void;
  clearTrainingError: () => void;

  // Configuration actions
  fetchConfig: () => Promise<void>;
  updateConfig: (config: Partial<AIConfiguration>) => Promise<void>;
  setConfig: (config: AIConfiguration) => void;
  clearConfigError: () => void;

  // UI actions
  setTimeRange: (timeRange: '1h' | '24h' | '7d' | '30d') => void;
  setAutoRefresh: (enabled: boolean) => void;
  setRefreshInterval: (interval: number) => void;
  refreshAll: () => Promise<void>;

  // Real-time actions
  startRealTimeUpdates: () => void;
  stopRealTimeUpdates: () => void;
  setRealTimeEnabled: (enabled: boolean) => void;

  // Utility actions
  clearAllErrors: () => void;
  reset: () => void;
}

export const useAIStore = create<AIState & AIActions>()(
  persist(
    (set, get) => ({
      // Initial state
      metrics: null,
      metricsLoading: false,
      metricsError: null,

      models: [],
      modelsLoading: false,
      modelsError: null,
      selectedModel: null,

      insights: [],
      insightsLoading: false,
      insightsError: null,

      trainingStatus: {},
      trainingLoading: false,
      trainingError: null,

      config: null,
      configLoading: false,
      configError: null,

      selectedTimeRange: '24h',
      autoRefresh: true,
      refreshInterval: 30000,
      lastUpdated: null,

      realTimeEnabled: false,
      isConnected: false,

      // Actions
      fetchMetrics: async () => {
        set({ metricsLoading: true, metricsError: null });
        try {
          const metrics = await aiService.getMetrics();
          set({
            metrics,
            metricsLoading: false,
            lastUpdated: new Date().toISOString(),
          });
        } catch (error) {
          set({
            metricsError:
              error instanceof Error
                ? error.message
                : 'Failed to fetch AI metrics',
            metricsLoading: false,
          });
        }
      },

      setMetrics: metrics => set({ metrics }),

      clearMetricsError: () => set({ metricsError: null }),

      fetchModels: async () => {
        set({ modelsLoading: true, modelsError: null });
        try {
          const models = await aiService.getModels();
          set({
            models,
            modelsLoading: false,
            lastUpdated: new Date().toISOString(),
          });
        } catch (error) {
          set({
            modelsError:
              error instanceof Error ? error.message : 'Failed to fetch models',
            modelsLoading: false,
          });
        }
      },

      setModels: models => set({ models }),

      clearModelsError: () => set({ modelsError: null }),

      selectModel: model => set({ selectedModel: model }),

      fetchInsights: async () => {
        set({ insightsLoading: true, insightsError: null });
        try {
          const insights = await aiService.getInsights();
          set({
            insights,
            insightsLoading: false,
            lastUpdated: new Date().toISOString(),
          });
        } catch (error) {
          set({
            insightsError:
              error instanceof Error
                ? error.message
                : 'Failed to fetch insights',
            insightsLoading: false,
          });
        }
      },

      setInsights: insights => set({ insights }),

      clearInsightsError: () => set({ insightsError: null }),

      startTraining: async config => {
        set({ trainingLoading: true, trainingError: null });
        try {
          // TODO: Implement training start
          console.log('Starting training with config:', config);
          set({
            trainingLoading: false,
            lastUpdated: new Date().toISOString(),
          });
        } catch (error) {
          set({
            trainingError:
              error instanceof Error
                ? error.message
                : 'Failed to start training',
            trainingLoading: false,
          });
        }
      },

      setTrainingStatus: (trainingId, status) => {
        set(state => ({
          trainingStatus: {
            ...state.trainingStatus,
            [trainingId]: status,
          },
        }));
      },

      clearTrainingError: () => set({ trainingError: null }),

      fetchConfig: async () => {
        set({ configLoading: true, configError: null });
        try {
          const config = await aiService.getConfiguration();
          set({
            config,
            configLoading: false,
            lastUpdated: new Date().toISOString(),
          });
        } catch (error) {
          set({
            configError:
              error instanceof Error
                ? error.message
                : 'Failed to fetch configuration',
            configLoading: false,
          });
        }
      },

      updateConfig: async configUpdates => {
        try {
          await aiService.updateAIConfig(configUpdates);
          set(state => ({
            config: state.config
              ? { ...state.config, ...configUpdates }
              : (configUpdates as AIConfiguration),
          }));
        } catch (error) {
          console.error('Failed to update AI config:', error);
        }
      },

      setConfig: config => set({ config }),

      clearConfigError: () => set({ configError: null }),

      setTimeRange: timeRange => set({ selectedTimeRange: timeRange }),

      setAutoRefresh: enabled => set({ autoRefresh: enabled }),

      setRefreshInterval: interval => set({ refreshInterval: interval }),

      refreshAll: async () => {
        const { fetchMetrics, fetchModels, fetchInsights, fetchConfig } = get();
        await Promise.all([
          fetchMetrics(),
          fetchModels(),
          fetchInsights(),
          fetchConfig(),
        ]);
      },

      startRealTimeUpdates: () => {
        set({ realTimeEnabled: true });
        // TODO: Implement real-time updates
      },

      stopRealTimeUpdates: () => {
        set({ realTimeEnabled: false });
        // TODO: Stop real-time updates
      },

      setRealTimeEnabled: enabled => set({ realTimeEnabled: enabled }),

      clearAllErrors: () => {
        set({
          metricsError: null,
          modelsError: null,
          insightsError: null,
          trainingError: null,
          configError: null,
        });
      },

      reset: () => {
        set({
          metrics: null,
          models: [],
          insights: [],
          trainingStatus: {},
          config: null,
          selectedModel: null,
          selectedTimeRange: '24h',
          autoRefresh: true,
          refreshInterval: 30000,
          lastUpdated: null,
          realTimeEnabled: false,
          isConnected: false,
        });
      },
    }),
    {
      name: 'ai-store',
      partialize: state => ({
        selectedTimeRange: state.selectedTimeRange,
        autoRefresh: state.autoRefresh,
        refreshInterval: state.refreshInterval,
        realTimeEnabled: state.realTimeEnabled,
      }),
    }
  )
);

export default useAIStore;
