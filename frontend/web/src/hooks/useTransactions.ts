/**
 * NEXUS Platform - useTransactions Hook
 * Custom hook for transaction management with API integration
 */

import { useState, useEffect, useCallback } from "react";
import { useGlobalStore } from "../store";
import { apiClient } from "../services/apiClient";
import {
  handleApiError,
  ErrorType,
  ErrorSeverity,
} from "../utils/errorHandler";

export interface Transaction {
  id: string;
  account_id: string;
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

export interface TransactionFilters {
  account_id?: string;
  category?: string;
  transaction_type?: string;
  start_date?: string;
  end_date?: string;
  search?: string;
  page?: number;
  limit?: number;
}

export interface TransactionStats {
  total_transactions: number;
  total_income: number;
  total_expenses: number;
  average_transaction: number;
  largest_income?: number;
  largest_expense?: number;
  most_used_category?: string;
  transactions_this_month: number;
  transactions_last_month: number;
  month_over_month_change?: number;
}

export const useTransactions = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<TransactionStats | null>(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0,
  });

  const { addNotification } = useGlobalStore();

  const fetchTransactions = useCallback(
    async (filters: TransactionFilters = {}) => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.getTransactions({
          ...filters,
          page: filters.page || pagination.page,
          limit: filters.limit || pagination.limit,
        });

        setTransactions((response.data as any).transactions || response.data);
        if ((response.data as any).pagination) {
          setPagination((response.data as any).pagination);
        }

        return response.data as any;
      } catch (err) {
        const errorMessage = "Failed to fetch transactions";
        setError(errorMessage);
        handleApiError(err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [pagination.page, pagination.limit],
  );

  const createTransaction = useCallback(
    async (
      transactionData: Omit<Transaction, "id" | "created_at" | "updated_at">,
    ) => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.createTransaction(transactionData);
        setTransactions((prev) => [response.data as Transaction, ...prev]);
        addNotification({
          type: "success",
          title: "Transaction Created",
          message: "Transaction has been created successfully",
          read: false,
        });
        return response.data;
      } catch (err) {
        const errorMessage = "Failed to create transaction";
        setError(errorMessage);
        handleApiError(err);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [addNotification],
  );

  const updateTransaction = useCallback(
    async (id: string, transactionData: Partial<Transaction>) => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.updateTransaction(id, transactionData);
        setTransactions((prev) =>
          prev.map((transaction) =>
            transaction.id === id
              ? { ...transaction, ...(response.data as any) }
              : transaction,
          ),
        );
        addNotification({
          type: "success",
          title: "Transaction Updated",
          message: "Transaction has been updated successfully",
          read: false,
        });
        return response.data;
      } catch (err) {
        const errorMessage = "Failed to update transaction";
        setError(errorMessage);
        handleApiError(err);
        throw err;
      }
    },
    [addNotification],
  );

  const deleteTransaction = useCallback(
    async (id: string) => {
      try {
        setLoading(true);
        setError(null);
        await apiClient.deleteTransaction(id);
        setTransactions((prev) =>
          prev.filter((transaction) => transaction.id !== id),
        );
        addNotification({
          type: "success",
          title: "Transaction Deleted",
          message: "Transaction has been deleted successfully",
          read: false,
        });
        return true;
      } catch (err) {
        const errorMessage = "Failed to delete transaction";
        setError(errorMessage);
        handleApiError(err);
        throw err;
      }
    },
    [addNotification],
  );

  const fetchStats = useCallback(
    async (filters: Partial<TransactionFilters> = {}) => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.get(
          "/transactions/stats",
          Object.fromEntries(
            Object.entries(filters).map(([key, value]) => [key, String(value)]),
          ) as Record<string, string | number | boolean>,
        );
        setStats(response.data as TransactionStats);
        return response.data;
      } catch (err) {
        const errorMessage = "Failed to fetch transaction stats";
        setError(errorMessage);
        handleApiError(err);
        throw err;
      }
    },
    [],
  );

  const bulkDelete = useCallback(
    async (ids: string[]) => {
      try {
        setLoading(true);
        setError(null);
        await Promise.all(ids.map((id) => apiClient.deleteTransaction(id)));
        setTransactions((prev) =>
          prev.filter((transaction) => !ids.includes(transaction.id)),
        );
        addNotification({
          type: "success",
          title: "Transactions Deleted",
          message: `${ids.length} transactions have been deleted successfully`,
          read: false,
        });
        return true;
      } catch (err) {
        const errorMessage = "Failed to delete transactions";
        setError(errorMessage);
        handleApiError(err);
        throw err;
      }
    },
    [addNotification],
  );

  const bulkUpdate = useCallback(
    async (ids: string[], updates: Partial<Transaction>) => {
      try {
        setLoading(true);
        setError(null);
        await Promise.all(
          ids.map((id) => apiClient.updateTransaction(id, updates)),
        );
        setTransactions((prev) =>
          prev.map((transaction) =>
            ids.includes(transaction.id)
              ? { ...transaction, ...updates }
              : transaction,
          ),
        );
        addNotification({
          type: "success",
          title: "Transactions Updated",
          message: `${ids.length} transactions have been updated successfully`,
          read: false,
        });
        return true;
      } catch (err) {
        const errorMessage = "Failed to update transactions";
        setError(errorMessage);
        handleApiError(err);
        throw err;
      }
    },
    [addNotification],
  );

  const searchTransactions = useCallback(
    async (query: string, filters: Partial<TransactionFilters> = {}) => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiClient.getTransactions({
          ...filters,
          search: query,
        });
        const data = response.data as any;
        setTransactions(data.transactions || data);
        return data;
      } catch (err) {
        const errorMessage = "Failed to search transactions";
        setError(errorMessage);
        handleApiError(err);
        throw err;
      }
    },
    [],
  );

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const refresh = useCallback(() => {
    return fetchTransactions();
  }, [fetchTransactions]);

  useEffect(() => {
    fetchTransactions();
  }, []);

  return {
    transactions,
    loading,
    error,
    stats,
    pagination,
    fetchTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    fetchStats,
    bulkDelete,
    bulkUpdate,
    searchTransactions,
    clearError,
    refresh,
    setTransactions,
    setPagination,
  };
};
