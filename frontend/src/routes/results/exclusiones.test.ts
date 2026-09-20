import { describe, expect, it, vi } from "vitest";
import {
  csvSinExcluidos,
  descargarCsv,
  hayExcluidoInterior,
  nombreCsvSinAtipicos,
  puntosDeSerie,
} from "./exclusiones";
import { makeEtapa1Datos } from "../../test/etapa1Fixtures";

const PUNTOS = [
  { indice: 0, anio: 2000, valor: 94.71 },
  { indice: 1, anio: 2001, valor: 89.83 },
  { indice: 2, anio: 2002, valor: 950 },
  { indice: 3, anio: 2003, valor: 105.13 },
];

describe("puntosDeSerie", () => {
  it("empareja cada valor de serie_efectiva con su año, con el índice de esa serie", () => {
    const datos = makeEtapa1Datos({
      serie_efectiva: [94.71, 89.83, 950],
      timestamps_efectivos: [
        { iso: "2000-01-01", anio: 2000 },
        { iso: "2001-01-01", anio: 2001 },
        { iso: "2002-01-01", anio: 2002 },
      ],
    });
    expect(puntosDeSerie(datos)).toEqual([
      { indice: 0, anio: 2000, valor: 94.71 },
      { indice: 1, anio: 2001, valor: 89.83 },
      { indice: 2, anio: 2002, valor: 950 },
    ]);
  });

  it("sin timestamps no hay forma de rotular los puntos: lista vacía", () => {
    expect(puntosDeSerie(makeEtapa1Datos({ timestamps_efectivos: null }))).toEqual([]);
  });
});

describe("csvSinExcluidos", () => {
  it.each([
    ["sin excluidos, todos los puntos", [], ["2000,94.71", "2001,89.83", "2002,950", "2003,105.13"]],
    ["el del medio", [2], ["2000,94.71", "2001,89.83", "2003,105.13"]],
    ["el primero y el último", [0, 3], ["2001,89.83", "2002,950"]],
    ["todos", [0, 1, 2, 3], []],
  ])("%s", (_caso, excluidos, filas) => {
    expect(csvSinExcluidos(PUNTOS, new Set(excluidos))).toBe(["periodo,valor", ...filas].join("\n") + "\n");
  });

  it("no usa notación científica ni coma decimal (para que METIS lo pueda volver a leer)", () => {
    const csv = csvSinExcluidos([{ indice: 0, anio: 1999, valor: 0.00012 }], new Set());
    expect(csv).toContain("1999,0.00012");
  });
});

describe("nombreCsvSinAtipicos", () => {
  it.each([
    ["estacion_04.csv", "estacion_04_sin_atipicos.csv"],
    ["Serie.mensual.xlsx", "Serie.mensual_sin_atipicos.csv"],
    ["C:\\datos\\rio.csv", "rio_sin_atipicos.csv"],
    ["sin_extension", "sin_extension_sin_atipicos.csv"],
    [undefined, "serie_sin_atipicos.csv"],
    [null, "serie_sin_atipicos.csv"],
    ["", "serie_sin_atipicos.csv"],
  ])("%j → %s", (entrada, esperado) => {
    expect(nombreCsvSinAtipicos(entrada)).toBe(esperado);
  });
});

describe("hayExcluidoInterior", () => {
  it.each([
    ["ninguno", [], false],
    ["solo el primero", [0], false],
    ["solo el último", [9], false],
    ["el primero y el último", [0, 9], false],
    ["uno del medio", [4], true],
    ["uno del medio junto con un extremo", [0, 4], true],
  ])("%s", (_caso, excluidos, esperado) => {
    expect(hayExcluidoInterior(new Set(excluidos), 10)).toBe(esperado);
  });
});

describe("descargarCsv", () => {
  it("crea un Blob text/csv, dispara la descarga con el nombre pedido y libera la URL", () => {
    const crear = vi.fn(() => "blob:fake");
    const liberar = vi.fn();
    vi.stubGlobal("URL", { createObjectURL: crear, revokeObjectURL: liberar });
    const clic = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

    descargarCsv("rio_sin_atipicos.csv", "periodo,valor\n2000,1\n");

    const blob = (crear.mock.calls[0] as unknown as [Blob])[0];
    expect(blob.type).toContain("text/csv");
    expect(clic).toHaveBeenCalledTimes(1);
    expect(liberar).toHaveBeenCalledWith("blob:fake");
    expect(document.querySelector("a[download]")).toBeNull(); // no deja el enlace colgado

    vi.unstubAllGlobals();
    clic.mockRestore();
  });
});
