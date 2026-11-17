import { afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { renderPage } from "../../test/renderPage";
import { ResetPasswordPage } from "./ResetPasswordPage";

function stubFetch(res: { ok: boolean; status?: number; body: unknown }) {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: res.ok,
    status: res.status ?? (res.ok ? 200 : 400),
    json: () => Promise.resolve(res.body),
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function renderAt(path: string) {
  return renderPage(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/auth/reset-password" element={<ResetPasswordPage />} />
        <Route path="/auth/forgot-password" element={<div>forgot screen</div>} />
        <Route path="/" element={<div>entry screen</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

function completar(password: string, confirmacion: string) {
  fireEvent.change(screen.getByLabelText("Contraseña nueva"), {
    target: { value: password },
  });
  fireEvent.change(screen.getByLabelText("Repetí la contraseña"), {
    target: { value: confirmacion },
  });
  fireEvent.click(screen.getByRole("button", { name: "Guardar contraseña" }));
}

describe("ResetPasswordPage", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("explains the problem and offers a new link when the URL has no token", () => {
    renderAt("/auth/reset-password");

    expect(screen.getByText(/Falta el token en el link/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("link", { name: "Pedir un link nuevo" }));
    expect(screen.getByText("forgot screen")).toBeInTheDocument();
  });

  it("rejects a short password without calling the backend", () => {
    const fetchMock = stubFetch({ ok: true, body: { ok: true } });
    renderAt("/auth/reset-password?token=abc");

    completar("corta", "corta");

    expect(
      screen.getByText("La contraseña debe tener al menos 8 caracteres."),
    ).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("rejects mismatched passwords without calling the backend", () => {
    const fetchMock = stubFetch({ ok: true, body: { ok: true } });
    renderAt("/auth/reset-password?token=abc");

    completar("clave-nueva-1", "clave-nueva-2");

    expect(screen.getByText("Las contraseñas no coinciden.")).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("sends token and password and confirms the change", async () => {
    const fetchMock = stubFetch({ ok: true, body: { ok: true } });
    renderAt("/auth/reset-password?token=abc");

    completar("clave-nueva-1", "clave-nueva-1");

    expect(
      await screen.findByText(/Contraseña actualizada/),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/reset-password",
      expect.objectContaining({
        body: JSON.stringify({ token: "abc", password: "clave-nueva-1" }),
      }),
    );
    expect(screen.queryByLabelText("Contraseña nueva")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("link", { name: "Ir a la puerta de entrada" }));
    expect(screen.getByText("entry screen")).toBeInTheDocument();
  });

  it("shows a legible error when the token is invalid, expired or already used", async () => {
    stubFetch({
      ok: false,
      status: 400,
      body: { error: { codigo: "AUTH_RESET_TOKEN_INVALID", mensaje: "..." } },
    });
    renderAt("/auth/reset-password?token=vencido");

    completar("clave-nueva-1", "clave-nueva-1");

    expect(
      await screen.findByText(
        "El link para restablecer la contraseña es inválido, expiró o ya se usó.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Pedir un link nuevo" })).toBeInTheDocument();
  });
});
