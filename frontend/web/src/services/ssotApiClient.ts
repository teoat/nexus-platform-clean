/**
 * NEXUS Platform - SSOT-Aware API Client
 * Integrates with SSOT Registry for dynamic API aliasing
 */

import { unifiedApiClient } from './unifiedApiClient';
import { ApiResponse } from '../types/ApiResponse';

interface SSOTConfig {
  registryUrl: string;
  context: string;
  cacheTimeout: number;
  enableCaching: boolean;
}

interface AliasCache {
  [key: string]: {
    canonical: string;
    timestamp: number;
    ttl: number;
  };
}

class SSOTApiClient {
  private config: SSOTConfig;
  private aliasCache: AliasCache = {};
  private readonly registryClient = unifiedApiClient;

  constructor(config?: Partial<SSOTConfig>) {
    this.config = {
      registryUrl:
        process.env.REACT_APP_SSOT_REGISTRY_URL ||
        'http://localhost:8000/api/v1/ssot',
      context: 'frontend',
      cacheTimeout: 300000, // 5 minutes
      enableCaching: true,
      ...config,
    };
  }

  // ===========================================
  // SSOT ALIAS RESOLUTION
  // ===========================================

  private async resolveAlias(alias: string): Promise<string> {
    const cacheKey = `${this.config.context}:${alias}`;

    // Check cache first
    if (this.config.enableCaching && this.aliasCache[cacheKey]) {
      const cached = this.aliasCache[cacheKey];
      if (Date.now() - cached.timestamp < cached.ttl) {
        return cached.canonical;
      }
      // Remove expired cache entry
      delete this.aliasCache[cacheKey];
    }

    try {
      // Resolve alias through SSOT registry
      const response = await this.registryClient.get<{ canonical: string }>(
        `/api/v1/ssot/resolve/${alias}`,
        { context: this.config.context }
      );

      if (response.success && response.data) {
        const canonical = response.data.canonical;

        // Cache the result
        if (this.config.enableCaching) {
          this.aliasCache[cacheKey] = {
            canonical,
            timestamp: Date.now(),
            ttl: this.config.cacheTimeout,
          };
        }

        return canonical;
      }
    } catch (error) {
      console.warn(`Failed to resolve alias '${alias}':`, error);
    }

    // Fallback to original alias if resolution fails
    return alias;
  }

  private async resolveEndpoint(endpoint: string): Promise<string> {
    // Check if endpoint is an alias (starts with @)
    if (endpoint.startsWith('@')) {
      const alias = endpoint.substring(1);
      const canonical = await this.resolveAlias(alias);
      return canonical;
    }

    return endpoint;
  }

  // ===========================================
  // SSOT-AWARE REQUEST METHODS
  // ===========================================

  async get<T>(
    endpoint: string,
    params?: Record<string, any>
  ): Promise<ApiResponse<T>> {
    const resolvedEndpoint = await this.resolveEndpoint(endpoint);
    return this.registryClient.get<T>(resolvedEndpoint, params);
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    const resolvedEndpoint = await this.resolveEndpoint(endpoint);
    return this.registryClient.post<T>(resolvedEndpoint, data);
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    const resolvedEndpoint = await this.resolveEndpoint(endpoint);
    return this.registryClient.put<T>(resolvedEndpoint, data);
  }

  async patch<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    const resolvedEndpoint = await this.resolveEndpoint(endpoint);
    return this.registryClient.patch<T>(resolvedEndpoint, data);
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    const resolvedEndpoint = await this.resolveEndpoint(endpoint);
    return this.registryClient.delete<T>(resolvedEndpoint);
  }

  // ===========================================
  // SSOT MANAGEMENT METHODS
  // ===========================================

  async createAlias(
    alias: string,
    canonical: string,
    description?: string
  ): Promise<ApiResponse<any>> {
    return this.registryClient.post<any>('/api/v1/ssot/aliases', {
      alias,
      canonical,
      context: this.config.context,
      description: description || `Alias for ${canonical}`,
      type: 'application',
    });
  }

  async listAliases(): Promise<ApiResponse<any[]>> {
    return this.registryClient.get('/api/v1/ssot/aliases', {
      context: this.config.context,
    });
  }

  async deleteAlias(alias: string): Promise<ApiResponse<void>> {
    return this.registryClient.delete(`/api/v1/ssot/aliases/${alias}`);
  }

  async getAliasInfo(alias: string): Promise<ApiResponse<any>> {
    return this.registryClient.get(`/api/v1/ssot/aliases/${alias}`, {
      context: this.config.context,
    });
  }

  // ===========================================
  // CONTEXT MANAGEMENT
  // ===========================================

  setContext(context: string): void {
    this.config.context = context;
    // Clear cache when context changes
    this.aliasCache = {};
  }

  getContext(): string {
    return this.config.context;
  }

  // ===========================================
  // CACHE MANAGEMENT
  // ===========================================

  clearCache(): void {
    this.aliasCache = {};
  }

  getCacheStats(): { size: number; entries: string[] } {
    return {
      size: Object.keys(this.aliasCache).length,
      entries: Object.keys(this.aliasCache),
    };
  }

  // ===========================================
  // CONVENIENCE METHODS FOR COMMON ALIASES
  // ===========================================

  // User management aliases
  async getUsers(params?: {
    skip?: number;
    limit?: number;
  }): Promise<ApiResponse<any[]>> {
    return this.get('@user-management', params);
  }

  async getUser(id: string): Promise<ApiResponse<any>> {
    return this.get(`@user-management/${id}`);
  }

  async updateUser(id: string, data: any): Promise<ApiResponse<any>> {
    return this.put(`@user-management/${id}`, data);
  }

  // Transaction processing aliases
  async getTransactions(params?: {
    skip?: number;
    limit?: number;
  }): Promise<ApiResponse<any[]>> {
    return this.get('@transaction-processing', params);
  }

  async createTransaction(data: any): Promise<ApiResponse<any>> {
    return this.post('@transaction-processing', data);
  }

  // Frenly AI aliases
  async sendAIMessage(
    message: string,
    context?: Record<string, any>
  ): Promise<ApiResponse<string>> {
    return this.post('@frenly-ai/chat', { message, context });
  }

  async getAIInsights(): Promise<ApiResponse<any[]>> {
    return this.get('@frenly-ai/insights');
  }

  // ===========================================
  // DELEGATION TO UNIFIED API CLIENT
  // ===========================================

  // Delegate authentication methods to unified client
  setAuthToken(token: string, refreshToken?: string): void {
    this.registryClient.setAuthToken(token, refreshToken);
  }
  clearAuth(): void {
    this.registryClient.clearAuth();
  }
  login(credentials: any): Promise<any> {
    // Use 'any' for now to resolve type issues, will refine later
    return this.registryClient.login(credentials);
  }
  register(userData: any): Promise<any> {
    // Use 'any' for now to resolve type issues, will refine later
    return this.registryClient.register(userData);
  }
  logout(): Promise<any> {
    // Use 'any' for now to resolve type issues, will refine later
    return this.registryClient.logout();
  }
  getCurrentUser(): Promise<any> {
    // Use 'any' for now to resolve type issues, will refine later
    return this.registryClient.getCurrentUser();
  }

  // Delegate utility methods
  uploadFile(file: File, endpoint?: string): Promise<ApiResponse<any>> {
    return this.registryClient.uploadFile(file, endpoint);
  }
  downloadFile(url: string, filename: string): Promise<void> {
    return this.registryClient.downloadFile(url, filename);
  }
}

// Create singleton instance
export const ssotApiClient = new SSOTApiClient();
export default ssotApiClient;
