import { useMemo, useState } from "react";
import { InteractiveChart } from "../../charts/InteractiveChart";
import type { ChartPoint, ChartSeries } from "../../charts/InteractiveChart";
import type { DesgloseFila, TestResultDetail } from "../../api/types";
import { BlockMath } from "../../components/BlockMath";
import { formatearFormulaAndersonLag } from "../../i18n/explicaciones";
import { formatInt, formatNum } from "../../i18n/format";
import "./Etapa1Desglose.css";

/**
 * Desglose paso a paso de una prueba de Etapa 1 — ítems E y F del plan de
 * feedback de directores (20/09/2026). Muestra, debajo de la fórmula
 * sustituida, el detalle que `core/` calcula por paso (un renglón por lag en
 * Anderson, uno por observación en Chow) y, para Anderson, el correlograma.
 *
 * Solo renderiza: cada número viene de `Explicacion.desglose` (DECISIÓN 064,
 * "core expone, frontend renderiza"). El desglose todavía lo emite nadie —
 * llega con la Tanda 2 del plan (backend, con Octavio) — así que hasta
 * entonces `desglose` viene ausente y este componente no renderiza nada:
 * `null`, sin nota de reemplazo, y la pantalla queda igual que antes. Lo
 * mismo pasa con cualquier análisis persistido sin desglose (DECISIÓN 058 §4).
 *
 * Los nombres de las claves de cada renglón son los del contrato propuesto en
 * `docs/plan-backend-feedback-directores-20-09-2026.md` §3; si el backend los
 * cambia, es este archivo (y el fixture de sus tests) lo único que se toca.
 */

function numero(fila: DesgloseFila, clave: string): number | null {
  const v = fila[clave];
  return typeof v === "number" ? v : null;
}

export function Etapa1Desglose({ test }: Readonly<{ test: TestResultDetail }>) {
  const filas = test.explicacion?.desglose;
  if (!filas || filas.length === 0) return null;
  if (test.prueba === "anderson") return <AndersonDesglose test={test} filas={filas} />;
  if (test.prueba === "chow") return <ChowDesglose filas={filas} />;
  return null;
}

// ── Anderson: correlograma + tabla por lag + fórmula del lag elegido ─────────

function AndersonDesglose({
  test,
  filas,
}: Readonly<{ test: TestResultDetail; filas: DesgloseFila[] }>) {
  const terminos = test.explicacion!.terminos;
  // El lag que produjo el estadístico reportado (`terminos.k`, ya en el
  // payload actual): es el que se muestra elegido de entrada.
  const lagReportado = terminos.k ?? numero(filas[0], "k");
  const [elegido, setElegido] = useState<number | null>(lagReportado);

  const series = useMemo(() => construirSeriesCorrelograma(filas, elegido), [filas, elegido]);
  const filaElegida = filas.find((f) => numero(f, "k") === elegido) ?? null;
  const pasos = filaElegida ? formatearFormulaAndersonLag(terminos, filaElegida) : null;

  return (
    <details className="results-desglose">
      <summary>Ver los k pasos (un lag por renglón)</summary>

      <InteractiveChart
        series={series}
        xScale="linear"
        xName="lag k"
        yName="r_k"
        ariaLabel="Correlograma de Anderson: autocorrelación r_k por lag con las bandas de confianza del 95%"
        xLabel="Lag k"
        yLabel="r_k"
        height={260}
        xTickFormat={(v) => (Number.isInteger(v) ? String(v) : "")}
        yTickFormat={(v) => formatNum(v)}
        onPointActivate={(p) => setElegido(p.id ?? null)}
      />
      <p className="fn results-desglose__nota">
        Cada barra es la autocorrelación r_k de un lag; las líneas punteadas son las bandas del
        95% (Ec. III-3) y en rojo están los lags que salen de ellas. Al elegir un lag, en el
        gráfico o en la tabla, se muestra su cálculo.
      </p>

      <div className="results-desglose__tabla">
        <table className="t">
          <thead>
            <tr>
              <th>Lag k</th>
              <th>r_k</th>
              <th>Banda inferior</th>
              <th>Banda superior</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {filas.map((fila) => {
              const k = numero(fila, "k");
              const activa = k !== null && k === elegido;
              return (
                <tr key={k ?? JSON.stringify(fila)} data-activa={activa || undefined}>
                  <td>
                    <button
                      type="button"
                      className="results-desglose__lag"
                      aria-pressed={activa}
                      onClick={() => setElegido(k)}
                    >
                      {formatInt(k)}
                    </button>
                    {k === lagReportado && <span className="fn"> · da el estadístico</span>}
                  </td>
                  <td className="num">{formatNum(numero(fila, "r_k"))}</td>
                  <td className="num">{formatNum(numero(fila, "banda_inf"))}</td>
                  <td className="num">{formatNum(numero(fila, "banda_sup"))}</td>
                  <td>{fila.fuera === true ? "fuera" : "dentro"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {pasos && (
        <div className="results-desglose__formula">
          {pasos.map((paso) => (
            <BlockMath key={paso.latex} math={paso.latex} fallback={paso.fallback} />
          ))}
        </div>
      )}
    </details>
  );
}

function construirSeriesCorrelograma(
  filas: DesgloseFila[],
  elegido: number | null,
): ChartSeries[] {
  const conLag = filas.flatMap((f) => {
    const k = numero(f, "k");
    const r = numero(f, "r_k");
    return k === null || r === null ? [] : [{ k, r, fuera: f.fuera === true, fila: f }];
  });
  if (conLag.length === 0) return [];
  const ks = conLag.map((l) => l.k);
  const kMin = Math.min(...ks);
  const kMax = Math.max(...ks);
  const banda = (clave: string): ChartPoint[] =>
    filas.flatMap((f) => {
      const k = numero(f, "k");
      const y = numero(f, clave);
      return k === null || y === null ? [] : [{ x: k, y }];
    });
  const puntos = (fuera: boolean): ChartPoint[] =>
    conLag.filter((l) => l.fuera === fuera).map((l) => ({ x: l.k, y: l.r, id: l.k }));
  const resaltar = (p: ChartPoint) => p.id === elegido;

  return [
    { id: "cero", kind: "line", label: "Cero", colorVar: "--mut", data: [{ x: kMin, y: 0 }, { x: kMax, y: 0 }] },
    { id: "banda-sup", kind: "line", label: "Banda superior", colorVar: "--mut", dashed: true, data: banda("banda_sup") },
    { id: "banda-inf", kind: "line", label: "Banda inferior", colorVar: "--mut", dashed: true, data: banda("banda_inf") },
    { id: "dentro", kind: "points", label: "Dentro de las bandas", colorVar: "--acc", stemFrom: 0, highlight: resaltar, data: puntos(false) },
    { id: "fuera", kind: "points", label: "Fuera de las bandas", colorVar: "--crit", stemFrom: 0, highlight: resaltar, data: puntos(true) },
  ];
}

// ── Chow: tabla por observación ──────────────────────────────────────────────

function ChowDesglose({ filas }: Readonly<{ filas: DesgloseFila[] }>) {
  // Solo para resaltar el renglón de mayor z, que es el que Chow compara
  // contra K_N. No es un estadístico nuevo: es el máximo de la columna que
  // `core/` ya calculó.
  const zMax = Math.max(...filas.map((f) => numero(f, "z_i") ?? Number.NEGATIVE_INFINITY));
  return (
    <details className="results-desglose">
      <summary>Ver el cálculo por observación</summary>
      <div className="results-desglose__tabla">
        <table className="t">
          <thead>
            <tr>
              <th>i</th>
              <th>x_i</th>
              <th>ln x_i</th>
              <th>z_i</th>
            </tr>
          </thead>
          <tbody>
            {filas.map((fila, idx) => {
              const z = numero(fila, "z_i");
              const esMaximo = z !== null && z === zMax;
              return (
                <tr key={numero(fila, "i") ?? idx} data-activa={esMaximo || undefined}>
                  <td>
                    {formatInt(numero(fila, "i"))}
                    {esMaximo && <span className="fn"> · máximo</span>}
                  </td>
                  <td className="num">{formatNum(numero(fila, "x_i"))}</td>
                  <td className="num">{formatNum(numero(fila, "ln_x_i"))}</td>
                  <td className="num">{formatNum(z)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </details>
  );
}
