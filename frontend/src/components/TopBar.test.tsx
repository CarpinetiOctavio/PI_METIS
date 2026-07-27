import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeProvider } from "../theme/ThemeProvider";
import { TopBar } from "./TopBar";

describe("TopBar", () => {
  beforeEach(() => {
    // jsdom's own matchMedia support for prefers-color-scheme is unreliable
    // across versions — stub it explicitly, same precedent as
    // ThemeProvider.test.tsx, since TopBar renders inside <ThemeProvider>.
    vi.spyOn(window, "matchMedia").mockReturnValue({
      matches: false,
    } as MediaQueryList);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows the METIS wordmark and the current mode badge", () => {
    render(
      <ThemeProvider>
        <TopBar />
      </ThemeProvider>,
    );
    expect(screen.getByText("METIS")).toBeInTheDocument();
    expect(screen.getByTestId("mode-badge")).toBeInTheDocument();
  });

  it("toggles the mode badge text when the toggle button is clicked", () => {
    render(
      <ThemeProvider>
        <TopBar />
      </ThemeProvider>,
    );
    const badge = screen.getByTestId("mode-badge");
    const before = badge.textContent;
    fireEvent.click(screen.getByRole("button", { name: /cambiar tema/i }));
    expect(badge.textContent).not.toBe(before);
  });
});
