import { useEffect, useRef } from "react";
import {
  hexToRgba,
  lerpHex,
  prefersReducedMotion,
  readCssVar,
  secureRandom,
  sizeCanvasToViewport,
} from "./canvasUtils";

// Fondo de todas las pantallas (DECISIÓN 051) — hermano de
// DotFieldBackground/GridScanBackground, mismo z-index negativo, montado
// siempre en RootLayout (sin lazy/Suspense). Hasta DECISIÓN 051 este
// componente usaba Three.js y estaba acotado a "/" vía React.lazy (addendum
// de DECISIÓN 045, docs/decisiones/decision045.md) porque el chunk pesaba
// ~600 KB minificados. Lo que dibujaba de verdad — THREE.Line con
// LineBasicMaterial, cámara ortográfica, sin luces/materiales/profundidad —
// es una polilínea 2D: se reimplementa acá en Canvas 2D, igual que sus dos
// hermanos, y Three.js sale del proyecto.
//
// 18 hilos, paleta de 5 tonos interpolados entre --glow y --acc2 (para que
// en tema claro el inicio de la paleta sea luminoso, no oscuro) — pedido
// explícito de verificación manual (05/08/2026): "que se vieran más líneas y
// de distintos colores", sin salirse de la paleta de la identidad
// "Instrumento". Parámetros conservados sin cambios respecto a la versión
// Three.js.
const THREAD_COUNT = 18;
const POINTS_PER_THREAD = 64;
const PALETTE_STEPS = 5;

/** La versión Three.js trabajaba en NDC (-1..1, cámara ortográfica
 * -1/1/1/-1). La función de onda y los rangos de yOffset/speed se
 * conservan intactos en NDC — este es el único punto nuevo, el mapeo final
 * a píxeles del viewport (mismo criterio que sizeCanvasToViewport: y=1 es
 * "arriba" en NDC, pero "arriba" es y=0 en coordenadas de canvas). */
function ndcToPixel(xNdc: number, yNdc: number, width: number, height: number) {
  return {
    x: ((xNdc + 1) / 2) * width,
    y: ((1 - yNdc) / 2) * height,
  };
}

export function ThreadsBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    // Guarda equivalente a la que protegía `new THREE.WebGLRenderer()`: un
    // contexto 2D no está garantizado (navegador sin soporte, o jsdom sin
    // el mock global de vitest.setup.ts). Sin esto, el resto del efecto
    // asumiría un contexto válido y rompería el render de toda la app en
    // vez de degradar a "sin Threads, los otros fondos siguen andando".
    if (!ctx) return;

    let width = 0;
    let height = 0;

    function resize() {
      const size = sizeCanvasToViewport(canvas!);
      width = size.width;
      height = size.height;
    }

    const accent = readCssVar("--glow", "#22d3ee");
    const accent2 = readCssVar("--acc2", "#c6f84e");
    const palette: string[] = [];
    for (let i = 0; i < PALETTE_STEPS; i++) {
      palette.push(lerpHex(accent, accent2, i / (PALETTE_STEPS - 1)));
    }

    const threads = Array.from({ length: THREAD_COUNT }, (_, i) => ({
      color: palette[i % palette.length],
      opacity: 0.14 + (i / THREAD_COUNT) * 0.14,
      seed: secureRandom() * 1000,
      yOffset: (i / (THREAD_COUNT - 1)) * 2 - 1,
      speed: 0.15 + secureRandom() * 0.15,
    }));

    // Mismas guardas que DotFieldBackground/GridScanBackground (B3): sin
    // esto, un rAF corriendo en pestaña oculta o fuera de viewport es el
    // mismo desperdicio de CPU/batería que ya se evitó para los otros dos
    // fondos.
    let tabVisible = document.visibilityState === "visible";
    let inViewport = true;
    let rafId: number | null = null;

    function draw(t: number) {
      const time = t / 1000;
      ctx!.clearRect(0, 0, width, height);
      ctx!.lineWidth = 1;
      for (const { color, opacity, seed, yOffset, speed } of threads) {
        ctx!.strokeStyle = hexToRgba(color, opacity);
        ctx!.beginPath();
        for (let p = 0; p < POINTS_PER_THREAD; p++) {
          const xNdc = (p / (POINTS_PER_THREAD - 1)) * 2 - 1;
          const wave =
            Math.sin(xNdc * 3 + time * speed + seed) * 0.15 +
            Math.sin(xNdc * 7 - time * speed * 1.7 + seed) * 0.05;
          const { x, y } = ndcToPixel(xNdc, yOffset + wave, width, height);
          if (p === 0) {
            ctx!.moveTo(x, y);
          } else {
            ctx!.lineTo(x, y);
          }
        }
        ctx!.stroke();
      }
    }

    function loop(t: number) {
      if (tabVisible && inViewport) draw(t);
      rafId = window.requestAnimationFrame(loop);
    }

    resize();

    if (prefersReducedMotion()) {
      // Guarda 1: un frame estático, sin arrancar el loop.
      draw(0);
    } else {
      rafId = window.requestAnimationFrame(loop);
    }

    // window resize, no ResizeObserver sobre el padre — mismo motivo que
    // DotFieldBackground/GridScanBackground (ver sizeCanvasToViewport en
    // canvasUtils.ts): el canvas es fixed/inset:0, lo que le importa es el
    // viewport, no el layout del padre.
    window.addEventListener("resize", resize);

    function handleVisibilityChange() {
      // Guarda 2: no dibujar en pestaña oculta.
      tabVisible = document.visibilityState === "visible";
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);

    // Guarda 3: no dibujar fuera del viewport.
    const intersectionObserver = new IntersectionObserver(([entry]) => {
      inViewport = entry?.isIntersecting ?? true;
    });
    intersectionObserver.observe(canvas);

    return () => {
      // Guarda 4: cleanup completo — rAF cancelado, los tres listeners
      // desregistrados, observer desconectado. Bajo StrictMode (que monta
      // dos veces) sin esto quedan loops duplicados corriendo para siempre
      // — misma clase de bug que F1
      // (docs/frontend/informe-diagnostico-ui-rota.md).
      if (rafId !== null) window.cancelAnimationFrame(rafId);
      window.removeEventListener("resize", resize);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      intersectionObserver.disconnect();
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{
        // z-index: -1 — mismo criterio que DotFieldBackground/
        // GridScanBackground (ver el comentario equivalente en esos
        // archivos): negativo, no 0, para quedar detrás del contenido
        // normal sin posicionar (TopBar, <main>) dentro del mismo stacking
        // context.
        position: "fixed",
        inset: 0,
        zIndex: -1,
        pointerEvents: "none",
      }}
    />
  );
}
