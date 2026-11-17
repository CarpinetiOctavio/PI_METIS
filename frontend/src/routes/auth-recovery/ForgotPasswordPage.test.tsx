import { afterEach, describe, expect, it, vi } from "vitest";
import { fireEvent, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { renderPage } from "../../test/renderPage";
import { ForgotPasswordPage } from "./ForgotPasswordPage";

function stubFetch(res: { ok: boolean; status?: number; body: unknown }) {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: res.ok,
    status: res.status ?? (res.ok ? 200 : 400),
    json: () => Promise.resolve(res.body),
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function renderForgot() {
  return renderPage(
    <MemoryRouter initialEntries={["/auth/forgot-password"]}>
      <Routes>
        <Route path="/auth/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/" element={<div>entry screen</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

function pedirLink(email: string) {
  fireEvent.change(screen.getByLabelText("Email institucional"), {
    target: { value: email },
  });
  fireEvent.click(screen.getByRole("button", { name: "Enviar link" }));
}

describe("ForgotPasswordPage", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("sends the email and shows the generic message from the backend", async () => {
    const fetchMock = stubFetch({
      ok: true,
      body: { ok: true, mensaje: "Si el email tiene una cuenta, te mandamos un link." },
    });
    renderForgot();

    pedirLink("a@ucc.edu.ar");

    expect(
      await screen.findByText("Si el email tiene una cuenta, te mandamos un link."),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/auth/forgot-password",
      expect.objectContaining({ body: JSON.stringify({ email: "a@ucc.edu.ar" }) }),
    );
    expect(screen.queryByRole("button", { name: "Enviar link" })).not.toBeInTheDocument();
  });

  it("shows a legible error and keeps the form when the request is invalid", async () => {
    stubFetch({
      ok: false,
      status: 422,
      body: { detail: [{ loc: ["body", "email"], msg: "no es un email", type: "value_error" }] },
    });
    renderForgot();

    pedirLink("esto-no-es-un-mail");

    expect(await screen.findByText("Revisá los datos ingresados.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Enviar link" })).toBeEnabled();
  });

  it("links back to the entry screen", () => {
    renderForgot();

    fireEvent.click(screen.getByRole("link", { name: "Volver a la puerta de entrada" }));

    expect(screen.getByText("entry screen")).toBeInTheDocument();
  });
});
