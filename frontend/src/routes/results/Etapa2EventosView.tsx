import { useState } from "react";
import { formatNum } from "../../i18n/format";
import type { Etapa2EventosState } from "../../api/sse";
import type { PuntoEmpirico } from "../../api/types";
import { Etapa2AjusteChart } from "./Etapa2AjusteChart";
import { Etapa2EventosChart } from "./Etapa2EventosChart";
import "./Etapa2EventosView.css";

/**
 * Eventos de diseño de la distribución+método elegidos — payload real de
 * result_etapa2_eventos. Siempre de solo lectura (elegir un período de
 * retorno distinto solo cambia qué valor se muestra, no dispara ningún
 * request nuevo — los ocho ya llegaron calculados juntos).
 *
 * `puntosEmpiricos` viene del evento result_etapa2_ranking (Etapa2RankingState),
 * previo a esta pausa — siempre disponible en este punto del flujo (Bloque C).
 */
export function Etapa2EventosView({
  eventos,
  puntosEmpiricos,
}: Readonly<{ eventos: Etapa2EventosState; puntosEmpiricos: PuntoEmpirico[] }>) {
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

      <div style={{ marginTop: 24, textAlign: "left" }}>
        <h3 className="h" style={{ fontSize: 13, marginBottom: 8 }}>
          Gráfico de ajuste
        </h3>
        <Etapa2AjusteChart
          puntosEmpiricos={puntosEmpiricos}
          curvaAjuste={eventos.curva_ajuste}
          distribucion={eventos.distribucion}
          metodo={eventos.metodo}
        />
      </div>

      <div style={{ marginTop: 24, textAlign: "left" }}>
        <h3 className="h" style={{ fontSize: 13, marginBottom: 8 }}>
          Gráfico de eventos de diseño
        </h3>
        <Etapa2EventosChart
          eventosDiseno={eventos.eventos_diseno}
          curvaAjuste={eventos.curva_ajuste}
        />
      </div>
    </div>
  );
}
