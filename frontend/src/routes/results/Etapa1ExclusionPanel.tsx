import type { CSSProperties } from "react";
import { formatAxis, formatInt } from "../../i18n/format";
import type { Etapa1Datos } from "../../api/types";
import {
  csvDeSerie,
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

interface Fila {
  /** Rótulo de la fila: la década ("1980"), o null en la vista sin décadas. */
  decada: number | null;
  /** Una celda por columna; null es un año que la serie no tiene. */
  celdas: (PuntoSerie | null)[];
}

/**
 * Una fila por década, diez columnas alineadas por el último dígito del año:
 * 1985 cae siempre en la misma columna que 1995, y un año que falta queda como
 * celda vacía. Si los años se repitieran (no debería pasar: `serie_efectiva` es
 * anual), no hay forma de alinearlos y se cae a una sola tira sin rótulos, para
 * no perder ningún punto.
 */
function filasPorDecada(puntos: readonly PuntoSerie[]): Fila[] {
  const porAnio = new Map(puntos.map((p) => [p.anio, p]));
  if (porAnio.size !== puntos.length) return [{ decada: null, celdas: [...puntos] }];

  const primera = Math.floor(Math.min(...puntos.map((p) => p.anio)) / 10) * 10;
  const ultima = Math.floor(Math.max(...puntos.map((p) => p.anio)) / 10) * 10;
  const filas: Fila[] = [];
  for (let decada = primera; decada <= ultima; decada += 10) {
    const celdas = Array.from({ length: 10 }, (_, j) => porAnio.get(decada + j) ?? null);
    if (celdas.some((c) => c !== null)) filas.push({ decada, celdas });
  }
  return filas;
}

/** Altura de la barra de fondo, 0 % en el mínimo de la serie y 100 % en el
 * máximo. Con todos los valores iguales, todas llenas. */
function altura(valor: number, min: number, max: number): string {
  if (max === min) return "100%";
  return `${Math.round(((valor - min) / (max - min)) * 100)}%`;
}

/**
 * Exclusión interactiva de puntos (ítem A del plan de feedback de directores).
 * Es la vista accesible de la selección que se hace con clic sobre los gráficos:
 * la misma selección, dos formas de verla.
 *
 * La grilla por década (F1 del plan de fixes post-verificación, 01/10/2026) es
 * a la vez selector y mini gráfico de barras: la barra de cada celda deja ver el
 * atípico sin leer números, que es para lo que existe el panel. Entra entera,
 * sin scroll propio.
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
  onRecalcular,
  calculando = false,
  errorSimulacion = null,
  serieResultante,
}: Readonly<{
  puntos: PuntoSerie[];
  excluidos: ReadonlySet<number>;
  onToggle: (indice: number) => void;
  onLimpiar: () => void;
  sugerido: number | null;
  resolucionOriginal: Etapa1Datos["resolucion_original"];
  nombreArchivo?: string | null;
  // A2 — recalcular Etapa 1 (y 2) sin los puntos seleccionados. Sin este prop
  // (la página no sabe simular) el panel es el de A1: seleccionar y descargar.
  onRecalcular?: () => void;
  calculando?: boolean;
  errorSimulacion?: string | null;
  // DECISIÓN 071 — la serie que devolvió el backend al recalcular, si
  // corresponde a la selección actual. Con ella el CSV sale de lo que calculó
  // core/, no de un recorte hecho acá.
  serieResultante?: { serie: number[]; anios: number[] };
}>) {
  const cantidad = excluidos.size;
  const restantes = puntos.length - cantidad;
  const origenAgregado = resolucionOriginal ? RESOLUCION_ORIGINAL[resolucionOriginal] : undefined;
  const filas = filasPorDecada(puntos);
  const min = Math.min(...puntos.map((p) => p.valor));
  const max = Math.max(...puntos.map((p) => p.valor));
  const haySugerido = sugerido !== null && puntos.some((p) => p.indice === sugerido);

  const avisos: string[] = [];
  if (hayExcluidoInterior(excluidos, puntos.length)) {
    avisos.push(
      "Quitar un punto del medio deja un hueco en los años: al analizar la serie sin él, las " +
        "pruebas que dependen del orden (independencia, homogeneidad y tendencia) tratan como " +
        "consecutivos a los años vecinos.",
    );
  }
  if (cantidad > 0 && restantes < MIN_DATOS) {
    avisos.push(
      `Quedarían ${formatInt(restantes)} datos: METIS necesita al menos ${MIN_DATOS} para ` +
        "analizar una serie.",
    );
  }
  if (cantidad > 0 && origenAgregado) {
    avisos.push(
      `Tu archivo original era ${origenAgregado}: lo que se descarga es la serie de máximos ` +
        "anuales, no los datos originales sin ese punto (quitar el máximo de un año de datos " +
        `${origenAgregado === "diaria" ? "diarios" : "mensuales"} no es lo mismo que quitar ese ` +
        "año: el segundo mayor valor pasaría a ser el máximo).",
    );
  }

  function descargar() {
    const csv = serieResultante
      ? csvDeSerie(serieResultante.anios, serieResultante.serie)
      : csvSinExcluidos(puntos, excluidos);
    descargarCsv(nombreCsvSinAtipicos(nombreArchivo), csv);
  }

  function celda(p: PuntoSerie) {
    const excluido = excluidos.has(p.indice);
    const esSugerido = p.indice === sugerido;
    const etiqueta =
      `${p.anio}, ${formatAxis(p.valor)}, ${excluido ? "excluido" : "incluido"}` +
      (esSugerido ? ", sugerido por Chow" : "");
    const clases = ["etapa1-exclusion__celda"];
    if (excluido) clases.push("etapa1-exclusion__celda--excluida");
    if (esSugerido) clases.push("etapa1-exclusion__celda--sugerida");
    return (
      <button
        key={p.indice}
        type="button"
        className={clases.join(" ")}
        aria-pressed={excluido}
        aria-label={etiqueta}
        onClick={() => onToggle(p.indice)}
        style={{ "--alto": altura(p.valor, min, max) } as CSSProperties}
      >
        <span className="etapa1-exclusion__barra" aria-hidden="true" />
        <span className="etapa1-exclusion__anio" aria-hidden="true">
          {p.anio}
        </span>
        <span className="etapa1-exclusion__valor num" aria-hidden="true">
          {formatAxis(p.valor)}
        </span>
      </button>
    );
  }

  return (
    <div className="card etapa1-exclusion">
      <div className="etapa1-exclusion__cabecera">
        <p className="ct">Excluir puntos de la serie</p>
        {/* <output> tiene rol "status" implícito (región viva educada): el lector
            de pantalla anuncia el conteo cada vez que cambia la selección. */}
        <output className={`etapa1-exclusion__estado${cantidad > 0 ? " activo" : ""}`}>
          {cantidad === 0
            ? "Ningún punto excluido"
            : `${formatInt(cantidad)} de ${formatInt(puntos.length)} excluidos · quedan ${formatInt(restantes)}`}
        </output>
      </div>
      <p className="fn">
        Hacé clic en un punto de los gráficos de arriba, o en su año acá abajo, para quitarlo de
        la serie. Los puntos excluidos se dibujan huecos. Explorar no cambia el análisis original.
      </p>

      <div
        className="etapa1-exclusion__grilla"
        role="group"
        aria-label={`Años de la serie (${formatInt(puntos.length)})`}
      >
        {filas.map((fila) => (
          <div
            key={fila.decada ?? "sin-decadas"}
            className="etapa1-exclusion__fila"
            role="group"
            aria-label={fila.decada === null ? "Años de la serie" : `Década de ${fila.decada}`}
          >
            {fila.decada !== null && (
              <span className="etapa1-exclusion__decada num" aria-hidden="true">
                {fila.decada}
              </span>
            )}
            <div className="etapa1-exclusion__celdas">
              {fila.celdas.map((p, j) =>
                p ? (
                  celda(p)
                ) : (
                  <span
                    key={`vacia-${fila.decada}-${j}`}
                    className="etapa1-exclusion__celda etapa1-exclusion__celda--vacia"
                    aria-hidden="true"
                  />
                ),
              )}
            </div>
          </div>
        ))}
      </div>

      {haySugerido && (
        <p className="fn etapa1-exclusion__leyenda">
          <span className="etapa1-exclusion__marca" aria-hidden="true" /> sugerido por Chow (no
          viene seleccionado)
        </p>
      )}

      {avisos.length > 0 && (
        <div className="etapa1-exclusion__avisos">
          {avisos.map((texto) => (
            <p key={texto} className="fn">
              {texto}
            </p>
          ))}
        </div>
      )}

      {errorSimulacion && (
        <div className="banner crit" role="alert">
          <span className="ic">✕</span> {errorSimulacion}
        </div>
      )}

      <div className="etapa1-exclusion__acciones">
        <button
          type="button"
          className="b b-sec etapa1-exclusion__limpiar"
          onClick={onLimpiar}
          disabled={cantidad === 0}
        >
          Limpiar selección
        </button>
        <span className="sp" />
        <button
          type="button"
          className={onRecalcular ? "b b-sec" : "b b-pri"}
          onClick={descargar}
          disabled={cantidad === 0}
        >
          Descargar serie sin los puntos seleccionados (CSV)
        </button>
        {onRecalcular && (
          <button
            type="button"
            className="b b-pri"
            onClick={onRecalcular}
            disabled={cantidad === 0 || restantes < MIN_DATOS || calculando}
          >
            {calculando ? "Calculando…" : "Recalcular sin los puntos seleccionados"}
          </button>
        )}
      </div>
    </div>
  );
}
