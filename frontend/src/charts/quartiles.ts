import type { BoxPlotStats } from "./BoxPlot";

/**
 * Cuartiles por el método de las bisagras de Tukey (mediana exclusiva) —
 * PR 5 del plan de cierre de pendientes no-test. Hay varias convenciones
 * de cuartiles con resultados numéricos distintos (Tukey/bisagras,
 * Moore-McCabe, el método 7 de Hyndman-Fan que usan numpy/Excel por
 * default, entre otras) — "la que usa la librería" no es una respuesta
 * aceptable en este proyecto (mismo criterio que rige `core/`, aunque
 * esto es estadística descriptiva de PRESENTACIÓN, no del motor: vive acá
 * a propósito, no en `core/`).
 *
 * Elegida: bisagras de Tukey — la mitad inferior/superior EXCLUYE la
 * mediana cuando n es impar, es el método que se enseña con más
 * frecuencia en cursos introductorios de estadística descriptiva (a
 * diferencia de la interpolación lineal del método 7).
 */
function mediana(ordenados: number[]): number {
  const n = ordenados.length;
  const mid = Math.floor(n / 2);
  return n % 2 === 0 ? (ordenados[mid - 1] + ordenados[mid]) / 2 : ordenados[mid];
}

export function calcularCuartiles(valores: number[]): BoxPlotStats | null {
  if (valores.length === 0) return null;
  const ordenados = [...valores].sort((a, b) => a - b);
  const n = ordenados.length;

  // Caso degenerado: con un solo dato, las dos mitades quedan vacías
  // (floor(1/2)=0) y mediana([]) da NaN — un solo punto colapsa los
  // cinco estadísticos al mismo valor.
  if (n === 1) {
    const [v] = ordenados;
    return { min: v, q1: v, mediana: v, q3: v, max: v };
  }

  const mitadInferior = ordenados.slice(0, Math.floor(n / 2));
  const mitadSuperior = n % 2 === 0 ? ordenados.slice(n / 2) : ordenados.slice(Math.ceil(n / 2));

  return {
    min: ordenados[0],
    q1: mediana(mitadInferior),
    mediana: mediana(ordenados),
    q3: mediana(mitadSuperior),
    max: ordenados[n - 1],
  };
}
