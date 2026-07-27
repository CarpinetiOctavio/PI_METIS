import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ThemeProvider } from "../theme/ThemeProvider";
import { TopBar } from "./TopBar";

describe("TopBar", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows the METIS wordmark, backend status, and mode badge", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: "ok" }),
      }),
    );

    render(
      <ThemeProvider>
        <TopBar />
      </ThemeProvider>,
    );
    expect(screen.getByText("METIS")).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByTestId("backend-status")).toHaveTextContent(
        "Backend conectado",
      ),
    );
    expect(screen.getByTestId("mode-badge")).toBeInTheDocument();
  });

  it("toggles the mode badge text when the toggle button is clicked", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: "ok" }),
      }),
    );

    render(
      <ThemeProvider>
        <TopBar />
      </ThemeProvider>,
    );
    await waitFor(() =>
      expect(screen.getByTestId("backend-status")).toHaveTextContent(
        "Backend conectado",
      ),
    );
    const badge = screen.getByTestId("mode-badge");
    const before = badge.textContent;
    fireEvent.click(screen.getByRole("button", { name: /cambiar tema/i }));
    expect(badge.textContent).not.toBe(before);
  });
});
