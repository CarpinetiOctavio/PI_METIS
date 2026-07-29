import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route, useLocation } from "react-router-dom";
import { StreamPage } from "./StreamPage";
import { useAnalysisStream, type StreamState } from "../../api/sse";
import type { AnalysisStreamForm, TestResultDetail } from "../../api/types";

vi.mock("../../api/sse", () => ({
  useAnalysisStream: vi.fn(),
}));

const mockedUseAnalysisStream = vi.mocked(useAnalysisStream);

function makeForm(): AnalysisStreamForm {
  return {
    archivo: new File(["1,100"], "serie.csv", { type: "text/csv" }),
    columna_x: "anio",
    columna_y: "caudal",
    tipo_variable: "caudal_precipitacion",
    modo: "experto",
    cramer_particion: "default",
  };
}

const BASE_STATE: StreamState = {
  fase: "streaming",
  contractWarnings: [],
  descriptive: null,
  tests: {},
  progress: { completado: 0, total: 8 },
  outlier: null,
  result: null,
  analysisId: null,
  error: null,
};

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

function ResultsProbe() {
  const location = useLocation();
  return <pre data-testid="results-state">{JSON.stringify(location.state)}</pre>;
}

function renderStreamPage(
  stateOverrides: Partial<StreamState> = {},
  { withForm = true }: { withForm?: boolean } = {},
) {
  const start = vi.fn();
  const resolveOutlier = vi.fn().mockResolvedValue(undefined);
  const abort = vi.fn();
  mockedUseAnalysisStream.mockReturnValue({
    start,
    state: { ...BASE_STATE, ...stateOverrides },
    resolveOutlier,
    abort,
  });

  // Función, no una constante reutilizada: <Routes> de react-router memoiza
  // internamente por identidad de referencia de sus children. Pasarle el
  // mismo elemento de árbol dos veces a `rerender` deja el DOM viejo sin
  // avisar — hay que construir un árbol nuevo en cada llamada. Confirmado
  // con un repro mínimo antes de este fix, no asumido.
  function makeTree() {
    return (
      <MemoryRouter
        initialEntries={[
          withForm
            ? { pathname: "/stream", state: { form: makeForm() } }
            : { pathname: "/stream" },
        ]}
      >
        <Routes>
          <Route path="/stream" element={<StreamPage />} />
          <Route path="/config" element={<div>config screen</div>} />
          <Route path="/results" element={<ResultsProbe />} />
        </Routes>
      </MemoryRouter>
    );
  }

  const { unmount, rerender } = render(makeTree());

  // Para simular una transición de estado del hook mockeado (ej. el modal
  // cerrándose) — actualiza el mock y vuelve a renderizar un árbol nuevo.
  function rerenderWithState(nextStateOverrides: Partial<StreamState>) {
    mockedUseAnalysisStream.mockReturnValue({
      start,
      state: { ...BASE_STATE, ...nextStateOverrides },
      resolveOutlier,
      abort,
    });
    rerender(makeTree());
  }

  return { start, resolveOutlier, abort, unmount, rerenderWithState };
}

describe("StreamPage", () => {
  afterEach(() => vi.restoreAllMocks());

  it("redirects to /config when there is no form in location.state", () => {
    renderStreamPage({}, { withForm: false });
    expect(screen.getByText("config screen")).toBeInTheDocument();
  });

  it("calls start() once on mount with the form from location.state", () => {
    const { start } = renderStreamPage();
    expect(start).toHaveBeenCalledTimes(1);
    expect(start.mock.calls[0][0]).toMatchObject({
      columna_x: "anio",
      columna_y: "caudal",
    });
  });

  // D2 (pasada de mejora): sin esto, navegar fuera de /stream a mitad de un
  // análisis dejaba el fetch SSE vivo y la sesión colgada hasta el timeout de
  // 300s del backend.
  it("calls abort() on unmount", () => {
    const { abort, unmount } = renderStreamPage();
    expect(abort).not.toHaveBeenCalled();
    unmount();
    expect(abort).toHaveBeenCalledTimes(1);
  });

  it("shows a pill once a group's tests all arrive, and pending groups show none", () => {
    renderStreamPage({
      tests: {
        anderson: testResult({ prueba: "anderson" }),
        wald_wolfowitz: testResult({ prueba: "wald_wolfowitz", veredicto: "aprobada" }),
      },
    });

    const independenciaStep = screen.getByText("Independencia").closest(".step");
    expect(independenciaStep?.querySelector(".pill")).toHaveTextContent("aprobada");

    const homogeneidadStep = screen.getByText("Homogeneidad").closest(".step");
    expect(homogeneidadStep?.querySelector(".pill")).toBeNull();
  });

  it("expands a completed group's detail table on click", () => {
    renderStreamPage({
      tests: {
        anderson: testResult({ prueba: "anderson", estadistico: 0.23 }),
        wald_wolfowitz: testResult({ prueba: "wald_wolfowitz", estadistico: 0.37 }),
      },
    });

    fireEvent.click(screen.getByText("Independencia"));

    expect(screen.getByText("anderson")).toBeInTheDocument();
    expect(screen.getByText("wald_wolfowitz")).toBeInTheDocument();
  });

  it("shows contract warnings as banners", () => {
    renderStreamPage({
      contractWarnings: [
        { codigo: "CONTRACT_LENGTH_WARNING", nivel: "normal", descripcion: "Serie corta" },
      ],
    });

    expect(screen.getByText("Serie corta")).toBeInTheDocument();
  });

  it("shows an error banner when fase=error", () => {
    renderStreamPage({
      fase: "error",
      error: { codigo: "CONTRACT_SERIES_TOO_SHORT", mensaje: "La serie es muy corta." },
    });

    expect(screen.getByRole("alert")).toHaveTextContent("La serie es muy corta.");
  });

  it("shows the outlier modal and calls resolveOutlier when Rechazar is clicked", async () => {
    const { resolveOutlier } = renderStreamPage({
      fase: "waiting_outlier",
      outlier: { session_id: "sess-1", valor_atipico: 245.7 },
    });

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Rechazar" }));

    await waitFor(() => expect(resolveOutlier).toHaveBeenCalledWith("rechazar"));
  });

  // M3 (cierre de Fase 6, pasada de mejora 3): foco del modal de atípico.
  it("auto-focuses the dialog container (not either button) when the outlier modal opens", async () => {
    renderStreamPage({
      fase: "waiting_outlier",
      outlier: { session_id: "sess-1", valor_atipico: 245.7 },
    });

    await waitFor(() => expect(screen.getByRole("dialog")).toHaveFocus());
  });

  it("Escape does not close the modal or resolve a decision — the backend is blocked waiting for a real choice", async () => {
    const { resolveOutlier } = renderStreamPage({
      fase: "waiting_outlier",
      outlier: { session_id: "sess-1", valor_atipico: 245.7 },
    });

    const dialog = screen.getByRole("dialog");
    await waitFor(() => expect(dialog).toHaveFocus());

    fireEvent.keyDown(dialog, { key: "Escape" });

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(resolveOutlier).not.toHaveBeenCalled();
    expect(dialog).toHaveFocus();
  });

  it("restores focus to the previously-focused element once the outlier modal closes", async () => {
    const { rerenderWithState } = renderStreamPage({
      tests: { anderson: testResult({ prueba: "anderson" }) },
    });

    const independenciaStep = screen.getByText("Independencia").closest(".step") as HTMLElement;
    independenciaStep.focus();
    expect(independenciaStep).toHaveFocus();

    rerenderWithState({
      fase: "waiting_outlier",
      outlier: { session_id: "sess-1", valor_atipico: 245.7 },
    });
    await waitFor(() => expect(screen.getByRole("dialog")).toHaveFocus());

    rerenderWithState({
      fase: "streaming",
      tests: { anderson: testResult({ prueba: "anderson" }) },
    });

    await waitFor(() => expect(independenciaStep).toHaveFocus());
  });

  it("shows a completion banner and navigates to /results carrying the result", async () => {
    renderStreamPage({
      fase: "done",
      result: {
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
      analysisId: "an-1",
    });

    fireEvent.click(screen.getByRole("button", { name: /Ver resultados/ }));

    await waitFor(() =>
      expect(screen.getByTestId("results-state")).toHaveTextContent("an-1"),
    );
    // modo viaja junto al resultado — ResultsPage lo necesita para elegir
    // presentación (acordeón paso a paso vs. tarjetas planas de experto).
    expect(screen.getByTestId("results-state")).toHaveTextContent(
      makeForm().modo,
    );
  });
});
