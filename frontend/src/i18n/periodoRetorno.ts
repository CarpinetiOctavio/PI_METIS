import type { Etapa1Datos } from "../api/types";

// Rótulos del período de retorno según la serie que se ajustó (DECISIÓN 076).
//
// METIS ajusta siempre la serie de máximos anuales (DECISIÓN 066): con carga
// mensual o diaria, el paso 0 la agrega a un máximo por año antes de Etapa 1.
// T = 1 / (1 - F) se mide en el intervalo de muestreo de la serie ajustada, así
// que está en años para las tres resoluciones. Lo que cambia con la carga es
// qué representa el valor de diseño y con qué año se agregó, y eso es lo que
// estos rótulos dejan explícito. Mismo texto que el informe PDF
// (backend/metis/reportes/pdf.py): si se cambia uno, cambiar el otro.

export interface ContextoSerie {
  resolucion?: Etapa1Datos["resolucion_original"];
  mesInicioAnio?: number | null;
  variableDiaria?: "pico" | "media" | null;
}

type CargaAgregada = "mensual" | "pico" | "media";

const MAXIMO: Record<CargaAgregada, string> = {
  mensual: "valor mensual máximo",
  pico: "pico diario máximo",
  media: "media diaria máxima",
};

const MAXIMO_CON_ARTICULO: Record<CargaAgregada, string> = {
  mensual: "el valor mensual máximo",
  pico: "el pico diario máximo",
  media: "la media diaria máxima",
};

const CARGA: Record<CargaAgregada, string> = {
  mensual: "una serie mensual",
  pico: "una serie de picos diarios",
  media: "una serie de medias diarias",
};

const MESES = [
  "enero",
  "febrero",
  "marzo",
  "abril",
  "mayo",
  "junio",
  "julio",
  "agosto",
  "septiembre",
  "octubre",
  "noviembre",
  "diciembre",
];

function cargaAgregada(ctx: ContextoSerie | undefined): CargaAgregada | null {
  if (ctx?.resolucion === "mensual") return "mensual";
  if (ctx?.resolucion === "diaria") return ctx.variableDiaria === "media" ? "media" : "pico";
  return null;
}

function mesValido(ctx: ContextoSerie | undefined): number | null {
  const mes = ctx?.mesInicioAnio;
  return typeof mes === "number" && Number.isInteger(mes) && mes >= 1 && mes <= 12 ? mes : null;
}

// mes=7 -> "de julio a junio"; mes=1 -> "de enero a diciembre".
function rangoAnio(mes: number): string {
  const fin = mes === 1 ? 12 : mes - 1;
  return `de ${MESES[mes - 1]} a ${MESES[fin - 1]}`;
}

/** "años", o "años, de julio a junio" cuando la serie se agregó. */
export function unidadPeriodoRetorno(ctx?: ContextoSerie): string {
  const mes = mesValido(ctx);
  if (cargaAgregada(ctx) === null || mes === null) return "años";
  return `años, ${rangoAnio(mes)}`;
}

/** Rótulo de eje y de campo: "Período de retorno T (años, de julio a junio)". */
export function rotuloEjePeriodoRetorno(ctx?: ContextoSerie): string {
  return `Período de retorno T (${unidadPeriodoRetorno(ctx)})`;
}

export function rotuloValorDiseno(ctx?: ContextoSerie): string {
  const carga = cargaAgregada(ctx);
  return carga === null ? "Valor de diseño" : `Valor de diseño (${MAXIMO[carga]} del año)`;
}

export function notaPeriodoRetorno(ctx?: ContextoSerie): string {
  const promedio =
    "el valor de diseño de T años es el que se espera igualar o superar, en promedio, " +
    "una vez cada T años (probabilidad 1/T de ser superado en un año cualquiera).";
  const carga = cargaAgregada(ctx);
  if (carga === null) {
    return `La distribución se ajustó a la serie de máximos anuales, por eso T se mide en años: ${promedio}`;
  }
  const mes = mesValido(ctx);
  const anio = mes === null ? "de cada año" : `de cada año (${rangoAnio(mes)})`;
  const unidadCarga = carga === "mensual" ? "meses" : "días";
  return (
    `Se cargó ${CARGA[carga]}. METIS no ajusta la distribución a esos valores: ` +
    `toma ${MAXIMO_CON_ARTICULO[carga]} ${anio} y ajusta la serie de esos máximos anuales. ` +
    `Por eso T se mide en años y no en ${unidadCarga}: ${promedio}`
  );
}
