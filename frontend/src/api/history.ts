import { requestJson } from "./client";
import type { AnalysisDetail, HistoryItem } from "./types";

export function listHistory(): Promise<HistoryItem[]> {
  return requestJson<HistoryItem[]>("/api/v1/history/");
}

export function getHistoryItem(id: string): Promise<AnalysisDetail> {
  return requestJson<AnalysisDetail>(`/api/v1/history/${id}`);
}
