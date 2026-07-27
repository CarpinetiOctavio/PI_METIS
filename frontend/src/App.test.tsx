import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "./theme/ThemeProvider";
import App from "./App";

describe("App", () => {
  beforeEach(() => {
    // jsdom's own matchMedia support for prefers-color-scheme is unreliable
    // across versions — stub it explicitly, same precedent as
    // ThemeProvider.test.tsx, since App renders TopBar inside <ThemeProvider>.
    vi.spyOn(window, "matchMedia").mockReturnValue({
      matches: false,
    } as MediaQueryList);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders the entry page at the root route", () => {
    render(
      <ThemeProvider>
        <App />
      </ThemeProvider>,
    );
    expect(
      screen.getByRole("heading", { name: "Puerta de entrada" }),
    ).toBeInTheDocument();
    expect(screen.getByText("METIS")).toBeInTheDocument();
  });
});
