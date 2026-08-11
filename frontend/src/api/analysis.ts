import { postJson, requestJson } from "./client";
import type {
  DistributionDecisionRequest,
  DistributionDecisionResponse,
  OutlierDecisionRequest,
  OutlierDecisionResponse,
  PreviewColumnsResponse,
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
