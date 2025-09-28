import { test, expect } from "@playwright/test";
test.describe("Internationalization Tests", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });
  test("should display English by default", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "NEXUS Financial Platform" }),
    ).toBeVisible();
    await expect(
      page.getByText("Revolutionizing financial examination"),
    ).toBeVisible();
    await expect(page.getByRole("link", { name: "Sign In" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Sign Up" })).toBeVisible();
  });
  test("should switch to Spanish", async ({ page }) => {
    await page.getByRole("button", { name: /🇺🇸 English/ }).click();
    await page.getByRole("menuitem", { name: /🇪🇸 Español/ }).click();
    await expect(
      page.getByRole("heading", { name: "Plataforma Financiera NEXUS" }),
    ).toBeVisible();
    await expect(
      page.getByText("Revolucionando el análisis financiero"),
    ).toBeVisible();
    await expect(
      page.getByRole("link", { name: "Iniciar Sesión" }),
    ).toBeVisible();
    await expect(page.getByRole("link", { name: "Registrarse" })).toBeVisible();
  });
  test("should switch to French", async ({ page }) => {
    await page.getByRole("button", { name: /🇺🇸 English/ }).click();
    await page.getByRole("menuitem", { name: /🇫🇷 Français/ }).click();
    await expect(
      page.getByRole("heading", { name: "Plateforme Financière NEXUS" }),
    ).toBeVisible();
    await expect(
      page.getByText("Révolutionner l'analyse financière"),
    ).toBeVisible();
    await expect(
      page.getByRole("link", { name: "Se Connecter" }),
    ).toBeVisible();
    await expect(page.getByRole("link", { name: "S'inscrire" })).toBeVisible();
  });
  test("should persist language selection", async ({ page }) => {
    await page.getByRole("button", { name: /🇺🇸 English/ }).click();
    await page.getByRole("menuitem", { name: /🇪🇸 Español/ }).click();
    await page.reload();
    await expect(
      page.getByRole("heading", { name: "Plataforma Financiera NEXUS" }),
    ).toBeVisible();
  });
  test("should translate dashboard content", async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem("nexus-auth-token", "mock-token");
    });
    await page.route("**/api/**", async (route) => {
      if (route.request().url().includes("/auth/verify")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            user: {
              id: 1,
              username: "testuser",
              email: "test@example.com",
              role: "management",
            },
          }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ data: [] }),
        });
      }
    });
    await page.getByRole("button", { name: /🇺🇸 English/ }).click();
    await page.getByRole("menuitem", { name: /🇪🇸 Español/ }).click();
    await page.goto("/dashboard");
    await expect(page.getByText("Panel Financiero")).toBeVisible();
    await expect(page.getByText("Balance Total")).toBeVisible();
    await expect(page.getByText("Ingresos Mensuales")).toBeVisible();
    await expect(page.getByText("Gastos Mensuales")).toBeVisible();
    await expect(page.getByText("Transacciones Recientes")).toBeVisible();
  });
  test("should format currency according to locale", async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem("nexus-auth-token", "mock-token");
    });
    await page.route("**/api/**", async (route) => {
      if (route.request().url().includes("/auth/verify")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            user: {
              id: 1,
              username: "testuser",
              email: "test@example.com",
              role: "management",
            },
          }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ data: [] }),
        });
      }
    });
    await page.goto("/dashboard");
    await expect(page.getByText("$125,430.50")).toBeVisible();
    await page.getByRole("button", { name: /🇺🇸 English/ }).click();
    await page.getByRole("menuitem", { name: /🇪🇸 Español/ }).click();
    await expect(page.getByText(/125[.,]430[.,]50/)).toBeVisible();
  });
  test("should translate error messages", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("button", { name: /🇺🇸 English/ }).click();
    await page.getByRole("menuitem", { name: /🇪🇸 Español/ }).click();
    await page.getByLabel("Usuario").fill("invalid@user.com");
    await page.getByLabel("Contraseña").fill("wrongpassword");
    await page.getByRole("button", { name: "Iniciar Sesión" }).click();
    await expect(
      page.getByText("Usuario o contraseña inválidos"),
    ).toBeVisible();
  });
  test("should translate navigation menu", async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem("nexus-auth-token", "mock-token");
    });
    await page.route("**/api/**", async (route) => {
      if (route.request().url().includes("/auth/verify")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            user: {
              id: 1,
              username: "testuser",
              email: "test@example.com",
              role: "management",
            },
          }),
        });
      } else {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ data: [] }),
        });
      }
    });
    await page.goto("/dashboard");
    await page.getByRole("button", { name: /🇺🇸 English/ }).click();
    await page.getByRole("menuitem", { name: /🇫🇷 Français/ }).click();
    await expect(
      page.getByRole("link", { name: "Tableau de Bord" }),
    ).toBeVisible();
    await expect(page.getByRole("link", { name: "Analytique" })).toBeVisible();
    await expect(
      page.getByRole("link", { name: "Transactions" }),
    ).toBeVisible();
    await expect(page.getByRole("link", { name: "Rapports" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Paramètres" })).toBeVisible();
  });
});
