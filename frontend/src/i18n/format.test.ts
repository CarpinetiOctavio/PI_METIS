import { describe, expect, it } from "vitest";
import { formatAxis } from "./format";

describe("formatAxis", () => {
  it("formats an integer without decimal padding", () => {
    // F2 (fix pre-reunión) — a diferencia de formatNum() (5 decimales fijos,
    // pensado para tablas), los ticks de eje no deben rellenar con ceros.
    expect(formatAxis(1000)).toBe("1.000");
  });

  it("caps at 2 decimals for non-integer values", () => {
    expect(formatAxis(800.123456)).toBe("800,12");
  });

  it("does not pad short decimals", () => {
    expect(formatAxis(2.5)).toBe("2,5");
  });
});
