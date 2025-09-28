/**
 * NEXUS Platform - Account Store
 * Zustand store for account state management
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { apiClient } from "../services/apiClient";

export interface Account {
  id: string;
  user_id: string;
  account_number: string;
  account_name: string;
  account_type: "checking" | "savings" | "credit" | "investment";
  balance: number;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface AccountState {
  accounts: Account[];
  selectedAccount: Account | null;
  isLoading: boolean;
  loading: boolean;
  error: string | null;
}

export interface AccountActions {
  fetchAccounts: () => Promise<void>;
  getAccount: (id: string) => Promise<Account | null>;
  createAccount: (
    accountData: Omit<Account, "id" | "user_id" | "created_at" | "updated_at">,
  ) => Promise<void>;
  updateAccount: (id: string, accountData: Partial<Account>) => Promise<void>;
  deleteAccount: (id: string) => Promise<void>;
  selectAccount: (account: Account | null) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAccountStore = create<AccountState & AccountActions>()(
  persist(
    (set, get) => ({
      // State
      accounts: [],
      selectedAccount: null,
      isLoading: false,
      loading: false,
      error: null,

      // Actions
      fetchAccounts: async () => {
        try {
          set({ isLoading: true, loading: true, error: null });
          const response = await apiClient.getAccounts();
          set({
            accounts: response.data as Account[],
            isLoading: false,
            loading: false,
            error: null,
          });
        } catch (error) {
          set({
            isLoading: false,
            loading: false,
            error: "Failed to fetch accounts",
          });
          throw error;
        }
      },

      getAccount: async (id) => {
        try {
          set({ isLoading: true, error: null });
          const response = await apiClient.getAccount(id);
          const account = response.data as Account;
          set({ isLoading: false, error: null });
          return account;
        } catch (error) {
          set({
            isLoading: false,
            error: "Failed to fetch account",
          });
          throw error;
        }
      },

      createAccount: async (accountData) => {
        try {
          set({ isLoading: true, error: null });
          const response = await apiClient.createAccount(accountData);
          const newAccount = response.data as Account;
          set((state) => ({
            accounts: [...state.accounts, newAccount],
            isLoading: false,
            error: null,
          }));
        } catch (error) {
          set({
            isLoading: false,
            error: "Failed to create account",
          });
          throw error;
        }
      },

      updateAccount: async (id, accountData) => {
        try {
          set({ isLoading: true, error: null });
          const response = await apiClient.updateAccount(id, accountData);
          const updatedAccount = response.data as Account;
          set((state) => ({
            accounts: state.accounts.map((account) =>
              account.id === id ? updatedAccount : account,
            ),
            selectedAccount:
              state.selectedAccount?.id === id
                ? updatedAccount
                : state.selectedAccount,
            isLoading: false,
            error: null,
          }));
        } catch (error) {
          set({
            isLoading: false,
            error: "Failed to update account",
          });
          throw error;
        }
      },

      deleteAccount: async (id) => {
        try {
          set({ isLoading: true, error: null });
          await apiClient.deleteAccount(id);
          set((state) => ({
            accounts: state.accounts.filter((account) => account.id !== id),
            selectedAccount:
              state.selectedAccount?.id === id ? null : state.selectedAccount,
            isLoading: false,
            error: null,
          }));
        } catch (error) {
          set({
            isLoading: false,
            error: "Failed to delete account",
          });
          throw error;
        }
      },

      selectAccount: (account) => set({ selectedAccount: account }),
      clearError: () => set({ error: null }),
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
    }),
    {
      name: "account-store",
      partialize: (state) => ({
        accounts: state.accounts,
        selectedAccount: state.selectedAccount,
      }),
    },
  ),
);
