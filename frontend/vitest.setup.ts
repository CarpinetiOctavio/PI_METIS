import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach, vi } from "vitest";

// jsdom does not implement matchMedia. ThemeProvider calls it unconditionally
// on mount (to read the prefers-color-scheme media query), so every test that
// renders <ThemeProvider> — directly or via <App>/<TopBar> — needs a
// deterministic stub. Defined once here instead of duplicated per test file.
//
// ThemeProvider also persists metis-theme-mode to localStorage and sets
// data-theme/data-mode on <html> on every mount. Without resetting those here,
// tests in the same file (or across files sharing jsdom's window) can leak
// mode state into each other — clearing localStorage and the attributes
// before every test guarantees real isolation, not just assertion-order luck.
beforeEach(() => {
  vi.spyOn(window, "matchMedia").mockReturnValue({
    matches: false,
  } as MediaQueryList);
  localStorage.clear();
  // R3 (limpieza SonarCloud): dataset en vez de removeAttribute — mismo
  // patrón que ThemeProvider.tsx usa para setear estos atributos.
  delete document.documentElement.dataset.theme;
  delete document.documentElement.dataset.mode;
});

// B6 (docs/frontend/plan-mejora-frontend-pasada4.md §4): jsdom no implementa
// canvas — HTMLCanvasElement.prototype.getContext devuelve null y emite un
// "Not implemented" al stderr. DotFieldBackground/GridScanBackground se
// montan globalmente (RootLayout/EntryPage), así que sin este stub TODOS los
// tests de página que pasan por renderPage() ensuciarían su salida.
// Proxy en vez de enumerar métodos: cualquier llamada a un método del
// contexto 2D devuelve un vi.fn() sin efecto, cualquier propiedad (fillStyle,
// globalAlpha, etc.) se puede leer/escribir — así el camino REAL del
// componente se ejercita en los tests de ciclo de vida (B5), no la guarda de
// `if (!ctx) return`.
// Métodos que en la API real devuelven un objeto con su propia interfaz
// (CanvasGradient.addColorStop, CanvasPattern), no un valor primitivo — un
// vi.fn() genérico como valor de retorno no alcanza para esos.
const GRADIENT_LIKE_METHODS = new Set([
  "createLinearGradient",
  "createRadialGradient",
  "createConicGradient",
  "createPattern",
]);

function createMockGradient() {
  return new Proxy(
    {},
    {
      get() {
        return vi.fn();
      },
    },
  );
}

function createMockCanvasContext() {
  const state: Record<string, unknown> = {};
  return new Proxy(state, {
    get(target, prop) {
      if (prop in target) return target[prop as string];
      if (typeof prop === "string" && GRADIENT_LIKE_METHODS.has(prop)) {
        return vi.fn(() => createMockGradient());
      }
      return vi.fn();
    },
    set(target, prop, value) {
      target[prop as string] = value;
      return true;
    },
  });
}

beforeEach(() => {
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockImplementation(
    ((contextId: string) =>
      contextId === "2d"
        ? createMockCanvasContext()
        : null) as typeof HTMLCanvasElement.prototype.getContext,
  );
});

// Tampoco implementados en jsdom, y los mismos dos componentes de fondo los
// usan (B4: pausar fuera de viewport, escalar por resize del contenedor).
// No-ops globales, no espías por test — nada en la suite necesita verificar
// que se llamó a observe/disconnect con argumentos concretos.
class NoopResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}
class NoopIntersectionObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords() {
    return [];
  }
  root = null;
  rootMargin = "";
  thresholds: number[] = [];
}
if (typeof globalThis.ResizeObserver === "undefined") {
  globalThis.ResizeObserver =
    NoopResizeObserver as unknown as typeof ResizeObserver;
}
if (typeof globalThis.IntersectionObserver === "undefined") {
  globalThis.IntersectionObserver =
    NoopIntersectionObserver as unknown as typeof IntersectionObserver;
}

afterEach(() => {
  vi.restoreAllMocks();
});
