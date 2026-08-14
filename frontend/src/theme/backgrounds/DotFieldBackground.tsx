import { useRef } from "react";
import { hexToRgba, readCssVar } from "./canvasUtils";
import { useCanvasAnimationLoop } from "./useCanvasAnimationLoop";
import { useMotion } from "../MotionProvider";

// Fondo de la aplicación (B2, plan pasada4 §4). Refuerza el paso de 28px de
// la retícula técnica que ya existe en .app-shell (global.css) — no la
// reemplaza. DECISIÓN 045: Canvas 2D + requestAnimationFrame, sin
// dependencias nuevas.
//
// A2 (plan post-avance) — con nivel "media", el paso pasa de 28 a 56 (una
// cuarta parte de los puntos en 2D) y se apaga el seguimiento del puntero
// por completo (setupExtra condicional más abajo).
const GRID_STEP_ALTA = 28;
const GRID_STEP_MEDIA = 56;
const INFLUENCE_RADIUS = 130;
const BASE_RADIUS = 1.1;
const HOVER_RADIUS = 2.6;
const BASE_OPACITY = 0.16;
const HOVER_OPACITY = 0.85;
const DRIFT_AMPLITUDE = 2;

export function DotFieldBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { effectiveLevel } = useMotion();
  const trackPointer = effectiveLevel === "alta";
  const gridStep = effectiveLevel === "media" ? GRID_STEP_MEDIA : GRID_STEP_ALTA;
  // pointer-events: none en el canvas — escuchar en window, el puntero
  // siempre está "sobre" el contenido real que está encima. Vive en un ref
  // (no en el hook compartido) porque el tracking de puntero es específico
  // de este fondo — DotFieldBackground es el único de los tres cuyo dibujo
  // reacciona a dónde está el mouse; GridScanBackground/ThreadsBackground no
  // tienen ningún concepto de puntero, y el hook no debe adquirirlo solo
  // para este consumidor.
  const pointerRef = useRef({ x: -9999, y: -9999 });

  useCanvasAnimationLoop(
    canvasRef,
    (t, ctx, width, height) => {
      const accent = readCssVar("--glow", "#7dd3e8");
      ctx.clearRect(0, 0, width, height);
      const cols = Math.ceil(width / gridStep) + 1;
      const rows = Math.ceil(height / gridStep) + 1;
      for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
          const baseX = col * gridStep;
          const baseY = row * gridStep;
          const x = baseX + Math.sin(t / 4000 + row) * DRIFT_AMPLITUDE;
          const y = baseY + Math.cos(t / 4000 + col) * DRIFT_AMPLITUDE;
          const dx = x - pointerRef.current.x;
          const dy = y - pointerRef.current.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const influence = Math.max(0, 1 - dist / INFLUENCE_RADIUS);
          const radius = BASE_RADIUS + (HOVER_RADIUS - BASE_RADIUS) * influence;
          const opacity = BASE_OPACITY + (HOVER_OPACITY - BASE_OPACITY) * influence;
          ctx.beginPath();
          ctx.arc(x, y, radius, 0, Math.PI * 2);
          ctx.fillStyle = hexToRgba(accent, opacity);
          ctx.fill();
        }
      }
    },
    effectiveLevel,
    // setupExtra: registrado por el hook solo si hay contexto 2D disponible
    // (mismo punto en el que vivía este registro antes de la extracción) —
    // ver useCanvasAnimationLoop.ts para el contrato completo. A2 (plan
    // post-avance) — "media" apaga el seguimiento del puntero por completo,
    // no solo lo atenúa: sin listener, pointerRef se queda fijo en
    // (-9999,-9999) y la influencia de hover siempre da 0, que es
    // exactamente el efecto buscado sin necesitar una segunda rama en
    // draw(). motionLevel ya es dependencia del efecto (ver
    // useCanvasAnimationLoop.ts), así que pasar de "alta" a "media"
    // desregistra el listener de verdad, no solo dibuja distinto.
    trackPointer
      ? () => {
          function handlePointerMove(e: PointerEvent) {
            pointerRef.current = { x: e.clientX, y: e.clientY };
          }
          function handlePointerLeave() {
            pointerRef.current = { x: -9999, y: -9999 };
          }
          window.addEventListener("pointermove", handlePointerMove);
          window.addEventListener("pointerleave", handlePointerLeave);
          return () => {
            window.removeEventListener("pointermove", handlePointerMove);
            window.removeEventListener("pointerleave", handlePointerLeave);
          };
        }
      : undefined,
  );

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{
        // z-index: -1, no 0 — un z-index de 0 en un elemento posicionado
        // pinta DESPUÉS del contenido normal sin posicionar (TopBar, <main>)
        // dentro del mismo stacking context (CSS2.1 Apéndice E, pasos 3 y
        // 6), así que taparía la UI en vez de quedar detrás. Negativo es lo
        // que garantiza "detrás de todo" sin tener que tocar cada
        // consumidor (.card ya es opaco, pero TopBar/<main> no tienen
        // position propio).
        position: "fixed",
        inset: 0,
        zIndex: -1,
        pointerEvents: "none",
      }}
    />
  );
}
