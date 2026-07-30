import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { useBackendPing } from "./useBackendPing";

function Probe() {
  const { state } = useBackendPing();
  return <span data-testid="state">{state}</span>;
}

describe("useBackendPing", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("starts in loading state then resolves to ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: "ok" }),
      }),
    );

    render(<Probe />);

    expect(screen.getByTestId("state")).toHaveTextContent("loading");
    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent("ok"),
    );
  });

  it("resolves to error when the ping fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 500 }),
    );

    render(<Probe />);

    await waitFor(() =>
      expect(screen.getByTestId("state")).toHaveTextContent("error"),
    );
  });
});
