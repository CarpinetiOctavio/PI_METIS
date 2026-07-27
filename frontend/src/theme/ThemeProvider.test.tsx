import { beforeEach, describe, expect, it } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ThemeProvider, useTheme } from "./ThemeProvider";

function Consumer() {
  const { mode, toggleMode } = useTheme();
  return (
    <div>
      <span data-testid="mode">{mode}</span>
      <button onClick={toggleMode}>toggle</button>
    </div>
  );
}

describe("ThemeProvider", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute("data-theme");
    document.documentElement.removeAttribute("data-mode");
  });

  it("sets data-theme to instrumento on the root element", () => {
    render(
      <ThemeProvider>
        <Consumer />
      </ThemeProvider>,
    );
    expect(document.documentElement.dataset.theme).toBe("instrumento");
  });

  it("defaults to light when there is no stored preference and no dark media match", () => {
    render(
      <ThemeProvider>
        <Consumer />
      </ThemeProvider>,
    );
    expect(screen.getByTestId("mode")).toHaveTextContent("light");
    expect(document.documentElement.dataset.mode).toBe("light");
  });

  it("toggles mode and persists the choice to localStorage", () => {
    render(
      <ThemeProvider>
        <Consumer />
      </ThemeProvider>,
    );

    fireEvent.click(screen.getByRole("button", { name: "toggle" }));

    expect(screen.getByTestId("mode")).toHaveTextContent("dark");
    expect(document.documentElement.dataset.mode).toBe("dark");
    expect(localStorage.getItem("metis-theme-mode")).toBe("dark");
  });

  it("reads a stored preference instead of the media query on mount", () => {
    localStorage.setItem("metis-theme-mode", "dark");

    render(
      <ThemeProvider>
        <Consumer />
      </ThemeProvider>,
    );

    expect(screen.getByTestId("mode")).toHaveTextContent("dark");
  });
});
