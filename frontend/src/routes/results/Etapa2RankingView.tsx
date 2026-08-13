import { useState } from "react";
import { formatInt, formatNum } from "../../i18n/format";
import type { DistribucionResult, Etapa2Result, MetodoStatus, WarningItem } from "../../api/types";
import { SpotlightCard } from "../../components/SpotlightCard";
import { Magnet } from "../../components/Magnet";
import { SpecularHighlight } from "../../components/SpecularHighlight";
import "./Etapa2RankingView.css";

const STATUS_LABEL: Record<MetodoStatus, string> = {
  ok: "ajustado",
  no_converge: "no converge",
  no_aplicable: "no aplicable",
  disabled_zeros: "deshabilitada por ceros",
};

// F3 (fix pre-reunión) — 13 cards ocupaban toda la pantalla. El backend ya
// ordena ascendente por mejor_eea (nulls al final); acá solo se corta la
// vista, nunca se reordena.
const TOP_VISIBLE = 4;

// F4 (fix pre-reunión) — a partir de cuántos warnings del mismo código se
// colapsan en un solo banner con detalle. Solo aplica a warnings
// nivel="normal" — uno crítico nunca se agrupa (RF-GEN-P-03).
const WARNING_GROUP_THRESHOLD = 3;

const pctFormatter = new Intl.NumberFormat("es-AR", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

// F4 — "EEA 7,65775 (7,0 %)": sin esto, un ajuste al 7% de error relativo
// (razonable) y uno al 83% (inservible) se leían exactamente igual en la
// card. null si no hay media disponible (ver nota de mediaSerie más abajo).
function formatEeaConPct(eea: number | null, mediaSerie: number | null | undefined): string {
  const base = formatNum(eea);
  if (eea === null || mediaSerie === null || mediaSerie === undefined || mediaSerie === 0) {
    return base;
  }
  const pct = (eea / Math.abs(mediaSerie)) * 100;
  return `${base} (${pctFormatter.format(pct)} %)`;
}

function DistribucionCard({
  item,
  esMejor,
  onElegir,
  resolving,
  mediaSerie,
}: Readonly<{
  item: DistribucionResult;
  esMejor: boolean;
  onElegir?: (distribucion: string, metodo: string) => void;
  resolving?: boolean;
  mediaSerie?: number | null;
}>) {
  const [expandido, setExpandido] = useState(false);
  const puedeElegirMejor = Boolean(onElegir) && item.mejor_metodo !== null;

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
        <span className="num">{formatEeaConPct(item.mejor_eea, mediaSerie)}</span>
      </p>
      {/* F5 (fix pre-reunión) — el botón "Elegir" existía pero vivía detrás
          de "Ver los N métodos", así que nadie lo encontraba. Este botón es
          la acción directa sobre el mejor método; los botones por método
          de la tabla de abajo siguen para quien quiera un método distinto. */}
      {puedeElegirMejor && (
        <Magnet style={{ width: "100%", marginTop: 8 }}>
          <SpecularHighlight style={{ width: "100%" }}>
            <button
              type="button"
              className="b b-pri"
              style={{ width: "100%" }}
              disabled={resolving}
              onClick={() => onElegir!(item.distribucion, item.mejor_metodo!)}
            >
              Elegir este ajuste
            </button>
          </SpecularHighlight>
        </Magnet>
      )}
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
                <td className="num">{formatEeaConPct(m.eea, mediaSerie)}</td>
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

interface WarningGroup {
  codigo: string;
  nivel: WarningItem["nivel"];
  items: WarningItem[];
}

// F4 — agrupa SOLO warnings nivel="normal" por código; un crítico se
// devuelve en su propio grupo de un elemento, nunca mezclado (se renderiza
// entero, arriba de todo — ver abajo).
function agruparWarnings(warnings: WarningItem[]): WarningGroup[] {
  const criticos = warnings.filter((w) => w.nivel === "critico");
  const normales = warnings.filter((w) => w.nivel !== "critico");

  const porCodigo = new Map<string, WarningItem[]>();
  for (const w of normales) {
    const grupo = porCodigo.get(w.codigo) ?? [];
    grupo.push(w);
    porCodigo.set(w.codigo, grupo);
  }

  const gruposNormales: WarningGroup[] = Array.from(porCodigo.entries()).map(
    ([codigo, items]) => ({ codigo, nivel: "normal" as const, items }),
  );

  return [
    ...criticos.map((w) => ({ codigo: w.codigo, nivel: w.nivel, items: [w] })),
    ...gruposNormales,
  ];
}

/**
 * Grilla completa de Etapa 2 — espejo del payload real de
 * result_etapa2_ranking (_serializar_etapa2()), sin aplanar a un top-3.
 *
 * `onElegir` presente = modo interactivo (dentro del stream en pausa,
 * StreamPage). Ausente = modo de solo lectura (ResultsPage, HistoryDetailPage
 * mostrando un análisis ya resuelto) — sin botones "Elegir".
 *
 * `mediaSerie` — media de la serie analizada (Etapa1Result.descriptive.media
 * en cada llamador), opcional: solo habilita el "% de la media" junto al EEA
 * (F4). Sin ella la card sigue mostrando el EEA crudo, como antes.
 */
export function Etapa2RankingView({
  etapa2,
  onElegir,
  resolving,
  mediaSerie,
}: Readonly<{
  etapa2: Etapa2Result;
  onElegir?: (distribucion: string, metodo: string) => void;
  resolving?: boolean;
  mediaSerie?: number | null;
}>) {
  const [verTodas, setVerTodas] = useState(false);

  // El backend ya ordena ascendente por mejor_eea (nulls al final) — el
  // frontend no reordena ni recalcula el ranking.
  const primero = etapa2.ranking[0];
  const hayMejor = Boolean(primero && primero.mejor_eea !== null);

  const visibles = verTodas ? etapa2.ranking : etapa2.ranking.slice(0, TOP_VISIBLE);
  const ocultas = etapa2.ranking.length - TOP_VISIBLE;

  const grupos = agruparWarnings(etapa2.warnings);

  return (
    <div className="etapa2-ranking">
      {etapa2.warnings.length > 0 && (
        <div className="stack" style={{ marginBottom: 12 }}>
          {grupos.map((g) =>
            g.items.length > WARNING_GROUP_THRESHOLD ? (
              <details key={g.codigo} className={`banner ${g.nivel === "critico" ? "crit" : "warn"}`}>
                <summary>
                  <span className="ic">▲</span>
                  <span>
                    <strong>{g.items.length} combinaciones</strong> con el mismo aviso —{" "}
                    {g.items[0].descripcion}. <span className="etapa2-warning-hint">Ver detalle</span>
                  </span>
                </summary>
                <ul style={{ margin: "8px 0 0", paddingLeft: 20 }}>
                  {g.items.map((w, i) => (
                    <li key={`${w.codigo}-${i}`}>{w.descripcion}</li>
                  ))}
                </ul>
              </details>
            ) : (
              g.items.map((w, i) => (
                <div
                  key={`${w.codigo}-${i}`}
                  className={`banner ${w.nivel === "critico" ? "crit" : "warn"}`}
                >
                  <span className="ic">▲</span> {w.descripcion}
                </div>
              ))
            ),
          )}
        </div>
      )}
      <div className="etapa2-grid">
        {visibles.map((item, index) => (
          <DistribucionCard
            key={item.distribucion}
            item={item}
            esMejor={hayMejor && index === 0}
            onElegir={onElegir}
            resolving={resolving}
            mediaSerie={mediaSerie}
          />
        ))}
      </div>
      {ocultas > 0 && (
        <button
          type="button"
          className="b b-sec"
          style={{ marginTop: 12 }}
          onClick={() => setVerTodas((v) => !v)}
        >
          {verTodas
            ? `Ver solo las ${TOP_VISIBLE} mejores`
            : `Ver las ${ocultas} distribuciones restantes`}
        </button>
      )}
    </div>
  );
}
