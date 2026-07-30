import { postJson } from "./client";
import type { OutlierDecisionRequest, OutlierDecisionResponse } from "./types";

export function postOutlierDecision(
  body: OutlierDecisionRequest,
): Promise<OutlierDecisionResponse> {
  return postJson<OutlierDecisionResponse>(
    "/api/v1/analysis/outlier-decision",
    body,
  );
}
