import { postJson } from "./client";
import type { DesignEventsRequest, DesignEventsResponse } from "./types";

// Contrato real documentado (api-contracts.md), pero el endpoint no está
// implementado en el backend — interceptado por MSW en dev (mocks/handlers.ts).
export function postDesignEvents(
  body: DesignEventsRequest,
): Promise<DesignEventsResponse> {
  return postJson<DesignEventsResponse>("/api/v1/analysis/design-events", body);
}
