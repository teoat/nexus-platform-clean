import { test, expect } from "@playwright/test";
test.describe("Analytics Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/register");
    await page.fill('input[type="text"]', "analyticstest");
    await page.fill('input[type="email"]', "analyticstest@example.com");
    await page.fill('input[type="password"]', "password123");
    await page.fill('input[type="password"]:nth-of-type(2)', "password123");
    await page.click('button[type="submit"]');
    await page.click("text=Sign In");
    await page.fill('input[type="text"]', "analyticstest");
    await page.fill('input[type="password"]', "password123");
    await page.click('button[type="submit"]');
    await page.click("text=Accounts");
    await page.click("text=Add New Account");
    await page.fill('input[placeholder*="Account Name"]', "Analytics Account");
    await page.selectOption("select", "checking");
    await page.fill('input[type="number"]', "2000");
    await page.fill('input[placeholder*="Currency"]', "USD");
    await page.click('button[type="submit"]');
    await page.click("text=Transactions");
    const transactions = [
      { amount: 100, type: "debit", description: "Grocery", category: "Food" },
      {
        amount: 50,
        type: "debit",
        description: "Gas",
        category: "Transportation",
      },
      {
        amount: 2000,
        type: "credit",
        description: "Salary",
        category: "Income",
      },
      {
        amount: 75,
        type: "debit",
        description: "Utilities",
        category: "Bills",
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
    await page.click("text=Analytics");
    await expect(page).toHaveURL("/analytics");
  });
  test("should display analytics dashboard", async ({ page }) => {
    await expect(page.locator("h4")).toContainText("Analytics Dashboard");
    await expect(
      page.locator("text=Insights into your financial data"),
    ).toBeVisible();
  });
  test("should show financial summary cards", async ({ page }) => {
    await expect(page.locator("text=Total Income")).toBeVisible();
    await expect(page.locator("text=Total Expenses")).toBeVisible();
    await expect(page.locator("text=Net Amount")).toBeVisible();
    await expect(page.locator("text=Total Transactions")).toBeVisible();
    await expect(page.locator("text=$2,000.00")).toBeVisible();
    await expect(page.locator("text=$225.00")).toBeVisible();
    await expect(page.locator("text=$1,775.00")).toBeVisible();
    await expect(page.locator("text=4")).toBeVisible();
  });
  test("should display expense categories", async ({ page }) => {
    await expect(page.locator("text=Expense Categories")).toBeVisible();
    await expect(page.locator("text=Food")).toBeVisible();
    await expect(page.locator("text=Transportation")).toBeVisible();
    await expect(page.locator("text=Bills")).toBeVisible();
  });
  test("should show account summary", async ({ page }) => {
    await expect(page.locator("text=Account Summary")).toBeVisible();
    await expect(page.locator("text=Analytics Account")).toBeVisible();
    await expect(page.locator("text=$2,000.00")).toBeVisible();
  });
  test("should allow time range filtering", async ({ page }) => {
    await expect(page.locator("text=Time Range")).toBeVisible();
    await page.click("text=Time Range");
    await page.click("text=Last 7 days");
    await expect(page.locator("text=Last 7 days")).toBeVisible();
  });
  test("should handle empty data gracefully", async ({ page }) => {
    await page.goto("/analytics");
    await expect(
      page.locator("text=No data available for analytics"),
    ).toBeVisible();
  });
  test("should be responsive on mobile", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator("h4")).toContainText("Analytics Dashboard");
    await expect(page.locator("text=Total Income")).toBeVisible();
  });
});
