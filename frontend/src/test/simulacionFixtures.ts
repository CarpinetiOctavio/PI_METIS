import type {
  Etapa1Result,
  SimulateExclusionResponse,
  TestResultDetail,
} from "../api/types";

/** Una prueba de Etapa 1 con los campos comunes en null. */
export function makePrueba(overrides: Partial<TestResultDetail> = {}): TestResultDetail {
  return {
    prueba: "anderson",
    estadistico: null,
    valor_critico: null,
    veredicto: "aprobada",
    warning_codigo: null,
    warning_nivel: null,
    n1: null,
    n2: null,
    valor_atipico: null,
    indice_atipico: null,
    explicacion: null,
    ...overrides,
  };
}

/** Resultado de Etapa 1 mínimo pero completo: Anderson y Helmert aprueban, Chow
 * marca un atípico. Base de los tests del what-if (original vs. simulado). */
export function makeEtapa1Result(overrides: Partial<Etapa1Result> = {}): Etapa1Result {
  return {
    contract: { bloqueante: false, codigo_error: null, warnings: [] },
    descriptive: {
      n: 12,
      media: 110,
      mediana: 108,
      desvio_estandar: 10,
      coef_variacion: 0.09,
      coef_asimetria: 0.2,
      minimo: 100,
      maximo: 133,
    },
    independencia: [makePrueba({ prueba: "anderson", estadistico: 0.2, veredicto: "aprobada" })],
    homogeneidad: [makePrueba({ prueba: "helmert", estadistico: 1, veredicto: "aprobada" })],
    tendencia: [],
    atipicos: [
      makePrueba({ prueba: "chow", estadistico: 3, veredicto: "rechazada", valor_atipico: 115 }),
    ],
    nivel_independencia: "independiente",
    nivel_homogeneidad: "homogeneidad_ok",
    nivel_confianza: "con_warnings",
    warnings: [],
    ...overrides,
  };
}

/** Respuesta de `POST /analysis/simulate-exclusion` (mock del contrato
 * propuesto: el backend todavía no lo tiene). Sin el año 2005, Anderson pasa a
 * rechazada, Chow deja de marcar atípico y aparece el aviso de espaciado. */
export function makeSimulacion(
  overrides: Partial<SimulateExclusionResponse> = {},
): SimulateExclusionResponse {
  const original = makeEtapa1Result();
  return {
    etapa1: makeEtapa1Result({
      descriptive: { ...original.descriptive!, n: 11 },
      independencia: [
        makePrueba({
          prueba: "anderson",
          estadistico: 0.6,
          veredicto: "rechazada",
          warning_nivel: "critico",
        }),
      ],
      atipicos: [makePrueba({ prueba: "chow", estadistico: 1.2, veredicto: "aprobada" })],
      nivel_independencia: "dependiente",
      warnings: [
        {
          codigo: "CONTRACT_IRREGULAR_SPACING",
          nivel: "normal",
          descripcion: "El espaciado temporal es irregular.",
        },
      ],
    }),
    etapa2: null,
    excluidos: [{ indice: 5, periodo: 2005, valor_original: 115 }],
    serie: [100, 103, 106, 109, 112, 118, 121, 124, 127, 130, 133],
    anios: [2000, 2001, 2002, 2003, 2004, 2006, 2007, 2008, 2009, 2010, 2011],
    ...overrides,
  };
}
