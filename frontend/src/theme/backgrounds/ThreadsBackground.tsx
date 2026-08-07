import { useRef } from "react";
import { hexToRgba, lerpHex, readCssVar, secureRandom } from "./canvasUtils";
import { useCanvasAnimationLoop } from "./useCanvasAnimationLoop";

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

interface Thread {
  opacity: number;
  seed: number;
  yOffset: number;
  speed: number;
}

export function ThreadsBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Generado una sola vez por instancia del componente, no en cada frame —
  // mismo criterio que la versión no extraída (el array vivía fuera de
  // draw(), dentro del efecto que corre una sola vez por montaje). Un
  // useRef con init perezoso logra lo mismo sin depender de la vida del
  // efecto del hook: los seeds/velocidades de cada hilo se sortean al
  // montar y se mantienen fijos mientras el componente esté vivo.
  const threadsRef = useRef<Thread[]>();
  threadsRef.current ??= Array.from({ length: THREAD_COUNT }, (_, i) => ({
    opacity: 0.14 + (i / THREAD_COUNT) * 0.14,
    seed: secureRandom() * 1000,
    yOffset: (i / (THREAD_COUNT - 1)) * 2 - 1,
    speed: 0.15 + secureRandom() * 0.15,
  }));

  useCanvasAnimationLoop(canvasRef, (t, ctx, width, height) => {
    const time = t / 1000;
    // Leídos en cada frame — no en el cuerpo del efecto — para que un
    // toggle de tema en caliente (ThemeProvider pisa `data-mode`, no
    // remonta el componente) se refleje sin esperar a un reload.
    const accent = readCssVar("--glow", "#22d3ee");
    const accent2 = readCssVar("--acc2", "#c6f84e");
    const palette: string[] = [];
    for (let i = 0; i < PALETTE_STEPS; i++) {
      palette.push(lerpHex(accent, accent2, i / (PALETTE_STEPS - 1)));
    }

    ctx.clearRect(0, 0, width, height);
    ctx.lineWidth = 1;
    threadsRef.current!.forEach(({ opacity, seed, yOffset, speed }, i) => {
      ctx.strokeStyle = hexToRgba(palette[i % palette.length], opacity);
      ctx.beginPath();
      for (let p = 0; p < POINTS_PER_THREAD; p++) {
        const xNdc = (p / (POINTS_PER_THREAD - 1)) * 2 - 1;
        const wave =
          Math.sin(xNdc * 3 + time * speed + seed) * 0.15 +
          Math.sin(xNdc * 7 - time * speed * 1.7 + seed) * 0.05;
        const { x, y } = ndcToPixel(xNdc, yOffset + wave, width, height);
        if (p === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
    });
  });

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
