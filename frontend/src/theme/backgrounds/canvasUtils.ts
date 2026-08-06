// Compartido por DotFieldBackground y GridScanBackground.
import { prefersReducedMotion } from "../motion";

export { prefersReducedMotion };

/** --acc/--line etc. siempre son hex en tokens.instrumento.css — sin eso
 * color-mix() no está disponible dentro de un contexto Canvas 2D. */
export function hexToRgba(hex: string, alpha: number): string {
  const clean = hex.trim().replace("#", "");
  const full =
    clean.length === 3
      ? clean
          .split("")
          .map((c) => c + c)
          .join("")
      : clean;
  const value = Number.parseInt(full, 16);
  const r = (value >> 16) & 255;
  const g = (value >> 8) & 255;
  const b = value & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/** Math.random() dispara la regla S2245 de SonarCloud (PRNG no
 * criptográfico) en cualquier uso, sin distinguir jitter puramente visual
 * de valores sensibles. Mismo rango [0, 1) que Math.random(), vía
 * crypto.getRandomValues — usado por ThreadsBackground para sembrar la
 * animación de los hilos. */
export function secureRandom(): number {
  const array = new Uint32Array(1);
  crypto.getRandomValues(array);
  return array[0] / (0xffffffff + 1);
}

export function readCssVar(name: string, fallback: string): string {
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
  return value || fallback;
}

/** DPR + tamaño del viewport — evita el fondo borroso en pantallas HiDPI
 * (plan pasada4 §4 B4, guarda 4).
 *
 * Bug encontrado en verificación manual (05/08/2026): esta función medía
 * `canvas.parentElement.clientWidth` en vez del viewport, para un canvas que
 * en los dos únicos consumidores (DotFieldBackground, GridScanBackground) es
 * siempre `position: fixed; inset: 0` — cubre la pantalla entera, el tamaño
 * del padre es irrelevante. En el primer render, el padre (`.route-enter`,
 * un `<div>` de layout normal sin ancho propio) podía leer `clientWidth: 0`
 * antes de que el layout terminara de asentarse; el `ResizeObserver` que
 * debía corregirlo observaba ese mismo padre y no volvía a disparar porque
 * su tamaño no cambiaba de nuevo después — el canvas quedaba con
 * `width: 0` para siempre, invisible, confirmado por un usuario real (no
 * solo en la herramienta de navegador de esta sesión). Medir el viewport
 * directamente elimina la dependencia del timing de layout del padre por
 * completo — es lo que el canvas fixed realmente cubre. */
export function sizeCanvasToViewport(canvas: HTMLCanvasElement): {
  width: number;
  height: number;
} {
  const width = document.documentElement.clientWidth;
  const height = document.documentElement.clientHeight;
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  canvas.width = Math.max(1, Math.round(width * dpr));
  canvas.height = Math.max(1, Math.round(height * dpr));
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  const ctx = canvas.getContext("2d");
  ctx?.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { width, height };
}
