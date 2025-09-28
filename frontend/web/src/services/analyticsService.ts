import { apiClient } from "./apiClient";

export interface AnalyticsMetrics {
  systemHealth: string;
  anomalyStatus: string;
  riskLevel: string;
  recentAnomalies: number;
  activeMetrics: number;
  latestRiskScore: number;
}

export interface AnomalyData {
  timestamp: string;
  metric_name: string;
  value: number;
  predicted_value: number;
  anomaly_score: number;
  is_anomaly: boolean;
  confidence: number;
}

export interface RiskAssessment {
  assessment_id: string;
  timestamp: string;
  risk_level: string;
  risk_score: number;
  factors: Record<string, number>;
  recommendations: string[];
  confidence: number;
}

export interface TrendAnalysis {
  metric_name: string;
  trend_direction: string;
  slope: number;
  volatility: number;
  short_ma: number;
  long_ma: number;
  data_points: number;
  time_range: {
    start: string;
    end: string;
  };
}

export interface ForecastResult {
  metric_name: string;
  forecast: {
    predicted_value: number;
    confidence_interval: [number, number];
    trend: string;
    forecast_horizon: number;
    model_accuracy: number;
  };
  data_points_used: number;
}

export interface AnalyticsSummary {
  engine_running: boolean;
  recent_anomalies: number;
  latest_risk_level: string;
  latest_risk_score: number;
  latest_risk_confidence: number;
  active_metrics: number;
  analysis_history_count: number;
}

export interface MetricsSummary {
  monitoring_metrics: any;
  analytics_summary: AnalyticsSummary;
  combined_insights: {
    system_health: string;
    anomaly_status: string;
    risk_level: string;
  };
}

class AnalyticsService {
  private baseUrl = "/api/v1/analytics";

  async getStatus(): Promise<{ success: boolean; data: AnalyticsSummary }> {
    const response = await apiClient.get(`${this.baseUrl}/status`);
    return response.data as { success: boolean; data: AnalyticsSummary };
  }

  async getAnomalies(
    hours: number = 24,
    metricName?: string,
  ): Promise<{ success: boolean; data: any }> {
    const params = new URLSearchParams();
    params.append("hours", hours.toString());
    if (metricName) {
      params.append("metric_name", metricName);
    }

    const response = await apiClient.get(`${this.baseUrl}/anomalies?${params}`);
    return response.data as { success: boolean; data: any };
  }

  async getRiskAssessments(
    limit: number = 10,
  ): Promise<{ success: boolean; data: any }> {
    const response = await apiClient.get(
      `${this.baseUrl}/risk-assessments?limit=${limit}`,
    );
    return response.data as { success: boolean; data: any };
  }

  async analyzeTrends(
    metricName: string,
    data: Array<{
      timestamp: string;
      value: number;
      tags?: Record<string, string>;
    }>,
  ): Promise<{
    success: boolean;
    data: {
      metric_name: string;
      trend_analysis: TrendAnalysis;
      data_points_analyzed: number;
    };
  }> {
    const response = await apiClient.post(`${this.baseUrl}/analyze/trends`, {
      metric_name: metricName,
      data: data,
    });
    return response.data as {
      success: boolean;
      data: {
        metric_name: string;
        trend_analysis: TrendAnalysis;
        data_points_analyzed: number;
      };
    };
  }

  async generateForecast(
    metricName: string,
    data: Array<{
      timestamp: string;
      value: number;
      tags?: Record<string, string>;
    }>,
    hoursAhead: number = 24,
  ): Promise<{ success: boolean; data: ForecastResult }> {
    const response = await apiClient.post(`${this.baseUrl}/analyze/forecast`, {
      metric_name: metricName,
      data: data,
      hours_ahead: hoursAhead,
    });
    return response.data as { success: boolean; data: ForecastResult };
  }

  async detectAnomalies(
    metricName: string,
    data: Array<{
      timestamp: string;
      value: number;
      tags?: Record<string, string>;
    }>,
  ): Promise<{ success: boolean; data: any }> {
    const response = await apiClient.post(`${this.baseUrl}/analyze/anomalies`, {
      metric_name: metricName,
      data: data,
    });
    return response.data as { success: boolean; data: any };
  }

  async assessRisk(
    metrics: Record<string, number>,
  ): Promise<{ success: boolean; data: any }> {
    const response = await apiClient.post(`${this.baseUrl}/analyze/risk`, {
      metrics: metrics,
    });
    return response.data as { success: boolean; data: any };
  }

  async startEngine(): Promise<{
    success: boolean;
    data: { message: string };
  }> {
    const response = await apiClient.post(`${this.baseUrl}/start`);
    return response.data as { success: boolean; data: { message: string } };
  }

  async stopEngine(): Promise<{ success: boolean; data: { message: string } }> {
    const response = await apiClient.post(`${this.baseUrl}/stop`);
    return response.data as { success: boolean; data: { message: string } };
  }

  async getHealth(): Promise<{
    status: string;
    engine_running: boolean;
    recent_anomalies: number;
    latest_risk_level: string;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/health`);
    return response.data as {
      status: string;
      engine_running: boolean;
      recent_anomalies: number;
      latest_risk_level: string;
    };
  }

  async getMetricsSummary(): Promise<{
    success: boolean;
    data: MetricsSummary;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/metrics/summary`);
    return response.data as { success: boolean; data: MetricsSummary };
  }

  // Utility methods for data processing
  formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
  }

  formatRiskLevel(riskLevel: string): string {
    return riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1);
  }

  getRiskColor(riskLevel: string): "success" | "warning" | "error" | "default" {
    switch (riskLevel.toLowerCase()) {
      case "low":
        return "success";
      case "medium":
        return "warning";
      case "high":
        return "error";
      case "critical":
        return "error";
      default:
        return "default";
    }
  }

  getHealthColor(status: string): "success" | "warning" | "error" | "default" {
    switch (status.toLowerCase()) {
      case "healthy":
        return "success";
      case "warning":
        return "warning";
      case "critical":
        return "error";
      default:
        return "default";
    }
  }

  calculateAnomalyRate(anomalies: AnomalyData[]): number {
    if (anomalies.length === 0) return 0;
    const anomalyCount = anomalies.filter((a) => a.is_anomaly).length;
    return (anomalyCount / anomalies.length) * 100;
  }

  prepareChartData(anomalies: AnomalyData[], limit: number = 20) {
    return anomalies.slice(-limit).map((anomaly) => ({
      time: new Date(anomaly.timestamp).toLocaleTimeString(),
      value: anomaly.value,
      predicted: anomaly.predicted_value,
      anomaly: anomaly.is_anomaly ? anomaly.value : null,
      score: anomaly.anomaly_score,
    }));
  }

  prepareRiskChartData(assessments: RiskAssessment[]) {
    return assessments.map((assessment) => ({
      time: new Date(assessment.timestamp).toLocaleDateString(),
      score: assessment.risk_score,
      level: assessment.risk_level,
      confidence: assessment.confidence,
    }));
  }

  prepareTrendChartData(trendData: TrendAnalysis[]) {
    return trendData.map((trend) => ({
      metric: trend.metric_name,
      slope: trend.slope,
      volatility: trend.volatility,
      short_ma: trend.short_ma,
      long_ma: trend.long_ma,
      direction: trend.trend_direction,
    }));
  }

  // Real-time data simulation for demo purposes
  generateMockTimeSeriesData(
    metricName: string,
    hours: number = 24,
  ): Array<{
    timestamp: string;
    value: number;
    tags?: Record<string, string>;
  }> {
    const data = [];
    const now = new Date();

    for (let i = hours; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
      const baseValue = 50 + Math.sin(i * 0.1) * 20;
      const noise = (Math.random() - 0.5) * 10;
      const value = Math.max(0, baseValue + noise);

      data.push({
        timestamp: timestamp.toISOString(),
        value: Math.round(value * 100) / 100,
        tags: { source: "simulation" },
      });
    }

    return data;
  }

  // Batch operations for multiple metrics
  async analyzeMultipleTrends(
    metrics: Array<{
      name: string;
      data: Array<{
        timestamp: string;
        value: number;
        tags?: Record<string, string>;
      }>;
    }>,
  ): Promise<Array<{ metric_name: string; trend_analysis: TrendAnalysis }>> {
    const promises = metrics.map((metric) =>
      this.analyzeTrends(metric.name, metric.data),
    );

    const results = await Promise.all(promises);
    return results.map((result) => result.data);
  }

  async detectMultipleAnomalies(
    metrics: Array<{
      name: string;
      data: Array<{
        timestamp: string;
        value: number;
        tags?: Record<string, string>;
      }>;
    }>,
  ): Promise<Array<{ metric_name: string; anomalies: AnomalyData[] }>> {
    const promises = metrics.map((metric) =>
      this.detectAnomalies(metric.name, metric.data),
    );

    const results = await Promise.all(promises);
    return results.map((result) => result.data);
  }
}

export const analyticsService = new AnalyticsService();
