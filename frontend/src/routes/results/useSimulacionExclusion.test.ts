import { describe, expect, it, vi } from "vitest";
import { act, renderHook, waitFor } from "@testing-library/react";
import { ApiError } from "../../api/client";
import type { SimulateExclusionResponse } from "../../api/types";
import { makeSimulacion } from "../../test/simulacionFixtures";
import { useSimulacionExclusion } from "./useSimulacionExclusion";

function diferida() {
  let resolver!: (r: SimulateExclusionResponse) => void;
  const promesa = new Promise<SimulateExclusionResponse>((res) => {
    resolver = res;
  });
  return { promesa, resolver };
}

describe("useSimulacionExclusion", () => {
  it("pide los índices ordenados y queda en 'lista' con la respuesta", async () => {
    const simular = vi.fn().mockResolvedValue(makeSimulacion());
    const { result } = renderHook(() => useSimulacionExclusion(simular));

    await act(() => result.current.calcular(new Set([7, 3])));

    expect(simular).toHaveBeenCalledWith([3, 7]);
    expect(result.current.estado).toMatchObject({ fase: "lista", indices: [3, 7] });
  });

  it("un ApiError pasa a 'error' con el texto en castellano, no el código crudo", async () => {
    const simular = vi.fn().mockRejectedValue(new ApiError(400, "CONTRACT_SERIES_TOO_SHORT", "x"));
    const { result } = renderHook(() => useSimulacionExclusion(simular));

    await act(() => result.current.calcular(new Set([1])));

    expect(result.current.estado).toEqual({
      fase: "error",
      mensaje: "La serie tiene menos de 10 datos. No se puede analizar.",
    });
  });

  it("si llegan fuera de orden, la respuesta vieja no pisa a la última", async () => {
    const primera = diferida();
    const segunda = diferida();
    const simular = vi.fn().mockReturnValueOnce(primera.promesa).mockReturnValueOnce(segunda.promesa);
    const { result } = renderHook(() => useSimulacionExclusion(simular));

    act(() => {
      void result.current.calcular(new Set([1]));
      void result.current.calcular(new Set([2]));
    });
    await act(async () => segunda.resolver(makeSimulacion()));
    await act(async () => primera.resolver(makeSimulacion({ serie: [] })));

    await waitFor(() => expect(result.current.estado.fase).toBe("lista"));
    expect(result.current.estado).toMatchObject({ indices: [2] });
  });

  it("reiniciar descarta también lo que esté en vuelo", async () => {
    const pendiente = diferida();
    const { result } = renderHook(() => useSimulacionExclusion(() => pendiente.promesa));

    act(() => {
      void result.current.calcular(new Set([1]));
    });
    expect(result.current.estado.fase).toBe("calculando");
    act(() => result.current.reiniciar());
    await act(async () => pendiente.resolver(makeSimulacion()));

    expect(result.current.estado.fase).toBe("ninguna");
  });

  it("sin función de simulación no hace nada", async () => {
    const { result } = renderHook(() => useSimulacionExclusion(undefined));
    await act(() => result.current.calcular(new Set([1])));
    expect(result.current.estado.fase).toBe("ninguna");
  });
});
