import { useRef, type ReactNode, type MouseEvent } from "react";
import { useMotion } from "../theme/MotionProvider";
import "./SpotlightCard.css";

/**
 * Confirmado tras verificación manual (Bloque C, 05/08/2026, veredicto
 * final) — ver PRs anteriores de esta pasada (#33-#35) para el detalle de
 * la exploración descartable que llevó a este veredicto.
 *
 * Un resplandor radial sigue al cursor sobre la tarjeta. A diferencia de
 * Magnet/SpecularHighlight (wrappers que envuelven un elemento ajeno), este
 * componente SÍ renderiza el <div class="card"> — reemplaza el div plano
 * en vez de envolverlo, porque el brillo necesita `overflow: hidden` +
 * `position: relative` en el MISMO elemento que ya tiene el border-radius
 * de `.card` (global.css) para recortarse correctamente en las esquinas.
 *
 * Bug corregido en la exploración (ronda 1): el resplandor vivía en
 * `.exp-spotlight-card::before`, pero `.card` (global.css) YA usa `::before`
 * para el corchete decorativo de esquina (10x10px fijo) — dos reglas sobre
 * el mismo pseudo-elemento se mezclan propiedad por propiedad, no se
 * reemplazan, así que el resplandor quedaba colapsado a una cajita en una
 * esquina. Acá el brillo es un `<div>` real (`.spotlight-card__glow`),
 * hermano del contenido — sin pisar ningún pseudo-elemento que `.card` ya
 * use.
 *
 * Alcance: tarjetas de listado (historial, ranking) por decisión explícita
 * — no aplicar a tarjetas de contenido denso (resultados, formularios) sin
 * confirmar antes.
 */
export function SpotlightCard({
  children,
  className,
}: Readonly<{ children: ReactNode; className?: string }>) {
  const ref = useRef<HTMLDivElement>(null);
  // A2 (plan post-avance) — a diferencia de Magnet/SpecularHighlight, este
  // componente SÍ renderiza el <div class="card"> real (ver el comentario
  // de arriba) — "sin envoltorio reactivo" acá significa sin el brillo que
  // sigue al mouse, no sin el div. La estructura/clase se conserva siempre;
  // solo se omiten el listener y el <div> del brillo en media/off.
  const { effectiveLevel } = useMotion();
  const spotlightEnabled = effectiveLevel === "alta";

  function handleMouseMove(event: MouseEvent<HTMLDivElement>) {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    el.style.setProperty("--spot-x", `${event.clientX - rect.left}px`);
    el.style.setProperty("--spot-y", `${event.clientY - rect.top}px`);
  }

  return (
    <div
      ref={ref}
      className={`card spotlight-card ${className ?? ""}`}
      onMouseMove={spotlightEnabled ? handleMouseMove : undefined}
    >
      {spotlightEnabled && <div className="spotlight-card__glow" aria-hidden="true" />}
      <div className="spotlight-card__content">{children}</div>
    </div>
  );
}
