import { afterEach, describe, expect, it, vi } from "vitest";
import { postOutlierDecision } from "./analysis";

describe("postOutlierDecision", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("posts session_id, decision, and dato_atipico to /outlier-decision", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ ok: true, pipeline_continua: true }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await postOutlierDecision({
      session_id: "sess-1",
      decisiones: [{ indice: 7, decision: "rechazar" }],
    });

    expect(result).toEqual({ ok: true, pipeline_continua: true });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/analysis/outlier-decision",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          session_id: "sess-1",
          decisiones: [{ indice: 7, decision: "rechazar" }],
        }),
      }),
    );
  });
});
