import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import type { ReactNode } from "react";
import { AuthProvider } from "./AuthProvider";
import { RedirectIfAuthed, RequireAuth } from "./guards";

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
  return render(
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
    await waitFor(() => expect(screen.getByText("secret")).toBeInTheDocument());
  });

  it("redirects to / when not authenticated", async () => {
    stubMe(false);
    renderAt(
      "/protected",
      <RequireAuth>
        <div>secret</div>
      </RequireAuth>,
    );
    await waitFor(() => expect(screen.getByText("entry")).toBeInTheDocument());
  });

  it("renders children when authenticated", async () => {
    stubMe(true, { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true });
    renderAt(
      "/protected",
      <RequireAuth>
        <div>secret</div>
      </RequireAuth>,
    );
    await waitFor(() => expect(screen.getByText("secret")).toBeInTheDocument());
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
    await waitFor(() => expect(screen.getByText("public")).toBeInTheDocument());
  });

  it("redirects to /config when authenticated", async () => {
    stubMe(true, { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true });
    renderAt(
      "/protected",
      <RedirectIfAuthed>
        <div>public</div>
      </RedirectIfAuthed>,
    );
    await waitFor(() => expect(screen.getByText("config")).toBeInTheDocument());
  });
});
