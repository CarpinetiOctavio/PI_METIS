import { afterEach, describe, expect, it, vi } from "vitest";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { renderPage } from "../../test/renderPage";
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

/** Enruta por URL — necesario para los tests que ejercitan archive/unarchive
 * además del listado inicial (mismo patrón que ConfigPage.test.tsx). */
function stubFetchRouted({
  activos,
  archivados = [],
}: {
  activos: HistoryItem[];
  archivados?: HistoryItem[];
}) {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.includes("/history/") && url.includes("archivados=true")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(archivados),
        });
      }
      if (url.match(/\/history\/[^/]+\/archive$/)) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ ok: true }),
        });
      }
      if (url.match(/\/history\/[^/]+\/unarchive$/)) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ ok: true }),
        });
      }
      if (url.endsWith("/history/") && (!init || init.method === undefined)) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(activos),
        });
      }
      return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({}) });
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
    archivado_at: null,
    nombre_archivo: null,
    serie_preview: [],
  }));
}

function renderHistoryPage() {
  return renderPage(
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

  // ── DECISIÓN 048 — archivado ────────────────────────────────────────────

  it("archives an item after confirmation, removing it from the active list", async () => {
    stubFetchRouted({ activos: makeItems(1) });
    renderHistoryPage();

    await screen.findByRole("link");
    fireEvent.click(screen.getByRole("button", { name: "Archivar" }));
    fireEvent.click(await screen.findByRole("button", { name: "Sí, archivar" }));

    await waitFor(() =>
      expect(screen.getByText("Todavía no tenés análisis guardados.")).toBeInTheDocument(),
    );
    expect(await screen.findByRole("status")).toHaveTextContent("Análisis archivado.");
  });

  it("cancelling the confirmation keeps the item in the list", async () => {
    stubFetchRouted({ activos: makeItems(1) });
    renderHistoryPage();

    await screen.findByRole("link");
    fireEvent.click(screen.getByRole("button", { name: "Archivar" }));
    fireEvent.click(await screen.findByRole("button", { name: "Cancelar" }));

    expect(screen.getByRole("link")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Archivar" })).toBeInTheDocument();
  });

  it("undo re-adds the item to the active list", async () => {
    stubFetchRouted({ activos: makeItems(1) });
    renderHistoryPage();

    await screen.findByRole("link");
    fireEvent.click(screen.getByRole("button", { name: "Archivar" }));
    fireEvent.click(await screen.findByRole("button", { name: "Sí, archivar" }));
    await screen.findByRole("status");

    fireEvent.click(screen.getByRole("button", { name: "Deshacer" }));

    expect(await screen.findByRole("link")).toHaveAttribute("href", "/history/id-0");
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });

  it("toggling 'Ver archivados' fetches and lists archived items with an unarchive action", async () => {
    const archivado = makeItems(1).map((i) => ({ ...i, archivado_at: "2026-07-31T00:00:00" }));
    stubFetchRouted({ activos: [], archivados: archivado });
    renderHistoryPage();

    await screen.findByText("Todavía no tenés análisis guardados.");
    fireEvent.click(screen.getByRole("button", { name: "Ver archivados" }));

    expect(await screen.findByRole("link")).toHaveAttribute("href", "/history/id-0");
    expect(screen.getByRole("button", { name: "Desarchivar" })).toBeInTheDocument();
  });

  // ── F7a/F7b (plan de fixes pre-reunión) ─────────────────────────────────

  it("F7a — muestra el nombre de archivo como título y el tipo de variable en los metadatos", async () => {
    const items = makeItems(1).map((i) => ({ ...i, nombre_archivo: "estacion_04.csv" }));
    stubFetch(200, items);
    renderHistoryPage();

    expect(await screen.findByText("estacion_04.csv")).toBeInTheDocument();
    expect(screen.getByText(/Tipo: caudal_precipitacion/)).toBeInTheDocument();
  });

  it("F7a — degrada al tipo de variable como título cuando nombre_archivo es null (análisis viejo)", async () => {
    stubFetch(200, makeItems(1)); // nombre_archivo: null por default en makeItems
    renderHistoryPage();

    expect(await screen.findByText("caudal_precipitacion")).toBeInTheDocument();
  });

  it("F7b — renderiza una sparkline cuando el item trae serie_preview", async () => {
    const items = makeItems(1).map((i) => ({ ...i, serie_preview: [94.71, 89.83, 105.13] }));
    stubFetch(200, items);
    const { container } = renderHistoryPage();

    await screen.findByRole("link");
    expect(container.querySelector(".sparkline")).toBeInTheDocument();
  });

  it("F7b — no renderiza la sparkline cuando serie_preview está vacía", async () => {
    stubFetch(200, makeItems(1)); // serie_preview: [] por default en makeItems
    const { container } = renderHistoryPage();

    await screen.findByRole("link");
    expect(container.querySelector(".sparkline")).not.toBeInTheDocument();
  });
});
