import { apiFetch } from "./client";

export interface PingResponse {
  status: string;
}

export async function checkBackendPing(): Promise<PingResponse> {
  const response = await apiFetch("/ping");
  if (!response.ok) {
    throw new Error(`Backend ping falló con status ${response.status}`);
  }
  return response.json();
}
