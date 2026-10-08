import { useState } from "react";
import { formatInt, formatNum } from "../../i18n/format";
import { unidadPeriodoRetorno, type ContextoSerie } from "../../i18n/periodoRetorno";
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
  disabled_negatives: "no aplica: la serie tiene valores negativos",
};

// DECISIÓN 074 — respaldo SOLO para análisis persistidos antes de esa decisión,
// que no traen `pendiente_validacion` (sin backfill, DECISIÓN 058 §4). La fuente
// de verdad es `PENDIENTES_VALIDACION` en core/etapa2/distributions/__init__.py;
// esta copia existe para que un análisis viejo de una serie como est_02 no siga
// mostrando Generalizada de Pareto con "menor EEA". Se borra cuando ya no quede
// ningún análisis anterior a la DECISIÓN 074 que la necesite.
const PENDIENTES_VALIDACION_V1 = new Set(["gen_pareto"]);

function esPendiente(item: DistribucionResult): boolean {
  return item.pendiente_validacion ?? PENDIENTES_VALIDACION_V1.has(item.distribucion);
}

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

// F6 (fix pre-reunión) — mismo default que StreamPage mandaba siempre
// (Bloque B del plan de Etapa 2, api-contracts.md). Vive acá ahora porque
// el campo editable es de esta vista, no de StreamPage.
const PERIODOS_RETORNO_DEFAULT = [2, 5, 10, 25, 50, 100, 200, 500];

// Mismos límites que valida el backend en POST /analysis/distribution-decision
// (DIST_SELECTION_INVALID, api-contracts.md) — entre 1 y 20 valores, todos
// > 1 (F = 1 - 1/T necesita T > 1). Validado acá para mostrar el error
// inline antes de mandar el request, no como un 400 genérico.
function parsePeriodosRetorno(input: string): { valores: number[] } | { error: string } {
  const partes = input
    .split(",")
    .map((p) => p.trim())
    .filter((p) => p.length > 0);

  if (partes.length === 0) {
    return { error: "Ingresá al menos un período de retorno." };
  }
  if (partes.length > 20) {
    return { error: "No se pueden pedir más de 20 períodos de retorno." };
  }

  const valores: number[] = [];
  for (const parte of partes) {
    const valor = Number(parte);
    if (!Number.isFinite(valor)) {
      return { error: `"${parte}" no es un número válido.` };
    }
    if (valor <= 1) {
      return {
        error: `Los períodos de retorno deben ser mayores que 1 — "${parte}" no lo es.`,
      };
    }
    valores.push(valor);
  }
  return { valores };
}

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

// F3 (plan de fixes post-verificación, 01/10/2026) — una distribución sin
// ningún método "ok" no tiene "mejor ajuste" que mostrar: en vez de la línea
// vacía, una píldora con el motivo, sacado de los status de sus métodos.
function motivoSinAjuste(item: DistribucionResult): string | null {
  if (item.mejor_metodo !== null) return null;
  const todos = (status: MetodoStatus) =>
    item.metodos.length > 0 && item.metodos.every((m) => m.status === status);
  if (todos("disabled_negatives")) return STATUS_LABEL.disabled_negatives;
  if (todos("disabled_zeros")) return STATUS_LABEL.disabled_zeros;
  return "sin ajuste posible con esta serie";
}

/** Cuántas distribuciones del final del ranking cumplen `cond`. El frontend no
 * reordena: solo separa los bloques que ya vienen al final (el backend manda las
 * sin ajuste y, después, las pendientes de validación al final). Una que cumpla
 * `cond` en el medio, si algún día llegara, se queda en su lugar y solo cambia de
 * estilo. */
function cuantasAlFinal(
  ranking: readonly DistribucionResult[],
  cond: (d: DistribucionResult) => boolean,
): number {
  let n = 0;
  while (n < ranking.length && cond(ranking[ranking.length - 1 - n])) n += 1;
  return n;
}

function DistribucionCard({
  item,
  esMejor,
  pendiente,
  metodoElegido,
  onElegir,
  textoAccion,
  resolving,
  mediaSerie,
}: Readonly<{
  item: DistribucionResult;
  esMejor: boolean;
  // DECISIÓN 074 — se ve, con su tabla de métodos, pero sin ningún botón para
  // elegirla ni explorarla.
  pendiente: boolean;
  // Bloque C3 — método de la elección registrada del análisis, si esta
  // card es la distribución elegida (undefined si no aplica o si estamos
  // en modo "lectura"/"stream", donde no hay ninguna elección todavía).
  metodoElegido?: string;
  onElegir?: (distribucion: string, metodo: string) => void;
  textoAccion: { principal: string; porMetodo: string };
  resolving?: boolean;
  mediaSerie?: number | null;
}>) {
  const esElegida = metodoElegido !== undefined;
  const [expandido, setExpandido] = useState(esElegida);
  const puedeElegirMejor = Boolean(onElegir) && item.mejor_metodo !== null;
  const motivo = motivoSinAjuste(item);

  const clases = ["etapa2-card"];
  if (esMejor) clases.push("top");
  if (motivo) clases.push("etapa2-card--sin-ajuste");
  if (pendiente) clases.push("etapa2-card--pendiente");

  return (
    <SpotlightCard className={clases.join(" ")} glow={!motivo && !pendiente}>
      <div className="row" style={{ alignItems: "center" }}>
        <h3 className="h" style={{ fontSize: 15, margin: 0 }}>
          {item.distribucion}
        </h3>
        <span className="sp" />
        {/* constraints.md — "METIS no sugiere distribución ganadora": la
            etiqueta declara el hecho objetivo (menor EEA de la grilla), no
            una recomendación. Nunca "recomendada/óptima/ganadora". Las dos
            etiquetas pueden coincidir o no — que se vea que no coinciden es
            información docente (Bloque C3, DECISIÓN 062), no se ocultan. */}
        {esMejor && <span className="pill ok">menor EEA</span>}
        {esElegida && <span className="pill acc">elegida en el análisis</span>}
        {pendiente && <span className="pill warn">pendiente de validación</span>}
      </div>
      <p className="fn" style={{ margin: "4px 0 8px" }}>
        {formatInt(item.n_parametros)} parámetro{item.n_parametros === 1 ? "" : "s"}
      </p>
      {motivo ? (
        <p className="etapa2-card__motivo">
          <span className="pill wait">{motivo}</span>
        </p>
      ) : (
        <p className="fn">
          Mejor ajuste: {item.mejor_metodo} · EEA{" "}
          <span className="num">{formatEeaConPct(item.mejor_eea, mediaSerie)}</span>
        </p>
      )}
      {pendiente && (
        <p className="fn etapa2-card__pendiente">
          No se puede elegir en esta versión: sus fórmulas de referencia tienen una
          inconsistencia que está en revisión con el autor de la tesis.
        </p>
      )}
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
              {textoAccion.principal}
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
        <div className="etapa2-metodos-scroll">
          <table className="t">
            <thead>
              <tr>
                <th>Método</th>
                <th>EEA</th>
                <th>Estado</th>
                {onElegir && <th />}
              </tr>
            </thead>
            <tbody>
              {/* Métodos que fallaron (no_converge/no_aplicable/disabled_zeros/disabled_negatives)
                  se listan siempre, nunca ocultos — son la mitad de lo que un
                  alumno tiene que ver (la tesis misma reporta combinaciones
                  que no convergen). */}
              {item.metodos.map((m) => (
                <tr key={m.metodo}>
                  <td>
                    {m.metodo}
                    {m.metodo === metodoElegido && (
                      <span className="fn" style={{ marginLeft: 6 }}>
                        (elegido en el análisis)
                      </span>
                    )}
                  </td>
                  <td className="num">{formatEeaConPct(m.eea, mediaSerie)}</td>
                  <td>
                    {m.status === "ok" ? (
                      <span
                        className="etapa2-estado-ok"
                        role="img"
                        aria-label={STATUS_LABEL.ok}
                      />
                    ) : (
                      <span className="pill wait">{STATUS_LABEL[m.status]}</span>
                    )}
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
                          {textoAccion.porMetodo}
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
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

// Bloque C3 (plan post-avance) — tres modos explícitos, no un cuarto prop
// booleano encima de onElegir (DECISIÓN 062). "stream": pausa real del
// pipeline (StreamPage), la elección desbloquea distribution-decision.
// "lectura": sin ningún botón (ResultsPage, y HistoryDetailPage cuando el
// análisis no tiene Etapa 2 ejecutada). "exploracion": botones activos
// pero el callback pega al endpoint de recálculo stateless, no decide nada
// — HistoryDetailPage. El texto del botón cambia según el modo para que
// "explorar" nunca se lea como "decidir".
/** Texto del botón de expandir: cuenta por separado las restantes con ajuste y
 * las sin ajuste posible (F3), para que no parezca que hay más candidatas de
 * las que hay. */
function textoBotonExpandir(
  verTodas: boolean,
  conAjuste: number,
  ocultas: number,
  sinAjuste: number,
  pendientes: number,
): string {
  if (verTodas) return `Ver solo las ${Math.min(TOP_VISIBLE, conAjuste)} mejores`;
  const extras: string[] = [];
  if (sinAjuste > 0) extras.push(`${sinAjuste} sin ajuste`);
  if (pendientes > 0) {
    extras.push(`${pendientes} pendiente${pendientes === 1 ? "" : "s"} de validación`);
  }
  if (extras.length === 0) return `Ver las ${ocultas} distribuciones restantes`;
  if (ocultas === 0 && pendientes === 0) return `Ver las ${sinAjuste} sin ajuste posible`;
  const partes = ocultas > 0 ? [`las ${ocultas} restantes`, ...extras] : extras;
  return `Ver ${partes.join(" · ")}`;
}

export type Etapa2RankingViewModo = "stream" | "lectura" | "exploracion";

const TEXTO_ACCION: Record<Etapa2RankingViewModo, { principal: string; porMetodo: string }> = {
  stream: { principal: "Elegir este ajuste", porMetodo: "Elegir" },
  exploracion: { principal: "Explorar este ajuste", porMetodo: "Explorar" },
  lectura: { principal: "Elegir este ajuste", porMetodo: "Elegir" }, // nunca se renderiza sin onElegir
};

/**
 * Grilla completa de Etapa 2 — espejo del payload real de
 * result_etapa2_ranking (_serializar_etapa2()), sin aplanar a un top-3.
 *
 * `modo` decide la interactividad y el texto de los botones (ver arriba).
 * Si se omite, se infiere de `onElegir` por compatibilidad con los
 * llamadores existentes ("stream" si está presente, "lectura" si no) — los
 * llamadores nuevos deberían pasarlo explícito.
 *
 * `mediaSerie` — media de la serie analizada (Etapa1Result.descriptive.media
 * en cada llamador), opcional: solo habilita el "% de la media" junto al EEA
 * (F4). Sin ella la card sigue mostrando el EEA crudo, como antes.
 *
 * `onElegir` recibe también `periodosRetorno` (F6) — el campo editable de
 * esta vista, validado en el cliente antes de llamarlo. StreamPage ya no
 * manda un default fijo, lo que el usuario haya dejado en el campo es lo
 * que viaja.
 *
 * `seleccionRegistrada` (Bloque C3) — distribución+método de
 * `etapa2.seleccion`, si el análisis ya tiene una elección persistida.
 * Marca la card correspondiente como "elegida en el análisis", distinto de
 * "menor EEA" — las dos etiquetas pueden no coincidir.
 */
export function Etapa2RankingView({
  etapa2,
  modo,
  onElegir,
  resolving,
  mediaSerie,
  seleccionRegistrada,
  contextoSerie,
}: Readonly<{
  etapa2: Etapa2Result;
  modo?: Etapa2RankingViewModo;
  onElegir?: (distribucion: string, metodo: string, periodosRetorno: number[]) => void;
  resolving?: boolean;
  mediaSerie?: number | null;
  seleccionRegistrada?: { distribucion: string; metodo: string } | null;
  // DECISIÓN 076: solo cambia la unidad que nombra el campo de períodos de retorno.
  contextoSerie?: ContextoSerie;
}>) {
  const modoEfectivo: Etapa2RankingViewModo = modo ?? (onElegir ? "stream" : "lectura");
  const textoAccion = TEXTO_ACCION[modoEfectivo];

  // Si la elección registrada quedó fuera de las TOP_VISIBLE, arrancar con
  // la grilla completa — sin esto, "elegida en el análisis" podría no
  // verse nunca sin que el usuario supiera que hay que hacer clic en "ver
  // las N restantes".
  const indiceElegida = seleccionRegistrada
    ? etapa2.ranking.findIndex((d) => d.distribucion === seleccionRegistrada.distribucion)
    : -1;
  // F3 y DECISIÓN 074 — los dos bloques del final van aparte, cada uno bajo su
  // subtítulo: primero las sin ajuste, al último las pendientes de validación.
  const nPendientes = cuantasAlFinal(etapa2.ranking, esPendiente);
  const antesDePendientes = etapa2.ranking.slice(0, etapa2.ranking.length - nPendientes);
  const nSinAjuste = cuantasAlFinal(antesDePendientes, (d) => d.mejor_metodo === null);
  const principal = antesDePendientes.slice(0, antesDePendientes.length - nSinAjuste);
  const sinAjuste = antesDePendientes.slice(principal.length);
  const pendientes = etapa2.ranking.slice(antesDePendientes.length);
  const [verTodas, setVerTodas] = useState(
    indiceElegida >= Math.min(TOP_VISIBLE, principal.length),
  );
  const [periodosInput, setPeriodosInput] = useState(PERIODOS_RETORNO_DEFAULT.join(", "));
  const [periodosError, setPeriodosError] = useState<string | null>(null);

  // El backend ya ordena ascendente por mejor_eea (nulls al final) — el
  // frontend no reordena ni recalcula el ranking. "menor EEA" es la primera que
  // no esté pendiente de validación y tenga EEA (DECISIÓN 074): en un análisis
  // nuevo da lo mismo que la primera; en uno viejo, sin el campo y con Pareto
  // arriba, evita la etiqueta engañosa.
  const conMenorEea = etapa2.ranking.find((d) => !esPendiente(d) && d.mejor_eea !== null);

  // Si ninguna ajusta, no hay nada que mostrar arriba: las sin ajuste van a la
  // vista directamente, sin botón de por medio.
  const mostrarTodas = verTodas || principal.length === 0;
  const visibles = mostrarTodas ? principal : principal.slice(0, TOP_VISIBLE);
  const ocultas = Math.max(0, principal.length - TOP_VISIBLE);

  const grupos = agruparWarnings(etapa2.warnings);

  function handleElegir(distribucion: string, metodo: string) {
    const parsed = parsePeriodosRetorno(periodosInput);
    if ("error" in parsed) {
      setPeriodosError(parsed.error);
      return;
    }
    setPeriodosError(null);
    onElegir!(distribucion, metodo, parsed.valores);
  }

  function renderCard(item: DistribucionResult) {
    const pendiente = esPendiente(item);
    return (
      <DistribucionCard
        key={item.distribucion}
        item={item}
        esMejor={item === conMenorEea}
        pendiente={pendiente}
        metodoElegido={
          seleccionRegistrada?.distribucion === item.distribucion
            ? seleccionRegistrada.metodo
            : undefined
        }
        onElegir={onElegir && !pendiente ? handleElegir : undefined}
        textoAccion={textoAccion}
        resolving={resolving}
        mediaSerie={mediaSerie}
      />
    );
  }

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
      {/* F6 (fix pre-reunión) — antes se mandaba siempre el default fijo.
          Un solo campo acá arriba, no uno por card: los períodos de retorno
          son un parámetro del request de distribution-decision, no algo
          por distribución. */}
      {onElegir && (
        <div className="field" style={{ marginBottom: 12, maxWidth: 420 }}>
          <label htmlFor="etapa2-periodos-retorno">
            Períodos de retorno T ({unidadPeriodoRetorno(contextoSerie)}, separados por coma)
          </label>
          <input
            id="etapa2-periodos-retorno"
            className="input"
            type="text"
            value={periodosInput}
            onChange={(event) => {
              setPeriodosInput(event.target.value);
              if (periodosError) setPeriodosError(null);
            }}
            aria-invalid={periodosError !== null}
            aria-describedby={periodosError ? "etapa2-periodos-retorno-error" : undefined}
          />
          {periodosError && (
            <p
              id="etapa2-periodos-retorno-error"
              role="alert"
              className="etapa2-periodos-error"
            >
              {periodosError}
            </p>
          )}
        </div>
      )}
      <div className="etapa2-grid">
        {visibles.map(renderCard)}
      </div>
      {mostrarTodas && sinAjuste.length > 0 && (
        <>
          <p className="ct etapa2-subtitulo">
            Sin ajuste posible con esta serie ({formatInt(sinAjuste.length)})
          </p>
          <div className="etapa2-grid">{sinAjuste.map(renderCard)}</div>
        </>
      )}
      {mostrarTodas && pendientes.length > 0 && (
        <>
          <p className="ct etapa2-subtitulo">
            Pendiente de validación ({formatInt(pendientes.length)})
          </p>
          <div className="etapa2-grid">{pendientes.map(renderCard)}</div>
        </>
      )}
      {principal.length > 0 && ocultas + sinAjuste.length + pendientes.length > 0 && (
        <button
          type="button"
          className="b b-sec"
          style={{ marginTop: 12 }}
          onClick={() => setVerTodas((v) => !v)}
        >
          {textoBotonExpandir(
            verTodas,
            principal.length,
            ocultas,
            sinAjuste.length,
            pendientes.length,
          )}
        </button>
      )}
    </div>
  );
}
