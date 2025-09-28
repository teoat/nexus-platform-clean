/**
 * NEXUS Platform - Unified Transaction Interface
 * Single source of truth for Transaction type across the application
 */

export interface Transaction {
  id: string;
  account_id: string;
  amount: number;
  currency: string;
  transaction_type: "credit" | "debit";
  category: string;
  description: string;
  merchant_name?: string;
  transaction_date: string;
  posted_date?: string;
  status: "pending" | "posted" | "failed" | "cancelled";
  reference_number?: string;
  memo?: string;
  tags?: string[];
  created_at: string;
  updated_at?: string;
  risk_score?: number;
  fraud_flags?: string[];
}

export interface TransactionCreate {
  account_id: string;
  amount: number;
  currency?: string;
  transaction_type: "credit" | "debit";
  category: string;
  description: string;
  merchant_name?: string;
  transaction_date: string;
  memo?: string;
  tags?: string[];
}

export interface TransactionUpdate {
  category?: string;
  description?: string;
  merchant_name?: string;
  memo?: string;
  tags?: string[];
  status?: "pending" | "posted" | "failed" | "cancelled";
}

export interface TransactionFilters {
  account_id?: string;
  start_date?: string;
  end_date?: string;
  category?: string;
  transaction_type?: "credit" | "debit";
  status?: "pending" | "posted" | "failed" | "cancelled";
  min_amount?: number;
  max_amount?: number;
}
