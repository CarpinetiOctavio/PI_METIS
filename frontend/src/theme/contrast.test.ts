import { describe, expect, it } from "vitest";
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
