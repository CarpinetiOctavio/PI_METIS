// Capa 2 de testing (docs/frontend/plan-arreglo-ui-rota.md §4.2-a): StreamPage
// REAL + useAnalysisStream REAL, con la red interceptada en el único borde
// real — fetchEventSource — igual que StreamPage.lifecycle.test.tsx (Bloque 0)
// y api/sse.test.ts. El plan original proponía MSW devolviendo un
// ReadableStream SSE en Node para esta capa, marcándolo como "lo más
// delicado" del plan; se optó por esta vía en cambio porque logra
// exactamente lo mismo (componente real + hook real, red interceptada en el
// borde) sin apartarse del patrón único de mocking de red que
// docs/decisiones/decision041.md ya fijó para toda la suite (vi.stubGlobal
// para fetch / vi.mock para fetchEventSource — MSW queda reservado al
// navegador de dev). Es, en efecto, el "plan B" que el propio plan de
// arreglo dejaba habilitado si MSW-en-Node resultaba delicado, sin haber
// necesitado siquiera llegar a probarlo.
import { afterEach, describe, expect, it, vi } from "vitest";
import { act, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route, useLocation } from "react-router-dom";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { renderPage } from "../../test/renderPage";
import { StreamPage } from "./StreamPage";
import * as analysisApi from "../../api/analysis";
import type { AnalysisStreamForm } from "../../api/types";

vi.mock("@microsoft/fetch-event-source", () => ({
  fetchEventSource: vi.fn(),
}));

const mockedFetchEventSource = vi.mocked(fetchEventSource);

function makeForm(): AnalysisStreamForm {
  return {
    archivo: new File(["anio,caudal\n1980,100"], "serie.csv", { type: "text/csv" }),
    columna_x: "anio",
    columna_y: "caudal",
    tipo_variable: "caudal_precipitacion",
    modo: "experto",
    cramer_particion: "default",
  };
}

// Bajo StrictMode puede haber dos llamadas a fetchEventSource (la primera se
// aborta sola, F1) — siempre apuntamos a la ÚLTIMA, la que sigue viva.
function lastOptions() {
  const call = mockedFetchEventSource.mock.calls.at(-1);
  if (!call) throw new Error("fetchEventSource no fue llamado todavía");
  return call[1];
}

function emit(type: string, payload: Record<string, unknown> = {}) {
  act(() => {
    lastOptions().onmessage?.({ event: type, data: JSON.stringify(payload), id: "" } as never);
  });
}

function closeStream() {
  act(() => {
    lastOptions().onclose?.();
  });
}

function testResult(prueba: string, iteracion = 1, overrides: Record<string, unknown> = {}) {
  emit("test_result", {
    prueba,
    estadistico: 0.5,
    valor_critico: 1.0,
    veredicto: "aprobada",
    warning_codigo: null,
    warning_nivel: null,
    n1: null,
    n2: null,
    valor_atipico: null,
    iteracion,
    ...overrides,
  });
}

function ResultsProbe() {
  const location = useLocation();
  return <pre data-testid="results-state">{JSON.stringify(location.state)}</pre>;
}

function renderStream() {
  mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
  return renderPage(
    <MemoryRouter initialEntries={[{ pathname: "/stream", state: { form: makeForm() } }]}>
      <Routes>
        <Route path="/stream" element={<StreamPage />} />
        <Route path="/results" element={<ResultsProbe />} />
      </Routes>
    </MemoryRouter>,
  );
}

const TODOS_LOS_GRUPOS = [
  "anderson",
  "wald_wolfowitz",
  "helmert",
  "t_student",
  "cramer",
  "mann_kendall",
  "kolmogorov_smirnov",
  "chow",
];

describe("StreamPage — integración de punta a punta (componente + hook reales)", () => {
  afterEach(() => vi.restoreAllMocks());

  // Este es el escenario que hace imposible que F1 vuelva: si el ciclo de
  // vida de StreamPage rompiera el stream otra vez, este test se cuelga en
  // "streaming" para siempre y nunca llega a "Ver resultados".
  it("camino feliz: los 4 grupos llegan a estado final y aparece 'Ver resultados'", async () => {
    renderStream();

    TODOS_LOS_GRUPOS.forEach((prueba) => testResult(prueba));
    emit("result_etapa1", {
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
    });
    emit("complete", { analysis_id: "an-1" });

    expect(
      await screen.findByRole("button", { name: /Ver resultados/ }),
    ).toBeInTheDocument();
    expect(screen.getByText("Independencia").closest(".step")?.querySelector(".pill")).toHaveTextContent("aprobada");
    expect(screen.getByText("Atípicos (Chow)").closest(".step")?.querySelector(".pill")).toHaveTextContent("aprobada");

    fireEvent.click(screen.getByRole("button", { name: /Ver resultados/ }));
    expect(await screen.findByTestId("results-state")).toHaveTextContent("an-1");
  });

  // Con atípico: el modal pausa el stream, resolveOutlier("rechazar") postea
  // la decisión, y la re-ejecución (iteracion:2) reemplaza los resultados en
  // vez de duplicarlos o acumularlos junto a los de iteracion:1.
  it("con atípico: pausa, resuelve, y la iteración 2 reemplaza los resultados sin duplicar", async () => {
    const postSpy = vi
      .spyOn(analysisApi, "postOutlierDecision")
      .mockResolvedValue({ ok: true, pipeline_continua: true });
    renderStream();

    testResult("anderson", 1, { estadistico: 0.11 });
    emit("outlier_detected", { session_id: "sess-1", valor_atipico: 245.7 });

    const dialog = await screen.findByRole("dialog");
    expect(dialog).toBeInTheDocument();
    // formatNum usa coma decimal y 5 decimales (sprint.md, F4) — "245.7" no
    // aparece literal en el DOM, "245,70000" sí.
    expect(dialog).toHaveTextContent("245,70000");

    fireEvent.click(screen.getByRole("button", { name: "Rechazar" }));

    await waitFor(() =>
      expect(postSpy).toHaveBeenCalledWith({
        session_id: "sess-1",
        decision: "rechazar",
        dato_atipico: 245.7,
      }),
    );
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());

    // Re-ejecución: mismo prueba, iteracion:2, valor distinto — reemplaza,
    // no se acumula un segundo resultado para "anderson".
    TODOS_LOS_GRUPOS.forEach((prueba) => testResult(prueba, 2, { estadistico: 0.22 }));
    emit("result_etapa1", {
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
    });
    emit("complete", { analysis_id: "an-2" });

    await screen.findByRole("button", { name: /Ver resultados/ });
    fireEvent.click(screen.getByText("Independencia"));
    // Solo una fila "anderson" en la tabla expandida — no dos (no quedó la
    // de iteracion:1 acumulada junto a la de iteracion:2).
    const andersonCells = screen.getAllByText("anderson");
    expect(andersonCells).toHaveLength(1);
    // formatNum: coma decimal, 5 decimales (sprint.md, F4) — el valor de la
    // fila es el de iteracion:2 (0.22), no el de iteracion:1 (0.11).
    const row = andersonCells[0].closest("tr");
    expect(row).toHaveTextContent("0,22000");
  });

  // Contrato bloqueante: contract_error deja fase="error", y el `complete`
  // que el backend SIEMPRE manda después (frontend-integration.md §4) no la
  // pisa con "done" — regresión ya cubierta en sse.test.ts a nivel de hook,
  // acá se confirma que también se ve así en la pantalla real.
  it("contrato bloqueante: banner de error, complete no lo pisa con 'done'", async () => {
    renderStream();

    emit("contract_error", { codigo: "CONTRACT_SERIES_TOO_SHORT", iteracion: 1 });
    emit("complete", { analysis_id: null });

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "La serie tiene menos de 10 datos. No se puede analizar.",
    );
    expect(screen.queryByRole("button", { name: /Ver resultados/ })).not.toBeInTheDocument();
  });

  // F1 (1.2 del plan de arreglo): si el servidor cierra la conexión sin
  // haber mandado `complete` antes, la pantalla no puede quedarse colgada en
  // "streaming" para siempre y en silencio — ahora es un error visible.
  it("el servidor cierra sin 'complete': STREAM_CLOSED_EARLY queda visible, no se cuelga en silencio", async () => {
    renderStream();

    testResult("anderson");
    closeStream();

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "El servidor cerró la conexión antes de terminar el análisis.",
    );
  });
});
