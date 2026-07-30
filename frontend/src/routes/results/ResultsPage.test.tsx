import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "../../auth/AuthProvider";
import { ResultsPage } from "./ResultsPage";
import type { Etapa1Result, Modo, TestResultDetail } from "../../api/types";

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
) {
  if (authed) {
    stubMe(true, { id: "1", email: "a@ucc.edu.ar", nombre: null, email_verified: true });
  } else {
    stubMe(false);
  }

  return render(
    <MemoryRouter
      initialEntries={[
        result
          ? { pathname: "/results", state: { result, analysisId: "an-1", modo } }
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
    await waitFor(() => expect(screen.getByText("config screen")).toBeInTheDocument());
  });

  it("shows the nivel_confianza banner and the independencia/homogeneidad KPIs", async () => {
    renderResultsPage(true, makeResult(), "experto");
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Resultados de Etapa 1" })).toBeInTheDocument(),
    );

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

    await waitFor(() => expect(screen.getByText("Se detectó tendencia.")).toBeInTheDocument());
  });

  it("renders test groups as collapsed <details> accordions in docencia + paso_a_paso", async () => {
    const { container } = renderResultsPage(true, makeResult(), "paso_a_paso");
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Resultados de Etapa 1" })).toBeInTheDocument(),
    );

    const detailsElements = container.querySelectorAll("details.results-group");
    expect(detailsElements).toHaveLength(4);
    detailsElements.forEach((el) => expect(el).not.toHaveAttribute("open"));
  });

  it("renders test groups as flat cards (no accordion) in docencia + experto", async () => {
    const { container } = renderResultsPage(true, makeResult(), "experto");
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Resultados de Etapa 1" })).toBeInTheDocument(),
    );

    expect(container.querySelectorAll("details")).toHaveLength(0);
  });

  it("forces the flat (experto) presentation for anonymous sessions even if modo says otherwise", async () => {
    const { container } = renderResultsPage(false, makeResult(), "paso_a_paso");
    await waitFor(() =>
      expect(screen.getByRole("heading", { name: "Resultados de Etapa 1" })).toBeInTheDocument(),
    );

    expect(container.querySelectorAll("details")).toHaveLength(0);
  });
});
