# DECISIÓN 064 — Paso a paso docente: `core/` calcula, el frontend renderiza e interpreta

**Fecha:** 18 de Agosto de 2026
**Estado:** Aplicada — backend (`feature/paso-a-paso-backend-explicacion`) y
frontend (`feature/paso-a-paso-frontend-render`, apilada sobre la anterior)
del Bloque D del [plan post-avance](../plan-post-avance.md).

### Contexto — el número reservado ya estaba tomado

`plan-post-avance.md` había reservado el 061 para este tema. Ya no está
libre: [DECISIÓN 060 y 061](decision060.md) los tomó la auditoría de
restricciones de dominio de Etapa 2 (Octavio, 17/08/2026), y
[DECISIÓN 063](decision063.md) (panel acoplable, Bloque E) tomó el 062 y 063
en el mismo reordenamiento — ver esa decisión para el detalle completo de
la colisión. Este documento toma el siguiente número real libre, 064.

### Diagnóstico — la diferencia entre modos era solo un `<details>`

Verificado contra `Etapa1ResultView.tsx` antes de este PR: la única
diferencia entre modo paso a paso y modo experto era

```tsx
pasoAPaso ? <details className="card"><summary>{label}</summary>…</details>
          : <div className="card"><p className="ct">{label}</p>…</div>
```

Acordeón contra card abierta — la misma `GroupTable` (tabla compacta
prueba/estadístico/crítico/veredicto) en los dos casos. `constraints.md` ya
define cuál debería ser la diferencia real, pero solo para el PDF de
exportación:

> En modo paso a paso: incluir fórmulas con valores sustituidos.
> En modo experto: resultados directos, sin fórmulas ni explicaciones.

### La pregunta que resuelve esta decisión

Para llevar esa diferencia a la UI (no solo al PDF), ¿dónde vive el cálculo
de "la fórmula con los valores de esta serie ya sustituidos"?

### Decisión

**En `core/`, no en TypeScript.** `formulas-etapa1.md` ya mapea cada
fórmula del proyecto a su ecuación en la tesis de Facundo, y la regla del
repo es que ninguna fórmula se implementa sin esa referencia explícita. Si
la sustitución de valores se arma en el frontend, aparece una segunda
fuente de verdad matemática fuera de `core/` — sin tests de regresión, sin
trazabilidad a una ecuación, exactamente lo que la arquitectura del
proyecto (`core/` completamente aislado, ver `architecture.md`) está
diseñada para evitar.

**Solución:** `TestResult` gana un campo opcional `explicacion:
{ecuacion, terminos} | None` (`core/types.py`). Cada una de las 8 pruebas
de Etapa 1 (Anderson, Wald-Wolfowitz, Helmert, t de Student, Cramer,
Mann-Kendall, Kolmogorov-Smirnov, Chow) lo puebla con los términos
intermedios que ya calculaba de todos modos — no hay ningún cálculo nuevo,
solo se **expone** lo que antes quedaba descartado al construir el
`TestResult` final. `null` en cualquier prueba con `veredicto ==
"no_ejecutada"`: no hay fórmula que sustituir sobre datos que no se
llegaron a usar.

El frontend **renderiza**, no calcula: sustituye `terminos` en una
plantilla de texto (HTML plano, ver "Renderizado de fórmulas" más abajo) y
arma una interpretación en castellano. La única aritmética que hace el
frontend es cosmética — reconstruir el denominador de una fracción para
mostrarlo, por ejemplo — nunca deriva un estadístico que no esté ya en
`estadistico`/estos términos.

### Por qué Cramer lleva más términos que los demás

Todas las pruebas reportan un único `estadistico`/`valor_critico`. Cramer
también, pero por construcción (`calcular_cramer()`, sin cambios en este
PR) ese par es el "binding" — el de mayor ratio `t/vc` entre los dos
bloques (60%/30%). La fórmula sustituida que el docente necesita ver
requiere los **dos** bloques completos (`tau_w1`, `tau_w2`, `t_w1`, `t_w2`,
`vc_w1`, `vc_w2`, `n_w1`, `n_w2`) — sin eso, "por qué `aprobada` exige que
los dos aprueben, no solo el reportado" no se puede explicar. `terminos` de
Cramer lleva ambos bloques completos; el `estadistico`/`valor_critico`
"binding" de siempre no cambia.

### Renderizado de fórmulas — HTML plano, no KaTeX

Dos caminos evaluados:

- **KaTeX** (`katex` + `react-katex`) — fórmulas de verdad, ~70 KB gzip.
  Dependencia nueva, defendible ante el tribunal (estándar de facto), pero
  peso real en el bundle.
- **HTML plano** con `<sub>`/`<sup>` y la tipografía monoespaciada que ya
  existe — cero dependencias nuevas, alcanza para las 8 fórmulas de
  Etapa 1 (todas son expresiones de una línea: sumas, raíces, fracciones
  simples). Se queda corto para Etapa 2 (Log-Pearson III, GVE, con
  sistemas de ecuaciones).

**Decisión: HTML plano para Etapa 1** (este PR). Evaluar KaTeX recién si
Etapa 2 lo pide — mismo criterio que ya aplicaron DECISIÓN 045/051/056/063
("código propio y chico antes que una dependencia grande, mientras
alcance").

### Alcance de este PR — solo backend

Este PR (`feature/paso-a-paso-backend-explicacion`) cierra únicamente el
lado del contrato: `core/types.py`, las 8 pruebas de `core/etapa1/`, y
`test_result_dict()` en `services/analysis_service.py` (el que sirve
`result_etapa1` y lo que queda persistido en `analysis_results.etapa1` para
CU-01). **No toca** el evento SSE `test_result` (el timeline transitorio de
`StreamPage` — no reusa `Etapa1ResultView`, así que no hay nada ahí que
renderizar distinto entre modos todavía; agregar el campo sería payload sin
consumidor). El PR de frontend (Bloque D del plan, mini-plan propio) es el
que hace que el modo paso a paso deje de ser un acordeón vacío.

### Criterio de hecho — backend

- `explicacion.terminos` de cada prueba reconstruye `estadistico` con
  precisión de punto flotante completa (`abs=1e-9`), no solo "en el orden
  de magnitud correcto" — test dedicado por prueba en
  `tests/unit/core/etapa1/`.
- `explicacion is None` para toda rama `no_ejecutada` — test dedicado por
  prueba con esa rama (Wald con `n1=0`, Cramer con `s_global=0`, Mann-Kendall
  con `n<10`, Chow con ceros).
- `pytest -m "unit or integration"` en verde (320 passed, 1 skipped —
  +12 sobre la línea base).

### Frontend — qué se agregó

`frontend/src/i18n/explicaciones.ts` — `formatearFormula()` (8 plantillas,
una por prueba, HTML plano) e `interpretar()` (interpretación en
castellano, sensible al veredicto), más `REGLA_GRUPO` (las tres reglas de
D1: Anderson manda, Cramer manda, y la regla OR de tendencia — `atipicos`
no tiene, un solo test no tiene jerarquía que explicar). `Etapa1ResultView`
gana `GroupExplicacion` (un bloque por prueba: encabezado + fórmula +
interpretación) que reemplaza a `GroupTable` solo en modo paso a paso; modo
experto no cambia — sigue siendo la tabla compacta original.

La única aritmética que hace el frontend es cosmética: t de Student no
persiste el denominador `Sp·√(1/n₁+1/n₂)` en `terminos` (solo `sp`, `n1`,
`n2`), así que `formatearFormula()` lo reconstruye para mostrarlo — el
mismo número que `core/` ya usó para llegar a `estadistico`, no un cálculo
nuevo.

**Mann-Kendall no reconstruye la tipificación de Z.** `formulas-etapa1.md`
§7 no deja una fórmula citable para la corrección por empates que aplica
`pymannkendall` (la delega a la librería, con la nota "aproximación normal
con corrección por empates") — mostrar una ecuación inventada ahí habría
sido peor que no mostrar ninguna. `formatearFormula()` para
`mann_kendall` muestra `S` y `Var(S)` (los términos que sí están
documentados) y nombra la corrección en prosa, sin fingir una sustitución
exacta que no está verificada.

### Criterio de hecho — frontend

- `i18n/explicaciones.test.ts` (16 tests) — cada plantilla reproduce
  `estadistico`/`valor_critico` a partir de `terminos`; `interpretar()`
  cambia de redacción según `veredicto`; Cramer distingue "los dos bloques
  aprueban" de "al menos uno rechaza".
- `Etapa1ResultView.test.tsx` (5 tests) — modo experto no muestra fórmula
  ni regla de grupo; modo paso a paso sí; una prueba `no_ejecutada` muestra
  el motivo sin fórmula vacía; `atipicos` no muestra regla de grupo.
- `npx tsc -b`, `npm run lint`, `npm test` (305 passed), `npm run build` —
  todos en verde.
- Verificado en el navegador de dev contra el backend real (Docker, CU-01
  con modo paso a paso): las 8 pruebas con fórmula + interpretación reales
  sobre una serie de 40 años, incluidos los dos bloques de Cramer y la nota
  de Mann-Kendall sin fórmula inventada — confirmado contra el texto real
  del DOM, no solo contra los tests.

**Ver también:** [DECISIÓN 063](decision063.md) — mismo criterio de
código propio antes que dependencia grande, para el panel acoplable.
`.claude/rules/core/formulas-etapa1.md` — las 8 ecuaciones referenciadas
por `explicacion.ecuacion`.

---

## Addendum — 02/09/2026: KaTeX entra para el render de las fórmulas de Etapa 1

**Origen.** `mejoras metis.docx` — feedback de Facundo sobre la UI en
funcionamiento (`docs/frontend/plan-fixes-feedback-facundo-02-09-2026.md`,
hallazgo F3). Con la captura de pantalla: en modo paso a paso la fórmula
sustituida sale como una sola línea de texto monoespaciado —
`r₄ = -36.662,73878 / 159.773,26103 = -0,22947` — donde la división es
una barra y no una fracción, los símbolos van en ASCII (`µ_R`, `σ_R`,
`√`), y expresión simbólica, sustitución y resultado comparten renglón.

**Qué revierte.** La sección "Renderizado de fórmulas — HTML plano, no
KaTeX" de esta misma decisión evaluó `katex` + `react-katex`, lo descartó
por peso de bundle, y dejó escrito que el HTML plano "alcanza para las 8
fórmulas de Etapa 1 (todas son expresiones de una línea)", con KaTeX a
reevaluar "recién si Etapa 2 lo pide".

**Evidencia nueva que mueve el criterio.**

1. **El pedido no es estético, es docente.** METIS es un software con
   enfoque de enseñanza y la fórmula sustituida *es* el producto de la
   pantalla de resultados en modo paso a paso, no su decoración. Un
   docente que compara la pantalla contra la tesis de Facundo necesita
   ver la fracción como fracción. "Alcanza con que se entienda" es un
   piso más bajo que el que corresponde acá.
2. **Etapa 2 lo iba a pedir igual.** Log-Pearson III y GVE tienen
   sistemas de ecuaciones y cuantiles con exponentes anidados que no
   entran en una línea de texto monoespaciado ni con `<sub>`/`<sup>`. La
   condición que esta decisión puso para reevaluar ("recién si Etapa 2 lo
   pide") se iba a cumplir en el próximo bloque de trabajo sobre el modo
   paso a paso — traerlo ahora paga la deuda una sola vez en vez de dos.
3. **El criterio "código propio y chico antes que una dependencia
   grande" (045/051/056/063) no aplica igual acá.** En esos casos había
   una alternativa propia *equivalente en resultado*: un fondo animado en
   Canvas 2D se ve igual que uno en Three.js; un gráfico en SVG + d3-scale
   se lee igual que uno de Recharts. Para notación matemática de calidad
   tipográfica no hay equivalente propio chico — reimplementar el layout
   de fracciones/raíces/subíndices de KaTeX es un proyecto, no un
   componente. KaTeX (LaTeX, MIT, estándar de facto) es exactamente la
   clase de dependencia que sí se justifica: hace algo que no se puede
   hacer chico y bien a mano.

**Costo real, medido (no estimado).** `npm run build`, antes y después,
misma rama:

| | JS inicial (gzip) | CSS inicial (gzip) | Chunk lazy (gzip) |
|---|---|---|---|
| Antes (F1/F2/F4 aplicados) | 136,63 kB | 8,95 kB | — |
| Después (F3) | 138,17 kB | 8,99 kB | `katex` 77,50 kB JS + 8,01 kB CSS |

- **Impacto en el bundle inicial: +1,58 kB gzip** (el componente
  `BlockMath` y su cargador). No +70 kB como estimaba esta decisión.
- KaTeX se carga con `import()` diná­mico — chunk aparte
  (`src/components/BlockMath.tsx`), **fuera del bundle inicial**. Se
  descarga solo cuando un usuario abre un resultado de Etapa 1 en modo
  paso a paso (CU-01). CU-02, CU-03 y el primer render de cualquier
  pantalla no pagan nada. Mismo patrón de code-splitting que el addendum
  de [DECISIÓN 045](decision045.md) usó para acotar Three.js en la puerta
  de entrada.
- KaTeX trae además sus fuentes web (~20 archivos woff2/woff/ttf, ~1 MB
  sin comprimir en total pero servidas por separado y perezosamente): el
  navegador baja solo la familia que cada glifo necesita, y solo cuando
  la fórmula se pinta. No entran a ningún bundle.
- Vite dejaba de emitir el warning de "chunk > 500 kB" con este cambio
  aplicado — antes de code-splitear, el bundle único llegaba a 667 kB
  (215 kB gzip).

**Licencia.** KaTeX es MIT (`node_modules/katex/package.json`), como el
resto de las dependencias del frontend.

### Lo que NO cambia — sigue siendo la parte no negociable

La regla central de esta decisión se mantiene entera: **`core/` calcula,
el frontend solo renderiza.** El frontend sustituye los `terminos` que
`TestResult.explicacion` ya trae calculados, nunca deriva un estadístico
nuevo. La única aritmética cosmética permitida sigue siendo la que ya
existía — reconstruir el denominador `Sp·√(1/n₁+1/n₂)` de t de Student
para mostrarlo (`explicaciones.ts`), porque no viaja en `terminos`. El
paso "resultado" de cada fórmula usa `tr.estadistico`/`tr.valor_critico`
tal como los emitió `core/`, no un valor recalculado a partir de la
sustitución.

Mann-Kendall sigue sin fórmula inventada para la tipificación con
corrección por empates (`formulas-etapa1.md` §7 no deja una citable): el
paso LaTeX muestra `S` y `Var(S)` y nombra la corrección en `\text{}`,
igual que la versión de texto plano.

### Implementación

- `katex@0.16.22` (exacto), `@types/katex@0.16.8` (exacto, dev). Sin
  `react-katex` — arrastra `prop-types` y es una capa fina sobre
  `katex.renderToString()` que no justifica dos dependencias más. El
  wrapper es local: `src/components/BlockMath.tsx` (~50 líneas, incluido
  el cargador diná­mico y el fallback).
- `i18n/explicaciones.ts` gana `formatearFormulaLatex()` — devuelve la
  fórmula en pasos (`PasoFormula[]`: expresión simbólica → sustitución
  numérica → resultado; Cramer devuelve simbólica + los dos bloques).
  Cada paso trae su `latex` **y** su `fallback` de texto plano.
  `formatearFormula()` (la versión de texto de una línea) **se conserva
  sin cambios** — es de donde sale el `fallback` de cada paso, y sus
  tests siguen verificando que el número sustituido es el correcto. No se
  reescribieron esos asserts a LaTeX: se agregaron asserts nuevos sobre
  `formatearFormulaLatex()` que verifican lo mismo sobre la cadena LaTeX
  real (`\dfrac{4378{,}38600}{12254{,}30800}`, `r_{9} = 0{,}35734`, etc.).
- `Etapa1ResultView.tsx` renderiza cada paso con
  `<BlockMath math={paso.latex} fallback={paso.fallback} />` en bloque
  (displayMode), alineado a la izquierda, un paso por línea. El `Ec. III-1`
  de trazabilidad a la tesis queda debajo, sin cambios. Modo experto no
  se toca.
- **Fallback en dos niveles:** mientras el chunk de KaTeX viaja, y si
  `katex.renderToString` tira (`throwOnError: true`), `BlockMath`
  muestra el `<code>` de texto plano — la pantalla nunca queda en blanco.
- Rama `no_ejecutada` (sin `explicacion`) intacta: `formatearFormulaLatex`
  devuelve `null` y la vista muestra el motivo, sin fórmula vacía.

### Criterio de hecho — addendum

- `i18n/explicaciones.test.ts` — 10 tests nuevos sobre
  `formatearFormulaLatex()` (los 8 tests, la rama `null`, y que cada paso
  trae `latex` + `fallback`); los 9 tests de `formatearFormula()` sin
  tocar.
- `Etapa1ResultView.test.tsx` — el test de "modo paso a paso muestra la
  fórmula" pasa a esperar el `.katex` renderizado (`waitFor`, por el
  `import()` diná­mico) y verifica que el `<annotation>` MathML lleva el
  LaTeX con los términos sustituidos.
- `npx tsc -b`, `npm run lint`, `npm test` (351 passed, +10 sobre la
  línea base de este plan de fixes), `npm run build` — todos en verde,
  sin el warning de chunk grande.
- Pendiente al momento de escribir este addendum: verificación en el
  navegador con las 8 pruebas en tema claro y oscuro (Definition of done
  del plan de fixes — se corre después del último commit).
