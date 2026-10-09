import { expect, test } from "@playwright/test";
import { linkDeVerificacion } from "./helpers/mailpit";
import { ingresar } from "./helpers/flujo";

// E2E-0 — Registro + verificación por mail (CU-01). La integración SMTP de punta a punta: el
// backend manda el mail por SMTP a Mailpit (DECISIÓN 049) y el link que trae verifica la cuenta.
test("E2E-0 · registro, mail de verificación en Mailpit, verificación y login", async ({ page, request }) => {
  // Email único por corrida: si la base no se recreó (en local), el registro no choca con
  // AUTH_EMAIL_ALREADY_REGISTERED.
  const email = `e2e-${Date.now()}@ucc.edu.ar`;
  const password = "e2e-metis-1234";

  await page.goto("/");
  await page.getByRole("button", { name: "Registrate" }).click();
  await page.locator("#register-email").fill(email);
  await page.locator("#register-password").fill(password);
  await page.locator("#register-nombre").fill("Usuario E2E");
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.getByRole("alert")).toContainText("Cuenta creada");

  const link = await linkDeVerificacion(request, email);
  await page.goto(link);
  await expect(page.locator("output")).toContainText("Cuenta verificada. Ya podés iniciar sesión.");
  await page.getByRole("link", { name: "Ir a la puerta de entrada" }).click();
  await expect(page).toHaveURL(/\/$/);

  // La cuenta recién verificada entra.
  await ingresar(page, email, password);
});
