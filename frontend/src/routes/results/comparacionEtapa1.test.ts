import { describe, expect, it } from "vitest";
import { avisosNuevos, compararPruebas } from "./comparacionEtapa1";
import { makeEtapa1Result, makePrueba, makeSimulacion } from "../../test/simulacionFixtures";

describe("compararPruebas", () => {
  const original = makeEtapa1Result();

  it("alinea por prueba y marca solo las que cambiaron de veredicto", () => {
    const filas = compararPruebas(original, makeSimulacion().etapa1);

    expect(filas.map((f) => [f.prueba, f.cambio])).toEqual([
      ["anderson", true], // aprobada → rechazada
      ["helmert", false],
      ["chow", true], // rechazada → aprobada
    ]);
    expect(filas[0].original?.veredicto).toBe("aprobada");
    expect(filas[0].simulado?.veredicto).toBe("rechazada");
  });

  it.each([
    ["ninguna cambia", makeEtapa1Result(), 0],
    ["una prueba deja de ejecutarse", makeEtapa1Result({ independencia: [] }), 1],
    [
      "una prueba aparece solo en la simulación",
      makeEtapa1Result({
        tendencia: [makePrueba({ prueba: "mann_kendall", veredicto: "aprobada" })],
      }),
      1,
    ],
  ])("cuenta los cambios: %s", (_caso, simulado, esperados) => {
    expect(compararPruebas(original, simulado).filter((f) => f.cambio)).toHaveLength(esperados);
  });

  it("una prueba que falta de un lado aparece con null de ese lado", () => {
    const filas = compararPruebas(original, makeEtapa1Result({ independencia: [] }));
    const anderson = filas.find((f) => f.prueba === "anderson")!;
    expect(anderson.original).not.toBeNull();
    expect(anderson.simulado).toBeNull();
  });
});

describe("avisosNuevos", () => {
  it("devuelve solo los avisos que la corrida original no tenía", () => {
    const previo = { codigo: "CONTRACT_LENGTH_WARNING", nivel: "normal" as const, descripcion: "x" };
    const original = makeEtapa1Result({ warnings: [previo] });
    const simulado = makeSimulacion().etapa1;
    simulado.warnings = [previo, ...simulado.warnings];

    expect(avisosNuevos(original, simulado).map((w) => w.codigo)).toEqual([
      "CONTRACT_IRREGULAR_SPACING",
    ]);
  });
});
