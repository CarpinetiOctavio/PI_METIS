// WCAG 2.1 — contraste real vía luminancia relativa (fórmula canónica, no
// una aproximación a ojo). Bloque H2 (plan post-avance, DECISIÓN 043).

export function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace("#", "");
  const parsed = [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
  return [parsed[0], parsed[1], parsed[2]];
}

function relativeLuminance([r, g, b]: [number, number, number]): number {
  const [R, G, B] = [r, g, b].map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  }) as [number, number, number];
  return 0.2126 * R + 0.7152 * G + 0.0722 * B;
}

export function contrastRatio(hex1: string, hex2: string): number {
  const l1 = relativeLuminance(hexToRgb(hex1));
  const l2 = relativeLuminance(hexToRgb(hex2));
  const [lighter, darker] = l1 > l2 ? [l1, l2] : [l2, l1];
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Composición real de `color-mix(in srgb, fgHex pct%, transparent)` sobre
 * un fondo sólido — nunca medir contra el color sólido de `fgHex`, siempre
 * contra lo que efectivamente se ve compuesto en la UI (decision043.md:
 * medir contra el color sólido daba falsos negativos porque los
 * pills/banners/steps nunca aparecen así en pantalla).
 */
export function mixOver(fgHex: string, pct: number, surfaceHex: string): string {
  const fg = hexToRgb(fgHex);
  const surface = hexToRgb(surfaceHex);
  const alpha = pct / 100;
  const mixed = fg.map((c, i) => Math.round(c * alpha + surface[i] * (1 - alpha)));
  return "#" + mixed.map((c) => c.toString(16).padStart(2, "0")).join("");
}
