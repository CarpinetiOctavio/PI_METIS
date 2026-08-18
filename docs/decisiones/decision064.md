# DECISIÓN 064 — Paso a paso docente: `core/` calcula, el frontend renderiza e interpreta

**Fecha:** 18 de Agosto de 2026
**Estado:** Backend aplicado (`feature/paso-a-paso-backend-explicacion`) — el
frontend que consume este contrato es un PR aparte (Bloque D del
[plan post-avance](../plan-post-avance.md)).

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

### Criterio de hecho

- `explicacion.terminos` de cada prueba reconstruye `estadistico` con
  precisión de punto flotante completa (`abs=1e-9`), no solo "en el orden
  de magnitud correcto" — test dedicado por prueba en
  `tests/unit/core/etapa1/`.
- `explicacion is None` para toda rama `no_ejecutada` — test dedicado por
  prueba con esa rama (Wald con `n1=0`, Cramer con `s_global=0`, Mann-Kendall
  con `n<10`, Chow con ceros).
- `pytest -m "unit or integration"` en verde (320 passed, 1 skipped —
  +12 sobre la línea base).

**Ver también:** [DECISIÓN 063](decision063.md) — mismo criterio de
código propio antes que dependencia grande, para el panel acoplable.
`.claude/rules/core/formulas-etapa1.md` — las 8 ecuaciones referenciadas
por `explicacion.ecuacion`.
