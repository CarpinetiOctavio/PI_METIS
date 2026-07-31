import { afterEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { renderPage } from "../../test/renderPage";
import { AuthVerifyPage } from "./AuthVerifyPage";

function renderAt(path: string) {
  return renderPage(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/auth/verify" element={<AuthVerifyPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("AuthVerifyPage", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("shows an error immediately when there is no token in the URL", () => {
    renderAt("/auth/verify");
    expect(
      screen.getByText("Falta el token de verificación en el link."),
    ).toBeInTheDocument();
  });

  it("calls verify and shows success when the token is valid", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ ok: true }),
      }),
    );
    renderAt("/auth/verify?token=abc123");

    expect(screen.getByText("Verificando cuenta…")).toBeInTheDocument();
    expect(
      await screen.findByText("Cuenta verificada. Ya podés iniciar sesión."),
    ).toBeInTheDocument();
  });

  it("shows a legible error when the token is invalid", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: () =>
          Promise.resolve({
            error: { codigo: "AUTH_INVALID_TOKEN", mensaje: "..." },
          }),
      }),
    );
    renderAt("/auth/verify?token=bad");

    expect(
      await screen.findByText("El link de verificación es inválido o expiró."),
    ).toBeInTheDocument();
  });
});
