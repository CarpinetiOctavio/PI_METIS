import { afterEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import type { ReactNode } from "react";
import { AuthProvider } from "./AuthProvider";
import { renderPage } from "../test/renderPage";
import { RedirectIfAuthed, RequireAuth, RequireSession } from "./guards";

function stubMe(ok: boolean, body: unknown = {}) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok,
      status: ok ? 200 : 401,
      json: () => Promise.resolve(body),
    }),
  );
}

function renderAt(path: string, protectedElement: ReactNode) {
  return renderPage(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<div>entry</div>} />
          <Route path="/config" element={<div>config</div>} />
          <Route path="/protected" element={protectedElement} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe("RequireAuth", () => {
  afterEach(() => vi.unstubAllGlobals());

  // D7 (pasada de mejora): antes devolvía null mientras isLoading —
  // pantalla completamente en blanco en cada carga de la app.
  it("shows a loading indicator instead of a blank screen while isLoading", async () => {
    stubMe(true, { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true });
    renderAt(
      "/protected",
      <RequireAuth>
        <div>secret</div>
      </RequireAuth>,
    );
    expect(screen.getByRole("status")).toBeInTheDocument();
    // Deja resolver el fetch de /me antes de que termine el test, para no
    // dejar un setState pendiente sin envolver en act().
    expect(await screen.findByText("secret")).toBeInTheDocument();
  });

  it("redirects to / when not authenticated", async () => {
    stubMe(false);
    renderAt(
      "/protected",
      <RequireAuth>
        <div>secret</div>
      </RequireAuth>,
    );
    expect(await screen.findByText("entry")).toBeInTheDocument();
  });

  it("renders children when authenticated", async () => {
    stubMe(true, { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true });
    renderAt(
      "/protected",
      <RequireAuth>
        <div>secret</div>
      </RequireAuth>,
    );
    expect(await screen.findByText("secret")).toBeInTheDocument();
  });
});

describe("RedirectIfAuthed", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("renders children when not authenticated", async () => {
    stubMe(false);
    renderAt(
      "/protected",
      <RedirectIfAuthed>
        <div>public</div>
      </RedirectIfAuthed>,
    );
    expect(await screen.findByText("public")).toBeInTheDocument();
  });

  it("redirects to /config when authenticated", async () => {
    stubMe(true, { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true });
    renderAt(
      "/protected",
      <RedirectIfAuthed>
        <div>public</div>
      </RedirectIfAuthed>,
    );
    expect(await screen.findByText("config")).toBeInTheDocument();
  });
});

// F7 (informe-diagnostico-ui-rota.md): /config, /stream, /results, /ranking
// y /design-events no tenían ningún guard — se podía entrar sin sesión de
// ningún tipo, tipeando la URL directo.
describe("RequireSession", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it("redirects to / when there is no session of any kind", async () => {
    stubMe(false);
    renderAt(
      "/protected",
      <RequireSession>
        <div>pipeline</div>
      </RequireSession>,
    );
    expect(await screen.findByText("entry")).toBeInTheDocument();
  });

  it("renders children for an anonymous session", async () => {
    localStorage.setItem("metis-anon-session", "true");
    stubMe(false);
    renderAt(
      "/protected",
      <RequireSession>
        <div>pipeline</div>
      </RequireSession>,
    );
    expect(await screen.findByText("pipeline")).toBeInTheDocument();
  });

  it("renders children for an authenticated session", async () => {
    stubMe(true, { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true });
    renderAt(
      "/protected",
      <RequireSession>
        <div>pipeline</div>
      </RequireSession>,
    );
    expect(await screen.findByText("pipeline")).toBeInTheDocument();
  });
});
