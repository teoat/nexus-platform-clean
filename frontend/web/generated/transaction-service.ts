// Transaction Service Client
import { apiClient } from "../services/apiClient";

export interface Transaction {
  id: string;
  amount: number;
  type: "debit" | "credit";
  description: string;
  accountId: string;
  category: string;
  date: string;
  status: "pending" | "completed" | "failed" | "cancelled";
}

export interface TransactionResponse {
  transactions: Transaction[];
  total: number;
  page: number;
  limit: number;
}

export interface CreateTransactionRequest {
  amount: number;
  type: "debit" | "credit";
  description: string;
  accountId: string;
  category: string;
}

export class TransactionServiceClient {
  async getTransactions(params?: {
    page?: number;
    limit?: number;
    accountId?: string;
    type?: string;
  }): Promise<TransactionResponse> {
    return apiClient.get("/api/v1/transactions", {
      params,
    }) as unknown as Promise<TransactionResponse>;
  }

  async getTransaction(id: string): Promise<Transaction> {
    return apiClient.get(
      `/api/v1/transactions/${id}`,
    ) as unknown as Promise<Transaction>;
  }

  async createTransaction(
    transaction: CreateTransactionRequest,
  ): Promise<Transaction> {
    return apiClient.post(
      "/api/v1/transactions",
      transaction,
    ) as unknown as Promise<Transaction>;
  }

  async updateTransaction(
    id: string,
    updates: Partial<CreateTransactionRequest>,
  ): Promise<Transaction> {
    return apiClient.put(
      `/api/v1/transactions/${id}`,
      updates,
    ) as unknown as Promise<Transaction>;
  }

  async deleteTransaction(id: string): Promise<void> {
    return apiClient.delete(
      `/api/v1/transactions/${id}`,
    ) as unknown as Promise<void>;
  }

  async getTransactionCategories(): Promise<string[]> {
    return apiClient.get(
      "/api/v1/transactions/categories",
    ) as unknown as Promise<string[]>;
  }
}

export const transactionService = new TransactionServiceClient();
