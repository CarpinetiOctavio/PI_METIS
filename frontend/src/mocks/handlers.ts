import { http, HttpResponse } from "msw";
import { designEventsMock } from "./designEvents.mock";

// Único endpoint interceptado: POST /api/v1/analysis/design-events tiene un
// contrato REAL documentado (api-contracts.md) pero NO está implementado en
// el backend (frontend-integration.md §3/§6, gap confirmado leyendo
// metis/api/v1/analysis.py). El ranking de Etapa 2 NO tiene handler acá
// porque no existe como endpoint REST en ningún documento — solo se
// menciona como evento SSE (`result_etapa2_ranking`) que el backend nunca
// emite hoy; inventar una URL para interceptar sería fabricar un contrato
// que no existe en ningún lado. RankingPage usa el mock directo, sin red.
export const handlers = [
  http.post("/api/v1/analysis/design-events", () => {
    return HttpResponse.json(designEventsMock);
  }),
];
