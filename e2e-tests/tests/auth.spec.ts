import { test, expect } from "@playwright/test";
test.describe("Authentication Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });
  test("should redirect to login when not authenticated", async ({ page }) => {
    await expect(page).toHaveURL("/login");
    await expect(page.locator("h5")).toContainText("Login");
  });
  test("should register a new user successfully", async ({ page }) => {
    await page.goto("/register");
    await page.fill('input[type="text"]', "testuser");
    await page.fill('input[type="email"]', "test@example.com");
    await page.fill('input[type="password"]', "password123");
    await page.fill('input[type="password"]:nth-of-type(2)', "password123");
    await page.click('button[type="submit"]');
    await expect(page.locator(".MuiAlert-message")).toContainText(
      "Registration successful",
    );
  });
  test("should login with valid credentials", async ({ page }) => {
    await page.goto("/register");
    await page.fill('input[type="text"]', "logintest");
    await page.fill('input[type="email"]', "logintest@example.com");
    await page.fill('input[type="password"]', "password123");
    await page.fill('input[type="password"]:nth-of-type(2)', "password123");
    await page.click('button[type="submit"]');
    await expect(page.locator(".MuiAlert-message")).toContainText(
      "Registration successful",
    );
    await page.click("text=Sign In");
    await page.fill('input[type="text"]', "logintest");
    await page.fill('input[type="password"]', "password123");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/");
    await expect(page.locator("h4")).toContainText("Welcome, logintest!");
  });
  test("should show error for invalid login credentials", async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="text"]', "invaliduser");
    await page.fill('input[type="password"]', "wrongpassword");
    await page.click('button[type="submit"]');
    await expect(page.locator(".MuiAlert-message")).toContainText(
      "Invalid username or password",
    );
  });
  test("should logout successfully", async ({ page }) => {
    await page.goto("/register");
    await page.fill('input[type="text"]', "logouttest");
    await page.fill('input[type="email"]', "logouttest@example.com");
    await page.fill('input[type="password"]', "password123");
    await page.fill('input[type="password"]:nth-of-type(2)', "password123");
    await page.click('button[type="submit"]');
    await page.click("text=Sign In");
    await page.fill('input[type="text"]', "logouttest");
    await page.fill('input[type="password"]', "password123");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL("/");
    await page.click("text=Logout");
    await expect(page).toHaveURL("/login");
  });
});
