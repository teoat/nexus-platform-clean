/**
 * NEXUS Platform - Auth Store
 * Zustand store for authentication state management
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { apiClient } from "../services/apiClient";

export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  role: "user" | "admin" | "moderator";
  created_at: string;
  updated_at?: string;
  avatar?: string;
  status?: "online" | "away" | "busy" | "offline";
  lastSeen?: number;
  currentActivity?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  frenlyAIConnected: boolean;
  monitoringEnabled: boolean;
  featureAccess: string[];
}

export interface AuthActions {
  login: (credentials: { email: string; password: string }) => Promise<void>;
  register: (userData: {
    username: string;
    email: string;
    password: string;
    full_name: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  updateProfile: (userData: Partial<User>) => Promise<void>;
  changePassword: (
    currentPassword: string,
    newPassword: string,
  ) => Promise<void>;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      frenlyAIConnected: false,
      monitoringEnabled: true,
      featureAccess: [],

      // Actions
      login: async (credentials) => {
        try {
          set({ isLoading: true, error: null });
          const response = await apiClient.login(credentials);
          set({
            user: response.data.user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          set({
            isLoading: false,
            error: "Login failed. Please check your credentials.",
          });
          throw error;
        }
      },

      register: async (userData) => {
        try {
          set({ isLoading: true, error: null });
          await apiClient.register(userData);
          set({ isLoading: false, error: null });
        } catch (error) {
          set({
            isLoading: false,
            error: "Registration failed. Please try again.",
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          set({ isLoading: true });
          await apiClient.logout();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          set({ isLoading: false });
          // Still clear the auth state even if logout fails
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      checkAuth: async () => {
        try {
          set({ isLoading: true, error: null });
          const response = await apiClient.getUser("me");
          set({
            user: response.data as User,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      updateProfile: async (userData) => {
        try {
          const { user } = get();
          if (!user) throw new Error("No user logged in");

          set({ isLoading: true, error: null });
          const response = await apiClient.updateUser(user.id, userData);
          set({
            user: { ...user, ...response.data },
            isLoading: false,
            error: null,
          });
        } catch (error) {
          set({
            isLoading: false,
            error: "Failed to update profile",
          });
          throw error;
        }
      },

      changePassword: async (currentPassword, newPassword) => {
        try {
          const { user } = get();
          if (!user) throw new Error("No user logged in");

          set({ isLoading: true, error: null });
          await apiClient.updateUser(user.id, {
            current_password: currentPassword,
            new_password: newPassword,
          });
          set({ isLoading: false, error: null });
        } catch (error) {
          set({
            isLoading: false,
            error: "Failed to change password",
          });
          throw error;
        }
      },

      clearError: () => set({ error: null }),
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
    }),
    {
      name: "auth-store",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);
