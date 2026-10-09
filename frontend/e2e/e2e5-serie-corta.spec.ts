import { expect, test } from "@playwright/test";
import { cargarSerie } from "./helpers/flujo";

// E2E-5 — Serie de 8 datos: el bloqueante por longitud (CONTRACT_SERIES_TOO_SHORT) se muestra y
// la pantalla no queda colgada esperando un `complete` que no llega.
test("E2E-5 · una serie de menos de 10 datos se bloquea con su mensaje", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Entrar como anónimo (solo resultados)" }).click();

  await cargarSerie(page, "serie_8_datos.csv");
  await page.getByRole("button", { name: "Ejecutar análisis ▸" }).click();

  await expect(page).toHaveURL(/\/stream$/);
  await expect(page.getByRole("alert")).toContainText(
    "La serie tiene menos de 10 datos. No se puede analizar.",
  );
  // El badge "en vivo" (no el título "Análisis en vivo") se apaga: el stream terminó.
  await expect(page.getByText("en vivo", { exact: true })).toHaveCount(0);
});
