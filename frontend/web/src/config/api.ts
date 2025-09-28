export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || "http://localhost:8000",
  REQUEST: {
    TIMEOUT: 10000,
  },
  AUTH: {
    TOKEN_KEY: "nexus_access_token",
    REFRESH_TOKEN_KEY: "nexus_refresh_token",
  },
  HEALTH_URL: "/health",
  ENDPOINTS: {
    HEALTH: "/health",
    API_HEALTH: "/api/health",
    AUTH: {
      REGISTER: "/api/v3/auth/register",
      LOGIN: "/api/v3/auth/login",
      LOGOUT: "/api/v3/auth/logout",
      REFRESH: "/api/v3/auth/refresh",
    },
    USERS: {
      PROFILE: "/api/v3/users/profile",
      SETTINGS: "/api/v3/users/settings",
    },
    FINANCIAL: {
      ACCOUNTS: "/api/v3/financial/accounts",
      TRANSACTIONS: "/api/v3/financial/transactions",
      BUDGETS: "/api/v3/financial/budgets",
      ANALYTICS: "/api/v3/financial/analytics",
    },
    AI: {
      CHAT: "/api/v3/ai/chat",
      INSIGHTS: "/api/v3/ai/insights",
      MONITORING: "/api/v3/ai/monitoring",
      OPTIMIZATION: "/api/v3/ai/optimization",
    },
    ADMIN: {
      USERS: "/api/v3/admin/users",
      AUDIT: "/api/v3/admin/audit",
      SYSTEM: "/api/v3/admin/system",
      MONITORING: "/api/v3/admin/monitoring",
    },
    SYSTEM: {
      CONFIG: "/api/v3/system/config",
      STATUS: "/api/status",
      METRICS: "/api/metrics",
    },
  },
};

export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {},
) => {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
};
