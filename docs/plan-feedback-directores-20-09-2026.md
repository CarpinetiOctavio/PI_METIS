# Plan: feedback de directores (20/09/2026)

**Origen:** feedback oral de Carlos Catalini (3 ítems), feedback parcial de Facundo Ganancias
(2 ítems, falta su respuesta al documento de preguntas de Octavio) y un hallazgo propio de Kevin
(1 ítem). Este documento define el **cómo** de cada uno antes de pasarlo a Claude Code.

**Base verificada contra el código** (`8761a31`, staging al 20/09/2026). Cada afirmación sobre el
estado actual cita el archivo donde se comprobó.

---

## 0. Resumen y orden sugerido

| Id | Ítem | Pidió | Toca backend | Decisión nueva | Depende de |
|----|------|-------|--------------|----------------|------------|
| 0 | Arreglo de `timestamps_efectivos` desalineado (§2.0) | Kevin | Sí, `core/` (mínimo) | No | nada — **HECHO 20/09/2026** |
| D | Auditoría de fórmulas LaTeX vs tesis vs core | Facundo | **No** (solo lectura) | No (sí addenda de doc) | nada — **HECHO 20/09/2026**, informe en `docs/auditoria/fases/auditoria-formulas-latex.md` |
| D2 | Correcciones de la auditoría que **no** tocan backend (frontend + doc) | Facundo | **No** | No | D |
| E | Desglose paso a paso (los k lags de Anderson, etc.) | Kevin | Sí, aditivo en `core/` | Addendum a 064 | D |
| F | Gráficos propios por prueba (correlograma, etc.) | Facundo | Sí, mismo cambio que E | Addendum a 064 | E |
| B | Probar otras distribuciones desde la pantalla de resultados | Catalini | Sí, endpoint nuevo stateless | Nueva (extiende 062) | nada — **Tanda 1 hecha 21/09/2026 (CU-01)**; falta CU-02 (Tanda 2) |
| A | Excluir atípicos clickeando el gráfico + resultados "sin ellos" + descarga | Catalini | Sí, `core/` + endpoint nuevo | Nueva (071) | B (Fase 0 ya hecha) — **A1 (selección + descarga CSV) y A2 (recalcular + vista comparativa, contra un mock del contrato, apagado por `VITE_SIMULATE_EXCLUSION`) hechas 21/09/2026**; falta el backend |
| C | Tratamiento de valores negativos con tipo "Otro" | Catalini | Sí, `core/` | Nueva (073) | nada |

**Orden de ejecución: 0 → D → D2 → E → F → B → A → C.**

**Restricción (Kevin, 20/09/2026): todo lo que toque `backend/` se implementa al final, después de
consultarlo con Octavio.** La única excepción fue la Fase 0. En consecuencia, el orden real de
trabajo es en dos tandas:

- **Tanda 1 (sin backend):** D2, y de B, A, E y F todo lo que se pueda hacer solo en frontend
  (componente `Etapa2Explorador`, `onPointActivate` en `InteractiveChart`, lista de checkboxes,
  correlograma sobre los datos que ya existen), con el contrato del backend acordado pero mockeado
  en los tests.
- **Tanda 2 (backend, tras hablar con Octavio):** `Explicacion.desglose` y campos aditivos en
  `terminos` (E), endpoint stateless de distribuciones (B), `aplicar_exclusiones` +
  `simulate-exclusion` (A), `disabled_negatives` (C).

Ver §5, "Resultado (20/09/2026) y reparto de los hallazgos", para el detalle por hallazgo de la
auditoría.

- D primero porque es solo lectura y cualquier error que encuentre en una fórmula se arrastraría a
  E y F si se construyen antes.
- E y F comparten el mismo cambio de backend (exponer el detalle por paso que `core/` ya calcula y
  hoy descarta), así que van juntos.
- B antes que A porque el recálculo de Etapa 2 dentro de A necesita el mismo endpoint stateless
  que B introduce.
- C es independiente del resto; puede ir en paralelo con cualquier fase.

---

## 1. Preguntas a cerrar con los directores antes de codear

Ninguna de estas se puede resolver desde ingeniería de software. Conviene mandarlas juntas.

**Para Catalini (ítems A y C):**

1. **"Tapar con la media" vs "eliminar": ¿qué significa "punto extremo"?** Lectura propuesta:
   *extremo temporal* (primer o último año de la serie), no *extremo en valor*. Justificación: un
   hueco interior rompe el espaciado anual del que dependen Anderson (lags), Wald-Wolfowitz
   (rachas), Cramer (bloques) y Mann-Kendall (orden); en un borde no hay nada que se corra. Es la
   misma asimetría extremos/interior que ya usa DECISIÓN 065. Confirmar.
2. **¿La media de qué?** Propuesta: media de la serie efectiva **excluyendo todos** los puntos
   desactivados (no la media de los vecinos, no la media con el atípico adentro).
3. **¿Etapa 2 corre sobre la serie imputada o sobre la serie sin el punto?** Esta es la pregunta
   más importante. Imputar con la media tiene sentido para las pruebas de Etapa 1 que dependen del
   orden, pero para el análisis de frecuencia un valor medio inventado entra como si fuera un
   máximo anual observado: altera los momentos-L, las posiciones de graficación y el tamaño
   muestral. "Resultados como si el atípico nunca hubiera estado" sugiere **Etapa 1 sobre la serie
   imputada, Etapa 2 sobre la serie sin el punto**. Proponerle esto explícitamente.
4. **¿El flujo actual de Chow ("rechazar atípico") debe adoptar la misma política?** Hoy rechazar
   **borra** el dato siempre, aunque sea interior (`analysis_service.py`, `del
   serie_filtrada[indice_real]`). Si la política nueva es "interior → media", mantener el borrado
   en el flujo de Chow deja dos criterios distintos para la misma operación en el mismo producto.
5. **Negativos (ítem C):** ¿qué variables tiene en mente para "Otro"? (niveles referidos a un cero
   de escala, temperaturas, anomalías). Y concretamente: ¿"tratarlos" es (a) trasladar la serie,
   (b) correr Chow sin logaritmos, o (c) dejar operar solo las distribuciones que admiten negativos
   y explicarlo? Ver el análisis en §4.

**Para Facundo (ítem F), sumar al documento de Octavio:**

6. De la tabla de §7, ¿qué gráficos considera necesarios para decidir y cuáles son accesorios?
7. **Mann-Kendall, valor crítico (hallazgo H-2 de la auditoría, 20/09/2026).** La Tabla A.4 del
   apéndice de Caamaño & Dasso da `V_crít = 1,64` para α = 0,05 (una cola); METIS usa 1,96 (dos
   colas, lo que decide `pymannkendall`). ¿Se mantiene 1,96 y se documenta la divergencia con la
   tabla, o se alinea con la fuente? Hasta que responda **no se cambia ningún valor**; D2 solo
   documenta la divergencia y corrige la prosa de la pantalla.

---

### Respuestas registradas (Kevin, 20/09/2026)

- **Preguntas 1 a 4, cerradas:** "extremo" = primer o último dato. El what-if **elimina** los
  puntos excluidos en cualquier posición, para las dos etapas, que es el criterio vigente del
  código (§2.0). El reemplazo por la media queda postergado: se muestra la versión implementada a
  los directores y se decide con su feedback. El flujo de Chow no se modifica. Detalle en §2.
- **Pregunta 5, cerrada:** opción 3 de §4 (estado propio `disabled_negatives`).
- **Restricción de proceso (Kevin, 20/09/2026):** los cambios que toquen `backend/` se dejan para
  el final y se consultan primero con Octavio; la Fase 0 fue la única excepción autorizada.
- **Chow, valor crítico (H-6 de la auditoría): se deja como está.** La auditoría encontró que el
  código usa un test bilateral al 10% (K_N(30) = 2,745) y que, según lo que se recuerda de la
  tabla del Bulletin 17B, esta traería 2,563. No se verificó contra el original (no está en el
  repo). Kevin decide no tocarlo: Octavio probablemente ya lo controló. **No se modifica
  `outliers.py` ni se abre decisión.** Lo único que se corrige de H-6 es el rótulo de α en la
  pantalla (ver D2), que es solo de frontend.

---

## 2.0 Cómo trata hoy el código los huecos (verificado)

El criterio vigente es **uno solo en todo el pipeline: eliminar y compactar, nunca imputar.**

| Lugar | Qué hace con el hueco | Rastro que deja |
|---|---|---|
| Rechazo de Chow (`analysis_service.py` ~600) | Borra el valor y su timestamp; la segunda pasada corre sobre n−1 y los vecinos quedan contiguos | `CONTRACT_IRREGULAR_SPACING` en la segunda pasada, solo si los timestamps son años numéricos |
| Valores faltantes (`filtrar_numericos`, `pipeline_etapa1.py:273`) | Descarta el `None` y compacta | `CONTRACT_MISSING_VALUES` |
| Año interior incompleto en la agregación (`aggregation.py:206`) | Descarta el año entero (`MOTIVO_HUECO_INTERIOR`); el docstring lo dice explícito: "nunca se completan ni interpolan" | `CONTRACT_INCOMPLETE_YEARS_*` |

Consecuencia: reemplazar con la media en el what-if sería **el único lugar del producto que
completa datos**. Por eso el what-if arranca eliminando, igual que el resto (ver §2, "Política de
exclusión").

> **RESUELTO el 20/09/2026 (Fase 0).** `core/utils.py::filtrar_numericos_alineados()` filtra
> timestamps y serie de a pares; `ejecutar_etapa1()` la usa en sus tres salidas. Verificado con el
> volcado de las 9 estaciones (30 de 36 idénticos byte a byte; los 6 restantes, con celdas `S/D`,
> cambian solo `timestamps_efectivos`), con tests que fallan sin el fix y con un smoke HTTP real.
> Detalle en `docs/auditoria/hallazgos/hallazgo-timestamps-desalineados.md`, sección "Resolución".
> **El ítem A ya puede reusar esta ruta.** Lo que sigue queda como registro del diagnóstico.

**Bug latente encontrado de paso (confirmado y corregido, ver arriba):** en una carga **anual** con celdas
vacías, `serie_efectiva` sale filtrada (`filtrar_numericos`) pero `timestamps_efectivos` no
(`pipeline_etapa1.py:338-339`), porque el parser conserva los `None` (`parser.py:56`). Las dos
listas quedan de distinto largo. Efectos esperables: los gráficos de serie temporal y de Chow se
corren un año a partir del faltante, y al rechazar un atípico se borra el timestamp equivocado
(`_mapear_indice_a_serie_original` recibe una serie ya filtrada, así que es la identidad). No
afecta a cargas mensuales o diarias (la agregación arma ambas listas juntas). Test sugerido: serie
anual de 15 años con un `None` en la posición 3 y un atípico en la posición 10; verificar largos y
el año del timestamp borrado. Conviene arreglarlo **antes** del ítem A, que reusa esta ruta.

---

## 2. Ítem A: exclusión interactiva de atípicos ("what-if")

### Lo que pidió Catalini

Una vez corrida la Etapa 1 (o 1+2), poder desactivar puntos desde la misma pantalla, clickeando en
el gráfico, y ver los resultados como si esos puntos no hubieran estado. Si el resultado le sirve
al usuario, descargar la serie sin esos puntos.

Su pedido incluía tapar los huecos interiores con la media y eliminar los extremos. Esa parte
queda **postergada** para decidirla con la versión implementada a la vista (ver "Política de
exclusión" abajo y §2.0).

### Lo que existe hoy

- Chow detecta **un solo** atípico (el z máximo sobre logaritmos) y pausa el stream. La única
  acción posible es aceptar o rechazar ese punto, y rechazar **borra** el dato
  (`outliers.py`, `analysis_service.py` ~línea 600).
- Lo que pide Catalini es más general: el usuario elige **cualquier** punto, **varios** a la vez, y
  **después** de ver los resultados, no durante la pausa.
- `InteractiveChart` ya tiene navegación por teclado pero **no expone ningún callback de
  selección de punto** (`charts/InteractiveChart.tsx`).
- El payload de resultados ya trae `serie_efectiva` y `timestamps_efectivos` (`api/types.ts:159`),
  que es exactamente la serie sobre la que hay que operar.

### Política de exclusión (decidida 20/09/2026)

**Eliminar los puntos excluidos, en cualquier posición, para las dos etapas.** Una sola forma de
tratar el hueco, sin opciones en la UI.

- Un punto excluido, sea el primero, el último o uno interior, se quita de la serie junto con su
  timestamp. Etapa 1 y Etapa 2 corren sobre la misma serie resultante.
- Es el criterio que ya aplican el rechazo de Chow, los valores faltantes y la agregación temporal
  (§2.0), así que el what-if no introduce un segundo criterio en el producto.
- **Reemplazar por la media quedó evaluado y postergado**, no descartado para siempre. Se muestra
  la versión implementada a los directores y se decide con su feedback. Razones registradas para
  no arrancar con ella: es el único lugar del producto que completaría datos (la agregación lo
  prohíbe de forma explícita, `aggregation.py:206`); reduce la varianza y acerca las
  autocorrelaciones a cero, así que tiende a favorecer que la serie apruebe independencia; y no
  serviría igual en las dos etapas, porque en Etapa 2 un valor medio entraría como si fuera un
  máximo anual observado.
- Costo conocido y aceptado, que hay que **mostrar** en la UI: al quitar un punto interior los
  vecinos quedan contiguos, así que las pruebas que dependen del orden (Anderson, Wald-Wolfowitz,
  Cramer, Mann-Kendall) tratan como consecutivos dos años que no lo son. Es el mismo efecto que ya
  tiene hoy rechazar un atípico de Chow, y se señala con el mismo warning
  (`CONTRACT_IRREGULAR_SPACING`).
- **Diseñar el código dejando la puerta abierta:** `aplicar_exclusiones()` recibe un parámetro
  `tratamiento` con un único valor válido hoy (`"eliminar"`). Si más adelante se aprueba el
  reemplazo por la media, se agrega el valor nuevo sin rehacer la firma ni el contrato del
  endpoint. No se implementa la rama de la media hasta que esté aprobada.

### Diseño propuesto

**Principio:** "explorar no es decidir" (DECISIÓN 062). El what-if no persiste nada ni modifica
el análisis original. Se muestra al lado, comparado.

**0. Prerrequisito: cumplido (Fase 0, 20/09/2026).** El bug de largos de §2.0 ya está corregido.
El what-if reusa la ruta de "quitar un índice y su timestamp", y con listas de distinto largo
habría borrado el año equivocado.

**1. `core/`: función pura nueva** `core/pipeline/exclusiones.py`

```python
def aplicar_exclusiones(
    serie: list[float],
    timestamps: list | None,
    indices_excluidos: list[int],
    tratamiento: str = "eliminar",   # único valor soportado hoy
) -> SerieConExclusiones
```

- Devuelve `serie`, `timestamps` (sin los excluidos) y `excluidos`:
  `[{indice, periodo, valor_original}]`.
- Un `tratamiento` distinto de `"eliminar"` levanta error, no se ignora en silencio.
- Debe ser **la misma operación** que hoy hace el rechazo de Chow en `analysis_service.py`
  (quitar el valor y su timestamp por índice). El flujo de Chow **no se toca** en este ítem: la
  equivalencia se garantiza con el test de regresión 2 (abajo), no con un refactor.
- Si quedan menos de 10 datos, el pipeline devuelve el mismo error bloqueante de siempre
  (`CONTRACT_SERIES_TOO_SHORT`). No se inventa un error nuevo.

**2. Endpoint nuevo stateless:** `POST /api/v1/analysis/simulate-exclusion`

- Body: `serie`, `timestamps`, `tipo_variable`, `cramer_particion`, `indices_excluidos`,
  `etapas`. `tratamiento` es opcional y hoy solo acepta `"eliminar"`.
- Corre `ejecutar_etapa1(..., resolucion_temporal="anual")` sobre la serie resultante (igual que
  la segunda pasada de Chow hoy: la serie ya está agregada, no se vuelve a agregar).
- Chow se evalúa **sin pausa** (como CU-03): si aparece un nuevo atípico, se informa como
  sugerencia, no se detiene nada.
- Si `etapas` incluye 2, corre `ejecutar_etapa2` sobre la misma serie y devuelve el ranking
  completo. La elección de distribución se hace después con el endpoint del ítem B.
- JWT opcional (sirve para CU-01 y CU-02). Sin `session_store`, sin BD.
- Tope de longitud de `serie` (es anual, un tope de ~500 valores es holgado) y validación de
  índices en el borde. Códigos de error nuevos van a `api-contracts.md` y a
  `errors.es.ts` (el job `error-catalog` de CI lo exige, DECISIÓN 038).
- Medir el tiempo de `ejecutar_etapa2` sincrónico con n≈40 antes de cerrar el diseño; si supera
  ~2 s, evaluar devolverlo por SSE.

**3. Frontend**

- `InteractiveChart`: prop nueva `onPointActivate(index)` disparada por click **y** por
  Enter/Espacio sobre el punto enfocado (accesibilidad: el teclado ya existe, falta la acción).
- Montarla en `Etapa1SerieTemporalChart` y `Etapa1ChowChart`. El punto que Chow marcó aparece
  pre-sugerido pero no pre-seleccionado.
- Alternativa accesible obligatoria: lista de años con checkbox debajo del gráfico (misma
  selección, dos vistas).
- Botón "Recalcular sin los puntos seleccionados" (no recalcular en cada click).
- Sin selector de tratamiento: el panel dice en una línea que los puntos seleccionados se quitan
  de la serie.
- Vista comparativa: veredictos originales vs simulados lado a lado, con los cambios resaltados
  (por ejemplo, "Anderson: rechazada → aprobada"), y el `n` de cada lado.
- Si se excluyó algún punto interior, nota visible: "Los años vecinos al punto quitado se tratan
  como consecutivos en las pruebas de independencia, homogeneidad y tendencia."
- Si hubo Etapa 2: ranking simulado y acceso al explorador del ítem B sobre ese ranking.

**4. Descarga de la serie**

- Se genera en el frontend como `Blob` CSV a partir de la **respuesta del backend** (el frontend
  solo serializa lo que devolvió `core/`).
- Columnas: `periodo`, `valor`. Los excluidos no aparecen. El formato tiene que poder re-subirse a
  METIS tal cual (el parser ya acepta año de 4 dígitos, `parser.py:120`).
- Nombre: `<archivo_original>_sin_atipicos.csv`.
- **Advertencia visible** en la UI: si la carga original era diaria o mensual, lo que se descarga
  es la serie de **máximos anuales**, no los datos crudos sin el punto (quitar el máximo de un año
  de datos diarios no es lo mismo que quitar ese año: el segundo mayor valor diario pasaría a ser el
  máximo). Consistente con el camino A (DECISIÓN 065/066).

### Tests

- Unit de `aplicar_exclusiones`: primer punto, último punto, interior, varios mezclados, excluir
  todo, n resultante < 10, timestamps `None`, largos de serie y timestamps siempre iguales,
  `tratamiento` inválido levanta error.
- Regresión 1: `simulate-exclusion` con `indices_excluidos=[]` da Etapa 1 byte a byte idéntica al
  resultado original de las 9 series.
- Regresión 2: `simulate-exclusion` con `[indice_atipico]` da el mismo resultado que el flujo de
  Chow con "rechazar" para la misma serie. Esto prueba que no hay dos criterios. **Se compara
  estadísticos, veredictos, niveles y `nivel_confianza`, no `warnings`:** el flujo de Chow arrastra
  desde la primera pasada los warnings de agregación (`CODIGOS_WARNING_AGREGACION`,
  `analysis_service.py`) y un endpoint sin estado no los tiene. `indices_excluidos` es relativo a
  `serie_efectiva`, y así debe quedar en el contrato.
- **Herramienta de volcado:** el script que usan estas regresiones (`regres.py`, citado en
  `docs/revision-resolucion-diaria.md`) **no está en el repo**. La Fase 0 lo reconstruyó (extrae las
  9 series de `docs/auditoria/regresion/regresion-pipeline/*.md` y vuelca el payload real de
  `_serializar_etapa1`/`_serializar_etapa2`). Los tres scripts (`extract_series.py`, `regres.py`,
  `diff.py`) y el modo de uso están en el **Apéndice C** de
  `docs/auditoria/hallazgos/hallazgo-timestamps-desalineados.md`. Decidir con Octavio si se
  promueven a un directorio del repo (le toca a `tests/regression/`) antes de la Tanda 2.
- Frontend: selección por click, por teclado y por checkbox producen el mismo estado; CSV
  generado re-parseable.

### Decisión a registrar

`decision071.md`: exclusión por eliminación en todas las posiciones, coherente con el criterio
vigente de huecos (rechazo de Chow, faltantes, agregación); reemplazo por la media evaluado y
**postergado** hasta ver el feedback de los directores sobre la versión implementada, con sus tres
contras registradas; efecto de la eliminación sobre las pruebas que dependen del orden; parámetro
`tratamiento` previsto en la firma para no rehacer el contrato si se aprueba; por qué no se
persiste.

---

## 3. Ítem B: probar otras distribuciones desde resultados

### Lo que existe hoy

- El historial ya lo hace: `HistoryDetailPage.tsx` usa `POST /analysis/{id}/design-events`
  (DECISIÓN 062), que busca los `parametros` ya ajustados en la BD y llama a
  `calcular_eventos_diseno()`.
- Ese endpoint **requiere un `analysis_id` persistido y JWT**. Sirve para CU-01 al terminar el
  stream (el evento `complete` trae `analysis_id`), pero **no para CU-02** (anónimo, no persiste)
  ni para el ranking simulado del ítem A (tampoco persiste).

### Diseño propuesto

- **Endpoint nuevo stateless** `POST /api/v1/analysis/design-events` (sin id):
  body `{distribucion, metodo, parametros, periodos_retorno, max_t_empirico}`. Llama a las mismas
  funciones puras (`calcular_eventos_diseno`, `_calcular_curva_ajuste`). Los `parametros` ya viajan
  en el ranking del SSE (`_serializar_etapa2`, `metodo_dict`).
- Recibir parámetros del cliente es aceptable: la función es pura, no persiste, y el usuario solo
  puede "engañarse" a sí mismo. Validar que `distribucion`/`metodo` existan y que los parámetros
  tengan las claves esperadas del módulo.
- `POST /analysis/{id}/design-events` **se mantiene** para el historial (fuente de verdad en BD).
- Frontend: extraer el bloque de exploración de `HistoryDetailPage` a un componente compartido
  (`routes/results/Etapa2Explorador.tsx`) y montarlo en `ResultsPage` (CU-01 y CU-02) y en la vista
  simulada del ítem A. El historial pasa a usar el mismo componente.
- Texto de UI: dejar claro que explorar **no cambia** la elección registrada (DECISIÓN 062).

### Decisión a registrar

Addendum a DECISIÓN 062 (o `decision072.md`): por qué hace falta la variante stateless y por qué es
seguro aceptar parámetros del cliente.

---

## 4. Ítem C: valores negativos con tipo "Otro" (análisis teórico)

### Comportamiento real hoy (verificado)

"Excluir" no es exactamente lo que pasa: Etapa 1 casi entera **sí** procesa los negativos. Lo que
pasa es que los métodos basados en logaritmos o con soporte positivo quedan fuera, y en silencio.

| Componente | Caudal/Precip. | Otro |
|---|---|---|
| Warning de contrato por negativos | Sí (`CONTRACT_NEGATIVE_VALUES`) | No |
| Anderson, Wald, Helmert, t, Cramer, MK, KS | Corren sobre valores crudos | Igual |
| Chow con ceros | `TEST_NOT_EXECUTED_ZEROS` | `TEST_NOT_EXECUTED_CONDITION` |
| Chow con negativos | `TEST_NOT_EXECUTED_CONDITION` | `TEST_NOT_EXECUTED_CONDITION` |
| Etapa 2 con ceros | `disabled_zeros` en LN2p, LP3, Gamma 2p, Exp β | **Igual** (el flag `tiene_ceros` no mira el tipo) |
| Etapa 2 con negativos | `no_aplicable` genérico en LN2p, LP3, Gamma 2p, Exp β, Gen. Exp. | Igual |

Fuentes: `contract.py:90`, `outliers.py:17-36`, `analysis_service.py:689`,
`lognormal2p.py:41`, `logpearson3.py:69`, `gamma2p.py:60`, `exponencial_beta.py:37`,
`gen_exponencial.py:98`.

Problemas concretos:

1. Con "Otro", la **única** diferencia real respecto de Caudal/Precip. es un warning y un código
   distinto de Chow. El toggle promete más de lo que hace.
2. En Etapa 2, un `no_aplicable` por negativos es indistinguible de un `no_aplicable` por fallo
   numérico. El usuario no sabe por qué se cayó la distribución.
3. Chow nunca corre ante un solo valor ≤ 0, aunque para una variable tipo temperatura el
   logaritmo no tiene sentido físico ni siquiera con todos los valores positivos.

### Opciones teóricas

**Opción 1: traslación de la serie** (x' = x + c, con c > −min(x)).
- A favor: habilita todos los métodos logarítmicos.
- En contra, y es decisivo: el resultado **depende de c**, que es arbitrario. Chow sobre
  ln(x + c) cambia de veredicto según c. Para las distribuciones de 2 parámetros, trasladar
  equivale a fijar a mano un tercer parámetro de posición; la forma defendible de hacer eso es
  **estimarlo**, que es exactamente lo que ya hacen LN3p, Gamma 3p, Exp x0β y Pareto generalizada
  (parámetro x0/µ). **Recomendación: descartar**, y registrar el porqué.

**Opción 2: Chow sin logaritmos para "Otro"** (test de Grubbs original sobre valores crudos,
Grubbs 1969).
- Grubbs-Beck aplica el test sobre logaritmos porque los caudales máximos se suponen
  aproximadamente log-normales (Bulletin 17B). Para una variable que puede ser negativa esa
  premisa no existe; el test original de Grubbs sobre los valores supone normalidad.
- Requiere referencia bibliográfica nueva en `formulas-etapa1.md` antes de implementar (regla del
  proyecto: ninguna fórmula sin referencia explícita) y el aval de los directores.

**Opción 3: estado explícito por dominio** (`disabled_negatives` o `no_aplicable_dominio`),
análogo a `disabled_zeros`.
- Cada distribución con soporte x > 0 declara esa restricción; el ranking muestra "no aplica: la
  serie tiene valores negativos" y sugiere la variante de 3 parámetros cuando existe.
- No cambia ningún número, solo la trazabilidad. Mínimo y defendible ante el tribunal.

**Recomendación: 3 siempre, 2 si Catalini y Facundo la avalan, 1 descartada.**

### Decidido (20/09/2026): opción 3. Especificación

Copiar el patrón exacto de los ceros, que ya existe en tres niveles:

1. **`core/etapa2/types.py`**: `STATUS_DISABLED_NEGATIVES = "disabled_negatives"`, junto a
   `STATUS_DISABLED_ZEROS`.
2. **Cada módulo**: flag `DISABLED_WITH_NEGATIVES: bool = True` al lado del
   `DISABLED_WITH_ZEROS` existente, en las distribuciones cuyo soporte exige x > 0 o x ≥ 0 y que
   hoy devuelven `no_aplicable` genérico ante un negativo:
   `lognormal2p`, `logpearson3`, `gamma2p`, `exponencial_beta` (chequean `serie <= 0`) y
   `gen_exponencial` (chequea `serie < 0`).
3. **`distributions/__init__.py`**: `DISABLED_WITH_NEGATIVES: frozenset[str]` con esas cinco.
   Las de 3 parámetros (`lognormal3p`, `gamma3p`, `exponencial_x0_beta`, `gen_pareto`) **no**
   entran: estiman la posición x0/µ y ya tienen su propio chequeo `x0 ≥ min(xi)`, que es el que
   debe decidir.
4. **`pipeline_etapa2.py`**: `ejecutar_etapa2(serie, tiene_ceros, tiene_negativos)`. Precedencia:
   si la serie tiene negativos **y** ceros, gana `disabled_negatives` (es la condición más fuerte y
   la que explica al usuario el motivo real).
5. **`analysis_service.py:689`**: calcular `tiene_negativos = bool(np.any(serie_np < 0))` junto a
   `tiene_ceros` y guardarlo en la sesión igual que `tiene_ceros`.
6. **El flag depende de los datos, no de `tipo_variable`**, igual que `tiene_ceros` hoy. Una
   serie Caudal/Precip. con negativos (ya advertida por `CONTRACT_NEGATIVE_VALUES`) recibe el mismo
   estado.
7. **Frontend**: `MetodoStatus` en `api/types.ts:368` y la etiqueta en
   `Etapa2RankingView.tsx:13` ("no aplica: la serie tiene valores negativos"). Cuando exista
   variante de 3 parámetros, agregar la sugerencia ("probá Log-Normal 3p").
8. **Texto de `ConfigPage.tsx:555-561`**: decir lo que el toggle hace de verdad, y que las
   distribuciones de soporte positivo quedan deshabilitadas ante negativos sea cual sea el tipo.
9. **Opcional, mismo espíritu:** código propio para Chow ante negativos
   (`TEST_NOT_EXECUTED_NEGATIVES`) en vez de `TEST_NOT_EXECUTED_CONDITION`, que hoy mezcla
   "negativos" con cualquier otra condición. Si se hace, pasa por el catálogo de errores
   (DECISIÓN 038).

**Verificación:** ninguna de las 9 series de regresión tiene negativos, así que su salida debe ser
byte a byte idéntica. Tests nuevos: serie con un negativo (las 5 en `disabled_negatives`, las 3p
decidiendo por su cuenta, Normal/Gumbel/GVE/Uniforme en `ok`); serie con negativo y cero
(precedencia); serie solo con ceros (sin cambios).

**Decisión:** `decision073.md`, con las opciones 1 y 2 registradas como descartada y pendiente.

Además:

- Revisar si `tiene_ceros` debe seguir deshabilitando distribuciones con tipo "Otro"
  (matemáticamente sí: ln 0 no existe; el motivo es de dominio, no de tipo de variable). Documentar.
- Actualizar el texto de `ConfigPage.tsx:555-561` para que diga lo que el toggle hace de verdad.
- Nota de alcance: "Otro" sigue agregando a **máximos** anuales. Si Catalini piensa en variables
  donde el extremo de interés es el mínimo (temperaturas mínimas, estiajes), eso es otra
  funcionalidad y conviene decirlo en la reunión para que no quede implícito.

### Decisión a registrar

`decision073.md` con las tres opciones, la elegida y la descartada con su argumento (la
dependencia de c es el argumento central).

---

## 5. Ítem D: auditoría de fórmulas LaTeX (solo lectura)

### Alcance

Las 8 pruebas de Etapa 1 con fórmula en `frontend/src/i18n/explicaciones.ts`
(`FORMULAS_LATEX`, líneas ~129-270). Etapa 2 no tiene fórmulas en modo paso a paso todavía.

### Método: matriz de 4 columnas por prueba

| Fórmula mostrada (LaTeX) | Ecuación en `formulas-etapa1.md` | Implementación en `core/` | Ecuación en la tesis |
|---|---|---|---|

Para cada fila, marcar: coincide / difiere (y cómo) / falta un paso. **Sin tocar backend.** Si el
error está en el código, se reporta como hallazgo para una decisión aparte; si está en el LaTeX o
en el `.md`, se corrige ahí.

**La columna de la tesis necesita el PDF de la tesis de Facundo**, que no está en el repo. Hay que
pasárselo a Claude Code (fuera del repo, o las páginas del capítulo III y del apéndice).

### Hallazgos ya encontrados al revisar para este plan (muestra del tipo de cosas que van a aparecer)

1. **`formulas-etapa1.md` está desactualizado respecto del código en Anderson, en dos puntos.**
   El `.md` dice `k_max = n // 3` y `aprobada = (lags_fuera / k_max) ≤ 0.10`. El código usa
   `k_max = ceil(n/3)` (DECISIÓN 016) y `lags_fuera ≤ ceil(0.10·k_max)` (DECISIÓN 012). No es
   una diferencia cosmética: con k_max = 9 el `.md` no tolera ningún lag fuera y el código tolera 1.
   El código está bien (respaldado por decisiones); el `.md` que "se lee siempre" está mal.
2. **Anderson no muestra la Ec. III-3** (las bandas de confianza por lag), que es la mitad de la
   prueba. Solo muestra III-1 para el lag de mayor |r_k|. La regla del 10% aparece solo en prosa.
3. **Chow muestra solo el valor crítico K_N**, no el estadístico. Faltan y_i = ln x_i, ȳ, S_y y
   G = max|y_i − ȳ|/S_y, que están en la sección 9 de `formulas-etapa1.md` y cuyos términos
   (`media_log`, `s_log`) ya viajan en `explicacion.terminos`. El estudiante ve contra qué se
   compara, pero no qué se compara.
4. **Mann-Kendall** no muestra la fórmula de Var(S) ni la tipificación; está justificado en un
   comentario (DECISIÓN 064: "sin fórmula inventada"), pero la auditoría debería buscar la ecuación
   exacta en la tesis o en el apéndice de Carlos (A.55) y, si existe, mostrarla.

### Entregable

`docs/auditoria/fases/auditoria-formulas-latex.md` con la matriz completa, los hallazgos
clasificados (error en LaTeX / error en `.md` / paso faltante / discrepancia en código) y los
cambios propuestos. Los cambios en `explicaciones.ts` y `formulas-etapa1.md` van en un PR aparte
del informe.

### Resultado (20/09/2026) y reparto de los hallazgos

La auditoría está hecha (`docs/auditoria/fases/auditoria-formulas-latex.md`, contrastada con la
tesis cap. III y con el apéndice de Caamaño A.5). Confirmó los 4 hallazgos de arriba y sumó
otros. Reparto por fase, según la restricción de dejar el backend para el final:

**Fase D2: solo frontend y documentación (PR propio, sin tocar `backend/`)**

| Id | Cambio | Archivo |
|----|--------|---------|
| H-10 | Corregir Anderson en `formulas-etapa1.md` §2 (`ceil(n/3)`, `lags_fuera ≤ ceil(0.10·k_max)`) y el `n/3` de `statistical-pipeline.md` | `.claude/rules/core/` |
| H-4 (parcial) | Anderson: mostrar la fórmula de las bandas (III-3) y la regla del 10% en el paso simbólico, y los lags fuera / tolerancia en la sustitución (`terminos` ya trae `k_max`, `lags_fuera`, `tolerancia`). **La tabla de bandas por lag y el correlograma siguen en E/F (Tanda 2)** | `explicaciones.ts` |
| H-5 | Wald-Wolfowitz: mostrar μ_R (III-5) y σ_R (III-6) con sus fórmulas. `terminos` ya trae `n1`, `n2`, `n` | `explicaciones.ts` |
| H-7 | Cramer: mostrar τ_w (III-13/14) y S_Q (III-10). `terminos` ya trae `media_global`, `s_global`, `tau_w*` | `explicaciones.ts` |
| H-8 | Kolmogorov-Smirnov: definir D (A.56) | `explicaciones.ts` |
| H-9 | Mann-Kendall: mostrar Var(S) aclarando que la fórmula literal de A.55 vale sin empates | `explicaciones.ts` |
| H-3 (parcial) | t de Student: mostrar la definición de S_p² = (n₁s₁²+n₂s₂²)/(n₁+n₂−2). El denominador del paso 2 se sigue armando en el frontend hasta la Tanda 2 (ver E) | `explicaciones.ts` |
| H-1 (interino) | Cramer: que los rótulos "Bloque 60% / 30%" (`explicaciones.ts:72-73, 211-216, 306`) dejen de afirmar un porcentaje que puede ser falso con partición personalizada: rotular por lo que sí es siempre cierto ("bloque 1: n_w₁ = … datos", "bloque 2: n_w₂ = … datos"). El porcentaje real vuelve en la Tanda 2 (ver E) | `explicaciones.ts` |
| H-6 (solo rótulo) | Chow: rotular que acá α = 0,10 y no el 0,05 global. **No se toca el valor crítico** (ver §1, respuestas registradas) | `explicaciones.ts` |
| H-2 (solo prosa) | Mann-Kendall: sacar "corrección por empates, Kendall 1975" de la prosa (A.55 no la tiene, es de la librería) y documentar en `formulas-etapa1.md` §7 la divergencia 1,96 vs. 1,64 de la Tabla A.4. **El valor no cambia** hasta la pregunta 7 de §1 | `explicaciones.ts`, `formulas-etapa1.md` |

Tests: los de `explicaciones.test.ts` (o los de `Etapa1ResultView`) que fijan el texto. Regla del
repo para PRs de frontend: correr el flujo en el navegador después del último commit y dejar
evidencia (`testing.md`, capa 4).

**Fase E (backend, Tanda 2):** además de `Explicacion.desglose` (Anderson por lag y Chow por
observación), el mismo cambio aditivo incorpora:

| Id | Cambio de backend | Qué habilita |
|----|-------------------|--------------|
| H-4 | El desglose de Anderson incluye las bandas por lag (III-3) | Mostrar la mitad de la prueba que hoy falta, y el correlograma (F) |
| H-1 | `n1_pct` y `n2_pct` en `terminos` de Cramer | Rótulos "Bloque X%" correctos con partición personalizada (hoy dicen 60/30 fijo). El frontend cambia en el mismo PR |
| H-3 (resto) | El denominador de t (`S_p·√(1/n₁+1/n₂)`) en `terminos` de t de Student | Que el frontend no lo recalcule (DECISIÓN 064) |

**Sin acción:** H-6 (valor crítico de Chow, decisión de Kevin) y H-2 (valor crítico de
Mann-Kendall, a la espera de la pregunta 7 de §1).

---

## 6. Ítem E: desglose paso a paso (los k pasos)

### Causa raíz

`calcular_anderson()` **ya calcula** r_k, el numerador y ambas bandas para cada lag
(`independence.py:26-33`), pero después de decidir **los descarta**: `Explicacion.terminos` es un
`dict[str, float | int | None]` plano y solo guarda el lag del estadístico. El frontend no puede
reconstruir los demás sin recalcular estadística, cosa que DECISIÓN 064 prohíbe (con razón).

### Diseño propuesto

- **Tanda 2 (backend).** Este cambio aditivo también lleva `n1_pct`/`n2_pct` en `terminos` de
  Cramer (H-1) y el denominador en `terminos` de t de Student (H-3), y las bandas por lag dentro
  del desglose de Anderson (H-4). Detalle en §5, "Reparto de los hallazgos".
- **`core/types.py`**: agregar a `Explicacion` un campo opcional
  `desglose: list[dict[str, float | int | bool | None]] | None = None`. Aditivo: no cambia ningún
  número ni ningún campo existente.
- Poblarlo en las pruebas que tienen pasos naturales:

| Prueba | Filas del desglose | Prioridad |
|---|---|---|
| Anderson | por lag k: `k, numerador, r_k, banda_inf, banda_sup, fuera` | Alta (pedido explícito) |
| Chow | por observación: `i, x_i, ln x_i, z_i` (resaltar el máximo) | Alta |
| Wald-Wolfowitz | por observación: `i, x_i, signo`; y `rachas` | Media |
| Helmert | por par consecutivo: `i, signo_i, signo_i+1, S o C` | Media |
| Cramer | ya muestra los dos bloques; agregar medias de bloque si faltan | Baja |
| Mann-Kendall | por i: contribución parcial a S (la matriz n² es demasiado) | Baja |

- **Serialización:** `_serializar_etapa1` y el tipo `TestResultDetail` del frontend. Los análisis
  ya persistidos no tienen `desglose`: el campo llega `null` y la UI degrada a la vista actual,
  sin backfill (mismo criterio que DECISIÓN 058 §4).
- **UI:** debajo de la fórmula actual, un `<details>` "Ver los k pasos" con una tabla (lag, r_k,
  bandas, dentro/fuera) y, al elegir una fila, la fórmula III-1 sustituida **para ese lag** y la
  III-3 con sus bandas. La fila del lag reportado queda resaltada. La tabla es a la vez la vista
  accesible del correlograma (ítem F).
- **Tamaño del payload:** Anderson agrega ~n/3 filas; Chow y Wald ~n filas. Con n≈40 es
  despreciable, pero medirlo igual (DECISIÓN 058 tiene el precedente de medir).

### Tests

- Regresión: las 9 series deben dar veredictos, estadísticos y valores críticos **idénticos**; solo
  cambia la presencia del campo nuevo. Reusar el script de volcado de
  `docs/revision-resolucion-diaria.md`, comparando todo salvo `desglose`.
- Unit: la fila de `desglose` del lag reportado coincide con `numerador`/`estadistico` actuales;
  `sum(fuera) == lags_fuera`.

### Decisión a registrar

Addendum fechado en `decision064.md`: el principio "core expone, frontend renderiza" no cambia; se
amplía qué expone.

---

## 7. Ítem F: gráficos propios por prueba

`formulas-etapa1.md` §2 ya lo exige para Anderson ("en los gráficos de la interfaz se deben dibujar
las bandas dinámicas lag por lag") y no está implementado. Todos salen de los datos del ítem E, sin
recalcular nada, sobre `InteractiveChart` (DECISIÓN 056).

| Prueba | Gráfico | Qué ayuda a decidir | Prioridad propuesta |
|---|---|---|---|
| Anderson | **Correlograma**: barras r_k por lag + bandas superior/inferior | Cuántos lags salen y cuáles | Alta |
| Chow | Ya existe (`Etapa1ChowChart`) | | |
| Cramer | Serie con los bloques 60% / 30% sombreados y sus medias | Dónde está el quiebre | Media |
| KS (tendencia) | Las dos distribuciones empíricas acumuladas con D marcado | De dónde sale D | Media |
| Wald-Wolfowitz | Serie vs media con las rachas coloreadas | Qué es una racha | Media (muy docente) |
| t de Student | Boxplot de las dos submuestras (`BoxPlot` ya existe) | Diferencia de medias | Baja |
| Mann-Kendall | Sin gráfico propio (la serie temporal ya cumple) | | |

Confirmar prioridades con Facundo (pregunta 6). El correlograma se hace sí o sí porque ya está
especificado.

---

## 8. Instrucciones para Claude Code

Un PR por fase, en este orden. Cada prompt asume que Claude Code lee primero los archivos de
"Leer siempre" de `CLAUDE.md`. **Todo lo que toque `backend/` va en la Tanda 2 (ver §0), después
de consultarlo con Octavio.**

**Fase 0 (HECHA 20/09/2026):** rama `fix/timestamps-efectivos-alineados`, ver §2.0.

**Fase D (HECHA 20/09/2026, auditoría, sin código):** informe en
`docs/auditoria/fases/auditoria-formulas-latex.md`.

**Fase D2 (Tanda 1, sin backend):**
> Leé §5 de este plan, sección "Resultado y reparto de los hallazgos", y el informe
> `docs/auditoria/fases/auditoria-formulas-latex.md`. Aplicá solo los cambios de la tabla de la
> Fase D2: `frontend/src/i18n/explicaciones.ts` y los dos `.md` de `.claude/rules/core/`. No
> modifiques nada de `backend/`. **No cambies ningún valor crítico** (Chow y Mann-Kendall quedan
> como están). Actualizá los tests que fijan el texto. Antes de dar por terminado, corré
> `npm run lint && npm test && npm run build` y el flujo en el navegador (modo paso a paso, las 8
> pruebas), y dejá evidencia.

**Fase E+F (desglose y gráficos):**
> Tanda 1 (sin backend): en `Etapa1ResultView`, la tabla desplegable de pasos y el correlograma de
> Anderson sobre `InteractiveChart`, contra un `desglose` mockeado en los tests; degradar a la
> vista actual si el campo llega `null`.
> Tanda 2 (con backend, después de hablar con Octavio): leé §5 (reparto) y §6. Agregá
> `Explicacion.desglose` en `core/types.py`, poblalo para Anderson (con bandas) y Chow primero, y
> los campos aditivos de `terminos` (`n1_pct`/`n2_pct` en Cramer, denominador en t de Student).
> Verificá con el volcado de las 9 series que la salida es idéntica salvo los campos nuevos
> (recordá que el script no está en el repo, ver §2). Addendum en `decision064.md`.

**Fase B (explorador de distribuciones):**
> **Tanda 1 — HECHA (21/09/2026), sin tocar backend.** `Etapa2Explorador` extraído de
> `HistoryDetailPage` y montado en `ResultsPage` **solo para CU-01**: ahí el evento `complete`
> trae `analysis_id` y sirve el endpoint que ya existe (`POST /analysis/{id}/design-events`,
> DECISIÓN 062). El componente recibe la función de exploración por prop (`explorar`), así que
> CU-02 (anónimo, sin id, sin persistencia: hoy sigue de solo lectura) enchufa el endpoint
> stateless en la Tanda 2 sin tocar el componente. Verificado contra el backend real: recálculo
> 200 con curva de 60 puntos, elección registrada intacta, anónimo 401.
> Tanda 1 (sin backend): componente compartido `Etapa2Explorador` extraído de `HistoryDetailPage`,
> montado en `ResultsPage`, contra el contrato acordado y mockeado en los tests.
> Tanda 2 (con backend, después de hablar con Octavio): leé §3. Endpoint stateless, contrato en
> `api-contracts.md`, códigos en `errors.es.ts`. Decisión 072 (nueva, enlazada a la 062).
> **Dos puntos a decidir antes de codear el endpoint** (surgieron al revisar el plan contra el
> código): (1) no reusar el nombre `POST /analysis/design-events`: es el de un contrato viejo que
> `api-contracts.md` marca como "reemplazado, no implementar"; conviene otro (por ejemplo
> `explore-design-events`). (2) En vez de aceptar `parametros` del cliente, el endpoint puede
> recibir `serie` y reajustar con `ejecutar_etapa2` (medido: ~40 ms para n=40 y n=100): no hay que
> validar claves ni valores finitos y sirve igual para el ranking simulado del ítem A.

**Fase A (what-if de atípicos):**
> El bug de largos de §2.0 ya está corregido (Fase 0).
> **A1 — HECHA (21/09/2026), sin tocar backend:** `onPointActivate` en `InteractiveChart` (clic y
> Enter/Espacio) y `marked` para dibujar los excluidos huecos; los dos gráficos con eje de año
> (serie temporal y Chow) y una lista de años con checkbox comparten una única selección
> (`Etapa1GraficosView`, dueño del estado; `Etapa1ResultView` sigue presentacional); Chow queda
> señalado como sugerido pero sin preseleccionar; descarga del CSV `periodo,valor` sin los
> excluidos (`<archivo>_sin_atipicos.csv`) con el aviso de que con carga mensual/diaria lo
> descargado son máximos anuales. Verificado contra el backend real: el CSV se vuelve a subir
> tal cual (13 datos, sin atípico) y METIS avisa `CONTRACT_IRREGULAR_SPACING` por el hueco.
> **A2 (pendiente, espera el contrato con Octavio):** botón "Recalcular" y vista comparativa
> (veredictos originales vs simulados). Van por prop (`simular`), igual que `explorar` en B, y
> el componente de comparación recibe dos `Etapa1Result`. El cuerpo de la respuesta propuesto
> es el mismo payload del stream (`result_etapa1` + ranking de Etapa 2 si se pidió) más la lista
> `excluidos`.
> Tanda 1 (sin backend): `onPointActivate` en `InteractiveChart` (click y Enter/Espacio), lista de
> años con checkbox como alternativa accesible, botón "Recalcular", vista comparativa y descarga CSV
> (Blob generado a partir de la respuesta), todo contra el contrato acordado y mockeado.
> Tanda 2 (con backend, después de hablar con Octavio): leé §2. `aplicar_exclusiones()` en `core/`,
> endpoint `simulate-exclusion` (medido: `ejecutar_etapa2` tarda ~40 ms, sincrónico alcanza) y las
> regresiones 1 y 2 de §2. Decisión 071.

**Fase C (negativos):** la respuesta 5 de §1 ya está cerrada (opción 3). Toca `core/` y va entera
en la Tanda 2 (después de hablar con Octavio), salvo la etiqueta y el texto de `ConfigPage` que son
frontend.
> Leé §4. Implementá `disabled_negatives` como copia del patrón de los ceros. Ojo: `gen_exponencial`
> no tiene un flag `DISABLED_WITH_ZEROS` a nivel de módulo (solo `serie < 0` en `ajustar()`), así
> que el flag nuevo va en el `frozenset` de `distributions/__init__.py` y en su chequeo, no "al lado"
> de uno existente. `ejecutar_etapa2` se llama desde dos lugares (`analysis_service.py` y
> `full_pipeline.py`): el parámetro `tiene_negativos` debe tener default `False` para no romper el
> segundo. Verificá que las 9 series dan salida idéntica. Decisión 073.
