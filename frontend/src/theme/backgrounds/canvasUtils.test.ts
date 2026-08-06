// lerpHex nace con DECISIÓN 051 (ThreadsBackground pasa de THREE.Color.lerp
// a Canvas 2D) — es la única pieza de canvasUtils.ts que no tenía test
// unitario propio hasta ahora (hexToRgba/secureRandom/readCssVar/
// sizeCanvasToViewport se ejercitan indistintamente vía los lifecycle tests
// de los tres fondos).
import { describe, expect, it } from "vitest";
import { lerpHex } from "./canvasUtils";

describe("lerpHex", () => {
  it("t=0 devuelve exactamente el primer color", () => {
    expect(lerpHex("#22d3ee", "#c6f84e", 0)).toBe("#22d3ee");
  });

  it("t=1 devuelve exactamente el segundo color", () => {
    expect(lerpHex("#22d3ee", "#c6f84e", 1)).toBe("#c6f84e");
  });

  it("t=0.5 interpola cada canal RGB por separado", () => {
    // #000000 -> #ffffff a mitad de camino: cada canal 0 + (255-0)*0.5 = 127.5 -> 128
    expect(lerpHex("#000000", "#ffffff", 0.5)).toBe("#808080");
  });

  it("acepta formato corto de 3 dígitos", () => {
    expect(lerpHex("#000", "#fff", 0.5)).toBe("#808080");
  });

  it("acepta hex sin '#' inicial", () => {
    expect(lerpHex("22d3ee", "c6f84e", 0)).toBe("#22d3ee");
  });

  it("redondea el resultado, no lo trunca", () => {
    // 0x10 (16) -> 0x20 (32) a t=0.9: 16 + (32-16)*0.9 = 30.4 -> redondea a 30 (0x1e)
    expect(lerpHex("#101010", "#202020", 0.9)).toBe("#1e1e1e");
  });
});
