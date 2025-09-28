/**
 * NEXUS Platform - Unified Account Interface
 * Single source of truth for Account type across the application
 */

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
  status: "active" | "inactive" | "closed";
  created_at: string;
  updated_at?: string;
  description?: string;
  last_transaction_date?: string;
  risk_level?: "low" | "medium" | "high";
  metadata?: Record<string, any>;
}

export interface AccountCreate {
  account_name: string;
  account_type: "checking" | "savings" | "credit" | "investment" | "loan";
  bank_name: string;
  routing_number: string;
  initial_balance?: number;
  currency?: string;
  description?: string;
}

export interface AccountUpdate {
  account_name?: string;
  bank_name?: string;
  is_active?: boolean;
  description?: string;
  risk_level?: "low" | "medium" | "high";
}

export interface BalanceResponse {
  account_id: string;
  current_balance: number;
  available_balance: number;
  pending_balance: number;
  last_updated: string;
}
