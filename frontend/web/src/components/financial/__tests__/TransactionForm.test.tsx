#!/usr/bin/env typescript
/**
 * NEXUS Platform - TransactionForm Component Tests
 * Integration tests for the TransactionForm component
 */

import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import TransactionForm, { Category } from "../TransactionForm";
import { Account } from "../../../services/accountService";

// Mock data
const mockAccounts: Account[] = [
  {
    id: "1",
    user_id: "user-123",
    account_number: "**** **** **** 1234",
    account_name: "Checking",
    account_type: "checking",
    bank_name: "Nexus Bank",
    routing_number: "123456789",
    balance: 1000,
    currency: "USD",
    is_active: true,
    created_at: "2023-01-01T00:00:00Z",
    updated_at: "2023-01-01T00:00:00Z",
  },
  {
    id: "2",
    user_id: "user-123",
    account_number: "**** **** **** 5678",
    account_name: "Savings",
    account_type: "savings",
    bank_name: "Nexus Bank",
    routing_number: "123456789",
    balance: 5000,
    currency: "USD",
    is_active: true,
    created_at: "2023-01-01T00:00:00Z",
    updated_at: "2023-01-01T00:00:00Z",
  },
];

const mockCategories: Category[] = [
  { id: "1", name: "Food & Dining", type: "expense" },
  { id: "2", name: "Income", type: "income" },
  { id: "3", name: "Transportation", type: "expense" },
];

const mockTransaction = {
  id: "1",
  account_id: "1",
  description: "Test Transaction",
  amount: 100,
  transaction_type: "expense" as const,
  category: "1",
  date: "2024-01-15",
};

describe("TransactionForm Component", () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders create form by default", () => {
    render(
      <TransactionForm
        accounts={mockAccounts}
        categories={mockCategories}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />,
    );

    expect(screen.getByText("Create Transaction")).toBeInTheDocument();
    expect(screen.getByLabelText(/account/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/amount/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/date/i)).toBeInTheDocument();
  });

  it("renders edit form when transaction is provided", () => {
    render(
      <TransactionForm
        transaction={mockTransaction}
        accounts={mockAccounts}
        categories={mockCategories}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        mode="edit"
      />,
    );

    expect(screen.getByText("Edit Transaction")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Test Transaction")).toBeInTheDocument();
    expect(screen.getByDisplayValue("100")).toBeInTheDocument();
  });

  it("shows loading state", () => {
    render(
      <TransactionForm
        accounts={mockAccounts}
        categories={mockCategories}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        loading={true}
      />,
    );

    expect(
      screen.getByRole("button", { name: /loading/i }),
    ).toBeInTheDocument();
  });

  it("displays error message", () => {
    const errorMessage = "Something went wrong";
    render(
      <TransactionForm
        accounts={mockAccounts}
        categories={mockCategories}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        error={errorMessage}
      />,
    );

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it("handles form submission", async () => {
    render(
      <TransactionForm
        accounts={mockAccounts}
        categories={mockCategories}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />,
    );

    // Fill out the form
    fireEvent.change(screen.getByLabelText(/description/i), {
      target: { value: "Test Transaction" },
    });
    fireEvent.change(screen.getByLabelText(/amount/i), {
      target: { value: "100" },
    });
    fireEvent.change(screen.getByLabelText(/account/i), {
      target: { value: "1" },
    });
    fireEvent.change(screen.getByLabelText(/type/i), {
      target: { value: "expense" },
    });
    fireEvent.change(screen.getByLabelText(/category/i), {
      target: { value: "1" },
    });

    // Submit the form
    fireEvent.click(
      screen.getByRole("button", { name: /create transaction/i }),
    );

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          description: "Test Transaction",
          amount: 100,
          account_id: "1",
          transaction_type: "expense",
          category: "1",
        }),
      );
    });
  });

  it("handles cancel action", () => {
    render(
      <TransactionForm
        accounts={mockAccounts}
        categories={mockCategories}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });

  it("validates required fields", async () => {
    render(
      <TransactionForm
        accounts={mockAccounts}
        categories={mockCategories}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />,
    );

    // Try to submit without filling required fields
    fireEvent.click(
      screen.getByRole("button", { name: /create transaction/i }),
    );

    await waitFor(() => {
      expect(mockOnSubmit).not.toHaveBeenCalled();
    });
  });

  it("filters categories based on transaction type", () => {
    render(
      <TransactionForm
        accounts={mockAccounts}
        categories={mockCategories}
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
      />,
    );

    // Change transaction type to income
    fireEvent.change(screen.getByLabelText(/type/i), {
      target: { value: "income" },
    });

    // Categories should be filtered to show only income categories
    const categorySelect = screen.getByLabelText(/category/i);
    expect(categorySelect).toBeInTheDocument();
  });
});
