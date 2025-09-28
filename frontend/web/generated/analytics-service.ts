// Analytics Service Client
import { apiClient } from "../services/apiClient";

export interface AnalyticsData {
  id: string;
  event: string;
  properties: Record<string, any>;
  timestamp: string;
  userId: string;
}

export interface AnalyticsResponse {
  data: AnalyticsData[];
  total: number;
  page: number;
  limit: number;
}

export class AnalyticsServiceClient {
  async getAnalytics(params?: {
    page?: number;
    limit?: number;
    event?: string;
  }): Promise<AnalyticsResponse> {
    return apiClient.get("/api/v1/analytics", {
      params,
    }) as unknown as Promise<AnalyticsResponse>;
  }

  async trackEvent(
    event: string,
    properties?: Record<string, any>,
  ): Promise<void> {
    return apiClient.post("/api/v1/analytics/track", {
      event,
      properties,
    }) as unknown as Promise<void>;
  }

  async getEventMetrics(
    event: string,
  ): Promise<{ count: number; uniqueUsers: number }> {
    return apiClient.get(
      `/api/v1/analytics/events/${event}/metrics`,
    ) as unknown as Promise<{ count: number; uniqueUsers: number }>;
  }
}

export const analyticsService = new AnalyticsServiceClient();
