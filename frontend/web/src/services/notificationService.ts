/**
 * NEXUS Platform - Notification Service
 * Real-time push notifications with WebSocket integration
 */

import React, { useState, useEffect, useCallback } from "react";
import { useGlobalStore } from "../store";
import { websocketService } from "./websocketService";
import { handleError, ErrorType, ErrorSeverity } from "../utils/errorHandler";

export interface Notification {
  id: string;
  type: "success" | "error" | "warning" | "info" | "system";
  title: string;
  message: string;
  data?: Record<string, unknown>;
  timestamp: number;
  read: boolean;
  persistent?: boolean;
  actions?: NotificationAction[];
  category?: string;
  priority: "low" | "medium" | "high" | "urgent";
}

export interface NotificationAction {
  id: string;
  label: string;
  action: () => void;
  variant?: "primary" | "secondary" | "danger";
}

export interface NotificationPreferences {
  enabled: boolean;
  types: {
    success: boolean;
    error: boolean;
    warning: boolean;
    info: boolean;
    system: boolean;
  };
  categories: { [key: string]: boolean };
  sound: boolean;
  vibration: boolean;
  desktop: boolean;
  mobile: boolean;
}

class NotificationService {
  private notifications = new Map<string, Notification>();
  private preferences: NotificationPreferences = {
    enabled: true,
    types: {
      success: true,
      error: true,
      warning: true,
      info: true,
      system: true,
    },
    categories: {},
    sound: true,
    vibration: true,
    desktop: true,
    mobile: true,
  };
  private listeners = new Set<(notifications: Notification[]) => void>();
  private wsUnsubscribe: (() => void) | null = null;

  constructor() {
    this.initializeWebSocket();
    this.requestPermission();
    this.loadPreferences();
  }

  private initializeWebSocket(): void {
    this.wsUnsubscribe = websocketService.subscribe(
      "notification",
      (message) => {
        this.handleWebSocketNotification(message.data);
      },
    );
  }

  private async requestPermission(): Promise<boolean> {
    if (!("Notification" in window)) {
      console.warn("This browser does not support notifications");
      return false;
    }

    if (Notification.permission === "granted") {
      return true;
    }

    if (Notification.permission === "denied") {
      return false;
    }

    try {
      const permission = await Notification.requestPermission();
      return permission === "granted";
    } catch (error) {
      console.error("Error requesting notification permission:", error);
      return false;
    }
  }

  private loadPreferences(): void {
    try {
      const saved = localStorage.getItem("notification_preferences");
      if (saved) {
        this.preferences = { ...this.preferences, ...JSON.parse(saved) };
      }
    } catch (error) {
      console.error("Error loading notification preferences:", error);
    }
  }

  private savePreferences(): void {
    try {
      localStorage.setItem(
        "notification_preferences",
        JSON.stringify(this.preferences),
      );
    } catch (error) {
      console.error("Error saving notification preferences:", error);
    }
  }

  public create(
    notification: Omit<Notification, "id" | "timestamp" | "read">,
  ): string {
    const id = this.generateId();
    const fullNotification: Notification = {
      ...notification,
      id,
      timestamp: Date.now(),
      read: false,
    };

    this.notifications.set(id, fullNotification);
    this.notifyListeners();

    if (this.preferences.enabled && this.preferences.desktop) {
      this.showBrowserNotification(fullNotification);
    }

    if (this.preferences.sound) {
      this.playNotificationSound(notification.type);
    }

    if (this.preferences.vibration && "vibrate" in navigator) {
      this.vibrate(notification.priority);
    }

    return id;
  }

  public success(
    title: string,
    message: string,
    options?: Partial<Notification>,
  ): string {
    return this.create({
      type: "success",
      title,
      message,
      priority: "medium",
      ...options,
    });
  }

  public error(
    title: string,
    message: string,
    options?: Partial<Notification>,
  ): string {
    return this.create({
      type: "error",
      title,
      message,
      priority: "high",
      ...options,
    });
  }

  public warning(
    title: string,
    message: string,
    options?: Partial<Notification>,
  ): string {
    return this.create({
      type: "warning",
      title,
      message,
      priority: "medium",
      ...options,
    });
  }

  public info(
    title: string,
    message: string,
    options?: Partial<Notification>,
  ): string {
    return this.create({
      type: "info",
      title,
      message,
      priority: "low",
      ...options,
    });
  }

  public system(
    title: string,
    message: string,
    options?: Partial<Notification>,
  ): string {
    return this.create({
      type: "system",
      title,
      message,
      priority: "medium",
      ...options,
    });
  }

  public markAsRead(id: string): void {
    const notification = this.notifications.get(id);
    if (notification) {
      notification.read = true;
      this.notifyListeners();
    }
  }

  public markAllAsRead(): void {
    this.notifications.forEach((notification) => {
      notification.read = true;
    });
    this.notifyListeners();
  }

  public remove(id: string): void {
    this.notifications.delete(id);
    this.notifyListeners();
  }

  public clear(): void {
    this.notifications.clear();
    this.notifyListeners();
  }

  public getAll(): Notification[] {
    return Array.from(this.notifications.values()).sort(
      (a, b) => b.timestamp - a.timestamp,
    );
  }

  public getUnread(): Notification[] {
    return this.getAll().filter((notification) => !notification.read);
  }

  public getUnreadCount(): number {
    return this.getUnread().length;
  }

  public subscribe(
    listener: (notifications: Notification[]) => void,
  ): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  public updatePreferences(
    preferences: Partial<NotificationPreferences>,
  ): void {
    this.preferences = { ...this.preferences, ...preferences };
    this.savePreferences();
  }

  public getPreferences(): NotificationPreferences {
    return { ...this.preferences };
  }

  private handleWebSocketNotification(data: Record<string, unknown>): void {
    try {
      const notification = {
        type: ((data.type as string) || "info") as
          | "success"
          | "error"
          | "warning"
          | "info"
          | "system",
        title: (data.title as string) || "Notification",
        message: (data.message as string) || "",
        data: data.data as Record<string, unknown>,
        priority: ((data.priority as string) || "medium") as
          | "low"
          | "medium"
          | "high"
          | "urgent",
        category: data.category as string,
        persistent: (data.persistent as boolean) || false,
        actions: data.actions as NotificationAction[],
      };
      this.create(notification);
    } catch (error) {
      handleError(error, ErrorType.UNKNOWN);
    }
  }

  private showBrowserNotification(notification: Notification): void {
    if (!this.preferences.types[notification.type]) {
      return;
    }

    if (
      notification.category &&
      !this.preferences.categories[notification.category]
    ) {
      return;
    }

    try {
      const browserNotification = new Notification(notification.title, {
        body: notification.message,
        icon: this.getNotificationIcon(notification.type),
        badge: this.getNotificationBadge(notification.type),
        tag: notification.id,
        requireInteraction: notification.persistent,
      });

      browserNotification.onclick = () => {
        window.focus();
        this.markAsRead(notification.id);
        browserNotification.close();
      };

      if (!notification.persistent) {
        setTimeout(() => {
          browserNotification.close();
        }, 5000);
      }
    } catch (error) {
      console.error("Error showing browser notification:", error);
    }
  }

  private playNotificationSound(type: string): void {
    try {
      const audio = new Audio(`/sounds/notification-${type}.mp3`);
      audio.volume = 0.5;
      audio.play().catch((error) => {
        console.warn("Could not play notification sound:", error);
      });
    } catch (error) {
      console.warn("Error playing notification sound:", error);
    }
  }

  private vibrate(priority: string): void {
    try {
      const patterns: Record<string, number[]> = {
        low: [100],
        medium: [200, 100, 200],
        high: [300, 100, 300, 100, 300],
        urgent: [500, 100, 500, 100, 500, 100, 500],
      };
      navigator.vibrate(patterns[priority] || patterns.medium);
    } catch (error) {
      console.warn("Error vibrating device:", error);
    }
  }

  private getNotificationIcon(type: string): string {
    const icons: Record<string, string> = {
      success: "/icons/notification-success.png",
      error: "/icons/notification-error.png",
      warning: "/icons/notification-warning.png",
      info: "/icons/notification-info.png",
      system: "/icons/notification-system.png",
    };
    return icons[type] || icons.info;
  }

  private getNotificationBadge(type: string): string {
    return "/icons/notification-badge.png";
  }

  private generateId(): string {
    return `notif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private notifyListeners(): void {
    const notifications = this.getAll();
    this.listeners.forEach((listener) => {
      try {
        listener(notifications);
      } catch (error) {
        console.error("Error in notification listener:", error);
      }
    });
  }

  public destroy(): void {
    if (this.wsUnsubscribe) {
      this.wsUnsubscribe();
    }
    this.listeners.clear();
    this.notifications.clear();
  }
}

export const notificationService = new NotificationService();

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const unsubscribe = notificationService.subscribe((newNotifications) => {
      setNotifications(newNotifications);
      setUnreadCount(notificationService.getUnreadCount());
    });

    setNotifications(notificationService.getAll());
    setUnreadCount(notificationService.getUnreadCount());

    return unsubscribe;
  }, []);

  const markAsRead = useCallback((id: string) => {
    notificationService.markAsRead(id);
  }, []);

  const markAllAsRead = useCallback(() => {
    notificationService.markAllAsRead();
  }, []);

  const remove = useCallback((id: string) => {
    notificationService.remove(id);
  }, []);

  const clear = useCallback(() => {
    notificationService.clear();
  }, []);

  return {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    remove,
    clear,
  };
};

export default notificationService;
