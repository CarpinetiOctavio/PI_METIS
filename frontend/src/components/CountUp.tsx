import { useEffect, useRef } from "react";
import { formatNum } from "../i18n/format";
import { prefersReducedMotion } from "../theme/motion";
import "./CountUp.css";

const DURATION_MS = 420; // --t-slow

// Aproximación de cubic-bezier(.2,.7,.2,1) (--ease-out) para interpolar en
// JS — no hay forma de evaluar un cubic-bezier de CSS desde acá; un ease-out
// cúbico estándar da una curva de salida muy similar (arranca rápido,
// decelera al final).
function easeOut(t: number): number {
  return 1 - Math.pow(1 - t, 3);
}

interface CountUpProps {
  value: number | null | undefined;
}

/**
 * Plan pasada4 §3 A5 pide "contadores que suben hasta clavar el
 * estadístico" para estadístico/valor_crítico (StreamPage,
 * Etapa1ResultView) y valor_atípico (modal de Chow). Pero el propio §3 A5
 * exige que ningún test existente necesite `waitFor` por culpa de una
 * animación — y dos tests reales (StreamPage.integration.test.tsx, el
 * `toHaveTextContent("245,70000")` del modal y el `"0,22000"` de una fila
 * expandida) chequean el texto final de forma SÍNCRONA apenas el nodo
 * aparece. Un conteo real que reemplace el texto perdería esa carrera
 * siempre — no es un problema de afinar tiempos, es estructural.
 *
 * Por eso el nodo real (`.count-up__real`, lo que ve Testing Library y un
 * lector de pantalla) muestra el valor final formateado de inmediato,
 * siempre. El conteo visible es una capa puramente decorativa
 * (`::before` con `content: attr(data-count)`, ver CountUp.css) — el
 * contenido generado por CSS nunca forma parte de `.textContent`, así que
 * la capa que interpola cuadro a cuadro es invisible para cualquier
 * aserción o tecnología de asistencia basada en texto.
 */
export function CountUp({ value }: Readonly<CountUpProps>) {
  const finalText = formatNum(value);
  const wrapRef = useRef<HTMLSpanElement>(null);
  const overlayRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (value === null || value === undefined || Number.isNaN(value)) return;
    if (prefersReducedMotion()) return;
    const wrap = wrapRef.current;
    const overlay = overlayRef.current;
    if (!wrap || !overlay) return;

    wrap.classList.add("count-up--animating");
    let rafId: number | null = null;
    const start = performance.now();

    function tick(now: number) {
      const elapsed = now - start;
      const t = Math.min(1, elapsed / DURATION_MS);
      overlay!.setAttribute("data-count", formatNum(value! * easeOut(t)));
      if (t < 1) {
        rafId = window.requestAnimationFrame(tick);
      } else {
        wrap!.classList.remove("count-up--animating");
      }
    }
    rafId = window.requestAnimationFrame(tick);

    return () => {
      if (rafId !== null) window.cancelAnimationFrame(rafId);
      wrap.classList.remove("count-up--animating");
    };
  }, [value]);

  return (
    <span className="count-up" ref={wrapRef}>
      <span className="count-up__real">{finalText}</span>
      <span className="count-up__overlay" ref={overlayRef} aria-hidden="true" />
    </span>
  );
}
