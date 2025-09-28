/**
 * NEXUS Platform - useAuth Hook
 * Custom hook for authentication management with API integration
 */

import { useState, useEffect, useCallback } from "react";
import { useGlobalStore } from "../store";
import { apiClient } from "../services/apiClient";
import {
  handleApiError,
  ErrorType,
  ErrorSeverity,
} from "../utils/errorHandler";

export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  role: "user" | "admin" | "moderator";
  created_at: string;
  updated_at?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  });

  const { setLoading, addNotification } = useGlobalStore();

  const checkAuth = useCallback(async () => {
    try {
      setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));
      const response = await apiClient.getUser("me");
      if (response.success && response.data) {
        setAuthState({
          user: response.data as User,
          isAuthenticated: true,
          isLoading: false,
          error: null,
        });
        return response.data as User;
      } else {
        throw new Error("Failed to get user data");
      }
    } catch (err) {
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
      return null;
    }
  }, []);

  const login = useCallback(
    async (credentials: LoginCredentials) => {
      try {
        setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));
        setLoading(true);
        const response = await apiClient.login(credentials);
        if (response.success && response.data) {
          const loginData = response.data as {
            user: User;
            access_token: string;
            refresh_token: string;
          };
          setAuthState({
            user: loginData.user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          addNotification({
            type: "success",
            title: "Welcome back!",
            message: `Hello, ${loginData.user?.username || "User"}`,
            read: false,
          });
          return { user: loginData.user, token: loginData.access_token };
        } else {
          throw new Error("Login failed");
        }
      } catch (err) {
        const errorMessage = "Login failed. Please check your credentials.";
        setAuthState((prev) => ({
          ...prev,
          isLoading: false,
          error: errorMessage,
        }));
        handleApiError(err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [addNotification, setLoading],
  );

  const register = useCallback(
    async (userData: RegisterData) => {
      try {
        setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));
        setLoading(true);
        const response = await apiClient.register({
          email: userData.email,
          password: userData.password,
          full_name: userData.full_name || `${userData.username}`,
        });
        addNotification({
          type: "success",
          title: "Account Created",
          message: "Your account has been created successfully. Please log in.",
          read: false,
        });
        return response.data;
      } catch (err) {
        const errorMessage = "Registration failed. Please try again.";
        setAuthState((prev) => ({
          ...prev,
          isLoading: false,
          error: errorMessage,
        }));
        handleApiError(err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [addNotification, setLoading],
  );

  const logout = useCallback(async () => {
    try {
      setLoading(true);
      await apiClient.logout();
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      });
      addNotification({
        type: "info",
        title: "Logged Out",
        message: "You have been logged out successfully",
        read: false,
      });
    } catch (err) {
      handleApiError(err);
    } finally {
      setLoading(false);
    }
  }, [addNotification, setLoading]);

  const updateProfile = useCallback(
    async (userData: Partial<User>) => {
      try {
        if (!authState.user) throw new Error("No user logged in");
        setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));
        const response = await apiClient.updateUser(
          authState.user.id,
          userData,
        );
        setAuthState((prev) => ({
          ...prev,
          user: { ...prev.user!, ...(response.data as any) },
          isLoading: false,
        }));
        addNotification({
          type: "success",
          title: "Profile Updated",
          message: "Your profile has been updated successfully",
          read: false,
        });
        return response.data;
      } catch (err) {
        const errorMessage = "Failed to update profile";
        setAuthState((prev) => ({
          ...prev,
          isLoading: false,
          error: errorMessage,
        }));
        handleApiError(err);
        throw err;
      }
    },
    [authState.user, addNotification],
  );

  const changePassword = useCallback(
    async (currentPassword: string, newPassword: string) => {
      try {
        if (!authState.user) throw new Error("No user logged in");
        setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));
        await apiClient.changePassword({
          current_password: currentPassword,
          new_password: newPassword,
        });
        addNotification({
          type: "success",
          title: "Password Changed",
          message: "Your password has been changed successfully",
          read: false,
        });
        return true;
      } catch (err) {
        const errorMessage = "Failed to change password";
        setAuthState((prev) => ({
          ...prev,
          isLoading: false,
          error: errorMessage,
        }));
        handleApiError(err);
        throw err;
      }
    },
    [authState.user, addNotification],
  );

  const clearError = useCallback(() => {
    setAuthState((prev) => ({ ...prev, error: null }));
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const hasRole = useCallback(
    (role: string) => {
      return authState.user?.role === role;
    },
    [authState.user],
  );

  const hasAnyRole = useCallback(
    (roles: string[]) => {
      return authState.user ? roles.includes(authState.user.role) : false;
    },
    [authState.user],
  );

  const isAdmin = useCallback(() => {
    return hasRole("admin");
  }, [hasRole]);

  const isModerator = useCallback(() => {
    return hasAnyRole(["admin", "moderator"]);
  }, [hasAnyRole]);

  return {
    ...authState,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    checkAuth,
    clearError,
    hasRole,
    hasAnyRole,
    isAdmin,
    isModerator,
  };
};
