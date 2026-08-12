import { useEffect, useMemo, useRef, useState } from "react";
import type { KeyboardEvent as ReactKeyboardEvent, MouseEvent as ReactMouseEvent } from "react";
import { scaleLinear, scaleLog } from "d3-scale";
import { curveMonotoneX, line as d3line } from "d3-shape";
import "./InteractiveChart.css";

/**
 * Gráfico XY interactivo propio — DECISIÓN 056 (Bloque C del plan de
 * Etapa 2): `d3-scale`/`d3-shape` para escalas y generador de curva, SVG
 * real (no canvas) para que los tests puedan verificar el DOM que ve el
 * usuario, zoom/tooltip/teclado escritos a mano.
 *
 * Eje X logarítmico por default (T, período de retorno) — el único uso que
 * tenían los dos gráficos de Etapa 2 hasta el PR 4 del plan de cierre de
 * pendientes no-test. `xScale="linear"` lo agrega ese PR para los gráficos
 * de Etapa 1 con eje de año (serie temporal, gráfico de Chow) — cumple lo
 * que este mismo docstring pedía: agregar la opción acá, no duplicar el
 * componente. El cálculo de dominio, zoom (rueda y selección) y distancia
 * de hover se bifurcan según la escala — una razón multiplicativa (T
 * nunca es 0, tiene sentido con ratios) no sirve para años, que pueden
 * estar cerca de 0 o repartirse con espaciado lineal.
 */

export interface ChartPoint {
  x: number;
  y: number;
}

export interface ChartSeries {
  id: string;
  kind: "line" | "points";
  label: string;
  data: ChartPoint[];
  colorVar: string; // nombre de variable CSS, ej. "--acc"
}

interface InteractiveChartProps {
  series: ChartSeries[];
  ariaLabel: string;
  xLabel: string;
  yLabel: string;
  xTickFormat?: (v: number) => string;
  yTickFormat?: (v: number) => string;
  height?: number;
  xScale?: "log" | "linear";
}

const VIEW_W = 640;
const MARGIN = { top: 12, right: 16, bottom: 40, left: 60 };
const MIN_SPAN_RATIO = 1.05; // no permite zoom infinito — escala log (ratio)
const MIN_SPAN_FRACTION_LINEAR = 0.01; // análogo para escala lineal (fracción del dominio completo)
const WHEEL_ZOOM_IN = 0.8;
const WHEEL_ZOOM_OUT = 1.25;

function defaultTickFormat(v: number): string {
  return Number.isInteger(v) ? String(v) : v.toFixed(1);
}

export function InteractiveChart({
  series,
  ariaLabel,
  xLabel,
  yLabel,
  xTickFormat = defaultTickFormat,
  yTickFormat = defaultTickFormat,
  height = 320,
  xScale: xScaleType = "log",
}: Readonly<InteractiveChartProps>) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [xOverride, setXOverride] = useState<[number, number] | null>(null);
  const [drag, setDrag] = useState<{ startPlotX: number; currentPlotX: number } | null>(
    null,
  );
  const [hover, setHover] = useState<{ point: ChartPoint; series: ChartSeries } | null>(
    null,
  );
  const [focusedIndex, setFocusedIndex] = useState<number | null>(null);

  const plotWidth = VIEW_W - MARGIN.left - MARGIN.right;
  const plotHeight = height - MARGIN.top - MARGIN.bottom;

  const allPoints = useMemo(() => series.flatMap((s) => s.data), [series]);

  const fullXDomain = useMemo((): [number, number] => {
    if (xScaleType === "linear") {
      const xs = allPoints.map((p) => p.x);
      if (xs.length === 0) return [0, 1];
      const lo = Math.min(...xs);
      const hi = Math.max(...xs);
      const pad = (hi - lo) * 0.05 || Math.abs(hi) * 0.05 || 1;
      return [lo - pad, hi + pad];
    }
    const xs = allPoints.map((p) => p.x).filter((x) => x > 0);
    if (xs.length === 0) return [1.01, 10];
    const lo = Math.min(...xs);
    const hi = Math.max(...xs);
    return lo === hi ? [lo / 1.1, hi * 1.1] : [lo / 1.05, hi * 1.05];
  }, [allPoints, xScaleType]);

  const yDomain = useMemo((): [number, number] => {
    const ys = allPoints.map((p) => p.y);
    if (ys.length === 0) return [0, 1];
    const lo = Math.min(...ys);
    const hi = Math.max(...ys);
    const pad = (hi - lo) * 0.1 || Math.abs(hi) * 0.1 || 1;
    return [lo - pad, hi + pad];
  }, [allPoints]);

  const xDomain = xOverride ?? fullXDomain;

  const xScale = useMemo(
    () =>
      (xScaleType === "linear" ? scaleLinear() : scaleLog())
        .domain(xDomain)
        .range([0, plotWidth])
        .clamp(true),
    [xDomain, plotWidth, xScaleType],
  );
  const yScale = useMemo(
    () => scaleLinear().domain(yDomain).range([plotHeight, 0]),
    [yDomain, plotHeight],
  );

  // Puntos navegables por teclado: solo las series de tipo "points"
  // (marcadores), ordenados por x y acotados al dominio visible — flechas
  // se mueven "entre puntos", no a lo largo de la curva continua.
  const navigablePoints = useMemo(() => {
    const flat = series
      .filter((s) => s.kind === "points")
      .flatMap((s) => s.data.map((p) => ({ point: p, series: s })));
    flat.sort((a, b) => a.point.x - b.point.x);
    return flat.filter(
      ({ point }) => point.x >= xDomain[0] && point.x <= xDomain[1],
    );
  }, [series, xDomain]);

  function clientXToPlotX(clientX: number, rect: DOMRect): number {
    const svgX = ((clientX - rect.left) / rect.width) * VIEW_W;
    return svgX - MARGIN.left;
  }

  // Guard de span mínimo — evita zoom infinito. Escala log compara por
  // razón (T nunca es 0, tiene sentido dividir); escala lineal compara por
  // fracción del dominio completo (un año puede estar cerca de 0 o
  // repartirse con espaciado parejo, dividir no tiene el mismo sentido).
  function spanTooSmall(lo: number, hi: number): boolean {
    if (xScaleType === "linear") {
      const fullSpan = fullXDomain[1] - fullXDomain[0];
      return hi - lo < fullSpan * MIN_SPAN_FRACTION_LINEAR;
    }
    return hi / lo < MIN_SPAN_RATIO;
  }

  function zoomAround(centerValue: number, factor: number) {
    const [lo, hi] = xDomain;
    if (xScaleType === "linear") {
      const c = Math.min(Math.max(centerValue, lo), hi);
      let newLo = c - (c - lo) * factor;
      let newHi = c + (hi - c) * factor;
      newLo = Math.max(newLo, fullXDomain[0]);
      newHi = Math.min(newHi, fullXDomain[1]);
      if (spanTooSmall(newLo, newHi)) return;
      setXOverride([newLo, newHi]);
      return;
    }
    if (centerValue <= 0) return;
    const logLo = Math.log(lo);
    const logHi = Math.log(hi);
    const logC = Math.log(Math.min(Math.max(centerValue, lo), hi));
    let newLo = Math.exp(logC - (logC - logLo) * factor);
    let newHi = Math.exp(logC + (logHi - logC) * factor);
    newLo = Math.max(newLo, fullXDomain[0]);
    newHi = Math.min(newHi, fullXDomain[1]);
    if (spanTooSmall(newLo, newHi)) return;
    setXOverride([newLo, newHi]);
  }

  // Listener nativo, no el prop onWheel de React: React registra los
  // listeners de wheel/touch como passive por default (para no trabar el
  // scroll de la página), y un listener passive no puede llamar
  // preventDefault() — el zoom funcionaría igual, pero la página scrollearía
  // por debajo al mismo tiempo. { passive: false } es la única forma de
  // bloquear ese scroll mientras se hace zoom sobre el gráfico.
  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
    function onWheel(event: WheelEvent) {
      event.preventDefault();
      const rect = svg?.getBoundingClientRect();
      if (!rect || rect.width === 0) return;
      const plotX = clientXToPlotX(event.clientX, rect);
      const clamped = Math.min(Math.max(plotX, 0), plotWidth);
      const centerValue = xScale.invert(clamped);
      zoomAround(centerValue, event.deltaY < 0 ? WHEEL_ZOOM_IN : WHEEL_ZOOM_OUT);
    }
    svg.addEventListener("wheel", onWheel, { passive: false });
    return () => svg.removeEventListener("wheel", onWheel);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [xDomain, fullXDomain, plotWidth, xScaleType]);

  function handleMouseDown(event: ReactMouseEvent<SVGRectElement>) {
    const rect = svgRef.current?.getBoundingClientRect();
    if (!rect || rect.width === 0) return;
    const plotX = clientXToPlotX(event.clientX, rect);
    setDrag({ startPlotX: plotX, currentPlotX: plotX });
  }

  function handleMouseMove(event: ReactMouseEvent<SVGRectElement>) {
    const rect = svgRef.current?.getBoundingClientRect();
    if (!rect || rect.width === 0) return;
    const plotX = clientXToPlotX(event.clientX, rect);
    if (drag) {
      setDrag((d) => (d ? { ...d, currentPlotX: plotX } : d));
      return;
    }
    const clamped = Math.min(Math.max(plotX, 0), plotWidth);
    const hoverValue = xScale.invert(clamped);
    const nearest = findNearestByX(allPointsWithSeries(series), hoverValue, xScaleType);
    setHover(nearest);
  }

  function handleMouseUp() {
    if (!drag) return;
    const x1 = Math.min(drag.startPlotX, drag.currentPlotX);
    const x2 = Math.max(drag.startPlotX, drag.currentPlotX);
    setDrag(null);
    if (x2 - x1 < 8) return; // umbral mínimo — un click no dispara zoom
    const domLo = xScale.invert(Math.min(Math.max(x1, 0), plotWidth));
    const domHi = xScale.invert(Math.min(Math.max(x2, 0), plotWidth));
    if (spanTooSmall(domLo, domHi)) return;
    setXOverride([domLo, domHi]);
  }

  function handleMouseLeave() {
    setDrag(null);
    setHover(null);
  }

  function handleReset() {
    setXOverride(null);
    setHover(null);
    setFocusedIndex(null);
  }

  function handleKeyDown(event: ReactKeyboardEvent<SVGSVGElement>) {
    if (navigablePoints.length === 0) return;
    let next: number | null = focusedIndex;
    if (event.key === "ArrowRight") {
      next = focusedIndex === null ? 0 : Math.min(focusedIndex + 1, navigablePoints.length - 1);
    } else if (event.key === "ArrowLeft") {
      next = focusedIndex === null ? navigablePoints.length - 1 : Math.max(focusedIndex - 1, 0);
    } else if (event.key === "Home") {
      next = 0;
    } else if (event.key === "End") {
      next = navigablePoints.length - 1;
    } else {
      return;
    }
    event.preventDefault();
    setFocusedIndex(next);
    const target = navigablePoints[next];
    setHover({ point: target.point, series: target.series });
  }

  const tooltip = hover;
  const focusedTarget =
    focusedIndex !== null ? navigablePoints[focusedIndex] : undefined;

  const xTicks = xScale.ticks(5);
  const yTicks = yScale.ticks(5);

  const dragRectX =
    drag !== null ? Math.min(drag.startPlotX, drag.currentPlotX) : null;
  const dragRectWidth =
    drag !== null ? Math.abs(drag.currentPlotX - drag.startPlotX) : 0;

  return (
    <div className="interactive-chart">
      <div className="interactive-chart__toolbar">
        <button
          type="button"
          className="b b-sec"
          onClick={handleReset}
          disabled={xOverride === null}
        >
          Restablecer zoom
        </button>
      </div>
      <svg
        ref={svgRef}
        viewBox={`0 0 ${VIEW_W} ${height}`}
        role="img"
        aria-label={ariaLabel}
        tabIndex={0}
        className="interactive-chart__svg"
        onKeyDown={handleKeyDown}
      >
        <g transform={`translate(${MARGIN.left}, ${MARGIN.top})`}>
          {/* Grilla + ejes */}
          {yTicks.map((t) => (
            <g key={`y-${t}`} transform={`translate(0, ${yScale(t)})`}>
              <line x1={0} x2={plotWidth} className="interactive-chart__gridline" />
              <text x={-8} dy="0.32em" textAnchor="end" className="interactive-chart__tick">
                {yTickFormat(t)}
              </text>
            </g>
          ))}
          {xTicks.map((t) => (
            <g key={`x-${t}`} transform={`translate(${xScale(t)}, 0)`}>
              <line y1={0} y2={plotHeight} className="interactive-chart__gridline" />
              <text
                y={plotHeight + 16}
                textAnchor="middle"
                className="interactive-chart__tick"
              >
                {xTickFormat(t)}
              </text>
            </g>
          ))}

          {/* Series */}
          {series.map((s) => {
            if (s.kind === "line") {
              const generator = d3line<ChartPoint>()
                .x((p) => xScale(p.x))
                .y((p) => yScale(p.y))
                .curve(curveMonotoneX);
              const sorted = [...s.data].sort((a, b) => a.x - b.x);
              const d = generator(sorted) ?? "";
              return (
                <path
                  key={s.id}
                  d={d}
                  className="interactive-chart__line"
                  style={{ stroke: `var(${s.colorVar})` }}
                  data-series={s.id}
                />
              );
            }
            return (
              <g key={s.id} data-series={s.id}>
                {s.data.map((p, i) => (
                  <circle
                    key={`${s.id}-${i}`}
                    cx={xScale(p.x)}
                    cy={yScale(p.y)}
                    r={
                      focusedTarget?.series.id === s.id && focusedTarget.point === p
                        ? 5
                        : 3.5
                    }
                    className="interactive-chart__point"
                    style={{ fill: `var(${s.colorVar})` }}
                  />
                ))}
              </g>
            );
          })}

          {/* Rectángulo de selección de zoom */}
          {drag !== null && dragRectWidth > 0 && (
            <rect
              x={dragRectX ?? 0}
              y={0}
              width={dragRectWidth}
              height={plotHeight}
              className="interactive-chart__selection"
            />
          )}

          {/* Tooltip */}
          {tooltip && (
            <g
              transform={`translate(${xScale(tooltip.point.x)}, ${yScale(tooltip.point.y)})`}
              className="interactive-chart__tooltip"
            >
              <circle r={5} style={{ fill: `var(${tooltip.series.colorVar})` }} />
              <foreignObject x={10} y={-28} width={150} height={44}>
                <div className="interactive-chart__tooltip-box">
                  <div>T = {xTickFormat(tooltip.point.x)}</div>
                  <div>valor = {yTickFormat(tooltip.point.y)}</div>
                </div>
              </foreignObject>
            </g>
          )}

          {/* Superficie de captura de mouse — encima de todo, para zoom por
              selección y tooltip por hover. */}
          <rect
            x={0}
            y={0}
            width={plotWidth}
            height={plotHeight}
            className="interactive-chart__capture"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseLeave}
          />
        </g>

        <text
          x={MARGIN.left + plotWidth / 2}
          y={height - 4}
          textAnchor="middle"
          className="interactive-chart__axis-label"
        >
          {xLabel}
        </text>
        <text
          x={-(MARGIN.top + plotHeight / 2)}
          y={14}
          textAnchor="middle"
          transform="rotate(-90)"
          className="interactive-chart__axis-label"
        >
          {yLabel}
        </text>
      </svg>
    </div>
  );
}

function allPointsWithSeries(
  series: ChartSeries[],
): { point: ChartPoint; series: ChartSeries }[] {
  return series.flatMap((s) => s.data.map((point) => ({ point, series: s })));
}

function findNearestByX(
  candidates: { point: ChartPoint; series: ChartSeries }[],
  value: number,
  scaleType: "log" | "linear",
): { point: ChartPoint; series: ChartSeries } | null {
  if (candidates.length === 0) return null;
  const dist = (x: number) =>
    scaleType === "linear" ? Math.abs(x - value) : Math.abs(Math.log(x) - Math.log(value));
  let best = candidates[0];
  let bestDist = dist(best.point.x);
  for (const candidate of candidates.slice(1)) {
    const d = dist(candidate.point.x);
    if (d < bestDist) {
      best = candidate;
      bestDist = d;
    }
  }
  return best;
}
