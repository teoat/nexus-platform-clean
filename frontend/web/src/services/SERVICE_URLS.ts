/**
 * NEXUS Platform - Service URLs
 * Centralized service endpoint URLs
 */

export const SERVICE_URLS = {
  AUTH: "/api/auth",
  USERS: "/api/users",
  ACCOUNTS: "/api/accounts",
  TRANSACTIONS: "/api/transactions",
  ANALYTICS: "/api/analytics",
  MONITORING: "/api/monitoring",
  FEATURES: "/api/features",
  HEALTH: "/api/health",
} as const;

export default SERVICE_URLS;
