import { test, expect } from "@playwright/test";
test.describe("Authentication Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });
  test("should display landing page for unauthenticated users", async ({
    page,
  }) => {
    await expect(
      page.getByRole("heading", { name: "NEXUS Financial Platform" }),
    ).toBeVisible();
    await expect(
      page.getByText("Revolutionizing financial examination"),
    ).toBeVisible();
    await expect(page.getByRole("link", { name: "Sign In" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Sign Up" })).toBeVisible();
  });
  test("should navigate to login page", async ({ page }) => {
    await page.getByRole("link", { name: "Sign In" }).click();
    await expect(page).toHaveURL("/login");
    await expect(
      page.getByRole("heading", { name: "Sign in to NEXUS" }),
    ).toBeVisible();
  });
  test("should navigate to register page", async ({ page }) => {
    await page.getByRole("link", { name: "Sign Up" }).click();
    await expect(page).toHaveURL("/register");
    await expect(
      page.getByRole("heading", { name: "Create your account" }),
    ).toBeVisible();
  });
  test("should show validation errors for empty login form", async ({
    page,
  }) => {
    await page.goto("/login");
    await page.getByRole("button", { name: "Sign In" }).click();
    await expect(page.getByLabel("Username")).toHaveAttribute("required");
    await expect(page.getByLabel("Password")).toHaveAttribute("required");
  });
  test("should show error for invalid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel("Username").fill("invalid@user.com");
    await page.getByLabel("Password").fill("wrongpassword");
    await page.getByRole("button", { name: "Sign In" }).click();
    await expect(page.getByText("Invalid username or password")).toBeVisible();
  });
  test("should successfully login with valid credentials", async ({ page }) => {
    await page.route("**/api/auth/login", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          access_token: "mock-token",
          user: {
            id: 1,
            username: "testuser",
            email: "test@example.com",
            role: "user",
          },
        }),
      });
    });
    await page.goto("/login");
    await page.getByLabel("Username").fill("testuser");
    await page.getByLabel("Password").fill("password123");
    await page.getByRole("button", { name: "Sign In" }).click();
    await expect(page).toHaveURL("/dashboard");
    await expect(page.getByText("Welcome, testuser")).toBeVisible();
  });
  test("should logout successfully", async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem("nexus-auth-token", "mock-token");
    });
    await page.goto("/dashboard");
    await page.getByRole("button", { name: "Sign Out" }).click();
    await expect(page).toHaveURL("/");
    await expect(page.getByRole("link", { name: "Sign In" })).toBeVisible();
  });
});
