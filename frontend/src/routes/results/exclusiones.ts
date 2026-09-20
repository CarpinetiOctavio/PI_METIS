import type { ChartPoint } from "../../charts/InteractiveChart";
import type { Etapa1Datos } from "../../api/types";

/**
 * Exclusión interactiva de puntos (ítem A del plan de feedback de directores,
 * 20/09/2026). Lógica pura: qué puntos hay, cuáles están excluidos y qué archivo
 * CSV queda sin ellos. Nada de esto calcula estadística — recalcular los
 * resultados sin los puntos excluidos es trabajo de `core/`.
 *
 * Política (DECISIÓN 071, a registrar): un punto excluido se ELIMINA de la serie
 * junto con su año, en cualquier posición — el mismo criterio que ya aplican el
 * rechazo de Chow, los valores faltantes y la agregación temporal. No se
 * reemplaza por la media.
 */

/** Un dato de `serie_efectiva`. `indice` es su posición en esa serie — el
 * mismo espacio de índices que `Etapa1Datos.indice_atipico`. */
export interface PuntoSerie {
  indice: number;
  anio: number;
  valor: number;
}

/** La selección de puntos excluidos, compartida entre los gráficos y la lista. */
export interface SeleccionPuntos {
  excluidos: ReadonlySet<number>;
  onToggle: (indice: number) => void;
}

/** Lo que un gráfico necesita para mostrar y operar la selección: cómo saber si
 * un punto está excluido y qué hacer al activarlo. Sin selección, nada. */
export function interaccionDeSeleccion(seleccion?: SeleccionPuntos) {
  if (!seleccion) return { marked: undefined, onPointActivate: undefined };
  return {
    marked: (p: ChartPoint) => p.id !== undefined && seleccion.excluidos.has(p.id),
    onPointActivate: (p: ChartPoint) => {
      if (p.id !== undefined) seleccion.onToggle(p.id);
    },
  };
}

/** Mínimo de datos para analizar una serie (bloqueante en el backend). */
export const MIN_DATOS = 10;

export function puntosDeSerie(datos: Etapa1Datos): PuntoSerie[] {
  const timestamps = datos.timestamps_efectivos;
  if (!timestamps) return [];
  return datos.serie_efectiva.map((valor, indice) => ({
    indice,
    anio: timestamps[indice]?.anio ?? 0,
    valor,
  }));
}

/** CSV `periodo,valor` con los puntos que NO están excluidos. Coma como
 * separador y punto decimal, un año de 4 dígitos por fila: es un formato que
 * METIS vuelve a leer tal cual (`core/validacion/parser.py`). */
export function csvSinExcluidos(
  puntos: readonly PuntoSerie[],
  excluidos: ReadonlySet<number>,
): string {
  const filas = puntos
    .filter((p) => !excluidos.has(p.indice))
    .map((p) => `${p.anio},${p.valor}`);
  return ["periodo,valor", ...filas].join("\n") + "\n";
}

/** `<archivo original>_sin_atipicos.csv`; sin nombre conocido, `serie_sin_atipicos.csv`. */
export function nombreCsvSinAtipicos(nombreArchivo?: string | null): string {
  const base = (nombreArchivo ?? "")
    .split(/[\\/]/)
    .pop()
    ?.replace(/\.[^.]+$/, "")
    .trim();
  return `${base || "serie"}_sin_atipicos.csv`;
}

/** ¿Algún excluido no es el primero ni el último dato? Ahí el hueco queda en
 * medio de la serie y las pruebas que dependen del orden tratarían como
 * consecutivos a los años vecinos. */
export function hayExcluidoInterior(
  excluidos: ReadonlySet<number>,
  cantidad: number,
): boolean {
  for (const i of excluidos) {
    if (i > 0 && i < cantidad - 1) return true;
  }
  return false;
}

/** Descarga `contenido` como archivo. Vive acá (no en el componente) para poder
 * reemplazarla en los tests: jsdom no implementa `URL.createObjectURL`. */
export function descargarCsv(nombre: string, contenido: string): void {
  const url = URL.createObjectURL(new Blob([contenido], { type: "text/csv;charset=utf-8" }));
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = nombre;
  document.body.appendChild(enlace);
  enlace.click();
  enlace.remove();
  URL.revokeObjectURL(url);
}
