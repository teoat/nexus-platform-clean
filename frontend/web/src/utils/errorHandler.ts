/**
 * Error Handler Utility
 * Provides centralized error handling functionality
 */

import { ApiError } from '../types/api';

export enum ErrorType {
  API = "API_ERROR",
  NETWORK = "NETWORK_ERROR",
  VALIDATION = "VALIDATION_ERROR",
  AUTH = "AUTH_ERROR",
  UNKNOWN = "UNKNOWN_ERROR",
}

export enum ErrorSeverity {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
  CRITICAL = "CRITICAL",
}

export interface ErrorInfo {
  type: ErrorType;
  message: string;
  code?: string | number;
  details?: any;
  timestamp: number;
  severity?: ErrorSeverity;
}

export const handleError = (
  error: any,
  type: ErrorType = ErrorType.UNKNOWN,
): ErrorInfo => {
  const errorInfo: ErrorInfo = {
    type,
    message: error?.message || "An unknown error occurred",
    code: error?.code || error?.status,
    details: error,
    timestamp: Date.now(),
  };

  // Log error for debugging
  console.error("Error handled:", errorInfo);

  return errorInfo;
};

export const handleApiError = (error: any): ErrorInfo => {
  if (error?.response) {
    // Server responded with error status
    const apiError: ApiError = error.response.data || {};
    return handleError({
      ...error,
      message: apiError.message || error.message || 'API request failed',
      code: apiError.code || error.response.status,
      details: apiError.details || error.response.data,
    }, ErrorType.API);
  } else if (error?.request) {
    // Request was made but no response received
    return handleError({
      ...error,
      message: 'Network error - no response received',
      code: 'NETWORK_ERROR',
    }, ErrorType.NETWORK);
  } else {
    // Something else happened
    return handleError({
      ...error,
      message: error.message || 'An unexpected error occurred',
    }, ErrorType.UNKNOWN);
  }
};

export const isApiError = (error: any): boolean => {
  return error?.response !== undefined;
};

export const isNetworkError = (error: any): boolean => {
  return error?.request !== undefined && error?.response === undefined;
};
