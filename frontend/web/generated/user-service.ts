import { apiClient } from "../services/apiClient";
export interface User {
  id: string;
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  role: "admin" | "user" | "manager";
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}
export interface CreateUserRequest {
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  password: string;
  role?: "admin" | "user" | "manager";
}
export interface UpdateUserRequest {
  email?: string;
  username?: string;
  firstName?: string;
  lastName?: string;
  role?: "admin" | "user" | "manager";
  isActive?: boolean;
}
export interface UsersResponse {
  users: User[];
  total: number;
  page: number;
  limit: number;
}
export class UserServiceClient {
  async getUsers(params?: {
    page?: number;
    limit?: number;
    search?: string;
  }): Promise<UsersResponse> {
    return apiClient.get("/api/v1/users", {
      params,
    }) as unknown as Promise<UsersResponse>;
  }
  async getUser(id: string): Promise<User> {
    return apiClient.get(`/api/v1/users/${id}`) as unknown as Promise<User>;
  }
  async createUser(userData: CreateUserRequest): Promise<User> {
    return apiClient.post(
      "/api/v1/users",
      userData,
    ) as unknown as Promise<User>;
  }
  async updateUser(id: string, userData: UpdateUserRequest): Promise<User> {
    return apiClient.put(
      `/api/v1/users/${id}`,
      userData,
    ) as unknown as Promise<User>;
  }
  async deleteUser(id: string): Promise<void> {
    return apiClient.delete(`/api/v1/users/${id}`) as unknown as Promise<void>;
  }
  async getCurrentUser(): Promise<User> {
    return apiClient.get("/api/v1/auth/me") as unknown as Promise<User>;
  }
  async updateProfile(userData: Partial<UpdateUserRequest>): Promise<User> {
    return apiClient.put(
      "/api/v1/users/profile",
      userData,
    ) as unknown as Promise<User>;
  }
  async changePassword(
    currentPassword: string,
    newPassword: string,
  ): Promise<void> {
    return apiClient.post("/api/v1/users/change-password", {
      currentPassword,
      newPassword,
    }) as unknown as Promise<void>;
  }
  async toggleUserStatus(id: string): Promise<User> {
    return apiClient.patch(
      `/api/v1/users/${id}/toggle-status`,
    ) as unknown as Promise<User>;
  }
}
export const userService = new UserServiceClient();
