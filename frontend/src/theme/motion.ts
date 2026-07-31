// Compartido por los fondos animados (theme/backgrounds/canvasUtils.ts) y
// cualquier animación JS-driven fuera de Canvas (CountUp) — un solo lugar
// para el chequeo de prefers-reduced-motion.
export function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}
