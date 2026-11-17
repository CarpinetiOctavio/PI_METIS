// Compartido por los fondos animados (theme/backgrounds/canvasUtils.ts),
// cualquier animación JS-driven fuera de Canvas (CountUp, Magnet), y el
// selector de intensidad de la app (MotionProvider.tsx) — un solo lugar
// para todo lo relacionado a prefers-reduced-motion y al nivel de
// movimiento elegido (plan post-avance, Bloque A).
export type MotionLevel = "alta" | "media" | "off";

export function prefersReducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

// A2 (plan post-avance) — el sistema operativo manda: si el usuario pidió
// movimiento reducido a nivel SO, el nivel efectivo es "off" sin importar
// lo que haya elegido dentro de la app. Regla de accesibilidad, no
// configurable — MotionProvider es el único llamador real, pero se expone
// acá (no inline en el provider) para que sea una única fuente de verdad
// testeable sin renderizar React.
export function resolveMotionLevel(stored: MotionLevel): MotionLevel {
  return prefersReducedMotion() ? "off" : stored;
}
