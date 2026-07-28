import type { RankingItem } from "../api/types";

// Datos de ejemplo — Etapa 2 no está expuesta por ningún endpoint todavía
// (ver frontend-implementation-plan.md §6). Números reutilizados de
// frontend-design/metis-prototipo-fase3.html (rankingE2, variante D ★), que
// ya los presenta como valores ilustrativos, no de una corrida real.
// Ninguna distribución se etiqueta "óptima/recomendada/ganadora" — solo se
// reporta el hecho objetivo de "menor EEA" en la de rank 1 (constraints.md:
// "METIS no sugiere distribución ganadora — presenta el ranking, el usuario
// decide").
export const rankingMock: RankingItem[] = [
  { distribucion: "Gumbel", metodo: "Momentos", eea: 34.5, rank: 1 },
  { distribucion: "GVE", metodo: "Momentos", eea: 35.1, rank: 2 },
  { distribucion: "Gamma 2p", metodo: "MV", eea: 36.2, rank: 3 },
];
