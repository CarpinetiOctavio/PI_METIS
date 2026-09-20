import { vi } from "vitest";

/** jsdom no calcula layout real: `getBoundingClientRect()` da todo 0 por
 * default. Los gráficos convierten `clientX/clientY` a coordenadas de su viewBox
 * (640×320) proporcionalmente al rect, así que los tests que simulan mouse lo
 * mockean 1:1 con el viewBox — así se puede calcular a mano el clic de cada
 * punto. Quien lo llame debe restaurar los mocks (`vi.restoreAllMocks()`). */
export function mockChartRect() {
  vi.spyOn(Element.prototype, "getBoundingClientRect").mockReturnValue({
    left: 0,
    top: 0,
    width: 640,
    height: 320,
    right: 640,
    bottom: 320,
    x: 0,
    y: 0,
    toJSON() {
      return this;
    },
  } as DOMRect);
}
