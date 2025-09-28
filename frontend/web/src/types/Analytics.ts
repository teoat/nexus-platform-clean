/**
 * NEXUS Platform - Unified Analytics Interface
 * Single source of truth for Analytics types across the application
 */

export interface AnalyticsData {
  period: string;
  total_transactions: number;
  total_amount: number;
  average_transaction: number;
  transaction_trend: number;
  top_categories: Array<{
    category: string;
    amount: number;
    count: number;
    percentage: number;
  }>;
  monthly_breakdown: Array<{
    month: string;
    transactions: number;
    amount: number;
  }>;
}

export interface DashboardData {
  accounts: {
    total: number;
    active: number;
    total_balance: number;
    currency: string;
  };
  transactions: {
    total: number;
    this_month: number;
    pending: number;
    failed: number;
  };
  alerts: Array<{
    id: string;
    type: "warning" | "error" | "info";
    message: string;
    timestamp: string;
  }>;
  recent_transactions: Array<{
    id: string;
    amount: number;
    description: string;
    date: string;
    status: string;
  }>;
}

export interface HealthStatus {
  status: "healthy" | "degraded" | "unhealthy";
  uptime: number;
  response_time: number;
  last_check: string;
  services: Record<
    string,
    {
      status: "up" | "down" | "degraded";
      response_time?: number;
      last_check: string;
    }
  >;
}

export interface MetricsData {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_in: number;
  network_out: number;
  active_connections: number;
  timestamp: string;
}

export interface AlertData {
  id: string;
  type: "system" | "security" | "performance" | "business";
  severity: "low" | "medium" | "high" | "critical";
  title: string;
  message: string;
  timestamp: string;
  resolved: boolean;
  resolved_at?: string;
}

export interface PerformanceMetrics {
  page_load_time: number;
  api_response_time: number;
  error_rate: number;
  throughput: number;
  timestamp: string;
}

export interface MonitoringInsights {
  anomalies: Array<{
    type: string;
    severity: "low" | "medium" | "high";
    description: string;
    timestamp: string;
  }>;
  trends: Array<{
    metric: string;
    trend: "increasing" | "decreasing" | "stable";
    change_percentage: number;
  }>;
  recommendations: string[];
}
