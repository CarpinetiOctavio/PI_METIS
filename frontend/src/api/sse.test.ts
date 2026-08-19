import { afterEach, describe, expect, it, vi } from "vitest";
import { act, renderHook, waitFor } from "@testing-library/react";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useAnalysisStream } from "./sse";
import * as analysisApi from "./analysis";
import type { AnalysisStreamForm } from "./types";

vi.mock("@microsoft/fetch-event-source", () => ({
  fetchEventSource: vi.fn(),
}));

const mockedFetchEventSource = vi.mocked(fetchEventSource);

function makeForm(): AnalysisStreamForm {
  return {
    archivo: new File(["1,100\n2,200"], "serie.csv", { type: "text/csv" }),
    columna_x: "anio",
    columna_y: "caudal",
    tipo_variable: "caudal_precipitacion",
    modo: "experto",
    cramer_particion: "default",
  };
}

// Cada callback real (onmessage/onopen/onclose/onerror) del quinto argumento
// posicional de fetchEventSource se dispara a mano acá, en vez de simular un
// stream de red real — ver frontend-implementation-plan.md §9.1, fixture
// recomendado como secuencia sintética.
function lastOptions() {
  const call = mockedFetchEventSource.mock.calls.at(-1);
  if (!call) throw new Error("fetchEventSource no fue llamado todavía");
  return call[1];
}

function emit(type: string, payload: Record<string, unknown> = {}) {
  const options = lastOptions();
  options.onmessage?.({
    event: type,
    data: JSON.stringify(payload),
    id: "",
  } as never);
}

describe("useAnalysisStream", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("moves to streaming on start and parses progress/test_result events", async () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());

    act(() => result.current.start(makeForm()));
    expect(result.current.state.fase).toBe("streaming");

    act(() => emit("progress", { paso: "anderson", etapa: 1, completado: 3, total: 8, iteracion: 1 }));
    expect(result.current.state.progress).toEqual({ completado: 3, total: 8 });

    act(() =>
      emit("test_result", {
        prueba: "anderson",
        estadistico: 0.23,
        valor_critico: 0.37,
        veredicto: "aprobada",
        warning_codigo: null,
        warning_nivel: null,
        n1: null,
        n2: null,
        valor_atipico: null,
        iteracion: 1,
      }),
    );
    expect(result.current.state.tests.anderson).toMatchObject({
      estadistico: 0.23,
      veredicto: "aprobada",
    });
  });

  it("dedupes contract_warning by codigo and resets on a new iteracion", () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));

    act(() => emit("contract_warning", { codigo: "CONTRACT_LENGTH_WARNING", nivel: "normal", iteracion: 1 }));
    act(() => emit("contract_warning", { codigo: "CONTRACT_LENGTH_WARNING", nivel: "normal", iteracion: 1 }));
    expect(result.current.state.contractWarnings).toHaveLength(1);

    // iteracion:2 (re-ejecución tras rechazar un atípico) resetea los
    // warnings de la corrida anterior en vez de acumularlos.
    act(() => emit("contract_warning", { codigo: "CONTRACT_NEGATIVE_VALUES", nivel: "normal", iteracion: 2 }));
    expect(result.current.state.contractWarnings).toHaveLength(1);
    expect(result.current.state.contractWarnings[0].codigo).toBe("CONTRACT_NEGATIVE_VALUES");
  });

  it("test_result with iteracion:2 replaces iteracion:1 for the same prueba, not accumulates", () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));

    act(() =>
      emit("test_result", {
        prueba: "anderson",
        estadistico: 0.23,
        valor_critico: 0.37,
        veredicto: "aprobada",
        warning_codigo: null,
        warning_nivel: null,
        n1: null,
        n2: null,
        valor_atipico: null,
        iteracion: 1,
      }),
    );
    act(() =>
      emit("test_result", {
        prueba: "anderson",
        estadistico: 0.11,
        valor_critico: 0.37,
        veredicto: "aprobada",
        warning_codigo: null,
        warning_nivel: null,
        n1: null,
        n2: null,
        valor_atipico: null,
        iteracion: 2,
      }),
    );

    expect(Object.keys(result.current.state.tests)).toEqual(["anderson"]);
    expect(result.current.state.tests.anderson.estadistico).toBe(0.11);
  });

  it("unwraps result_etapa1 correctly — the real backend sends the raw Etapa1Result as the payload, not {result: ...} (regression — found via live backend testing)", () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));

    const rawEtapa1Result = {
      contract: { bloqueante: false, codigo_error: null, warnings: [] },
      descriptive: {
        n: 39,
        media: 134.4,
        mediana: 134.3,
        desvio_estandar: 24.55,
        coef_variacion: 0.18,
        coef_asimetria: 0.21,
        minimo: 91.9,
        maximo: 189.1,
      },
      independencia: [],
      homogeneidad: [],
      tendencia: [],
      atipicos: [],
      nivel_independencia: "independiente",
      nivel_homogeneidad: "homogeneidad_ok",
      nivel_confianza: "validado",
      warnings: [],
    };
    // emit() manda el payload crudo tal cual — sin envoltura {result: ...} —
    // igual que lo confirmado contra el backend real (docker-compose up).
    act(() => emit("result_etapa1", rawEtapa1Result));

    expect(result.current.state.result).toEqual(rawEtapa1Result);
  });

  it("pauses on outlier_detected and resolveOutlier posts the decision then resumes streaming", async () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const postSpy = vi
      .spyOn(analysisApi, "postOutlierDecision")
      .mockResolvedValue({ ok: true, pipeline_continua: true });

    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));
    act(() => emit("outlier_detected", { session_id: "sess-1", valor_atipico: 245.7 }));

    expect(result.current.state.fase).toBe("waiting_outlier");
    expect(result.current.state.outlier).toEqual({
      session_id: "sess-1",
      valor_atipico: 245.7,
    });

    await act(async () => {
      await result.current.resolveOutlier("rechazar");
    });

    expect(postSpy).toHaveBeenCalledWith({
      session_id: "sess-1",
      decision: "rechazar",
      dato_atipico: 245.7,
    });
    expect(result.current.state.fase).toBe("streaming");
    expect(result.current.state.outlier).toBeNull();
  });

  // Bug real encontrado en vivo (plan post-avance, 14/08/2026, hallazgo V1):
  // el POST de outlier-decision y el stream SSE son dos conexiones
  // independientes — el servidor puede reanudar el pipeline y emitir
  // result_etapa2_ranking (que ya deja fase="waiting_distribution") ANTES
  // de que la promesa de este POST resuelva del lado del cliente. Sin el
  // guard en resolveOutlier, el setInternal tardío pisaba
  // "waiting_distribution" con "streaming" otra vez — el ranking quedaba
  // visible pero sin ningún botón "Elegir" posible. Reproducido contra el
  // backend real (dev y build de producción) con logging de la secuencia
  // exacta de eventos.
  it("does not let a late-resolving resolveOutlier overwrite fase once result_etapa2_ranking already advanced it (regression — found via live backend testing)", async () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    let resolvePost!: () => void;
    const postSpy = vi
      .spyOn(analysisApi, "postOutlierDecision")
      .mockImplementation(
        () =>
          new Promise((resolve) => {
            resolvePost = () => resolve({ ok: true, pipeline_continua: true });
          }),
      );

    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));
    act(() => emit("outlier_detected", { session_id: "sess-1", valor_atipico: 245.7 }));

    let resolveOutlierPromise!: Promise<void>;
    act(() => {
      resolveOutlierPromise = result.current.resolveOutlier("rechazar");
    });
    expect(postSpy).toHaveBeenCalled();

    // El stream ya avanzó a la pausa de distribución mientras el POST de
    // arriba sigue sin resolver — exactamente la carrera reproducida en vivo.
    act(() =>
      emit("result_etapa2_ranking", {
        session_id: "sess-1",
        ranking: [],
        warnings: [],
        puntos_empiricos: [],
      }),
    );
    expect(result.current.state.fase).toBe("waiting_distribution");

    await act(async () => {
      resolvePost();
      await resolveOutlierPromise;
    });

    // El setInternal tardío de resolveOutlier no debe pisar la fase más
    // avanzada — sigue en waiting_distribution, con el ranking intacto.
    expect(result.current.state.fase).toBe("waiting_distribution");
    expect(result.current.state.etapa2).not.toBeNull();
    expect(result.current.state.outlier).toBeNull();
  });

  // Mismo patrón que el test anterior, para la segunda pausa (DECISIÓN 052
  // reusa el mismo mecanismo de sesión) — result_etapa2_eventos o incluso
  // complete pueden llegar antes de que el POST de distribution-decision
  // resuelva. Sin el guard, un análisis ya "done" volvía a "streaming".
  it("does not let a late-resolving resolveDistribution overwrite fase once complete already advanced it (regression)", async () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    let resolvePost!: () => void;
    vi.spyOn(analysisApi, "postDistributionDecision").mockImplementation(
      () =>
        new Promise((resolve) => {
          resolvePost = () => resolve({ ok: true, pipeline_continua: true });
        }),
    );

    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));
    act(() =>
      emit("result_etapa2_ranking", {
        session_id: "sess-1",
        ranking: [],
        warnings: [],
        puntos_empiricos: [],
      }),
    );
    expect(result.current.state.fase).toBe("waiting_distribution");

    let resolveDistribPromise!: Promise<void>;
    act(() => {
      resolveDistribPromise = result.current.resolveDistribution("gumbel", "momentos", [10, 100]);
    });

    // El stream ya terminó mientras el POST de arriba sigue sin resolver.
    act(() =>
      emit("result_etapa2_eventos", {
        distribucion: "gumbel",
        metodo: "momentos",
        eventos_diseno: [],
        curva_ajuste: [],
      }),
    );
    act(() => emit("complete", { analysis_id: null }));
    expect(result.current.state.fase).toBe("done");

    await act(async () => {
      resolvePost();
      await resolveDistribPromise;
    });

    expect(result.current.state.fase).toBe("done");
  });

  it("sets fase=error with a legible message on contract_error", () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));

    act(() => emit("contract_error", { codigo: "CONTRACT_SERIES_TOO_SHORT", iteracion: 1 }));

    expect(result.current.state.fase).toBe("error");
    expect(result.current.state.error?.codigo).toBe("CONTRACT_SERIES_TOO_SHORT");
    expect(result.current.state.error?.mensaje).toMatch(/menos de 10 datos/);
  });

  it("does not let the complete event that always follows contract_error overwrite fase=error with done (regression — found via live backend testing)", () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));

    act(() => emit("contract_error", { codigo: "CONTRACT_NO_TEMPORAL_RESOLUTION", iteracion: 1 }));
    act(() => emit("complete", { analysis_id: null }));

    expect(result.current.state.fase).toBe("error");
    expect(result.current.state.error?.codigo).toBe("CONTRACT_NO_TEMPORAL_RESOLUTION");
  });

  // D1 (pasada de mejora): el texto mostrado sale del diccionario curado
  // (errorText), nunca del `mensaje` crudo que manda el backend — el
  // backend no es consistente en qué manda ahí (str(exc) técnico en
  // PARSE_ERROR, texto ya curado en SESSION_TIMEOUT). Unificado en el
  // frontend, ver docs/decisiones/decision038.md.
  it("sets fase=error on a server error event, using the curated dictionary text (e.g. SESSION_TIMEOUT)", () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));

    act(() => emit("error", { codigo: "SESSION_TIMEOUT", mensaje: "timeout real (crudo, no se usa)" }));

    expect(result.current.state.fase).toBe("error");
    expect(result.current.state.error).toEqual({
      codigo: "SESSION_TIMEOUT",
      mensaje: "Se agotó el tiempo de espera para decidir sobre el dato atípico.",
    });
  });

  it("sets fase=error on malformed JSON instead of throwing", () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));

    act(() => {
      const options = lastOptions();
      options.onmessage?.({ event: "test_result", data: "{not json", id: "" } as never);
    });

    expect(result.current.state.fase).toBe("error");
    expect(result.current.state.error?.codigo).toBe("PARSE_ERROR");
  });

  it("onerror sets fase=error and rethrows to stop the library's automatic retry", async () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));

    const options = lastOptions();
    act(() => {
      expect(() => options.onerror?.(new Error("conexión perdida"))).toThrow();
    });

    await waitFor(() => expect(result.current.state.fase).toBe("error"));
    expect(result.current.state.error?.codigo).toBe("STREAM_CONNECTION_ERROR");
  });

  // Bloque H1 (plan post-avance, DECISIÓN 036) — cramer_particion personalizada.

  it("manda cramer_particion='default' tal cual cuando no es personalizada", async () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));

    const body = lastOptions().body as FormData;
    expect(body.get("cramer_particion")).toBe("default");
  });

  it("manda un objeto cramer_particion como JSON string en el mismo campo", async () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());
    act(() =>
      result.current.start({
        ...makeForm(),
        cramer_particion: { n1_pct: 70, n2_pct: 20 },
      }),
    );

    const body = lastOptions().body as FormData;
    expect(body.get("cramer_particion")).toBe(
      JSON.stringify({ n1_pct: 70, n2_pct: 20 }),
    );
  });
});
