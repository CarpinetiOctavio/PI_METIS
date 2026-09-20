import { formatInt, formatNum } from "../../i18n/format";
import type { Etapa1Datos } from "../../api/types";
import {
  csvSinExcluidos,
  descargarCsv,
  hayExcluidoInterior,
  MIN_DATOS,
  nombreCsvSinAtipicos,
} from "./exclusiones";
import type { PuntoSerie } from "./exclusiones";
import "./Etapa1ExclusionPanel.css";

const RESOLUCION_ORIGINAL: Partial<Record<NonNullable<Etapa1Datos["resolucion_original"]>, string>> = {
  mensual: "mensual",
  diaria: "diaria",
};

/**
 * Exclusión interactiva de puntos (ítem A del plan de feedback de directores).
 * Es la vista accesible de la selección que se hace con clic sobre los gráficos:
 * la misma selección, dos formas de verla (por eso una lista con checkbox y no
 * solo el gráfico, que no se puede operar con lector de pantalla).
 *
 * `sugerido` es el atípico que marcó Chow: se señala pero NO viene seleccionado —
 * quitarlo es una decisión del usuario, no un valor por defecto.
 */
export function Etapa1ExclusionPanel({
  puntos,
  excluidos,
  onToggle,
  onLimpiar,
  sugerido,
  resolucionOriginal,
  nombreArchivo,
}: Readonly<{
  puntos: PuntoSerie[];
  excluidos: ReadonlySet<number>;
  onToggle: (indice: number) => void;
  onLimpiar: () => void;
  sugerido: number | null;
  resolucionOriginal: Etapa1Datos["resolucion_original"];
  nombreArchivo?: string | null;
}>) {
  const cantidad = excluidos.size;
  const restantes = puntos.length - cantidad;
  const origenAgregado = resolucionOriginal ? RESOLUCION_ORIGINAL[resolucionOriginal] : undefined;

  function descargar() {
    descargarCsv(nombreCsvSinAtipicos(nombreArchivo), csvSinExcluidos(puntos, excluidos));
  }

  return (
    <div className="card etapa1-exclusion">
      <p className="ct">Excluir puntos de la serie</p>
      <p className="fn">
        Hacé clic en un punto de los gráficos de arriba, o marcalo en la lista, para quitarlo de
        la serie. Los puntos excluidos se dibujan huecos. Explorar no cambia el análisis original.
      </p>

      <fieldset className="etapa1-exclusion__lista">
        <legend>Años de la serie ({formatInt(puntos.length)})</legend>
        {puntos.map((p) => (
          <label key={p.indice} className="etapa1-exclusion__item">
            <input
              type="checkbox"
              checked={excluidos.has(p.indice)}
              onChange={() => onToggle(p.indice)}
            />
            <span className="num">{p.anio}</span>
            <span className="num">{formatNum(p.valor)}</span>
            {p.indice === sugerido && <span className="pill warn">sugerido por Chow</span>}
          </label>
        ))}
      </fieldset>

      {/* <output> tiene rol "status" implícito (región viva educada): el lector de
          pantalla anuncia el conteo cada vez que cambia la selección. */}
      <output className="etapa1-exclusion__estado">
        {cantidad === 0
          ? "Ningún punto excluido."
          : `${formatInt(cantidad)} de ${formatInt(puntos.length)} puntos excluidos.`}
      </output>

      {hayExcluidoInterior(excluidos, puntos.length) && (
        <p className="fn">
          Quitar un punto del medio deja un hueco en los años: al analizar la serie sin él, las
          pruebas que dependen del orden (independencia, homogeneidad y tendencia) tratan como
          consecutivos a los años vecinos.
        </p>
      )}
      {cantidad > 0 && restantes < MIN_DATOS && (
        <p className="fn">
          Quedarían {formatInt(restantes)} datos: METIS necesita al menos {MIN_DATOS} para analizar
          una serie.
        </p>
      )}
      {origenAgregado && (
        <p className="fn">
          Tu archivo original era {origenAgregado}: lo que se descarga es la serie de máximos
          anuales, no los datos originales sin ese punto (quitar el máximo de un año de datos{" "}
          {origenAgregado === "diaria" ? "diarios" : "mensuales"} no es lo mismo que quitar ese año:
          el segundo mayor valor pasaría a ser el máximo).
        </p>
      )}

      <div className="etapa1-exclusion__acciones">
        <button type="button" className="b b-sec" onClick={onLimpiar} disabled={cantidad === 0}>
          Limpiar selección
        </button>
        <button type="button" className="b b-pri" onClick={descargar} disabled={cantidad === 0}>
          Descargar serie sin los puntos seleccionados (CSV)
        </button>
      </div>
    </div>
  );
}
