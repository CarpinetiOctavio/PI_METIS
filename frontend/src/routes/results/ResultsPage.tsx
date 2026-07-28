import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";
import type { Etapa1Result, Modo, TestResultDetail } from "../../api/types";
import "./ResultsPage.css";

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

interface ResultsLocationState {
  result?: Etapa1Result;
  analysisId?: string | null;
  modo?: Modo;
}

function GroupTable({ items }: { items: TestResultDetail[] }) {
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
            <td className="num">{t.estadistico ?? "—"}</td>
            <td className="num">{t.valor_critico ?? "—"}</td>
            <td>
              {t.veredicto ?? "—"}
              {(t.n1 !== null || t.n2 !== null) && (
                <span className="fn">
                  {" "}
                  (n1={t.n1}, n2={t.n2})
                </span>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthed } = useAuth();

  const locationState = location.state as ResultsLocationState | null;
  const result = locationState?.result;

  useEffect(() => {
    if (!result) navigate("/config", { replace: true });
  }, [result, navigate]);

  if (!result) return null;

  // Decisión D — anónimo siempre ve la presentación Experto, sin acordeón.
  const modoEfectivo: Modo = isAuthed ? (locationState?.modo ?? "experto") : "experto";
  const pasoAPaso = modoEfectivo === "paso_a_paso";

  const groups: Group[] = [
    { key: "independencia", label: "Independencia", items: result.independencia },
    { key: "homogeneidad", label: "Homogeneidad", items: result.homogeneidad },
    { key: "tendencia", label: "Tendencia", items: result.tendencia },
    { key: "atipicos", label: "Atípicos (Chow)", items: result.atipicos },
  ];

  return (
    <div className="results-page">
      <h1 className="h">Resultados de Etapa 1</h1>

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
                <td>n</td>
                <td className="num">{result.descriptive.n}</td>
              </tr>
              <tr>
                <td>media</td>
                <td className="num">{result.descriptive.media}</td>
              </tr>
              <tr>
                <td>mediana</td>
                <td className="num">{result.descriptive.mediana}</td>
              </tr>
              <tr>
                <td>desvío S</td>
                <td className="num">{result.descriptive.desvio_estandar}</td>
              </tr>
              <tr>
                <td>CV</td>
                <td className="num">{result.descriptive.coef_variacion}</td>
              </tr>
              <tr>
                <td>asimetría</td>
                <td className="num">{result.descriptive.coef_asimetria}</td>
              </tr>
              <tr>
                <td>mínimo</td>
                <td className="num">{result.descriptive.minimo}</td>
              </tr>
              <tr>
                <td>máximo</td>
                <td className="num">{result.descriptive.maximo}</td>
              </tr>
            </tbody>
          </table>
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
              <GroupTable items={group.items} />
            </details>
          ) : (
            <div key={group.key} className="card">
              <p className="ct">{group.label}</p>
              <GroupTable items={group.items} />
            </div>
          ),
        )}
      </div>
    </div>
  );
}
