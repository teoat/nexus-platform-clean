/**
 * NEXUS Platform - SSOT Hook
 * React hook for SSOT-aware API operations
 */

import { useState, useEffect, useCallback } from 'react';
import { ssotApiClient } from '../services/ssotApiClient';
import { ApiResponse } from '../types/ApiResponse';

interface SSOTState {
  context: string;
  aliases: any[];
  cacheStats: { size: number; entries: string[] };
  isLoading: boolean;
  error: string | null;
}

interface UseSSOTReturn extends SSOTState {
  // Context management
  setContext: (context: string) => void;

  // Alias management
  createAlias: (
    alias: string,
    canonical: string,
    description?: string
  ) => Promise<ApiResponse<any>>;
  deleteAlias: (alias: string) => Promise<ApiResponse<void>>;
  refreshAliases: () => Promise<void>;

  // Cache management
  clearCache: () => void;

  // SSOT-aware API calls
  get: <T>(
    endpoint: string,
    params?: Record<string, any>
  ) => Promise<ApiResponse<T>>;
  post: <T>(endpoint: string, data?: any) => Promise<ApiResponse<T>>;
  put: <T>(endpoint: string, data?: any) => Promise<ApiResponse<T>>;
  patch: <T>(endpoint: string, data?: any) => Promise<ApiResponse<T>>;
  delete: <T>(endpoint: string) => Promise<ApiResponse<T>>;
}

export const useSSOT = (initialContext: string = 'frontend'): UseSSOTReturn => {
  const [state, setState] = useState<SSOTState>({
    context: initialContext,
    aliases: [],
    cacheStats: { size: 0, entries: [] },
    isLoading: false,
    error: null,
  });

  // Initialize context
  useEffect(() => {
    ssotApiClient.setContext(initialContext);
  }, [initialContext]);

  // Load aliases on mount and context change
  const refreshAliases = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await ssotApiClient.listAliases();
      if (response.success) {
        setState(prev => ({
          ...prev,
          aliases: response.data || [],
          isLoading: false,
        }));
      } else {
        setState(prev => ({
          ...prev,
          error: response.message || 'Failed to load aliases',
          isLoading: false,
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Unknown error',
        isLoading: false,
      }));
    }
  }, []);

  // Update cache stats
  const updateCacheStats = useCallback(() => {
    const cacheStats = ssotApiClient.getCacheStats();
    setState(prev => ({ ...prev, cacheStats }));
  }, []);

  // Context management
  const setContext = useCallback(
    (context: string) => {
      ssotApiClient.setContext(context);
      setState(prev => ({ ...prev, context }));
      refreshAliases();
    },
    [refreshAliases]
  );

  // Alias management
  const createAlias = useCallback(
    async (
      alias: string,
      canonical: string,
      description?: string
    ): Promise<ApiResponse<any>> => {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await ssotApiClient.createAlias(
          alias,
          canonical,
          description
        );
        if (response.success) {
          await refreshAliases();
          updateCacheStats();
        }
        setState(prev => ({ ...prev, isLoading: false }));
        return response;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Unknown error';
        setState(prev => ({
          ...prev,
          error: errorMessage,
          isLoading: false,
        }));
        throw error;
      }
    },
    [refreshAliases, updateCacheStats]
  );

  const deleteAlias = useCallback(
    async (alias: string): Promise<ApiResponse<void>> => {
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await ssotApiClient.deleteAlias(alias);
        if (response.success) {
          await refreshAliases();
          updateCacheStats();
        }
        setState(prev => ({ ...prev, isLoading: false }));
        return response;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Unknown error';
        setState(prev => ({
          ...prev,
          error: errorMessage,
          isLoading: false,
        }));
        throw error;
      }
    },
    [refreshAliases, updateCacheStats]
  );

  // Cache management
  const clearCache = useCallback(() => {
    ssotApiClient.clearCache();
    updateCacheStats();
  }, [updateCacheStats]);

  // SSOT-aware API methods
  const get = useCallback(
    async <T>(
      endpoint: string,
      params?: Record<string, any>
    ): Promise<ApiResponse<T>> => {
      try {
        const response = await ssotApiClient.get<T>(endpoint, params);
        updateCacheStats();
        return response;
      } catch (error) {
        setState(prev => ({
          ...prev,
          error: error instanceof Error ? error.message : 'API call failed',
        }));
        throw error;
      }
    },
    [updateCacheStats]
  );

  const post = useCallback(
    async <T>(endpoint: string, data?: any): Promise<ApiResponse<T>> => {
      try {
        const response = await ssotApiClient.post<T>(endpoint, data);
        updateCacheStats();
        return response;
      } catch (error) {
        setState(prev => ({
          ...prev,
          error: error instanceof Error ? error.message : 'API call failed',
        }));
        throw error;
      }
    },
    [updateCacheStats]
  );

  const put = useCallback(
    async <T>(endpoint: string, data?: any): Promise<ApiResponse<T>> => {
      try {
        const response = await ssotApiClient.put<T>(endpoint, data);
        updateCacheStats();
        return response;
      } catch (error) {
        setState(prev => ({
          ...prev,
          error: error instanceof Error ? error.message : 'API call failed',
        }));
        throw error;
      }
    },
    [updateCacheStats]
  );

  const patch = useCallback(
    async <T>(endpoint: string, data?: any): Promise<ApiResponse<T>> => {
      try {
        const response = await ssotApiClient.patch<T>(endpoint, data);
        updateCacheStats();
        return response;
      } catch (error) {
        setState(prev => ({
          ...prev,
          error: error instanceof Error ? error.message : 'API call failed',
        }));
        throw error;
      }
    },
    [updateCacheStats]
  );

  const deleteMethod = useCallback(
    async <T>(endpoint: string): Promise<ApiResponse<T>> => {
      try {
        const response = await ssotApiClient.delete<T>(endpoint);
        updateCacheStats();
        return response;
      } catch (error) {
        setState(prev => ({
          ...prev,
          error: error instanceof Error ? error.message : 'API call failed',
        }));
        throw error;
      }
    },
    [updateCacheStats]
  );

  // Load initial data
  useEffect(() => {
    refreshAliases();
    updateCacheStats();
  }, [refreshAliases, updateCacheStats]);

  return {
    ...state,
    setContext,
    createAlias,
    deleteAlias,
    refreshAliases,
    clearCache,
    get,
    post,
    put,
    patch,
    delete: deleteMethod,
  };
};

export default useSSOT;
