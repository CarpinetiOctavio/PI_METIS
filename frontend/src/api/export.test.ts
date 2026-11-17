import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "./client";
import { obtenerPdfAnalisis } from "./export";

function stubFetch(response: {
  ok: boolean;
  status: number;
  headers?: Record<string, string>;
  blob?: Blob;
  json?: unknown;
}) {
  const fn = vi.fn().mockResolvedValue({
    ok: response.ok,
    status: response.status,
    headers: new Headers(response.headers ?? {}),
    blob: () => Promise.resolve(response.blob ?? new Blob()),
    json: () => Promise.resolve(response.json),
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

describe("obtenerPdfAnalisis", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("pide GET /api/v1/export/{id} con la cookie y usa el nombre de Content-Disposition", async () => {
    const pdf = new Blob(["%PDF-1.4"], { type: "application/pdf" });
    const fetchFn = stubFetch({
      ok: true,
      status: 200,
      headers: {
        "Content-Disposition": 'attachment; filename="metis_estacion_2026-10-06.pdf"',
      },
      blob: pdf,
    });

    const resultado = await obtenerPdfAnalisis("an-1");

    expect(fetchFn).toHaveBeenCalledWith(
      "/api/v1/export/an-1",
      expect.objectContaining({ credentials: "include" }),
    );
    expect(resultado.blob).toBe(pdf);
    expect(resultado.nombre).toBe("metis_estacion_2026-10-06.pdf");
  });

  it("con puntos excluidos pide POST /api/v1/export/{id}/simulacion con los índices", async () => {
    const fetchFn = stubFetch({ ok: true, status: 200 });

    await obtenerPdfAnalisis("an-1", [3, 17]);

    const [url, init] = fetchFn.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/api/v1/export/an-1/simulacion");
    expect(init.method).toBe("POST");
    expect(init.credentials).toBe("include");
    expect(JSON.parse(String(init.body))).toEqual({ indices_excluidos: [3, 17] });
  });

  it("con la lista de excluidos vacía exporta el análisis sin simulación", async () => {
    const fetchFn = stubFetch({ ok: true, status: 200 });
    await obtenerPdfAnalisis("an-1", []);
    expect(fetchFn.mock.calls[0][0]).toBe("/api/v1/export/an-1");
  });

  it("sin Content-Disposition usa un nombre por defecto", async () => {
    stubFetch({ ok: true, status: 200 });
    expect((await obtenerPdfAnalisis("an-1")).nombre).toBe("metis_analisis.pdf");
  });

  it("ante un 404 lanza ApiError con el código del backend", async () => {
    stubFetch({
      ok: false,
      status: 404,
      json: { error: { codigo: "ANALYSIS_NOT_FOUND", mensaje: "No existe." } },
    });

    const error = await obtenerPdfAnalisis("an-x").catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).codigo).toBe("ANALYSIS_NOT_FOUND");
    expect((error as ApiError).status).toBe(404);
  });
});
