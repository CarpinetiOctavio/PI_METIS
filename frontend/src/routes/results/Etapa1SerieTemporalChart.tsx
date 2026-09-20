import { useState } from "react";
import { InteractiveChart } from "../../charts/InteractiveChart";
import type { ChartSeries } from "../../charts/InteractiveChart";
import { formatAxis } from "../../i18n/format";
import type { Etapa1Datos } from "../../api/types";
import { interaccionDeSeleccion } from "./exclusiones";
import type { SeleccionPuntos } from "./exclusiones";

/**
 * Serie temporal — máximos anuales (serie_efectiva) contra el año. PR 4
 * del plan de cierre de pendientes no-test (DECISIÓN 058). Eje X lineal
 * (año), no logarítmico — a diferencia de los gráficos de Etapa 2, que
 * usan T (período de retorno) en escala log.
 *
 * Toggle configurada/calendario solo si la carga fue mensual o diaria y el
 * backend mandó serie_calendario — con carga anual el criterio de año ya lo
 * fijó el usuario al armar el archivo, no hay una segunda agregación posible
 * para comparar (DECISIÓN 058 §1/§2; diaria por docs/plan-resolucion-diaria.md
 * R3.4). serie_calendario trae sus PROPIOS timestamps (corrección del PR 4
 * sobre la decisión original) porque puede tener más o menos puntos que
 * serie_efectiva.
 */
export function Etapa1SerieTemporalChart({
  datos,
  seleccion,
}: Readonly<{ datos: Etapa1Datos; seleccion?: SeleccionPuntos }>) {
  const [vista, setVista] = useState<"configurada" | "calendario">("configurada");
  const cargaConAgregacion =
    datos.resolucion_original === "mensual" ||
    datos.resolucion_original === "diaria";
  const puedeAlternar = cargaConAgregacion && datos.serie_calendario !== null;
  const usandoCalendario = puedeAlternar && vista === "calendario";

  if (!datos.timestamps_efectivos) return null;

  const valores = usandoCalendario
    ? datos.serie_calendario!.serie
    : datos.serie_efectiva;
  const timestamps = usandoCalendario
    ? datos.serie_calendario!.timestamps
    : datos.timestamps_efectivos;

  // `id` = posición en la serie que se dibuja. Los índices de la selección son
  // de `serie_efectiva`: en la vista calendario (otra agregación, otros puntos)
  // no se puede seleccionar, sus posiciones no corresponden.
  const puntos = valores.map((v, i) => ({ x: timestamps[i]?.anio ?? 0, y: v, id: i }));
  const { marked, onPointActivate } = interaccionDeSeleccion(
    usandoCalendario ? undefined : seleccion,
  );
  const series: ChartSeries[] = [
    { id: "linea", kind: "line", label: "Máximos anuales", colorVar: "--acc", data: puntos },
    { id: "puntos", kind: "points", label: "Máximos anuales", colorVar: "--acc", data: puntos, marked },
  ];

  return (
    <div className="card">
      <p className="ct">Serie temporal</p>
      {datos.resolucion_original === "diaria" && (
        <p className="fn">
          Máximos anuales agregados desde los datos diarios subidos.
        </p>
      )}
      {puedeAlternar && (
        <fieldset className="field">
          <legend>Criterio de año</legend>
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
      {usandoCalendario && (
        <p className="fn">
          Vista comparativa — ningún estadístico, veredicto ni warning de esta
          pantalla corresponde a esta agregación.
        </p>
      )}
      {usandoCalendario && seleccion && (
        <p className="fn">La selección de puntos solo está disponible en la vista configurada.</p>
      )}
      <InteractiveChart
        series={series}
        xScale="linear"
        onPointActivate={onPointActivate}
        ariaLabel="Serie temporal de máximos anuales por año"
        xLabel="Año"
        yLabel="Valor"
        xTickFormat={(v) => String(Math.round(v))}
        yTickFormat={(v) => formatAxis(v)}
      />
    </div>
  );
}
