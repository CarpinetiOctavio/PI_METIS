import { useState } from "react";
import type { AtipicoDetectado, DecisionAtipico } from "../../api/types";
import { formatNum } from "../../i18n/format";

/**
 * Cuerpo de la pausa de Chow — DECISIÓN 079. Una fila por atípico detectado
 * (todos los valores fuera de los umbrales de Bulletin 17B, no solo el más
 * extremo), con dos botones iguales por fila y sin opción preseleccionada.
 * "Continuar" se habilita recién cuando todas las filas tienen decisión: el
 * backend rechaza una decisión incompleta (OUTLIER_DECISION_INVALID).
 *
 * Los dos botones de cada fila tienen la misma clase a propósito: un estilo
 * primario en uno solo sesgaría la decisión, y METIS detecta y advierte pero
 * no decide por el usuario.
 */
export function DecisionAtipicos({
  atipicos,
  resolving,
  onConfirmar,
}: Readonly<{
  atipicos: AtipicoDetectado[];
  resolving: boolean;
  onConfirmar: (decisiones: Record<number, DecisionAtipico>) => void;
}>) {
  const [decisiones, setDecisiones] = useState<Record<number, DecisionAtipico>>({});
  const completas = atipicos.every((a) => decisiones[a.indice] !== undefined);
  const uno = atipicos.length === 1;

  function decidir(indice: number, decision: DecisionAtipico) {
    setDecisiones((prev) => ({ ...prev, [indice]: decision }));
  }

  return (
    <>
      <p className="sub">
        {uno
          ? "Chow detectó un valor fuera de los umbrales."
          : `Chow detectó ${atipicos.length} valores fuera de los umbrales.`}{" "}
        Decidí qué hacer con {uno ? "él" : "cada uno"}:
      </p>
      <ul id="outlier-opciones" className="sub">
        <li>
          <b>Rechazar:</b> el dato se excluye de la serie y Etapa 1 se recalcula sin él. Los
          rechazados se excluyen todos juntos.
        </li>
        <li>
          <b>Aceptar:</b> el dato se conserva como parte de la población.
        </li>
      </ul>
      <div className="decision-atipicos">
        <table className="t">
          <thead>
            <tr>
              <th>Año</th>
              <th>Valor</th>
              <th>Lado</th>
              <th>Desvíos</th>
              <th>Decisión</th>
            </tr>
          </thead>
          <tbody>
            {atipicos.map((a) => {
              const elegida = decisiones[a.indice];
              const rotulo = `${a.periodo ?? `posición ${a.indice + 1}`}, ${formatNum(a.valor)}`;
              return (
                <tr key={a.indice}>
                  <td>{a.periodo ?? "—"}</td>
                  <td className="num">{formatNum(a.valor)}</td>
                  <td>{a.lado === "alto" ? "Alto" : "Bajo"}</td>
                  <td className="num">{formatNum(Math.abs(a.z))}</td>
                  <td>
                    <div className="row" role="group" aria-label={`Decisión para ${rotulo}`}>
                      <button
                        type="button"
                        className="b b-sec"
                        aria-pressed={elegida === "rechazar"}
                        aria-describedby="outlier-opciones"
                        disabled={resolving}
                        onClick={() => decidir(a.indice, "rechazar")}
                      >
                        Rechazar
                      </button>
                      <button
                        type="button"
                        className="b b-sec"
                        aria-pressed={elegida === "aceptar"}
                        aria-describedby="outlier-opciones"
                        disabled={resolving}
                        onClick={() => decidir(a.indice, "aceptar")}
                      >
                        Aceptar
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="sub">METIS no recomienda ninguna respuesta: la decisión es tuya.</p>
      <button
        type="button"
        className="b b-sec"
        disabled={!completas || resolving}
        onClick={() => onConfirmar(decisiones)}
      >
        Continuar con estas decisiones
      </button>
    </>
  );
}
