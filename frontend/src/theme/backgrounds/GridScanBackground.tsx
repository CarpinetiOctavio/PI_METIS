import { useRef } from "react";
import { hexToRgba, readCssVar } from "./canvasUtils";
import { useCanvasAnimationLoop } from "./useCanvasAnimationLoop";
import { useMotion } from "../MotionProvider";

// Fondo de la puerta de entrada (B3, plan pasada4 §4). Hermano de
// DotFieldBackground: misma retícula de 28px y el mismo acento, pero acá el
// protagonista es el barrido luminoso ("línea de escaneo con glow" — Fase 2,
// nunca implementado antes de esta pasada, G3). Intensidad mayor que
// DotFieldBackground: es la primera pantalla, no protege tablas de datos.
const GRID_STEP = 28;
const CYCLE_MS = 6000;
// Feedback de verificación manual (Bloque C, 05/08/2026): el trail se veía
// débil y se apagaba muy rápido — TRAIL_WIDTH 240 -> 360 (persiste más
// distancia detrás del barrido), SWEEP_LINE_OPACITY 0.75 -> 0.92 (color más
// fuerte cerca del barrido).
const TRAIL_WIDTH = 360;
const BASE_LINE_OPACITY = 0.12;
const SWEEP_LINE_OPACITY = 0.92;
const BEAM_OPACITY = 0.9;
// Núcleo blanco-caliente del barrido — en tema claro, --glow es un cian claro
// que se lee como luz sobre fondo claro. Un núcleo blanco en el centro del
// gradiente con --glow en los bordes se lee como una fuente de luz real en los
// dos temas.
const CORE_COLOR = "#ffffff";

export function GridScanBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { effectiveLevel } = useMotion();
  // A2 (plan post-avance) — "media" conserva la grilla base (lo menos
  // llamativo del fondo) y apaga el haz de barrido en sí, que es el
  // elemento más activo/llamativo. Se lee en cada frame (no una vez en el
  // cuerpo del efecto) por el mismo motivo que --glow/--line: drawRef ya
  // se actualiza en cada render sin reiniciar el loop, así que el cambio
  // de nivel se refleja en el siguiente frame sin esperar un remount.
  const drawBeam = effectiveLevel === "alta";

  useCanvasAnimationLoop(
    canvasRef,
    (t, ctx, width, height) => {
      const accent = readCssVar("--glow", "#7dd3e8");
      const line = readCssVar("--line", "#d7dfe7");
      ctx.clearRect(0, 0, width, height);

      const progress = (t % CYCLE_MS) / CYCLE_MS;
      const beamX = progress * (width + TRAIL_WIDTH * 2) - TRAIL_WIDTH;

      // Grilla base, tenue — la retícula que Fase 3 ya especifica. Se
      // conserva siempre; solo el trail/beam de abajo depende de drawBeam.
      ctx.lineWidth = 1;
      for (let x = 0; x <= width; x += GRID_STEP) {
        const distBehindBeam = beamX - x;
        const inTrail = drawBeam && distBehindBeam >= 0 && distBehindBeam <= TRAIL_WIDTH;
        const trailFade = inTrail ? 1 - distBehindBeam / TRAIL_WIDTH : 0;
        const opacity = BASE_LINE_OPACITY + (SWEEP_LINE_OPACITY - BASE_LINE_OPACITY) * trailFade;
        ctx.strokeStyle = inTrail ? hexToRgba(accent, opacity) : hexToRgba(line, BASE_LINE_OPACITY);
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y <= height; y += GRID_STEP) {
        ctx.strokeStyle = hexToRgba(line, BASE_LINE_OPACITY);
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      if (!drawBeam) return;

      // El barrido en sí — banda vertical con glow, encima de la grilla.
      // Núcleo blanco al centro, acento del tema en los bordes (ver
      // CORE_COLOR más arriba) — se lee como brillo real en los dos temas.
      const gradient = ctx.createLinearGradient(beamX - 14, 0, beamX + 14, 0);
      gradient.addColorStop(0, hexToRgba(accent, 0));
      gradient.addColorStop(0.35, hexToRgba(accent, BEAM_OPACITY * 0.55));
      gradient.addColorStop(0.5, hexToRgba(CORE_COLOR, BEAM_OPACITY));
      gradient.addColorStop(0.65, hexToRgba(accent, BEAM_OPACITY * 0.55));
      gradient.addColorStop(1, hexToRgba(accent, 0));
      ctx.fillStyle = gradient;
      ctx.fillRect(beamX - 14, 0, 28, height);
    },
    effectiveLevel,
  );

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{
        // Ver el comentario equivalente en DotFieldBackground.tsx — z-index
        // negativo, no 0, para quedar detrás del contenido normal sin
        // posicionar dentro del mismo stacking context.
        position: "fixed",
        inset: 0,
        zIndex: -1,
        pointerEvents: "none",
      }}
    />
  );
}
