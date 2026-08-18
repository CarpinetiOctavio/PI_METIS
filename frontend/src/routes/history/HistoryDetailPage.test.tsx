import { afterEach, describe, expect, it, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { renderPage } from "../../test/renderPage";
import { HistoryDetailPage } from "./HistoryDetailPage";
import type { AnalysisDetail, Etapa2Result } from "../../api/types";

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

// Bloque C3 — a diferencia de stubFetch (una sola respuesta para todas las
// llamadas), estos tests disparan un segundo fetch (POST design-events) al
// explorar una distribución. Ruteado por URL/método en vez de posicional
// (mockResolvedValueOnce encadenado) a propósito: bajo StrictMode
// (renderPage envuelve todo en él) el efecto de carga de GET /history/{id}
// corre dos veces al montar — un mock posicional consumiría un slot con la
// llamada descartada y desalinearía el resto.
function stubFetchRouted(
  routes: Array<{
    match: (url: string, init?: RequestInit) => boolean;
    status: number;
    body: unknown;
  }>,
) {
  const fn = vi.fn((url: string, init?: RequestInit) => {
    const route = routes.find((r) => r.match(String(url), init));
    if (!route) {
      throw new Error(`stubFetchRouted: sin ruta para ${init?.method ?? "GET"} ${url}`);
    }
    return Promise.resolve({
      ok: route.status < 400,
      status: route.status,
      json: () => Promise.resolve(route.body),
    });
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

function makeEtapa2(overrides: Partial<Etapa2Result> = {}): Etapa2Result {
  return {
    ranking: [
      {
        distribucion: "gumbel",
        n_parametros: 2,
        metodos: [
          { metodo: "momentos", parametros: { mu: 100, alpha: 20 }, eea: 12.5, status: "ok" },
        ],
        mejor_eea: 12.5,
        mejor_metodo: "momentos",
      },
      {
        distribucion: "gve",
        n_parametros: 3,
        metodos: [
          { metodo: "ml", parametros: { nu: 90, alpha: 18, beta: 0.1 }, eea: 15.2, status: "ok" },
        ],
        mejor_eea: 15.2,
        mejor_metodo: "ml",
      },
    ],
    warnings: [],
    puntos_empiricos: [{ valor: 142.5, periodo_retorno: 41, probabilidad: 0.9756 }],
    seleccion: null,
    ...overrides,
  };
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

  // Bloque C3 (plan post-avance) — historial interactivo de Etapa 2.

  it("C3 — muestra la elección registrada con distribución, método y períodos de retorno", async () => {
    stubFetch(
      200,
      makeDetail({
        etapa2: makeEtapa2({
          seleccion: {
            distribucion: "gumbel",
            metodo: "momentos",
            periodos_retorno: [2, 10, 100],
            eventos_diseno: [{ periodo_retorno: 2, valor: 138.4 }],
            curva_ajuste: [{ periodo_retorno: 1.05, valor: 61.2 }],
          },
        }),
      }),
    );
    renderDetail();

    expect(await screen.findByText("Elección registrada")).toBeInTheDocument();
    expect(screen.getByText(/gumbel · momentos · períodos de retorno: 2, 10, 100/)).toBeInTheDocument();
  });

  it("C3 — muestra un banner de estado vacío cuando etapa2 no tiene ninguna elección registrada", async () => {
    stubFetch(200, makeDetail({ etapa2: makeEtapa2({ seleccion: null }) }));
    renderDetail();

    expect(
      await screen.findByText(/no quedó registrada ninguna distribución elegida/),
    ).toBeInTheDocument();
    expect(screen.queryByText("Elección registrada")).not.toBeInTheDocument();
  });

  it("C3 — explorar otra distribución llama al endpoint de recálculo y muestra el resultado marcado como exploración", async () => {
    const user = userEvent.setup();
    const detailBody = makeDetail({
      etapa2: makeEtapa2({
        seleccion: {
          distribucion: "gumbel",
          metodo: "momentos",
          periodos_retorno: [2, 10, 100],
          eventos_diseno: [{ periodo_retorno: 2, valor: 138.4 }],
          curva_ajuste: [{ periodo_retorno: 1.05, valor: 61.2 }],
        },
      }),
    });
    const fetchMock = stubFetchRouted([
      {
        match: (url, init) => !init?.method && url.includes("/history/"),
        status: 200,
        body: detailBody,
      },
      {
        match: (url, init) => init?.method === "POST" && url.includes("/design-events"),
        status: 200,
        body: {
          eventos_diseno: [{ periodo_retorno: 2, valor: 108.4 }],
          curva_ajuste: [{ periodo_retorno: 1.05, valor: 55.0 }],
        },
      },
    ]);
    renderDetail();

    await screen.findByText("Elección registrada");
    // "gve" es la otra distribución del ranking, distinta de la elegida.
    const botonesExplorar = await screen.findAllByRole("button", {
      name: "Explorar este ajuste",
    });
    await user.click(botonesExplorar[1]);

    expect(await screen.findByText(/No es la elección registrada/)).toBeInTheDocument();
    expect(screen.getByText(/Exploración/)).toBeInTheDocument();

    // La llamada de recálculo pegó a design-events, no a distribution-decision.
    const llamadaRecalculo = fetchMock.mock.calls.find(
      ([, init]) => init?.method === "POST",
    );
    expect(String(llamadaRecalculo?.[0])).toContain("/analysis/an-1/design-events");

    // La elección registrada sigue mostrando gumbel/momentos — explorar no la cambió.
    expect(screen.getByText(/gumbel · momentos · períodos de retorno: 2, 10, 100/)).toBeInTheDocument();
  });

  it("C3 — muestra un error legible si el recálculo falla", async () => {
    const user = userEvent.setup();
    stubFetchRouted([
      {
        match: (url, init) => !init?.method && url.includes("/history/"),
        status: 200,
        body: makeDetail({ etapa2: makeEtapa2({ seleccion: null }) }),
      },
      {
        match: (url, init) => init?.method === "POST" && url.includes("/design-events"),
        status: 400,
        body: {
          error: {
            codigo: "DIST_METHOD_NOT_FITTED",
            mensaje: "Esa combinación no tiene parámetros ajustados.",
          },
        },
      },
    ]);
    renderDetail();

    const boton = await screen.findAllByRole("button", { name: "Explorar este ajuste" });
    await user.click(boton[0]);

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent(
        /no tiene parámetros ajustados/,
      ),
    );
  });
});
