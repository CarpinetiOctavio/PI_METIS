import { afterEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { renderPage } from "../../test/renderPage";
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
    serie: null,
    timestamps: null,
    configuracion: null,
    ...overrides,
  };
}

function renderDetail(id = "an-1") {
  return renderPage(
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
    expect(await screen.findByText("validado")).toBeInTheDocument();
  });

  it("shows a legible error banner on failure", async () => {
    stubFetch(404, { error: { codigo: "AUTH_USER_NOT_FOUND", mensaje: "..." } });
    renderDetail();

    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });

  it("shows a warning when the analysis has no etapa1 recorded", async () => {
    stubFetch(200, makeDetail({ etapa1: null }));
    renderDetail();

    expect(
      await screen.findByText(
        "Este análisis no tiene resultados de Etapa 1 registrados.",
      ),
    ).toBeInTheDocument();
  });

  // PR 5 del plan de cierre de pendientes no-test (DECISIÓN 058 §4) —
  // timestamps=null es la señal de que este registro es anterior a la
  // migración 005, sin backfill posible.
  it("shows an explicit empty-state banner for an analysis persisted before the migration (timestamps=null)", async () => {
    stubFetch(200, makeDetail({ timestamps: null }));
    renderDetail();

    expect(
      await screen.findByText(/anterior a esta versión de METIS/),
    ).toBeInTheDocument();
  });

  it("does not show the empty-state banner once the analysis has real timestamps", async () => {
    stubFetch(
      200,
      makeDetail({ timestamps: [{ iso: "2000-01-01", anio: 2000 }] }),
    );
    renderDetail();

    await screen.findByText("validado");
    expect(
      screen.queryByText(/anterior a esta versión de METIS/),
    ).not.toBeInTheDocument();
  });

  it("passes mes_inicio_anio from configuracion through to the criterio de año note", async () => {
    stubFetch(
      200,
      makeDetail({
        configuracion: { cramer_particion: "default", mes_inicio_anio: 7 },
        etapa1: {
          contract: { bloqueante: false, codigo_error: null, warnings: [] },
          descriptive: {
            n: 10,
            media: 1,
            mediana: 1,
            desvio_estandar: 1,
            coef_variacion: 1,
            coef_asimetria: 1,
            minimo: 1,
            maximo: 1,
          },
          independencia: [],
          homogeneidad: [],
          tendencia: [],
          atipicos: [],
          nivel_independencia: "independiente",
          nivel_homogeneidad: "homogeneidad_ok",
          nivel_confianza: "validado",
          warnings: [],
        },
      }),
    );
    renderDetail();

    expect(await screen.findByText(/Criterio de año: julio/)).toBeInTheDocument();
  });
});
