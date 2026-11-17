import { expect, test } from "@playwright/test";
import { cargarSerie, rechazarAtipico } from "./helpers/flujo";

// E2E-2 — Anónimo (CU-02): mismo pipeline, sin persistencia ni exportación.
test("E2E-2 · anónimo corre Etapa 1 sin PDF ni historial", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Entrar como anónimo (solo resultados)" }).click();
  await expect(page).toHaveURL(/\/config$/);

  await cargarSerie(page, "serie_con_atipico.csv");
  await page.getByRole("button", { name: "Solo validación (Etapa 1)" }).click();
  await page.getByRole("button", { name: "Ejecutar análisis ▸" }).click();

  await expect(page).toHaveURL(/\/stream$/);
  await rechazarAtipico(page);

  await expect(page).toHaveURL(/\/results$/);
  await expect(page.getByRole("heading", { name: "Resultados de Etapa 1" })).toBeVisible();
  await expect(page.getByRole("button", { name: /Exportar PDF/ })).toHaveCount(0);
  await expect(page.getByRole("link", { name: "Historial" })).toHaveCount(0);
});
