import { expect, test } from "@playwright/test";
import { linkDeReseteo } from "./helpers/mailpit";
import { ingresar } from "./helpers/flujo";

// E2E-6 — Recuperación de contraseña (DECISIÓN 085). El backend manda el mail por SMTP a Mailpit
// (DECISIÓN 049); el link que trae permite elegir una contraseña nueva, una sola vez.
// La cuenta se registra y NO se verifica: restablecer la contraseña prueba el mail, así que
// también deja la cuenta verificada (mitigación de H8, DECISIÓN 034).
test("E2E-6 · olvidé mi contraseña: mail, link de un solo uso, nueva contraseña y login", async ({
  page,
  request,
}) => {
  const email = `e2e-reset-${Date.now()}@ucc.edu.ar`;
  const passwordVieja = `e2e-${crypto.randomUUID()}`;
  const passwordNueva = `e2e-${crypto.randomUUID()}`;

  await page.goto("/");
  await page.getByRole("button", { name: "Registrate" }).click();
  await page.locator("#register-email").fill(email);
  await page.locator("#register-password").fill(passwordVieja);
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.getByRole("alert")).toContainText("Cuenta creada");

  // Pedido desde el link del login.
  await page.goto("/");
  await page.getByRole("link", { name: "¿Olvidaste tu contraseña?" }).click();
  await expect(page).toHaveURL(/\/auth\/forgot-password$/);
  await page.locator("#forgot-email").fill(email);
  await page.getByRole("button", { name: "Enviar link" }).click();
  await expect(page.getByRole("alert")).toContainText("te mandamos un link");

  // Link del mail: elegir la contraseña nueva.
  const link = await linkDeReseteo(request, email);
  await page.goto(link);
  await page.locator("#reset-password").fill(passwordNueva);
  await page.locator("#reset-confirmacion").fill(passwordNueva);
  await page.getByRole("button", { name: "Guardar contraseña" }).click();
  await expect(page.getByRole("alert")).toContainText("Contraseña actualizada");

  // El link ya no sirve.
  await page.goto(link);
  await page.locator("#reset-password").fill(`${passwordNueva}-otra`);
  await page.locator("#reset-confirmacion").fill(`${passwordNueva}-otra`);
  await page.getByRole("button", { name: "Guardar contraseña" }).click();
  await expect(page.getByRole("alert")).toContainText("inválido, expiró o ya se usó");

  // La contraseña nueva entra (aunque el mail nunca se verificó por el link de verificación)...
  await ingresar(page, email, passwordNueva);
});

test("E2E-6 · la contraseña vieja deja de servir tras el reseteo", async ({ page, request }) => {
  const email = `e2e-reset2-${Date.now()}@ucc.edu.ar`;
  const passwordVieja = `e2e-${crypto.randomUUID()}`;
  const passwordNueva = `e2e-${crypto.randomUUID()}`;

  await page.goto("/");
  await page.getByRole("button", { name: "Registrate" }).click();
  await page.locator("#register-email").fill(email);
  await page.locator("#register-password").fill(passwordVieja);
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await expect(page.getByRole("alert")).toContainText("Cuenta creada");

  await page.goto("/auth/forgot-password");
  await page.locator("#forgot-email").fill(email);
  await page.getByRole("button", { name: "Enviar link" }).click();
  await page.goto(await linkDeReseteo(request, email));
  await page.locator("#reset-password").fill(passwordNueva);
  await page.locator("#reset-confirmacion").fill(passwordNueva);
  await page.getByRole("button", { name: "Guardar contraseña" }).click();
  await expect(page.getByRole("alert")).toContainText("Contraseña actualizada");

  await page.goto("/");
  await page.locator("#login-email").fill(email);
  await page.locator("#login-password").fill(passwordVieja);
  await page.getByRole("button", { name: "Ingresar" }).click();
  await expect(page.getByRole("alert")).toContainText(/incorrect/i);
});
