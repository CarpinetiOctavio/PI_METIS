import { postJson, requestJson } from "./client";
import type {
  DesignEventsRecalcRequest,
  DesignEventsRecalcResponse,
  DistributionDecisionRequest,
  DistributionDecisionResponse,
  OutlierDecisionRequest,
  OutlierDecisionResponse,
  PreviewColumnsResponse,
  SimulateExclusionRequest,
  SimulateExclusionResponse,
} from "./types";

export function postOutlierDecision(
  body: OutlierDecisionRequest,
): Promise<OutlierDecisionResponse> {
  return postJson<OutlierDecisionResponse>(
    "/api/v1/analysis/outlier-decision",
    body,
  );
}

// DECISIÓN 052 — reemplaza al design-events documentado y nunca
// implementado. Misma forma que outlier-decision: el cliente manda la
// decisión, el resultado (result_etapa2_eventos) llega por el stream SSE
// ya abierto, no en la respuesta de este POST.
export function postDistributionDecision(
  body: DistributionDecisionRequest,
): Promise<DistributionDecisionResponse> {
  return postJson<DistributionDecisionResponse>(
    "/api/v1/analysis/distribution-decision",
    body,
  );
}

// Bloque C2c (plan post-avance) — historial interactivo: recalcula eventos
// de diseño para una distribución+método explorados desde HistoryDetailPage,
// sin ningún stream ni session_id de por medio (DECISIÓN 062, "explorar no
// es decidir" — no confundir con postDistributionDecision).
export function postRecalcularDesignEvents(
  analysisId: string,
  body: DesignEventsRecalcRequest,
): Promise<DesignEventsRecalcResponse> {
  return postJson<DesignEventsRecalcResponse>(
    `/api/v1/analysis/${analysisId}/design-events`,
    body,
  );
}

// Ítem A del plan de feedback de directores — what-if de atípicos. El endpoint
// todavía no existe en el backend (Tanda 2): mientras tanto la interfaz que lo
// usa queda apagada salvo que se habilite `VITE_SIMULATE_EXCLUSION=1` (para
// probar contra un backend que ya lo tenga o un stub). Cuando el backend lo
// publique se borra el flag y la interfaz queda siempre encendida.
export function simulacionExclusionDisponible(): boolean {
  return import.meta.env.VITE_SIMULATE_EXCLUSION === "1";
}

export function postSimularExclusion(
  body: SimulateExclusionRequest,
): Promise<SimulateExclusionResponse> {
  return postJson<SimulateExclusionResponse>("/api/v1/analysis/simulate-exclusion", body);
}

// DECISIÓN 047 — multipart, no JSON, así que no usa postJson (fija
// Content-Type: application/json). requestJson no toca headers si no se
// los pasan, dejando que el navegador ponga el boundary del multipart solo.
export function postPreviewColumns(archivo: File): Promise<PreviewColumnsResponse> {
  const body = new FormData();
  body.append("archivo", archivo);
  return requestJson<PreviewColumnsResponse>("/api/v1/analysis/preview-columns", {
    method: "POST",
    body,
  });
}
