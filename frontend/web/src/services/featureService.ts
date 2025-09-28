import { apiClient } from './apiClient';

export interface FeatureConfig {
  name: string;
  displayName: string;
  description: string;
  version: string;
  dependencies: string[];
  settings: Record<string, any>;
  permissions: string[];
}

export interface FeatureState {
  enabled: boolean;
  status: 'stopped' | 'starting' | 'running' | 'stopping' | 'error';
  config: FeatureConfig;
}

class FeatureService {
  async getAvailableFeatures() {
    const response = await apiClient.get('/api/v1/features/available');
    return response.data;
  }

  async getFeatureStates() {
    const response = await apiClient.get('/api/v1/features/states');
    return response.data;
  }

  async getFeatureConfig(featureName: string) {
    const response = await apiClient.get(`/api/v1/features/${featureName}/config`);
    return response.data;
  }

  async updateFeatureConfig(featureName: string, config: Partial<FeatureConfig>) {
    const response = await apiClient.put(`/api/v1/features/${featureName}/config`, config);
    return response.data;
  }

  async enableFeature(featureName: string) {
    const response = await apiClient.post(`/api/v1/features/${featureName}/enable`);
    return response.data;
  }

  async disableFeature(featureName: string) {
    const response = await apiClient.post(`/api/v1/features/${featureName}/disable`);
    return response.data;
  }

  async getFeatureMetrics(featureName: string) {
    const response = await apiClient.get(`/api/v1/features/${featureName}/metrics`);
    return response.data;
  }

  async validateFeatureConfig(featureName: string, config: Partial<FeatureConfig>) {
    const response = await apiClient.post(`/api/v1/features/${featureName}/validate`, config);
    return response.data;
  }
}

export const featureService = new FeatureService();