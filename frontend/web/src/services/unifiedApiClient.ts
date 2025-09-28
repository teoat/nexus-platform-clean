/**
 * NEXUS Platform - Unified API Client
 * Supreme AI Agent - Autonomous Evolution
 * Single source of truth for all API communications
 */

import { ApiResponse, PaginatedResponse, ApiError } from '../types/ApiResponse';
import {
  User,
  UserCreate,
  UserUpdate,
  LoginCredentials,
  RegisterData,
  LoginResponse,
} from '../types/User';
import { Account, AccountCreate, AccountUpdate } from '../types/Account';
import {
  Transaction,
  TransactionCreate,
  TransactionUpdate,
} from '../types/Transaction';
import {
  AnalyticsData,
  DashboardData,
  HealthStatus,
  MetricsData,
  AlertData,
  PerformanceMetrics,
  MonitoringInsights,
} from '../types/Analytics';
import { AIMessage, AIInsights, AIMetrics, AIConfiguration } from '../types/AI';

interface ApiConfig {
  baseURL: string;
  timeout: number;
  retries: number;
  retryDelay: number;
}

interface RequestOptions {
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retries?: number;
}

class UnifiedApiClient {
  private config: ApiConfig;
  private authToken: string | null = null;
  private refreshToken: string | null = null;
  private isRefreshing: boolean = false;
  private refreshPromise: Promise<string> | null = null;

  constructor(config?: Partial<ApiConfig>) {
    this.config = {
      baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      timeout: 30000,
      retries: 3,
      retryDelay: 1000,
      ...config,
    };
  }

  // ===========================================
  // AUTHENTICATION METHODS
  // ===========================================

  setAuthToken(token: string, refreshToken?: string): void {
    this.authToken = token;
    this.refreshToken = refreshToken || null;
  }

  clearAuth(): void {
    this.authToken = null;
    this.refreshToken = null;
  }

  private async refreshAuthToken(): Promise<string> {
    if (this.isRefreshing && this.refreshPromise) {
      return this.refreshPromise;
    }

    this.isRefreshing = true;
    this.refreshPromise = this.performTokenRefresh();

    try {
      const newToken = await this.refreshPromise;
      this.authToken = newToken;
      return newToken;
    } finally {
      this.isRefreshing = false;
      this.refreshPromise = null;
    }
  }

  private async performTokenRefresh(): Promise<string> {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch(`${this.config.baseURL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: this.refreshToken }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    return data.access_token;
  }

  // ===========================================
  // CORE REQUEST METHODS
  // ===========================================

  private async request<T>(
    endpoint: string,
    options: RequestOptions = { method: 'GET' }
  ): Promise<ApiResponse<T>> {
    const url = `${this.config.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.authToken) {
      headers.Authorization = `Bearer ${this.authToken}`;
    }

    const requestOptions: RequestInit = {
      method: options.method,
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    };

    let lastError: Error | null = null;
    const maxRetries = options.retries ?? this.config.retries;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(
          () => controller.abort(),
          options.timeout ?? this.config.timeout
        );

        const response = await fetch(url, {
          ...requestOptions,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // Handle token refresh for 401 errors
        if (response.status === 401 && this.refreshToken && attempt === 0) {
          try {
            await this.refreshAuthToken();
            headers.Authorization = `Bearer ${this.authToken}`;
            continue;
          } catch (refreshError) {
            this.clearAuth();
            throw new Error('Authentication failed');
          }
        }

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || `HTTP ${response.status}`);
        }

        return {
          data: data.data || data,
          success: true,
          message: data.message,
          meta: data.meta,
        };
      } catch (error) {
        lastError = error as Error;

        if (attempt < maxRetries) {
          const delay = this.config.retryDelay * Math.pow(2, attempt);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError || new Error('Request failed');
  }

  // ===========================================
  // HTTP METHODS
  // ===========================================

  async get<T>(
    endpoint: string,
    params?: Record<string, any>
  ): Promise<ApiResponse<T>> {
    const query = params
      ? `?${new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))}`
      : '';
    return this.request<T>(`${endpoint}${query}`, { method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data,
    });
  }

  async patch<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data,
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // ===========================================
  // AUTHENTICATION ENDPOINTS
  // ===========================================

  async login(
    credentials: LoginCredentials
  ): Promise<ApiResponse<LoginResponse>> {
    const response = await this.post<LoginResponse>(
      '/api/v1/auth/login',
      credentials
    );
    if (response.success && response.data) {
      this.setAuthToken(
        response.data?.access_token,
        response.data?.refresh_token
      );
    }
    return response;
  }

  async register(userData: RegisterData): Promise<ApiResponse<LoginResponse>> {
    const response = await this.post<LoginResponse>(
      '/api/v1/auth/register',
      userData
    );
    if (response.success && response.data) {
      this.setAuthToken(
        response.data?.access_token,
        response.data?.refresh_token
      );
    }
    return response;
  }

  async logout(): Promise<ApiResponse<void>> {
    const response = await this.post<void>('/api/v1/auth/logout');
    this.clearAuth();
    return response;
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.get('/api/v1/auth/me');
  }

  // ===========================================
  // USER MANAGEMENT ENDPOINTS
  // ===========================================

  async getUsers(params?: {
    skip?: number;
    limit?: number;
  }): Promise<PaginatedResponse<User>> {
    const response = await this.get<User[]>('/api/v1/users', params);
    return {
      data: response.data || [],
      pagination: {
        page: 1,
        limit: params?.limit || 10,
        total: response.data?.length || 0,
        totalPages: Math.ceil(
          (response.data?.length || 0) / (params?.limit || 10)
        ),
        hasNext: false,
        hasPrev: false,
      },
      success: response.success,
      message: response.message,
    };
  }

  async getUser(id: string): Promise<ApiResponse<User>> {
    return this.get(`/api/v1/users/${id}`);
  }

  async updateUser(id: string, data: UserUpdate): Promise<ApiResponse<User>> {
    return this.put(`/api/v1/users/${id}`, data);
  }

  async deleteUser(id: string): Promise<ApiResponse<void>> {
    return this.delete(`/api/v1/users/${id}`);
  }

  // ===========================================
  // ACCOUNT MANAGEMENT ENDPOINTS
  // ===========================================

  async getAccounts(): Promise<ApiResponse<Account[]>> {
    return this.get('/api/v1/accounts');
  }

  async getAccount(id: string): Promise<ApiResponse<Account>> {
    return this.get(`/api/v1/accounts/${id}`);
  }

  async createAccount(data: AccountCreate): Promise<ApiResponse<Account>> {
    return this.post('/api/v1/accounts', data);
  }

  async updateAccount(
    id: string,
    data: AccountUpdate
  ): Promise<ApiResponse<Account>> {
    return this.put(`/api/v1/accounts/${id}`, data);
  }

  async deleteAccount(id: string): Promise<ApiResponse<void>> {
    return this.delete(`/api/v1/accounts/${id}`);
  }

  // ===========================================
  // TRANSACTION ENDPOINTS
  // ===========================================

  async getTransactions(params?: {
    skip?: number;
    limit?: number;
  }): Promise<PaginatedResponse<Transaction>> {
    const response = await this.get<Transaction[]>(
      '/api/v1/transactions',
      params
    );
    return {
      data: response.data || [],
      pagination: {
        page: 1,
        limit: params?.limit || 10,
        total: response.data?.length || 0,
        totalPages: Math.ceil(
          (response.data?.length || 0) / (params?.limit || 10)
        ),
        hasNext: false,
        hasPrev: false,
      },
      success: response.success,
      message: response.message,
    };
  }

  async getTransaction(id: string): Promise<ApiResponse<Transaction>> {
    return this.get(`/api/v1/transactions/${id}`);
  }

  async createTransaction(
    data: TransactionCreate
  ): Promise<ApiResponse<Transaction>> {
    return this.post('/api/v1/transactions', data);
  }

  async updateTransaction(
    id: string,
    data: TransactionUpdate
  ): Promise<ApiResponse<Transaction>> {
    return this.put(`/api/v1/transactions/${id}`, data);
  }

  async deleteTransaction(id: string): Promise<ApiResponse<void>> {
    return this.delete(`/api/v1/transactions/${id}`);
  }

  // ===========================================
  // ANALYTICS ENDPOINTS
  // ===========================================

  async getAnalytics(params?: {
    period?: string;
    type?: string;
  }): Promise<ApiResponse<AnalyticsData>> {
    return this.get('/api/v1/analytics', params);
  }

  async getDashboardData(): Promise<ApiResponse<DashboardData>> {
    return this.get('/api/v1/analytics/dashboard');
  }

  // ===========================================
  // MONITORING ENDPOINTS
  // ===========================================

  async getHealth(): Promise<ApiResponse<HealthStatus>> {
    return this.get('/health');
  }

  async getMetrics(): Promise<ApiResponse<MetricsData>> {
    return this.get('/api/v1/monitoring/metrics');
  }

  async getAlerts(): Promise<ApiResponse<AlertData[]>> {
    return this.get('/api/v1/monitoring/alerts');
  }

  async getPerformanceMetrics(): Promise<ApiResponse<PerformanceMetrics>> {
    return this.get('/api/v1/monitoring/performance');
  }

  async getMonitoringInsights(): Promise<ApiResponse<MonitoringInsights[]>> {
    return this.get('/api/v1/monitoring/insights');
  }

  // ===========================================
  // AI ENDPOINTS
  // ===========================================

  async sendAIMessage(
    message: string,
    context?: Record<string, any>
  ): Promise<ApiResponse<string>> {
    return this.post('/api/v1/ai/chat', { message, context });
  }

  async getAIInsights(): Promise<ApiResponse<AIInsights[]>> {
    return this.get('/api/v1/ai/insights');
  }

  async getAIMetrics(): Promise<ApiResponse<AIMetrics>> {
    return this.get('/api/v1/ai/metrics');
  }

  async getAIConfiguration(): Promise<ApiResponse<AIConfiguration>> {
    return this.get('/api/v1/ai/configuration');
  }

  async updateAIConfiguration(
    config: AIConfiguration
  ): Promise<ApiResponse<void>> {
    return this.put('/api/v1/ai/configuration', config);
  }

  // ===========================================
  // UTILITY METHODS
  // ===========================================

  async uploadFile(
    file: File,
    endpoint: string = '/api/v1/files/upload'
  ): Promise<ApiResponse<any>> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.config.baseURL}${endpoint}`, {
      method: 'POST',
      headers: {
        Authorization: this.authToken ? `Bearer ${this.authToken}` : '',
      },
      body: formData,
    });

    const data = await response.json();
    return {
      data: data.data || data,
      success: response.ok,
      message: data.message,
    };
  }

  async downloadFile(url: string, filename: string): Promise<void> {
    const response = await fetch(url, {
      headers: {
        Authorization: this.authToken ? `Bearer ${this.authToken}` : '',
      },
    });

    if (!response.ok) {
      throw new Error('Download failed');
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }
}

// Create singleton instance
export const unifiedApiClient = new UnifiedApiClient();
export default unifiedApiClient;
