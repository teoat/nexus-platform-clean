import { test, expect } from "@playwright/test";
test.describe("Transaction Management", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/register");
    await page.fill('input[type="text"]', "transactiontest");
    await page.fill('input[type="email"]', "transactiontest@example.com");
    await page.fill('input[type="password"]', "password123");
    await page.fill('input[type="password"]:nth-of-type(2)', "password123");
    await page.click('button[type="submit"]');
    await page.click("text=Sign In");
    await page.fill('input[type="text"]', "transactiontest");
    await page.fill('input[type="password"]', "password123");
    await page.click('button[type="submit"]');
    await page.click("text=Accounts");
    await page.click("text=Add New Account");
    await page.fill('input[placeholder*="Account Name"]', "Test Account");
    await page.selectOption("select", "checking");
    await page.fill('input[type="number"]', "1000");
    await page.fill('input[placeholder*="Currency"]', "USD");
    await page.click('button[type="submit"]');
    await page.click("text=Transactions");
    await expect(page).toHaveURL("/transactions");
  });
  test("should create a new transaction", async ({ page }) => {
    await page.click("text=Add New Transaction");
    await page.fill('input[placeholder*="Account ID"]', "1");
    await page.fill('input[placeholder*="Amount"]', "100");
    await page.selectOption("select", "debit");
    await page.fill('input[placeholder*="Description"]', "Test Transaction");
    await page.fill('input[placeholder*="Category"]', "Food");
    await page.fill('input[placeholder*="Currency"]', "USD");
    await page.click('button[type="submit"]');
    await expect(page.locator("text=Test Transaction")).toBeVisible();
    await expect(page.locator("text=$100.00")).toBeVisible();
  });
  test("should edit an existing transaction", async ({ page }) => {
    await page.click("text=Add New Transaction");
    await page.fill('input[placeholder*="Account ID"]', "1");
    await page.fill('input[placeholder*="Amount"]', "50");
    await page.selectOption("select", "credit");
    await page.fill(
      'input[placeholder*="Description"]',
      "Original Transaction",
    );
    await page.fill('input[placeholder*="Category"]', "Income");
    await page.fill('input[placeholder*="Currency"]', "USD");
    await page.click('button[type="submit"]');
    await expect(page.locator("text=Original Transaction")).toBeVisible();
    await page.click("text=Edit");
    await page.fill('input[placeholder*="Description"]', "Updated Transaction");
    await page.fill('input[placeholder*="Amount"]', "75");
    await page.click('button[type="submit"]');
    await expect(page.locator("text=Updated Transaction")).toBeVisible();
    await expect(page.locator("text=$75.00")).toBeVisible();
  });
  test("should delete a transaction", async ({ page }) => {
    await page.click("text=Add New Transaction");
    await page.fill('input[placeholder*="Account ID"]', "1");
    await page.fill('input[placeholder*="Amount"]', "25");
    await page.selectOption("select", "debit");
    await page.fill(
      'input[placeholder*="Description"]',
      "Transaction to Delete",
    );
    await page.fill('input[placeholder*="Category"]', "Misc");
    await page.fill('input[placeholder*="Currency"]', "USD");
    await page.click('button[type="submit"]');
    await expect(page.locator("text=Transaction to Delete")).toBeVisible();
    await page.click("text=Delete");
    await expect(page.locator("text=Transaction to Delete")).not.toBeVisible();
  });
  test("should display transaction cards correctly", async ({ page }) => {
    const transactions = [
      {
        description: "Grocery Shopping",
        amount: 50,
        type: "debit",
        category: "Food",
      },
      {
        description: "Salary",
        amount: 3000,
        type: "credit",
        category: "Income",
      },
      {
        description: "Gas Bill",
        amount: 80,
        type: "debit",
        category: "Utilities",
      },
    ];
    for (const transaction of transactions) {
      await page.click("text=Add New Transaction");
      await page.fill('input[placeholder*="Account ID"]', "1");
      await page.fill(
        'input[placeholder*="Amount"]',
        transaction.amount.toString(),
      );
      await page.selectOption("select", transaction.type);
      await page.fill(
        'input[placeholder*="Description"]',
        transaction.description,
      );
      await page.fill('input[placeholder*="Category"]', transaction.category);
      await page.fill('input[placeholder*="Currency"]', "USD");
      await page.click('button[type="submit"]');
    }
    for (const transaction of transactions) {
      await expect(
        page.locator(`text=${transaction.description}`),
      ).toBeVisible();
      await expect(
        page.locator(`text=$${transaction.amount}.00`),
      ).toBeVisible();
    }
  });
  test("should handle form validation", async ({ page }) => {
    await page.click("text=Add New Transaction");
    await page.click('button[type="submit"]');
    await expect(page.locator("text=Account ID")).toBeVisible();
    await expect(page.locator("text=Amount")).toBeVisible();
    await expect(page.locator("text=Description")).toBeVisible();
  });
});
