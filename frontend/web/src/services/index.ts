/**
 * NEXUS Platform - Services Barrel Export
 * Centralized exports for optimized tree shaking
 */

// Core Services
export { default as apiClient } from "./apiClient";
export { userService } from "./userService";
export { accountService } from "./accountService";
export { transactionService } from "./transactionService";
export { analyticsService } from "./analyticsService";
export { default as fileService } from "./fileService";
export { default as notificationService } from "./notificationService";

// Security Services
export { default as securityService, useSecurity } from "./securityService";
export { auditService } from "./auditService";

// WebSocket Services
export { useWebSocket } from "./websocketService";

// Performance Services
export {
  default as performanceService,
  usePerformanceMonitoring,
} from "./performanceService";

// Cache Services
export { default as cacheService, useCache } from "./cacheService";

// Search Services
export { default as searchService } from "./searchService";

// Generated Services - TODO: Add when generated
// export * from '../generated';
