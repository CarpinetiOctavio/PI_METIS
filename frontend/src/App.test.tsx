import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { ThemeProvider } from "./theme/ThemeProvider";
import App from "./App";

describe("App", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the entry page at the root route", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ status: "ok" }),
      }),
    );

    render(
      <ThemeProvider>
        <App />
      </ThemeProvider>,
    );
    expect(
      screen.getByRole("heading", { name: "Puerta de entrada" }),
    ).toBeInTheDocument();
    expect(screen.getByText("METIS")).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByTestId("backend-status")).toHaveTextContent(
        "Backend conectado",
      ),
    );
  });
});
