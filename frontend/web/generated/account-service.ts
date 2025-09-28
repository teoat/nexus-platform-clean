import { apiClient } from "../services/apiClient";
export interface Account {
  id: string;
  name: string;
  type: "checking" | "savings" | "credit" | "investment";
  balance: number;
  currency: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  userId: string;
}
export interface CreateAccountRequest {
  name: string;
  type: "checking" | "savings" | "credit" | "investment";
  initialBalance?: number;
  currency?: string;
}
export interface UpdateAccountRequest {
  name?: string;
  type?: "checking" | "savings" | "credit" | "investment";
  isActive?: boolean;
}
export interface AccountsResponse {
  accounts: Account[];
  total: number;
  page: number;
  limit: number;
}
export interface TransferRequest {
  fromAccountId: string;
  toAccountId: string;
  amount: number;
  description?: string;
}
export class AccountServiceClient {
  async getAccounts(params?: {
    page?: number;
    limit?: number;
    type?: string;
  }): Promise<AccountsResponse> {
    return apiClient.get("/api/v1/accounts", {
      params,
    }) as unknown as Promise<AccountsResponse>;
  }
  async getUserAccounts(userId: string): Promise<Account[]> {
    return apiClient.get(
      `/api/v1/users/${userId}/accounts`,
    ) as unknown as Promise<Account[]>;
  }
  async getAccount(id: string): Promise<Account> {
    return apiClient.get(
      `/api/v1/accounts/${id}`,
    ) as unknown as Promise<Account>;
  }
  async createAccount(accountData: CreateAccountRequest): Promise<Account> {
    return apiClient.post(
      "/api/v1/accounts",
      accountData,
    ) as unknown as Promise<Account>;
  }
  async updateAccount(
    id: string,
    accountData: UpdateAccountRequest,
  ): Promise<Account> {
    return apiClient.put(
      `/api/v1/accounts/${id}`,
      accountData,
    ) as unknown as Promise<Account>;
  }
  async deleteAccount(id: string): Promise<void> {
    return apiClient.delete(
      `/api/v1/accounts/${id}`,
    ) as unknown as Promise<void>;
  }
  async getAccountBalance(
    id: string,
  ): Promise<{ balance: number; currency: string }> {
    return apiClient.get(
      `/api/v1/accounts/${id}/balance`,
    ) as unknown as Promise<{ balance: number; currency: string }>;
  }
  async transferFunds(
    transferData: TransferRequest,
  ): Promise<{ transactionId: string; success: boolean }> {
    return apiClient.post(
      "/api/v1/accounts/transfer",
      transferData,
    ) as unknown as Promise<{ transactionId: string; success: boolean }>;
  }
}
export const accountService = new AccountServiceClient();
