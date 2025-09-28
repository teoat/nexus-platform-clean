/**
 * NEXUS Platform - Unified API Response Types
 * Single source of truth for API response types
 */

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  errors?: string[];
  meta?: {
    timestamp: string;
    requestId: string;
    version: string;
  };
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  success: boolean;
  message?: string;
  errors?: string[];
  meta?: {
    timestamp: string;
    requestId: string;
    version: string;
  };
}

export interface ApiError {
  type:
    | "validation"
    | "network"
    | "authentication"
    | "authorization"
    | "server"
    | "client"
    | "unknown";
  severity: "low" | "medium" | "high" | "critical";
  message: string;
  code?: string;
  details?: Record<string, any>;
  timestamp: string;
}
