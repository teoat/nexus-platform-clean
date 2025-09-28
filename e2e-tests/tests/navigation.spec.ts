import { test, expect } from "@playwright/test";
test.describe("Navigation and User Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/register");
    await page.fill('input[type="text"]', "navtest");
    await page.fill('input[type="email"]', "navtest@example.com");
    await page.fill('input[type="password"]', "password123");
    await page.fill('input[type="password"]:nth-of-type(2)', "password123");
    await page.click('button[type="submit"]');
    await page.click("text=Sign In");
    await page.fill('input[type="text"]', "navtest");
    await page.fill('input[type="password"]', "password123");
    await page.click('button[type="submit"]');
  });
  test("should navigate between all main pages", async ({ page }) => {
    await expect(page).toHaveURL("/");
    await expect(page.locator("h4")).toContainText("Welcome, navtest!");
    await page.click("text=Accounts");
    await expect(page).toHaveURL("/accounts");
    await expect(page.locator("h4")).toContainText("Your Accounts");
    await page.click("text=Transactions");
    await expect(page).toHaveURL("/transactions");
    await expect(page.locator("h4")).toContainText("Your Transactions");
    await page.click("text=Analytics");
    await expect(page).toHaveURL("/analytics");
    await expect(page.locator("h4")).toContainText("Analytics Dashboard");
    await page.click("text=Dashboard");
    await expect(page).toHaveURL("/");
  });
  test("should maintain authentication state across navigation", async ({
    page,
  }) => {
    await page.click("text=Accounts");
    await page.click("text=Transactions");
    await page.click("text=Analytics");
    await expect(page.locator("text=Welcome, navtest")).toBeVisible();
  });
  test("should redirect to login when not authenticated", async ({ page }) => {
    await page.click("text=Logout");
    await expect(page).toHaveURL("/login");
    await page.goto("/accounts");
    await expect(page).toHaveURL("/login");
    await page.goto("/transactions");
    await expect(page).toHaveURL("/login");
    await page.goto("/analytics");
    await expect(page).toHaveURL("/login");
  });
  test("should handle mobile navigation", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('[aria-label="open drawer"]')).toBeVisible();
    await page.click('[aria-label="open drawer"]');
    await expect(page.locator("text=Dashboard")).toBeVisible();
    await expect(page.locator("text=Accounts")).toBeVisible();
    await expect(page.locator("text=Transactions")).toBeVisible();
    await expect(page.locator("text=Analytics")).toBeVisible();
  });
  test("should show loading states during navigation", async ({ page }) => {
    await page.click("text=Accounts");
    await expect(page.locator("h4")).toContainText("Your Accounts");
  });
  test("should handle browser back/forward navigation", async ({ page }) => {
    await page.click("text=Accounts");
    await expect(page).toHaveURL("/accounts");
    await page.click("text=Transactions");
    await expect(page).toHaveURL("/transactions");
    await page.goBack();
    await expect(page).toHaveURL("/accounts");
    await page.goForward();
    await expect(page).toHaveURL("/transactions");
  });
});
