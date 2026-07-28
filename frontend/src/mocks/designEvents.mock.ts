import type { DesignEventsResponse } from "../api/types";

// Respuesta de ejemplo para POST /api/v1/analysis/design-events — el
// contrato SÍ está documentado (api-contracts.md), pero el endpoint no está
// implementado (frontend-integration.md §3). Números reutilizados del
// ejemplo de ese mismo documento, no inventados de cero.
export const designEventsMock: DesignEventsResponse = {
  distribucion: "gumbel",
  metodo: "momentos",
  parametros: { mu: 142.5, sigma: 38.2 },
  eventos_diseno: [
    { periodo_retorno: 2, valor: 138.4 },
    { periodo_retorno: 5, valor: 176.9 },
    { periodo_retorno: 10, valor: 223.0 },
    { periodo_retorno: 25, valor: 260.4 },
    { periodo_retorno: 50, valor: 290.9 },
    { periodo_retorno: 100, valor: 312.7 },
    { periodo_retorno: 200, valor: 345.6 },
    { periodo_retorno: 500, valor: 378.4 },
  ],
  grafico_ajuste: null,
  analysis_id: null,
};
