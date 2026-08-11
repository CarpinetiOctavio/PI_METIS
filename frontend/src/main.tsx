import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { ThemeProvider } from "./theme/ThemeProvider";
import "@fontsource-variable/jetbrains-mono";
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

renderApp();
