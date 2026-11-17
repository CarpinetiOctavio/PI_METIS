import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { instrumentoTokens } from "./tokens";
import { contrastRatio, mixOver } from "./contrast";

const AA_NORMAL_TEXT = 4.5;

/**
 * Bloque H2 del plan post-avance (DECISIÓN 043) — el entregable de verdad
 * de esa decisión. Sin este test, el próximo ajuste visual puede volver a
 * bajar alguno de estos pares de 4.5:1 y nadie se entera hasta la próxima
 * auditoría manual. Cubre los pares reales que aparecen en la UI:
 *
 * - `.fn` (`--fnt` sobre `--surf`) — notas al pie, `(n1=X, n2=Y)`, EEA de
 *   cada card, tamaño del archivo en el dropzone. El hallazgo más
 *   extendido de la auditoría original: aparece en casi todas las
 *   pantallas.
 * - `.pill`/`.step .node`/`.banner` — texto sólido (`--ok`/`--warn`/
 *   `--crit`/`--acc`) sobre su propio color mezclado con `--surf`
 *   (`color-mix(in srgb, TOKEN pct%, transparent)`) — nunca contra el
 *   color sólido: estos elementos viven siempre dentro de `.card`
 *   (`background: var(--surf)`, ver `global.css`), nunca directo sobre
 *   `--bg`. Se verifica el peor caso (mayor % de mezcla) de cada token —
 *   más mezcla = fondo más cerca del propio color de texto = menor
 *   contraste.
 */
describe.each(["light", "dark"] as const)("contraste WCAG AA — modo %s", (modo) => {
  const t = instrumentoTokens[modo];

  it("fnt sobre surf (.fn)", () => {
    expect(contrastRatio(t.fnt, t.surf)).toBeGreaterThanOrEqual(AA_NORMAL_TEXT);
  });

  it.each([
    ["ok", 18] as const, // .step.done .node
    ["warn", 18] as const, // .step.warn .node, .pill.warn
    ["crit", 18] as const, // .step.crit .node
    // .pill.acc (historial interactivo, DECISIÓN 062) — par nuevo desde la
    // auditoría de la pasada 2, al 12% tras el ajuste de este bloque (16%
    // original daba 4.29:1 en claro, por debajo de 4.5 — ver decision043.md).
    ["acc", 12] as const,
  ])("%s sobre su propio fondo al %d%% de mezcla (peor caso)", (token, pct) => {
    const fondoCompuesto = mixOver(t[token], pct, t.surf);
    expect(contrastRatio(t[token], fondoCompuesto)).toBeGreaterThanOrEqual(AA_NORMAL_TEXT);
  });
});

/**
 * Revisión manual 21/10/2026 (D-13, #135) — el diálogo de la pausa de Chow es
 * una tarjeta semitransparente (`color-mix(var(--surf) N%, transparent)`)
 * sobre un scrim oscuro. Medir `--mut` contra `--surf` puro no veía esa
 * composición: con 55% el texto secundario quedaba en 2,9:1 con el tema
 * claro. Se compone el fondo real leyendo el % y el scrim de StreamPage.css
 * (así una baja de la opacidad rompe este test) y se toma el peor caso de lo
 * que puede haber detrás: `--bg` o `--ink` (el blur lo promedia, nunca es
 * más extremo que eso).
 */
const streamCss = readFileSync(
  path.join(path.dirname(fileURLToPath(import.meta.url)), "../routes/stream/StreamPage.css"),
  "utf-8",
);

function modalCard(): { surfPct: number; scrim: { rgb: [number, number, number]; alpha: number } } {
  const card = /^\.modal-backdrop \.card\s*\{([\s\S]*?)^\}/m.exec(streamCss)?.[1] ?? "";
  const pct = /background:\s*color-mix\(in srgb, var\(--surf\) (\d+)%, transparent\)/.exec(card);
  const backdrop = /^\.modal-backdrop\s*\{([\s\S]*?)^\}/m.exec(streamCss)?.[1] ?? "";
  const scrim = /background:\s*rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/.exec(backdrop);
  if (!pct || !scrim) throw new Error("No se encontró el fondo del modal en StreamPage.css");
  return {
    surfPct: Number(pct[1]),
    scrim: { rgb: [Number(scrim[1]), Number(scrim[2]), Number(scrim[3])], alpha: Number(scrim[4]) },
  };
}

function rgbToHex(rgb: [number, number, number]): string {
  return "#" + rgb.map((c) => c.toString(16).padStart(2, "0")).join("");
}

describe.each(["light", "dark"] as const)("contraste del diálogo de pausa de Chow — modo %s", (modo) => {
  const t = instrumentoTokens[modo];
  const { surfPct, scrim } = modalCard();

  it.each(["bg", "ink"] as const)("mut sobre la tarjeta con %s detrás del scrim", (detras) => {
    const bajoScrim = mixOver(rgbToHex(scrim.rgb), scrim.alpha * 100, t[detras]);
    const fondoTarjeta = mixOver(t.surf, surfPct, bajoScrim);
    expect(contrastRatio(t.mut, fondoTarjeta)).toBeGreaterThanOrEqual(AA_NORMAL_TEXT);
  });
});
