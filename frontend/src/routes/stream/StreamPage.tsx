import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAnalysisStream } from "../../api/sse";
import type { AnalysisStreamForm, TestResultDetail } from "../../api/types";
import { formatNum } from "../../i18n/format";
import "./StreamPage.css";

interface Group {
  key: string;
  label: string;
  tests: string[];
}

const GROUPS: Group[] = [
  {
    key: "independencia",
    label: "Independencia",
    tests: ["anderson", "wald_wolfowitz"],
  },
  {
    key: "homogeneidad",
    label: "Homogeneidad",
    tests: ["helmert", "t_student", "cramer"],
  },
  {
    key: "tendencia",
    label: "Tendencia",
    tests: ["mann_kendall", "kolmogorov_smirnov"],
  },
  { key: "atipicos", label: "Atípicos (Chow)", tests: ["chow"] },
];

type GroupStatus = "pending" | "active" | "ok" | "warn" | "crit";

const STEP_CLASS: Record<GroupStatus, string> = {
  pending: "step",
  active: "step active",
  ok: "step done",
  warn: "step warn",
  crit: "step crit",
};

const PILL_LABEL: Record<Exclude<GroupStatus, "pending">, string> = {
  active: "calculando…",
  ok: "aprobada",
  warn: "warning",
  crit: "crítico",
};

// Decisión de dominio (D9, pasada de mejora — no una DECISIÓN NNN nueva:
// aclara una ambigüedad, no contradice ningún documento vigente).
//
// Esta función NO reproduce el veredicto final agregado de independencia u
// homogeneidad (`nivel_independencia`/`nivel_homogeneidad` de `Etapa1Result`,
// "Anderson manda"/"Cramer manda" — ver constraints.md). Ese veredicto solo
// existe una vez que llega el evento `result_etapa1` al final del stream, y
// se muestra en `Etapa1ResultView` — no acá.
//
// Mientras el stream está en curso, esta función solo agrega "hay algo para
// mirar en este grupo" (warn) vs. "todo limpio" (ok) vs. "crítico" (crit) a
// partir de las pruebas individuales ya recibidas. Verificado que esto SÍ es
// consistente con la jerarquía documentada para el límite crit/warn: en el
// código real (`core/etapa1/independence.py`, `core/etapa1/homogeneity.py`),
// `warning_nivel="critico"` únicamente lo produce la prueba dominante de
// cada grupo (Anderson en independencia, Cramer en homogeneidad) — Wald,
// Helmert y t de Student nunca producen "critico". Así que "crit" acá
// siempre coincide con que la prueba dominante rechazó, igual que la regla
// de negocio. Lo que esta función SÍ hace de forma deliberada es mostrar
// "warn" también cuando una prueba no dominante rechaza o trae una
// advertencia normal (ej. Wald con n≤40) — aunque el veredicto final sea
// INDEPENDIENTE, ese es un warning de nivel "normal" real y documentado
// (constraints.md, "Wald-Wolfowitz rechaza" y "n ≤ 40" están listados como
// NORMAL), no algo que deba ocultarse. "warn" acá significa "hay una nota",
// no "el veredicto final falló".
function summarizeGroup(
  tests: Record<string, TestResultDetail>,
  keys: string[],
): GroupStatus {
  const present = keys
    .map((key) => tests[key])
    .filter((t): t is TestResultDetail => Boolean(t));
  if (present.length === 0) return "pending";
  if (present.length < keys.length) return "active";
  if (present.some((t) => t.warning_nivel === "critico")) return "crit";
  if (present.some((t) => t.warning_nivel === "normal" || t.veredicto === "rechazada")) {
    return "warn";
  }
  return "ok";
}

function StatusPill({ status }: { status: GroupStatus }) {
  if (status === "pending") return null;
  const kind = status === "active" ? "wait" : status;
  return <span className={`pill ${kind}`}>{PILL_LABEL[status]}</span>;
}

export function StreamPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { start, state, resolveOutlier, abort } = useAnalysisStream();
  const startedRef = useRef(false);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [resolving, setResolving] = useState(false);

  const form = (location.state as { form?: AnalysisStreamForm } | null)?.form;

  useEffect(() => {
    if (!form) {
      navigate("/config", { replace: true });
      return;
    }
    if (startedRef.current) return;
    startedRef.current = true;
    start(form);
  }, [form, start, navigate]);

  useEffect(() => {
    // Si el usuario navega a mitad de stream, sin esto el fetch queda vivo
    // (setState sobre componente desmontado) y la sesión queda colgada hasta
    // el timeout de 300s en session_store del backend.
    return () => abort();
  }, [abort]);

  const modalOpen = state.fase === "waiting_outlier" && Boolean(state.outlier);
  const contentRef = useRef<HTMLDivElement>(null);
  const dialogRef = useRef<HTMLDivElement>(null);
  const previouslyFocusedRef = useRef<HTMLElement | null>(null);

  // `inert` no está en los tipos de esta versión de @types/react — se
  // setea imperativamente sobre el DOM real en vez de pasarlo como prop JSX.
  // Hooks van todos antes del `return null` de abajo — rules-of-hooks exige
  // el mismo orden de hooks en cada render, incluido el primero (sin form).
  useEffect(() => {
    if (contentRef.current) contentRef.current.inert = modalOpen;
  }, [modalOpen]);

  // M3 (cierre de Fase 6, pasada de mejora 3) — foco del modal de atípico.
  useEffect(() => {
    if (modalOpen) {
      // Auto-foco al abrir: al contenedor del diálogo (tabIndex={-1}), no a
      // ninguno de los dos botones — "Rechazar"/"Aceptar" son dos decisiones
      // reales, ninguna es un "cancelar" por defecto; poner el foco inicial
      // en cualquiera de las dos sesgaría al usuario hacia esa opción ante
      // un Enter apurado. El contenedor es neutral y de todas formas mete el
      // foco (y al lector de pantalla) adentro del diálogo.
      previouslyFocusedRef.current = document.activeElement as HTMLElement | null;
      dialogRef.current?.focus();
    } else if (previouslyFocusedRef.current) {
      // Restaurar el foco al elemento que lo tenía cuando el modal se cierra.
      previouslyFocusedRef.current.focus();
      previouslyFocusedRef.current = null;
    }
  }, [modalOpen]);

  function handleDialogKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key !== "Escape") return;
    event.preventDefault();
    // Decisión de producto, no de accesibilidad (M3.2): Escape NO cierra el
    // modal ni descarta la decisión pendiente. El backend está bloqueado
    // esperando (session_store, hasta 300s) y el pipeline no continúa sin
    // una respuesta real — "rechazar" y "aceptar" son las dos únicas
    // decisiones válidas, ninguna es un "cancelar" seguro para mapear un
    // Escape accidental. Además cada una queda en el registro de auditoría
    // (TEST_OUTLIER_REJECTED_BY_USER / TEST_OUTLIER_ACCEPTED_BY_USER) — un
    // Escape sin querer no puede convertirse silenciosamente en una de las
    // dos. Escape solo devuelve el foco al contenedor del diálogo; el modal
    // sigue abierto y el usuario tiene que elegir explícitamente un botón.
    dialogRef.current?.focus();
  }

  if (!form) return null;

  async function handleOutlierDecision(decision: "rechazar" | "aceptar") {
    setResolving(true);
    try {
      await resolveOutlier(decision);
    } finally {
      setResolving(false);
    }
  }

  function toggleGroup(key: string, expandable: boolean) {
    if (!expandable) return;
    setExpanded((current) => (current === key ? null : key));
  }

  const progressPct = state.progress.total
    ? Math.min(100, (state.progress.completado / state.progress.total) * 100)
    : 0;

  return (
    <div className="card">
      {/* D10 (pasada de mejora) — el resto de la página queda inert/aria-hidden
          mientras el modal de atípico está abierto, para que el foco y el
          lector de pantalla no puedan "escaparse" del diálogo. */}
      <div ref={contentRef} aria-hidden={modalOpen || undefined}>
        <h1 className="h">Análisis en vivo</h1>

        {state.fase === "error" && state.error && (
          <div className="banner crit" role="alert">
            <span className="ic">!</span> {state.error.mensaje}
          </div>
        )}

        {state.contractWarnings.map((warning) => (
          <div className="banner warn" key={warning.codigo}>
            <span className="ic">▲</span> {warning.descripcion}
          </div>
        ))}

        {state.fase !== "error" && (
          <>
            <div className="prog" style={{ marginBottom: 20 }}>
              <i style={{ width: `${progressPct}%` }} />
            </div>
            <div className="stack">
              {GROUPS.map((group) => {
                const status = summarizeGroup(state.tests, group.tests);
                const expandable = status !== "pending";
                const results = group.tests
                  .map((key) => state.tests[key])
                  .filter((t): t is TestResultDetail => Boolean(t));

                return (
                  <div key={group.key}>
                    <div
                      className={STEP_CLASS[status]}
                      role={expandable ? "button" : undefined}
                      tabIndex={expandable ? 0 : undefined}
                      onClick={() => toggleGroup(group.key, expandable)}
                      onKeyDown={(event) => {
                        if (expandable && (event.key === "Enter" || event.key === " ")) {
                          event.preventDefault();
                          toggleGroup(group.key, expandable);
                        }
                      }}
                    >
                      <div className="node">{status === "ok" ? "✓" : "▸"}</div>
                      <div style={{ flex: 1 }}>
                        <b>{group.label}</b> <StatusPill status={status} />
                      </div>
                    </div>
                    {expanded === group.key && results.length > 0 && (
                      <table className="t">
                        <thead>
                          <tr>
                            <th>Prueba</th>
                            <th>Estadístico</th>
                            <th>Crítico</th>
                            <th>Veredicto</th>
                          </tr>
                        </thead>
                        <tbody>
                          {results.map((t) => (
                            <tr key={t.prueba}>
                              <td>{t.prueba}</td>
                              <td className="num">{formatNum(t.estadistico)}</td>
                              <td className="num">{formatNum(t.valor_critico)}</td>
                              <td>{t.veredicto ?? "—"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                  </div>
                );
              })}
            </div>
          </>
        )}

        {state.fase === "done" && (
          <div className="banner ok" style={{ marginTop: 14 }}>
            <span className="ic">✓</span> Análisis completo.
            <button
              type="button"
              className="b b-pri"
              style={{ marginLeft: "auto" }}
              onClick={() =>
                navigate("/results", {
                  state: {
                    result: state.result,
                    analysisId: state.analysisId,
                    modo: form.modo,
                  },
                })
              }
            >
              Ver resultados ▸
            </button>
          </div>
        )}
      </div>

      {modalOpen && state.outlier && (
        <div className="modal-backdrop">
          <div
            ref={dialogRef}
            className="card"
            role="dialog"
            aria-modal="true"
            aria-labelledby="outlier-title"
            tabIndex={-1}
            onKeyDown={handleDialogKeyDown}
          >
            <h2 id="outlier-title" className="h">
              Dato atípico detectado
            </h2>
            <p className="sub">
              Chow detectó un valor atípico:{" "}
              <span className="num">{formatNum(state.outlier.valor_atipico)}</span>. ¿Qué
              hacemos con este dato?
            </p>
            <div className="row">
              <button
                type="button"
                className="b b-sec"
                disabled={resolving}
                onClick={() => handleOutlierDecision("rechazar")}
              >
                Rechazar
              </button>
              <button
                type="button"
                className="b b-pri"
                disabled={resolving}
                onClick={() => handleOutlierDecision("aceptar")}
              >
                Aceptar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
