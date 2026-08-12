import { describe, expect, it } from "vitest";
import { calcularCuartiles } from "./quartiles";

describe("calcularCuartiles", () => {
  it("computes Tukey hinges for an odd-length sample (textbook example)", () => {
    // Ejemplo canónico de bisagras de Tukey: 1..9, Q1=2.5, mediana=5, Q3=7.5.
    const stats = calcularCuartiles([9, 1, 5, 3, 7, 2, 8, 4, 6]);
    expect(stats).toEqual({ min: 1, q1: 2.5, mediana: 5, q3: 7.5, max: 9 });
  });

  it("computes Tukey hinges for an even-length sample", () => {
    const stats = calcularCuartiles([8, 2, 6, 4, 1, 7, 3, 5]);
    expect(stats).toEqual({ min: 1, q1: 2.5, mediana: 4.5, q3: 6.5, max: 8 });
  });

  it("does not mutate the input array (sorts a copy)", () => {
    const valores = [3, 1, 2];
    calcularCuartiles(valores);
    expect(valores).toEqual([3, 1, 2]);
  });

  it("returns null for an empty sample", () => {
    expect(calcularCuartiles([])).toBeNull();
  });

  it("collapses to a single value for a sample of one", () => {
    expect(calcularCuartiles([42])).toEqual({
      min: 42,
      q1: 42,
      mediana: 42,
      q3: 42,
      max: 42,
    });
  });
});
