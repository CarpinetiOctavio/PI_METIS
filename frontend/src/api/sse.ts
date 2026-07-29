import { fetchEventSource } from "@microsoft/fetch-event-source";
import { useCallback, useRef, useState } from "react";
import { postOutlierDecision } from "./analysis";
import { errorText } from "../i18n/errors.es";
import type {
  AnalysisStreamForm,
  DescriptiveStats,
  Etapa1Result,
  SseEvent,
  TestResultDetail,
  WarningItem,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export type StreamFase =
  | "idle"
  | "streaming"
  | "waiting_outlier"
  | "done"
  | "error";

export interface StreamState {
  fase: StreamFase;
  contractWarnings: WarningItem[];
  descriptive: DescriptiveStats | null;
  tests: Record<string, TestResultDetail>;
  progress: { completado: number; total: number };
  outlier: { session_id: string; valor_atipico: number } | null;
  result: Etapa1Result | null;
  analysisId: string | null;
  error: { codigo: string; mensaje: string } | null;
}

// _iteracion es contable interno del hook (detecta la re-ejecución tras
// rechazar un atípico) — no se expone en StreamState.
interface InternalState extends StreamState {
  _iteracion: number;
}

const INITIAL_STATE: InternalState = {
  fase: "idle",
  contractWarnings: [],
  descriptive: null,
  tests: {},
  progress: { completado: 0, total: 0 },
  outlier: null,
  result: null,
  analysisId: null,
  error: null,
  _iteracion: 1,
};

export interface UseAnalysisStreamResult {
  start: (form: AnalysisStreamForm) => void;
  state: StreamState;
  resolveOutlier: (decision: "rechazar" | "aceptar") => Promise<void>;
  abort: () => void;
}

function buildFormData(form: AnalysisStreamForm): FormData {
  const body = new FormData();
  body.append("archivo", form.archivo);
  body.append("columna_x", form.columna_x);
  body.append("columna_y", form.columna_y);
  body.append("tipo_variable", form.tipo_variable);
  body.append("modo", form.modo);
  body.append("cramer_particion", form.cramer_particion ?? "default");
  return body;
}

/**
 * Corre un análisis de Etapa 1 y expone su progreso como estado React.
 * SSE-sobre-fetch (no EventSource nativo — el stream es un POST multipart,
 * ver docs/decisiones/decision040.md — DECISIÓN 040).
 */
export function useAnalysisStream(): UseAnalysisStreamResult {
  const [internal, setInternal] = useState<InternalState>(INITIAL_STATE);
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleEvent = useCallback((event: SseEvent) => {
    setInternal((prev) => {
      // Reset por nueva iteración — ver frontend-integration.md §4: tras
      // rechazar un atípico, el server re-emite contract_warning/
      // descriptive_stats/progress/test_result con iteracion:2. `tests` no
      // necesita reset explícito (se sobrescribe por clave `prueba`), pero
      // contractWarnings/progress sí, para no arrastrar la corrida anterior.
      const base =
        "iteracion" in event && event.iteracion > prev._iteracion
          ? {
              ...prev,
              _iteracion: event.iteracion,
              contractWarnings: [],
              progress: { completado: 0, total: 0 },
            }
          : prev;

      switch (event.type) {
        case "contract_error":
          return {
            ...base,
            fase: "error",
            error: { codigo: event.codigo, mensaje: errorText(event.codigo) },
          };
        case "contract_warning": {
          if (base.contractWarnings.some((w) => w.codigo === event.codigo)) {
            return base;
          }
          return {
            ...base,
            contractWarnings: [
              ...base.contractWarnings,
              {
                codigo: event.codigo,
                nivel: event.nivel,
                descripcion: errorText(event.codigo),
              },
            ],
          };
        }
        case "descriptive_stats":
          // event trae de más `type`/`iteracion` — asignación estructural,
          // no un literal, así que TS no exige despojarlos.
          return { ...base, descriptive: event };
        case "progress":
          return {
            ...base,
            progress: { completado: event.completado, total: event.total },
          };
        case "test_result":
          return { ...base, tests: { ...base.tests, [event.prueba]: event } };
        case "outlier_detected":
          return {
            ...base,
            fase: "waiting_outlier",
            outlier: {
              session_id: event.session_id,
              valor_atipico: event.valor_atipico,
            },
          };
        case "result_etapa1":
          return { ...base, result: event.result };
        case "complete":
          // `complete` SIEMPRE llega después de `contract_error` también
          // (docs/frontend-integration.md §4: "Después de este evento el
          // backend manda complete con analysis_id: null y cierra") — si ya
          // estamos en fase="error" no hay que pisarla con "done".
          return base.fase === "error"
            ? base
            : { ...base, fase: "done", analysisId: event.analysis_id };
        case "error":
          return {
            ...base,
            fase: "error",
            error: { codigo: event.codigo, mensaje: event.mensaje },
          };
        default:
          return base;
      }
    });
  }, []);

  const start = useCallback(
    (form: AnalysisStreamForm) => {
      abortControllerRef.current?.abort();
      const controller = new AbortController();
      abortControllerRef.current = controller;
      setInternal({ ...INITIAL_STATE, fase: "streaming" });

      fetchEventSource(`${API_BASE}/api/v1/analysis/stream`, {
        method: "POST",
        body: buildFormData(form),
        credentials: "include",
        signal: controller.signal,
        // El server pausa hasta 300s esperando la decisión ante un atípico —
        // no queremos que la librería cierre/reabra la conexión si la pestaña
        // pierde foco mientras el usuario decide.
        openWhenHidden: true,
        async onopen(response) {
          if (!response.ok) {
            throw new Error(`El stream abrió con status ${response.status}`);
          }
        },
        onmessage(ev) {
          if (!ev.data) return;
          try {
            const payload = JSON.parse(ev.data) as Record<string, unknown>;
            // El discriminante `type` no viaja en el JSON — lo da la línea
            // `event:` del frame SSE (ver architecture.md, formato `_sse()`).
            //
            // result_etapa1 es un caso especial confirmado contra el backend
            // real (no solo la doc): el frame trae el Etapa1Result crudo
            // como payload — NO como `{result: {...}}` — hay que envolverlo
            // acá. Bug real encontrado recién al probar contra Docker real;
            // el mock sintético de sse.test.ts asumía (incorrectamente) el
            // shape ya envuelto, por eso no lo agarró antes.
            const event: SseEvent =
              ev.event === "result_etapa1"
                ? { type: "result_etapa1", result: payload as unknown as Etapa1Result }
                : ({ type: ev.event, ...payload } as SseEvent);
            handleEvent(event);
          } catch {
            setInternal((prev) => ({
              ...prev,
              fase: "error",
              error: {
                codigo: "PARSE_ERROR",
                mensaje: errorText("PARSE_ERROR"),
              },
            }));
          }
        },
        onclose() {
          // Cierre normal del server tras `complete` o `contract_error` — no
          // se reintenta nada acá, la fase ya quedó resuelta por handleEvent.
        },
        onerror(err) {
          setInternal((prev) => ({
            ...prev,
            fase: "error",
            error: { codigo: "STREAM_CONNECTION_ERROR", mensaje: String(err) },
          }));
          // Relanzar evita el retry automático de la librería — este stream
          // no es idempotente para reintentar solo (re-correría el pipeline).
          throw err;
        },
      }).catch(() => {
        // onerror ya dejó el estado en fase="error" — acá solo evitamos que
        // la promesa rechazada quede sin manejar.
      });
    },
    [handleEvent],
  );

  const resolveOutlier = useCallback(
    async (decision: "rechazar" | "aceptar") => {
      const { outlier } = internal;
      if (!outlier) return;
      await postOutlierDecision({
        session_id: outlier.session_id,
        decision,
        dato_atipico: outlier.valor_atipico,
      });
      setInternal((prev) => ({ ...prev, fase: "streaming", outlier: null }));
    },
    [internal],
  );

  const abort = useCallback(() => {
    abortControllerRef.current?.abort();
  }, []);

  const state: StreamState = {
    fase: internal.fase,
    contractWarnings: internal.contractWarnings,
    descriptive: internal.descriptive,
    tests: internal.tests,
    progress: internal.progress,
    outlier: internal.outlier,
    result: internal.result,
    analysisId: internal.analysisId,
    error: internal.error,
  };
  return { start, state, resolveOutlier, abort };
}
