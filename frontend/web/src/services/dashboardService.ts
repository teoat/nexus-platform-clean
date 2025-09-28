import { apiClient } from "./apiClient";

export interface DashboardMetrics {
  totalUsers: number;
  activeUsers: number;
  totalRevenue: number;
  monthlyGrowth: number;
}

export interface DashboardData {
  metrics: DashboardMetrics;
  charts: {
    userGrowth: Array<{ date: string; users: number }>;
    revenue: Array<{ month: string; amount: number }>;
  };
}

export class DashboardService {
  async getDashboardData(): Promise<DashboardData> {
    const response = await apiClient.get<DashboardData>("/dashboard");
    return response.data;
  }

  async getMetrics(): Promise<DashboardMetrics> {
    const response =
      await apiClient.get<DashboardMetrics>("/dashboard/metrics");
    return response.data;
  }

  async getUserGrowth(): Promise<Array<{ date: string; users: number }>> {
    const response = await apiClient.get<
      Array<{ date: string; users: number }>
    >("/dashboard/user-growth");
    return response.data;
  }

  async getRevenueData(): Promise<Array<{ month: string; amount: number }>> {
    const response =
      await apiClient.get<Array<{ month: string; amount: number }>>(
        "/dashboard/revenue",
      );
    return response.data;
  }

  async acknowledgeAlert(alertId: string): Promise<void> {
    await apiClient.post(`/dashboard/alerts/${alertId}/acknowledge`);
  }

  async resolveAlert(alertId: string): Promise<void> {
    await apiClient.post(`/dashboard/alerts/${alertId}/resolve`);
  }

  async restartService(serviceName: string): Promise<void> {
    await apiClient.post(`/dashboard/services/${serviceName}/restart`, {});
  }

  async clearCache(): Promise<void> {
    await apiClient.post("/dashboard/cache/clear", {});
  }

  async exportData(format: "json" | "csv" | "xlsx"): Promise<any> {
    const response = await apiClient.get(`/dashboard/export?format=${format}`);
    return response.data;
  }

  async healthCheck(): Promise<any> {
    const response = await apiClient.get("/dashboard/health");
    return response.data;
  }
}

export const dashboardService = new DashboardService();
export default dashboardService;
