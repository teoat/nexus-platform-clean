import { apiClient } from './apiClient';

export interface AIInsight {
  id: string;
  title: string;
  description: string;
  type: 'warning' | 'info' | 'success' | 'error';
  priority: 'low' | 'medium' | 'high';
  timestamp: string;
  source: string;
}

export interface AIConfiguration {
  autoLearning: boolean;
    learningRate: number;
    batchSize: number;
    maxModels: number;
    gpuEnabled: boolean;
    memoryLimit: number;
}

class AIService {
  private baseUrl = process.env.REACT_APP_AI_API_URL || 'http://localhost:8001';

  async getInsights(): Promise<AIInsight[]> {
    const response = await apiClient.get<AIInsight[]>(
      `${this.baseUrl}/ai/insights`
    );
    return response.data;
  }

  async updateAIConfig(config: Partial<AIConfiguration>): Promise<void> {
    await apiClient.put(`${this.baseUrl}/ai/configuration`, config);
  }

  async sendMessage(
    message: string,
    context?: Record<string, any>
  ): Promise<string> {
    const response = await apiClient.post<{ response: string }>(
      `${this.baseUrl}/ai/chat`,
      {
        message,
        context: context || {},
      }
    );
    return response.data.response;
  }

  async getMetrics(): Promise<any> {
    const response = await apiClient.get<any>(`${this.baseUrl}/ai/metrics`);
    return response.data;
  }

  async getModels(): Promise<any[]> {
    const response = await apiClient.get<any[]>(`${this.baseUrl}/ai/models`);
    return response.data;
  }

  async getConfiguration(): Promise<any> {
    const response = await apiClient.get<any>(
      `${this.baseUrl}/ai/configuration`
    );
    return response.data;
  }
}

export const aiService = new AIService();
export default aiService;
