import { useState } from "react";
import { formatNum } from "../../i18n/format";
import type { Etapa2EventosState } from "../../api/sse";
import "./Etapa2EventosView.css";

/**
 * Eventos de diseño de la distribución+método elegidos — payload real de
 * result_etapa2_eventos. Siempre de solo lectura (elegir un período de
 * retorno distinto solo cambia qué valor se muestra, no dispara ningún
 * request nuevo — los ocho ya llegaron calculados juntos).
 */
export function Etapa2EventosView({
  eventos,
}: Readonly<{ eventos: Etapa2EventosState }>) {
  const periodos = eventos.eventos_diseno.map((e) => e.periodo_retorno);
  const [seleccionado, setSeleccionado] = useState<number | null>(
    periodos[0] ?? null,
  );

  const actual = eventos.eventos_diseno.find(
    (e) => e.periodo_retorno === seleccionado,
  );

  return (
    <div className="etapa2-eventos card soft" style={{ textAlign: "center", padding: 22 }}>
      <p className="sub" style={{ marginBottom: 12 }}>
        {eventos.distribucion} · {eventos.metodo}
      </p>
      <div className="chips" style={{ justifyContent: "center", marginBottom: 14 }}>
        {periodos.map((p) => (
          <button
            key={p}
            type="button"
            className={`chip${p === seleccionado ? " on" : ""}`}
            aria-pressed={p === seleccionado}
            onClick={() => setSeleccionado(p)}
          >
            {p}
          </button>
        ))}
      </div>
      <div
        className="fn"
        style={{ textTransform: "uppercase", letterSpacing: 0.5, fontSize: 10 }}
      >
        Valor de diseño · T = {seleccionado} años
      </div>
      <div className="num" style={{ fontSize: 38, fontWeight: 700 }}>
        {actual ? formatNum(actual.valor) : "—"}
      </div>
      {actual && actual.valor === null && (
        <p className="fn" style={{ marginTop: 8 }}>
          No se pudo calcular el evento de diseño para este período de retorno.
        </p>
      )}
    </div>
  );
}
