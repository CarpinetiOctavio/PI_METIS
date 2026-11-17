import { useRef, type CSSProperties, type ReactNode, type MouseEvent } from "react";
import { useMotion } from "../theme/MotionProvider";
import "./SpecularHighlight.css";

/**
 * Confirmado tras verificación manual (Bloque C, 05/08/2026, veredicto
 * final) — ver frontend/src/experimental/README.md. Highlight especular
 * que sigue al cursor sobre la superficie del botón envuelto.
 *
 * Bug corregido en la exploración (ronda 2): un highlight blanco puro se
 * lee bien sobre superficies oscuras pero se pierde sin contraste sobre
 * superficies claras. La mezcla con --acc (en SpecularHighlight.css) lo
 * mantiene con el mismo carácter en los dos temas.
 *
 * Alcance: solo botones primarios (.b-pri) por decisión explícita — envuelve
 * el botón real sin cambiar su estilo, solo agrega la capa de brillo encima.
 */
export function SpecularHighlight({
  children,
  className,
  style,
}: Readonly<{ children: ReactNode; className?: string; style?: CSSProperties }>) {
  const ref = useRef<HTMLSpanElement>(null);
  // A2 (plan post-avance) — con "media"/"off" no hay brillo que siga al
  // mouse, pero el <span> se conserva (className/style siguen siendo
  // load-bearing en varios llamadores reales, ej. `width: "100%"` en
  // Etapa2RankingView) — mismo criterio que Magnet.tsx.
  const { effectiveLevel } = useMotion();
  const highlightEnabled = effectiveLevel === "alta";

  function handleMouseMove(event: MouseEvent<HTMLSpanElement>) {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    el.style.setProperty("--spec-x", `${event.clientX - rect.left}px`);
    el.style.setProperty("--spec-y", `${event.clientY - rect.top}px`);
  }

  return (
    <span
      ref={ref}
      className={`specular-highlight ${className ?? ""}`}
      style={style}
      onMouseMove={highlightEnabled ? handleMouseMove : undefined}
    >
      {children}
    </span>
  );
}
