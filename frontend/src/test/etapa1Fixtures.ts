import type { Etapa1Datos, TestResultDetail } from "../api/types";

/** Bloque `datos` de Etapa 1: doce máximos anuales (2000-2011) con carga anual y
 * el atípico de Chow en la posición 5. Compartido por los tests de los gráficos y
 * del panel de exclusión — antes cada archivo armaba el suyo. */
export function makeEtapa1Datos(overrides: Partial<Etapa1Datos> = {}): Etapa1Datos {
  const anios = Array.from({ length: 12 }, (_, i) => 2000 + i);
  return {
    resolucion_original: "anual",
    resolucion_serie_original: null,
    serie_efectiva: anios.map((_, i) => 100 + i * 3),
    timestamps_efectivos: anios.map((anio) => ({ iso: `${anio}-01-01`, anio })),
    serie_original: null,
    timestamps_originales: null,
    indice_atipico: 5,
    serie_calendario: null,
    ...overrides,
  };
}

/** `TestResultDetail` con los campos comunes en null — base para armar una
 * prueba a mano en los tests que no necesitan un payload real. */
export function makeTestResult(overrides: Partial<TestResultDetail> = {}): TestResultDetail {
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

const ANDERSON_N = 16;
const ANDERSON_R = [0.35, 0.1, -0.62, 0.05, -0.2, 0.18];

/** Anderson con un desglose de 6 lags (n = 16). Las bandas se calculan con la
 * Ec. III-3 solo para que el fixture sea coherente; en producción las trae
 * `core/`. El lag 3 (r = −0,62) es el único fuera de banda y el que da el
 * estadístico. Es un MOCK del contrato propuesto (Tanda 2 del plan de feedback
 * de directores): el backend todavía no emite `desglose`. */
export function makeAndersonConDesglose(): TestResultDetail {
  const denominador = 1000;
  const desglose = ANDERSON_R.map((r, i) => {
    const k = i + 1;
    const semiancho = (1.96 * Math.sqrt(ANDERSON_N - k - 1)) / (ANDERSON_N - k);
    const centro = -1 / (ANDERSON_N - k);
    const banda_inf = centro - semiancho;
    const banda_sup = centro + semiancho;
    return { k, numerador: r * denominador, r_k: r, banda_inf, banda_sup, fuera: r < banda_inf || r > banda_sup };
  });
  return makeTestResult({
    prueba: "anderson",
    estadistico: -0.62,
    valor_critico: 0.3,
    veredicto: "aprobada",
    explicacion: {
      ecuacion: "III-1",
      terminos: { n: ANDERSON_N, k: 3, media: 50, numerador: -620, denominador, k_max: 6, lags_fuera: 1, tolerancia: 1 },
      desglose,
    },
  });
}

/** Chow con un desglose de 4 observaciones; la tercera tiene el z máximo. */
export function makeChowConDesglose(): TestResultDetail {
  const x = [100, 110, 400, 105];
  const ln = x.map((v) => Math.log(v));
  const media = ln.reduce((a, b) => a + b, 0) / ln.length;
  const z = ln.map((v) => Math.abs(v - media));
  return makeTestResult({
    prueba: "chow",
    estadistico: Math.max(...z),
    valor_critico: 2.1,
    veredicto: "rechazada",
    explicacion: {
      ecuacion: "Bulletin 17B",
      terminos: { n: 4, media_log: media, s_log: 1, t_bonferroni: 3 },
      desglose: x.map((v, i) => ({ i: i + 1, x_i: v, ln_x_i: ln[i], z_i: z[i] })),
    },
  });
}
