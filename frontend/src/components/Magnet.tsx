import { useRef, type CSSProperties, type ReactNode, type MouseEvent } from "react";
import { gsap } from "gsap";
import { prefersReducedMotion } from "../theme/motion";

/**
 * Confirmado tras verificación manual (Bloque C, 05/08/2026, veredicto
 * final) — ver frontend/src/experimental/README.md para el detalle de la
 * exploración descartable que llevó a este veredicto. El elemento se
 * desplaza levemente hacia el cursor dentro de un radio, y vuelve a su
 * lugar con un resorte suave (gsap) al salir.
 *
 * Alcance: solo botones primarios (.b-pri) por decisión explícita — no
 * envolver .b-sec ni otros elementos sin confirmar antes.
 */
const RADIUS = 60;
const STRENGTH = 0.35;

export function Magnet({
  children,
  className,
  style,
}: Readonly<{ children: ReactNode; className?: string; style?: CSSProperties }>) {
  const ref = useRef<HTMLSpanElement>(null);

  function handleMouseMove(event: MouseEvent<HTMLSpanElement>) {
    if (prefersReducedMotion()) return;
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = event.clientX - cx;
    const dy = event.clientY - cy;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist > RADIUS) return;
    gsap.to(el, { x: dx * STRENGTH, y: dy * STRENGTH, duration: 0.3, ease: "power2.out" });
  }

  function handleMouseLeave() {
    const el = ref.current;
    if (!el) return;
    gsap.to(el, { x: 0, y: 0, duration: 0.5, ease: "elastic.out(1, 0.4)" });
  }

  return (
    <span
      ref={ref}
      className={className}
      style={{ display: "inline-block", ...style }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {children}
    </span>
  );
}
