import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "../../auth/AuthProvider";
import { EntryPage } from "./EntryPage";

function stubFetch(
  map: Record<string, { ok: boolean; status?: number; body: unknown }>,
) {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = typeof input === "string" ? input : input.toString();
      const match = Object.entries(map).find(([key]) => url.includes(key));
      if (!match) throw new Error(`unstubbed fetch: ${url}`);
      const [, res] = match;
      return Promise.resolve({
        ok: res.ok,
        status: res.status ?? (res.ok ? 200 : 400),
        json: () => Promise.resolve(res.body),
      });
    }),
  );
}

function renderEntryPage() {
  return render(
    <MemoryRouter initialEntries={["/"]}>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<EntryPage />} />
          <Route path="/config" element={<div>config screen</div>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe("EntryPage", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("shows the login form by default and toggles to register and back", async () => {
    stubFetch({ "/auth/me": { ok: false, status: 401, body: {} } });
    renderEntryPage();

    expect(
      await screen.findByRole("heading", { name: "Iniciar sesión" }),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Registrate" }));
    expect(
      screen.getByRole("heading", { name: "Crear cuenta" }),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Iniciá sesión" }));
    expect(
      screen.getByRole("heading", { name: "Iniciar sesión" }),
    ).toBeInTheDocument();
  });

  it("shows a legible error banner when login fails with invalid credentials", async () => {
    stubFetch({
      "/auth/me": { ok: false, status: 401, body: {} },
      "/auth/login": {
        ok: false,
        status: 401,
        body: { error: { codigo: "AUTH_INVALID_CREDENTIALS", mensaje: "..." } },
      },
    });
    renderEntryPage();
    expect(
      await screen.findByRole("heading", { name: "Iniciar sesión" }),
    ).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Email institucional"), {
      target: { value: "a@ucc.edu.ar" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "wrongpass" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ingresar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Email o contraseña incorrectos.",
    );
  });

  // F3 (informe-diagnostico-ui-rota.md): antes, si POST /auth/login
  // respondía 200 pero el GET /auth/me posterior no confirmaba la sesión
  // (acá /me devuelve 401 tanto antes como después del login — nunca hay
  // sesión real), login() resolvía igual sin lanzar. Desde la UI eso se veía
  // como "aprieto Ingresar y no pasa nada": sin banner, sin redirect, sin
  // pista de qué falló. Ahora un banner explícito.
  it("shows a legible error banner when login succeeds but the session can't be confirmed", async () => {
    stubFetch({
      "/auth/me": { ok: false, status: 401, body: {} },
      "/auth/login": { ok: true, status: 200, body: { ok: true } },
    });
    renderEntryPage();
    expect(
      await screen.findByRole("heading", { name: "Iniciar sesión" }),
    ).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Email institucional"), {
      target: { value: "a@ucc.edu.ar" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "correctpass" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ingresar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "El login fue aceptado pero no se pudo abrir la sesión. Revisá la conexión con el backend.",
    );
    // No quedó "colgado": el botón sigue siendo clickeable, no en isSubmitting.
    expect(screen.getByRole("button", { name: "Ingresar" })).toBeEnabled();
  });

  it("shows the success message after a successful registration", async () => {
    stubFetch({
      "/auth/me": { ok: false, status: 401, body: {} },
      "/auth/register": {
        ok: true,
        body: { ok: true, mensaje: "Cuenta creada. Revisá tu mail." },
      },
    });
    renderEntryPage();
    expect(
      await screen.findByRole("heading", { name: "Iniciar sesión" }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Registrate" }));

    fireEvent.change(screen.getByLabelText("Email institucional"), {
      target: { value: "a@ucc.edu.ar" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "12345678" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Crear cuenta" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Cuenta creada. Revisá tu mail.",
    );
  });

  it("shows a dev-specific banner (not the generic error) when register fails with AUTH_VERIFICATION_EMAIL_FAILED", async () => {
    stubFetch({
      "/auth/me": { ok: false, status: 401, body: {} },
      "/auth/register": {
        ok: false,
        status: 500,
        body: {
          error: { codigo: "AUTH_VERIFICATION_EMAIL_FAILED", mensaje: "..." },
        },
      },
    });
    renderEntryPage();
    expect(
      await screen.findByRole("heading", { name: "Iniciar sesión" }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Registrate" }));
    fireEvent.change(screen.getByLabelText("Email institucional"), {
      target: { value: "a@ucc.edu.ar" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "12345678" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Crear cuenta" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Modo dev: no hay SMTP configurado",
    );
  });

  it("enters anonymously, navigates to /config and persists the flag", async () => {
    stubFetch({ "/auth/me": { ok: false, status: 401, body: {} } });
    renderEntryPage();
    expect(
      await screen.findByRole("heading", { name: "Iniciar sesión" }),
    ).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Entrar como anónimo/ }));

    expect(await screen.findByText("config screen")).toBeInTheDocument();
    expect(localStorage.getItem("metis-anon-session")).toBe("true");
  });
});
