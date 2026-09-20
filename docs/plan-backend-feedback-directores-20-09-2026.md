# Cambios de backend pendientes del feedback de directores — documento para Octavio

**Fecha:** 21/09/2026. **Origen:** `docs/plan-feedback-directores-20-09-2026.md` (el plan completo; este
documento junta solo lo que toca `backend/`). **Autor:** Kevin, con Claude Code.

**Para qué sirve:** Kevin dejó todo lo que toca `backend/` para el final, a consultar con vos antes
de tocar nada. El frontend ya está hecho (o hecho hasta donde se puede sin backend) y espera estos
cambios. Acá está cada uno con su contrato exacto, los archivos que toca, los tests, los riesgos y las
decisiones que te tocan a vos. Nada de esto está implementado en el backend, salvo la Fase 0.

**Ya hecho en backend (para no repetirlo):** PR #90 (Fase 0) — `timestamps_efectivos` quedaba de
distinto largo que `serie_efectiva` en cargas anuales con celdas vacías; se filtran de a pares
(`core/utils.py::filtrar_numericos_alineados`). Verificado con el volcado de las 9 estaciones.

---

## 0. Resumen

| Bloque | Qué es | Tamaño | Depende de | Decisión |
|---|---|---|---|---|
| **C** | Estado `disabled_negatives` en Etapa 2 (con "Otro" + valores negativos) | Chico-medio | nada | 073 |
| **B** | Endpoint de exploración de distribuciones **sin id** (CU-02) | Chico | nada | 072 |
| **E** | `Explicacion.desglose` + campos aditivos en `terminos` (paso a paso y correlograma) | Medio | nada | addendum 064 |
| **A** | `aplicar_exclusiones()` + endpoint `simulate-exclusion` (what-if de atípicos) | El más grande | helpers de B | 071 |

**Orden que se propone:** herramienta de regresión → **C → B → E → A**. C es la más chica e
independiente; B reutiliza funciones que ya existen; E es puramente aditiva; A es la más grande y
reutiliza lo de B para el ranking de Etapa 2.

**Regla común a los cuatro:** ningún cambio modifica un número. Las 9 estaciones de la tesis deben
dar la misma salida antes y después, salvo los campos nuevos. Ver §6.

---

## 1. Bloque C — valores negativos con tipo "Otro" (`disabled_negatives`)

**Pedido:** Catalini. **Decidido por Kevin (20/09):** opción 3 del plan §4 — estado propio, análogo a
`disabled_zeros`. No cambia ningún número, solo la trazabilidad: hoy un negativo hace que 5
distribuciones devuelvan `no_aplicable` genérico, indistinguible de un fallo numérico.

**Comportamiento actual verificado:** `lognormal2p`, `logpearson3`, `gamma2p`, `exponencial_beta`
devuelven `no_aplicable` con `serie <= 0` y `gen_exponencial` con `serie < 0` (todos los métodos). Las
de 3 parámetros (`lognormal3p`, `gamma3p`, `exponencial_x0_beta`, `gen_pareto`) tienen su propio chequeo
`x0 ≥ min(xi)` y **no** entran.

**Cambios:**

1. `core/etapa2/types.py`: `STATUS_DISABLED_NEGATIVES = "disabled_negatives"`, junto a `STATUS_DISABLED_ZEROS`.
2. `core/etapa2/distributions/__init__.py`: `DISABLED_WITH_NEGATIVES: frozenset[str]` con las cinco.
   ⚠️ `gen_exponencial` **no** tiene un flag `DISABLED_WITH_ZEROS` a nivel de módulo (solo el
   `serie < 0` dentro de `ajustar()`, línea ~98), así que su entrada va en el `frozenset` y en ese
   chequeo, no "al lado" de un flag existente. Los otros cuatro sí tienen flag por módulo.
3. `core/pipeline/pipeline_etapa2.py`: `ejecutar_etapa2(serie, tiene_ceros=False, tiene_negativos=False)`.
   **Default `False`**: se llama desde dos lugares (`services/analysis_service.py:701` y
   `core/pipeline/full_pipeline.py:70`); el segundo no debe romperse. Precedencia: con negativos **y**
   ceros gana `disabled_negatives` (la condición más fuerte, la que explica el motivo real).
4. `services/analysis_service.py:689`: `tiene_negativos = bool(np.any(serie_np < 0))` junto a
   `tiene_ceros`, y guardarlo en `SessionState` (`session_store.py`) igual que `tiene_ceros`.
5. **El flag depende de los datos, no de `tipo_variable`**, igual que `tiene_ceros` hoy. Una serie
   Caudal/Precip. con negativos (ya advertida por `CONTRACT_NEGATIVE_VALUES`) recibe el mismo estado.
6. Opcional, mismo espíritu: `TEST_NOT_EXECUTED_NEGATIVES` para Chow en vez de
   `TEST_NOT_EXECUTED_CONDITION` (`outliers.py:27-36`, que hoy mezcla negativos con cualquier otra
   condición). Si se hace, pasa por el catálogo (§7).
7. Frontend (ya preparado para recibirlo, es un PR chico aparte): `MetodoStatus` en `api/types.ts`,
   la etiqueta de `Etapa2RankingView.tsx` ("no aplica: la serie tiene valores negativos") y el texto de
   `ConfigPage.tsx:555-561`, que hoy promete que con "Otro" un negativo "es un dato válido" sin decir
   que varias distribuciones quedan fuera.

**Tests nuevos:** serie con un negativo (las 5 en `disabled_negatives`; las 3p decidiendo por su
cuenta; Normal/Gumbel/GVE/Uniforme en `ok`); serie con negativo **y** cero (precedencia); serie solo
con ceros (sin cambios). **Verificación:** ninguna de las 9 series de regresión tiene negativos: su
salida debe ser **byte a byte idéntica**.

**Decisión 073** — registrar las tres opciones: (3) elegida; (1) **traslación** `x' = x + c`
descartada — el resultado depende de `c`, arbitrario, y equivale a fijar a mano un tercer parámetro
de posición que las distribuciones de 3 parámetros ya **estiman**; (2) Chow sin logaritmos para "Otro"
(Grubbs 1969) **pendiente**: exige referencia bibliográfica nueva en `formulas-etapa1.md` y aval de los
directores. Nota de alcance: "Otro" sigue agregando a **máximos** anuales; si Catalini piensa en
variables donde el extremo es el mínimo (estiajes, temperaturas mínimas), es otra funcionalidad.

---

## 2. Bloque B — endpoint de exploración **sin id** (CU-02)

**Contexto:** desde `PR #92` el ranking de resultados es explorable en CU-01 con el endpoint que ya
existe, `POST /analysis/{id}/design-events`, que busca los `parametros` ya ajustados en la BD.
CU-02 (anónimo) no persiste nada, no tiene `analysis_id` y ese endpoint exige JWT (verificado: 401).
El componente de frontend recibe la función de exploración **por prop**, así que agregar CU-02 es
pasarle una función nueva desde `ResultsPage`; no hay que tocar el componente.

**Dos decisiones para vos antes de codear:**

1. **Nombre.** No reusar `POST /analysis/design-events`: es el de un contrato viejo que
   `api-contracts.md` marca como "reemplazado, no implementar". Propuesta: `POST /analysis/explore-design-events`.
2. **Qué manda el cliente.**
   - **Opción recomendada — la serie, el servidor reajusta.** `ejecutar_etapa2` tarda ~40 ms (medido
     n=40 y n=100). No hay que validar claves ni valores finitos de `parametros`, no se confía en
     nada del cliente, y sirve igual para el ranking simulado del bloque A.
   - Opción del plan original — el cliente manda `{distribucion, metodo, parametros, max_t_empirico}`.
     Es pura y sin estado, pero hay que validar que las claves coincidan con el módulo y que los
     valores sean finitos, y el usuario puede "engañarse" solo.

**Contrato propuesto (opción recomendada):**

```jsonc
// POST /api/v1/analysis/explore-design-events        Auth: JWT opcional
{ "serie": [94.71, 89.83, ...],              // 10..500 valores finitos
  "distribucion": "gve", "metodo": "ml",
  "periodos_retorno": [2, 5, 10, 25, 50, 100, 200, 500] }
// 200 — misma forma que POST /analysis/{id}/design-events
{ "eventos_diseno": [{"periodo_retorno": 2, "valor": 107.5}],
  "curva_ajuste":   [{"periodo_retorno": 1.05, "valor": 61.2}] }
```

**Implementación:** `ejecutar_etapa2(np.asarray(serie), tiene_ceros, tiene_negativos)` → buscar
`(distribucion, metodo)` en el ranking → si no aparece o `status != "ok"`, 400 `DIST_METHOD_NOT_FITTED`
→ `calcular_eventos_diseno()` y `_calcular_curva_ajuste()` (ambas ya existen y son las mismas que usa
`recalcular_eventos_diseno`, `analysis_service.py:995`), con `max_t_empirico` sacado de los
`puntos_empiricos` del propio resultado. Validación en el borde con `_validar_seleccion_distribucion`
(`api/v1/analysis.py:287`, compartida con los otros dos endpoints). Sin `session_store`, sin BD.

**Códigos:** `DIST_SELECTION_INVALID` y `DIST_METHOD_NOT_FITTED` ya existen. Nuevo (propuesta):
`CONTRACT_SERIES_INVALID` (400) para serie fuera de 10..500 o con valores no finitos.

**Tests:** ranking idéntico al de `ejecutar_etapa2` directo; combinación no ajustada → 400;
período ≤ 1 → 400; serie corta/larga/NaN → 400; sin cookie → 200; **equivalencia**: mismo resultado
que `POST /analysis/{id}/design-events` para un análisis persistido.

**Decisión 072** (nueva, enlazada a la 062): por qué hace falta la variante sin estado y por qué es
seguro. "Explorar no es decidir": no persiste nada ni toca `decisiones`.

---

## 3. Bloque E — desglose paso a paso y correlograma

**Pedido:** Kevin (los k lags de Anderson) y Facundo (gráficos por prueba). **Causa raíz:**
`calcular_anderson()` **ya calcula** `r_k`, el numerador y la banda superior de cada lag
(`independence.py:26-33`) y después de decidir los descarta: `Explicacion.terminos` es un dict plano
que solo guarda el lag del estadístico. El frontend no puede reconstruirlos sin recalcular estadística,
que la DECISIÓN 064 prohíbe (con razón).

**Cambios (todos aditivos):**

1. `core/types.py`: `Explicacion.desglose: list[dict[str, float | int | bool | None]] | None = None`.
2. Poblarlo, por prioridad:

   | Prueba | Filas del desglose | Prioridad |
   |---|---|---|
   | Anderson | por lag: `k, numerador, r_k, banda_inf, banda_sup, fuera` | **Alta** |
   | Chow | por observación: `i, x_i, ln x_i, z_i` (resaltar el máximo) | **Alta** |
   | Wald-Wolfowitz | por observación: `i, x_i, signo` + rachas | Media |
   | Helmert | por par consecutivo: `i, signo_i, signo_i+1, S o C` | Media |
   | Cramer / Mann-Kendall | medias de bloque / contribución parcial a S | Baja |

   ⚠️ En Anderson la banda **inferior** hoy se recalcula en línea (`independence.py:42`) y no se
   guarda: hay que guardarla sin cambiar ningún número (`(-1 - Z_CRIT·√(n-k-1))/(n-k)`).
3. **Campos nuevos en `terminos`** (cierran hallazgos de la auditoría de fórmulas, informe en
   `docs/auditoria/fases/auditoria-formulas-latex.md`): en Cramer `n1_pct` y `n2_pct` — hoy el
   frontend rotula "por `n_w`" porque con partición personalizada (DECISIÓN 036) los porcentajes ya no
   son 60/30; en t de Student el denominador `S_p·√(1/n₁+1/n₂)`, que hoy el frontend reconstruye.
4. Serialización: `test_result_dict()` (`analysis_service.py:116`) y `Explicacion` en `api/types.ts`.
   Los análisis persistidos no tienen `desglose`: llega `null` y la UI degrada a la vista actual, **sin
   backfill** (mismo criterio que DECISIÓN 058 §4).
5. **Tamaño del payload:** Anderson suma ~n/3 filas, Chow y Wald ~n. Con n≈40 es despreciable, pero
   medirlo igual (DECISIÓN 058 tiene el precedente).

**Tests:** las 9 series con veredictos, estadísticos y valores críticos **idénticos** (solo cambia la
presencia del campo nuevo); la fila del lag reportado coincide con `numerador`/`estadistico`;
`sum(fuera) == lags_fuera`. **Decisión:** addendum fechado a `decision064.md` (el principio "core
expone, frontend renderiza" no cambia; se amplía qué expone).

---

## 4. Bloque A — what-if de atípicos (`simulate-exclusion`)

**Pedido:** Catalini — desactivar puntos desde la pantalla de resultados y ver los resultados como si
no hubieran estado; si sirve, descargar la serie sin ellos. **Ya hecho (PR #93, A1):** selección con clic,
lista con checkbox y descarga del CSV, todo en frontend.

**Política decidida (Kevin, 20/09):** **eliminar** los puntos excluidos, en cualquier posición y para
las dos etapas. Es el criterio que ya aplican el rechazo de Chow, los faltantes y la agregación
temporal (uno solo en todo el pipeline: eliminar y compactar, nunca imputar). Reemplazar por la media
quedó **postergado**, no descartado: es el único lugar del producto que completaría datos; reduce la
varianza y acerca las autocorrelaciones a cero (favorece aprobar independencia); y en Etapa 2 un valor
medio entraría como si fuera un máximo anual observado. Se decide con el feedback de los directores
sobre la versión implementada.

**1. `core/pipeline/exclusiones.py` — función pura:**

```python
def aplicar_exclusiones(serie, anios, indices_excluidos, tratamiento="eliminar") -> SerieConExclusiones
# devuelve: serie, anios (sin los excluidos), excluidos: [{indice, periodo, valor_original}]
```

`tratamiento` distinto de `"eliminar"` **levanta error** (no se ignora en silencio); es el punto de
extensión si se aprueba el reemplazo por la media. Debe ser **la misma operación** que hoy hace el
rechazo de Chow (`analysis_service.py` ~600-622: quitar el valor y su timestamp por índice). **El flujo
de Chow no se toca**: la equivalencia se garantiza con el test de regresión 2, no con un refactor.

**2. Endpoint `POST /api/v1/analysis/simulate-exclusion`** (sin sesión ni BD; JWT opcional):

```jsonc
{ "serie": [...],                 // = datos.serie_efectiva, hasta 500 valores
  "anios": [2000, 2001, ...],     // = datos.timestamps_efectivos[].anio, mismo largo
  "tipo_variable": "caudal_precipitacion" | "otro",
  "cramer_particion": "default" | "{\"n1_pct\":..,\"n2_pct\":..}",   // igual que /stream
  "indices_excluidos": [3, 17],   // posiciones en `serie` (no en la serie cruda), sin repetir
  "etapas": [1] | [1, 2],
  "tratamiento": "eliminar" }     // opcional
// 200
{ "etapa1": { ...mismo payload que result_etapa1 (_serializar_etapa1)... },
  "etapa2": { "ranking": [...], "warnings": [...], "puntos_empiricos": [...], "seleccion": null } | null,
  "excluidos": [{ "indice": 3, "periodo": 2003, "valor_original": 88.0 }],
  "serie": [...], "anios": [...] }   // la serie resultante, para que el frontend genere el CSV desde lo que devolvió core
```

- Corre `ejecutar_etapa1(..., resolucion_temporal="anual")` sobre la serie resultante — igual que la
  segunda pasada de Chow: la serie ya está agregada, no se vuelve a agregar.
- **Chow se evalúa sin pausa** (como CU-03): un atípico nuevo se informa en `etapa1.atipicos`, no detiene nada.
- Con `etapas` = `[1, 2]` y `nivel_confianza != "rechazado"`, corre `ejecutar_etapa2` sobre la misma
  serie y devuelve el ranking completo (medido: ~40 ms; sincrónico alcanza, no hace falta SSE). La
  elección de distribución se hace después con el endpoint del bloque B.
- Quedan menos de 10 datos → el pipeline responde su error bloqueante de siempre
  (`CONTRACT_SERIES_TOO_SHORT`, dentro de `etapa1.contract`); **no se inventa un error nuevo**.
- **Códigos nuevos (propuesta):** `CONTRACT_EXCLUSION_INVALID` (400: índices fuera de rango o
  repetidos, `anios` de otro largo que `serie`, `tratamiento` inválido) y `CONTRACT_SERIES_INVALID` (400,
  el mismo del bloque B).
- **No persiste nada** ni toca `decisiones` (DECISIÓN 062, "explorar no es decidir").

**3. Tests:**
- Unitarios de `aplicar_exclusiones`: primero, último, interior, varios mezclados, excluir todo,
  n resultante < 10, largos de serie y años siempre iguales, `tratamiento` inválido.
- **Regresión 1:** `indices_excluidos=[]` da Etapa 1 **byte a byte idéntica** al resultado original de
  las 9 series.
- **Regresión 2:** `[indice_atipico]` da el mismo resultado que el flujo de Chow con "rechazar" para
  la misma serie. Se comparan **estadísticos, veredictos, niveles y `nivel_confianza`, no `warnings`**:
  el flujo de Chow arrastra desde la primera pasada los warnings de agregación
  (`CODIGOS_WARNING_AGREGACION`) y un endpoint sin estado no los tiene. Esto prueba que no hay dos criterios.

**4. Costo conocido y aceptado (se muestra en la UI):** al quitar un punto interior los vecinos quedan
contiguos, así que las pruebas que dependen del orden (Anderson, Wald-Wolfowitz, Cramer,
Mann-Kendall) tratan como consecutivos a dos años que no lo son — el mismo efecto que ya tiene rechazar
un atípico de Chow, señalado con el mismo warning (`CONTRACT_IRREGULAR_SPACING`).

**Decisión 071:** eliminación en todas las posiciones, coherente con el criterio vigente; reemplazo por
la media evaluado y postergado con sus tres contras; efecto sobre las pruebas de orden; por qué el
parámetro `tratamiento` está previsto; por qué no se persiste.

**Frontend que se engancha después (A2):** botón "Recalcular sin los puntos seleccionados" y una vista
comparativa (veredictos originales vs simulados, con el `n` de cada lado y los cambios resaltados). El
componente de comparación recibe **dos `Etapa1Result`**, así que la forma de `etapa1` de arriba (el
mismo payload del stream) es lo que lo hace barato.

---

## 5. Preguntas que te tocan a vos

1. **B:** ¿nombre `explore-design-events`? ¿el servidor reajusta desde la serie (recomendado) o el
   cliente manda `parametros`?
2. **A:** ¿`etapa2` dentro de la misma respuesta (propuesto) o un endpoint aparte? ¿tope de 500 valores?
   ¿`anios` como enteros (propuesto, es lo que `parsear_timestamps` ya entiende) o los timestamps normalizados?
3. **E:** ¿alcance del desglose — Anderson y Chow primero, el resto después? ¿te parece aceptable el
   crecimiento del payload (~n/3 filas por prueba)?
4. **C:** ¿código propio `TEST_NOT_EXECUTED_NEGATIVES` para Chow o se deja `TEST_NOT_EXECUTED_CONDITION`?
5. **Infraestructura:** las regresiones piden el volcado de las 9 series. El script no estaba en el repo;
   quedó documentado en el **Apéndice C** de `docs/auditoria/hallazgos/hallazgo-timestamps-desalineados.md`
   (`extract_series.py`, `regres.py`, `diff.py`). ¿Lo promovés a `tests/regression/` (que llevás vos)?
6. **Chow, valor crítico — sin acción, solo para que lo confirmes.** El código usa un test bilateral al
   10% (`t_{ν, 1−α/(2n)}`, α = 0,10): K_N = 2,176 (n=10), 2,557 (n=20), 2,745 (n=30). Con una cola
   (`t_{ν, 1−α/n}`) darían 2,036, 2,385, 2,565. Kevin decidió no tocarlo porque probablemente ya lo
   controlaste; si la tabla del Bulletin 17B trae los de una cola, `formulas-etapa1.md` §9 ("K_N=2,745
   coincide con la tabla") estaría mal. El Bulletin no está en el repo: no está verificado.

**Para Facundo/Carlos** (no bloquean backend): pregunta 6 del plan (qué gráficos por prueba considera
necesarios) y pregunta 7 (Mann-Kendall: la Tabla A.4 da 1,64 y METIS usa 1,96).

---

## 6. Verificación común y reglas del repo

- **Regresión de las 9 estaciones:** volcar `_serializar_etapa1` + `_serializar_etapa2` antes y después de
  cada cambio (36 corridas: 9 series × 2 tipos de variable × timestamps `None`/años) y comparar campo por
  campo. Resultado esperado: idéntico salvo los campos nuevos de cada bloque.
- **Correr todo dentro del contenedor** (`docker exec <backend> pytest -m "unit or integration"`, `ruff
  check metis/`, `ruff format --check metis/`); el `backend` recarga solo por el bind mount.
- **Catálogo de errores:** todo código nuevo va a `api-contracts.md` y a `frontend/src/i18n/errors.es.ts`
  **en el mismo commit** (job `error-catalog`, DECISIÓN 038).
- **Numeración de decisiones:** hacer `git fetch` y mirar el número más alto en `origin/staging` antes de
  elegir (hoy: 070, así que 071/072/073 están libres). Reservados sin archivo, no reusar: 035, 046, 049.
- **Contratos:** actualizar `api-contracts.md` (endpoints nuevos) y `statistical-pipeline.md` si cambia el payload.
- **SonarCloud** analiza cada PR (consultivo, no bloqueante). Ojo con la duplicación en tests: Sonar
  normaliza los literales, así que tests consecutivos con la misma estructura cuentan como duplicados;
  conviene `it.each`/`pytest.mark.parametrize` con tabla.

## 7. Qué NO cambia

Ningún estadístico, valor crítico ni veredicto. CU-03 (solo Etapa 1, sin estos endpoints). La
persistencia de CU-01. El flujo de Chow ("rechazar" sigue borrando el dato). `α = 5%`. El reemplazo por
la media (postergado). El valor crítico de Chow y el de Mann-Kendall (sin acción, ver §5).
