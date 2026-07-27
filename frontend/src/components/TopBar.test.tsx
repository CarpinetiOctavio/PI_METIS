import { describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeProvider } from "../theme/ThemeProvider";
import { TopBar } from "./TopBar";

describe("TopBar", () => {
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
