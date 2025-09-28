// NEXUS Platform - Generated API Clients
// Auto-generated from backend OpenAPI schemas

// API Gateway Client
export * from "./api-gateway";

// Service Clients
export * from "./user-service";
export * from "./account-service";
export * from "./transaction-service";
export * from "./analytics-service";
export * from "./file-service";
export * from "./notification-service";

// Client Factory
export class NexusAPIClient {
  private baseURL: string;
  private apiKey?: string;

  constructor(
    baseURL: string = process.env.REACT_APP_API_BASE_URL ||
      "http://localhost:8000",
    apiKey?: string,
  ) {
    this.baseURL = baseURL;
    this.apiKey = apiKey;
  }

  // Get service-specific client
  getServiceClient(service: string) {
    const serviceMap: Record<string, any> = {
      "api-gateway": () => import("./api-gateway"),
      "user-service": () => import("./user-service"),
      "account-service": () => import("./account-service"),
      "transaction-service": () => import("./transaction-service"),
      "analytics-service": () => import("./analytics-service"),
      "file-service": () => import("./file-service"),
      "notification-service": () => import("./notification-service"),
    };

    return serviceMap[service]?.();
  }
}

// Default client instance
export const nexusClient = new NexusAPIClient();
