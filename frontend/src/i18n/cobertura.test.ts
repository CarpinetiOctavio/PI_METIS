import { describe, expect, it } from "vitest";
import { parseCobertura, textoCoberturaAnalisis } from "./cobertura";
import { makeEtapa1Datos } from "../test/etapa1Fixtures";

// DECISIÓN 081 — cobertura mínima de los años interiores, a criterio del usuario.

describe("parseCobertura", () => {
  it.each(["50", "90", "100", " 75 "])("acepta %s", (texto) => {
    expect(parseCobertura(texto)).toEqual({ value: Number(texto.trim()) });
  });

  it.each(["49", "101", "90.5", "", "abc"])("rechaza %s", (texto) => {
    expect(parseCobertura(texto)).toEqual({
      error:
        "La cobertura mínima de los años interiores tiene que ser un porcentaje entero entre 50 y 100.",
    });
  });
});

describe("textoCoberturaAnalisis", () => {
  it("con carga anual no hay nada que informar", () => {
    expect(textoCoberturaAnalisis(makeEtapa1Datos({ resolucion_original: "anual" }))).toBeNull();
    expect(textoCoberturaAnalisis(null)).toBeNull();
  });

  it("con carga mensual o diaria informa el valor usado", () => {
    expect(
      textoCoberturaAnalisis(
        makeEtapa1Datos({ resolucion_original: "mensual", cobertura_minima_interior: 90 }),
      ),
    ).toBe("90 %");
    expect(
      textoCoberturaAnalisis(
        makeEtapa1Datos({ resolucion_original: "diaria", cobertura_minima_interior: 100 }),
      ),
    ).toBe("100 %");
  });

  it("un análisis anterior sin el campo se informa como 100 % implícito", () => {
    expect(textoCoberturaAnalisis(makeEtapa1Datos({ resolucion_original: "mensual" }))).toBe(
      "100 % (el único criterio disponible cuando se corrió el análisis)",
    );
  });
});
