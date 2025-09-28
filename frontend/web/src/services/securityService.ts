/**
 * NEXUS Platform - Security Service
 * Comprehensive security management and monitoring
 */

import React, { useState, useEffect, useCallback } from "react";
import { handleError, ErrorType, ErrorSeverity } from "../utils/errorHandler";
import {
  SECURITY_EVENT_TYPES,
  SECURITY_SEVERITY,
  SecurityEventType,
  SecuritySeverity,
} from "../constants";

export interface SecurityEvent {
  id: string;
  type: SecurityEventType;
  severity: SecuritySeverity;
  message: string;
  timestamp: number;
  userId?: string;
  ipAddress?: string;
  userAgent?: string;
  metadata?: Record<string, unknown>;
}

export interface SecurityConfig {
  enableMonitoring: boolean;
  enableEncryption: boolean;
  enableAuditLogging: boolean;
  maxLoginAttempts: number;
  lockoutDuration: number;
  sessionTimeout: number;
  requireStrongPasswords: boolean;
  enable2FA: boolean;
  enableRateLimiting: boolean;
}

export interface SecurityStats {
  totalEvents: number;
  eventsByType: { [type: string]: number };
  eventsBySeverity: { [severity: string]: number };
  recentEvents: SecurityEvent[];
  riskScore: number;
  lastActivity: number;
}

class SecurityService {
  private events: SecurityEvent[] = [];
  private config: SecurityConfig = {
    enableMonitoring: true,
    enableEncryption: true,
    enableAuditLogging: true,
    maxLoginAttempts: 5,
    lockoutDuration: 15 * 60 * 1000, // 15 minutes
    sessionTimeout: 30 * 60 * 1000, // 30 minutes
    requireStrongPasswords: true,
    enable2FA: true,
    enableRateLimiting: true,
  };
  private loginAttempts = new Map<
    string,
    { count: number; lastAttempt: number }
  >();
  private rateLimits = new Map<string, { count: number; resetTime: number }>();

  public logEvent(event: Omit<SecurityEvent, "id" | "timestamp">): string {
    const securityEvent: SecurityEvent = {
      ...event,
      id: this.generateEventId(),
      timestamp: Date.now(),
    };

    this.events.push(securityEvent);

    // Keep only last 1000 events
    if (this.events.length > 1000) {
      this.events = this.events.slice(-1000);
    }

    if (process.env.NODE_ENV === "development") {
      console.log("Security Event:", securityEvent);
    }

    if (process.env.NODE_ENV === "production") {
      this.sendToMonitoring(securityEvent);
    }

    return securityEvent.id;
  }

  public checkLoginAttempts(identifier: string): {
    allowed: boolean;
    remainingAttempts: number;
    lockoutTime?: number;
  } {
    const attempts = this.loginAttempts.get(identifier);

    if (!attempts) {
      return { allowed: true, remainingAttempts: this.config.maxLoginAttempts };
    }

    const now = Date.now();
    const timeSinceLastAttempt = now - attempts.lastAttempt;

    // Reset if lockout period has passed
    if (timeSinceLastAttempt > this.config.lockoutDuration) {
      this.loginAttempts.delete(identifier);
      return { allowed: true, remainingAttempts: this.config.maxLoginAttempts };
    }

    // Check if locked out
    if (attempts.count >= this.config.maxLoginAttempts) {
      const lockoutTime = this.config.lockoutDuration - timeSinceLastAttempt;
      return {
        allowed: false,
        remainingAttempts: 0,
        lockoutTime: Math.max(0, lockoutTime),
      };
    }

    return {
      allowed: true,
      remainingAttempts: this.config.maxLoginAttempts - attempts.count,
    };
  }

  public recordFailedLogin(identifier: string, ipAddress?: string): void {
    const attempts = this.loginAttempts.get(identifier) || {
      count: 0,
      lastAttempt: 0,
    };
    attempts.count++;
    attempts.lastAttempt = Date.now();
    this.loginAttempts.set(identifier, attempts);

    this.logEvent({
      type: SECURITY_EVENT_TYPES.FAILED_LOGIN,
      severity: SECURITY_SEVERITY.MEDIUM,
      message: `Failed login attempt for ${identifier}`,
      ipAddress,
      metadata: { attemptCount: attempts.count },
    });
  }

  public recordSuccessfulLogin(identifier: string, ipAddress?: string): void {
    this.loginAttempts.delete(identifier);
    this.logEvent({
      type: SECURITY_EVENT_TYPES.LOGIN,
      severity: SECURITY_SEVERITY.LOW,
      message: `Successful login for ${identifier}`,
      ipAddress,
    });
  }

  public checkRateLimit(
    identifier: string,
    limit: number = 100,
    window: number = 60000,
  ): boolean {
    const now = Date.now();
    const key = `${identifier}_${Math.floor(now / window)}`;
    const rateLimit = this.rateLimits.get(key);

    if (!rateLimit || now > rateLimit.resetTime) {
      this.rateLimits.set(key, { count: 1, resetTime: now + window });
      return true;
    }

    if (rateLimit.count >= limit) {
      this.logEvent({
        type: SECURITY_EVENT_TYPES.SUSPICIOUS_ACTIVITY,
        severity: SECURITY_SEVERITY.HIGH,
        message: `Rate limit exceeded for ${identifier}`,
        metadata: { limit, window, count: rateLimit.count },
      });
      return false;
    }

    rateLimit.count++;
    return true;
  }

  public validatePassword(password: string): {
    valid: boolean;
    score: number;
    feedback: string[];
  } {
    const feedback: string[] = [];
    let score = 0;

    if (password.length < 8) {
      feedback.push("Password must be at least 8 characters long");
    } else {
      score += 1;
    }

    if (!/[a-z]/.test(password)) {
      feedback.push("Password must contain at least one lowercase letter");
    } else {
      score += 1;
    }

    if (!/[A-Z]/.test(password)) {
      feedback.push("Password must contain at least one uppercase letter");
    } else {
      score += 1;
    }

    if (!/[0-9]/.test(password)) {
      feedback.push("Password must contain at least one number");
    } else {
      score += 1;
    }

    if (!/[^a-zA-Z0-9]/.test(password)) {
      feedback.push("Password must contain at least one special character");
    } else {
      score += 1;
    }

    const valid = score >= 4 && password.length >= 8;
    return { valid, score, feedback };
  }

  public encrypt(data: string): string {
    if (!this.config.enableEncryption) {
      return data;
    }

    try {
      return btoa(encodeURIComponent(data));
    } catch (error) {
      handleError(error, ErrorType.UNKNOWN);
      return data;
    }
  }

  public decrypt(encryptedData: string): string {
    if (!this.config.enableEncryption) {
      return encryptedData;
    }

    try {
      return decodeURIComponent(atob(encryptedData));
    } catch (error) {
      handleError(error, ErrorType.UNKNOWN);
      return encryptedData;
    }
  }

  public sanitizeInput(input: string): string {
    return input
      .replace(/[<>]/g, "") // Remove potential HTML tags
      .replace(/['"]/g, "") // Remove quotes
      .replace(/[;]/g, "") // Remove semicolons
      .trim();
  }

  public validateInput(
    input: string,
    type: "email" | "username" | "text",
  ): { valid: boolean; message?: string } {
    switch (type) {
      case "email": {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return {
          valid: emailRegex.test(input),
          message: emailRegex.test(input) ? undefined : "Invalid email format",
        };
      }
      case "username": {
        const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
        return {
          valid: usernameRegex.test(input),
          message: usernameRegex.test(input)
            ? undefined
            : "Username must be 3-20 characters and contain only letters, numbers, and underscores",
        };
      }
      case "text":
        return {
          valid: input.length > 0 && input.length <= 1000,
          message:
            input.length === 0
              ? "Input is required"
              : input.length > 1000
                ? "Input too long"
                : undefined,
        };
      default:
        return { valid: true };
    }
  }

  public getStats(): SecurityStats {
    const now = Date.now();
    const last24Hours = now - 24 * 60 * 60 * 1000;
    const recentEvents = this.events.filter(
      (event) => event.timestamp > last24Hours,
    );

    const eventsByType = this.events.reduce(
      (acc, event) => {
        acc[event.type] = (acc[event.type] || 0) + 1;
        return acc;
      },
      {} as { [type: string]: number },
    );

    const eventsBySeverity = this.events.reduce(
      (acc, event) => {
        acc[event.severity] = (acc[event.severity] || 0) + 1;
        return acc;
      },
      {} as { [severity: string]: number },
    );

    const riskScore = this.calculateRiskScore();

    return {
      totalEvents: this.events.length,
      eventsByType,
      eventsBySeverity,
      recentEvents: recentEvents.slice(-10),
      riskScore,
      lastActivity:
        this.events.length > 0
          ? this.events[this.events.length - 1].timestamp
          : 0,
    };
  }

  public getEvents(filters?: {
    type?: string;
    severity?: string;
    startDate?: number;
    endDate?: number;
    limit?: number;
  }): SecurityEvent[] {
    let filteredEvents = [...this.events];

    if (filters?.type) {
      filteredEvents = filteredEvents.filter(
        (event) => event.type === filters.type,
      );
    }

    if (filters?.severity) {
      filteredEvents = filteredEvents.filter(
        (event) => event.severity === filters.severity,
      );
    }

    if (filters?.startDate) {
      filteredEvents = filteredEvents.filter(
        (event) => event.timestamp >= filters.startDate!,
      );
    }

    if (filters?.endDate) {
      filteredEvents = filteredEvents.filter(
        (event) => event.timestamp <= filters.endDate!,
      );
    }

    if (filters?.limit) {
      filteredEvents = filteredEvents.slice(-filters.limit);
    }

    return filteredEvents.sort((a, b) => b.timestamp - a.timestamp);
  }

  public clearOldEvents(olderThan: number = 7 * 24 * 60 * 60 * 1000): number {
    const cutoff = Date.now() - olderThan;
    const initialLength = this.events.length;
    this.events = this.events.filter((event) => event.timestamp > cutoff);
    return initialLength - this.events.length;
  }

  public updateConfig(config: Partial<SecurityConfig>): void {
    this.config = { ...this.config, ...config };
  }

  public getConfig(): SecurityConfig {
    return { ...this.config };
  }

  private generateEventId(): string {
    return `sec_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private calculateRiskScore(): number {
    const recentEvents = this.events.filter(
      (event) => event.timestamp > Date.now() - 24 * 60 * 60 * 1000, // Last 24 hours
    );

    let score = 0;
    recentEvents.forEach((event) => {
      switch (event.severity) {
        case SECURITY_SEVERITY.LOW:
          score += 1;
          break;
        case SECURITY_SEVERITY.MEDIUM:
          score += 3;
          break;
        case SECURITY_SEVERITY.HIGH:
          score += 7;
          break;
        case SECURITY_SEVERITY.CRITICAL:
          score += 15;
          break;
      }
    });

    return Math.min(100, score);
  }

  private sendToMonitoring(event: SecurityEvent): void {
    // In a real implementation, this would send to a monitoring service
    console.log("Sending security event to monitoring:", event);
  }
}

export const securityService = new SecurityService();

export const useSecurity = () => {
  const [stats, setStats] = useState<SecurityStats>(securityService.getStats());
  const [events, setEvents] = useState<SecurityEvent[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      setStats(securityService.getStats());
      setEvents(securityService.getEvents({ limit: 50 }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const logEvent = useCallback(
    (event: Omit<SecurityEvent, "id" | "timestamp">) => {
      return securityService.logEvent(event);
    },
    [],
  );

  const checkLoginAttempts = useCallback((identifier: string) => {
    return securityService.checkLoginAttempts(identifier);
  }, []);

  const recordFailedLogin = useCallback(
    (identifier: string, ipAddress?: string) => {
      securityService.recordFailedLogin(identifier, ipAddress);
    },
    [],
  );

  const recordSuccessfulLogin = useCallback(
    (identifier: string, ipAddress?: string) => {
      securityService.recordSuccessfulLogin(identifier, ipAddress);
    },
    [],
  );

  const validatePassword = useCallback((password: string) => {
    return securityService.validatePassword(password);
  }, []);

  const sanitizeInput = useCallback((input: string) => {
    return securityService.sanitizeInput(input);
  }, []);

  const validateInput = useCallback(
    (input: string, type: "email" | "username" | "text") => {
      return securityService.validateInput(input, type);
    },
    [],
  );

  return {
    stats,
    events,
    logEvent,
    checkLoginAttempts,
    recordFailedLogin,
    recordSuccessfulLogin,
    validatePassword,
    sanitizeInput,
    validateInput,
  };
};

export default securityService;
