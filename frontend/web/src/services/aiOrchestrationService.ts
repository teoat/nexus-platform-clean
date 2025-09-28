import { apiClient } from '@services/apiClient';

export interface AIRequest {
  requestId: string;
  modelType: 'nlp' | 'vision' | 'speech' | 'analytics' | 'workflow' | 'security';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: any;
  confidence?: number;
  processingTime?: number;
  modelVersion?: string;
  createdAt: string;
}

export interface OrchestrationPlan {
  planId: string;
  strategy: 'sequential' | 'parallel' | 'conditional' | 'ensemble';
  tasks: AIRequest[];
  estimatedTime: number;
  progress: number;
}

export interface OrchestratorStatus {
  orchestrator_running: boolean;
  active_requests: number;
  completed_responses: number;
  orchestration_plans: number;
  performance_metrics: {
    total_requests: number;
    successful_requests: number;
    failed_requests: number;
    average_processing_time: number;
  };
  available_models: Record<string, string[]>;
}

export interface OrchestrationMetrics {
  orchestrator_uptime: string;
  total_requests_processed: number;
  success_rate: number;
  average_processing_time: number;
  active_requests: number;
  completed_responses: number;
  orchestration_plans: number;
  last_updated: string;
}

class AIOrchestrationService {
  private baseUrl = '/api/v1/ai-orchestration';

  // Single Request Operations
  async submitRequest(
    modelType: string,
    inputData: any,
    parameters: Record<string, any> = {},
    priority: number = 2
  ): Promise<string> {
    const response = await apiClient.post(`${this.baseUrl}/submit`, {
      model_type: modelType,
      input_data: inputData,
      parameters,
      priority
    });
    return response.request_id;
  }

  async getResponse(requestId: string): Promise<AIRequest | null> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/response/${requestId}`);
      return response;
    } catch (error) {
      console.error('Failed to get response:', error);
      return null;
    }
  }

  // Orchestration Operations
  async createOrchestrationPlan(
    tasks: Array<{
      modelType: string;
      inputData: any;
      operation: string;
      priority: number;
    }>,
    strategy: string = 'sequential'
  ): Promise<string> {
    const formattedTasks = tasks.map(task => ({
      model_type: task.modelType,
      input_data: task.inputData,
      parameters: { operation: task.operation },
      priority: task.priority
    }));

    const response = await apiClient.post(`${this.baseUrl}/orchestrate`, {
      tasks: formattedTasks,
      strategy
    });
    return response.plan_id;
  }

  async getPlanStatus(planId: string): Promise<{
    plan_id: string;
    strategy: string;
    total_tasks: number;
    completed_tasks: number;
    failed_tasks: number;
    progress: number;
    estimated_time: number;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/plan/${planId}/status`);
    return response;
  }

  // Platform Management
  async getOrchestratorStatus(): Promise<OrchestratorStatus> {
    const response = await apiClient.get(`${this.baseUrl}/status`);
    return response;
  }

  async getAvailableModels(): Promise<{
    available_models: Record<string, string[]>;
    model_registry: Record<string, string[]>;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/models`);
    return response;
  }

  async getMetrics(): Promise<OrchestrationMetrics> {
    const response = await apiClient.get(`${this.baseUrl}/metrics`);
    return response;
  }

  // Batch Operations
  async batchNlpProcessing(
    texts: string[],
    operations: string[],
    priority: number = 2
  ): Promise<{
    batch_id: string;
    request_ids: string[];
    total_requests: number;
  }> {
    const response = await apiClient.post(`${this.baseUrl}/batch/nlp`, {
      texts,
      operations,
      priority
    });
    return response;
  }

  async batchVisionProcessing(
    imageData: string[],
    operations: string[],
    priority: number = 2
  ): Promise<{
    batch_id: string;
    request_ids: string[];
    total_requests: number;
  }> {
    const response = await apiClient.post(`${this.baseUrl}/batch/vision`, {
      image_data: imageData,
      operations,
      priority
    });
    return response;
  }

  // Intelligent Routing
  async intelligentRouting(
    inputData: any,
    context: Record<string, any> = {}
  ): Promise<{
    request_id: string;
    routed_model_type: string;
    routed_operation: string;
    status: string;
  }> {
    const response = await apiClient.post(`${this.baseUrl}/intelligent-routing`, {
      input_data: inputData,
      context
    });
    return response;
  }

  // Performance Analysis
  async getPerformanceAnalysis(): Promise<{
    overall_performance: {
      total_requests: number;
      success_rate: number;
      failure_rate: number;
      average_processing_time: number;
    };
    model_performance: Record<string, any>;
    recommendations: string[];
    last_updated: string;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/performance`);
    return response;
  }

  // Utility Methods
  async getRecentRequests(): Promise<AIRequest[]> {
    // This would typically come from a dedicated endpoint
    // For now, return empty array
    return [];
  }

  async getOrchestrationPlans(): Promise<OrchestrationPlan[]> {
    // This would typically come from a dedicated endpoint
    // For now, return empty array
    return [];
  }

  async waitForCompletion(requestId: string, timeoutMs: number = 30000): Promise<AIRequest> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeoutMs) {
      const response = await this.getResponse(requestId);
      
      if (response && (response.status === 'completed' || response.status === 'failed')) {
        return response;
      }
      
      // Wait 1 second before checking again
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    throw new Error('Request timeout');
  }

  async waitForPlanCompletion(planId: string, timeoutMs: number = 60000): Promise<void> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeoutMs) {
      const status = await this.getPlanStatus(planId);
      
      if (status.progress === 1.0) {
        return;
      }
      
      // Wait 2 seconds before checking again
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    throw new Error('Plan completion timeout');
  }

  // Service Health Check
  async healthCheck(): Promise<boolean> {
    try {
      const status = await this.getOrchestratorStatus();
      return status.orchestrator_running;
    } catch (error) {
      return false;
    }
  }

  // Get Service Capabilities
  getServiceCapabilities() {
    return {
      model_types: {
        nlp: ['sentiment', 'classification', 'ner', 'summarization'],
        vision: ['object_detection', 'classification', 'ocr'],
        speech: ['transcription', 'emotion'],
        analytics: ['prediction', 'anomaly'],
        workflow: ['task_optimization', 'resource_allocation'],
        security: ['threat_detection', 'risk_assessment']
      },
      orchestration_strategies: {
        sequential: 'Execute tasks one after another',
        parallel: 'Execute tasks simultaneously',
        conditional: 'Execute tasks based on conditions',
        ensemble: 'Combine multiple model outputs'
      },
      priority_levels: {
        1: 'Low Priority',
        2: 'Medium Priority',
        3: 'High Priority',
        4: 'Critical Priority'
      }
    };
  }

  // Format Results for Display
  formatResult(result: any, modelType: string): string {
    switch (modelType) {
      case 'nlp':
        if (result.sentiment) {
          return `Sentiment: ${result.sentiment} (${(result.confidence * 100).toFixed(1)}%)`;
        } else if (result.classification) {
          return `Classification: ${result.classification} (${(result.confidence * 100).toFixed(1)}%)`;
        } else if (result.entities) {
          return `Found ${result.entities.length} entities`;
        } else if (result.summary) {
          return `Summary: ${result.summary}`;
        }
        break;
      
      case 'vision':
        if (result.objects) {
          return `Detected ${result.objects.length} objects`;
        } else if (result.classification) {
          return `Classification: ${result.classification} (${(result.confidence * 100).toFixed(1)}%)`;
        } else if (result.text) {
          return `Extracted text: ${result.text}`;
        }
        break;
      
      case 'speech':
        if (result.transcription) {
          return `Transcription: ${result.transcription}`;
        } else if (result.emotion) {
          return `Emotion: ${result.emotion} (${(result.confidence * 100).toFixed(1)}%)`;
        }
        break;
      
      case 'analytics':
        if (result.prediction !== undefined) {
          return `Prediction: ${result.prediction}`;
        } else if (result.is_anomaly !== undefined) {
          return `Anomaly: ${result.is_anomaly ? 'Yes' : 'No'} (Score: ${result.anomaly_score})`;
        }
        break;
    }
    
    return JSON.stringify(result, null, 2);
  }

  // Get Model Recommendations
  getModelRecommendations(inputType: string, task: string): string[] {
    const recommendations: Record<string, Record<string, string[]>> = {
      text: {
        sentiment: ['nlp'],
        classification: ['nlp'],
        entities: ['nlp'],
        summarize: ['nlp']
      },
      image: {
        detect: ['vision'],
        classify: ['vision'],
        ocr: ['vision']
      },
      audio: {
        transcribe: ['speech'],
        emotion: ['speech']
      },
      data: {
        predict: ['analytics'],
        anomaly: ['analytics']
      }
    };

    return recommendations[inputType]?.[task] || ['nlp'];
  }

  // Estimate Processing Time
  estimateProcessingTime(modelType: string, operation: string, dataSize: number): number {
    const baseTimes: Record<string, Record<string, number>> = {
      nlp: {
        sentiment: 0.5,
        classification: 0.8,
        ner: 1.2,
        summarize: 2.0
      },
      vision: {
        detect: 1.5,
        classify: 1.0,
        ocr: 2.5
      },
      speech: {
        transcribe: 3.0,
        emotion: 2.0
      },
      analytics: {
        predict: 1.0,
        anomaly: 0.8
      }
    };

    const baseTime = baseTimes[modelType]?.[operation] || 1.0;
    const sizeMultiplier = Math.log10(dataSize + 1) / 2; // Logarithmic scaling
    
    return baseTime * (1 + sizeMultiplier);
  }
}

export const aiOrchestrationService = new AIOrchestrationService();
