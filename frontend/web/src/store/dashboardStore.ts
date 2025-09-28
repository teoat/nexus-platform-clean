import { create } from 'zustand';

export interface DashboardState {
  // Dashboard data
  metrics: {
    totalUsers: number;
    activeUsers: number;
    totalRevenue: number;
    monthlyGrowth: number;
    cpu?: number; // Added
    memory?: number; // Added
    errorRate?: number; // Added
  };

  services: any[];
  alerts: any[];
  performanceData: any;
  selectedTimeRange: string;
  autoRefresh: boolean;
  refreshInterval: number;
  lastUpdated: Date | null;
  isRealTimeEnabled: boolean;

  // UI state
  isLoading: boolean;
  error: string | null;
  metricsLoading: boolean;
  servicesLoading: boolean;
  alertsLoading: boolean;
  performanceLoading: boolean;
  metricsError: string | null;
  servicesError: string | null;
  alertsError: string | null;
  performanceError: string | null;

  // Actions
  setMetrics: (metrics: Partial<DashboardState['metrics']>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  fetchMetrics: () => Promise<void>;
  fetchServices: () => Promise<void>;
  fetchAlerts: () => Promise<void>;
  fetchPerformanceData: () => Promise<void>;
  setTimeRange: (range: string) => void;
  setAutoRefresh: (enabled: boolean) => void;
  setRefreshInterval: (interval: number) => void;
  refreshAll: () => Promise<void>;
  startRealTimeUpdates: () => void;
  stopRealTimeUpdates: () => void;
  clearAllErrors: () => void;
  reset: () => void;
}

export const useDashboardStore = create<DashboardState>(set => ({
  // Initial state
  metrics: {
    totalUsers: 0,
    activeUsers: 0,
    totalRevenue: 0,
    monthlyGrowth: 0,
    cpu: 0,
    memory: 0,
    errorRate: 0,
  },

  services: [],
  alerts: [],
  performanceData: null,
  selectedTimeRange: '24h',
  autoRefresh: false,
  refreshInterval: 30000,
  lastUpdated: null,
  isRealTimeEnabled: false,

  isLoading: false,
  error: null,
  metricsLoading: false,
  servicesLoading: false,
  alertsLoading: false,
  performanceLoading: false,
  metricsError: null,
  servicesError: null,
  alertsError: null,
  performanceError: null,

  // Actions
  setMetrics: metrics =>
    set(state => ({
      metrics: { ...state.metrics, ...metrics },
    })),

  setLoading: loading => set({ isLoading: loading }),

  setError: error => set({ error }),

  fetchMetrics: async () => {
    set({ metricsLoading: true, metricsError: null });
    try {
      // Mock metrics fetch
      await new Promise(resolve => setTimeout(resolve, 1000));
      set({
        metrics: {
          totalUsers: 100,
          activeUsers: 80,
          totalRevenue: 50000,
          monthlyGrowth: 15,
          cpu: 45,
          memory: 67,
          errorRate: 0.1,
        },
        metricsLoading: false,
      });
    } catch (error) {
      set({ metricsError: 'Failed to fetch metrics', metricsLoading: false });
    }
  },

  fetchServices: async () => {
    set({ servicesLoading: true, servicesError: null });
    try {
      // Mock services fetch
      await new Promise(resolve => setTimeout(resolve, 1000));
      set({ services: [], servicesLoading: false });
    } catch (error) {
      set({
        servicesError: 'Failed to fetch services',
        servicesLoading: false,
      });
    }
  },

  fetchAlerts: async () => {
    set({ alertsLoading: true, alertsError: null });
    try {
      // Mock alerts fetch
      await new Promise(resolve => setTimeout(resolve, 1000));
      set({ alerts: [], alertsLoading: false });
    } catch (error) {
      set({ alertsError: 'Failed to fetch alerts', alertsLoading: false });
    }
  },

  fetchPerformanceData: async () => {
    set({ performanceLoading: true, performanceError: null });
    try {
      // Mock performance data fetch
      await new Promise(resolve => setTimeout(resolve, 1000));
      set({ performanceData: null, performanceLoading: false });
    } catch (error) {
      set({
        performanceError: 'Failed to fetch performance data',
        performanceLoading: false,
      });
    }
  },

  setTimeRange: range => set({ selectedTimeRange: range }),

  setAutoRefresh: enabled => set({ autoRefresh: enabled }),

  setRefreshInterval: interval => set({ refreshInterval: interval }),

  refreshAll: async () => {
    set({ isLoading: true });
    try {
      await Promise.all([
        // Mock refresh all
        new Promise(resolve => setTimeout(resolve, 1000)),
      ]);
      set({ lastUpdated: new Date(), isLoading: false });
    } catch (error) {
      set({ error: 'Failed to refresh data', isLoading: false });
    }
  },

  startRealTimeUpdates: () => set({ isRealTimeEnabled: true }),

  stopRealTimeUpdates: () => set({ isRealTimeEnabled: false }),

  clearAllErrors: () =>
    set({
      error: null,
      metricsError: null,
      servicesError: null,
      alertsError: null,
      performanceError: null,
    }),

  reset: () =>
    set({
      metrics: {
        totalUsers: 0,
        activeUsers: 0,
        totalRevenue: 0,
        monthlyGrowth: 0,
        cpu: 0,
        memory: 0,
        errorRate: 0,
      },
      services: [],
      alerts: [],
      performanceData: null,
      selectedTimeRange: '24h',
      autoRefresh: false,
      refreshInterval: 30000,
      lastUpdated: null,
      isRealTimeEnabled: false,
      isLoading: false,
      error: null,
      metricsLoading: false,
      servicesLoading: false,
      alertsLoading: false,
      performanceLoading: false,
      metricsError: null,
      servicesError: null,
      alertsError: null,
      performanceError: null,
    }),
}));
