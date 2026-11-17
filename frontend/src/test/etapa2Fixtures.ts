import type { Etapa2Result } from "../api/types";

/** Resultado de Etapa 2 mínimo pero realista: dos distribuciones (gumbel y
 * gve) con un método ajustado cada una y un punto empírico. Compartido por los
 * tests de `HistoryDetailPage`, `ResultsPage` y `Etapa2Explorador` — antes cada
 * archivo tenía su propia copia y SonarCloud las contaba como duplicación. */
export function makeEtapa2(overrides: Partial<Etapa2Result> = {}): Etapa2Result {
  return {
    ranking: [
      {
        distribucion: "gumbel",
        n_parametros: 2,
        metodos: [
          { metodo: "momentos", parametros: { mu: 100, alpha: 20 }, eea: 12.5, status: "ok" },
        ],
        mejor_eea: 12.5,
        mejor_metodo: "momentos",
      },
      {
        distribucion: "gve",
        n_parametros: 3,
        metodos: [
          { metodo: "ml", parametros: { nu: 90, alpha: 18, beta: 0.1 }, eea: 15.2, status: "ok" },
        ],
        mejor_eea: 15.2,
        mejor_metodo: "ml",
      },
    ],
    warnings: [],
    puntos_empiricos: [{ valor: 142.5, periodo_retorno: 41, probabilidad: 0.9756 }],
    seleccion: null,
    ...overrides,
  };
}
