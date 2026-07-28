// Diccionario código→texto legible en español. El backend no manda mensaje
// legible en varios eventos (ver docs/frontend-implementation-plan.md §7).
export const ERROR_TEXT: Record<string, string> = {
  // Auth
  AUTH_EMAIL_ALREADY_REGISTERED: "Ese email ya está registrado.",
  AUTH_VERIFICATION_EMAIL_FAILED:
    "No pudimos enviar el mail de verificación. Probá de nuevo en unos minutos.",
  AUTH_INVALID_TOKEN: "El link de verificación es inválido o expiró.",
  AUTH_USER_NOT_FOUND: "No encontramos el usuario.",
  AUTH_INVALID_CREDENTIALS: "Email o contraseña incorrectos.",
  AUTH_EMAIL_NOT_VERIFIED: "Verificá tu email antes de iniciar sesión.",
  VALIDATION_ERROR: "Revisá los datos ingresados.",

  // Contrato — bloqueantes
  CONTRACT_SERIES_TOO_SHORT: "La serie tiene menos de 10 datos. No se puede analizar.",
  CONTRACT_NO_TEMPORAL_RESOLUTION:
    "No se pudo determinar la resolución temporal de la serie.",

  // Contrato — warnings
  CONTRACT_LENGTH_WARNING:
    "Serie con menos de 30 datos — los resultados no son certificables.",
  CONTRACT_NEGATIVE_VALUES:
    "Hay valores negativos en una serie de caudal/precipitación.",
  CONTRACT_MISSING_VALUES: "Hay valores faltantes o celdas vacías.",
  CONTRACT_DUPLICATE_TIMESTAMPS: "Se detectaron duplicados en el eje temporal.",
  CONTRACT_WRONG_ORDER: "La serie no está en orden cronológico.",
  CONTRACT_IRREGULAR_SPACING: "El espaciado temporal es irregular.",
  CONTRACT_NON_NUMERIC_VALUES: "Hay valores no numéricos mezclados en la serie.",

  // Etapa 1 — pruebas
  TEST_WARNING_TREND:
    "Se detectó una posible tendencia (Mann-Kendall o Kolmogorov-Smirnov).",
  TEST_WARNING_HOMOGENEITY: "Helmert o t de Student rechazaron homogeneidad.",
  TEST_WARNING_SMALL_SAMPLE:
    "Muestra chica (n ≤ 40) — Wald-Wolfowitz se ejecuta con advertencia.",
  TEST_WARNING_OUTLIER_DETECTED:
    "Chow detectó un dato atípico — se requiere tu decisión.",
  TEST_NOT_EXECUTED_ZEROS:
    "Chow no se ejecutó: hay ceros en la serie de caudal/precipitación.",
  TEST_NOT_EXECUTED_CONDITION:
    "La prueba no se ejecutó: no se cumple una condición previa.",

  // Stream
  PARSE_ERROR:
    "No se pudo leer el archivo. Revisá el formato y las columnas seleccionadas.",
  SESSION_TIMEOUT:
    "Se agotó el tiempo de espera para decidir sobre el dato atípico.",
  STREAM_CONNECTION_ERROR:
    "Se perdió la conexión con el servidor durante el análisis.",
};

const FALLBACK_TEXT = "Ocurrió un error inesperado. Probá de nuevo.";

export function errorText(codigo: string): string {
  return ERROR_TEXT[codigo] ?? FALLBACK_TEXT;
}
