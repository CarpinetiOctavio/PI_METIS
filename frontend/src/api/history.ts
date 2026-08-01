import { requestJson } from "./client";
import type { AnalysisDetail, HistoryItem, OkResponse } from "./types";

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
