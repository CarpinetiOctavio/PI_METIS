import { describe, expect, it } from "vitest";
import { textoParticionCramer } from "./cramer";

describe("textoParticionCramer (D-18)", () => {
  it.each([
    ["default", 24, 12, "últimos 60 % y 30 % (n₁ = 24, n₂ = 12)"],
    [{ n1_pct: 70, n2_pct: 35 }, 28, 14, "personalizada: últimos 70 % y 35 % (n₁ = 28, n₂ = 14)"],
    ["default", null, null, "últimos 60 % y 30 %"],
  ] as const)("%j con n₁=%s, n₂=%s → %s", (particion, n1, n2, esperado) => {
    expect(textoParticionCramer(particion, n1, n2)).toBe(esperado);
  });

  it.each([undefined, null])("sin partición registrada (%s) no inventa nada", (particion) => {
    expect(textoParticionCramer(particion, 24, 12)).toBeNull();
  });
});
