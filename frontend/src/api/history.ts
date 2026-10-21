import { requestJson } from "./client";
import type { AnalysisDetail, ExclusionGuardada, HistoryItem, OkResponse } from "./types";

export function listHistory(incluirArchivados = false): Promise<HistoryItem[]> {
  const query = incluirArchivados ? "?archivados=true" : "";
  return requestJson<HistoryItem[]>(`/api/v1/history/${query}`);
}

export function getHistoryItem(id: string): Promise<AnalysisDetail> {
  return requestJson<AnalysisDetail>(`/api/v1/history/${id}`);
}

// DECISIÓN 048 — soft-delete, reversible.
export function archiveAnalysis(id: string): Promise<OkResponse> {
  return requestJson<OkResponse>(`/api/v1/history/${id}/archive`, {
    method: "POST",
  });
}

export function unarchiveAnalysis(id: string): Promise<OkResponse> {
  return requestJson<OkResponse>(`/api/v1/history/${id}/unarchive`, {
    method: "POST",
  });
}

// DECISIÓN 080 — exclusiones guardadas a pedido. No tocan el resultado ni las
// decisiones del análisis: los resultados se recalculan con simulate-exclusion.
export function guardarExclusion(
  id: string,
  indicesExcluidos: number[],
): Promise<ExclusionGuardada> {
  return requestJson<ExclusionGuardada>(`/api/v1/history/${id}/exclusiones`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ indices_excluidos: indicesExcluidos }),
  });
}

export function quitarExclusion(id: string, exclusionId: string): Promise<OkResponse> {
  return requestJson<OkResponse>(`/api/v1/history/${id}/exclusiones/${exclusionId}`, {
    method: "DELETE",
  });
}
