import { postJson, requestJson } from "./client";
import type {
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
