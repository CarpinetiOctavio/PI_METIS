import { describe, expect, it } from "vitest";
import { instrumentoTokens } from "./tokens";

describe("instrumentoTokens", () => {
  it("defines both light and dark sets with matching keys", () => {
    const lightKeys = Object.keys(instrumentoTokens.light).sort();
    const darkKeys = Object.keys(instrumentoTokens.dark).sort();
    expect(lightKeys).toEqual(darkKeys);
  });

  it("uses the exact accent color confirmed for Instrumento dark mode", () => {
    expect(instrumentoTokens.dark.acc).toBe("#22D3EE");
  });

  it("uses the exact background confirmed for Instrumento light mode", () => {
    expect(instrumentoTokens.light.bg).toBe("#EDF1F5");
  });
});
