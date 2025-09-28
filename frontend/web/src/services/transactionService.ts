/** * Transaction Service API Client * Handles financial transaction processing and management */
import { apiClient } from "./apiClient";

export interface Transaction {
  id: string;
  user_id: string;
  account_id: string;
  transaction_id: string;
  amount: number;
  transaction_type: "debit" | "credit" | "transfer" | "refund";
  status: "pending" | "completed" | "failed" | "cancelled";
  description: string;
  merchant_name?: string;
  category?: string;
  subcategory?: string;
  tags?: string[];
  metadata?: Record<string, any>;
  transaction_date: string;
  posted_date?: string;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  account_id: string;
  amount: number;
  transaction_type: "debit" | "credit" | "transfer" | "refund";
  description: string;
  merchant_name?: string;
  category?: string;
  subcategory?: string;
  tags?: string[];
  metadata?: Record<string, any>;
  transaction_date?: string;
}

export interface TransactionUpdate {
  description?: string;
  merchant_name?: string;
  category?: string;
  subcategory?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

export interface TransactionFilter {
  account_id?: string;
  transaction_type?: "debit" | "credit" | "transfer" | "refund";
  status?: "pending" | "completed" | "failed" | "cancelled";
  category?: string;
  merchant_name?: string;
  start_date?: string;
  end_date?: string;
  min_amount?: number;
  max_amount?: number;
  tags?: string[];
}

export interface TransferRequest {
  from_account_id: string;
  to_account_id: string;
  amount: number;
  description: string;
  metadata?: Record<string, any>;
}

export interface BalanceResponse {
  account_id: string;
  current_balance: number;
  available_balance: number;
  pending_balance: number;
  last_updated: string;
}

export class TransactionService {
  async getTransactions(
    skip = 0,
    limit = 100,
    filters?: TransactionFilter,
  ): Promise<Transaction[]> {
    const params = { skip, limit, ...filters };
    const response = await apiClient.get<Transaction[]>(
      "/api/v1/transactions",
      params,
    );
    return response.data;
  }

  async getTransactionById(transactionId: string): Promise<Transaction> {
    const response = await apiClient.get<Transaction>(
      `/api/v1/transactions/${transactionId}`,
    );
    return response.data;
  }

  async createTransaction(
    transactionData: TransactionCreate,
  ): Promise<Transaction> {
    const response = await apiClient.post<Transaction>(
      "/api/v1/transactions",
      transactionData,
    );
    return response.data;
  }

  async updateTransaction(
    transactionId: string,
    transactionData: TransactionUpdate,
  ): Promise<Transaction> {
    const response = await apiClient.put<Transaction>(
      `/api/v1/transactions/${transactionId}`,
      transactionData,
    );
    return response.data;
  }

  async deleteTransaction(transactionId: string): Promise<void> {
    await apiClient.delete(`/api/v1/transactions/${transactionId}`);
  }

  async createTransfer(transferData: TransferRequest): Promise<Transaction[]> {
    const response = await apiClient.post<Transaction[]>(
      "/api/v1/accounts/transfer",
      {
        fromAccountId: transferData.from_account_id,
        toAccountId: transferData.to_account_id,
        amount: transferData.amount,
        description: transferData.description,
        metadata: transferData.metadata,
      },
    );
    return response.data;
  }

  async getAccountBalance(accountId: string): Promise<BalanceResponse> {
    const response = await apiClient.get<BalanceResponse>(
      `/api/v1/accounts/${accountId}/balance`,
    );
    return response.data;
  }

  async checkHealth(): Promise<{ status: string; service: string }> {
    const response = await apiClient.get<{ status: string; service: string }>(
      "/api/v1/transactions/health",
    );
    return response.data;
  }
}

export const transactionService = new TransactionService();
