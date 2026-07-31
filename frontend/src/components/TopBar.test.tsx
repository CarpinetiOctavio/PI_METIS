import { afterEach, describe, expect, it, vi } from "vitest";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "../theme/ThemeProvider";
import { AuthProvider } from "../auth/AuthProvider";
import { renderPage } from "../test/renderPage";
import { TopBar } from "./TopBar";

function stubFetch(
  meResponse: { ok: boolean; status?: number; body: unknown } = {
    ok: false,
    status: 401,
    body: {},
  },
) {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.includes("/auth/me")) {
        return Promise.resolve({
          ok: meResponse.ok,
          status: meResponse.status ?? (meResponse.ok ? 200 : 401),
          json: () => Promise.resolve(meResponse.body),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ status: "ok" }),
      });
    }),
  );
}

function EntryProbe() {
  return <div>entry screen</div>;
}

function renderTopBar() {
  return renderPage(
    <MemoryRouter initialEntries={["/config"]}>
      <ThemeProvider>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<EntryProbe />} />
            <Route path="/config" element={<TopBar />} />
          </Routes>
        </AuthProvider>
      </ThemeProvider>
    </MemoryRouter>,
  );
}

describe("TopBar", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it("shows the METIS wordmark, backend status, and mode badge", async () => {
    stubFetch();

    renderTopBar();
    expect(screen.getByText("METIS")).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByTestId("backend-status")).toHaveTextContent(
        "Backend conectado",
      ),
    );
    expect(screen.getByTestId("mode-badge")).toBeInTheDocument();
  });

  it("toggles the mode badge text when the toggle button is clicked", async () => {
    stubFetch();

    renderTopBar();
    await waitFor(() =>
      expect(screen.getByTestId("backend-status")).toHaveTextContent(
        "Backend conectado",
      ),
    );
    const badge = screen.getByTestId("mode-badge");
    const before = badge.textContent;
    fireEvent.click(screen.getByRole("button", { name: /cambiar tema/i }));
    expect(badge.textContent).not.toBe(before);
  });

  // F4/F5/F6 (informe-diagnostico-ui-rota.md): antes esta barra no tenía un
  // solo link — "Nuevo análisis"/"Historial" eran alcanzables solo tipeando
  // la URL, y "Cerrar sesión" no redirigía a ningún lado.
  it("shows no navigation links or session controls when there is no session", async () => {
    stubFetch();

    renderTopBar();
    await waitFor(() =>
      expect(screen.getByTestId("backend-status")).toHaveTextContent(
        "Backend conectado",
      ),
    );
    expect(screen.queryByTestId("user-email")).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Nuevo análisis" })).not.toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Historial" })).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Cerrar sesión" }),
    ).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Salir" })).not.toBeInTheDocument();
  });

  it("shows the user's email, Nuevo análisis, Historial and a logout button when authenticated", async () => {
    stubFetch({
      ok: true,
      body: { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true },
    });

    renderTopBar();
    await waitFor(() =>
      expect(screen.getByTestId("user-email")).toHaveTextContent("a@ucc.edu.ar"),
    );
    expect(screen.getByRole("link", { name: "Nuevo análisis" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Historial" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Cerrar sesión" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Salir" })).not.toBeInTheDocument();
  });

  // F6: "Cerrar sesión" antes borraba la cookie y el estado pero no
  // redirigía — el usuario se quedaba en la misma pantalla, sin ninguna
  // señal visible de que algo pasó.
  it("navigates to / after clicking Cerrar sesión", async () => {
    stubFetch({
      ok: true,
      body: { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true },
    });

    renderTopBar();
    await waitFor(() =>
      expect(screen.getByTestId("user-email")).toHaveTextContent("a@ucc.edu.ar"),
    );

    fireEvent.click(screen.getByRole("button", { name: "Cerrar sesión" }));

    expect(await screen.findByText("entry screen")).toBeInTheDocument();
  });

  it("shows Nuevo análisis and Salir (not Historial/Cerrar sesión) for an anonymous session", async () => {
    localStorage.setItem("metis-anon-session", "true");
    stubFetch();

    renderTopBar();
    await waitFor(() =>
      expect(screen.getByTestId("backend-status")).toHaveTextContent(
        "Backend conectado",
      ),
    );
    expect(screen.getByRole("link", { name: "Nuevo análisis" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Salir" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Historial" })).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Cerrar sesión" }),
    ).not.toBeInTheDocument();
  });

  // F4/F6: un anónimo no tenía forma de "salir" y volver a la puerta de
  // entrada — el flag metis-anon-session solo se limpiaba desde logout().
  it("navigates to / and clears the anonymous flag after clicking Salir", async () => {
    localStorage.setItem("metis-anon-session", "true");
    stubFetch();

    renderTopBar();
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Salir" })).toBeInTheDocument(),
    );

    fireEvent.click(screen.getByRole("button", { name: "Salir" }));

    expect(await screen.findByText("entry screen")).toBeInTheDocument();
    expect(localStorage.getItem("metis-anon-session")).toBeNull();
  });
});
