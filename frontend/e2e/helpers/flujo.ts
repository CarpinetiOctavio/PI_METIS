import { fileURLToPath } from "node:url";
import { expect, type Page } from "@playwright/test";

// Usuario verificado que siembra scripts/deploy-local.sh (el mismo del smoke del backend).
export const USUARIO = {
  email: process.env.E2E_EMAIL ?? "smoke@ucc.edu.ar",
  password: process.env.E2E_PASSWORD ?? "smoke-metis-1234",
};

/** Ruta absoluta de un archivo de e2e/fixtures/. Copiados de docs/series prueba/ a propósito: si
 *  cambia la serie de docs, el E2E no se rompe en silencio. */
export function fixture(nombre: string): string {
  return fileURLToPath(new URL(`../fixtures/${nombre}`, import.meta.url));
}

/** Login desde la puerta de entrada; termina en /config con la sesión confirmada en la barra. */
export async function ingresar(page: Page, email = USUARIO.email, password = USUARIO.password) {
  await page.goto("/");
  await page.locator("#login-email").fill(email);
  await page.locator("#login-password").fill(password);
  await page.getByRole("button", { name: "Ingresar" }).click();
  await expect(page).toHaveURL(/\/config$/);
  await expect(page.getByTestId("user-email")).toHaveText(email);
}

/** Sube la serie en /config y espera los dropdowns de columnas (preview-columns). La preselección
 *  elige `anio` y `caudal`; se afirma igual. */
export async function cargarSerie(page: Page, nombre: string) {
  await page.getByLabel("Archivo (CSV o Excel)").setInputFiles(fixture(nombre));
  // El value de cada <option> es el índice de la columna; lo legible es el texto.
  await expect(page.locator("#config-columna-x option:checked")).toContainText("anio");
  await expect(page.locator("#config-columna-y option:checked")).toContainText("caudal");
}

/** En el stream: el modal de Chow no se cierra con Escape (M3.2); hay que elegir por nombre. */
export async function rechazarAtipico(page: Page) {
  const modal = page.getByRole("dialog", { name: "Dato atípico detectado" });
  await expect(modal).toBeVisible();
  await modal.getByRole("button", { name: "Rechazar" }).click();
  await expect(modal).toBeHidden();
}
