import { expect, test } from "@playwright/test";
import { USUARIO, ingresar } from "./helpers/flujo";

// E2E-1 — Login (F2/F3 del informe de diagnóstico: el botón "muerto" y la sesión no confirmada).
test("E2E-1 · login lleva a /config con la sesión en la barra", async ({ page }) => {
  await ingresar(page);
  await expect(page.getByRole("link", { name: "Historial" })).toBeVisible();

  // La sesión vive en la cookie HttpOnly: sobrevive a recargar la página.
  await page.reload();
  await expect(page.getByTestId("user-email")).toHaveText(USUARIO.email);
});

test("E2E-1 · contraseña incorrecta muestra el error del catálogo", async ({ page }) => {
  await page.goto("/");
  await page.locator("#login-email").fill(USUARIO.email);
  await page.locator("#login-password").fill("no-es-la-contraseña");
  await page.getByRole("button", { name: "Ingresar" }).click();
  // AUTH_INVALID_CREDENTIALS con la estructura estándar (#106), no el texto genérico.
  await expect(page.getByRole("alert")).toContainText(/incorrect/i);
  await expect(page).toHaveURL(/\/$/);
});
