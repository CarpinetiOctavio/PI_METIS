import { InteractiveChart } from "../../charts/InteractiveChart";
import type { ChartSeries } from "../../charts/InteractiveChart";
import { formatAxis } from "../../i18n/format";
import { notaCriterioAnio } from "../../i18n/mesInicioAnio";
import type { Etapa1Datos, TestResultDetail } from "../../api/types";

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
 *
 * Fajas de máximos y mínimos — Chow (Grubbs-Beck) marca un dato como
 * atípico cuando |ln(x) − media_log| / s_log supera K_N. Llevado a la
 * escala original de la serie, eso son dos umbrales horizontales:
 *   exp(media_log ± K_N · s_log)
 * entre los que cae la población "normal". Se dibujan punteados a partir
 * de `media_log`/`s_log` (`chow.explicacion.terminos`, DECISIÓN 064) y
 * K_N (`chow.valor_critico`). Si Chow no se ejecutó (serie con ceros o
 * valores ≤ 0) `explicacion` es null y las fajas no se dibujan.
 */
export function Etapa1ChowChart({
  datos,
  chow,
  mesInicioAnio,
}: Readonly<{
  datos: Etapa1Datos;
  chow?: TestResultDetail;
  mesInicioAnio?: number;
}>) {
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
  ];

  const mediaLog = chow?.explicacion?.terminos.media_log;
  const sLog = chow?.explicacion?.terminos.s_log;
  const kN = chow?.valor_critico;
  if (
    todosLosPuntos.length > 0 &&
    typeof mediaLog === "number" &&
    typeof sLog === "number" &&
    typeof kN === "number"
  ) {
    const xs = todosLosPuntos.map((p) => p.x);
    const xMin = Math.min(...xs);
    const xMax = Math.max(...xs);
    const limiteSuperior = Math.exp(mediaLog + kN * sLog);
    const limiteInferior = Math.exp(mediaLog - kN * sLog);
    series.push(
      {
        id: "faja-max",
        kind: "line",
        label: "Faja de máximos",
        colorVar: "--mut",
        dashed: true,
        data: [
          { x: xMin, y: limiteSuperior },
          { x: xMax, y: limiteSuperior },
        ],
      },
      {
        id: "faja-min",
        kind: "line",
        label: "Faja de mínimos",
        colorVar: "--mut",
        dashed: true,
        data: [
          { x: xMin, y: limiteInferior },
          { x: xMax, y: limiteInferior },
        ],
      },
    );
  }

  series.push({
    id: "normales",
    kind: "points",
    label: "Datos",
    colorVar: "--acc",
    data: puntosSinAtipico,
  });
  if (puntoAtipico) {
    series.push({
      id: "atipico",
      kind: "points",
      label: "Atípico (Chow)",
      // --crit (rojo) en vez de --acc2: en modo claro --acc2 (verde oliva)
      // se confundía con --acc (teal) del resto de los puntos. --crit
      // destaca en ambos temas y es el token semántico de "anomalía".
      colorVar: "--crit",
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
        ariaLabel="Gráfico de Chow: serie analizada, fajas de máximos y mínimos, y el atípico marcado"
        xLabel="Año"
        yLabel="Valor"
        xTickFormat={(v) => String(Math.round(v))}
        yTickFormat={(v) => formatAxis(v)}
      />
    </div>
  );
}
