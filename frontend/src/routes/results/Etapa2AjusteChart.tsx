import { InteractiveChart } from "../../charts/InteractiveChart";
import type { ChartSeries } from "../../charts/InteractiveChart";
import { formatAxis } from "../../i18n/format";
import type { EventoDiseno, PuntoEmpirico } from "../../api/types";

/**
 * Gráfico de ajuste — puntos empíricos (Weibull) contra la curva de la
 * distribución elegida. Bloque C del plan de Etapa 2 (§5, C2). Eje X en
 * escala log (T, período de retorno empírico/de la curva).
 *
 * Sin toggle calendario/hidrológico — DECISIÓN 056, ver §5 (C3) del plan:
 * el criterio de año es una regla de agregación aguas arriba de Etapa 1
 * (Bloque F, sin implementar), no una opción de dibujo de este gráfico.
 */
export function Etapa2AjusteChart({
  puntosEmpiricos,
  curvaAjuste,
  distribucion,
  metodo,
}: Readonly<{
  puntosEmpiricos: PuntoEmpirico[];
  curvaAjuste: EventoDiseno[];
  distribucion: string;
  metodo: string;
}>) {
  const curvaValida = curvaAjuste.filter(
    (e): e is { periodo_retorno: number; valor: number } => e.valor !== null,
  );

  const series: ChartSeries[] = [
    {
      id: "curva",
      kind: "line",
      label: `${distribucion} / ${metodo}`,
      colorVar: "--acc",
      data: curvaValida.map((e) => ({ x: e.periodo_retorno, y: e.valor })),
    },
    {
      id: "empiricos",
      kind: "points",
      label: "Datos observados",
      colorVar: "--acc2",
      data: puntosEmpiricos.map((p) => ({ x: p.periodo_retorno, y: p.valor })),
    },
  ];

  return (
    <InteractiveChart
      series={series}
      ariaLabel={`Gráfico de ajuste: puntos empíricos contra la curva de ${distribucion} (${metodo})`}
      xLabel="Período de retorno T (años)"
      yLabel="Valor"
      xTickFormat={(v) => formatAxis(v)}
      yTickFormat={(v) => formatAxis(v)}
    />
  );
}
