import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { AuthVerifyPage } from "./AuthVerifyPage";

function renderAt(path: string) {
  return render(
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
    await waitFor(() =>
      expect(
        screen.getByText("Cuenta verificada. Ya podés iniciar sesión."),
      ).toBeInTheDocument(),
    );
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

    await waitFor(() =>
      expect(
        screen.getByText("El link de verificación es inválido o expiró."),
      ).toBeInTheDocument(),
    );
  });
});
