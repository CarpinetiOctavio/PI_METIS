import { useEffect, useRef } from "react";
import { hexToRgba, prefersReducedMotion, readCssVar, sizeCanvasToViewport } from "./canvasUtils";

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
// Núcleo blanco-caliente del barrido — mismo motivo que el punto anterior:
// en tema claro, --acc es oscuro (necesita contraste como texto/ícono en
// otros lugares), así que una banda "glow" pintada solo con --acc se lee
// como una sombra/mancha oscura sobre fondo claro, no como un brillo. Un
// núcleo blanco en el centro del gradiente, con el acento del tema en los
// bordes, se lee como una fuente de luz real en los dos temas.
const CORE_COLOR = "#ffffff";

export function GridScanBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = 0;
    let height = 0;
    let rafId: number | null = null;
    let tabVisible = document.visibilityState === "visible";
    let inViewport = true;

    function resize() {
      const size = sizeCanvasToViewport(canvas!);
      width = size.width;
      height = size.height;
    }

    function draw(t: number) {
      const accent = readCssVar("--acc", "#0e7490");
      const line = readCssVar("--line", "#dee5eb");
      ctx!.clearRect(0, 0, width, height);

      const progress = (t % CYCLE_MS) / CYCLE_MS;
      const beamX = progress * (width + TRAIL_WIDTH * 2) - TRAIL_WIDTH;

      // Grilla base, tenue — la retícula que Fase 3 ya especifica.
      ctx!.lineWidth = 1;
      for (let x = 0; x <= width; x += GRID_STEP) {
        const distBehindBeam = beamX - x;
        const inTrail = distBehindBeam >= 0 && distBehindBeam <= TRAIL_WIDTH;
        const trailFade = inTrail ? 1 - distBehindBeam / TRAIL_WIDTH : 0;
        const opacity = BASE_LINE_OPACITY + (SWEEP_LINE_OPACITY - BASE_LINE_OPACITY) * trailFade;
        ctx!.strokeStyle = inTrail ? hexToRgba(accent, opacity) : hexToRgba(line, BASE_LINE_OPACITY);
        ctx!.beginPath();
        ctx!.moveTo(x, 0);
        ctx!.lineTo(x, height);
        ctx!.stroke();
      }
      for (let y = 0; y <= height; y += GRID_STEP) {
        ctx!.strokeStyle = hexToRgba(line, BASE_LINE_OPACITY);
        ctx!.beginPath();
        ctx!.moveTo(0, y);
        ctx!.lineTo(width, y);
        ctx!.stroke();
      }

      // El barrido en sí — banda vertical con glow, encima de la grilla.
      // Núcleo blanco al centro, acento del tema en los bordes (ver
      // CORE_COLOR más arriba) — se lee como brillo real en los dos temas.
      const gradient = ctx!.createLinearGradient(beamX - 14, 0, beamX + 14, 0);
      gradient.addColorStop(0, hexToRgba(accent, 0));
      gradient.addColorStop(0.35, hexToRgba(accent, BEAM_OPACITY * 0.55));
      gradient.addColorStop(0.5, hexToRgba(CORE_COLOR, BEAM_OPACITY));
      gradient.addColorStop(0.65, hexToRgba(accent, BEAM_OPACITY * 0.55));
      gradient.addColorStop(1, hexToRgba(accent, 0));
      ctx!.fillStyle = gradient;
      ctx!.fillRect(beamX - 14, 0, 28, height);
    }

    function loop(t: number) {
      if (tabVisible && inViewport) {
        draw(t);
      }
      rafId = window.requestAnimationFrame(loop);
    }

    resize();

    if (prefersReducedMotion()) {
      draw(0);
    } else {
      rafId = window.requestAnimationFrame(loop);
    }

    // window resize, no ResizeObserver sobre el padre — el canvas es
    // fixed/inset:0, lo que le importa es el viewport, no el layout del
    // padre (ver comentario de sizeCanvasToViewport en canvasUtils.ts).
    window.addEventListener("resize", resize);

    function handleVisibilityChange() {
      tabVisible = document.visibilityState === "visible";
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);

    const intersectionObserver = new IntersectionObserver(([entry]) => {
      inViewport = entry?.isIntersecting ?? true;
    });
    intersectionObserver.observe(canvas);

    return () => {
      if (rafId !== null) window.cancelAnimationFrame(rafId);
      window.removeEventListener("resize", resize);
      intersectionObserver.disconnect();
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

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
