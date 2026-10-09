import { defineConfig, devices } from "@playwright/test";

// E2E (DECISIÓN 046, B6 del plan del TP de Calidad). Corre contra el build de producción detrás de
// nginx, levantado con scripts/deploy-local.sh — nunca contra `npm run dev`: con StrictMode de
// desarrollo AuthVerifyPage verifica dos veces el token y StreamPage abre dos streams.
export default defineConfig({
  testDir: "./e2e",
  // Los flujos comparten la base del despliegue (el historial de E2E-4 depende del análisis de
  // E2E-3): uno a la vez y en orden.
  workers: 1,
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  // Etapa 2 ajusta 13 distribuciones antes de mostrar el ranking.
  timeout: 120_000,
  expect: { timeout: 30_000 },
  reporter: [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost",
    trace: "retain-on-failure",
    video: "retain-on-failure",
    screenshot: "only-on-failure",
    locale: "es-AR",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
