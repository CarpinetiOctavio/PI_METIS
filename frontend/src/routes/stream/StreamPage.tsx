import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAnalysisStream } from "../../api/sse";
import type { AnalysisStreamForm, TestResultDetail } from "../../api/types";
import { CountUp } from "../../components/CountUp";
import { Magnet } from "../../components/Magnet";
import { SpecularHighlight } from "../../components/SpecularHighlight";
import { Etapa2RankingView } from "../results/Etapa2RankingView";
import { Etapa2EventosView } from "../results/Etapa2EventosView";
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

const PILL_LABEL: Record<GroupStatus, string> = {
  pending: "esperando resultados",
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
// mirar en este grupo" (warn) vs. "limpio" (ok) vs. "crítico" (crit) a
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

// F8 (informe-diagnostico-ui-rota.md): antes "pending" no mostraba ninguna
// pill — un paso sin resultados todavía y un botón roto se veían exactamente
// igual (nada). "esperando resultados" dice explícitamente que es un estado
// normal en curso, no una falla.
// A5 (plan pasada4 §3): el llamador pasa key={status} — key solo importa
// para cómo el PADRE reconcilia, así que ponerlo acá adentro no haría nada.
// Con esa key, React reemplaza el nodo entero en cada transición de estado
// en vez de mutar el existente, y la animación de entrada que .pill ya trae
// (components.css) se re-dispara como cross-fade en vez de salto seco. El
// texto sigue siendo correcto de inmediato en cada render — nada que
// testear con waitFor.
function StatusPill({ status }: Readonly<{ status: GroupStatus }>) {
  const kind = status === "active" || status === "pending" ? "wait" : status;
  return <span className={`pill ${kind}`}>{PILL_LABEL[status]}</span>;
}

export function StreamPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { start, state, resolveOutlier, resolveDistribution, abort } = useAnalysisStream();
  const [expanded, setExpanded] = useState<string | null>(null);
  const [resolving, setResolving] = useState(false);
  const [resolvingDistribucion, setResolvingDistribucion] = useState(false);

  const form = (location.state as { form?: AnalysisStreamForm } | null)?.form;
  // El form se congela en el primer render: location.state es estable dentro
  // de una misma entrada del historial, pero no queremos reintentar el
  // análisis si cambia la referencia. StreamPage lo consume una sola vez.
  const formRef = useRef(form);

  // F1 (docs/frontend/informe-diagnostico-ui-rota.md): un solo efecto, con
  // la limpieza en el MISMO efecto que arranca. En el doble montaje de
  // StrictMode se aborta el primer stream y la segunda pasada arranca uno
  // nuevo — eso es lo correcto. La versión anterior separaba "arrancar" de
  // "limpiar" en dos efectos con una guarda `startedRef`: la limpieza fantasma
  // de StrictMode abortaba el stream recién abierto, y la segunda pasada de
  // montaje salía por la guarda sin volver a arrancarlo — cero streams vivos.
  //
  // Costo aceptado y explícito: en desarrollo, StrictMode dispara dos veces
  // POST /analysis/stream; el primero se aborta a los pocos milisegundos y
  // el backend limpia esa sesión en el `finally` de stream_etapa1 — no queda
  // basura. En producción StrictMode no corre.
  useEffect(() => {
    const f = formRef.current;
    if (!f) {
      navigate("/config", { replace: true });
      return;
    }
    start(f);
    // Si el usuario navega a mitad de stream, sin esto el fetch queda vivo
    // (setState sobre componente desmontado) y la sesión queda colgada hasta
    // el timeout de 300s en session_store del backend.
    return () => abort();
  }, [start, abort, navigate]);

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
      // preventScroll: true — feedback de verificación manual (Bloque C,
      // 05/08/2026): "el aviso de atípico carga más arriba y después se
      // ajusta". El modal es position:fixed (ya centrado en el viewport),
      // pero .focus() por defecto pide al navegador desplazar los
      // contenedores con scroll para "revelar" el elemento enfocado — sin
      // preventScroll, el scroll de la página salta aunque el modal en sí
      // nunca se mueva, dando la sensación de que el modal "se reacomoda".
      dialogRef.current?.focus({ preventScroll: true });
    } else if (previouslyFocusedRef.current) {
      // Restaurar el foco al elemento que lo tenía cuando el modal se cierra.
      previouslyFocusedRef.current.focus();
      previouslyFocusedRef.current = null;
    }
  }, [modalOpen]);

  useEffect(() => {
    if (!modalOpen) return;

    const handleKeyDown = (event: KeyboardEvent) => {
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
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [modalOpen]);

  if (!form) return null;

  async function handleOutlierDecision(decision: "rechazar" | "aceptar") {
    setResolving(true);
    try {
      await resolveOutlier(decision);
    } finally {
      setResolving(false);
    }
  }

  async function handleDistribucionElegida(
    distribucion: string,
    metodo: string,
    periodosRetorno: number[],
  ) {
    setResolvingDistribucion(true);
    try {
      await resolveDistribution(distribucion, metodo, periodosRetorno);
    } finally {
      setResolvingDistribucion(false);
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
        <div className="row" style={{ alignItems: "center", marginBottom: 3 }}>
          <h1 className="h" style={{ margin: 0 }}>
            Análisis en vivo
          </h1>
          {/* A5 (plan pasada4 §3) — el "REC" que la identidad Instrumento
              especifica (Fase 2, G3): .badge-live existía en el CSS desde
              antes pero ningún componente lo usaba todavía. */}
          {state.fase === "streaming" && (
            <span className="badge-live">en vivo</span>
          )}
        </div>

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
              {/* A5 — el highlight que barre en la dirección del avance
                  mientras la Etapa 1 sigue en curso; la transición de width
                  ya existía, esto solo se agrega mientras fase==="streaming". */}
              <i
                style={{ width: `${progressPct}%` }}
                className={state.fase === "streaming" ? "prog__live" : undefined}
              />
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
                    {/* N1 (limpieza SonarCloud): antes era un <div role="button"
                        tabIndex onClick onKeyDown> — un <button> nativo da lo
                        mismo (Enter/Espacio, foco) con menos código.
                        F8 (informe-diagnostico-ui-rota.md): antes usaba el
                        atributo `disabled` nativo — un botón "no tiene nada
                        que mostrar todavía" y uno "roto" se ven idénticos así
                        (grisado, sin explicación). aria-disabled mantiene el
                        botón fuera de la interacción real (toggleGroup ya
                        ignora el click si !expandable) sin el aspecto de
                        control roto; la pill "esperando resultados" de arriba
                        es la que comunica por qué. */}
                    <button
                      type="button"
                      className={STEP_CLASS[status]}
                      aria-disabled={!expandable}
                      onClick={() => toggleGroup(group.key, expandable)}
                    >
                      <div className="node">{status === "ok" ? "✓" : "▸"}</div>
                      {/* A5 — key={status}: cuando llega un test_result nuevo
                          y el grupo cambia de estado, React reemplaza este
                          nodo en vez de mutarlo, y .step-entrance dispara el
                          fade-up (components.css). El texto sigue correcto
                          de inmediato, no hay nada que testear con waitFor. */}
                      <div style={{ flex: 1 }} className="step-entrance" key={status}>
                        <b>{group.label}</b> <StatusPill status={status} />
                      </div>
                    </button>
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
                              <td className="num">
                                <CountUp value={t.estadistico} />
                              </td>
                              <td className="num">
                                <CountUp value={t.valor_critico} />
                              </td>
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

        {/* DECISIÓN 052 — Etapa 2 pausa DENTRO de este mismo stream, igual
            que Chow arriba: sin navegación a una ruta separada. Se muestra
            en cuanto llega el ranking y sigue visible después de resolver
            (de ahí que la condición sea "existe el dato", no "la fase es
            waiting_distribution" — el usuario elige y la grilla se queda a
            la vista mientras se calculan los eventos). */}
        {state.fase !== "error" && state.etapa2 && (
          <div style={{ marginTop: 20 }}>
            <h2 className="h" style={{ fontSize: 16, marginBottom: 0 }}>
              {state.fase === "waiting_distribution"
                ? "Elegí una distribución"
                : "Ranking de distribuciones"}
            </h2>
            <p className="sub">
              METIS ordena por EEA; la distribución la elegís vos.
            </p>
            <Etapa2RankingView
              etapa2={{
                ranking: state.etapa2.ranking,
                warnings: state.etapa2.warnings,
                puntos_empiricos: state.etapa2.puntos_empiricos,
              }}
              onElegir={
                state.fase === "waiting_distribution"
                  ? handleDistribucionElegida
                  : undefined
              }
              resolving={resolvingDistribucion}
              mediaSerie={state.result?.descriptive?.media}
            />
          </div>
        )}

        {state.fase !== "error" && state.eventosDiseno && (
          <div style={{ marginTop: 20 }}>
            <h2 className="h" style={{ fontSize: 16, marginBottom: 0 }}>
              Evento de diseño
            </h2>
            <Etapa2EventosView
              eventos={state.eventosDiseno}
              puntosEmpiricos={state.etapa2?.puntos_empiricos ?? []}
            />
          </div>
        )}

        {state.fase === "done" && (
          <div className="banner ok" style={{ marginTop: 14 }}>
            <span className="ic">✓</span> Análisis completo.{" "}
            <Magnet style={{ marginLeft: "auto" }}>
              <SpecularHighlight>
                <button
                  type="button"
                  className="b b-pri"
                  onClick={() =>
                    navigate("/results", {
                      state: {
                        result: state.result,
                        analysisId: state.analysisId,
                        modo: form.modo,
                        etapa2: state.etapa2,
                        eventosDiseno: state.eventosDiseno,
                        mesInicioAnio: form.mes_inicio_anio,
                      },
                    })
                  }
                >
                  Ver resultados ▸
                </button>
              </SpecularHighlight>
            </Magnet>
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
          >
            <h2 id="outlier-title" className="h">
              Dato atípico detectado
            </h2>
            <p className="sub">
              Chow detectó un valor atípico:{" "}
              <span className="num">
                <CountUp value={state.outlier.valor_atipico} />
              </span>
              . ¿Qué hacemos con este dato?
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
              <Magnet>
                <SpecularHighlight>
                  <button
                    type="button"
                    className="b b-pri"
                    disabled={resolving}
                    onClick={() => handleOutlierDecision("aceptar")}
                  >
                    Aceptar
                  </button>
                </SpecularHighlight>
              </Magnet>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
