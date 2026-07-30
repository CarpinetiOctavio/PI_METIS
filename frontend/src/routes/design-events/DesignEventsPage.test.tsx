import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "../../auth/AuthProvider";
import { DesignEventsPage } from "./DesignEventsPage";
import { designEventsMock } from "../../mocks/designEvents.mock";

// Mismo patrón vi.stubGlobal("fetch", ...) que el resto del repo (D5) —
// no MSW acá: mezclar el interceptor de MSW (que parchea fetch a nivel
// global) con vi.stubGlobal en el mismo test arriesga que ambos compitan
// por el mismo slot global. MSW queda para el navegador en dev
// (mocks/browser.ts), donde sí aporta valor real: un humano puede navegar
// la pantalla mock sin tooling especial de test.
function stubFetch(authed: boolean) {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.includes("/auth/me")) {
        return Promise.resolve({
          ok: authed,
          status: authed ? 200 : 401,
          json: () =>
            Promise.resolve(
              authed
                ? { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true }
                : {},
            ),
        });
      }
      if (url.includes("/analysis/design-events")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(designEventsMock),
        });
      }
      throw new Error(`unstubbed fetch: ${url}`);
    }),
  );
}

function renderDesignEvents() {
  return render(
    <MemoryRouter initialEntries={["/design-events"]}>
      <AuthProvider>
        <Routes>
          <Route path="/design-events" element={<DesignEventsPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe("DesignEventsPage", () => {
  afterEach(() => vi.unstubAllGlobals());

  // Valores formateados con formatNum (F2/F4, pasada 3): 5 decimales fijos,
  // separador es-AR — 312.7 -> "312,70000". Ver src/i18n/format.ts.
  it("shows a loading state, then the mock value for the default period (T=100)", async () => {
    stubFetch(false);
    renderDesignEvents();

    expect(screen.getByText("Calculando eventos de diseño…")).toBeInTheDocument();
    expect(await screen.findByText("312,70000")).toBeInTheDocument();
    expect(screen.getByText("Valor de diseño · T = 100 años")).toBeInTheDocument();
  });

  it("updates the value when a different periodo_retorno chip is selected", async () => {
    stubFetch(false);
    renderDesignEvents();

    expect(await screen.findByText("312,70000")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "50" }));

    expect(screen.getByText("290,90000")).toBeInTheDocument();
  });

  it("shows the PendingBadge marking the response as mock", async () => {
    stubFetch(false);
    renderDesignEvents();

    expect(await screen.findByText("pendiente · datos de ejemplo")).toBeInTheDocument();
  });

  it("hides the export button for anonymous sessions", async () => {
    stubFetch(false);
    renderDesignEvents();

    expect(await screen.findByText("312,70000")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /Exportar PDF/ }),
    ).not.toBeInTheDocument();
  });

  it("shows a disabled export button for docencia sessions", async () => {
    stubFetch(true);
    renderDesignEvents();

    expect(await screen.findByText("312,70000")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Exportar PDF/ })).toBeDisabled();
  });
});
