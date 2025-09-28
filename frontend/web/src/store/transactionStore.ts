/**
 * NEXUS Platform - Transaction Store
 * Zustand store for transaction state management
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { apiClient } from "../services/apiClient";

export interface Transaction {
  id: string;
  user_id: string;
  account_id: string;
  transaction_id: string;
  description: string;
  amount: number;
  transaction_type: "income" | "expense" | "transfer";
  category: string;
  subcategory?: string;
  reference_number?: string;
  notes?: string;
  date: string;
  tags?: string[];
  created_at: string;
  updated_at?: string;
}

export interface TransactionState {
  transactions: Transaction[];
  selectedTransaction: Transaction | null;
  isLoading: boolean;
  error: string | null;
  filters: {
    account_id?: string;
    category?: string;
    transaction_type?: string;
    start_date?: string;
    end_date?: string;
    search?: string;
  };
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface TransactionActions {
  fetchTransactions: (
    filters?: Partial<TransactionState["filters"]>,
  ) => Promise<void>;
  getTransaction: (id: string) => Promise<Transaction | null>;
  createTransaction: (
    transactionData: Omit<
      Transaction,
      "id" | "user_id" | "transaction_id" | "created_at" | "updated_at"
    >,
  ) => Promise<void>;
  updateTransaction: (
    id: string,
    transactionData: Partial<Transaction>,
  ) => Promise<void>;
  deleteTransaction: (id: string) => Promise<void>;
  selectTransaction: (transaction: Transaction | null) => void;
  setFilters: (filters: Partial<TransactionState["filters"]>) => void;
  clearFilters: () => void;
  setPagination: (pagination: Partial<TransactionState["pagination"]>) => void;
  clearError: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useTransactionStore = create<
  TransactionState & TransactionActions
>()(
  persist(
    (set, get) => ({
      // State
      transactions: [],
      selectedTransaction: null,
      isLoading: false,
      error: null,
      filters: {},
      pagination: {
        page: 1,
        limit: 20,
        total: 0,
        totalPages: 0,
      },

      // Actions
      fetchTransactions: async (filters = {}) => {
        try {
          const currentFilters = get().filters;
          const mergedFilters = { ...currentFilters, ...filters };

          set({ isLoading: true, error: null, filters: mergedFilters });
          const response = await apiClient.getTransactions(mergedFilters);

          const data = response.data as any;
          set({
            transactions: data.transactions || data,
            pagination: data.pagination || get().pagination,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          set({
            isLoading: false,
            error: "Failed to fetch transactions",
          });
          throw error;
        }
      },

      getTransaction: async (id) => {
        try {
          set({ isLoading: true, error: null });
          const response = await apiClient.getTransaction(id);
          const transaction = response.data as Transaction;
          set({ isLoading: false, error: null });
          return transaction;
        } catch (error) {
          set({
            isLoading: false,
            error: "Failed to fetch transaction",
          });
          throw error;
        }
      },

      createTransaction: async (transactionData) => {
        try {
          set({ isLoading: true, error: null });
          const response = await apiClient.createTransaction(transactionData);
          const newTransaction = response.data as Transaction;
          set((state) => ({
            transactions: [newTransaction, ...state.transactions],
            isLoading: false,
            error: null,
          }));
        } catch (error) {
          set({
            isLoading: false,
            error: "Failed to create transaction",
          });
          throw error;
        }
      },

      updateTransaction: async (id, transactionData) => {
        try {
          set({ isLoading: true, error: null });
          const response = await apiClient.updateTransaction(
            id,
            transactionData,
          );
          const updatedTransaction = response.data as Transaction;
          set((state) => ({
            transactions: state.transactions.map((transaction) =>
              transaction.id === id ? updatedTransaction : transaction,
            ),
            selectedTransaction:
              state.selectedTransaction?.id === id
                ? updatedTransaction
                : state.selectedTransaction,
            isLoading: false,
            error: null,
          }));
        } catch (error) {
          set({
            isLoading: false,
            error: "Failed to update transaction",
          });
          throw error;
        }
      },

      deleteTransaction: async (id) => {
        try {
          set({ isLoading: true, error: null });
          await apiClient.deleteTransaction(id);
          set((state) => ({
            transactions: state.transactions.filter(
              (transaction) => transaction.id !== id,
            ),
            selectedTransaction:
              state.selectedTransaction?.id === id
                ? null
                : state.selectedTransaction,
            isLoading: false,
            error: null,
          }));
        } catch (error) {
          set({
            isLoading: false,
            error: "Failed to delete transaction",
          });
          throw error;
        }
      },

      selectTransaction: (transaction) =>
        set({ selectedTransaction: transaction }),
      setFilters: (filters) =>
        set((state) => ({ filters: { ...state.filters, ...filters } })),
      clearFilters: () => set({ filters: {} }),
      setPagination: (pagination) =>
        set((state) => ({
          pagination: { ...state.pagination, ...pagination },
        })),
      clearError: () => set({ error: null }),
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
    }),
    {
      name: "transaction-store",
      partialize: (state) => ({
        transactions: state.transactions,
        selectedTransaction: state.selectedTransaction,
        filters: state.filters,
        pagination: state.pagination,
      }),
    },
  ),
);
