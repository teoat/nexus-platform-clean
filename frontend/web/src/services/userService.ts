/**
 * User Service API Client
 * Handles user management, authentication, and authorization
 */

import { apiClient } from "./apiClient";

export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: "admin" | "manager" | "analyst" | "viewer";
  status: "active" | "inactive" | "suspended" | "pending";
  is_email_verified: boolean;
  is_2fa_enabled: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role?: "admin" | "manager" | "analyst" | "viewer";
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

export class UserService {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>("/api/v1/auth/login", {
      username: credentials.username,
      password: credentials.password,
    });
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<User> {
    const response = await apiClient.post<User>("/api/v1/auth/register", {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      full_name: `${userData.first_name} ${userData.last_name}`,
    });
    return response.data;
  }

  async logout(): Promise<void> {
    await apiClient.post("/api/v1/auth/logout", {});
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>("/api/v1/auth/me");
    return response.data;
  }

  async updateCurrentUser(userData: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>(
      "/api/v1/users/profile",
      userData,
    );
    return response.data;
  }

  async changePassword(passwordData: PasswordChangeRequest): Promise<void> {
    await apiClient.post<void>("/api/v1/users/change-password", passwordData);
  }

  async getUsers(skip = 0, limit = 100): Promise<User[]> {
    const response = await apiClient.get<User[]>("/api/v1/users", {
      params: { skip, limit },
    });
    return response.data;
  }

  async getUserById(userId: string): Promise<User> {
    const response = await apiClient.get<User>(`/api/v1/users/${userId}`);
    return response.data;
  }

  async updateUser(userId: string, userData: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>(
      `/api/v1/users/${userId}`,
      userData,
    );
    return response.data;
  }

  async deleteUser(userId: string): Promise<void> {
    await apiClient.delete(`/api/v1/users/${userId}`);
  }

  async checkHealth(): Promise<{ status: string; service: string }> {
    const response = await apiClient.get<{ status: string; service: string }>(
      "/health",
    );
    return response.data;
  }
}

export const userService = new UserService();
