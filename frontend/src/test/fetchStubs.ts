import { vi } from "vitest";

interface RutaStub {
  match: (url: string, init?: RequestInit) => boolean;
  status: number;
  body: unknown;
}

/** `fetch` ruteado por URL/método, para tests que disparan más de una llamada
 * (por ejemplo GET de la página + POST al explorar una distribución).
 *
 * Ruteado en vez de posicional (`mockResolvedValueOnce` encadenado) a propósito:
 * bajo StrictMode (`renderPage` envuelve todo en él) los efectos de carga
 * corren dos veces al montar — un mock posicional consumiría un slot con la
 * llamada descartada y desalinearía el resto. */
export function stubFetchRouted(rutas: RutaStub[]) {
  const fn = vi.fn((url: string, init?: RequestInit) => {
    const ruta = rutas.find((r) => r.match(String(url), init));
    if (!ruta) {
      throw new Error(`stubFetchRouted: sin ruta para ${init?.method ?? "GET"} ${url}`);
    }
    return Promise.resolve({
      ok: ruta.status < 400,
      status: ruta.status,
      json: () => Promise.resolve(ruta.body),
    });
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}
