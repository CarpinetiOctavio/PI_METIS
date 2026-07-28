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

  it("sets fase=error with a legible message on contract_error", () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));

    act(() => emit("contract_error", { codigo: "CONTRACT_SERIES_TOO_SHORT", iteracion: 1 }));

    expect(result.current.state.fase).toBe("error");
    expect(result.current.state.error?.codigo).toBe("CONTRACT_SERIES_TOO_SHORT");
    expect(result.current.state.error?.mensaje).toMatch(/menos de 10 datos/);
  });

  it("sets fase=error on a server error event (e.g. SESSION_TIMEOUT)", () => {
    mockedFetchEventSource.mockImplementation(() => new Promise(() => {}));
    const { result } = renderHook(() => useAnalysisStream());
    act(() => result.current.start(makeForm()));

    act(() => emit("error", { codigo: "SESSION_TIMEOUT", mensaje: "timeout real" }));

    expect(result.current.state.fase).toBe("error");
    expect(result.current.state.error).toEqual({
      codigo: "SESSION_TIMEOUT",
      mensaje: "timeout real",
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
});
