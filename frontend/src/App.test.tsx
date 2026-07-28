import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { ThemeProvider } from "./theme/ThemeProvider";
import App from "./App";

describe("App", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the entry page at the root route", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = typeof input === "string" ? input : input.toString();
        // AuthProvider consulta /auth/me al montar — sin esto, el mock
        // compartido de /ping haría pasar isAuthed=true y RedirectIfAuthed
        // saltearía la puerta de entrada antes de la aserción de abajo.
        if (url.includes("/auth/me")) {
          return Promise.resolve({ ok: false, status: 401 });
        }
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ status: "ok" }),
        });
      }),
    );

    render(
      <ThemeProvider>
        <App />
      </ThemeProvider>,
    );
    // AuthProvider arranca en isLoading=true (esperando /me) — RedirectIfAuthed
    // no renderiza la puerta de entrada hasta que esa carga inicial resuelve.
    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: "Puerta de entrada" }),
      ).toBeInTheDocument(),
    );
    // "METIS" aparece tanto en el TopBar como en el panel de marca de
    // EntryPage — alcanza con confirmar que al menos una instancia rindió.
    expect(screen.getAllByText("METIS").length).toBeGreaterThan(0);
    await waitFor(() =>
      expect(screen.getByTestId("backend-status")).toHaveTextContent(
        "Backend conectado",
      ),
    );
  });
});
