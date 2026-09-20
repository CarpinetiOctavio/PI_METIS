import type { Etapa1Datos } from "../api/types";

/** Bloque `datos` de Etapa 1: doce máximos anuales (2000-2011) con carga anual y
 * el atípico de Chow en la posición 5. Compartido por los tests de los gráficos y
 * del panel de exclusión — antes cada archivo armaba el suyo. */
export function makeEtapa1Datos(overrides: Partial<Etapa1Datos> = {}): Etapa1Datos {
  const anios = Array.from({ length: 12 }, (_, i) => 2000 + i);
  return {
    resolucion_original: "anual",
    resolucion_serie_original: null,
    serie_efectiva: anios.map((_, i) => 100 + i * 3),
    timestamps_efectivos: anios.map((anio) => ({ iso: `${anio}-01-01`, anio })),
    serie_original: null,
    timestamps_originales: null,
    indice_atipico: 5,
    serie_calendario: null,
    ...overrides,
  };
}
