import { scaleLinear } from "d3-scale";
import { curveMonotoneX, line as d3line } from "d3-shape";
import "./Sparkline.css";

/**
 * Sparkline decorativa — F7b (plan de fixes pre-reunión), un vistazo rápido
 * de la forma de la serie en cada fila del historial. Deliberadamente NO es
 * InteractiveChart: sin ejes, sin zoom, sin tooltip, sin teclado — montar 10
 * instancias de InteractiveChart en una lista sería caro y ninguna de esas
 * funciones tiene sentido en un ícono de 120×32.
 */

const WIDTH = 120;
const HEIGHT = 32;
const PADDING = 3;

export function Sparkline({ valores }: Readonly<{ valores: number[] }>) {
  if (valores.length < 2) return null;

  const min = Math.min(...valores);
  const max = Math.max(...valores);
  // Serie plana (todos los valores iguales) — dominio degenerado, se
  // acolcha para que la línea se dibuje al medio en vez de romper la escala.
  const [lo, hi] = min === max ? [min - 1, max + 1] : [min, max];

  const xScale = scaleLinear()
    .domain([0, valores.length - 1])
    .range([PADDING, WIDTH - PADDING]);
  const yScale = scaleLinear().domain([lo, hi]).range([HEIGHT - PADDING, PADDING]);

  const generator = d3line<number>()
    .x((_, i) => xScale(i))
    .y((v) => yScale(v))
    .curve(curveMonotoneX);

  const d = generator(valores) ?? "";

  return (
    <svg
      className="sparkline"
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      width={WIDTH}
      height={HEIGHT}
      aria-hidden="true"
    >
      <path d={d} className="sparkline__path" />
    </svg>
  );
}
