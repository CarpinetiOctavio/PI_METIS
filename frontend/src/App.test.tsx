import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ThemeProvider } from "./theme/ThemeProvider";
import App from "./App";

describe("App", () => {
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
