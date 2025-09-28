/**
 * NEXUS Platform - Constants
 * Centralized constants to replace string literals
 */

// User Roles
export const USER_ROLES = {
  ADMIN: "admin",
  MANAGER: "manager",
  USER: "user",
  VIEWER: "viewer",
  AUDITOR: "auditor",
} as const;

export type UserRole = (typeof USER_ROLES)[keyof typeof USER_ROLES];

// Account Types
export const ACCOUNT_TYPES = {
  CHECKING: "checking",
  SAVINGS: "savings",
  CREDIT_CARD: "credit_card",
  INVESTMENT: "investment",
  LOAN: "loan",
} as const;

export type AccountType = (typeof ACCOUNT_TYPES)[keyof typeof ACCOUNT_TYPES];

// Transaction Types
export const TRANSACTION_TYPES = {
  INCOME: "income",
  EXPENSE: "expense",
  TRANSFER: "transfer",
} as const;

export type TransactionType =
  (typeof TRANSACTION_TYPES)[keyof typeof TRANSACTION_TYPES];

// Transaction Status
export const TRANSACTION_STATUS = {
  PENDING: "pending",
  COMPLETED: "completed",
  CANCELLED: "cancelled",
  FAILED: "failed",
} as const;

export type TransactionStatus =
  (typeof TRANSACTION_STATUS)[keyof typeof TRANSACTION_STATUS];

// Notification Types
export const NOTIFICATION_TYPES = {
  INFO: "info",
  WARNING: "warning",
  ERROR: "error",
  SUCCESS: "success",
} as const;

export type NotificationType =
  (typeof NOTIFICATION_TYPES)[keyof typeof NOTIFICATION_TYPES];

// Theme Types
export const THEME_TYPES = {
  LIGHT: "light",
  DARK: "dark",
  AUTO: "auto",
  SYSTEM: "system",
} as const;

export type ThemeType = (typeof THEME_TYPES)[keyof typeof THEME_TYPES];

// Time Periods
export const TIME_PERIODS = {
  WEEK: "week",
  MONTH: "month",
  QUARTER: "quarter",
  YEAR: "year",
} as const;

export type TimePeriod = (typeof TIME_PERIODS)[keyof typeof TIME_PERIODS];

// Component Sizes
export const COMPONENT_SIZES = {
  SMALL: "small",
  MEDIUM: "medium",
  LARGE: "large",
} as const;

export type ComponentSize =
  (typeof COMPONENT_SIZES)[keyof typeof COMPONENT_SIZES];

// Component Variants
export const COMPONENT_VARIANTS = {
  PRIMARY: "primary",
  SECONDARY: "secondary",
  SUCCESS: "success",
  ERROR: "error",
  WARNING: "warning",
  OUTLINE: "outline",
  GHOST: "ghost",
  DANGER: "danger",
} as const;

export type ComponentVariant =
  (typeof COMPONENT_VARIANTS)[keyof typeof COMPONENT_VARIANTS];

// API Status
export const API_STATUS = {
  OPERATIONAL: "operational",
  DEGRADED: "degraded",
  MAINTENANCE: "maintenance",
} as const;

export type ApiStatus = (typeof API_STATUS)[keyof typeof API_STATUS];

// Health Status
export const HEALTH_STATUS = {
  HEALTHY: "healthy",
  UNHEALTHY: "unhealthy",
  WARNING: "warning",
} as const;

export type HealthStatus = (typeof HEALTH_STATUS)[keyof typeof HEALTH_STATUS];

// Service Status
export const SERVICE_STATUS = {
  RUNNING: "running",
  STOPPED: "stopped",
  DEGRADED: "degraded",
} as const;

export type ServiceStatus =
  (typeof SERVICE_STATUS)[keyof typeof SERVICE_STATUS];

// Database Status
export const DATABASE_STATUS = {
  CONNECTED: "connected",
  DISCONNECTED: "disconnected",
  DEGRADED: "degraded",
} as const;

export type DatabaseStatus =
  (typeof DATABASE_STATUS)[keyof typeof DATABASE_STATUS];

// Cache Status
export const CACHE_STATUS = {
  READY: "ready",
  NOT_READY: "not_ready",
  DEGRADED: "degraded",
} as const;

export type CacheStatus = (typeof CACHE_STATUS)[keyof typeof CACHE_STATUS];

// Storage Status
export const STORAGE_STATUS = {
  AVAILABLE: "available",
  UNAVAILABLE: "unavailable",
  DEGRADED: "degraded",
} as const;

export type StorageStatus =
  (typeof STORAGE_STATUS)[keyof typeof STORAGE_STATUS];

// Check Status
export const CHECK_STATUS = {
  OK: "ok",
  ERROR: "error",
  WARNING: "warning",
} as const;

export type CheckStatus = (typeof CHECK_STATUS)[keyof typeof CHECK_STATUS];

// Risk Levels
export const RISK_LEVELS = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  CRITICAL: "critical",
} as const;

export type RiskLevel = (typeof RISK_LEVELS)[keyof typeof RISK_LEVELS];

// Security Event Types
export const SECURITY_EVENT_TYPES = {
  LOGIN: "login",
  LOGOUT: "logout",
  FAILED_LOGIN: "failed_login",
  SUSPICIOUS_ACTIVITY: "suspicious_activity",
  DATA_ACCESS: "data_access",
  PERMISSION_CHANGE: "permission_change",
} as const;

export type SecurityEventType =
  (typeof SECURITY_EVENT_TYPES)[keyof typeof SECURITY_EVENT_TYPES];

// Security Severity Levels
export const SECURITY_SEVERITY = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
  CRITICAL: "critical",
} as const;

export type SecuritySeverity =
  (typeof SECURITY_SEVERITY)[keyof typeof SECURITY_SEVERITY];

// Account Status
export const ACCOUNT_STATUS = {
  ACTIVE: "active",
  INACTIVE: "inactive",
  SUSPENDED: "suspended",
  CLOSED: "closed",
} as const;

export type AccountStatus =
  (typeof ACCOUNT_STATUS)[keyof typeof ACCOUNT_STATUS];

// Compliance Status
export const COMPLIANCE_STATUS = {
  COMPLIANT: "compliant",
  NON_COMPLIANT: "non_compliant",
  PENDING_REVIEW: "pending_review",
  REQUIRES_ACTION: "requires_action",
} as const;

export type ComplianceStatus =
  (typeof COMPLIANCE_STATUS)[keyof typeof COMPLIANCE_STATUS];

// Financial Health Status
export const FINANCIAL_HEALTH_STATUS = {
  GOOD: "good",
  WARNING: "warning",
  CRITICAL: "critical",
} as const;

export type FinancialHealthStatus =
  (typeof FINANCIAL_HEALTH_STATUS)[keyof typeof FINANCIAL_HEALTH_STATUS];

// AI Model Types
export const AI_MODEL_TYPES = {
  CLASSIFICATION: "classification",
  REGRESSION: "regression",
  NLP: "nlp",
  VISION: "vision",
} as const;

export type AIModelType = (typeof AI_MODEL_TYPES)[keyof typeof AI_MODEL_TYPES];

// Activity Types
export const ACTIVITY_TYPES = {
  MILESTONE: "milestone",
  TRADING: "trading",
} as const;

export type ActivityType = (typeof ACTIVITY_TYPES)[keyof typeof ACTIVITY_TYPES];

// Priority Levels
export const PRIORITY_LEVELS = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
} as const;

export type PriorityLevel =
  (typeof PRIORITY_LEVELS)[keyof typeof PRIORITY_LEVELS];

// File Types
export const FILE_TYPES = {
  CSV: "csv",
  EXCEL: "excel",
  JSON: "json",
  PDF: "pdf",
} as const;

export type FileType = (typeof FILE_TYPES)[keyof typeof FILE_TYPES];

// Report Types
export const REPORT_TYPES = {
  SUMMARY: "summary",
  DETAILED: "detailed",
  TAX: "tax",
  CUSTOM: "custom",
} as const;

export type ReportType = (typeof REPORT_TYPES)[keyof typeof REPORT_TYPES];

// Data Types
export const DATA_TYPES = {
  TRANSACTIONS: "transactions",
  ACCOUNTS: "accounts",
  ANALYTICS: "analytics",
  ALL: "all",
} as const;

export type DataType = (typeof DATA_TYPES)[keyof typeof DATA_TYPES];

// Budget Periods
export const BUDGET_PERIODS = {
  WEEKLY: "weekly",
  MONTHLY: "monthly",
  QUARTERLY: "quarterly",
  YEARLY: "yearly",
} as const;

export type BudgetPeriod = (typeof BUDGET_PERIODS)[keyof typeof BUDGET_PERIODS];

// Budget Status
export const BUDGET_STATUS = {
  ACTIVE: "active",
  COMPLETED: "completed",
  EXCEEDED: "exceeded",
} as const;

export type BudgetStatus = (typeof BUDGET_STATUS)[keyof typeof BUDGET_STATUS];

// Privacy Settings
export const PRIVACY_VISIBILITY = {
  PUBLIC: "public",
  PRIVATE: "private",
  FRIENDS: "friends",
} as const;

export type PrivacyVisibility =
  (typeof PRIVACY_VISIBILITY)[keyof typeof PRIVACY_VISIBILITY];

// Currency Codes
export const CURRENCY_CODES = {
  USD: "USD",
  EUR: "EUR",
  GBP: "GBP",
  JPY: "JPY",
  CAD: "CAD",
  AUD: "AUD",
} as const;

export type CurrencyCode = (typeof CURRENCY_CODES)[keyof typeof CURRENCY_CODES];

// Language Codes
export const LANGUAGE_CODES = {
  EN: "en",
  ES: "es",
  FR: "fr",
  DE: "de",
  ZH: "zh",
} as const;

export type LanguageCode = (typeof LANGUAGE_CODES)[keyof typeof LANGUAGE_CODES];

// Timezone Codes
export const TIMEZONE_CODES = {
  AMERICA_NEW_YORK: "America/New_York",
  AMERICA_CHICAGO: "America/Chicago",
  AMERICA_DENVER: "America/Denver",
  AMERICA_LOS_ANGELES: "America/Los_Angeles",
  EUROPE_LONDON: "Europe/London",
  EUROPE_PARIS: "Europe/Paris",
  ASIA_TOKYO: "Asia/Tokyo",
} as const;

export type TimezoneCode = (typeof TIMEZONE_CODES)[keyof typeof TIMEZONE_CODES];

// Date Formats
export const DATE_FORMATS = {
  MM_DD_YYYY: "MM/dd/yyyy",
  DD_MM_YYYY: "dd/MM/yyyy",
  YYYY_MM_DD: "yyyy-MM-dd",
  DD_MMM_YYYY: "dd MMM yyyy",
} as const;

export type DateFormat = (typeof DATE_FORMATS)[keyof typeof DATE_FORMATS];

// Department Names
export const DEPARTMENTS = {
  FINANCE: "Finance",
  ACCOUNTING: "Accounting",
  OPERATIONS: "Operations",
  SALES: "Sales",
  MARKETING: "Marketing",
  HR: "HR",
  IT: "IT",
  LEGAL: "Legal",
  EXECUTIVE: "Executive",
} as const;

export type Department = (typeof DEPARTMENTS)[keyof typeof DEPARTMENTS];

// Color Palette
export const COLORS = {
  PRIMARY: "#2196f3",
  SECONDARY: "#9c27b0",
  SUCCESS: "#4caf50",
  ERROR: "#f44336",
  WARNING: "#ffc107",
  INFO: "#2196f3",
  LIGHT: "#f5f5f5",
  DARK: "#333333",
  WHITE: "#ffffff",
  BLACK: "#000000",
} as const;

export type Color = (typeof COLORS)[keyof typeof COLORS];

// Icon Names
export const ICONS = {
  ACCOUNT_BALANCE: "AccountBalance",
  ATTACH_MONEY: "AttachMoney",
  PIE_CHART: "PieChart",
  BAR_CHART: "BarChart",
  SHOW_CHART: "ShowChart",
  TRENDING_UP: "TrendingUp",
  TRENDING_DOWN: "TrendingDown",
  REFRESH: "Refresh",
  FILTER_LIST: "FilterList",
  DOWNLOAD: "Download",
  SHARE: "Share",
  WARNING: "Warning",
  CHECK_CIRCLE: "CheckCircle",
  SCHEDULE: "Schedule",
  CATEGORY: "Category",
  CALENDAR_TODAY: "CalendarToday",
  ARROW_UPWARD: "ArrowUpward",
  ARROW_DOWNWARD: "ArrowDownward",
  REMOVE: "Remove",
} as const;

export type IconName = (typeof ICONS)[keyof typeof ICONS];

// Default Values
export const DEFAULTS = {
  PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
  DEBOUNCE_DELAY: 300,
  ANIMATION_DURATION: 200,
  TOAST_DURATION: 5000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  TIMEOUT: 10000,
  CACHE_TTL: 300000, // 5 minutes
} as const;

// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: "/api/v1/auth/login",
    REGISTER: "/api/v1/auth/register",
    LOGOUT: "/api/v1/auth/logout",
    REFRESH: "/api/v1/auth/refresh",
    FORGOT_PASSWORD: "/api/v1/auth/forgot-password",
    RESET_PASSWORD: "/api/v1/auth/reset-password",
    VERIFY_EMAIL: "/api/v1/auth/verify-email",
  },
  USER: {
    PROFILE: "/api/v1/users/profile",
    SETTINGS: "/api/v1/users/settings",
    PREFERENCES: "/api/v1/users/preferences",
  },
  ACCOUNTS: {
    LIST: "/api/v1/accounts",
    CREATE: "/api/v1/accounts",
    GET: "/api/v1/accounts/:id",
    UPDATE: "/api/v1/accounts/:id",
    DELETE: "/api/v1/accounts/:id",
  },
  TRANSACTIONS: {
    LIST: "/api/v1/transactions",
    CREATE: "/api/v1/transactions",
    GET: "/api/v1/transactions/:id",
    UPDATE: "/api/v1/transactions/:id",
    DELETE: "/api/v1/transactions/:id",
  },
  DASHBOARD: {
    OVERVIEW: "/api/v1/dashboard",
    ANALYTICS: "/api/v1/dashboard/analytics",
    SUMMARY: "/api/v1/dashboard/summary",
  },
  ANALYTICS: {
    OVERVIEW: "/api/v1/analytics",
    TRENDS: "/api/v1/analytics/trends",
    REPORTS: "/api/v1/analytics/reports",
    EXPORT: "/api/v1/analytics/export",
  },
  FILES: {
    LIST: "/api/v1/files",
    UPLOAD: "/api/v1/files/upload",
    GET: "/api/v1/files/:id",
    DOWNLOAD: "/api/v1/files/:id/download",
    DELETE: "/api/v1/files/:id",
  },
  CATEGORIES: {
    LIST: "/api/v1/categories",
    CREATE: "/api/v1/categories",
    GET: "/api/v1/categories/:id",
    UPDATE: "/api/v1/categories/:id",
    DELETE: "/api/v1/categories/:id",
  },
  BUDGETS: {
    LIST: "/api/v1/budgets",
    CREATE: "/api/v1/budgets",
    GET: "/api/v1/budgets/:id",
    UPDATE: "/api/v1/budgets/:id",
    DELETE: "/api/v1/budgets/:id",
  },
  NOTIFICATIONS: {
    LIST: "/api/v1/notifications",
    CREATE: "/api/v1/notifications",
    GET: "/api/v1/notifications/:id",
    MARK_READ: "/api/v1/notifications/:id/read",
    MARK_ALL_READ: "/api/v1/notifications/read-all",
  },
  SYSTEM: {
    STATUS: "/api/v1/status",
    HEALTH: "/api/v1/health",
    VERSION: "/api/v1/version",
  },
} as const;

// Frontend Routes
export const FRONTEND_ROUTES = {
  AUTH: {
    LOGIN: "/login",
    REGISTER: "/register",
    FORGOT_PASSWORD: "/forgot-password",
    RESET_PASSWORD: "/reset-password",
    LOGOUT: "/logout",
  },
  DASHBOARD: "/dashboard",
  ACCOUNTS: "/accounts",
  TRANSACTIONS: "/transactions",
  ANALYTICS: "/analytics",
  REPORTS: "/reports",
  FILES: "/files",
  BUDGETS: "/budgets",
  SETTINGS: "/settings",
  PROFILE: "/profile",
  ACCOUNT_DETAILS: "/accounts/:id",
  ACCOUNT_EDIT: "/accounts/:id/edit",
  ACCOUNT_NEW: "/accounts/new",
  TRANSACTION_DETAILS: "/transactions/:id",
  TRANSACTION_EDIT: "/transactions/:id/edit",
  TRANSACTION_NEW: "/transactions/new",
  ANALYTICS_OVERVIEW: "/analytics",
  ANALYTICS_TRENDS: "/analytics/trends",
  ANALYTICS_REPORTS: "/analytics/reports",
  FILE_DETAILS: "/files/:id",
  FILE_UPLOAD: "/files/upload",
  SETTINGS_GENERAL: "/settings",
  SETTINGS_SECURITY: "/settings/security",
  SETTINGS_NOTIFICATIONS: "/settings/notifications",
  SETTINGS_PREFERENCES: "/settings/preferences",
} as const;

export default {
  USER_ROLES,
  ACCOUNT_TYPES,
  TRANSACTION_TYPES,
  TRANSACTION_STATUS,
  NOTIFICATION_TYPES,
  THEME_TYPES,
  TIME_PERIODS,
  COMPONENT_SIZES,
  COMPONENT_VARIANTS,
  API_STATUS,
  HEALTH_STATUS,
  SERVICE_STATUS,
  DATABASE_STATUS,
  CACHE_STATUS,
  STORAGE_STATUS,
  CHECK_STATUS,
  RISK_LEVELS,
  PRIORITY_LEVELS,
  FILE_TYPES,
  REPORT_TYPES,
  DATA_TYPES,
  BUDGET_PERIODS,
  BUDGET_STATUS,
  PRIVACY_VISIBILITY,
  CURRENCY_CODES,
  LANGUAGE_CODES,
  TIMEZONE_CODES,
  DATE_FORMATS,
  DEPARTMENTS,
  COLORS,
  ICONS,
  DEFAULTS,
  API_ENDPOINTS,
  FRONTEND_ROUTES,
};
