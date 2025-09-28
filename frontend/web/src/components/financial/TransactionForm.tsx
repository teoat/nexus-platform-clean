#!/usr/bin/env typescript
/**
 * NEXUS Platform - Transaction Form Component
 * Comprehensive transaction creation and editing form
 */

import React, { useState } from "react";
import Form from "../ui/Form";
import FormField, { FormFieldProps } from "../ui/FormField";
import Button from "../ui/Button";
import Card from "../ui/Card";
import Alert from "../ui/Alert";
import LoadingSpinner from "../ui/LoadingSpinner";

export interface Transaction {
  id?: string;
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
}

import { Account } from "../../services/accountService";

export interface Category {
  id: string;
  name: string;
  type: "income" | "expense";
  parent_id?: string;
}

export interface TransactionFormProps {
  transaction?: Transaction;
  accounts: Account[];
  categories: Category[];
  onSubmit: (transaction: Transaction) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
  error?: string;
  mode?: "create" | "edit";
}

const TransactionForm: React.FC<TransactionFormProps> = ({
  transaction,
  accounts,
  categories,
  onSubmit,
  onCancel,
  loading = false,
  error,
  mode = "create",
}) => {
  const [formData, setFormData] = useState<Transaction>({
    account_id: "",
    description: "",
    amount: 0,
    transaction_type: "expense",
    category: "",
    subcategory: "",
    reference_number: "",
    notes: "",
    date: new Date().toISOString().split("T")[0],
    tags: [],
    ...transaction,
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFieldChange = (field: keyof Transaction, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSubmitting(true);
      await onSubmit(formData);
    } catch (err) {
      console.error("Form submission error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formFields: FormFieldProps[] = [
    {
      name: "account_id",
      label: "Account",
      type: "select",
      required: true,
      options: accounts.map((account: any) => ({
        label: `${account.account_name} (${account.currency} ${account.balance.toFixed(2)})`,
        value: account.id,
      })),
    },
    {
      name: "description",
      label: "Description",
      type: "text",
      required: true,
      placeholder: "Enter transaction description",
    },
    {
      name: "amount",
      label: "Amount",
      type: "number",
      required: true,
      placeholder: "0.00",
    },
    {
      name: "transaction_type",
      label: "Type",
      type: "select",
      required: true,
      options: [
        { label: "Expense", value: "expense" },
        { label: "Income", value: "income" },
        { label: "Transfer", value: "transfer" },
      ],
    },
    {
      name: "category",
      label: "Category",
      type: "select",
      required: true,
      options: categories.map((category) => ({
        label: category.name,
        value: category.id,
      })),
    },
    {
      name: "date",
      label: "Date",
      type: "date",
      required: true,
    },
    {
      name: "notes",
      label: "Notes",
      type: "textarea",
      placeholder: "Additional notes (optional)",
    },
  ];

  if (loading) {
    return (
      <Card className="p-8">
        <div className="flex items-center justify-center">
          <LoadingSpinner size="large" />
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          {mode === "create" ? "Create Transaction" : "Edit Transaction"}
        </h2>
      </div>

      {error && (
        <Alert severity="error" className="mb-6">
          {error}
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {formFields.map((field) => (
            <div key={field.name}>
              <FormField
                {...field}
                value={
                  String(
                    formData[field.name as keyof Transaction] || "",
                  ) as string
                }
                onChange={(value) =>
                  handleFieldChange(field.name as keyof Transaction, value)
                }
              />
            </div>
          ))}
        </div>

        <div className="flex items-center justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
          <Button
            type="button"
            variant="outlined"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={isSubmitting}
            className="min-w-[120px]"
          >
            {isSubmitting ? (
              <LoadingSpinner size="small" />
            ) : mode === "create" ? (
              "Create Transaction"
            ) : (
              "Update Transaction"
            )}
          </Button>
        </div>
      </form>
    </Card>
  );
};

TransactionForm.displayName = "TransactionForm";

export default TransactionForm;
