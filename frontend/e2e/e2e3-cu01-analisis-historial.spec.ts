import { readFile } from "node:fs/promises";
import { expect, test } from "@playwright/test";
import { cargarSerie, ingresar, rechazarAtipico } from "./helpers/flujo";

// E2E-3 y E2E-4 en serie: el historial (E2E-4) muestra el análisis que persiste E2E-3.
test.describe.serial("CU-01 · análisis completo, PDF e historial", () => {
  test("E2E-3 · Etapa 1 y 2 con pausa de Chow, elección de distribución y PDF", async ({ page }) => {
    await ingresar(page);
    await cargarSerie(page, "serie_con_atipico.csv");
    await page.getByRole("button", { name: "Validación + análisis de frecuencia (Etapa 1 y 2)" }).click();
    await page.getByRole("button", { name: "Experto" }).click();
    await page.getByRole("button", { name: "Ejecutar análisis ▸" }).click();

    // F1: el stream llega a la pausa de Chow (el 950 del año 2000) sin abortarse solo.
    await expect(page).toHaveURL(/\/stream$/);
    await rechazarAtipico(page);

    // Segunda pausa: el ranking de Etapa 2, sin ganadora marcada (DECISIÓN 055).
    await expect(page.getByRole("heading", { name: "Elegí una distribución" })).toBeVisible();
    await page.getByRole("button", { name: "Elegir este ajuste" }).and(page.locator(":enabled")).first().click();

    // Con la elección hecha, navega sola a Resultados.
    await expect(page).toHaveURL(/\/results$/);
    await expect(page.getByRole("heading", { name: "Resultados de Etapa 1" })).toBeVisible();

    // PDF de CU-01 (DECISIÓN 075): se baja como blob con <a download>, no como respuesta de red.
    const descarga = page.waitForEvent("download");
    await page.getByRole("button", { name: "Exportar PDF", exact: true }).click();
    const pdf = await descarga;
    expect(pdf.suggestedFilename()).toMatch(/^metis_.*\.pdf$/);
    const contenido = await readFile(await pdf.path());
    expect(contenido.subarray(0, 4).toString("latin1")).toBe("%PDF");
  });

  test("E2E-4 · el historial lista el análisis y abre su detalle", async ({ page }) => {
    await ingresar(page);
    await page.getByRole("link", { name: "Historial" }).click();
    await expect(page).toHaveURL(/\/history$/);

    await page.getByRole("link", { name: /serie_con_atipico\.csv/ }).first().click();
    await expect(page).toHaveURL(/\/history\/[0-9a-f-]{36}$/);
    await expect(page.getByRole("heading", { name: "Detalle del análisis" })).toBeVisible();
  });
});
