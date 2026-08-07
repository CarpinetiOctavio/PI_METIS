import { useEffect, useRef, type RefObject } from "react";
import { prefersReducedMotion, sizeCanvasToViewport } from "./canvasUtils";

/** Firma de la función de dibujo que cada fondo le pasa al hook — mismo
 * `draw(t)` que tenían los tres componentes antes de esta extracción, más
 * `ctx`/`width`/`height` explícitos (antes eran variables cerradas sobre el
 * efecto de cada componente; acá viven en el efecto del hook, así que se
 * pasan como argumentos en vez de depender de un closure compartido). */
export type CanvasDrawFn = (
  t: number,
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
) => void;

/**
 * Esqueleto de ciclo de vida compartido por los tres fondos animados
 * (DotFieldBackground, GridScanBackground, ThreadsBackground) — extraído
 * tras el hallazgo de SonarCloud en PR #37 (7.3% de duplicación en código
 * nuevo, umbral 3%; ver task-3-brief.md). Los tres componentes repetían
 * textualmente: obtener el contexto 2D y degradar si es `null`, `resize` vía
 * `sizeCanvasToViewport`, las guardas de reduced-motion/pestaña
 * oculta/fuera-de-viewport, el loop de `requestAnimationFrame` y el cleanup
 * completo. Lo único que varía entre los tres es QUÉ dibujan — eso vive en
 * `draw`, nunca acá.
 *
 * `setupExtra`, si se pasa, corre en el mismo punto del efecto en el que
 * corría el registro de listeners propios en las versiones no extraídas
 * (después de confirmar que hay contexto 2D, antes de arrancar el loop) y
 * DEBE devolver su propia función de cleanup — mismo contrato que el
 * `useEffect` que reemplaza. Es la única escotilla de extensión: le permite
 * a un consumidor puntual (hoy solo DotFieldBackground, tracking de
 * puntero) agregar setup/cleanup propio sin que este hook tenga que saber
 * nada de punteros, mouse, ni de ningún otro dominio específico de un
 * componente. Si no hay contexto 2D, `setupExtra` no corre — mismo
 * comportamiento que las versiones no extraídas, donde el registro de
 * listeners adicionales vivía después de la guarda de contexto, dentro del
 * mismo efecto.
 */
export function useCanvasAnimationLoop(
  canvasRef: RefObject<HTMLCanvasElement>,
  draw: CanvasDrawFn,
  setupExtra?: () => () => void,
): void {
  // draw/setupExtra se guardan en refs, actualizadas en cada render, en vez
  // de ser dependencias del efecto de abajo — ese efecto debe seguir
  // corriendo una sola vez por montaje (igual que los tres componentes
  // originales, todos con deps `[]`), no reiniciar el loop entero (y con
  // él, perder el estado de tabVisible/inViewport/rafId) cada vez que el
  // componente re-renderiza y crea una nueva función draw por identidad.
  const drawRef = useRef(draw);
  drawRef.current = draw;
  const setupExtraRef = useRef(setupExtra);
  setupExtraRef.current = setupExtra;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    // Guarda equivalente a la que protegía `new THREE.WebGLRenderer()` en la
    // versión Three.js original de ThreadsBackground: un contexto 2D no
    // está garantizado (navegador sin soporte, o jsdom sin el mock global de
    // vitest.setup.ts). Sin esto, el resto del efecto asumiría un contexto
    // válido y rompería el render de toda la app en vez de degradar a "sin
    // este fondo, los otros siguen andando encima".
    if (!ctx) return;

    let width = 0;
    let height = 0;

    function resize() {
      const size = sizeCanvasToViewport(canvas!);
      width = size.width;
      height = size.height;
    }

    // Guardas de pestaña oculta / fuera de viewport: sin esto, un rAF
    // corriendo de fondo cuando el usuario ni ve el canvas es CPU/batería
    // desperdiciada por nada.
    let tabVisible = document.visibilityState === "visible";
    let inViewport = true;
    let rafId: number | null = null;

    function loop(t: number) {
      if (tabVisible && inViewport) drawRef.current(t, ctx!, width, height);
      rafId = window.requestAnimationFrame(loop);
    }

    resize();

    if (prefersReducedMotion()) {
      // Guarda de reduced-motion: un frame estático, sin arrancar el loop —
      // no basta con acelerar la animación, hay que no gastar CPU en
      // absoluto.
      drawRef.current(0, ctx, width, height);
    } else {
      rafId = window.requestAnimationFrame(loop);
    }

    // window resize, no ResizeObserver sobre el padre — los tres canvas son
    // fixed/inset:0, lo que les importa es el viewport, no el layout del
    // padre (ver sizeCanvasToViewport en canvasUtils.ts).
    window.addEventListener("resize", resize);

    function handleVisibilityChange() {
      tabVisible = document.visibilityState === "visible";
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);

    // Guarda de fuera de viewport.
    const intersectionObserver = new IntersectionObserver(([entry]) => {
      inViewport = entry?.isIntersecting ?? true;
    });
    intersectionObserver.observe(canvas);

    const cleanupExtra = setupExtraRef.current?.();

    return () => {
      // Cleanup completo: rAF cancelado, los dos listeners (resize,
      // visibilitychange) desregistrados, IntersectionObserver
      // desconectado, y cualquier setup extra de un consumidor puntual (en
      // ese orden no importa cuál primero — ninguno depende de otro). Bajo
      // StrictMode (que monta dos veces) sin esto quedan loops/listeners
      // duplicados corriendo para siempre — misma clase de bug que F1
      // (docs/frontend/informe-diagnostico-ui-rota.md).
      if (rafId !== null) window.cancelAnimationFrame(rafId);
      window.removeEventListener("resize", resize);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      intersectionObserver.disconnect();
      cleanupExtra?.();
    };
    // canvasRef es un RefObject estable (identidad fija durante toda la
    // vida del componente); draw/setupExtra se leen vía ref
    // (drawRef/setupExtraRef) a propósito, para que este efecto siga
    // corriendo una sola vez por montaje, igual que en los tres
    // componentes antes de esta extracción.
  }, [canvasRef]);
}
