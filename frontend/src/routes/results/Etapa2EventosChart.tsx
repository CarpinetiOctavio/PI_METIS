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
  periodoResaltado,
}: Readonly<{
  eventosDiseno: EventoDiseno[];
  curvaAjuste: EventoDiseno[];
  // F4 (feedback Facundo 02/09) — período de retorno seleccionado con los
  // chips de Etapa2EventosView. Su marcador se dibuja más grande y con
  // --acc-hi. El chip ya es la fuente de verdad (aria-pressed) — acá no hay
  // estado nuevo.
  periodoResaltado?: number | null;
}>) {
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
      highlight:
        periodoResaltado != null
          ? (p) => p.x === periodoResaltado
          : undefined,
    },
  ];

  const ariaLabel =
    periodoResaltado != null
      ? `Gráfico de eventos de diseño: valor estimado contra período de retorno. Período de retorno resaltado: T = ${periodoResaltado} años`
      : "Gráfico de eventos de diseño: valor estimado contra período de retorno";

  return (
    <InteractiveChart
      series={series}
      ariaLabel={ariaLabel}
      xLabel="Período de retorno T (años)"
      yLabel="Valor estimado (xT)"
      xTickFormat={(v) => formatAxis(v)}
      yTickFormat={(v) => formatAxis(v)}
    />
  );
}
