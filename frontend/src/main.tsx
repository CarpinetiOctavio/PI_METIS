import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { ThemeProvider } from "./theme/ThemeProvider";
import "./theme/tokens.instrumento.css";
import "./theme/global.css";
import "./theme/components.css";

function renderApp() {
  createRoot(document.getElementById("root")!).render(
    <StrictMode>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </StrictMode>,
  );
}

// MSW intercepta /api/v1/analysis/design-events (único gap con contrato real
// documentado, ver mocks/handlers.ts) — solo en dev, nunca bajo Vitest
// (jsdom no tiene Service Worker) y nunca en el build de producción.
if (import.meta.env.DEV && !import.meta.env.VITEST) {
  const { worker } = await import("./mocks/browser");
  await worker.start({ onUnhandledRequest: "bypass" });
}

renderApp();
