// Diccionario código→texto legible en español. El backend no manda mensaje
// legible en varios eventos (ver docs/frontend/frontend-implementation-plan.md §7).
export const ERROR_TEXT: Record<string, string> = {
  // Auth
  AUTH_EMAIL_ALREADY_REGISTERED: "Ese email ya está registrado.",
  AUTH_VERIFICATION_EMAIL_FAILED:
    "No pudimos enviar el mail de verificación. Probá de nuevo en unos minutos.",
  AUTH_INVALID_TOKEN: "El link de verificación es inválido o expiró.",
  AUTH_USER_NOT_FOUND: "No encontramos el usuario.",
  AUTH_INVALID_CREDENTIALS: "Email o contraseña incorrectos.",
  AUTH_EMAIL_NOT_VERIFIED: "Verificá tu email antes de iniciar sesión.",
  SESSION_NOT_ESTABLISHED:
    "El login fue aceptado pero no se pudo abrir la sesión. Revisá la conexión con el backend.",
  VALIDATION_ERROR: "Revisá los datos ingresados.",

  // Contrato — bloqueantes
  CONTRACT_SERIES_TOO_SHORT: "La serie tiene menos de 10 datos. No se puede analizar.",
  CONTRACT_NO_TEMPORAL_RESOLUTION:
    "No se pudo determinar la resolución temporal de la serie.",

  // Contrato — parámetros de request
  CONTRACT_CRAMER_PARTICION_UNSUPPORTED:
    "La partición personalizada de Cramer todavía no está disponible. Usá la partición por defecto.",
  CONTRACT_ETAPAS_INVALID: "El alcance del análisis pedido no es válido.",
  CONTRACT_MES_INICIO_INVALID: "El mes de inicio del año debe estar entre 1 y 12.",

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
  CONTRACT_PARTIAL_YEARS_TRIMMED:
    "Se recortaron años parciales en los extremos del registro al agregar a máximos anuales.",
  CONTRACT_INCOMPLETE_YEARS_DISCARDED:
    "Se descartó al menos un año incompleto dentro del registro al agregar a máximos anuales.",

  // Etapa 1 — pruebas
  TEST_CRITICAL_INDEPENDENCE:
    "Anderson rechazó independencia — resultado crítico.",
  TEST_CRITICAL_HOMOGENEITY:
    "Cramer rechazó homogeneidad — resultado crítico.",
  TEST_WARNING_TREND:
    "Se detectó una posible tendencia (Mann-Kendall o Kolmogorov-Smirnov).",
  TEST_WARNING_HOMOGENEITY: "Helmert o t de Student rechazaron homogeneidad.",
  TEST_WARNING_SMALL_SAMPLE:
    "Muestra chica — Wald-Wolfowitz (n ≤ 40) o Mann-Kendall (10 ≤ n ≤ 30) se ejecutan con advertencia.",
  TEST_WARNING_OUTLIER_DETECTED:
    "Chow detectó un dato atípico — se requiere tu decisión.",
  TEST_OUTLIER_REJECTED_BY_USER: "Rechazaste el dato atípico detectado por Chow.",
  TEST_OUTLIER_ACCEPTED_BY_USER:
    "Aceptaste el dato atípico como parte de la población.",
  TEST_NOT_EXECUTED_ZEROS:
    "Chow no se ejecutó: hay ceros en la serie de caudal/precipitación.",
  TEST_NOT_EXECUTED_CONDITION:
    "La prueba no se ejecutó: no se cumple una condición previa.",
  TEST_NOT_EXECUTED_MIN_SAMPLES:
    "Mann-Kendall no se ejecutó: la serie tiene menos de 10 datos.",

  // Etapa 2
  DIST_SELECTION_INVALID:
    "La selección de distribución y método no es válida. Revisá los períodos de retorno.",
  DIST_NOT_APPLICABLE:
    "Esta combinación de distribución y método no aplica a los datos de la serie.",
  DIST_NOT_CONVERGED:
    "El método iterativo no encontró una solución estable para esta distribución.",
  DIST_HIGH_EEA:
    "El error estándar de ajuste supera el 5% de la media — el ajuste es de baja calidad.",
  DIST_DISABLED_ZEROS:
    "Esta distribución está deshabilitada porque la serie tiene ceros.",
  DIST_ZEROS_TOLERATED:
    "La serie tiene ceros y este ajuste se calculó igual — el comportamiento ante ceros está pendiente de confirmación con Facundo.",
  DIST_METHOD_NOT_FITTED:
    "Esa combinación de distribución y método no tiene parámetros ajustados en este análisis.",

  // Stream
  PARSE_ERROR:
    "No se pudo leer el archivo. Revisá el formato y las columnas seleccionadas.",
  PARSE_FILE_TOO_LARGE: "El archivo supera el límite de 10 MB permitido.",
  SESSION_TIMEOUT:
    "Se agotó el tiempo de espera para decidir sobre el dato atípico.",
  SESSION_NOT_FOUND: "La sesión de análisis no existe o ya expiró.",
  ANALYSIS_NOT_FOUND:
    "El análisis no existe, no te pertenece, o no tiene Etapa 2 ejecutada.",
  STREAM_CONNECTION_ERROR:
    "Se perdió la conexión con el servidor durante el análisis.",
  STREAM_CLOSED_EARLY:
    "El servidor cerró la conexión antes de terminar el análisis.",
};

const FALLBACK_TEXT = "Ocurrió un error inesperado. Probá de nuevo.";

export function errorText(codigo: string): string {
  return ERROR_TEXT[codigo] ?? FALLBACK_TEXT;
}
