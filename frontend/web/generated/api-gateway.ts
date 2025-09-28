// API Gateway Client
import { apiClient } from "../services/apiClient";

export interface GatewayStatus {
  status: string;
  services: string[];
  uptime: number;
}

export class ApiGatewayClient {
  async getStatus(): Promise<GatewayStatus> {
    return apiClient.get(
      "/api/v1/gateway/status",
    ) as unknown as Promise<GatewayStatus>;
  }

  async getHealth(): Promise<{
    healthy: boolean;
    services: Record<string, boolean>;
  }> {
    return apiClient.get("/api/v1/gateway/health") as unknown as Promise<{
      healthy: boolean;
      services: Record<string, boolean>;
    }>;
  }

  async getMetrics(): Promise<{
    requests: number;
    errors: number;
    latency: number;
  }> {
    return apiClient.get("/api/v1/gateway/metrics") as unknown as Promise<{
      requests: number;
      errors: number;
      latency: number;
    }>;
  }
}

export const apiGatewayClient = new ApiGatewayClient();
