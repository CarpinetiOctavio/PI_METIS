import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { HistoryDetailPage } from "./HistoryDetailPage";
import type { AnalysisDetail } from "../../api/types";

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

function makeDetail(overrides: Partial<AnalysisDetail> = {}): AnalysisDetail {
  return {
    id: "an-1",
    tipo_variable: "caudal_precipitacion",
    modo: "experto",
    etapas: ["1"],
    created_at: "2026-01-15T00:00:00Z",
    etapa1: {
      contract: { bloqueante: false, codigo_error: null, warnings: [] },
      descriptive: null,
      independencia: [],
      homogeneidad: [],
      tendencia: [],
      atipicos: [],
      nivel_independencia: "independiente",
      nivel_homogeneidad: "homogeneidad_ok",
      nivel_confianza: "validado",
      warnings: [],
    },
    etapa2: null,
    ...overrides,
  };
}

function renderDetail(id = "an-1") {
  return render(
    <MemoryRouter initialEntries={[`/history/${id}`]}>
      <Routes>
        <Route path="/history/:id" element={<HistoryDetailPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("HistoryDetailPage", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("shows a loading state, then the analysis result", async () => {
    stubFetch(200, makeDetail());
    renderDetail();

    expect(screen.getByText("Cargando análisis…")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("validado")).toBeInTheDocument());
  });

  it("shows a legible error banner on failure", async () => {
    stubFetch(404, { error: { codigo: "AUTH_USER_NOT_FOUND", mensaje: "..." } });
    renderDetail();

    await waitFor(() => expect(screen.getByRole("alert")).toBeInTheDocument());
  });

  it("shows a warning when the analysis has no etapa1 recorded", async () => {
    stubFetch(200, makeDetail({ etapa1: null }));
    renderDetail();

    await waitFor(() =>
      expect(
        screen.getByText(
          "Este análisis no tiene resultados de Etapa 1 registrados.",
        ),
      ).toBeInTheDocument(),
    );
  });
});
