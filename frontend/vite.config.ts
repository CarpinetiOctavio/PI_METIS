import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev-only CORS bypass (Decision D2, docs/frontend-implementation-plan.md §9.2.2):
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
  },
});
