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

export interface AnalysisStreamForm {
  archivo: File;
  columna_x: string;
  columna_y: string;
  tipo_variable: TipoVariable;
  modo: Modo;
  // "Personalizada" está roto en el wiring real del backend — solo "default"
  // funciona (ver frontend-integration.md §3, nota crítica de cramer_particion).
  cramer_particion?: "default";
  // DECISIÓN 054 — solo "1" y "1,2" son valores válidos para el backend.
  // Sin selector de alcance todavía en ConfigPage (eso es Bloque B4 del plan
  // de Etapa 2) — default "1" mantiene el comportamiento actual sin cambios.
  etapas?: "1" | "1,2";
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
  etapa: 1;
  completado: number;
  total: number;
  iteracion: number;
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

export type SseEvent =
  | SseContractErrorEvent
  | SseContractWarningEvent
  | SseDescriptiveStatsEvent
  | SseProgressEvent
  | SseTestResultEvent
  | SseOutlierDetectedEvent
  | SseResultEtapa1Event
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
}

export interface AnalysisDetail {
  id: string;
  tipo_variable: string;
  modo: string | null;
  etapas: string[] | null;
  created_at: string;
  etapa1: Etapa1Result | null;
  etapa2: null;
}

// --- Etapa 2 — MOCK, no implementado por el backend todavía (ver
// frontend-implementation-plan.md §6 y §10, D19). El ranking no tiene shape
// de contrato real (nunca se documentó un endpoint REST para él — solo
// aparece como evento SSE `result_etapa2_ranking` que el backend nunca
// emite); RankingItem es un shape de ejemplo para la pantalla mock, no una
// interfaz derivada de api-contracts.md. design-events, en cambio, SÍ tiene
// contrato real documentado (api-contracts.md) aunque no implementado.

export interface RankingItem {
  distribucion: string;
  metodo: string;
  eea: number;
  rank: number;
}

export interface DesignEventsRequest {
  session_id: string;
  distribucion: string;
  metodo: string;
  periodos_retorno: number[];
}

export interface DesignEvento {
  periodo_retorno: number;
  valor: number;
}

export interface DesignEventsResponse {
  distribucion: string;
  metodo: string;
  parametros: Record<string, number>;
  eventos_diseno: DesignEvento[];
  grafico_ajuste: string | null;
  analysis_id: string | null;
}
