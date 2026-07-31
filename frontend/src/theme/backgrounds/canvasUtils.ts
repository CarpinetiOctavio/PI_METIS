// Compartido por DotFieldBackground y GridScanBackground.

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

export function readCssVar(name: string, fallback: string): string {
  const value = getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
  return value || fallback;
}

export function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

/** DPR + tamaño del contenedor — evita el fondo borroso en pantallas HiDPI
 * (plan pasada4 §4 B4, guarda 4). */
export function sizeCanvasToParent(canvas: HTMLCanvasElement): {
  width: number;
  height: number;
} {
  const parent = canvas.parentElement;
  const width = parent ? parent.clientWidth : window.innerWidth;
  const height = parent ? parent.clientHeight : window.innerHeight;
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  canvas.width = Math.max(1, Math.round(width * dpr));
  canvas.height = Math.max(1, Math.round(height * dpr));
  canvas.style.width = `${width}px`;
  canvas.style.height = `${height}px`;
  const ctx = canvas.getContext("2d");
  ctx?.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { width, height };
}
