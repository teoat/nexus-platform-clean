import { test, expect } from "@playwright/test";
test.describe("Accessibility Tests", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });
  test("should have proper heading hierarchy", async ({ page }) => {
    const h1 = page.getByRole("heading", { level: 1 });
    await expect(h1).toHaveCount(1);
    await expect(h1).toHaveText("NEXUS Financial Platform");
  });
  test("should have skip links for keyboard navigation", async ({ page }) => {
    const skipToMain = page.getByRole("link", { name: "Skip to main content" });
    const skipToNav = page.getByRole("link", { name: "Skip to navigation" });
    await expect(skipToMain).toBeAttached();
    await expect(skipToNav).toBeAttached();
  });
  test("should support keyboard navigation", async ({ page }) => {
    await page.keyboard.press("Tab");
    await expect(
      page.getByRole("link", { name: "Skip to main content" }),
    ).toBeFocused();
    await page.keyboard.press("Tab");
    await expect(
      page.getByRole("link", { name: "Skip to navigation" }),
    ).toBeFocused();
    await page.keyboard.press("Tab");
    await expect(
      page.getByRole("link", { name: "NEXUS - Go to homepage" }),
    ).toBeFocused();
  });
  test("should have proper ARIA labels and roles", async ({ page }) => {
    await expect(page.getByRole("navigation")).toBeVisible();
    await expect(page.getByRole("main")).toBeVisible();
    const signInButton = page.getByRole("link", { name: "Sign In" });
    await expect(signInButton).toHaveAttribute(
      "aria-label",
      "Sign in to your account",
    );
  });
  test("should support high contrast mode", async ({ page }) => {
    await page.addStyleTag({
      content: ` .high-contrast * { filter: contrast(150%) !important; } `,
    });
    await page.evaluate(() => {
      document.documentElement.classList.add("high-contrast");
    });
    await expect(
      page.getByRole("heading", { name: "NEXUS Financial Platform" }),
    ).toBeVisible();
  });
  test("should support reduced motion", async ({ page }) => {
    await page.evaluate(() => {
      document.documentElement.classList.add("reduced-motion");
    });
    await expect(
      page.getByRole("heading", { name: "NEXUS Financial Platform" }),
    ).toBeVisible();
  });
  test("should have proper focus indicators", async ({ page }) => {
    const signInLink = page.getByRole("link", { name: "Sign In" });
    await signInLink.focus();
    await expect(signInLink).toBeFocused();
  });
  test("should work with screen reader navigation", async ({ page }) => {
    await page.keyboard.press("Alt+m");
    await expect(page.getByRole("main")).toBeFocused();
    await page.keyboard.press("Alt+n");
    await expect(page.getByRole("navigation")).toBeFocused();
  });
  test("should have proper form labels", async ({ page }) => {
    await page.goto("/login");
    const usernameInput = page.getByLabel("Username");
    const passwordInput = page.getByLabel("Password");
    await expect(usernameInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    await expect(usernameInput).toHaveAttribute("id");
    await expect(passwordInput).toHaveAttribute("id");
  });
  test("should announce toast notifications to screen readers", async ({
    page,
  }) => {
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
    const liveRegion = page.locator("[aria-live]");
    await expect(liveRegion).toBeAttached();
  });
});
