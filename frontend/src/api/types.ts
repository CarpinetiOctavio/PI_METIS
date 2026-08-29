// Interfaces 1:1 con el contrato real documentado en docs/frontend/frontend-integration.md
// (no con metis/schemas/analysis.py — desconectado de los endpoints reales, ver
// ese documento §5/§6). Alcance actual: solo Auth (Fase 1 del frontend).

export interface RegisterRequest {
  email: string;
  password: string;
  nombre?: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface VerifyRequest {
  token: string;
}

export interface UserMe {
  id: string;
  email: string;
  nombre: string | null;
  email_verified: boolean;
}

export interface RegisterResponse {
  ok: true;
  mensaje: string;
}

export interface OkResponse {
  ok: true;
}

// --- Análisis — shapes reales, ver docs/frontend/frontend-integration.md §3-4.
// NO usar metis/schemas/analysis.py como referencia: desconectado de los
// endpoints reales (ver ese documento §5/§6).

export type TipoVariable = "caudal_precipitacion" | "otro";
export type Modo = "paso_a_paso" | "experto";

// Bloque H1 (plan post-avance, DECISIÓN 036) — "default" o un objeto con
// los dos porcentajes. api/sse.ts::buildFormData() manda el objeto como
// JSON string en el mismo campo Form — el contrato multipart no ganó un
// campo nuevo, solo lo que viaja adentro del que ya existía.
export type CramerParticion = "default" | { n1_pct: number; n2_pct: number };

export interface AnalysisStreamForm {
  archivo: File;
  columna_x: string;
  columna_y: string;
  tipo_variable: TipoVariable;
  modo: Modo;
  cramer_particion?: CramerParticion;
  // DECISIÓN 054 — solo "1" y "1,2" son valores válidos para el backend.
  // Sin selector de alcance todavía en ConfigPage (eso es Bloque B4 del plan
  // de Etapa 2) — default "1" mantiene el comportamiento actual sin cambios.
  etapas?: "1" | "1,2";
  // DECISIÓN 057 — mes de inicio del año hidrológico, [1..12]. Sin selector
  // todavía en ConfigPage (eso es el Bloque F5 del plan de Etapa 2) —
  // default 7 (julio) mantiene el comportamiento actual sin cambios; solo
  // tiene efecto cuando la serie subida es de resolución mensual o diaria.
  mes_inicio_anio?: number;
  // DECISIÓN 065 (PR 2.5 / R0.2) — qué contiene la columna de una serie
  // DIARIA: "pico" (picos o máximos diarios) o "media" (medias diarias).
  // Solo tiene efecto con carga diaria: cambia el texto del warning
  // CONTRACT_DAILY_SERIES_AGGREGATED, no los números. Default "pico".
  variable_diaria?: "pico" | "media";
}

export interface OutlierDecisionRequest {
  session_id: string;
  decision: "rechazar" | "aceptar";
  dato_atipico: number;
}

export interface OutlierDecisionResponse {
  ok: boolean;
  pipeline_continua: boolean;
}

// DECISIÓN 047 — POST /analysis/preview-columns
export interface ColumnaPreview {
  nombre: string;
  indice: number;
  muestra: string[];
}

export interface PreviewColumnsResponse {
  columnas: ColumnaPreview[];
  filas: number;
}

export type Veredicto = "aprobada" | "rechazada" | "no_ejecutada";
export type WarningNivel = "critico" | "normal";

export interface WarningItem {
  codigo: string;
  nivel: WarningNivel;
  descripcion: string;
}

// Bloque D del plan post-avance (DECISIÓN 064) — términos intermedios que
// la prueba ya calculó, para reconstruir la fórmula sustituida en modo
// paso a paso. `terminos` es heterogéneo por prueba (Anderson expone
// numerador/denominador, Cramer expone los dos bloques 60%/30%…) — el
// backend no fuerza una forma común, así que acá tampoco. `i18n/explicaciones.ts`
// sabe qué claves esperar según `TestResultDetail.prueba`.
export interface Explicacion {
  ecuacion: string;
  terminos: Record<string, number | null>;
}

export interface TestResultDetail {
  prueba: string;
  estadistico: number | null;
  valor_critico: number | null;
  veredicto: Veredicto | null;
  warning_codigo: string | null;
  warning_nivel: WarningNivel | null;
  n1: number | null;
  n2: number | null;
  valor_atipico: number | null;
  // PR 3 del plan de cierre de pendientes no-test (DECISIÓN 058) — ya
  // existía en el backend (TestResult), nunca se serializaba.
  indice_atipico: number | null;
  explicacion: Explicacion | null;
}

// Timestamp normalizado — PR 3 (DECISIÓN 058 §4.4): siempre ISO-8601 str +
// `anio` propio, sin importar si el dato de origen era str/int/pd.Timestamp
// (sin agregación) o list[int] de año-etiqueta (con agregación).
export interface TimestampNormalizado {
  iso: string;
  anio: number;
}

// Segunda agregación (mes_inicio=1), con sus PROPIOS timestamps — PR 4,
// corrección sobre DECISIÓN 058: puede tener más o menos puntos que
// serie_efectiva (otro mes_inicio, otro criterio de qué período queda
// completo), nunca se puede asumir el mismo eje X.
export interface SerieCalendario {
  serie: number[];
  timestamps: TimestampNormalizado[];
}

// Bloque "datos" de result_etapa1 — PR 3 del plan de cierre de pendientes
// no-test (DECISIÓN 058). Ver .claude/rules/core/statistical-pipeline.md
// para el detalle completo de cada campo.
export interface Etapa1Datos {
  resolucion_original: "anual" | "mensual" | "diaria" | null;
  // R3.3 opción 2 (docs/plan-resolucion-diaria.md) — a qué resolución está
  // `serie_original` en ESTE payload, distinto de `resolucion_original` (la
  // del archivo subido): con carga diaria el backend serializa la agregación
  // MENSUAL (~480 ítems), no la serie diaria cruda (~14.600). "anual" (o
  // null, sin timestamps) cuando serie_original es null.
  resolucion_serie_original: "anual" | "mensual" | "diaria" | null;
  serie_efectiva: number[];
  timestamps_efectivos: TimestampNormalizado[] | null;
  // Presentes con carga mensual o diaria (para el boxplot y la serie
  // temporal). Con carga anual son idénticos a los _efectiva y el backend
  // no los duplica (null). Con carga diaria son la agregación a máximos
  // mensuales — resolucion_serie_original === "mensual", aunque el archivo
  // fuera diario.
  serie_original: number[] | null;
  timestamps_originales: TimestampNormalizado[] | null;
  // Ya mapeado a posición en serie_efectiva — null si no hay atípico (o si
  // el usuario ya lo rechazó en una iteración anterior del stream).
  indice_atipico: number | null;
  // null si no hubo agregación real o si mes_inicio_anio ya era 1
  // (DECISIÓN 058 §3, solo para presentación).
  serie_calendario: SerieCalendario | null;
}

export interface DescriptiveStats {
  n: number;
  media: number;
  mediana: number;
  desvio_estandar: number;
  coef_variacion: number;
  coef_asimetria: number;
  minimo: number;
  maximo: number;
}

export interface Etapa1Result {
  contract: {
    bloqueante: boolean;
    codigo_error: string | null;
    warnings: WarningItem[];
  };
  descriptive: DescriptiveStats | null;
  independencia: TestResultDetail[];
  homogeneidad: TestResultDetail[];
  tendencia: TestResultDetail[];
  atipicos: TestResultDetail[];
  nivel_independencia: "independiente" | "dependiente" | null;
  nivel_homogeneidad:
    | "homogeneidad_ok"
    | "homogeneidad_warning"
    | "homogeneidad_critica"
    | null;
  // "rechazado" nunca llega en este evento — ver frontend-integration.md §4,
  // nota sobre result_etapa1 (el stream corta antes en contract_error).
  nivel_confianza: "validado" | "con_warnings" | "rechazado";
  warnings: WarningItem[];
  // Opcional — el historial persistido antes de la migración 005 no lo
  // trae (sin backfill, DECISIÓN 058 §4). Sin este campo, la sección de
  // gráficos de Etapa1ResultView no se renderiza.
  datos?: Etapa1Datos;
}

// --- Eventos SSE — union discriminada por `type`. Todos llevan `iteracion`
// salvo outlier_detected/result_etapa1/complete/error (ver frontend-integration.md §4).

export interface SseContractErrorEvent {
  type: "contract_error";
  codigo: string;
  iteracion: number;
}

export interface SseContractWarningEvent {
  type: "contract_warning";
  codigo: string;
  nivel: "normal";
  iteracion: number;
}

export interface SseDescriptiveStatsEvent extends DescriptiveStats {
  type: "descriptive_stats";
  iteracion: number;
}

export interface SseProgressEvent {
  type: "progress";
  paso: string;
  etapa: 1 | 2;
  completado: number;
  total: number;
  // Los eventos de progreso de Etapa 1 llevan iteracion (re-ejecución tras
  // Chow); el único progress de Etapa 2 (DECISIÓN 052) no re-ejecuta nada,
  // así que no lo lleva.
  iteracion?: number;
}

export interface SseTestResultEvent extends TestResultDetail {
  type: "test_result";
  iteracion: number;
}

export interface SseOutlierDetectedEvent {
  type: "outlier_detected";
  session_id: string;
  valor_atipico: number;
}

export interface SseResultEtapa1Event {
  type: "result_etapa1";
  result: Etapa1Result;
}

export interface SseCompleteEvent {
  type: "complete";
  analysis_id: string | null;
}

export interface SseErrorEvent {
  type: "error";
  codigo: "PARSE_ERROR" | "SESSION_TIMEOUT";
  mensaje: string;
}

// DECISIÓN 052 — pausa de Etapa 2, misma forma que outlier_detected/
// result_etapa1: result_etapa2_ranking trae la grilla completa serializada
// por _serializar_etapa2() (13 distribuciones, sin aplanar a top-3) y pausa
// el stream hasta POST /analysis/distribution-decision.
export interface SseResultEtapa2RankingEvent {
  type: "result_etapa2_ranking";
  session_id: string;
  ranking: DistribucionResult[];
  warnings: WarningItem[];
  // Bloque C — insumo del gráfico de ajuste (puntos empíricos vs. curva).
  // Independiente de la distribución que se elija después.
  puntos_empiricos: PuntoEmpirico[];
}

export interface SseResultEtapa2EventosEvent {
  type: "result_etapa2_eventos";
  distribucion: string;
  metodo: string;
  eventos_diseno: EventoDiseno[];
  // Bloque C — muestreo denso (60 puntos, escala log) de la curva de la
  // distribución elegida, distinto de eventos_diseno (los T puntuales que
  // pidió el usuario). Insumo del gráfico de ajuste.
  curva_ajuste: EventoDiseno[];
}

export type SseEvent =
  | SseContractErrorEvent
  | SseContractWarningEvent
  | SseDescriptiveStatsEvent
  | SseProgressEvent
  | SseTestResultEvent
  | SseOutlierDetectedEvent
  | SseResultEtapa1Event
  | SseResultEtapa2RankingEvent
  | SseResultEtapa2EventosEvent
  | SseCompleteEvent
  | SseErrorEvent;

// --- Historial (CU-01) — ver frontend-integration.md §3. Array plano, sin
// envoltura ni paginación de parte del backend (paginación client-side).

// archivado_at (DECISIÓN 048) — null si el análisis no está archivado.
export interface HistoryItem {
  id: string;
  tipo_variable: string;
  modo: string | null;
  etapas: string[] | null;
  created_at: string;
  archivado_at: string | null;
  // F7a/F7b (plan de fixes pre-reunión) — null para cualquier análisis
  // persistido antes de este fix (sin backfill, mismo criterio que
  // timestamps/DECISIÓN 058 §4). El frontend degrada a tipo_variable
  // cuando nombre_archivo es null.
  nombre_archivo: string | null;
  serie_preview: number[];
}

// PR 3/5 del plan de cierre de pendientes no-test (DECISIÓN 058) —
// mes_inicio_anio ya se persistía desde DECISIÓN 057, esto solo tipa la
// forma real de analyses.configuracion tal como GET /history/{id} la
// devuelve.
export interface AnalysisConfiguracion {
  cramer_particion: string;
  mes_inicio_anio: number;
  // DECISIÓN 065 (PR 2.5) — presente en análisis persistidos desde esa
  // fecha; opcional para no romper la lectura de análisis anteriores.
  variable_diaria?: "pico" | "media";
}

export interface AnalysisDetail {
  id: string;
  tipo_variable: string;
  modo: string | null;
  etapas: string[] | null;
  created_at: string;
  etapa1: Etapa1Result | null;
  etapa2: Etapa2Result | null;
  // Entrada tal como se subió y configuró (analyses, DECISIÓN 058 §1) —
  // no el resultado, que ya viaja dentro de etapa1.datos. `timestamps` es
  // `null` para cualquier análisis persistido antes de la migración 005
  // (sin backfill, DECISIÓN 058 §4) — es la señal que usa HistoryDetailPage
  // para el estado vacío explícito.
  serie: number[] | null;
  timestamps: TimestampNormalizado[] | null;
  configuracion: AnalysisConfiguracion | null;
}

// --- Etapa 2 — shapes reales, cableada de punta a punta (Bloque A del plan
// de implementación de Etapa 2, DECISIÓN 052/055). Espejo 1:1 de
// _serializar_etapa2() (analysis_service.py) — grilla completa, sin aplanar
// a un top-3: los métodos que no convergen o no aplican son información
// docente, no un error a esconder (constraints.md, "METIS no sugiere
// distribución ganadora").

export type MetodoStatus = "ok" | "no_converge" | "no_aplicable" | "disabled_zeros";

export interface MetodoResultDetail {
  metodo: string;
  parametros: Record<string, number> | null;
  eea: number | null;
  status: MetodoStatus;
}

export interface DistribucionResult {
  distribucion: string;
  n_parametros: number;
  metodos: MetodoResultDetail[];
  mejor_eea: number | null;
  mejor_metodo: string | null;
}

// Bloque C2a (plan post-avance) — la elección de distribución+método hecha
// durante el stream original y sus resultados, persistidos junto al
// ranking para que el historial la muestre sin recalcular nada. `null`
// cuando no se llegó a elegir ninguna (stream abandonado en la pausa) —
// mismo criterio sin backfill que `timestamps` (DECISIÓN 058 §4).
export interface SeleccionEtapa2 {
  distribucion: string;
  metodo: string;
  periodos_retorno: number[];
  eventos_diseno: EventoDiseno[];
  curva_ajuste: EventoDiseno[];
}

export interface Etapa2Result {
  ranking: DistribucionResult[];
  warnings: WarningItem[];
  puntos_empiricos: PuntoEmpirico[];
  seleccion: SeleccionEtapa2 | null;
}

// Posición de ploteo Weibull de un dato observado (empirical.py::
// probabilidades_weibull) — propiedad de la muestra, no del ajuste.
export interface PuntoEmpirico {
  valor: number;
  periodo_retorno: number;
  probabilidad: number;
}

export interface EventoDiseno {
  periodo_retorno: number;
  // null si cuantil() falló para este período puntual — core/etapa2/
  // design_events.py, un T inválido para una distribución no tumba el
  // resto de los eventos.
  valor: number | null;
}

export interface DistributionDecisionRequest {
  session_id: string;
  distribucion: string;
  metodo: string;
  periodos_retorno: number[];
}

// Bloque C2c (plan post-avance) — POST /analysis/{id}/design-events,
// recálculo stateless desde el historial (DECISIÓN 062). Misma forma que
// DistributionDecisionRequest sin session_id: no hay ningún stream de por
// medio, se pega directo sobre un análisis ya persistido.
export interface DesignEventsRecalcRequest {
  distribucion: string;
  metodo: string;
  periodos_retorno: number[];
}

export interface DesignEventsRecalcResponse {
  eventos_diseno: EventoDiseno[];
  curva_ajuste: EventoDiseno[];
}

export interface DistributionDecisionResponse {
  ok: boolean;
  pipeline_continua: boolean;
}
