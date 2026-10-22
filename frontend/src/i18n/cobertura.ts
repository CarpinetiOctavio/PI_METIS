import type { Etapa1Datos } from "../api/types";

// DECISIÓN 081 — cobertura mínima de los años interiores al agregar una carga
// mensual o diaria, en porcentaje entero. Facundo (22/10/2026): "lo dejaría a
// criterio del operador". 100 % por defecto (el criterio estricto de antes); por
// debajo del 50 % el máximo de ese año deja de ser un máximo anual con sentido.
// Los años de los extremos del registro siempre exigen 100 %.
export const COBERTURA_DEFECTO = 100;
export const COBERTURA_PISO = 50;

/** Valida el texto del campo: entero de 50 a 100. */
export function parseCobertura(texto: string): { value: number } | { error: string } {
  const valor = Number(texto.trim());
  if (texto.trim() === "" || !Number.isInteger(valor) || valor < COBERTURA_PISO || valor > 100) {
    return {
      error: `La cobertura mínima de los años interiores tiene que ser un porcentaje entero entre ${COBERTURA_PISO} y 100.`,
    };
  }
  return { value: valor };
}

/**
 * Rótulo de la cobertura con que se agregó la serie, o null si no hubo
 * agregación (carga anual). Un análisis anterior a la DECISIÓN 081 no la trae:
 * se agregó con 100 % sin registrarlo.
 */
export function textoCoberturaAnalisis(datos: Etapa1Datos | null | undefined): string | null {
  if (datos?.resolucion_original !== "mensual" && datos?.resolucion_original !== "diaria") {
    return null;
  }
  const cobertura = datos.cobertura_minima_interior;
  if (typeof cobertura !== "number") {
    return `${COBERTURA_DEFECTO} % (el único criterio disponible cuando se corrió el análisis)`;
  }
  return `${cobertura} %`;
}
