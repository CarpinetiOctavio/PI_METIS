import { InteractiveChart } from "../../charts/InteractiveChart";
import type { ChartSeries } from "../../charts/InteractiveChart";
import { formatAxis } from "../../i18n/format";
import type { EventoDiseno } from "../../api/types";

/**
 * Gráfico de eventos de diseño — xT contra T, eje X en escala log. Bloque C
 * del plan de Etapa 2 (§5, C2). Curva continua (curva_ajuste, muestreo
 * denso) con los períodos de retorno que el usuario pidió resaltados como
 * marcadores (eventos_diseno).
 */
export function Etapa2EventosChart({
  eventosDiseno,
  curvaAjuste,
}: Readonly<{ eventosDiseno: EventoDiseno[]; curvaAjuste: EventoDiseno[] }>) {
  const curvaValida = curvaAjuste.filter(
    (e): e is { periodo_retorno: number; valor: number } => e.valor !== null,
  );
  const eventosValidos = eventosDiseno.filter(
    (e): e is { periodo_retorno: number; valor: number } => e.valor !== null,
  );

  const series: ChartSeries[] = [
    {
      id: "curva",
      kind: "line",
      label: "Curva ajustada",
      colorVar: "--acc",
      data: curvaValida.map((e) => ({ x: e.periodo_retorno, y: e.valor })),
    },
    {
      id: "eventos",
      kind: "points",
      label: "Períodos de retorno pedidos",
      colorVar: "--acc2",
      data: eventosValidos.map((e) => ({ x: e.periodo_retorno, y: e.valor })),
    },
  ];

  return (
    <InteractiveChart
      series={series}
      ariaLabel="Gráfico de eventos de diseño: valor estimado contra período de retorno"
      xLabel="Período de retorno T (años)"
      yLabel="Valor estimado (xT)"
      xTickFormat={(v) => formatAxis(v)}
      yTickFormat={(v) => formatAxis(v)}
    />
  );
}
