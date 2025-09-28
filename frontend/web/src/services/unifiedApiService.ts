/**
 * NEXUS Platform - Unified API Service
 * Centralized API communication with advanced features
 */

import { apiClient } from "./apiClient";
import { ApiResponse } from "../types/ApiResponse";

export type { ApiResponse };

export interface ApiConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  retryDelay: number;
}

export interface RequestOptions {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

export interface CacheConfig {
  enabled: boolean;
  ttl: number; // Time to live in milliseconds
  key?: string;
}

class UnifiedApiService {
  private config: ApiConfig;
  private cache: Map<string, { data: any; timestamp: number; ttl: number }> =
    new Map();

  constructor(config: Partial<ApiConfig> = {}) {
    this.config = {
      baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
      timeout: 30000,
      retries: 3,
      retryDelay: 1000,
      ...config,
    };
  }

  private getCacheKey(endpoint: string, params?: any): string {
    const paramString = params ? JSON.stringify(params) : "";
    return `${endpoint}${paramString}`;
  }

  private getCachedData(key: string): any | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const now = Date.now();
    if (now - cached.timestamp > cached.ttl) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  private setCachedData(key: string, data: any, ttl: number): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  }

  private async retryRequest<T>(
    requestFn: () => Promise<ApiResponse<T>>,
    retries: number,
    delay: number,
  ): Promise<ApiResponse<T>> {
    try {
      return await requestFn();
    } catch (error) {
      if (retries > 0) {
        await new Promise((resolve) => setTimeout(resolve, delay));
        return this.retryRequest(requestFn, retries - 1, delay * 2);
      }
      throw error;
    }
  }

  async get<T>(
    endpoint: string,
    params?: Record<string, any>,
    options: RequestOptions & { cache?: CacheConfig } = {},
  ): Promise<ApiResponse<T>> {
    const { cache, ...requestOptions } = options;

    // Check cache first
    if (cache?.enabled) {
      const cacheKey = this.getCacheKey(endpoint, params);
      const cachedData = this.getCachedData(cacheKey);
      if (cachedData) {
        return { data: cachedData, success: true };
      }
    }

    const requestFn = () => apiClient.get<T>(endpoint, params);
    const response = await this.retryRequest(
      requestFn,
      requestOptions.retries || this.config.retries,
      requestOptions.retryDelay || this.config.retryDelay,
    );

    // Cache successful responses
    if (cache?.enabled && response.success) {
      const cacheKey = this.getCacheKey(endpoint, params);
      this.setCachedData(cacheKey, response.data, cache.ttl);
    }

    return response;
  }

  async post<T>(
    endpoint: string,
    data?: any,
    options: RequestOptions = {},
  ): Promise<ApiResponse<T>> {
    const requestFn = () => apiClient.post<T>(endpoint, data);
    return this.retryRequest(
      requestFn,
      options.retries || this.config.retries,
      options.retryDelay || this.config.retryDelay,
    );
  }

  async put<T>(
    endpoint: string,
    data?: any,
    options: RequestOptions = {},
  ): Promise<ApiResponse<T>> {
    const requestFn = () => apiClient.put<T>(endpoint, data);
    return this.retryRequest(
      requestFn,
      options.retries || this.config.retries,
      options.retryDelay || this.config.retryDelay,
    );
  }

  async patch<T>(
    endpoint: string,
    data?: any,
    options: RequestOptions = {},
  ): Promise<ApiResponse<T>> {
    const requestFn = () => apiClient.patch<T>(endpoint, data);
    return this.retryRequest(
      requestFn,
      options.retries || this.config.retries,
      options.retryDelay || this.config.retryDelay,
    );
  }

  async delete<T>(
    endpoint: string,
    options: RequestOptions = {},
  ): Promise<ApiResponse<T>> {
    const requestFn = () => apiClient.delete<T>(endpoint);
    return this.retryRequest(
      requestFn,
      options.retries || this.config.retries,
      options.retryDelay || this.config.retryDelay,
    );
  }

  async uploadFile<T>(
    endpoint: string,
    file: File,
    onProgress?: (progress: number) => void,
    options: RequestOptions = {},
  ): Promise<ApiResponse<T>> {
    return apiClient.uploadFile<T>(endpoint, file, onProgress);
  }

  // Batch operations
  async batch<T>(
    requests: Array<{
      method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
      endpoint: string;
      data?: any;
      params?: Record<string, any>;
    }>,
    options: RequestOptions = {},
  ): Promise<ApiResponse<T>[]> {
    const promises = requests.map((request) => {
      switch (request.method) {
        case "GET":
          return this.get<T>(request.endpoint, request.params, options);
        case "POST":
          return this.post<T>(request.endpoint, request.data, options);
        case "PUT":
          return this.put<T>(request.endpoint, request.data, options);
        case "PATCH":
          return this.patch<T>(request.endpoint, request.data, options);
        case "DELETE":
          return this.delete<T>(request.endpoint, options);
        default:
          throw new Error(`Unsupported method: ${request.method}`);
      }
    });

    return Promise.all(promises);
  }

  // Real-time subscriptions
  subscribe<T>(
    endpoint: string,
    onMessage: (data: T) => void,
    onError?: (error: Error) => void,
  ): () => void {
    // WebSocket implementation would go here
    // For now, return a no-op unsubscribe function
    return () => {};
  }

  // Cache management
  clearCache(): void {
    this.cache.clear();
  }

  clearCacheByPattern(pattern: string): void {
    const regex = new RegExp(pattern);
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    }
  }

  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }
}

export const unifiedApiService = new UnifiedApiService();

// Convenience methods for common operations
export const api = {
  // Dashboard data
  getDashboardMetrics: () =>
    unifiedApiService.get("/dashboard/metrics", undefined, {
      cache: { enabled: true, ttl: 30000 }, // 30 seconds
    }),

  getSystemStatus: () =>
    unifiedApiService.get("/dashboard/status", undefined, {
      cache: { enabled: true, ttl: 10000 }, // 10 seconds
    }),

  // AI services
  getAIMetrics: () =>
    unifiedApiService.get("/ai/metrics", undefined, {
      cache: { enabled: true, ttl: 15000 }, // 15 seconds
    }),

  getAIModels: () =>
    unifiedApiService.get("/ai/models", undefined, {
      cache: { enabled: true, ttl: 60000 }, // 1 minute
    }),

  trainModel: (modelId: string, config: any) =>
    unifiedApiService.post(`/ai/models/${modelId}/train`, config),

  // User experience
  getUserMetrics: () =>
    unifiedApiService.get("/users/metrics", undefined, {
      cache: { enabled: true, ttl: 30000 }, // 30 seconds
    }),

  getUserFeedback: (filters?: any) =>
    unifiedApiService.get("/users/feedback", filters, {
      cache: { enabled: true, ttl: 60000 }, // 1 minute
    }),

  // Real-time data
  subscribeToMetrics: (onUpdate: (data: any) => void) =>
    unifiedApiService.subscribe("/metrics/stream", onUpdate),

  subscribeToAlerts: (onAlert: (alert: any) => void) =>
    unifiedApiService.subscribe("/alerts/stream", onAlert),
};

export default unifiedApiService;
