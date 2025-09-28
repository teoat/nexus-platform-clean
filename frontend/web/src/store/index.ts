/**
 * NEXUS Platform - Store Index
 * Centralized exports for all stores
 */

export { useDashboardStore } from './dashboardStore';
export { useAIStore } from './aiStore';
export { useUserStore } from './userStore';
export { useAuthStore } from './authStore';
export { useAppStore as useGlobalStore } from './enhancedStore';

// Re-export types
export type { DashboardState } from './dashboardStore';
export type { AIState, AIActions } from './aiStore';
export type { UserState } from './userStore';
export type { AuthState, AuthActions, User } from './authStore';
