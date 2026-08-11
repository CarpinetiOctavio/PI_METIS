import { useState } from "react";
import { formatInt, formatNum } from "../../i18n/format";
import type { DistribucionResult, Etapa2Result, MetodoStatus } from "../../api/types";
import { SpotlightCard } from "../../components/SpotlightCard";
import "./Etapa2RankingView.css";

const STATUS_LABEL: Record<MetodoStatus, string> = {
  ok: "ajustado",
  no_converge: "no converge",
  no_aplicable: "no aplicable",
  disabled_zeros: "deshabilitada por ceros",
};

function DistribucionCard({
  item,
  esMejor,
  onElegir,
  resolving,
}: Readonly<{
  item: DistribucionResult;
  esMejor: boolean;
  onElegir?: (distribucion: string, metodo: string) => void;
  resolving?: boolean;
}>) {
  const [expandido, setExpandido] = useState(false);

  return (
    <SpotlightCard className={`etapa2-card${esMejor ? " top" : ""}`}>
      <div className="row" style={{ alignItems: "center" }}>
        <h3 className="h" style={{ fontSize: 15, margin: 0 }}>
          {item.distribucion}
        </h3>
        <span className="sp" />
        {/* constraints.md — "METIS no sugiere distribución ganadora": la
            etiqueta declara el hecho objetivo (menor EEA de la grilla), no
            una recomendación. Nunca "recomendada/óptima/ganadora". */}
        {esMejor && <span className="pill ok">menor EEA</span>}
      </div>
      <p className="fn" style={{ margin: "4px 0 8px" }}>
        {formatInt(item.n_parametros)} parámetro{item.n_parametros === 1 ? "" : "s"}
      </p>
      <p className="fn">
        Mejor ajuste: {item.mejor_metodo ?? "—"} · EEA{" "}
        <span className="num">{formatNum(item.mejor_eea)}</span>
      </p>
      <button
        type="button"
        className="b b-sec"
        style={{ width: "100%", marginTop: 8 }}
        onClick={() => setExpandido((v) => !v)}
        aria-expanded={expandido}
      >
        {expandido ? "Ocultar métodos" : `Ver los ${item.metodos.length} métodos`}
      </button>
      {expandido && (
        <table className="t" style={{ marginTop: 8 }}>
          <thead>
            <tr>
              <th>Método</th>
              <th>EEA</th>
              <th>Estado</th>
              {onElegir && <th />}
            </tr>
          </thead>
          <tbody>
            {/* Métodos que fallaron (no_converge/no_aplicable/disabled_zeros)
                se listan siempre, nunca ocultos — son la mitad de lo que un
                alumno tiene que ver (la tesis misma reporta combinaciones
                que no convergen). */}
            {item.metodos.map((m) => (
              <tr key={m.metodo}>
                <td>{m.metodo}</td>
                <td className="num">{formatNum(m.eea)}</td>
                <td>
                  <span className={`pill ${m.status === "ok" ? "ok" : "wait"}`}>
                    {STATUS_LABEL[m.status]}
                  </span>
                </td>
                {onElegir && (
                  <td>
                    {m.status === "ok" && (
                      <button
                        type="button"
                        className="b b-sec"
                        disabled={resolving}
                        onClick={() => onElegir(item.distribucion, m.metodo)}
                      >
                        Elegir
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </SpotlightCard>
  );
}

/**
 * Grilla completa de Etapa 2 — espejo del payload real de
 * result_etapa2_ranking (_serializar_etapa2()), sin aplanar a un top-3.
 *
 * `onElegir` presente = modo interactivo (dentro del stream en pausa,
 * StreamPage). Ausente = modo de solo lectura (ResultsPage, HistoryDetailPage
 * mostrando un análisis ya resuelto) — sin botones "Elegir".
 */
export function Etapa2RankingView({
  etapa2,
  onElegir,
  resolving,
}: Readonly<{
  etapa2: Etapa2Result;
  onElegir?: (distribucion: string, metodo: string) => void;
  resolving?: boolean;
}>) {
  // El backend ya ordena ascendente por mejor_eea (nulls al final) — el
  // frontend no reordena ni recalcula el ranking.
  const primero = etapa2.ranking[0];
  const hayMejor = Boolean(primero && primero.mejor_eea !== null);

  return (
    <div className="etapa2-ranking">
      {etapa2.warnings.length > 0 && (
        <div className="stack" style={{ marginBottom: 12 }}>
          {etapa2.warnings.map((w, i) => (
            <div
              key={`${w.codigo}-${i}`}
              className={`banner ${w.nivel === "critico" ? "crit" : "warn"}`}
            >
              <span className="ic">▲</span> {w.descripcion}
            </div>
          ))}
        </div>
      )}
      <div className="etapa2-grid">
        {etapa2.ranking.map((item, index) => (
          <DistribucionCard
            key={item.distribucion}
            item={item}
            esMejor={hayMejor && index === 0}
            onElegir={onElegir}
            resolving={resolving}
          />
        ))}
      </div>
    </div>
  );
}
