import { useEffect, useState } from "react";
import type Katex from "katex";

/**
 * Render de una expresión LaTeX en bloque (displayMode). F3 (feedback de
 * Facundo, 02/09/2026) — addendum a DECISIÓN 064: las 8 fórmulas de Etapa 1
 * en modo paso a paso pasan de texto monoespaciado de una línea a notación
 * matemática real (fracciones, raíces, subíndices).
 *
 * Se usa `katex` directo (`renderToString`), sin `react-katex` — una
 * dependencia en vez de tres (`react-katex` arrastra `prop-types`), y este
 * wrapper es local y chico, consistente con el criterio del repo de código
 * propio antes que una capa de terceros (DECISIÓN 045/051/056/063).
 *
 * KaTeX se carga con `import()` diná­mico — chunk aparte, no entra al bundle
 * inicial. Solo se descarga cuando un docente abre un resultado de Etapa 1
 * en modo paso a paso; CU-02 y el primer render no pagan nada (mismo
 * criterio de code-splitting que el addendum de DECISIÓN 045 para Three.js).
 * Hasta que el chunk llega, se muestra `fallback` (el texto plano de
 * `formatearFormula()`), que también es el fallback definitivo si KaTeX no
 * puede parsear `math`. La pantalla nunca queda en blanco.
 */

let katexModule: typeof Katex | null = null;
let katexLoad: Promise<typeof Katex> | null = null;

function loadKatex(): Promise<typeof Katex> {
  if (katexModule) return Promise.resolve(katexModule);
  katexLoad ??= Promise.all([
    import("katex"),
    // El CSS de KaTeX viaja en el mismo chunk diná­mico — fuera del bundle
    // inicial. Vite inyecta el <link> al cargar el chunk. `.catch` para no
    // tumbar el render si el CSS falla: la fórmula se ve sin estilar, pero
    // se ve.
    import("katex/dist/katex.min.css").catch(() => undefined),
  ]).then(([m]) => {
    katexModule = m.default;
    return katexModule;
  });
  return katexLoad;
}

export function BlockMath({
  math,
  fallback,
}: Readonly<{ math: string; fallback: string }>) {
  const [katex, setKatex] = useState<typeof Katex | null>(katexModule);

  useEffect(() => {
    if (katex) return;
    let alive = true;
    loadKatex().then((m) => {
      if (alive) setKatex(() => m);
    });
    return () => {
      alive = false;
    };
  }, [katex]);

  if (katex) {
    try {
      const html = katex.renderToString(math, {
        displayMode: true,
        throwOnError: true,
      });
      return (
        <span
          className="results-test__math"
          // El HTML lo produce katex.renderToString a partir de `math`, que
          // arman nuestras propias plantillas con números formateados —
          // nunca entrada del usuario. `throwOnError` evita el modo
          // "renderizar el error en rojo"; un LaTeX inválido cae al
          // fallback de texto.
          dangerouslySetInnerHTML={{ __html: html }}
        />
      );
    } catch {
      /* cae al fallback de abajo */
    }
  }

  return <code className="results-test__formula-fallback">{fallback}</code>;
}
