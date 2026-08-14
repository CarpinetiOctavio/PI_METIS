import { useRef, type CSSProperties, type ReactNode, type MouseEvent } from "react";
import { gsap } from "gsap";
import { prefersReducedMotion } from "../theme/motion";
import { useMotion } from "../theme/MotionProvider";

/**
 * Confirmado tras verificación manual (Bloque C, 05/08/2026, veredicto
 * final) — ver frontend/src/experimental/README.md para el detalle de la
 * exploración descartable que llevó a este veredicto. El elemento se
 * desplaza levemente hacia el cursor dentro de un radio, y vuelve a su
 * lugar con un resorte suave (gsap) al salir.
 *
 * Alcance: solo botones primarios (.b-pri) por decisión explícita — no
 * envolver .b-sec ni otros elementos sin confirmar antes.
 *
 * A2 (plan post-avance) — con nivel "media"/"off" no hay desplazamiento en
 * absoluto (`className`/`style` sí se conservan: varios llamadores reales
 * pasan `width`/`margin` de layout en `style`, no solo decoración — un
 * <>{children}</> literal, como haría un wrapper verdaderamente "puro",
 * rompería ese layout). `prefersReducedMotion()` se mantiene dentro de
 * `handleMouseMove` como red de seguridad adicional (mismo criterio de
 * defensa en profundidad que useCanvasAnimationLoop.ts) — en la práctica
 * ya no debería activarse nunca sin que `effectiveLevel` también sea "off"
 * (MotionProvider resuelve el nivel efectivo mirando la misma preferencia
 * del sistema), pero es la que ya cubren los tests existentes de este
 * componente sin necesitar un <MotionProvider> real.
 */
const RADIUS = 60;
const STRENGTH = 0.35;

export function Magnet({
  children,
  className,
  style,
}: Readonly<{ children: ReactNode; className?: string; style?: CSSProperties }>) {
  const ref = useRef<HTMLSpanElement>(null);
  const { effectiveLevel } = useMotion();
  const magnetEnabled = effectiveLevel === "alta";

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
      onMouseMove={magnetEnabled ? handleMouseMove : undefined}
      onMouseLeave={magnetEnabled ? handleMouseLeave : undefined}
    >
      {children}
    </span>
  );
}
