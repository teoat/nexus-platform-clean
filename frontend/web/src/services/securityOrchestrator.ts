/** * Security Orchestrator Integration Service * Provides secure integration between frontend auth components and security orchestration */
import { SecurityEventType, ThreatLevel } from "../types/security";

export interface SecurityEvent {
  eventId: string;
  eventType: SecurityEventType;
  userId?: string;
  ipAddress: string;
  userAgent: string;
  timestamp: string;
  threatLevel: ThreatLevel;
  details: Record<string, any>;
  sessionId?: string;
  location?: string;
}

export interface SecurityMetrics {
  totalEvents: number;
  successfulLogins: number;
  failedLogins: number;
  passwordResets: number;
  registrations: number;
  threatsDetected: number;
  accountsLocked: number;
  lastUpdated: string;
}

export interface LoginRequest {
  username: string;
  password: string;
  rememberMe?: boolean;
}

export interface LoginResponse {
  success: boolean;
  session?: {
    sessionId: string;
    expiresAt: string;
    securityLevel: string;
  };
  user?: {
    id: string;
    username: string;
    email: string;
    role: string;
  };
  error?: string;
}

export interface RegistrationRequest {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
  role: string;
}

export interface RegistrationResponse {
  success: boolean;
  userId?: string;
  message?: string;
  error?: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetResponse {
  success: boolean;
  message?: string;
  error?: string;
}

export interface SessionValidationResponse {
  valid: boolean;
  user?: string;
  expiresAt?: string;
  reason?: string;
}

class SecurityOrchestratorService {
  private baseUrl: string;
  private sessionId: string | null = null;
  private securityLevel: string = "low";

  constructor(baseUrl: string = "/api/security") {
    this.baseUrl = baseUrl;
    this.sessionId = this.getStoredSessionId();
  }

  /** * Orchestrate secure login process */
  async orchestrateLogin(request: LoginRequest): Promise<LoginResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          ...request,
          ipAddress: await this.getClientIP(),
          userAgent: navigator.userAgent,
          sessionId: this.sessionId,
        }),
      });
      const result = await response.json();
      if (result.success && result.session) {
        this.sessionId = result.session.sessionId;
        this.securityLevel = result.session.securityLevel;
        if (this.sessionId) {
          this.storeSessionId(this.sessionId);
        }
      }
      return result;
    } catch (error) {
      console.error("Login orchestration error:", error);
      return {
        success: false,
        error: "Authentication service unavailable",
      };
    }
  }

  /** * Orchestrate secure registration process */
  async orchestrateRegistration(
    request: RegistrationRequest,
  ): Promise<RegistrationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          ...request,
          ipAddress: await this.getClientIP(),
          userAgent: navigator.userAgent,
        }),
      });
      return await response.json();
    } catch (error) {
      console.error("Registration orchestration error:", error);
      return {
        success: false,
        error: "Registration service unavailable",
      };
    }
  }

  /** * Orchestrate secure password reset process */
  async orchestratePasswordReset(
    request: PasswordResetRequest,
  ): Promise<PasswordResetResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/password-reset`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          ...request,
          ipAddress: await this.getClientIP(),
          userAgent: navigator.userAgent,
        }),
      });
      return await response.json();
    } catch (error) {
      console.error("Password reset orchestration error:", error);
      return {
        success: false,
        error: "Password reset service unavailable",
      };
    }
  }

  /** * Validate current session */
  async validateSession(): Promise<SessionValidationResponse> {
    if (!this.sessionId) {
      return {
        valid: false,
        reason: "No active session",
      };
    }
    try {
      const response = await fetch(`${this.baseUrl}/validate-session`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          sessionId: this.sessionId,
          ipAddress: await this.getClientIP(),
        }),
      });
      const result = await response.json();
      if (!result.valid) {
        this.clearSession();
      }
      return result;
    } catch (error) {
      console.error("Session validation error:", error);
      return {
        valid: false,
        reason: "Session validation failed",
      };
    }
  }

  /** * Logout and clear session */
  async logout(): Promise<void> {
    if (this.sessionId) {
      try {
        await fetch(`${this.baseUrl}/logout`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify({
            sessionId: this.sessionId,
            ipAddress: await this.getClientIP(),
          }),
        });
      } catch (error) {
        console.error("Logout error:", error);
      }
    }
    this.clearSession();
  }

  /** * Get security metrics */
  async getSecurityMetrics(): Promise<SecurityMetrics | null> {
    try {
      const response = await fetch(`${this.baseUrl}/metrics`, {
        method: "GET",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error("Failed to fetch security metrics:", error);
    }
    return null;
  }

  /** * Get recent security events */
  async getSecurityEvents(limit: number = 100): Promise<SecurityEvent[]> {
    try {
      const response = await fetch(`${this.baseUrl}/events?limit=${limit}`, {
        method: "GET",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
      });
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.error("Failed to fetch security events:", error);
    }
    return [];
  }

  /** * Get current security level */
  getSecurityLevel(): string {
    return this.securityLevel;
  }

  /** * Check if session is active */
  hasActiveSession(): boolean {
    return this.sessionId !== null;
  }

  /** * Get stored session ID */
  private getStoredSessionId(): string | null {
    try {
      return localStorage.getItem("nexus_session_id");
    } catch {
      return null;
    }
  }

  /** * Store session ID */
  private storeSessionId(sessionId: string): void {
    try {
      localStorage.setItem("nexus_session_id", sessionId);
    } catch (error) {
      console.error("Failed to store session ID:", error);
    }
  }

  /** * Clear session data */
  private clearSession(): void {
    this.sessionId = null;
    this.securityLevel = "low";
    try {
      localStorage.removeItem("nexus_session_id");
    } catch (error) {
      console.error("Failed to clear session:", error);
    }
  }

  /** * Get client IP address (simplified) */
  private async getClientIP(): Promise<string> {
    return "127.0.0.1";
  }

  /** * Enhanced security validation for forms */
  validatePasswordStrength(password: string): {
    isValid: boolean;
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
    if (!/[A-Z]/.test(password)) {
      feedback.push("Password must contain at least one uppercase letter");
    } else {
      score += 1;
    }
    if (!/[a-z]/.test(password)) {
      feedback.push("Password must contain at least one lowercase letter");
    } else {
      score += 1;
    }
    if (!/\d/.test(password)) {
      feedback.push("Password must contain at least one number");
    } else {
      score += 1;
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      feedback.push("Password must contain at least one special character");
    } else {
      score += 1;
    }
    return {
      isValid: score >= 4,
      score,
      feedback,
    };
  }

  /** * Validate email format */
  validateEmail(email: string): boolean {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  }

  /** * Check for suspicious patterns in user input */
  detectSuspiciousInput(input: string): {
    isSuspicious: boolean;
    reasons: string[];
  } {
    const reasons: string[] = [];
    if (
      /('|(\\')|(;)|(--)|(\/\*)|(\*\/)|(\b(union|select|insert|update|delete|drop|create|alter)\b)/i.test(
        input,
      )
    ) {
      reasons.push("Potential SQL injection detected");
    }
    if (/<script|javascript:|on\w+\s*=/i.test(input)) {
      reasons.push("Potential XSS attack detected");
    }
    if (/[;&|`$(){}[\]]/.test(input)) {
      reasons.push("Potential command injection detected");
    }
    return {
      isSuspicious: reasons.length > 0,
      reasons,
    };
  }
}
export const securityOrchestrator = new SecurityOrchestratorService();
