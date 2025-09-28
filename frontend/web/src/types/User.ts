/**
 * NEXUS Platform - Unified User Interface
 * Single source of truth for User type across the application
 */

export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  role: "user" | "admin" | "moderator";
  created_at: string;
  updated_at?: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  full_name?: string;
  is_active?: boolean;
  role?: "user" | "admin" | "moderator";
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface LoginResponse {
  user: User;
  access_token: string;
  refresh_token: string;
}
