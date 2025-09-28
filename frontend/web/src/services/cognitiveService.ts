import { apiClient } from '@services/apiClient';

export interface CognitiveRequest {
  requestId: string;
  serviceType: 'nlp' | 'vision' | 'speech';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  result?: any;
  confidence?: number;
  processingTime?: number;
  createdAt: string;
}

export interface PlatformStatus {
  platform_running: boolean;
  total_requests: number;
  completed_requests: number;
  failed_requests: number;
  success_rate: number;
  services: {
    nlp: 'active' | 'inactive';
    vision: 'active' | 'inactive';
    speech: 'active' | 'inactive';
  };
}

export interface CognitiveMetrics {
  platform_uptime: string;
  total_requests_processed: number;
  success_rate: number;
  average_processing_time: number;
  services_status: {
    nlp: 'active' | 'inactive';
    vision: 'active' | 'inactive';
    speech: 'active' | 'inactive';
  };
  last_updated: string;
}

class CognitiveService {
  private baseUrl = '/api/v1/cognitive';

  // NLP Operations
  async analyzeSentiment(text: string): Promise<string> {
    const formData = new FormData();
    formData.append('text', text);
    
    const response = await apiClient.post(`${this.baseUrl}/nlp/sentiment`, formData);
    return response.request_id;
  }

  async classifyText(text: string, categories: string[]): Promise<string> {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('categories', JSON.stringify(categories));
    
    const response = await apiClient.post(`${this.baseUrl}/nlp/classify`, formData);
    return response.request_id;
  }

  async extractEntities(text: string): Promise<string> {
    const formData = new FormData();
    formData.append('text', text);
    
    const response = await apiClient.post(`${this.baseUrl}/nlp/entities`, formData);
    return response.request_id;
  }

  async summarizeText(text: string, maxLength: number = 150): Promise<string> {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('max_length', maxLength.toString());
    
    const response = await apiClient.post(`${this.baseUrl}/nlp/summarize`, formData);
    return response.request_id;
  }

  // Vision Operations
  async detectObjects(file: File): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(`${this.baseUrl}/vision/detect`, formData);
    return response.request_id;
  }

  async classifyImage(file: File): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(`${this.baseUrl}/vision/classify`, formData);
    return response.request_id;
  }

  async extractTextFromImage(file: File): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(`${this.baseUrl}/vision/ocr`, formData);
    return response.request_id;
  }

  // Speech Operations
  async transcribeAudio(file: File): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(`${this.baseUrl}/speech/transcribe`, formData);
    return response.request_id;
  }

  async analyzeAudioEmotion(file: File): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(`${this.baseUrl}/speech/emotion`, formData);
    return response.request_id;
  }

  // Response Management
  async getResponse(requestId: string): Promise<CognitiveRequest | null> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/response/${requestId}`);
      return response;
    } catch (error) {
      console.error('Failed to get response:', error);
      return null;
    }
  }

  // Platform Management
  async getPlatformStatus(): Promise<PlatformStatus> {
    const response = await apiClient.get(`${this.baseUrl}/status`);
    return response;
  }

  async getAvailableServices(): Promise<any> {
    const response = await apiClient.get(`${this.baseUrl}/services`);
    return response;
  }

  async getMetrics(): Promise<CognitiveMetrics> {
    const response = await apiClient.get(`${this.baseUrl}/metrics`);
    return response;
  }

  // Batch Operations
  async batchNlpProcessing(texts: string[], operations: string[]): Promise<any> {
    const formData = new FormData();
    formData.append('texts', JSON.stringify(texts));
    formData.append('operations', JSON.stringify(operations));
    
    const response = await apiClient.post(`${this.baseUrl}/batch/nlp`, formData);
    return response;
  }

  // Utility Methods
  async getRecentRequests(): Promise<CognitiveRequest[]> {
    // This would typically come from a dedicated endpoint
    // For now, return empty array
    return [];
  }

  async waitForCompletion(requestId: string, timeoutMs: number = 30000): Promise<CognitiveRequest> {
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

  // Service Health Check
  async healthCheck(): Promise<boolean> {
    try {
      const status = await this.getPlatformStatus();
      return status.platform_running;
    } catch (error) {
      return false;
    }
  }

  // Get Service Capabilities
  getServiceCapabilities() {
    return {
      nlp: {
        sentiment_analysis: 'Analyze text sentiment (positive, negative, neutral)',
        text_classification: 'Classify text into custom categories',
        entity_extraction: 'Extract named entities (people, places, organizations)',
        text_summarization: 'Summarize long text into shorter versions'
      },
      vision: {
        object_detection: 'Detect and identify objects in images',
        image_classification: 'Classify images into categories',
        ocr: 'Extract text from images using optical character recognition'
      },
      speech: {
        speech_recognition: 'Convert speech to text',
        emotion_analysis: 'Analyze emotional content in audio'
      }
    };
  }

  // Format Results for Display
  formatResult(result: any, serviceType: string): string {
    switch (serviceType) {
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
          return `Detected ${result.detection_count} objects`;
        } else if (result.classification) {
          return `Classification: ${result.classification} (${(result.confidence * 100).toFixed(1)}%)`;
        } else if (result.extracted_text) {
          return `Extracted text: ${result.extracted_text}`;
        }
        break;
      
      case 'speech':
        if (result.transcription) {
          return `Transcription: ${result.transcription}`;
        } else if (result.audio_features) {
          return `Audio analyzed - Duration: ${result.duration.toFixed(2)}s`;
        }
        break;
    }
    
    return JSON.stringify(result, null, 2);
  }
}

export const cognitiveService = new CognitiveService();
