import { describe, expect, it } from "vitest";
import { render } from "@testing-library/react";
import { Sparkline } from "./Sparkline";

describe("Sparkline", () => {
  it("renders a path through the given values", () => {
    const { container } = render(<Sparkline valores={[10, 20, 15, 30]} />);
    const path = container.querySelector(".sparkline__path");
    expect(path?.getAttribute("d")).toBeTruthy();
  });

  it("renders nothing with fewer than two values", () => {
    const { container } = render(<Sparkline valores={[10]} />);
    expect(container.querySelector(".sparkline")).not.toBeInTheDocument();
  });

  it("does not crash with a flat series (all values equal)", () => {
    const { container } = render(<Sparkline valores={[5, 5, 5, 5]} />);
    const path = container.querySelector(".sparkline__path");
    expect(path?.getAttribute("d")).toBeTruthy();
  });

  it("is decorative — hidden from the accessibility tree", () => {
    const { container } = render(<Sparkline valores={[1, 2, 3]} />);
    expect(container.querySelector("svg")).toHaveAttribute("aria-hidden", "true");
  });
});
