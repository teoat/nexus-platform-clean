/**
 * NEXUS Platform - Unified AI Interface
 * Single source of truth for AI types across the application
 */

export interface AIMessage {
  id: string;
  content: string;
  role: "user" | "assistant" | "system";
  timestamp: string;
  context?: Record<string, any>;
}

export interface AIInsights {
  id: string;
  type:
    | "spending_pattern"
    | "risk_assessment"
    | "budget_recommendation"
    | "anomaly_detection";
  title: string;
  description: string;
  confidence: number;
  data: Record<string, any>;
  recommendations?: string[];
  timestamp: string;
}

export interface AIMetrics {
  total_messages: number;
  average_response_time: number;
  success_rate: number;
  error_rate: number;
  popular_topics: Array<{
    topic: string;
    count: number;
  }>;
  timestamp: string;
}

export interface AIConfiguration {
  enabled: boolean;
  model: string;
  temperature: number;
  max_tokens: number;
  context_window: number;
  features: {
    spending_analysis: boolean;
    risk_assessment: boolean;
    budget_planning: boolean;
    anomaly_detection: boolean;
  };
}

export interface AIContext {
  user_id: string;
  session_id: string;
  conversation_history: AIMessage[];
  user_profile: {
    risk_tolerance: "low" | "medium" | "high";
    spending_habits: Record<string, any>;
    financial_goals: string[];
  };
  current_context: Record<string, any>;
}
