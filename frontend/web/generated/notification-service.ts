// Notification Service Client
import { apiClient } from "../services/apiClient";

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: "info" | "success" | "warning" | "error";
  read: boolean;
  createdAt: string;
}

export interface NotificationResponse {
  notifications: Notification[];
  total: number;
  unreadCount: number;
}

export class NotificationServiceClient {
  async getNotifications(params?: {
    page?: number;
    limit?: number;
    unreadOnly?: boolean;
  }): Promise<NotificationResponse> {
    return apiClient.get("/api/v1/notifications", {
      params,
    }) as unknown as Promise<NotificationResponse>;
  }

  async markAsRead(id: string): Promise<void> {
    return apiClient.patch(
      `/api/v1/notifications/${id}/read`,
    ) as unknown as Promise<void>;
  }

  async markAllAsRead(): Promise<void> {
    return apiClient.patch(
      "/api/v1/notifications/read-all",
    ) as unknown as Promise<void>;
  }

  async deleteNotification(id: string): Promise<void> {
    return apiClient.delete(
      `/api/v1/notifications/${id}`,
    ) as unknown as Promise<void>;
  }

  async createNotification(notification: {
    title: string;
    message: string;
    type: string;
  }): Promise<Notification> {
    return apiClient.post(
      "/api/v1/notifications",
      notification,
    ) as unknown as Promise<Notification>;
  }
}

export const notificationService = new NotificationServiceClient();
