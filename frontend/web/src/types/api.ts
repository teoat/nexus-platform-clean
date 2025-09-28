/**
 * API Response Types
 * Centralized type definitions for API responses
 */

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
  success: boolean;
  timestamp: string;
}

export interface ApiError {
  message: string;
  code?: string | number;
  details?: any;
  status?: number;
  timestamp?: string;
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
}

export interface SearchApiResponse {
  results: any[];
  stats: {
    totalResults: number;
    searchTime: number;
    facets: {
      types: { [key: string]: number };
      categories: { [key: string]: number };
      tags: { [key: string]: number };
      accounts: { [key: string]: number };
      users: { [key: string]: number };
    };
  };
}

export interface AuthApiResponse {
  user: {
    id: string;
    email: string;
    username: string;
    firstName?: string;
    lastName?: string;
    isActive: boolean;
    isVerified: boolean;
    roles: string[];
  };
  token: string;
  refreshToken: string;
  expiresIn: number;
}

export interface TransactionApiResponse {
  id: string;
  amount: number;
  description: string;
  category: string;
  accountId: string;
  userId: string;
  date: string;
  type: 'income' | 'expense' | 'transfer';
  tags?: string[];
  metadata?: any;
  createdAt: string;
  updatedAt: string;
}

export interface AccountApiResponse {
  id: string;
  name: string;
  type: 'checking' | 'savings' | 'credit' | 'investment' | 'loan';
  balance: number;
  currency: string;
  userId: string;
  isActive: boolean;
  metadata?: any;
  createdAt: string;
  updatedAt: string;
}

export interface UserApiResponse {
  id: string;
  email: string;
  username: string;
  firstName?: string;
  lastName?: string;
  isActive: boolean;
  isVerified: boolean;
  roles: string[];
  createdAt: string;
  updatedAt: string;
  lastLogin?: string;
}

export interface FileApiResponse {
  id: string;
  filename: string;
  originalName: string;
  mimeType: string;
  size: number;
  path: string;
  userId: string;
  metadata?: any;
  createdAt: string;
  updatedAt: string;
}

export interface NotificationApiResponse {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  userId: string;
  isRead: boolean;
  metadata?: any;
  createdAt: string;
  updatedAt: string;
}

export interface AnalyticsApiResponse {
  period: string;
  metrics: {
    totalTransactions: number;
    totalIncome: number;
    totalExpenses: number;
    netIncome: number;
    averageTransaction: number;
    topCategories: { category: string; amount: number; count: number }[];
    monthlyTrends: { month: string; income: number; expenses: number }[];
  };
}

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  services: {
    database: 'up' | 'down';
    redis: 'up' | 'down';
    storage: 'up' | 'down';
  };
  version: string;
  uptime: number;
}
