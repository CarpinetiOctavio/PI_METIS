import type { Etapa1Result, Modo, TestResultDetail, WarningNivel } from "../../api/types";
import { formatInt, formatNum } from "../../i18n/format";
import { notaCriterioAnio } from "../../i18n/mesInicioAnio";
import { formatearFormula, interpretar, REGLA_GRUPO } from "../../i18n/explicaciones";
import { errorText } from "../../i18n/errors.es";
import { CountUp } from "../../components/CountUp";
import { Etapa1SerieTemporalChart } from "./Etapa1SerieTemporalChart";
import { Etapa1ChowChart } from "./Etapa1ChowChart";
import { Etapa1BoxplotMensualChart } from "./Etapa1BoxplotMensualChart";
import "./Etapa1ResultView.css";

interface Group {
  key: string;
  label: string;
  items: TestResultDetail[];
}

type BannerKind = "ok" | "warn" | "crit";

const NIVEL_CONFIANZA_LABEL: Record<Etapa1Result["nivel_confianza"], string> = {
  validado: "validado",
  con_warnings: "con warnings",
  rechazado: "rechazado",
};

const NIVEL_CONFIANZA_KIND: Record<Etapa1Result["nivel_confianza"], BannerKind> = {
  validado: "ok",
  con_warnings: "warn",
  rechazado: "crit",
};

const INDEP_KIND: Record<
  NonNullable<Etapa1Result["nivel_independencia"]>,
  "ok" | "crit"
> = {
  independiente: "ok",
  dependiente: "crit",
};

const HOMOG_KIND: Record<
  NonNullable<Etapa1Result["nivel_homogeneidad"]>,
  BannerKind
> = {
  homogeneidad_ok: "ok",
  homogeneidad_warning: "warn",
  homogeneidad_critica: "crit",
};

const HOMOG_LABEL: Record<NonNullable<Etapa1Result["nivel_homogeneidad"]>, string> = {
  homogeneidad_ok: "ok",
  homogeneidad_warning: "warning",
  homogeneidad_critica: "crítico",
};

function GroupTable({ items }: Readonly<{ items: TestResultDetail[] }>) {
  if (items.length === 0) {
    return <p className="fn">No ejecutada.</p>;
  }
  return (
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
        {items.map((t) => (
          <tr key={t.prueba}>
            <td>{t.prueba}</td>
            <td className="num">
              <CountUp value={t.estadistico} />
            </td>
            <td className="num">
              <CountUp value={t.valor_critico} />
            </td>
            <td>
              {t.veredicto ?? "—"}
              {/* D6 (pasada de mejora): antes renderizaba literalmente
                  "n2=null" cuando solo uno de los dos estaba presente —
                  Cramer siempre reporta ambos, pero otras pruebas no
                  reportan ninguno. Cada uno se muestra solo si no es null. */}
              {(t.n1 !== null || t.n2 !== null) && (
                <span className="fn">
                  {" "}
                  ({t.n1 !== null && `n1=${t.n1}`}
                  {t.n1 !== null && t.n2 !== null && ", "}
                  {t.n2 !== null && `n2=${t.n2}`})
                </span>
              )}
              {/* Bloque F (plan post-avance) — antes esta celda quedaba en
                  literalmente "no_ejecutada" sin decir por qué (fila vacía
                  sin explicación). warning_codigo ya distingue las tres
                  causas reales (ceros, condición previa, muestra chica). */}
              {t.veredicto === "no_ejecutada" && t.warning_codigo && (
                <span className="fn results-test__motivo">
                  {" "}
                  — {errorText(t.warning_codigo)}
                </span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// Bloque D del plan post-avance (DECISIÓN 064) — modo paso a paso.
function VeredictoPill({
  veredicto,
  warningNivel,
}: Readonly<{ veredicto: TestResultDetail["veredicto"]; warningNivel: WarningNivel | null }>) {
  if (veredicto === "aprobada") return <span className="pill ok">aprobada</span>;
  if (veredicto === "rechazada") {
    return (
      <span className={`pill ${warningNivel === "critico" ? "crit" : "warn"}`}>rechazada</span>
    );
  }
  return <span className="fn">no ejecutada</span>;
}

// Un test por bloque: encabezado (prueba + veredicto), fórmula sustituida
// (HTML plano, DECISIÓN 064) y su interpretación en castellano. Sin
// `explicacion` (rama no_ejecutada) solo queda el encabezado + el motivo.
function GroupExplicacion({ items }: Readonly<{ items: TestResultDetail[] }>) {
  if (items.length === 0) {
    return <p className="fn">No ejecutada.</p>;
  }
  return (
    <div className="stack results-explicacion">
      {items.map((t) => {
        const formula = formatearFormula(t);
        const interpretacion = interpretar(t);
        return (
          <div key={t.prueba} className="results-test">
            <div className="results-test__header">
              <b>{t.prueba}</b> <VeredictoPill veredicto={t.veredicto} warningNivel={t.warning_nivel} />
            </div>
            {formula ? (
              <div className="results-test__formula">
                {formula.map((linea) => (
                  <code key={linea}>{linea}</code>
                ))}
                {t.explicacion && (
                  <span className="fn results-test__ecuacion">Ec. {t.explicacion.ecuacion}</span>
                )}
              </div>
            ) : (
              <p className="fn">
                {t.warning_codigo ? errorText(t.warning_codigo) : "No ejecutada."}
              </p>
            )}
            {interpretacion && <p className="results-test__interpretacion">{interpretacion}</p>}
          </div>
        );
      })}
    </div>
  );
}

/**
 * Vista puramente presentacional de un `Etapa1Result` — reutilizada por
 * ResultsPage (stream en vivo, Fase 3) y HistoryDetailPage (historial
 * persistido, Fase 4). No decide el `modo` efectivo (anónimo=experto,
 * UX-D) — eso es responsabilidad de quien la use, según su propio
 * contexto de auth.
 *
 * `mesInicioAnio` (Bloque F5, DECISIÓN 057) es opcional a propósito. Viaja
 * de punta a punta en la sesión interactiva (ConfigPage → StreamPage →
 * ResultsPage vía router state). Corrección PR 3 del plan de cierre de
 * pendientes no-test (DECISIÓN 058): `mes_inicio_anio` SÍ se persiste en
 * `analyses.configuracion` desde DECISIÓN 057 (PR 8 del plan de Etapa 2) —
 * lo que faltaba era que `GET /history/{id}` devolviera `configuracion`, y
 * ya lo hace. `HistoryDetailPage` todavía no lo consume para pasarlo acá
 * (PR 5 del mismo plan) — hasta que eso pase, sin el prop la nota
 * simplemente no se renderiza.
 */
export function Etapa1ResultView({
  result,
  modo,
  mesInicioAnio,
}: Readonly<{ result: Etapa1Result; modo: Modo; mesInicioAnio?: number }>) {
  const pasoAPaso = modo === "paso_a_paso";

  const groups: Group[] = [
    { key: "independencia", label: "Independencia", items: result.independencia },
    { key: "homogeneidad", label: "Homogeneidad", items: result.homogeneidad },
    { key: "tendencia", label: "Tendencia", items: result.tendencia },
    { key: "atipicos", label: "Atípicos (Chow)", items: result.atipicos },
  ];

  return (
    <>
      <div className={`banner ${NIVEL_CONFIANZA_KIND[result.nivel_confianza]}`}>
        <span className="ic">i</span> Resultado:{" "}
        <b>&nbsp;{NIVEL_CONFIANZA_LABEL[result.nivel_confianza]}</b>
      </div>

      <div className="results-kpis">
        <div className="kpi">
          <div className="l">Independencia</div>
          <div className="v">
            {result.nivel_independencia ? (
              <span className={`pill ${INDEP_KIND[result.nivel_independencia]}`}>
                {result.nivel_independencia}
              </span>
            ) : (
              "—"
            )}
          </div>
        </div>
        <div className="kpi">
          <div className="l">Homogeneidad</div>
          <div className="v">
            {result.nivel_homogeneidad ? (
              <span className={`pill ${HOMOG_KIND[result.nivel_homogeneidad]}`}>
                {HOMOG_LABEL[result.nivel_homogeneidad]}
              </span>
            ) : (
              "—"
            )}
          </div>
        </div>
      </div>

      {result.descriptive && (
        <div className="card">
          <p className="ct">Descriptivos</p>
          <table className="t">
            <tbody>
              <tr>
                <th scope="row">n</th>
                <td className="num">{formatInt(result.descriptive.n)}</td>
              </tr>
              <tr>
                <th scope="row">media</th>
                <td className="num">{formatNum(result.descriptive.media)}</td>
              </tr>
              <tr>
                <th scope="row">mediana</th>
                <td className="num">{formatNum(result.descriptive.mediana)}</td>
              </tr>
              <tr>
                <th scope="row">desvío S</th>
                <td className="num">{formatNum(result.descriptive.desvio_estandar)}</td>
              </tr>
              <tr>
                <th scope="row">CV</th>
                <td className="num">{formatNum(result.descriptive.coef_variacion)}</td>
              </tr>
              <tr>
                <th scope="row">asimetría</th>
                <td className="num">{formatNum(result.descriptive.coef_asimetria)}</td>
              </tr>
              <tr>
                <th scope="row">mínimo</th>
                <td className="num">{formatNum(result.descriptive.minimo)}</td>
              </tr>
              <tr>
                <th scope="row">máximo</th>
                <td className="num">{formatNum(result.descriptive.maximo)}</td>
              </tr>
            </tbody>
          </table>
          {mesInicioAnio !== undefined && (
            <p className="fn">{notaCriterioAnio(mesInicioAnio)}</p>
          )}
        </div>
      )}

      {/* PR 4 del plan de cierre de pendientes no-test — sin result.datos
          (historial persistido antes de la migración 005, DECISIÓN 058 §4)
          esta sección no se renderiza, sin nota de reemplazo acá: el
          estado vacío completo (con la nota explicando por qué) es
          responsabilidad de HistoryDetailPage (PR 5), no de este
          componente presentacional puro. */}
      {result.datos && (
        <div className="stack" style={{ marginTop: 14 }}>
          <Etapa1SerieTemporalChart datos={result.datos} />
          <Etapa1ChowChart
            datos={result.datos}
            chow={result.atipicos.find((t) => t.prueba === "chow")}
            mesInicioAnio={mesInicioAnio}
          />
          <Etapa1BoxplotMensualChart datos={result.datos} mesInicioAnio={mesInicioAnio} />
        </div>
      )}

      {result.warnings.length > 0 && (
        <div className="stack" style={{ marginTop: 14 }}>
          {result.warnings.map((warning) => (
            <div
              key={warning.codigo}
              className={`banner ${warning.nivel === "critico" ? "crit" : "warn"}`}
            >
              <span className="ic">{warning.nivel === "critico" ? "✕" : "▲"}</span>{" "}
              {warning.descripcion}
            </div>
          ))}
        </div>
      )}

      <div className="stack" style={{ marginTop: 14 }}>
        {groups.map((group) =>
          pasoAPaso ? (
            <details key={group.key} className="card results-group">
              <summary>{group.label}</summary>
              <GroupExplicacion items={group.items} />
              {REGLA_GRUPO[group.key] && (
                <p className="fn results-group__regla">{REGLA_GRUPO[group.key]}</p>
              )}
            </details>
          ) : (
            <div key={group.key} className="card">
              <p className="ct">{group.label}</p>
              <GroupTable items={group.items} />
            </div>
          ),
        )}
      </div>
    </>
  );
}
