import { afterEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "../../auth/AuthProvider";
import { renderPage } from "../../test/renderPage";
import { ResultsPage } from "./ResultsPage";
import type { Etapa1Result, Etapa2Result, Modo, TestResultDetail } from "../../api/types";
import type { Etapa2EventosState, Etapa2RankingState } from "../../api/sse";

function testResult(overrides: Partial<TestResultDetail> = {}): TestResultDetail {
  return {
    prueba: "anderson",
    estadistico: 0.23,
    valor_critico: 0.37,
    veredicto: "aprobada",
    warning_codigo: null,
    warning_nivel: null,
    n1: null,
    n2: null,
    valor_atipico: null,
    indice_atipico: null,
    explicacion: null,
    ...overrides,
  };
}

function makeResult(overrides: Partial<Etapa1Result> = {}): Etapa1Result {
  return {
    contract: { bloqueante: false, codigo_error: null, warnings: [] },
    descriptive: {
      n: 40,
      media: 142.5,
      mediana: 138.2,
      desvio_estandar: 38.1,
      coef_variacion: 0.267,
      coef_asimetria: 0.84,
      minimo: 72.3,
      maximo: 312.7,
    },
    independencia: [testResult({ prueba: "anderson" }), testResult({ prueba: "wald_wolfowitz" })],
    homogeneidad: [
      testResult({ prueba: "helmert" }),
      testResult({ prueba: "t_student", n1: 21, n2: 11 }),
      testResult({ prueba: "cramer", n1: 21, n2: 11 }),
    ],
    tendencia: [testResult({ prueba: "mann_kendall" }), testResult({ prueba: "kolmogorov_smirnov" })],
    atipicos: [testResult({ prueba: "chow", veredicto: "no_ejecutada" })],
    nivel_independencia: "independiente",
    nivel_homogeneidad: "homogeneidad_ok",
    nivel_confianza: "validado",
    warnings: [],
    ...overrides,
  };
}

function makeEtapa2Result(): Etapa2Result {
  return {
    ranking: [
      {
        distribucion: "gumbel",
        n_parametros: 2,
        metodos: [
          { metodo: "momentos", parametros: { mu: 100, alpha: 20 }, eea: 12.5, status: "ok" },
          { metodo: "mv", parametros: null, eea: null, status: "no_converge" },
        ],
        mejor_eea: 12.5,
        mejor_metodo: "momentos",
      },
    ],
    warnings: [],
    puntos_empiricos: [
      { valor: 142.5, periodo_retorno: 41, probabilidad: 0.9756 },
    ],
    seleccion: null,
  };
}

function stubMe(ok: boolean, body: unknown = {}) {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok,
      status: ok ? 200 : 401,
      json: () => Promise.resolve(body),
    }),
  );
}

function renderResultsPage(
  authed: boolean,
  result: Etapa1Result | undefined,
  modo?: Modo,
  extra?: {
    etapa2?: Etapa2RankingState;
    eventosDiseno?: Etapa2EventosState;
    mesInicioAnio?: number;
  },
) {
  if (authed) {
    stubMe(true, { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true });
  } else {
    stubMe(false);
  }

  return renderPage(
    <MemoryRouter
      initialEntries={[
        result
          ? {
              pathname: "/results",
              state: { result, analysisId: "an-1", modo, ...extra },
            }
          : { pathname: "/results" },
      ]}
    >
      <AuthProvider>
        <Routes>
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/config" element={<div>config screen</div>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe("ResultsPage", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("redirects to /config when there is no result in location.state", async () => {
    renderResultsPage(true, undefined);
    expect(await screen.findByText("config screen")).toBeInTheDocument();
  });

  it("shows the nivel_confianza banner and the independencia/homogeneidad KPIs", async () => {
    renderResultsPage(true, makeResult(), "experto");
    expect(
      await screen.findByRole("heading", { name: "Resultados de Etapa 1" }),
    ).toBeInTheDocument();

    expect(screen.getByText("validado")).toBeInTheDocument();
    expect(screen.getByText("independiente")).toBeInTheDocument();
    expect(screen.getByText("ok")).toBeInTheDocument();
  });

  it("shows warnings with their descripcion", async () => {
    renderResultsPage(
      true,
      makeResult({
        nivel_confianza: "con_warnings",
        warnings: [
          { codigo: "TEST_WARNING_TREND", nivel: "normal", descripcion: "Se detectó tendencia." },
        ],
      }),
      "experto",
    );

    expect(
      await screen.findByText("Se detectó tendencia."),
    ).toBeInTheDocument();
  });

  it("renders test groups as collapsed <details> accordions in docencia + paso_a_paso", async () => {
    const { container } = renderResultsPage(true, makeResult(), "paso_a_paso");
    expect(
      await screen.findByRole("heading", { name: "Resultados de Etapa 1" }),
    ).toBeInTheDocument();

    const detailsElements = container.querySelectorAll("details.results-group");
    expect(detailsElements).toHaveLength(4);
    detailsElements.forEach((el) => expect(el).not.toHaveAttribute("open"));
  });

  it("renders test groups as flat cards (no accordion) in docencia + experto", async () => {
    const { container } = renderResultsPage(true, makeResult(), "experto");
    expect(
      await screen.findByRole("heading", { name: "Resultados de Etapa 1" }),
    ).toBeInTheDocument();

    expect(container.querySelectorAll("details")).toHaveLength(0);
  });

  it("forces the flat (experto) presentation for anonymous sessions even if modo says otherwise", async () => {
    const { container } = renderResultsPage(false, makeResult(), "paso_a_paso");
    expect(
      await screen.findByRole("heading", { name: "Resultados de Etapa 1" }),
    ).toBeInTheDocument();

    expect(container.querySelectorAll("details")).toHaveLength(0);
  });

  // Bloque B del plan de Etapa 2 — Etapa 2 ya no es una pantalla mock
  // aparte: corrió (si se pidió) dentro de StreamPage, y acá se muestra de
  // solo lectura si el router state la trae.
  it("does not show any Etapa 2 section when the stream only ran Etapa 1", async () => {
    renderResultsPage(true, makeResult(), "experto");
    expect(
      await screen.findByRole("heading", { name: "Resultados de Etapa 1" }),
    ).toBeInTheDocument();

    expect(screen.queryByText("Ranking de distribuciones")).not.toBeInTheDocument();
    expect(screen.queryByText("Evento de diseño")).not.toBeInTheDocument();
  });

  it("shows the Etapa 2 ranking (read-only, no 'Elegir') when the router state carries it", async () => {
    renderResultsPage(true, makeResult(), "experto", {
      etapa2: { session_id: "s1", ...makeEtapa2Result() },
    });

    expect(
      await screen.findByRole("heading", { name: "Ranking de distribuciones" }),
    ).toBeInTheDocument();
    expect(screen.getByText("gumbel")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Elegir" })).not.toBeInTheDocument();
  });

  // Bloque F5 del plan de Etapa 2 (DECISIÓN 057).
  it("shows the criterio de año note when the router state carries mesInicioAnio", async () => {
    renderResultsPage(true, makeResult(), "experto", { mesInicioAnio: 9 });
    expect(
      await screen.findByRole("heading", { name: "Resultados de Etapa 1" }),
    ).toBeInTheDocument();

    expect(screen.getByText(/Criterio de año: septiembre/)).toBeInTheDocument();
  });

  it("does not show the criterio de año note when mesInicioAnio is absent", async () => {
    renderResultsPage(true, makeResult(), "experto");
    expect(
      await screen.findByRole("heading", { name: "Resultados de Etapa 1" }),
    ).toBeInTheDocument();

    expect(screen.queryByText(/Criterio de año/)).not.toBeInTheDocument();
  });

  it("shows the design events view when the router state carries eventosDiseno", async () => {
    renderResultsPage(true, makeResult(), "experto", {
      eventosDiseno: {
        distribucion: "gumbel",
        metodo: "momentos",
        eventos_diseno: [{ periodo_retorno: 100, valor: 312.7 }],
        curva_ajuste: [{ periodo_retorno: 100, valor: 312.7 }],
      },
    });

    expect(
      await screen.findByRole("heading", { name: "Evento de diseño" }),
    ).toBeInTheDocument();
  });
});
