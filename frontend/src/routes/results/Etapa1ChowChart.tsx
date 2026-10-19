import { InteractiveChart } from "../../charts/InteractiveChart";
import type { ChartSeries } from "../../charts/InteractiveChart";
import { formatAxis } from "../../i18n/format";
import { notaCriterioAnio } from "../../i18n/mesInicioAnio";
import type { Etapa1Datos, TestResultDetail } from "../../api/types";
import { interaccionDeSeleccion } from "./exclusiones";
import type { SeleccionPuntos } from "./exclusiones";

/**
 * Gráfico de Chow — la serie analizada (serie_efectiva) con el atípico
 * marcado. PR 4 del plan de cierre de pendientes no-test.
 *
 * Sin toggle calendario/configurado (DECISIÓN 058 §2, apartamiento parcial
 * de la regla de "dos versiones" de constraints.md, documentado ahí):
 * Chow corrió sobre serie_efectiva — la agregación con el mes_inicio_anio
 * configurado. El atípico es un punto DE ESA serie; en la agregación
 * calendario ese punto puede no existir, o existir con otro valor y otro
 * año. Un toggle acá presentaría un atípico que no corresponde a lo que
 * el gráfico dice.
 *
 * `indice_atipico` ya viene mapeado a posición en `serie_efectiva`
 * (DECISIÓN 058 §5) — sin traducir nada acá. `null` tras rechazar el
 * atípico (iteración 2 del stream): la serie se dibuja sin marcador.
 *
 * Fajas de máximos y mínimos — Chow (Grubbs-Beck) marca un dato como
 * atípico cuando |ln(x) − media_log| / s_log supera K_N. Llevado a la
 * escala original de la serie, eso son dos umbrales horizontales:
 *   exp(media_log ± K_N · s_log)
 * entre los que cae la población "normal". DECISIÓN 079: los umbrales vienen
 * del servidor (`terminos.limite_inferior`/`limite_superior`), los mismos con
 * que Chow decidió, y se marcan TODOS los valores fuera de ellos
 * (`chow.valores_atipicos`), con un rombo además del color. Un análisis
 * guardado antes de esa decisión no trae los umbrales: se reconstruyen de
 * `media_log`/`s_log` y K_N, la cuenta que este gráfico hacía antes, y se
 * marca solo `indice_atipico`. Si Chow no se ejecutó (serie con ceros o
 * valores ≤ 0) `explicacion` es null y las fajas no se dibujan.
 *
 * Revisión 19/10/2026 de la DECISIÓN 073: cuando no se ejecutó, el gráfico lo
 * dice arriba y marca con un cuadrado los valores que lo impidieron
 * (`chow.valores_no_validos`, del servidor). No son atípicos: un negativo o un
 * cero no tiene logaritmo. "Físicamente imposible" solo se dice de un negativo
 * en caudal o precipitación (`tipoVariable`); un cero en caudal es posible.
 */
export function Etapa1ChowChart({
  datos,
  chow,
  mesInicioAnio,
  seleccion,
  tipoVariable,
}: Readonly<{
  datos: Etapa1Datos;
  chow?: TestResultDetail;
  mesInicioAnio?: number;
  seleccion?: SeleccionPuntos;
  tipoVariable?: string;
}>) {
  if (!datos.timestamps_efectivos) return null;
  const timestamps = datos.timestamps_efectivos;

  // `id` = posición en serie_efectiva, el espacio de índices de la selección
  // (y de `indice_atipico`).
  const todosLosPuntos = datos.serie_efectiva.map((v, i) => ({
    x: timestamps[i]?.anio ?? 0,
    y: v,
    id: i,
  }));
  const { marked, onPointActivate } = interaccionDeSeleccion(seleccion);
  const indicesAtipicos = new Set(
    chow?.valores_atipicos
      ? chow.valores_atipicos.map((a) => a.indice)
      : datos.indice_atipico !== null
        ? [datos.indice_atipico]
        : [],
  );
  const noEjecutada = chow?.veredicto === "no_ejecutada";
  const indicesNoValidos = new Set(
    noEjecutada ? (chow?.valores_no_validos ?? []).map((v) => v.indice) : [],
  );
  const puntosSinAtipico = todosLosPuntos.filter(
    (_, i) => !indicesAtipicos.has(i) && !indicesNoValidos.has(i),
  );
  const puntosAtipicos = todosLosPuntos.filter((_, i) => indicesAtipicos.has(i));
  const puntosNoValidos = todosLosPuntos.filter((_, i) => indicesNoValidos.has(i));

  const series: ChartSeries[] = [
    { id: "linea", kind: "line", label: "Serie analizada", colorVar: "--acc", data: todosLosPuntos },
  ];

  const limites = umbralesDeChow(chow);
  if (todosLosPuntos.length > 0 && limites) {
    const xs = todosLosPuntos.map((p) => p.x);
    const xMin = Math.min(...xs);
    const xMax = Math.max(...xs);
    const { limiteInferior, limiteSuperior } = limites;
    series.push(
      {
        id: "faja-max",
        kind: "line",
        label: "Faja de máximos",
        colorVar: "--mut",
        dashed: true,
        data: [
          { x: xMin, y: limiteSuperior },
          { x: xMax, y: limiteSuperior },
        ],
      },
      {
        id: "faja-min",
        kind: "line",
        label: "Faja de mínimos",
        colorVar: "--mut",
        dashed: true,
        data: [
          { x: xMin, y: limiteInferior },
          { x: xMax, y: limiteInferior },
        ],
      },
    );
  }

  series.push({
    id: "normales",
    kind: "points",
    label: "Datos",
    colorVar: "--acc",
    data: puntosSinAtipico,
    marked,
  });
  if (puntosAtipicos.length > 0) {
    series.push({
      id: "atipico",
      kind: "points",
      label: "Atípico (Chow)",
      // --crit (rojo) en vez de --acc2: en modo claro --acc2 (verde oliva)
      // se confundía con --acc (teal) del resto de los puntos. --crit
      // destaca en ambos temas y es el token semántico de "anomalía". El
      // rombo lo distingue también sin color (DECISIÓN 079).
      colorVar: "--crit",
      shape: "diamond",
      pointRadius: 4.5,
      data: puntosAtipicos,
      marked,
    });
  }
  if (puntosNoValidos.length > 0) {
    series.push({
      id: "no-validos",
      kind: "points",
      label: "Valor no válido para Chow",
      colorVar: "--warn",
      shape: "square",
      pointRadius: 4.5,
      data: puntosNoValidos,
      marked,
    });
  }

  return (
    <div className="card">
      <p className="ct">Gráfico de Chow</p>
      {mesInicioAnio !== undefined && (
        <p className="fn">{notaCriterioAnio(mesInicioAnio)}</p>
      )}
      {noEjecutada && chow && (
        <div className="banner warn results-chow-no-ejecutada">
          <span className="ic">▲</span> {motivoNoEjecutada(chow, tipoVariable)}
        </div>
      )}
      <InteractiveChart
        series={series}
        xScale="linear"
        onPointActivate={onPointActivate}
        ariaLabel={
          noEjecutada
            ? `Gráfico de Chow: serie analizada, sin umbrales porque la prueba no se ejecutó${
                puntosNoValidos.length > 0
                  ? `, con ${plural(puntosNoValidos.length, "valor no válido marcado", "valores no válidos marcados")}`
                  : ""
              }`
            : `Gráfico de Chow: serie analizada, fajas de máximos y mínimos, y ${
                puntosAtipicos.length === 1
                  ? "el atípico marcado"
                  : `${puntosAtipicos.length} atípicos marcados`
              }`
        }
        xLabel="Año"
        yLabel="Valor"
        xTickFormat={(v) => String(Math.round(v))}
        yTickFormat={(v) => formatAxis(v)}
      />
      {limites && (
        <p className="fn results-chow-leyenda">
          Líneas punteadas: umbrales de Bulletin 17B. Todo valor fuera de ellos es atípico
          {puntosAtipicos.length > 0 && (
            <>
              {" "}
              — <span aria-hidden="true">◆</span> {puntosAtipicos.length === 1
                ? "1 valor marcado"
                : `${puntosAtipicos.length} valores marcados`}
            </>
          )}
          .
        </p>
      )}
      {puntosNoValidos.length > 0 && (
        <p className="fn results-chow-leyenda">
          <span aria-hidden="true">■</span>{" "}
          {plural(puntosNoValidos.length, "valor no válido para Chow", "valores no válidos para Chow")}{" "}
          (no son atípicos: la prueba no puede calcularse con ellos).
        </p>
      )}
    </div>
  );
}

function plural(n: number, singular: string, varios: string): string {
  return n === 1 ? `1 ${singular}` : `${n} ${varios}`;
}

/** Por qué Chow no se ejecutó, con los valores que lo impidieron. Un negativo es
 * físicamente imposible solo en caudal o precipitación; con tipo "Otro" puede ser
 * un dato válido, y no se sugiere excluirlo. */
function motivoNoEjecutada(chow: TestResultDetail, tipoVariable?: string): string {
  const n = chow.valores_no_validos?.length ?? 0;
  const caudal = tipoVariable === "caudal_precipitacion";
  if (chow.warning_codigo === "TEST_NOT_EXECUTED_NEGATIVES" && n > 0) {
    const negativos = plural(n, "valor negativo", "valores negativos");
    return caudal
      ? `La prueba de Chow no se ejecutó: hay ${negativos}, y la prueba trabaja sobre logaritmos. ` +
          "Un valor negativo es físicamente imposible en una serie de caudal o precipitación; " +
          "podés excluirlos abajo y recalcular."
      : `Chow no se ejecutó porque la serie tiene ${negativos} y la prueba trabaja sobre logaritmos.`;
  }
  if (
    (chow.warning_codigo === "TEST_NOT_EXECUTED_ZEROS" ||
      chow.warning_codigo === "TEST_NOT_EXECUTED_CONDITION") &&
    n > 0
  ) {
    const ceros = plural(n, "cero", "ceros");
    return (
      `La prueba de Chow no se ejecutó: hay ${ceros} en la serie, y la prueba trabaja sobre ` +
      "logaritmos (el logaritmo de cero no existe)." +
      (caudal ? " Podés excluirlos abajo y recalcular." : "")
    );
  }
  return "La prueba de Chow no se ejecutó en este análisis: no hay umbrales que dibujar.";
}

/** Umbrales de Chow en la escala de la serie: los del servidor (DECISIÓN
 * 079) o, en un análisis anterior que no los trae, los que se dibujaban antes. */
function umbralesDeChow(
  chow: TestResultDetail | undefined,
): { limiteInferior: number; limiteSuperior: number } | null {
  const t = chow?.explicacion?.terminos;
  if (!t) return null;
  if (typeof t.limite_inferior === "number" && typeof t.limite_superior === "number") {
    return { limiteInferior: t.limite_inferior, limiteSuperior: t.limite_superior };
  }
  const kN = chow?.valor_critico;
  if (typeof t.media_log !== "number" || typeof t.s_log !== "number" || typeof kN !== "number") {
    return null;
  }
  return {
    limiteInferior: Math.exp(t.media_log - kN * t.s_log),
    limiteSuperior: Math.exp(t.media_log + kN * t.s_log),
  };
}
