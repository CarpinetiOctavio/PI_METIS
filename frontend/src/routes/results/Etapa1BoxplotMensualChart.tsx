import { useState } from "react";
import { BoxPlot } from "../../charts/BoxPlot";
import type { BoxPlotCategory } from "../../charts/BoxPlot";
import { calcularCuartiles } from "../../charts/quartiles";
import { formatAxis } from "../../i18n/format";
import type { Etapa1Datos } from "../../api/types";

const MESES_ABREV = [
  "Ene",
  "Feb",
  "Mar",
  "Abr",
  "May",
  "Jun",
  "Jul",
  "Ago",
  "Sep",
  "Oct",
  "Nov",
  "Dic",
];

function ordenDeMeses(mesInicio: number): number[] {
  return Array.from({ length: 12 }, (_, i) => ((mesInicio - 1 + i) % 12) + 1);
}

/**
 * Boxplot mensual — doce cajas, una por mes, sobre `datos.serie_original`
 * + `timestamps_originales` (la serie mensual CRUDA, no la agregada). PR 5
 * del plan de cierre de pendientes no-test. Se renderiza solo con carga
 * mensual — con carga anual no hay meses que agrupar.
 *
 * El toggle configurado/calendario acá NO recalcula los datos (a
 * diferencia del de `Etapa1SerieTemporalChart`): los 12 grupos de valores
 * son siempre los mismos. Lo único que cambia es el ORDEN de los meses en
 * el eje X — arranca en `mes_inicio_anio` o en enero.
 */
export function Etapa1BoxplotMensualChart({
  datos,
  mesInicioAnio,
}: Readonly<{ datos: Etapa1Datos; mesInicioAnio?: number }>) {
  const puedeAlternarOrden = mesInicioAnio !== undefined && mesInicioAnio !== 1;
  const [vista, setVista] = useState<"configurada" | "calendario">(
    puedeAlternarOrden ? "configurada" : "calendario",
  );

  if (
    datos.resolucion_original !== "mensual" ||
    !datos.serie_original ||
    !datos.timestamps_originales
  ) {
    return null;
  }

  const timestamps = datos.timestamps_originales;
  const porMes = new Map<number, number[]>();
  datos.serie_original.forEach((valor, i) => {
    const iso = timestamps[i]?.iso;
    if (!iso) return;
    const mes = Number(iso.slice(5, 7));
    const grupo = porMes.get(mes) ?? [];
    grupo.push(valor);
    porMes.set(mes, grupo);
  });

  const ordenMeses =
    vista === "configurada" && mesInicioAnio !== undefined
      ? ordenDeMeses(mesInicioAnio)
      : ordenDeMeses(1);

  const categories: BoxPlotCategory[] = ordenMeses.map((mes) => ({
    label: MESES_ABREV[mes - 1],
    stats: calcularCuartiles(porMes.get(mes) ?? []),
  }));

  return (
    <div className="card">
      <p className="ct">Boxplot mensual</p>
      {puedeAlternarOrden && (
        <fieldset className="field">
          <legend>Orden de meses</legend>
          <div className="seg">
            <button
              type="button"
              className={vista === "configurada" ? "on" : ""}
              aria-pressed={vista === "configurada"}
              onClick={() => setVista("configurada")}
            >
              Configurado
            </button>
            <button
              type="button"
              className={vista === "calendario" ? "on" : ""}
              aria-pressed={vista === "calendario"}
              onClick={() => setVista("calendario")}
            >
              Calendario
            </button>
          </div>
        </fieldset>
      )}
      <BoxPlot
        categories={categories}
        ariaLabel="Boxplot mensual de la serie cruda"
        yLabel="Valor"
        yTickFormat={(v) => formatAxis(v)}
      />
    </div>
  );
}
