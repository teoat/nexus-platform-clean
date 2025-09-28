import { test, expect } from "@playwright/test";
test.describe("Account Management", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/register");
    await page.fill('input[type="text"]', "accounttest");
    await page.fill('input[type="email"]', "accounttest@example.com");
    await page.fill('input[type="password"]', "password123");
    await page.fill('input[type="password"]:nth-of-type(2)', "password123");
    await page.click('button[type="submit"]');
    await page.click("text=Sign In");
    await page.fill('input[type="text"]', "accounttest");
    await page.fill('input[type="password"]', "password123");
    await page.click('button[type="submit"]');
    await page.click("text=Accounts");
    await expect(page).toHaveURL("/accounts");
  });
  test("should create a new account", async ({ page }) => {
    await page.click("text=Add New Account");
    await page.fill(
      'input[placeholder*="Account Name"]',
      "Test Checking Account",
    );
    await page.selectOption("select", "checking");
    await page.fill('input[type="number"]', "1000");
    await page.fill('input[placeholder*="Currency"]', "USD");
    await page.fill("textarea", "Test account for E2E testing");
    await page.click('button[type="submit"]');
    await expect(page.locator("text=Test Checking Account")).toBeVisible();
    await expect(page.locator("text=$1,000.00")).toBeVisible();
  });
  test("should edit an existing account", async ({ page }) => {
    await page.click("text=Add New Account");
    await page.fill('input[placeholder*="Account Name"]', "Test Account");
    await page.selectOption("select", "savings");
    await page.fill('input[type="number"]', "500");
    await page.fill('input[placeholder*="Currency"]', "USD");
    await page.click('button[type="submit"]');
    await expect(page.locator("text=Test Account")).toBeVisible();
    await page.click("text=Edit");
    await page.fill(
      'input[placeholder*="Account Name"]',
      "Updated Test Account",
    );
    await page.fill('input[type="number"]', "750");
    await page.click('button[type="submit"]');
    await expect(page.locator("text=Updated Test Account")).toBeVisible();
    await expect(page.locator("text=$750.00")).toBeVisible();
  });
  test("should delete an account", async ({ page }) => {
    await page.click("text=Add New Account");
    await page.fill('input[placeholder*="Account Name"]', "Account to Delete");
    await page.selectOption("select", "checking");
    await page.fill('input[type="number"]', "200");
    await page.fill('input[placeholder*="Currency"]', "USD");
    await page.click('button[type="submit"]');
    await expect(page.locator("text=Account to Delete")).toBeVisible();
    await page.click("text=Delete");
    await expect(page.locator("text=Account to Delete")).not.toBeVisible();
  });
  test("should display account cards correctly", async ({ page }) => {
    const accounts = [
      { name: "Checking Account", type: "checking", balance: 1000 },
      { name: "Savings Account", type: "savings", balance: 5000 },
      { name: "Business Account", type: "business", balance: 2500 },
    ];
    for (const account of accounts) {
      await page.click("text=Add New Account");
      await page.fill('input[placeholder*="Account Name"]', account.name);
      await page.selectOption("select", account.type);
      await page.fill('input[type="number"]', account.balance.toString());
      await page.fill('input[placeholder*="Currency"]', "USD");
      await page.click('button[type="submit"]');
    }
    for (const account of accounts) {
      await expect(page.locator(`text=${account.name}`)).toBeVisible();
      await expect(
        page.locator(`text=$${account.balance.toLocaleString()}.00`),
      ).toBeVisible();
    }
  });
  test("should handle form validation", async ({ page }) => {
    await page.click("text=Add New Account");
    await page.click('button[type="submit"]');
    await expect(page.locator("text=Account Name")).toBeVisible();
    await expect(page.locator("text=Balance")).toBeVisible();
  });
});
