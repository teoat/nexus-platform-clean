/**
 * Account Service API Client
 * Handles bank account management and balance tracking
 */

import { apiClient } from "./apiClient";

export interface Account {
  id: string;
  user_id: string;
  account_number: string;
  account_name: string;
  account_type: "checking" | "savings" | "credit" | "investment" | "loan";
  bank_name: string;
  routing_number: string;
  balance: number;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AccountCreate {
  account_name: string;
  account_type: "checking" | "savings" | "credit" | "investment" | "loan";
  bank_name: string;
  routing_number: string;
  initial_balance?: number;
  currency?: string;
}

export interface AccountUpdate {
  account_name?: string;
  bank_name?: string;
  is_active?: boolean;
}

export interface BalanceResponse {
  account_id: string;
  current_balance: number;
  available_balance: number;
  pending_balance: number;
  last_updated: string;
}

export class AccountService {
  private baseUrl = process.env.REACT_APP_API_URL || "http://localhost:8000";

  async getAccounts(): Promise<Account[]> {
    const response = await apiClient.get("/api/v1/accounts");
    return response.data as Account[];
  }

  async getAccountById(accountId: string): Promise<Account> {
    const response = await apiClient.get(`/api/v1/accounts/${accountId}`);
    return response.data as Account;
  }

  async createAccount(accountData: AccountCreate): Promise<Account> {
    const response = await apiClient.post(
      "/api/v1/accounts",
      accountData as unknown as Record<string, unknown>,
    );
    return response.data as Account;
  }

  async updateAccount(
    accountId: string,
    accountData: AccountUpdate,
  ): Promise<Account> {
    const response = await apiClient.put(
      `/api/v1/accounts/${accountId}`,
      accountData as unknown as Record<string, unknown>,
    );
    return response.data as Account;
  }

  async getAccountBalance(accountId: string): Promise<BalanceResponse> {
    const response = await apiClient.get(
      `/api/v1/accounts/${accountId}/balance`,
    );
    return response.data as BalanceResponse;
  }

  async deleteAccount(accountId: string): Promise<void> {
    await apiClient.delete(`/api/v1/accounts/${accountId}`);
  }

  async transferFunds(
    fromAccountId: string,
    toAccountId: string,
    amount: number,
    description?: string,
  ): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post("/api/v1/accounts/transfer", {
      from_account_id: fromAccountId,
      to_account_id: toAccountId,
      amount,
      description,
    });
    return response.data as { success: boolean; message: string };
  }

  async checkHealth(): Promise<{ status: string; service: string }> {
    const response = await apiClient.get("/health");
    return response.data as { status: string; service: string };
  }
}

export const accountService = new AccountService();
