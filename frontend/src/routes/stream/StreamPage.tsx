import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAnalysisStream } from "../../api/sse";
import type { AnalysisStreamForm, TestResultDetail } from "../../api/types";
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
  const { start, state, resolveOutlier } = useAnalysisStream();
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
                            <td className="num">{t.estadistico ?? "—"}</td>
                            <td className="num">{t.valor_critico ?? "—"}</td>
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
                state: { result: state.result, analysisId: state.analysisId },
              })
            }
          >
            Ver resultados ▸
          </button>
        </div>
      )}

      {state.fase === "waiting_outlier" && state.outlier && (
        <div
          className="modal-backdrop"
          role="dialog"
          aria-modal="true"
          aria-labelledby="outlier-title"
        >
          <div className="card">
            <h2 id="outlier-title" className="h">
              Dato atípico detectado
            </h2>
            <p className="sub">
              Chow detectó un valor atípico:{" "}
              <span className="num">{state.outlier.valor_atipico}</span>. ¿Qué
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
