# Plan rápido de fixes post-verificación (01/10/2026)

**Origen:** la verificación en el navegador del PR #95 (checklist `docs/checklist-pendientes-feedback-directores.md` §1)
salió bien. De esa corrida quedaron cuatro observaciones de Kevin, y en una segunda vuelta (mismo día) sumó dos
pedidos más: ordenar todos los planes de implementación de `docs/` en un único índice y archivarlos, y una serie
artificial con valores negativos para probar "Otro". Al analizar esa serie apareció un problema en Generalizada de
Pareto que viene de la tesis de Facundo; Kevin decidió mitigarlo en V1.0 y dejar la corrección de fórmulas para la
V2 (Bloque G). **Autor:** Kevin, con Claude.

**Cambio de regla que trae este plan:** Octavio no tiene tiempo para la Tanda 2 de backend del feedback de directores,
así que la hacemos nosotros (decisión de Kevin, 01/10/2026). Queda sin efecto la línea de `CLAUDE.md` que dice "no tocar
`backend/` por ese plan sin que Octavio lo haya visto". Todo lo que se haga en `backend/` sigue el estilo del resto del
backend (capas, `core/` puro, códigos de error por catálogo, decisiones numeradas) y se documenta igual que si lo
hubiera hecho él. Recomendación: sumarlo como reviewer de los PRs de backend para que sepa qué cambió en su capa,
sin esperar su aprobación para avanzar salvo que el Ruleset la exija.

---

## 0. Diagnóstico antes de tocar nada

### D1. El botón "Otro" funciona: lo que engaña es el texto

La serie de la corrida tiene **mínimo 83,00**: no tiene ningún valor negativo. Las cinco distribuciones que nombra la
nota (LN2p, LP3, Gamma 2p, Exponencial β, Gen. Exponencial) solo quedan fuera cuando **la serie tiene negativos**, no
cuando se elige "Otro". Verificado en el código:

- Etapa 2 decide por los datos, nunca por `tipo_variable`: cada distribución devuelve `no_aplicable` con
  `serie <= 0` (`lognormal2p.py:41`, `logpearson3.py:69`, `gamma2p.py:60`, `exponencial_beta.py:37`) o `serie < 0`
  (`gen_exponencial.py:98`). `ejecutar_etapa2` ni siquiera recibe el tipo de variable.
- `tipo_variable` solo cambia dos cosas: el warning `CONTRACT_NEGATIVE_VALUES` (`contract.py:90`, solo con
  Caudal/Precip.) y qué código reporta Chow ante ceros (`outliers.py:17`).
- Conclusión: **sin negativos ni ceros, "Otro" y "Caudal/Precip." producen exactamente el mismo análisis.** Con esta
  serie, que se vieran las 13 distribuciones es el comportamiento correcto.

Lo que sí está mal, y es lo que este plan arregla:

1. La nota de `ConfigPage` se lee como "elegir Otro saca estas distribuciones". Tiene que decir "si la serie tiene
   negativos".
2. Aun con negativos de verdad, una distribución sin ningún ajuste posible se dibuja **igual que las demás**: misma
   card, sin atenuar, con la línea "Mejor ajuste" vacía (sin método ni EEA). Ya va al fondo (el backend ordena con `mejor_eea` nulo al final),
   pero no se distingue.
3. Su estado dice "no aplicable" genérico, indistinguible de un fallo numérico, porque el backend todavía no emite
   `disabled_negatives` (bloque C del plan de backend).

Para verificarlo no había ninguna serie con negativos en `docs/series prueba/`: ya está creada (ver F3 y D5).

### D2. El panel de exclusión

Hoy (`Etapa1ExclusionPanel.tsx`): un `<fieldset>` con scroll propio de 220 px que muestra unos 12 de los 39 años; año
y valor pegados con la misma tipografía y el mismo peso; el valor con los 5 decimales de `formatNum` (pensados para las
tablas de resultados, no para elegir un punto); y nada que permita comparar valores de un vistazo, que es justamente lo
que hace falta para encontrar un atípico. Las notas (hueco interior, menos de 10 datos, archivo agregado) se apilan
como párrafos sueltos.

### D3. La nota de tipo de variable

Es estática (`ConfigPage.tsx:550-566`): explica las dos opciones a la vez y se muestra siempre, con cualquiera de las
dos seleccionada. El mismo formulario ya resuelve esto bien en otro lado: la nota de "mes de inicio del año" cambia
según el caso (`serieYaEsAnual`).

### D4. Qué backend hace falta para lo que Kevin vio

| Bloque (plan de backend del 21/09) | Lo que destraba | ¿Entra en este plan? |
|---|---|---|
| **C** `disabled_negatives` | El estado correcto en el punto 3 | **Sí** |
| **E** `Explicacion.desglose` | Correlograma de Anderson y desglose de Chow | **Sí** |
| **A** `simulate-exclusion` | Botón "Recalcular" y la comparación | **Sí** |
| **B** exploración sin id (CU-02) | Explorar distribuciones en modo anónimo | No: Kevin no lo pidió. Queda en el checklist |

El ranking simulado del bloque A se muestra de solo lectura (`Etapa1Comparacion.tsx:182`, `modo="lectura"`), así que
A **no depende de B**.

### D5. Lo que mostró la serie con negativos (ya creada, ver F3)

Corrida directa contra `core/` (no por HTTP) con `serie_con_negativos_otro.csv`, el 01/10:

- **Confirma D1:** con "Otro", Etapa 1 corre entera (Anderson, Wald-Wolfowitz, Helmert, t de Student, Cramer,
  Mann-Kendall y KS aprueban), Chow queda `no_ejecutada` con `TEST_NOT_EXECUTED_CONDITION`, y en Etapa 2 las cinco
  distribuciones quedan con todos sus métodos en `no_aplicable` y `mejor_eea` nulo, al final del ranking. Con
  "Caudal/Precip." el resultado es el mismo más el warning `CONTRACT_NEGATIVE_VALUES`.
- **Dos cosas que aparecieron con esta serie:**
  1. **`DIST_HIGH_EEA` con "Otro".** El umbral es el 5 % de la media (DECISIÓN 070). En una variable referida a un
     cero arbitrario (un nivel de escala, una anomalía) la media puede estar cerca de cero y el porcentaje deja de
     significar algo: con esta serie (media ≈ 0,99) las **19 de 19** combinaciones ajustadas lo disparan, incluida
     la de menor EEA (≈ 9 % de la media). No se cambia el umbral (es regla de negocio cerrada): va a
     `docs/pendientes-tecnicos.md` y como pregunta para los directores, junto con la de "Otro" del checklist.
  2. **Generalizada de Pareto da EEA absurdos.** Investigado a fondo el mismo día: son tres inconsistencias de la
     sección IV.3.10 de la tesis (el código la copia fielmente), no los negativos. Diagnóstico, impacto y lo que se
     hace en V1.0 en el **Bloque G**.

---

## 1. Decisiones que antes eran de Octavio (§5 del plan de backend)

Con la recomendación que tomo como default si no decís otra cosa:

| # | Pregunta | Default propuesto | Por qué |
|---|---|---|---|
| 1 | A: ¿`etapa2` en la misma respuesta o endpoint aparte? | **Misma respuesta** | `ejecutar_etapa2` tarda ~40 ms; un solo request; el frontend ya está hecho así |
| 2 | A: ¿tope de valores? | **500** | Misma cota que se propuso para B; un análisis anual real no pasa de ~150 |
| 3 | A: ¿`anios` como enteros o timestamps? | **Enteros** | Es lo que el frontend ya manda y lo que `parsear_timestamps` entiende |
| 4 | E: ¿qué pruebas tienen desglose? | **Anderson y Chow** | Son las dos únicas que `Etapa1Desglose.tsx` renderiza; Wald, Helmert y el resto quedan para después |
| 5 | C: ¿código propio para Chow con negativos? | **Sí, `TEST_NOT_EXECUTED_NEGATIVES`** | La nota de `ConfigPage` promete que Chow no corre con negativos; hoy el motivo se pierde dentro de `TEST_NOT_EXECUTED_CONDITION` |
| 6 | ¿Promover los scripts de regresión a `tests/regression/`? | **No en este plan** | Se usan como verificación fuera del repo (Apéndice C). Promoverlos es un PR propio |
| 7 | Valor crítico de Chow (una cola vs. dos) | **Sin acción** | Fuera de alcance, sigue como pregunta abierta |

Números de decisión: el máximo en `origin/staging` hoy es **070** (verificado con `git fetch` el 01/10). Se usan
**071** (exclusión), **073** (negativos) y **074** (Generalizada de Pareto, Bloque G), más el addendum fechado a
**064** (desglose). **072** queda reservado para el bloque B, que no entra acá: no reutilizarlo. Antes de escribir cada archivo, volver a hacer `git fetch`.

---

## 2. Bloque F: frontend que no espera backend

### F1. Rediseño del panel "Excluir puntos de la serie"

**Archivos:** `src/routes/results/Etapa1ExclusionPanel.tsx`, `Etapa1ExclusionPanel.css`.
**No cambia:** `exclusiones.ts` (lógica pura), el estado en `Etapa1GraficosView`, el clic sobre los gráficos.

Propuesta: reemplazar la lista con scroll por una **grilla por década**, que funciona a la vez como selector y como
mini gráfico de barras.

- **Una fila por década**, rotulada a la izquierda (`1980`, `1990`…), con **10 columnas fijas** alineadas por el
  último dígito del año. Los años fuera de la serie quedan como celda vacía, así 1985 siempre está en la misma
  columna que 1995. Con 39 años son 5 filas: entra entera, **sin scroll interno**.
- **Cada celda es un `<button aria-pressed>`** (el mismo patrón que los `.seg` del resto de la app) con el año chico
  y apagado arriba, y el valor abajo con `formatAxis` (hasta 2 decimales, no 5).
- **Una barra fina en el fondo de cada celda**, de altura proporcional al valor entre el mínimo y el máximo de la
  serie. Es lo que permite ver el atípico sin leer números, que es para lo que existe el panel.
- **Excluido:** la celda pasa a contorno hueco con el valor tachado, el mismo lenguaje visual que el punto hueco de
  los gráficos de arriba. **Sugerido por Chow:** borde `--warn` y una marca chica, con una leyenda de una línea debajo
  de la grilla (hoy es una píldora que estira la fila).
- **Encabezado:** título a la izquierda y el estado a la derecha como chip ("2 de 39 excluidos · quedan 37"). Se
  conserva el `<output>` para que el lector de pantalla siga anunciando el conteo.
- **Notas** (hueco interior, menos de 10 datos, archivo agregado): un solo bloque de avisos debajo de la grilla, que
  aparece **solo cuando hay algo seleccionado**. La de "archivo agregado" hoy se muestra siempre que el origen es
  mensual o diario, aunque no haya nada excluido.
- **Acciones** en una fila al pie: "Limpiar" como botón terciario a la izquierda; a la derecha "Descargar CSV" y,
  cuando exista el backend, "Recalcular sin estos puntos" como primario.
- **Angosto (< 560 px):** 5 columnas por fila (cada década ocupa dos filas). Sin scroll horizontal.
- **Accesibilidad:** cada fila es un `role="group"` con `aria-label` de la década; cada botón lleva
  `aria-label="1984, 122,87, excluido"` (o "incluido"). Se navega con Tab como hoy; las flechas entre celdas quedan
  fuera para no sumar un manejador de foco propio.

**Tests:** los tres archivos que hoy buscan `checkbox` (`Etapa1GraficosView.test.tsx`,
`Etapa1GraficosView.simulacion.test.tsx`, `ResultsPage.simulacion.test.tsx`) pasan a buscar
`button` con `aria-pressed`. Nuevos: celdas vacías para los años fuera de la serie; altura de barra en el mínimo y el
máximo; el aviso de archivo agregado no aparece sin selección. Con `it.each` para no sumar duplicación en Sonar.

### F2. Nota de tipo de variable: solo la de la opción elegida

**Archivo:** `src/routes/config/ConfigPage.tsx` (~550-566).

Se descartó el pop-up: el proyecto no tiene ningún componente de popover, habría que hacerlo accesible desde cero
(foco, Escape, lector de pantalla) y esconde justo la información que el usuario necesita para elegir. En su lugar,
**una nota por opción**, como ya hace "mes de inicio del año":

- **Caudal/Precip.** (una línea): "METIS avisa si la serie tiene valores negativos, que en un caudal o una
  precipitación no existen."
- **Otro** (solo con "Otro" seleccionado): "Un valor negativo se toma como dato válido (por ejemplo, una temperatura
  bajo cero). **Si la serie tiene alguno**, Chow no se ejecuta y cinco distribuciones de Etapa 2 no se pueden ajustar:
  aparecen al final del ranking, marcadas como no aplicables. Si la serie no tiene negativos, el análisis es el mismo
  que con Caudal/Precip."

La nota del caso Caudal sobre ceros en Chow se saca de acá: es un detalle de una prueba que ya se explica en
resultados. **Test:** la nota de "Otro" no está en el documento con "Caudal/Precip." seleccionado, y aparece al
cambiar.

### F3. Distribuciones sin ningún ajuste posible: atenuadas y separadas al fondo

**Archivos:** `src/routes/results/Etapa2RankingView.tsx` y `.css` (lo comparten el stream, `ResultsPage`,
`HistoryDetailPage` y el explorador, así que se arregla en un solo lugar).

- Una distribución **sin ningún método `ok`** (`mejor_metodo === null`) se renderiza con una variante
  `etapa2-card--sin-ajuste`: opacidad y saturación bajas, sin brillo de spotlight, y una píldora con el motivo en
  lugar de la línea "Mejor ajuste" vacía. El motivo sale de los `status` de sus métodos: si todos son
  `disabled_negatives`, "no aplica: la serie tiene valores negativos"; si todos son `disabled_zeros`, "deshabilitada
  por ceros"; si no, "sin ajuste posible con esta serie".
- **No se ocultan.** Los métodos que fallaron "son la mitad de lo que un alumno tiene que ver" (comentario vigente en
  el propio archivo) y la tesis reporta combinaciones que no ajustan. Se separan: al expandir "Ver las N restantes",
  van bajo un subtítulo propio "Sin ajuste posible con esta serie (5)". El botón de expandir cuenta las dos cosas por
  separado: "Ver las 4 restantes · 5 sin ajuste".
- **El frontend no reordena** (regla vigente desde F3 del 14/08): solo se parte la lista que ya viene ordenada. Si un
  día el backend devolviera una sin ajuste en el medio, se respeta el orden y solo cambia el estilo.
- Esto vale también para ceros, no solo negativos.

**Serie de prueba: ya creada (01/10).** `docs/series prueba/serie_con_negativos_otro.csv`: 40 años (1980 a 2019),
columnas `anio,nivel_m`, **sintética** (normal con media 0,6 y desvío 0,9, semilla fija `20261001`, redondeo a 2
decimales). Simula el nivel máximo anual de un río referido al cero de escala, una variable donde un negativo es un
dato real. Tiene **5 negativos** (1989: -0,36; 2005: -0,21; 2006: -0,74; 2015: -0,29; 2019: -0,37), ningún cero,
mínimo -0,74 y máximo 2,88. Verificada pasando por `parse_file` (el mismo camino que una subida real): se infiere
resolución anual, se leen los 40 valores con sus negativos y el resultado es el descrito en D5. Para probarla:
columna X `anio`, columna Y `nivel_m`, tipo de variable "Otro", alcance Etapa 1 y 2.

Ojo: **la carpeta `docs/series prueba/` no está versionada** (no figura en git ni en `.gitignore`), así que la serie
hoy existe solo en tu máquina. En PR 1 conviene versionar las series sintéticas con un `README.md` corto que diga cuál
es sintética y qué prueba cada una. `UCC-DAT-ESR-AH-001-26-00.xlsx` queda afuera hasta confirmar que se puede
publicar en el repositorio.

**Tests:** una distribución con todos sus métodos `disabled_negatives` tiene la clase atenuada y la píldora correcta;
una con un método `ok` no; el conteo del botón separa las dos cosas.

---

## 3. Bloque B: backend (lo que era de Octavio)

Los contratos completos ya están en `docs/plan-backend-feedback-directores-20-09-2026.md` (§1, §3, §4). Acá va solo
lo que cambia respecto de ese documento y el orden.

### B0. Línea base de regresión (antes de la primera línea de código)

Con los scripts del Apéndice C de `docs/auditoria/hallazgos/hallazgo-timestamps-desalineados.md`
(`extract_series.py`, `regres.py`, `diff.py`), volcar `base.json` de las 9 estaciones sobre `staging` limpio. Después
de cada bloque, `after.json` y `diff.py`: **solo pueden aparecer los campos nuevos de ese bloque**.
Ningún número, veredicto ni valor crítico cambia en ninguno de los bloques. **Excepción esperada del PR 2 (Pareto):**
aparece el campo `pendiente_validacion` y `gen_pareto` pasa al último puesto del ranking en las estaciones donde no lo
estaba (est_02, est_03, est_05, est_09); el orden relativo de las otras 12 y todos los números quedan idénticos.

### C. `disabled_negatives` (chico, primero)

Tal cual §1 del plan de backend: `STATUS_DISABLED_NEGATIVES` en `core/etapa2/types.py`; `DISABLED_WITH_NEGATIVES`
(las cinco) en `distributions/__init__.py`; `ejecutar_etapa2(serie, tiene_ceros=False, tiene_negativos=False)` con
default `False` (lo llaman `services/analysis_service.py:701` y `core/pipeline/full_pipeline.py:70`); precedencia
negativos sobre ceros; `tiene_negativos` en `SessionState` junto a `tiene_ceros`. Más la decisión 5: rama nueva en
`calcular_chow` **antes** del chequeo `arr <= 0` que devuelve `TEST_NOT_EXECUTED_NEGATIVES`; va a `api-contracts.md`
y a `frontend/src/i18n/errors.es.ts` en el mismo commit.

Los análisis ya persistidos conservan su `no_aplicable` de siempre: `recalcular_eventos_diseno` (`/{id}/design-events`) no reajusta, lee el ranking guardado. Sin backfill (mismo criterio que DECISIÓN 058 §4); la card atenuada de F3 los cubre igual con el rótulo genérico.

**Tests:** los de §1 del plan de backend (`pytest.mark.parametrize` con tabla). **Decisión 073.**

### E. Desglose de Anderson y Chow

Tal cual §3 del plan de backend, recortado a dos pruebas (decisión 4):

- `core/types.py`: `Explicacion.desglose: list[dict[str, float | int | bool | None]] | None = None`.
- **Anderson** (`independence.py`): una fila por lag con `k, numerador, r_k, banda_inf, banda_sup, fuera`. La banda
  inferior hoy se recalcula en línea dentro de `lags_fuera` (línea ~42): pasarla a una lista como la superior, **con
  la misma expresión**, y que `lags_fuera` cuente sobre las filas. Así el conteo y el desglose no pueden divergir.
- **Chow** (`outliers.py`): una fila por observación con `i, x_i, ln_x_i, z_i`. Son los `z_scores` que ya se
  calculan para el estadístico.
- Serializar en `test_result_dict()` (`analysis_service.py:116`). Los análisis viejos llegan con `desglose: null` y la
  UI ya degrada sola (sin backfill, DECISIÓN 058 §4).
- **Claves:** son exactamente las que espera `Etapa1Desglose.tsx` y su fixture (`simulacionFixtures.ts`). Si alguna
  cambia, se ajusta el frontend en el mismo PR.

**Tests:** las 9 series con veredictos y estadísticos idénticos; la fila del lag reportado coincide con
`terminos.k`/`estadistico`; `sum(fuera) == lags_fuera`; en Chow, `max(z_i) == estadistico`. **Addendum fechado a
`decision064.md`** ("core expone, frontend renderiza" no cambia; se amplía qué expone). Medir el payload de una serie
de 40 años antes y después (precedente: DECISIÓN 058).

Fuera de este bloque: `n1_pct`/`n2_pct` de Cramer y el denominador de la t de Student (§3.3 del plan de backend).
Son chicos, pero no son lo que Kevin pidió; quedan anotados en el checklist.

### A. `aplicar_exclusiones()` + `POST /analysis/simulate-exclusion` (el más grande, último)

Tal cual §4 del plan de backend, con las decisiones 1 a 3:

- `core/pipeline/exclusiones.py`: función pura `aplicar_exclusiones(serie, anios, indices_excluidos,
  tratamiento="eliminar")`. Cualquier otro `tratamiento` levanta error (punto de extensión del reemplazo por la media,
  postergado).
- Endpoint en `api/v1/analysis.py` (validación en el borde, sin lógica) que delega en una función nueva de
  `services/analysis_service.py`, siguiendo el patrón de `recalcular_eventos_diseno`: sin `session_store`, sin BD, JWT
  opcional. Corre `ejecutar_etapa1(..., resolucion_temporal="anual")` como la segunda pasada de Chow (sin pausa: un
  atípico nuevo se informa, no detiene nada) y, con `etapas=[1, 2]` y nivel distinto de `rechazado`,
  `ejecutar_etapa2` con `tiene_ceros`/`tiene_negativos` calculados sobre la serie resultante. Serializa con
  `_serializar_etapa1`/`_serializar_etapa2`, así que la respuesta trae también el `desglose` de E.
- Menos de 10 datos tras excluir: el error bloqueante de siempre dentro de `etapa1.contract`. Códigos nuevos:
  `CONTRACT_EXCLUSION_INVALID` y `CONTRACT_SERIES_INVALID` (400), al catálogo en el mismo commit.
- **El flujo de Chow no se toca** (decisión de Kevin del 20/09). La equivalencia se prueba con la regresión 2 del plan
  de backend, no con un refactor.

**Tests:** unitarios de `aplicar_exclusiones` (primero, último, interior, varios, todos, < 10, largos iguales,
`tratamiento` inválido); integración del endpoint (200, 400 por cada código, sin cookie responde igual);
**regresión 1** (`[]` da Etapa 1 idéntica a la original en las 9 series) y **regresión 2** (excluir el atípico da lo
mismo que "rechazar" en el flujo de Chow, comparando estadísticos, veredictos y niveles, no `warnings`).
**Decisión 071.**

---

## 4. Bloque R: frontend que se enciende con el backend

- **Con C:** nada obligatorio (`disabled_negatives` ya está tipado y rotulado). Sumar `TEST_NOT_EXECUTED_NEGATIVES` a
  `errors.es.ts` (va en el commit de C).
- **Con E:** confirmar en el navegador que el correlograma y la tabla por lag aparecen con un análisis nuevo y que un
  análisis viejo del historial no muestra nada roto.
- **Con A:** borrar `VITE_SIMULATE_EXCLUSION` y `simulacionExclusionDisponible()` (`api/analysis.ts:52-56`,
  `ResultsPage.tsx:99`); armar el CSV desde `serie`/`anios` de la respuesta cuando hay simulación; mapear los dos
  códigos nuevos. **Opcional:** el botón en `HistoryDetailPage` (hoy solo `ResultsPage` pasa `simular`); necesita
  `tipo_variable` y `cramer_particion` de `detail.configuracion`. Si no sale fácil, queda anotado.

---

## 5. Documentación (en el mismo PR que el cambio que documenta)

- `docs/decisiones/decision071.md`, `decision073.md` y addendum a `decision064.md`; entradas en
  `docs/decisiones/README.md`.
- `.claude/rules/architecture/api-contracts.md`: endpoint `simulate-exclusion`, los tres códigos nuevos, el status
  `disabled_negatives`, el campo `desglose`.
- `.claude/rules/core/statistical-pipeline.md`: `desglose` en el payload de Etapa 1 y el nuevo estado de Etapa 2.
- `CLAUDE.md`: la tabla de endpoints suma `simulate-exclusion`; el párrafo del plan de feedback de directores deja de
  decir "dormido" para A, E y C, y se reemplaza la regla de "no tocar backend sin Octavio" por la decisión del 01/10.
  **Antes de editarlo, commitear o descartar el cambio local que ya tiene `CLAUDE.md`** (está modificado y sin
  commitear en `staging`).
- `docs/checklist-pendientes-feedback-directores.md`: tildar C, E y A con fecha; B, Cramer `n_pct` y t de Student
  siguen abiertos.
- `.claude/rules/sprint.md`: una sección corta para este plan, no más (pesa ~97 KB).
- `docs/pendientes-tecnicos.md`: el hallazgo de `DIST_HIGH_EEA` de D5 y la fila de Pareto para V2 (G2).

---

## 5b. Bloque G: Generalizada de Pareto (mitigación en V1.0, corrección en V2)

**Decisión de Kevin (01/10/2026):** no corregir las fórmulas en V1.0. Se mitiga en pantalla para que ningún usuario
pueda elegir un resultado que sabemos que está mal, y se documenta con el detalle suficiente para que Octavio lo
corrija en la V2 (que se presenta con su tesis) sin tener que rehacer el diagnóstico. Postura ante el tribunal:
**METIS es fiel a la fuente, detectó la inconsistencia, la midió, la contuvo y la dejó documentada.**

### G0. El diagnóstico (lo que tiene que quedar escrito)

Verificado contra el PDF de la tesis (`Bibliografia/Facundo/Tesis de Maestria/`, páginas 73 a 76 del PDF, ecuaciones
IV-145 a IV-174). Las tres cosas están **impresas así en la tesis**; el código las reproduce fielmente.

1. **Dos convenciones de signo mezcladas (afecta a los cuatro métodos).** La Pareto Generalizada se escribe en dos
   convenciones con el parámetro de forma de signo opuesto: la de Hosking (k; con k > 0 la distribución tiene techo) y
   la de Coles (ξ = -k; con ξ > 0 la cola es pesada). En la tesis:
   - **Convención de Hosking (k):** Momentos (IV-147 a IV-149: media `µ + σ/(1+ε)` y la asimetría de IV-148), Máxima
     Verosimilitud (IV-150: `((1-ε)/ε)·Σ ln(1 - ε(x-µ)/σ)`), Mínimos Cuadrados (`z = (1-F)^ε`) y Momentos de
     Probabilidad Pesada (IV-168, IV-169).
   - **Convención de Coles (ξ):** la función de distribución IV-146, `F = 1 - (1 + ε(x-µ)/σ)^(-1/ε)`, y el cuantil
     IV-174, `x = [(1/(1-F))^ε - 1]·σ/ε + µ`.
   - Consecuencia: METIS estima ε con un significado y calcula los eventos de diseño con el contrario. Con ε > 0 el
     modelo estimado tiene techo, pero IV-174 lo evalúa como de cola pesada y los cuantiles altos explotan.
   - Cuantil coherente con los estimadores: `x = µ + (σ/ε)·[1 - (1-F)^ε]`.
2. **IV-167 (Momentos de Probabilidad Pesada) tiene el signo del numerador cambiado.** La tesis imprime
   `ε = (n·I1 + 2·I2·(n-1)) / (I2·(n-1) - I1)`. Despejando ε de las propias IV-168 a IV-171 de la tesis (que son
   consistentes con Hosking):
   - `E[x(1:n)] = µ + σ/(n+ε)` (el mínimo de n valores de una Pareto de Hosking es otra Pareto con σ/n y ε/n), así que
     `I1 = M0 - x1 = σ(n-1) / ((1+ε)(n+ε))`.
   - `α0 = µ + σ/(1+ε)` y `α1 = µ/2 + σ/(2(2+ε))`, así que `I2 = M0 - 2·M1 = σ / ((1+ε)(2+ε))` (de acá sale IV-168).
   - `I1/I2 = (n-1)(2+ε)/(n+ε)`, que despejado da **`ε = (n·I1 - 2·I2·(n-1)) / (I2·(n-1) - I1)`**.
3. **Mínimos Cuadrados no recupera el parámetro (la causa es la menos segura de las tres).** IV-153, tal como quedó
   transcrita en la DECISIÓN 068, tiene una sola raíz, cerca de ε = 1, sea cual sea la serie. Un ajuste de mínimos
   cuadrados común (x contra z(ε)) sí recupera el parámetro. Además IV-155, `µ = x1 - (ε/µ)·(1 - z1)`, no es
   dimensionalmente consistente (resta 1/unidad a un valor con unidades); lo coherente con `x = µ + (σ/ε)(1 - z)`
   evaluado en i = 1 es `µ = x1 - (σ/ε)·(1 - z1)`, lo que también explicaría el "valor inicial de µ" de IV-166. Ya
   había una duda abierta sobre este método: `Bibliografia/Facundo/Tesis de Maestria/Dudas/Pareto - Minimos
   Cuadrados.docx`.

**Evidencia** (script en G4; la salida completa del 01/10 está en `.scratch-local/gen_pareto/salida_01-10-2026.txt`):

*Recuperación del parámetro, mediana de 400 muestras simuladas por fila (n = 40, semilla 1):*

| ε real | MPP de la tesis (+) | MPP con signo corregido (-) | Momentos | Mínimos Cuadrados |
|---|---|---|---|---|
| -0,2 | 3,98 | -0,21 | -0,02 | 0,94 |
| 0,1 | 4,28 | 0,06 | 0,18 | 0,97 |
| 0,4 | 4,54 | 0,30 | 0,44 | 0,99 |

Momentos sigue al valor real en la convención de Hosking (confirma el punto 1); MPP con "+" da alrededor de 4 siempre
(punto 2; explica el "ε físicamente implausible en las 9 estaciones" de `consolidacion-e2e.md` §8); Mínimos Cuadrados
da alrededor de 1 siempre (punto 3).

*Impacto hoy en las 9 estaciones (Momentos, que es el único método que a veces da un EEA creíble):*

| Estación | Puesto actual | EEA actual | EEA con cuantil coherente | Mejor de las otras 12 | T=100 actual / coherente | T=500 actual / coherente |
|---|---|---|---|---|---|---|
| est_01 | 13 | 279,54 | 17,56 | 25,26 | 2456,8 / 456,2 | 4863,3 / 503,7 |
| **est_02** | **1 ("menor EEA")** | 16,25 | 24,23 | 20,91 | 684,7 / 517,2 (+32 %) | 964,1 / 657,2 (+47 %) |
| est_03 | 10 | 49,75 | 29,40 | 13,59 | 190,5 / 361,1 | 234,2 / 553,2 |
| est_05 | 2 | 7,18 | 8,88 | 6,33 | 223,3 / 208,0 | 305,9 / 277,9 |
| est_06 | 13 | 28,43 | 5,18 | 5,74 | 325,4 / 129,4 | 530,6 / 150,0 |
| est_09 | 12 | 5229,55 | 3,04 | 2,68 | 11451237,5 / 36,3 | 992588509,7 / 36,3 |

En est_04, est_07 y est_08 Momentos es `no_aplicable` (DECISIÓN 060) y Pareto queda última por MC y MPP, con EEA de
10² a 10⁹. Lectura: en la mayoría de las estaciones el error se ve y nadie elegiría Pareto; **el caso peligroso es
est_02**, donde aparece primera con la etiqueta "menor EEA" y sus eventos de diseño salen inflados entre un 32 % y un
47 %. Al revés, en est_01 y est_06 el cálculo coherente la dejaría como el mejor ajuste y hoy aparece última. Etapa 1 y
las otras 12 distribuciones no se ven afectadas. La tesis marca Pareto como "No converge" en todas sus tablas, así que
**no hay ningún valor de referencia de la tesis que se rompa** al corregirla en la V2.

### G1. Mitigación en V1.0 (sin tocar ninguna fórmula ni ningún número)

**Principio:** Pareto se sigue calculando y mostrando (trazabilidad: "los métodos que fallan son la mitad de lo que
un alumno tiene que ver"), pero **no se puede elegir, nunca lleva "menor EEA" y va al final**. La fuente de verdad es
`core/`; el frontend solo renderiza.

**Backend:**
- `core/etapa2/distributions/__init__.py`: `PENDIENTES_VALIDACION: frozenset[str] = frozenset({"gen_pareto"})`, con
  un comentario que remita a la DECISIÓN 074 y al hallazgo. Mismo patrón que `DISABLED_WITH_ZEROS`.
- `core/etapa2/types.py`: `DistResult.pendiente_validacion: bool = False`.
- `core/pipeline/pipeline_etapa2.py`: poblar el campo y sumarlo **primero** en la clave de orden:
  `(d.pendiente_validacion, d.mejor_eea is None, mejor_eea o inf, d.n_parametros)`. Pareto queda última, después de
  las distribuciones sin ajuste; el orden relativo de las otras 12 no cambia.
- `services/analysis_service.py::_serializar_etapa2()`: serializar `pendiente_validacion` (queda persistido en
  `analysis_results.etapa2`).
- **Elegirla devuelve error:** código nuevo `DIST_PENDING_VALIDATION` (400) en `POST /analysis/distribution-decision`
  y en `POST /analysis/{id}/design-events`. Lo ideal es validarlo en el borde, en `_validar_seleccion_distribucion`
  (`api/v1/analysis.py:287`), importando la constante de `core/` (que `api/` importe de `core/` está permitido; lo
  prohibido es lo inverso). Antes, confirmar con `git grep "from metis.core" metis/api` que ya hay precedente; si no lo
  hay, hacer el chequeo en `services/` con la misma forma que `DIST_METHOD_NOT_FITTED`. El código va a
  `api-contracts.md` y a `frontend/src/i18n/errors.es.ts` **en el mismo commit**.
- **CU-03 (sin implementar):** dejar escrito en la decisión y en `constraints.md` que la selección automática por
  menor EEA tiene que saltear las distribuciones pendientes de validación.

**Frontend** (`Etapa2RankingView.tsx` y `.css`, que comparten stream, resultados, historial y explorador):
- `api/types.ts`: `pendiente_validacion?: boolean` en `DistribucionResult`.
- **Análisis viejos del historial** (persistidos sin el campo, sin backfill): `item.pendiente_validacion ??
  PENDIENTES_VALIDACION_V1.has(item.distribucion)`, con una constante local comentada que explique por qué se duplica
  (es solo el respaldo para datos anteriores a la DECISIÓN 074). Sin esto, un análisis viejo de una serie como est_02
  seguiría mostrando Pareto con "menor EEA".
- Card con variante `etapa2-card--pendiente`: atenuada (mismo lenguaje visual que F3), píldora **"pendiente de
  validación"** y una línea de texto: "No se puede elegir en esta versión: sus fórmulas de referencia tienen una
  inconsistencia que está en revisión con el autor de la tesis." Sin botón "Elegir/Explorar este ajuste" ni botones
  por método; la tabla de métodos con sus EEA sigue visible.
- **"menor EEA"** pasa a ser el primer elemento **no pendiente y con EEA**, no `index === 0`. En análisis nuevos da
  lo mismo (Pareto ya viene al final); en los viejos es lo que evita la etiqueta engañosa. El frontend no reordena: en
  un análisis viejo Pareto queda donde estaba, solo atenuada.
- Junto con F3: se agrupa al final bajo su propio subtítulo, "Pendiente de validación (1)", después de "Sin ajuste
  posible con esta serie". El botón de expandir lo cuenta aparte.

**Tests:**
- Backend (`pytest.mark.parametrize`): con est_02, Pareto queda en el puesto 13 con `pendiente_validacion = True` y el
  resto del ranking en el mismo orden relativo que antes; ningún EEA ni parámetro cambia; `distribution-decision` y
  `/{id}/design-events` con `gen_pareto` dan 400 `DIST_PENDING_VALIDATION`; con cualquier otra distribución, igual que
  antes.
- Frontend: la card pendiente no tiene botones y tiene la píldora; con un ranking viejo sin el campo y Pareto
  primera, la píldora "menor EEA" la lleva la segunda; el subtítulo y el conteo del botón.

### G2. Documentación (con cuidado especial: es lo que va a usar Octavio)

1. **Hallazgo nuevo:** `docs/auditoria/hallazgos/hallazgo-gen-pareto-convenciones.md`, con esta estructura:
   1. **Resumen** en un párrafo: tres inconsistencias, impacto, qué se hizo en V1.0, qué queda para V2.
   2. **Las dos convenciones**, lado a lado (distribución, cuantil, media, varianza, qué significa ε > 0) y **una
      tabla que asigne cada ecuación IV-145 a IV-174 a su convención**. Es la pieza que más tiempo le ahorra a Octavio.
   3. **Problema 1**, con el cuantil coherente y la evidencia.
   4. **Problema 2**, con la derivación paso a paso de G0 (que se pueda seguir con lápiz y papel) y la tabla de
      simulación.
   5. **Problema 3**, separando lo verificado (no recupera el parámetro; IV-155 no es dimensionalmente consistente) de
      lo hipotético (que la ecuación correcta sea un ajuste de mínimos cuadrados común); relación con la DECISIÓN 068 y
      con el `.docx` de dudas.
   6. **Impacto** en las 9 estaciones (tabla de G0), con la lectura de est_02, est_01 y est_06.
   7. **Qué se hizo en V1.0 y por qué no se corrigió** (decisión de Kevin, DECISIÓN 074; corregir es apartarse de la
      tesis y la regla del proyecto exige referencia bibliográfica y aval del director).
   8. **Guía para V2**, paso por paso (ver G3).
   9. **Cómo reproducirlo:** el script de G4 como apéndice, con la salida esperada, mismo formato que el Apéndice C de
      `hallazgo-timestamps-desalineados.md`.
   10. **Referencias:** tesis, páginas 73 a 76 del PDF; Hosking y Wallis (1987), "Parameter and quantile estimation for
       the generalized Pareto distribution", *Technometrics* 29(3), 339-349 (convención k y momentos de probabilidad
       pesada); Coles (2001), *An Introduction to Statistical Modeling of Extreme Values*, Springer (convención ξ).
       **Ninguna de las dos está en `Bibliografia/`:** conseguirlas y verificar las páginas exactas antes de citarlas en
       `formulas-etapa2.md`. No citar de memoria.
2. **`docs/decisiones/decision074.md`** (hacer `git fetch` antes; 072 queda reservado para el bloque B): Pareto
   "pendiente de validación" en V1.0. Alternativas evaluadas: (a) corregir ya, descartada por apartarse de la fuente
   sin aval; (b) dejarla tal cual y solo documentar, descartada porque en est_02 lleva "menor EEA" con eventos de
   diseño inflados; (c) ocultarla, descartada por trazabilidad; (d) **elegida:** calcular, mostrar, no permitir
   elegir, mandar al final y documentar. Consecuencias: orden del ranking, código de error nuevo, respaldo en frontend
   para análisis viejos, regla para CU-03. Condición de cierre: el addendum de la V2. Agregarla a
   `docs/decisiones/README.md`.
3. **`docs/auditoria/pendientes/pendientes-facundo.md`:** sección nueva con tres preguntas concretas: (1) ¿qué
   convención de signo usó para el cuantil, y la de IV-146 es la que corresponde a sus estimadores?; (2) ¿IV-167 lleva
   "-" en el numerador?; (3) ¿cuál es la expresión correcta de IV-153 y de IV-155 (σ/ε en lugar de ε/µ)?
4. **Notas fechadas, sin reescribir lo existente:** `formulas-etapa2.md` §10 (junto a IV-146, IV-155, IV-167 e
   IV-174); `fase1-unitarias.md` §3.10 (decía "verificados, sin hallazgos": lo estaban contra la tesis, que es el
   origen del problema); `consolidacion-e2e.md` §8 (el "estimador mal condicionado" de MPP ya tiene causa);
   `est_01-e2e.md`, hallazgo E; `decision068.md` (addendum: la ecuación transcrita no recupera el parámetro).
5. **`docs/pendientes-tecnicos.md`:** una fila "Corrección de Generalizada de Pareto, V2", que apunte al hallazgo.
6. **`.claude/rules/core/statistical-pipeline.md` y `api-contracts.md`:** el campo `pendiente_validacion` en el
   payload del ranking y el código `DIST_PENDING_VALIDATION`.
7. Guardar el script en el repo: `docs/auditoria/hallazgos/scripts/analisis_gen_pareto.py` (hoy está en
   `.scratch-local/gen_pareto/`, que git ignora).

### G3. Guía para la V2 (va dentro del hallazgo, §8)

1. Confirmar con Facundo las tres preguntas de `pendientes-facundo.md`. Sin su respuesta, corregir los puntos 1 y 2
   igual es defendible con Hosking y Wallis (1987) como referencia; el punto 3 no.
2. Agregar las referencias a `formulas-etapa2.md` §10 y reescribir IV-146/IV-174 en la convención de los estimadores.
3. Cambiar `cuantil()` de `gen_pareto.py` (un solo lugar; el límite ε → 0 no cambia) y el signo de IV-167 en la rama
   `mpp`. Mínimos Cuadrados, solo con la ecuación confirmada.
4. Tests nuevos: recuperación del parámetro en muestras simuladas con semilla fija para cada método (tolerancia
   amplia, es una mediana de 400 muestras); ida y vuelta `F(x(F)) = F` usando la función de distribución en la misma
   convención; las 9 estaciones con la expectativa de G0 (solo cambia Pareto).
5. Sacar `gen_pareto` de `PENDIENTES_VALIDACION` (el mecanismo queda para futuros casos), sacar el respaldo del
   frontend solo si ya no hay análisis viejos que lo necesiten, addendum de cierre en `decision074.md` y nota en el
   hallazgo.
6. Revisar el impacto en el ranking: en est_01 y est_06 Pareto pasaría a ser el mejor ajuste por Momentos.

### G4. Script de reproducción

Ya escrito y corrido el 01/10: `.scratch-local/gen_pareto/analisis_gen_pareto.py` (salida en
`salida_01-10-2026.txt`, al lado). Se corre desde la raíz del repo con
`python .scratch-local/gen_pareto/analisis_gen_pareto.py` y necesita numpy, scipy y pandas (dentro del contenedor del
backend también funciona). Solo lee `core/` y las series de `docs/`; no modifica nada. Imprime las cuatro tablas de
G0 (simulación, raíces de IV-153, EEA por serie, puesto e impacto en eventos de diseño). Si al ejecutar el PR los
números no coinciden con los de G0, **parar y revisar** antes de escribir el hallazgo.

---

## 6. Bloque L: limpieza de los planes de `docs/`

**Pedido:** un único documento que explique qué hizo cada plan de implementación, y sacar los planes de la carpeta
principal. **Archivar, no borrar:** es la regla vigente del propio repo (`docs/README.md`, sección `historico/`:
"nunca se borran, se mueven acá con una nota"), y varios de estos planes son la única justificación escrita de
decisiones que el tribunal puede preguntar. El índice nuevo es lo que se lee; el archivo es lo que se consulta si
hace falta el detalle.

### L1. Inventario (relevado el 01/10 con `git grep`)

| Archivo | Estado | Referencias desde otros archivos |
|---|---|---|
| `frontend/plan-mejora-frontend-pasada2.md` + `informe-pasada2-resultados.md` + `fix-sonarcloud-pr18.md` | Cerrado | 9 / 5 / 0 |
| `frontend/plan-mejora-frontend-pasada3.md` + `informe-pasada3-resultados.md` | Cerrado | 5 / 4 |
| `frontend/plan-limpieza-sonarcloud.md` + `informe-limpieza-sonarcloud-resultados.md` | Cerrado | 1 / 0 |
| `frontend/informe-diagnostico-ui-rota.md` + `plan-arreglo-ui-rota.md` + `informe-resultados-arreglo-ui-rota.md` | Cerrado | 25 / 10 / 4 |
| `frontend/plan-mejora-frontend-pasada4.md` + `informe-resultados-pasada4.md` | Cerrado | 7 / 5 |
| `frontend/plan-mejora-frontend-pasada5.md` + `informe-resultados-pasada5.md` | Cerrado | 4 / 3 |
| `frontend/informe-implementacion-frontend-fase1-6.md` | Cerrado (resumen) | 7 |
| `plan-post-pasada4-roadmap.md` | Cerrado | 5 |
| `plan-etapa2-implementacion.md` | Cerrado (`sprint.md` ya decía "se borra cuando cierren los siete PRs") | 12 |
| `frontend/plan-fixes-pre-reunion.md` | Cerrado, **nunca se commiteó** (está sin versionar) | (sin versionar) |
| `informe-relevamiento-plan-post-avance.md` | Cerrado | 0 |
| `informe-viabilidad-resoluciones-temporales.md` + `plan-resolucion-diaria.md` + `revision-resolucion-diaria.md` | Cerrado (PR #77 a #81) | 4 / 16 / 6 |
| `frontend/plan-fixes-feedback-facundo-02-09-2026.md` | Cerrado (PR #88) | 2 |
| `plan-feedback-directores-20-09-2026.md` | **Activo** | 5 |
| `plan-backend-feedback-directores-20-09-2026.md` | **Activo** (lo ejecuta este plan) | 4 |
| `checklist-pendientes-feedback-directores.md` | **Activo** | 1 |
| `plan-fixes-post-verificacion-01-10-2026.md` (este) | **Activo** | 0 |

**No se archivan** porque no son planes sino documentos vivos: `frontend/frontend-implementation-plan.md` (`CLAUDE.md`
lo cita como fuente de verdad decisión por decisión, §10), `frontend/frontend-integration.md`,
`pendientes-tecnicos.md`, `decisiones/` y `auditoria/`. `frontend/feedback-ux-pendiente-analisis.md` es un
relevamiento: se revisa punto por punto y se archiva solo si todos sus puntos ya se resolvieron en las pasadas 4 y 5.

### L2. El índice: `docs/planes-implementados.md`

Un solo archivo, en orden cronológico, con una tabla resumen arriba y una entrada por **frente de trabajo** (no por
archivo: plan + informe de resultados + revisión van juntos). Cada entrada:

- **Fechas y PRs** (sacados de `git log`, no de lo que dice el plan, porque varios planes quedaron con estados
  atrasados: el checklist de `sprint.md` ya lo advierte).
- **Qué pedía y por qué** (dos o tres líneas).
- **Qué se hizo de verdad**, incluido lo que se descartó (por ejemplo, el panel flotante de F5(a), implementado y
  revertido).
- **Decisiones que salieron** (números de `docs/decisiones/`).
- **Qué quedó abierto y dónde vive ahora.** Regla: **antes de archivar un plan, cada pendiente abierto que tenga
  tiene que figurar en `pendientes-tecnicos.md`, el checklist o `pendientes-facundo.md`**; si no figura, se agrega.
  Archivar no puede ser una forma de que algo abierto desaparezca.
- **Ruta del archivo archivado.**

### L3. Mover y arreglar referencias

- `git mv` (conserva la historia con `git log --follow`) a `docs/historico/planes/`, manteniendo la subcarpeta
  `frontend/` para que los links relativos entre plan e informe del mismo frente sigan funcionando.
- **Script de links rotos, antes y después** (único, fuera de CI): resuelve cada link relativo de markdown en `docs/`,
  `.claude/` y `CLAUDE.md` y lista los que no apuntan a un archivo existente. Se corre antes de mover (línea base: ya
  puede haber links rotos, y esos no son de este bloque) y después: **no puede aparecer ninguno nuevo**.
- Las menciones por ruta en texto plano (no link), incluidos comentarios de código en `backend/` y `frontend/`, se
  actualizan con un reemplazo mecánico de la ruta vieja por la nueva, revisando el diff a mano. El contenido de las
  decisiones no se reescribe: solo cambia la ruta citada.
- `docs/historico/README.md`: una línea que remita a `planes-implementados.md` (no una entrada por archivo, eso ya
  lo tiene el índice). `docs/README.md`: la sección `frontend/` deja de listar los planes uno por uno. `CLAUDE.md`:
  `informe-implementacion-frontend-fase1-6.md` deja de ser el "punto de entrada para retomar" y pasa a serlo el
  índice.

### L4. Cuándo

- **PR 0 (antes que todo):** los frentes cerrados. Es solo documentación, no puede romper nada, y deja `docs/` limpio
  para el resto del trabajo.
- **Último PR de este plan:** los cuatro activos, cuando cierren, con su entrada en el índice. Si al terminar este
  plan queda algo del feedback de directores sin hacer (por ejemplo el bloque B), el checklist sigue activo y no se
  archiva.

---

## 7. PRs: seis, todos desde `staging`

| PR | Rama | Contiene | Toca backend |
|---|---|---|---|
| 0 | `docs/limpieza-planes` | Bloque L para los frentes cerrados + `planes-implementados.md` | No |
| 1 | `fix/ui-post-verificacion` | F1 + F2 + F3 + versionar las series sintéticas | No |
| 2 | `fix/gen-pareto-pendiente-validacion` | Bloque G completo: G1 + hallazgo + DECISIÓN 074 + notas | Sí (chico) |
| 3 | `feature/etapa2-disabled-negatives` | C + su decisión + catálogo | Sí (chico) |
| 4 | `feature/etapa1-desglose-backend` | E + addendum 064 + ajuste de claves si hiciera falta | Sí |
| 5 | `feature/simulate-exclusion` | A + decisión 071 + R (quitar el flag) | Sí |

- **PR 0 primero:** solo mueve documentos, se revisa rápido y evita que los PRs siguientes editen rutas que después
  cambian.
- **PR 1 después:** es lo que Kevin vio en pantalla y no puede romper un número.
- **PR 2 (Pareto) después de PR 1:** los dos tocan `Etapa2RankingView.tsx` (F3 y G1 comparten la agrupación al
  final). Se apila sobre PR 1 y se retargetea a `staging` cuando PR 1 mergee.
- **PR 3 (negativos) después de PR 2:** los dos tocan la clave de orden y `distributions/__init__.py`.
- **PR 4 (desglose) es independiente** de los anteriores.
- **PR 5 se apila sobre PR 3** (usa `tiene_negativos` para Etapa 2 de la simulación) y conviene que entre después de
  PR 4 para que la comparación ya traiga desglose. Se retargetea a `staging` cuando mergee lo anterior. Ese último PR archiva además los planes activos (L4).

**Corte si el tiempo no alcanza:** PR 1, PR 2 y PR 3 cierran las tres observaciones de UI y el riesgo de Pareto. E y A son los que más pesan;
mejor dos PRs de backend cerrados y verificados que tres abiertos a mitad.

## 8. Verificación (no saltear)

- Backend, dentro del contenedor: `ruff check metis/`, `ruff format --check metis/`,
  `pytest -m "unit or integration"`, y el `diff.py` contra la línea base de B0 después de cada bloque.
- Frontend: `npm run lint && npm test && npm run build`.
- PR 0: el script de links rotos sin links nuevos rotos respecto de la línea base; `git grep` de cada nombre de
  archivo movido sin ninguna ruta vieja fuera de `docs/historico/`; y la tabla del índice con una fila por cada
  archivo del inventario L1.
- **Navegador, después del último commit de cada PR** (regla del repo, `testing.md` Capa 4), con la serie anual de
  40 años y con `serie_con_negativos_otro.csv`, en claro y oscuro:
  - PR 1 (con `serie_con_negativos_otro.csv` y "Otro"): grilla por década en ancho normal y angosto; clic en el gráfico marca la celda y viceversa; la nota de
    "Otro" aparece y desaparece; con negativos, las cinco distribuciones al fondo y atenuadas.
  - PR 2: con una serie como est_02 (sacarla de `docs/auditoria/regresion/regresion-pipeline/est_02-pipeline.md` a un
    CSV), Pareto al final, atenuada, sin botones, y "menor EEA" en la Exponencial β; un análisis viejo del historial
    con Pareto primera muestra la etiqueta en la segunda; pedir `gen_pareto` por la API da 400.
  - PR 3: con negativos, las cinco con "no aplica: la serie tiene valores negativos" y Chow con su motivo propio.
  - PR 4: correlograma de Anderson y tabla de Chow en un análisis nuevo; un análisis viejo del historial sin cambios.
  - PR 5: excluir el atípico de `serie_con_atipico.csv`, recalcular, ver la comparación y el ranking simulado;
    descargar el CSV.

## 9. Qué NO cambia

Ningún estadístico, valor crítico ni veredicto. El flujo de Chow. El orden del ranking (lo decide el backend). La
persistencia de CU-01 (simular no guarda nada, DECISIÓN 062). El reemplazo por la media (postergado). El bloque B y
CU-02. El valor crítico de Chow y el de Mann-Kendall. El umbral de `DIST_HIGH_EEA` (D5, solo se anota). Las
fórmulas de Generalizada de Pareto (Bloque G: se contiene en pantalla, se corrige en la V2). El contenido de los planes archivados (se mueven tal cual, con su fecha).
