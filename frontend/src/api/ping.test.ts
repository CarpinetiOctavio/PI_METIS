import { afterEach, describe, expect, it, vi } from "vitest";
import { checkBackendPing } from "./ping";

describe("checkBackendPing", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("calls /ping with credentials included and returns the parsed body", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: "ok" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await checkBackendPing();

    expect(result).toEqual({ status: "ok" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/ping",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("throws when the backend responds with a non-ok status", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 500 }),
    );

    await expect(checkBackendPing()).rejects.toThrow();
  });
});
