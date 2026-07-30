import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { HistoryPage } from "./HistoryPage";
import type { HistoryItem } from "../../api/types";

function stubFetch(status: number, body: unknown) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: status < 400,
      status,
      json: () => Promise.resolve(body),
    }),
  );
}

function makeItems(n: number): HistoryItem[] {
  return Array.from({ length: n }, (_, i) => ({
    id: `id-${i}`,
    tipo_variable: "caudal_precipitacion",
    modo: "experto",
    etapas: ["1"],
    created_at: new Date(2026, 0, i + 1).toISOString(),
  }));
}

function renderHistoryPage() {
  return render(
    <MemoryRouter initialEntries={["/history"]}>
      <Routes>
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/history/:id" element={<div>detail screen</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("HistoryPage", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("shows a loading state, then an empty message when there are no items", async () => {
    stubFetch(200, []);
    renderHistoryPage();

    expect(screen.getByText("Cargando historial…")).toBeInTheDocument();
    expect(
      await screen.findByText("Todavía no tenés análisis guardados."),
    ).toBeInTheDocument();
  });

  it("shows a legible error banner when the request fails", async () => {
    stubFetch(401, {
      error: { codigo: "AUTH_INVALID_CREDENTIALS", mensaje: "..." },
    });
    renderHistoryPage();

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Email o contraseña incorrectos.",
    );
  });

  it("renders items and paginates client-side (10 per page)", async () => {
    stubFetch(200, makeItems(15));
    renderHistoryPage();

    expect(await screen.findByText("Página 1 de 2")).toBeInTheDocument();
    expect(screen.getAllByRole("link")).toHaveLength(10);
    expect(screen.getByRole("button", { name: /Anterior/ })).toBeDisabled();

    fireEvent.click(screen.getByRole("button", { name: /Siguiente/ }));

    expect(screen.getByText("Página 2 de 2")).toBeInTheDocument();
    expect(screen.getAllByRole("link")).toHaveLength(5);
    expect(screen.getByRole("button", { name: /Siguiente/ })).toBeDisabled();
  });

  it("links each item to /history/:id", async () => {
    stubFetch(200, makeItems(1));
    renderHistoryPage();

    expect(await screen.findByRole("link")).toHaveAttribute(
      "href",
      "/history/id-0",
    );
  });
});
