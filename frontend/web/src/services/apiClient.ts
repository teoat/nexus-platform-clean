/**
 * NEXUS Platform - Enhanced ApiClient
 * Complete API client with all required methods
 */

import { ApiResponse, PaginatedResponse, ApiError } from '../types/ApiResponse';

export class ApiClient {
  private baseURL: string;
  private timeout: number;
  private retries: number;

  constructor(
    baseURL: string = process.env.REACT_APP_API_URL || 'http://localhost:8000'
  ) {
    this.baseURL = baseURL;
    this.timeout = 30000;
    this.retries = 3;
  }

  async get<T>(
    endpoint: string,
    params?: Record<string, any>
  ): Promise<ApiResponse<T>> {
    const query = params
      ? `?${new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))}`
      : '';
    return this.request<T>(`${endpoint}${query}`);
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }

  async uploadFile<T>(
    endpoint: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);

    // Note: 'fetch' does not support progress events out of the box.
    // A more advanced implementation would use XMLHttpRequest.
    // For simplicity, we are not implementing the onProgress callback here.

    return this.request<T>(endpoint, {
      method: 'POST',
      body: formData,
      headers: {
        // Content-Type is automatically set by the browser when using FormData
      },
    });
  }

  // Core HTTP methods
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        data,
        success: true,
        meta: {
          timestamp: new Date().toISOString(),
          requestId: response.headers.get('X-Request-ID') || 'unknown',
          version: '1.0.0',
        },
      };
    } catch (error) {
      return {
        data: null as T,
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
        errors: [error instanceof Error ? error.message : 'Unknown error'],
        meta: {
          timestamp: new Date().toISOString(),
          requestId: 'unknown',
          version: '1.0.0',
        },
      };
    }
  }

  private async paginatedRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<PaginatedResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        data: data.data,
        pagination: data.pagination,
        success: true,
        meta: {
          timestamp: new Date().toISOString(),
          requestId: response.headers.get('X-Request-ID') || 'unknown',
          version: '1.0.0',
        },
      };
    } catch (error) {
      return {
        data: [],
        pagination: {
          page: 0,
          limit: 0,
          total: 0,
          totalPages: 0,
          hasNext: false,
          hasPrev: false,
        },
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
        errors: [error instanceof Error ? error.message : 'Unknown error'],
        meta: {
          timestamp: new Date().toISOString(),
          requestId: 'unknown',
          version: '1.0.0',
        },
      };
    }
  }

  // Auth methods
  async login(credentials: {
    email: string;
    password: string;
  }): Promise<
    ApiResponse<{ access_token: string; refresh_token: string; user: any }>
  > {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async register(userData: {
    email: string;
    password: string;
    full_name: string;
  }): Promise<
    ApiResponse<{ access_token: string; refresh_token: string; user: any }>
  > {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async logout(): Promise<ApiResponse<void>> {
    return this.request('/api/auth/logout', {
      method: 'POST',
    });
  }

  async refreshToken(): Promise<
    ApiResponse<{ access_token: string; refresh_token: string }>
  > {
    return this.request('/api/auth/refresh', {
      method: 'POST',
    });
  }

  // User methods
  async getProfile(): Promise<ApiResponse<any>> {
    return this.request('/api/users/profile');
  }

  async getUser(id: string): Promise<ApiResponse<any>> {
    return this.request(`/api/users/${id}`);
  }

  async updateProfile(data: any): Promise<ApiResponse<any>> {
    return this.request('/api/users/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async updateUser(id: string, data: any): Promise<ApiResponse<any>> {
    return this.request(`/api/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async getUsers(params?: {
    skip?: number;
    limit?: number;
  }): Promise<ApiResponse<any[]>> {
    const query = params
      ? `?${new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))}`
      : '';
    return this.request(`/api/users${query}`);
  }

  async changePassword(data: {
    current_password: string;
    new_password: string;
  }): Promise<ApiResponse<void>> {
    return this.request('/api/users/password', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Account methods
  async getAccounts(): Promise<ApiResponse<any[]>> {
    return this.request('/api/accounts');
  }

  async getAccount(id: string): Promise<ApiResponse<any>> {
    return this.request(`/api/accounts/${id}`);
  }

  async createAccount(data: any): Promise<ApiResponse<any>> {
    return this.request('/api/accounts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAccount(id: string, data: any): Promise<ApiResponse<any>> {
    return this.request(`/api/accounts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteAccount(id: string): Promise<ApiResponse<void>> {
    return this.request(`/api/accounts/${id}`, {
      method: 'DELETE',
    });
  }

  // Transaction methods
  async getTransactions(params?: any): Promise<PaginatedResponse<any>> {
    const query = params
      ? `?${new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))}`
      : '';
    return this.paginatedRequest(`/api/transactions${query}`);
  }

  async getTransaction(id: string): Promise<ApiResponse<any>> {
    return this.request(`/api/transactions/${id}`);
  }

  async createTransaction(data: any): Promise<ApiResponse<any>> {
    return this.request('/api/transactions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTransaction(id: string, data: any): Promise<ApiResponse<any>> {
    return this.request(`/api/transactions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteTransaction(id: string): Promise<ApiResponse<void>> {
    return this.request(`/api/transactions/${id}`, {
      method: 'DELETE',
    });
  }

  // Analytics methods
  async getAnalytics(): Promise<ApiResponse<any>> {
    return this.request('/api/analytics');
  }

  async getDashboardData(): Promise<ApiResponse<any>> {
    return this.request('/api/analytics/dashboard');
  }

  // Monitoring methods
  async getMonitoringMetrics(): Promise<any> {
    const response = await this.request('/api/monitoring/metrics');
    return response.data;
  }

  async getAlerts(): Promise<any[]> {
    const response = await this.request<any[]>('/api/monitoring/alerts');
    return response.data;
  }

  async getPerformanceMetrics(): Promise<any> {
    const response = await this.request('/api/monitoring/performance');
    return response.data;
  }

  async getMonitoringInsights(): Promise<any[]> {
    const response = await this.request<any[]>('/api/monitoring/insights');
    return response.data;
  }

  async acknowledgeAlert(alertId: string): Promise<ApiResponse<void>> {
    return this.post(`/api/monitoring/alerts/${alertId}/acknowledge`, {});
  }

  // Feature management methods
  async loadFeature(featureId: string): Promise<any> {
    const response = await this.request(`/api/features/${featureId}/load`, {
      method: 'POST',
    });
    return response.data;
  }

  async unloadFeature(featureId: string): Promise<void> {
    await this.request(`/api/features/${featureId}/unload`, {
      method: 'POST',
    });
  }

  async getFeatureStatus(featureId: string): Promise<any> {
    const response = await this.request(`/api/features/${featureId}/status`);
    return response.data;
  }

  async listFeatures(): Promise<ApiResponse<any[]>> {
    return this.request('/api/features');
  }

  // Health check methods
  async healthCheck(): Promise<
    ApiResponse<{ status: string; service: string }>
  > {
    return this.request('/api/health');
  }

  async getServiceHealth(): Promise<
    ApiResponse<{ status: string; service: string }>
  > {
    return this.request('/api/health/service');
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
export default apiClient;
