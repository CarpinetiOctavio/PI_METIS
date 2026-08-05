import { useEffect, useRef } from "react";
import { hexToRgba, prefersReducedMotion, readCssVar, sizeCanvasToViewport } from "./canvasUtils";

// Fondo de la aplicación (B2, plan pasada4 §4). Refuerza el paso de 28px de
// la retícula técnica que ya existe en .app-shell (global.css) — no la
// reemplaza. DECISIÓN 045: Canvas 2D + requestAnimationFrame, sin
// dependencias nuevas.
const GRID_STEP = 28;
const INFLUENCE_RADIUS = 130;
const BASE_RADIUS = 1.1;
const HOVER_RADIUS = 2.6;
const BASE_OPACITY = 0.16;
const HOVER_OPACITY = 0.85;
const DRIFT_AMPLITUDE = 2;

export function DotFieldBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let width = 0;
    let height = 0;
    let pointerX = -9999;
    let pointerY = -9999;
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
      ctx!.clearRect(0, 0, width, height);
      const cols = Math.ceil(width / GRID_STEP) + 1;
      const rows = Math.ceil(height / GRID_STEP) + 1;
      for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
          const baseX = col * GRID_STEP;
          const baseY = row * GRID_STEP;
          const x = baseX + Math.sin(t / 4000 + row) * DRIFT_AMPLITUDE;
          const y = baseY + Math.cos(t / 4000 + col) * DRIFT_AMPLITUDE;
          const dx = x - pointerX;
          const dy = y - pointerY;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const influence = Math.max(0, 1 - dist / INFLUENCE_RADIUS);
          const radius = BASE_RADIUS + (HOVER_RADIUS - BASE_RADIUS) * influence;
          const opacity = BASE_OPACITY + (HOVER_OPACITY - BASE_OPACITY) * influence;
          ctx!.beginPath();
          ctx!.arc(x, y, radius, 0, Math.PI * 2);
          ctx!.fillStyle = hexToRgba(accent, opacity);
          ctx!.fill();
        }
      }
    }

    function loop(t: number) {
      if (tabVisible && inViewport) {
        draw(t);
      }
      rafId = window.requestAnimationFrame(loop);
    }

    resize();

    if (prefersReducedMotion()) {
      // Guarda 1 (B4): un frame estático, sin arrancar el loop — no basta
      // con acelerar la animación, hay que no gastar CPU en absoluto.
      draw(0);
    } else {
      rafId = window.requestAnimationFrame(loop);
    }

    // window resize, no ResizeObserver sobre el padre — el canvas es
    // fixed/inset:0, lo que le importa es el viewport, no el layout del
    // padre (ver comentario de sizeCanvasToViewport en canvasUtils.ts).
    window.addEventListener("resize", resize);

    function handlePointerMove(e: PointerEvent) {
      pointerX = e.clientX;
      pointerY = e.clientY;
    }
    function handlePointerLeave() {
      pointerX = -9999;
      pointerY = -9999;
    }
    // pointer-events: none en el canvas — escuchar en window, el puntero
    // siempre está "sobre" el contenido real que está encima.
    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerleave", handlePointerLeave);

    function handleVisibilityChange() {
      tabVisible = document.visibilityState === "visible";
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);

    const intersectionObserver = new IntersectionObserver(([entry]) => {
      inViewport = entry?.isIntersecting ?? true;
    });
    intersectionObserver.observe(canvas);

    return () => {
      // Guarda 2 (B4): cancelar el rAF en la limpieza — sin esto, bajo
      // StrictMode (que monta dos veces) quedan dos loops corriendo para
      // siempre. Misma clase de bug que F1
      // (docs/frontend/informe-diagnostico-ui-rota.md).
      if (rafId !== null) window.cancelAnimationFrame(rafId);
      window.removeEventListener("resize", resize);
      intersectionObserver.disconnect();
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerleave", handlePointerLeave);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

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
