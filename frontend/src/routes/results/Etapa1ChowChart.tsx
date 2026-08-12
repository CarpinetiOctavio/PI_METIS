import { InteractiveChart } from "../../charts/InteractiveChart";
import type { ChartSeries } from "../../charts/InteractiveChart";
import { formatNum } from "../../i18n/format";
import { notaCriterioAnio } from "../../i18n/mesInicioAnio";
import type { Etapa1Datos } from "../../api/types";

/**
 * Gráfico de Chow — la serie analizada (serie_efectiva) con el atípico
 * marcado. PR 4 del plan de cierre de pendientes no-test.
 *
 * Sin toggle calendario/configurado (DECISIÓN 058 §2, apartamiento parcial
 * de la regla de "dos versiones" de constraints.md, documentado ahí):
 * Chow corrió sobre serie_efectiva — la agregación con el mes_inicio_anio
 * configurado. El atípico es un punto DE ESA serie; en la agregación
 * calendario ese punto puede no existir, o existir con otro valor y otro
 * año. Un toggle acá presentaría un atípico que no corresponde a lo que
 * el gráfico dice.
 *
 * `indice_atipico` ya viene mapeado a posición en `serie_efectiva`
 * (DECISIÓN 058 §5) — sin traducir nada acá. `null` tras rechazar el
 * atípico (iteración 2 del stream): la serie se dibuja sin marcador.
 */
export function Etapa1ChowChart({
  datos,
  mesInicioAnio,
}: Readonly<{ datos: Etapa1Datos; mesInicioAnio?: number }>) {
  if (!datos.timestamps_efectivos) return null;
  const timestamps = datos.timestamps_efectivos;

  const todosLosPuntos = datos.serie_efectiva.map((v, i) => ({
    x: timestamps[i]?.anio ?? 0,
    y: v,
  }));
  const puntosSinAtipico = todosLosPuntos.filter(
    (_, i) => i !== datos.indice_atipico,
  );
  const puntoAtipico =
    datos.indice_atipico !== null ? todosLosPuntos[datos.indice_atipico] : null;

  const series: ChartSeries[] = [
    { id: "linea", kind: "line", label: "Serie analizada", colorVar: "--acc", data: todosLosPuntos },
    { id: "normales", kind: "points", label: "Datos", colorVar: "--acc", data: puntosSinAtipico },
  ];
  if (puntoAtipico) {
    series.push({
      id: "atipico",
      kind: "points",
      label: "Atípico (Chow)",
      colorVar: "--acc2",
      data: [puntoAtipico],
    });
  }

  return (
    <div className="card">
      <p className="ct">Gráfico de Chow</p>
      {mesInicioAnio !== undefined && (
        <p className="fn">{notaCriterioAnio(mesInicioAnio)}</p>
      )}
      <InteractiveChart
        series={series}
        xScale="linear"
        ariaLabel="Gráfico de Chow: serie analizada con el atípico marcado"
        xLabel="Año"
        yLabel="Valor"
        xTickFormat={(v) => String(Math.round(v))}
        yTickFormat={(v) => formatNum(v)}
      />
    </div>
  );
}
