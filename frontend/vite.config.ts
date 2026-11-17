import { configDefaults, defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Dev-only CORS bypass (Decision D2, docs/frontend/frontend-implementation-plan.md §9.2.2):
// same-origin via proxy so the browser never needs cross-origin CORS in development.
// Real CORS handling for production is pendiente P1 — not implemented here.
const BACKEND_ORIGIN = "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: {
      "/api": { target: BACKEND_ORIGIN, changeOrigin: true },
      "/ping": { target: BACKEND_ORIGIN, changeOrigin: true },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./vitest.setup.ts"],
    // Los recorridos de navegación completos (routes.navigation.test.tsx) pasan los 5 s por
    // defecto cuando corren instrumentados por la cobertura en un runner compartido.
    testTimeout: 15_000,
    // e2e/ son specs de Playwright (DECISIÓN 046): el include por defecto de Vitest
    // los tomaría y los correría con jsdom.
    exclude: [...configDefaults.exclude, "e2e/**"],
    // Cobertura (DECISIÓN 077): solo código de producción de src/. lcov alimenta a
    // diff-cover en CI; json-summary, al resumen del job.
    coverage: {
      provider: "v8",
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/**/*.test.{ts,tsx}", "src/test/**", "src/**/*.d.ts", "src/main.tsx"],
      reporter: ["text-summary", "lcov", "html", "json-summary"],
      reportsDirectory: "coverage",
      reportOnFailure: true,
    },
  },
});
