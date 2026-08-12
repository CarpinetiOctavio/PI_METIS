import { useMemo, useState } from "react";
import { scaleLinear } from "d3-scale";
import "./BoxPlot.css";

/**
 * Boxplot propio — PR 5 del plan de cierre de pendientes no-test. No
 * reusa `InteractiveChart`: ese componente es XY de puntos y líneas
 * (dominio continuo, zoom por rueda/selección), y un boxplot es otra
 * geometría — categorías discretas, cuartiles y bigotes, sin zoom que
 * tenga sentido sobre 12 meses fijos. Comparte tokens de tema y el
 * patrón general de accesibilidad (SVG real, `role="img"`), no la
 * implementación.
 */

export interface BoxPlotStats {
  min: number;
  q1: number;
  mediana: number;
  q3: number;
  max: number;
}

export interface BoxPlotCategory {
  label: string;
  stats: BoxPlotStats | null;
}

interface BoxPlotProps {
  categories: BoxPlotCategory[];
  ariaLabel: string;
  yLabel: string;
  yTickFormat?: (v: number) => string;
  height?: number;
}

const VIEW_W = 640;
const MARGIN = { top: 12, right: 16, bottom: 40, left: 60 };

function defaultTickFormat(v: number): string {
  return Number.isInteger(v) ? String(v) : v.toFixed(1);
}

export function BoxPlot({
  categories,
  ariaLabel,
  yLabel,
  yTickFormat = defaultTickFormat,
  height = 320,
}: Readonly<BoxPlotProps>) {
  const [hover, setHover] = useState<string | null>(null);

  const plotWidth = VIEW_W - MARGIN.left - MARGIN.right;
  const plotHeight = height - MARGIN.top - MARGIN.bottom;

  const yDomain = useMemo((): [number, number] => {
    const values = categories.flatMap((c) => (c.stats ? [c.stats.min, c.stats.max] : []));
    if (values.length === 0) return [0, 1];
    const lo = Math.min(...values);
    const hi = Math.max(...values);
    const pad = (hi - lo) * 0.1 || Math.abs(hi) * 0.1 || 1;
    return [lo - pad, hi + pad];
  }, [categories]);

  const yScale = useMemo(
    () => scaleLinear().domain(yDomain).range([plotHeight, 0]),
    [yDomain, plotHeight],
  );

  const n = categories.length || 1;
  const bandWidth = plotWidth / n;
  const boxWidth = bandWidth * 0.55;
  const yTicks = yScale.ticks(5);
  const hoveredCategory = categories.find((c) => c.label === hover) ?? null;

  return (
    <div className="box-plot">
      <svg
        viewBox={`0 0 ${VIEW_W} ${height}`}
        role="img"
        aria-label={ariaLabel}
        className="box-plot__svg"
      >
        <g transform={`translate(${MARGIN.left}, ${MARGIN.top})`}>
          {yTicks.map((t) => (
            <g key={`y-${t}`} transform={`translate(0, ${yScale(t)})`}>
              <line x1={0} x2={plotWidth} className="box-plot__gridline" />
              <text x={-8} dy="0.32em" textAnchor="end" className="box-plot__tick">
                {yTickFormat(t)}
              </text>
            </g>
          ))}

          {categories.map((c, i) => {
            const cx = bandWidth * i + bandWidth / 2;
            return (
              <g
                key={c.label}
                data-category={c.label}
                onMouseEnter={() => c.stats && setHover(c.label)}
                onMouseLeave={() => setHover(null)}
              >
                {c.stats && (
                  <>
                    <line
                      x1={cx}
                      x2={cx}
                      y1={yScale(c.stats.min)}
                      y2={yScale(c.stats.max)}
                      className="box-plot__whisker"
                    />
                    <line
                      x1={cx - boxWidth / 4}
                      x2={cx + boxWidth / 4}
                      y1={yScale(c.stats.min)}
                      y2={yScale(c.stats.min)}
                      className="box-plot__cap"
                    />
                    <line
                      x1={cx - boxWidth / 4}
                      x2={cx + boxWidth / 4}
                      y1={yScale(c.stats.max)}
                      y2={yScale(c.stats.max)}
                      className="box-plot__cap"
                    />
                    <rect
                      x={cx - boxWidth / 2}
                      y={yScale(c.stats.q3)}
                      width={boxWidth}
                      height={Math.max(yScale(c.stats.q1) - yScale(c.stats.q3), 0.5)}
                      className="box-plot__box"
                    />
                    <line
                      x1={cx - boxWidth / 2}
                      x2={cx + boxWidth / 2}
                      y1={yScale(c.stats.mediana)}
                      y2={yScale(c.stats.mediana)}
                      className="box-plot__median"
                    />
                    {/* Superficie de hover — más ancha que la caja para que
                        el tooltip no dependa de apuntar exacto a un pixel. */}
                    <rect
                      x={cx - bandWidth / 2}
                      y={0}
                      width={bandWidth}
                      height={plotHeight}
                      className="box-plot__hit"
                    />
                  </>
                )}
                <text
                  x={cx}
                  y={plotHeight + 16}
                  textAnchor="middle"
                  className="box-plot__tick"
                >
                  {c.label}
                </text>
              </g>
            );
          })}

          {hoveredCategory?.stats && (
            <g
              transform={`translate(${
                bandWidth * categories.indexOf(hoveredCategory) + bandWidth / 2
              }, ${yScale(hoveredCategory.stats.max)})`}
              className="box-plot__tooltip"
            >
              <foreignObject x={8} y={-92} width={140} height={92}>
                <div className="box-plot__tooltip-box">
                  <div>{hoveredCategory.label}</div>
                  <div>máx = {yTickFormat(hoveredCategory.stats.max)}</div>
                  <div>Q3 = {yTickFormat(hoveredCategory.stats.q3)}</div>
                  <div>mediana = {yTickFormat(hoveredCategory.stats.mediana)}</div>
                  <div>Q1 = {yTickFormat(hoveredCategory.stats.q1)}</div>
                  <div>mín = {yTickFormat(hoveredCategory.stats.min)}</div>
                </div>
              </foreignObject>
            </g>
          )}
        </g>

        <text
          x={MARGIN.left + plotWidth / 2}
          y={height - 4}
          textAnchor="middle"
          className="box-plot__axis-label"
        >
          Mes
        </text>
        <text
          x={-(MARGIN.top + plotHeight / 2)}
          y={14}
          textAnchor="middle"
          transform="rotate(-90)"
          className="box-plot__axis-label"
        >
          {yLabel}
        </text>
      </svg>
    </div>
  );
}
