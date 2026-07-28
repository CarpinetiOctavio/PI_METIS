import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
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

    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: "Iniciar sesión" }),
      ).toBeInTheDocument(),
    );

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
    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: "Iniciar sesión" }),
      ).toBeInTheDocument(),
    );

    fireEvent.change(screen.getByLabelText("Email institucional"), {
      target: { value: "a@ucc.edu.ar" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "wrongpass" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Ingresar" }));

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Email o contraseña incorrectos.",
      ),
    );
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
    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: "Iniciar sesión" }),
      ).toBeInTheDocument(),
    );
    fireEvent.click(screen.getByRole("button", { name: "Registrate" }));

    fireEvent.change(screen.getByLabelText("Email institucional"), {
      target: { value: "a@ucc.edu.ar" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "12345678" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Crear cuenta" }));

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Cuenta creada. Revisá tu mail.",
      ),
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
    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: "Iniciar sesión" }),
      ).toBeInTheDocument(),
    );
    fireEvent.click(screen.getByRole("button", { name: "Registrate" }));
    fireEvent.change(screen.getByLabelText("Email institucional"), {
      target: { value: "a@ucc.edu.ar" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "12345678" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Crear cuenta" }));

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Modo dev: no hay SMTP configurado",
      ),
    );
  });

  it("enters anonymously, navigates to /config and persists the flag", async () => {
    stubFetch({ "/auth/me": { ok: false, status: 401, body: {} } });
    renderEntryPage();
    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: "Iniciar sesión" }),
      ).toBeInTheDocument(),
    );

    fireEvent.click(screen.getByRole("button", { name: /Entrar como anónimo/ }));

    await waitFor(() =>
      expect(screen.getByText("config screen")).toBeInTheDocument(),
    );
    expect(localStorage.getItem("metis-anon-session")).toBe("true");
  });
});
