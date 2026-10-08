import { describe, expect, it } from "vitest";
import {
  notaPeriodoRetorno,
  rotuloEjePeriodoRetorno,
  rotuloValorDiseno,
  unidadPeriodoRetorno,
} from "./periodoRetorno";

// Mismo texto que backend/tests/unit/reportes/test_pdf.py (DECISIÓN 076).
describe("rótulos del período de retorno", () => {
  it("carga anual: T en años, sin criterio de año ni variable agregada", () => {
    const ctx = { resolucion: "anual" as const, mesInicioAnio: 7 };
    expect(rotuloEjePeriodoRetorno(ctx)).toBe("Período de retorno T (años)");
    expect(rotuloValorDiseno(ctx)).toBe("Valor de diseño");
    expect(notaPeriodoRetorno(ctx)).toMatch(/^La distribución se ajustó a la serie de máximos anuales/);
    expect(notaPeriodoRetorno(ctx)).toContain("1/T");
  });

  it("sin contexto se comporta como la carga anual", () => {
    expect(unidadPeriodoRetorno()).toBe("años");
    expect(rotuloValorDiseno(undefined)).toBe("Valor de diseño");
  });

  it("carga mensual: T sigue en años y se explica por qué no en meses", () => {
    const ctx = { resolucion: "mensual" as const, mesInicioAnio: 7 };
    expect(rotuloEjePeriodoRetorno(ctx)).toBe("Período de retorno T (años, de julio a junio)");
    expect(rotuloValorDiseno(ctx)).toBe("Valor de diseño (valor mensual máximo del año)");
    const nota = notaPeriodoRetorno(ctx);
    expect(nota).toMatch(/^Se cargó una serie mensual\./);
    expect(nota).toContain("toma el valor mensual máximo de cada año (de julio a junio)");
    expect(nota).toContain("T se mide en años y no en meses");
  });

  it("carga diaria: nombra picos o medias y el año calendario", () => {
    const pico = { resolucion: "diaria" as const, mesInicioAnio: 1, variableDiaria: "pico" as const };
    const media = { ...pico, variableDiaria: "media" as const };
    expect(unidadPeriodoRetorno(pico)).toBe("años, de enero a diciembre");
    expect(rotuloValorDiseno(pico)).toBe("Valor de diseño (pico diario máximo del año)");
    expect(rotuloValorDiseno(media)).toBe("Valor de diseño (media diaria máxima del año)");
    expect(notaPeriodoRetorno(media)).toContain("toma la media diaria máxima de cada año (de enero a diciembre)");
    expect(notaPeriodoRetorno(pico)).toContain("T se mide en años y no en días");
  });

  it("carga diaria sin variable declarada (análisis viejo) asume picos, como el backend", () => {
    expect(rotuloValorDiseno({ resolucion: "diaria" })).toBe("Valor de diseño (pico diario máximo del año)");
  });

  it("agregada sin mes de inicio conocido no inventa un rango", () => {
    const ctx = { resolucion: "mensual" as const };
    expect(unidadPeriodoRetorno(ctx)).toBe("años");
    expect(notaPeriodoRetorno(ctx)).toContain("de cada año y ajusta");
  });
});
