# Checklist de pendientes — feedback de directores (al 21/09/2026)

Para ir tildando. Cada bloque es una persona a la que hay que pedirle algo; abajo de cada ítem dice
**qué se necesita**, **qué desbloquea** y **dónde está el detalle**. Marcá `[x]` cuando esté resuelto y
anotá la fecha al lado.

Fuentes: `docs/plan-feedback-directores-20-09-2026.md` (el plan), `docs/plan-backend-feedback-directores-20-09-2026.md`
(el documento para Octavio), `docs/auditoria/pendientes/pendientes-facundo.md`, `docs/pendientes-tecnicos.md`
y `.claude/rules/architecture/constraints.md`.

---

## A quién presionar — resumen

| Persona | Qué bloquea | Ítems |
|---|---|---|
| **Octavio** | **Todo el backend del plan** (regla: se hace al final y se consulta con él): `disabled_negatives`, exploración sin id, desglose paso a paso, what-if. El frontend ya está hecho contra mocks y espera esto. | §2 |
| **Facundo** | Qué gráficos por prueba hacer (F), el valor crítico de Mann-Kendall, y las preguntas de fidelidad del core que llevan semanas abiertas. **R0.2 bloquea exponer la carga diaria en la UI.** | §3 |
| **Catalini** | Feedback sobre la versión implementada del what-if de atípicos (¿reemplazar por la media?), y qué variables tiene en mente para "Otro" con negativos. | §4 |
| **IT / UCC** | Deploy: registry de imágenes saliente, SSH desde GitHub Actions, verificación del SMTP desde adentro de la red. | §5 |
| **Kevin + Octavio** | Decisiones de gobernanza (SonarCloud como check obligatorio, decisiones con número reservado sin escribir). | §6 |
| **Kevin** | Verificar en el navegador antes de mergear este PR. | §1 |

---

## 1. Kevin — antes de mergear el PR de frontend

El repo exige (`testing.md`, Capa 4) correr el flujo en el navegador después del último commit de un PR
que toca `frontend/`. Esto **no se hizo**: la extensión de Chrome no estaba conectada.

- [ ] **Flujo completo sin flags**, en modo paso a paso y en modo experto: config → stream → resultados.
      Tiene que verse exactamente igual que antes (los tres cambios están apagados o dormidos por defecto).
- [ ] **Texto de negativos en `ConfigPage`** (ítem C): con el toggle "Otro", la nota ahora lista las
      distribuciones que quedan fuera y avisa que Chow no se ejecuta. Es lo único de este PR visible hoy.
- [ ] **Exclusión de puntos (A1, ya mergeado)** sigue funcionando: clic en el gráfico, lista con checkbox,
      descarga del CSV. No debería aparecer ningún botón "Recalcular" (está apagado).
- [ ] **Correlograma de Anderson (E+F)**: *no se ve en la app real* hasta que Octavio publique `desglose`.
      Para verlo hace falta un arnés temporal (una página con el fixture; lo armé y borré en la sesión).
      Pedile a Claude que lo recree si querés mirarlo antes de mergear.
- [ ] **Recalcular (A2)**: *no se puede probar sin el endpoint*. Con `VITE_SIMULATE_EXCLUSION=1` aparece
      el botón, pero pega a `POST /analysis/simulate-exclusion`, que hoy da 404. Solo probable contra un stub.
- [ ] Revisar que SonarCloud no marque duplicación nueva en los tests (los armé con `it.each`).
- [ ] Limpiar el usuario de prueba que pueda haber quedado en la BD local: `scripts/clean-dev-user.sh 2209999@ucc.edu.ar`
      (y verificar con `docker ps` el nombre real de los contenedores).
- [ ] Después de mergear: `git checkout staging && git pull`, y borrar las tres ramas locales
      (`feature/etapa1-desglose`, `feature/excluir-recalcular`, `feature/etapa2-negativos-frontend`).
- [ ] Sincronizar `.claude/rules/sprint.md`: no registra los PRs #88–#94 ni este (dice que el #88 está
      abierto). Pesa ~97 KB; conviene sumar una sección corta y no seguir engordándolo.

---

## 2. Octavio — backend (Tanda 2)

**Primero, revisar el documento con él:** `docs/plan-backend-feedback-directores-20-09-2026.md`. Kevin dejó
dicho que nada de `backend/` se toca sin que Octavio lo haya visto.

**Orden propuesto en el documento:** herramienta de regresión → **C → B → E → A**.

### Preguntas que tiene que contestar (§5 del documento)

- [ ] **B — nombre y forma.** ¿`POST /analysis/explore-design-events`? ¿El servidor reajusta desde la serie
      (recomendado, ~40 ms, no se confía en nada del cliente) o el cliente manda `parametros`?
- [ ] **A — contrato.** ¿`etapa2` dentro de la misma respuesta (propuesto) o endpoint aparte? ¿Tope de 500
      valores? ¿`anios` como enteros (propuesto) o timestamps normalizados?
- [ ] **E — alcance del desglose.** ¿Anderson y Chow primero, el resto después? ¿Aceptable el crecimiento
      del payload (~n/3 filas por prueba)?
- [ ] **C — código para Chow.** ¿`TEST_NOT_EXECUTED_NEGATIVES` propio o se deja `TEST_NOT_EXECUTED_CONDITION`?
- [ ] **Infraestructura de regresión.** El script de volcado de las 9 series no estaba en el repo; quedó en el
      Apéndice C de `docs/auditoria/hallazgos/hallazgo-timestamps-desalineados.md` (`extract_series.py`,
      `regres.py`, `diff.py`). ¿Lo promueve a `tests/regression/` (que lleva él)? Lo necesitan los cuatro bloques.
- [ ] **Chow, valor crítico** (solo confirmar, sin acción): el código usa un test bilateral al 10%
      (K_N(30) = 2,745); con una cola daría 2,565. Si el Bulletin 17B trae los de una cola, `formulas-etapa1.md` §9
      ("2,745 coincide con la tabla") estaría mal. El Bulletin no está en el repo: no está verificado.

### Bloques a implementar (cada uno: código + tests + verificación de las 9 estaciones idénticas)

- [ ] **C — `disabled_negatives`** (chico, independiente). Decisión 073.
- [ ] **B — endpoint de exploración sin id** (CU-02). Decisión 072.
- [ ] **E — `Explicacion.desglose`** + `n1_pct`/`n2_pct` en Cramer + denominador en t de Student. Addendum a la 064.
- [ ] **A — `aplicar_exclusiones()` + `simulate-exclusion`** (el más grande). Decisión 071.
- [ ] Cada código de error nuevo (`CONTRACT_EXCLUSION_INVALID`, `CONTRACT_SERIES_INVALID`, y `TEST_NOT_EXECUTED_NEGATIVES`
      si se hace) va a `api-contracts.md` **y** a `frontend/src/i18n/errors.es.ts` **en el mismo commit**
      (si no, falla el job `error-catalog`).

### Qué hay que hacer en el frontend cuando cada bloque aterrice

- [ ] **C:** nada obligatorio (`disabled_negatives` ya se muestra). Si hay código nuevo de Chow, agregarlo a `errors.es.ts`.
- [ ] **B:** pasarle la función `explorar` a `Etapa2Explorador` en `ResultsPage` para CU-02, y en la comparación
      del what-if para explorar el ranking simulado. Hoy el CU-02 queda de solo lectura.
- [ ] **E:** confirmar que las claves del `desglose` coinciden con las que el frontend espera
      (Anderson: `k, numerador, r_k, banda_inf, banda_sup, fuera`; Chow: `i, x_i, ln_x_i, z_i`) — si no, se ajusta
      `Etapa1Desglose.tsx` y su fixture. Quitar la aritmética cosmética de `explicaciones.ts` (rótulos de Cramer
      "por n_w" y denominador de t de Student) y mostrar el porcentaje real. Sumar Wald-Wolfowitz/Helmert si se incluyen.
- [ ] **A:** borrar el flag `VITE_SIMULATE_EXCLUSION` (`api/analysis.ts::simulacionExclusionDisponible`), armar el CSV
      con `serie`/`anios` de la respuesta en vez de en el cliente, y evaluar el botón en el historial.

### Decisiones y documentación que le tocan

- [ ] Escribir `decision071.md` (exclusión por eliminación), `decision072.md` (exploración sin estado),
      `decision073.md` (negativos con "Otro") y el addendum a `decision064.md`. Antes de elegir número:
      `git fetch` y comparar con `origin/staging` (hoy el máximo es 070).
- [ ] **`variable_diaria` (PR 2.5) no tiene decisión numerada ni addendum a la 065** — cerrarlo antes de la defensa.
- [ ] Actualizar `statistical-pipeline.md` (payload) y `api-contracts.md` (endpoints nuevos).

### Otras cosas suyas que siguen abiertas

- [ ] **Tests de regresión matemática** (`tests/regression/` vacío) — criterio de M1/M2 sin cerrar.
- [ ] **`tests/e2e/` vacío** (E2E de API que `testing.md` compromete) y después **quitar la tolerancia del exit code 5**
      del job `test` en un PR propio.
- [ ] **CU-03:** `POST /validate/` y gestión de API Keys (el modelo `api_client` existe, nada lo usa) — necesario para M7.
- [ ] **`GET /export/{id}`** — exportación PDF de CU-01, sin implementar.
- [ ] **Persistir Etapa 1 si el usuario abandona la pausa de elección de distribución** (hoy se pierde todo). Requiere
      primero una decisión de producto.

---

## 3. Facundo — dominio

### Lo nuevo de este plan

- [ ] **Gráficos por prueba (ítem F).** ¿Cuáles considera necesarios para decidir y cuáles accesorios? Lista propuesta
      (§7 del plan): correlograma de Anderson *(ya hecho, no depende de su respuesta)*; Cramer con bloques sombreados;
      KS con las dos distribuciones acumuladas y D marcado; Wald-Wolfowitz con las rachas coloreadas; boxplot para t de Student.
- [ ] **Mann-Kendall, valor crítico.** La Tabla A.4 del apéndice de Caamaño da 1,64 (una cola); METIS usa 1,96 (dos colas,
      lo que decide `pymannkendall`). ¿Se mantiene 1,96 y se documenta la divergencia, o se alinea con la fuente?
      Hasta que conteste no se cambia ningún valor.

### De la agregación temporal (`pendientes-facundo.md`, sección "Agregación temporal")

- [ ] **R0.2 — media diaria vs. pico instantáneo.** ¿Qué variable se espera en un archivo diario?
      **Bloquea exponer la carga diaria en la UI**, no la implementación.
- [ ] **R0.1** — ¿un año incompleto del medio se descarta siempre o hay un umbral? (hoy: estricto, 100%).
- [ ] **R0.3** — ¿diaria → anual directo (implementado) o encadenado diaria → mensual → anual?
- [ ] ¿El máximo anual es también la agregación correcta para `tipo_variable == "otro"`?
- [ ] ¿Con qué `mes_inicio_anio` se armaron los máximos anuales de las 9 estaciones de la tesis?

### De la fidelidad del core (`pendientes-facundo.md`)

Cada sección puede tener un addendum de cierre: revisar antes de mandar.

- [ ] **Fórmula de asimetría g (DECISIÓN 013):** METIS usa IV-4/IV-5 (ddof=0), Facundo usó `SKEW()` de Excel (ddof=1); ~4% de
      diferencia que se propaga a LP3 Indirecto y LN3p Momentos.
- [ ] **Partición de Cramer (DECISIÓN 011):** ¿qué función usa en Excel para `n_w1` y `n_w2`? La tesis no explicita el redondeo.
- [ ] **Mann-Kendall, Tabla A.4, valor crítico de S para n = 7.**
- [ ] **ME y MC:** ¿son "Mínimos Cuadrados Estándar y Corregidos"? ¿A qué otras distribuciones aplican?
- [ ] **LP3 Método Directo:** la tesis reporta parámetros y EEA con B fuera de (3, 6] en 3 estaciones; METIS aplica la restricción.
- [ ] **Log-Normal 2p:** el criterio de `NO_APLICABLE` de la tesis no es uniforme entre estaciones.
- [ ] **Gamma 3p + MPP:** la fórmula no está en el capítulo IV pese a que la Tabla IV-1 la lista.
- [ ] **Normal y Log-Normal 2p:** la Tabla IV-1 solo lista MV, no Momentos.
- [ ] **GVE Momentos — beta** no reproducible (est_02, est_03, est_05); **Gamma 3p MV** (est_06, est_08);
      **una cola vs. dos colas** en est_08 (Cramer/t de Student).
- [ ] **El Excel de la planilla.** Sin él no se pueden explicar las discrepancias de EEA (Causa C) ni los cuantiles de LN3p MV est_05
      y est_04. Es lo que más destraba.

---

## 4. Catalini

- [ ] **Mostrarle la versión implementada del what-if de atípicos** (ítem A). Se postergó a propósito decidir si los huecos
      interiores se tapan con la media: hoy se **eliminan**. Las tres razones para no arrancar con la media, para llevarle:
      es el único lugar del producto que completaría datos; reduce la varianza y acerca las autocorrelaciones a cero (favorece
      que la serie apruebe independencia); y en Etapa 2 un valor medio entraría como si fuera un máximo anual observado.
      *Nota:* recién se puede mostrar completo cuando esté el backend (§2, bloque A); hoy solo se ve la selección y la descarga.
- [ ] **Valores negativos con "Otro" (ítem C).** ¿Qué variables tiene en mente (niveles referidos a un cero de escala,
      temperaturas, anomalías)? Kevin ya eligió la opción 3 (estado propio `disabled_negatives`); confirmar que le sirve.
- [ ] **Chow sin logaritmos para "Otro"** (opción 2 del plan §4, Grubbs 1969): sigue pendiente; exige referencia bibliográfica
      nueva en `formulas-etapa1.md` y su aval.
- [ ] **Alcance de "Otro":** METIS sigue agregando a **máximos** anuales. Si piensa en variables donde el extremo es el mínimo
      (estiajes, temperaturas mínimas), es otra funcionalidad.
- [ ] **Explorar otras distribuciones desde resultados (ítem B):** ya funciona en CU-01; en CU-02 espera el endpoint (§2).
      Mostrarle CU-01 y confirmar que es lo que pidió.

---

## 5. IT / UCC — despliegue

Decisión de referencia: `docs/decisiones/decision028.md`. El deploy real lo haría Facundo. Acceso al servidor de contenedores
(portal institucional, usuario de dominio) confirmado el 18/07/2026.

- [ ] **Registry de imágenes saliente** (Docker Hub o GitHub Container Registry): ¿el servidor puede salir a buscarlas?
- [ ] **Acceso SSH desde GitHub Actions** al servidor, y restricciones de firewall.
- [ ] **Docker disponible** en los servidores de la UCC.
- [ ] **SMTP desde adentro de la red:** el smoke test se hizo desde red doméstica. Falta verificar desde el servidor real
      (`wally.uccor.edu.ar:587`): alcanzabilidad, resolución DNS interna (por si hay split-horizon), coincidencia de
      certificado/hostname, y el deploy real en sí.
- [ ] Cuando exista el compose de producción: mover `--reload` y el bind mount a un `docker-compose.override.yml`.

---

## 6. Kevin + Octavio — decisiones de gobernanza

- [ ] **SonarCloud como check obligatorio** en el Ruleset (hoy es consultivo: con el gate en rojo el botón de merge sigue
      habilitado). Requiere login en GitHub/SonarCloud. Ver `decision044.md`.
- [ ] Escribir las decisiones con número reservado y sin archivo: **035** (Ruleset de ramas), **046** (E2E con Playwright:
      contradice `constraints.md`, hay que revisar esa exclusión primero) y **049** (escotilla SMTP de desarrollo, que permitiría
      probar registro → verify sin SMTP real).
- [ ] Confirmar cuál es el hito activo hoy (M1/M2 tienen criterios abiertos; M3 no se cumple sin export y validate).

---

## 7. Deuda técnica sin dueño externo

Se puede hacer sin esperar a nadie (`docs/pendientes-tecnicos.md` tiene el detalle):

- [ ] Mover el chequeo de espaciado antes de la agregación (`_espaciado_regular()` es inerte para series agregadas). PR propio.
- [ ] Refactor de la DECISIÓN 022 (`_skewness` ×5, M̂ ×3 duplicados en `etapa2/`).
- [ ] Fix simétrico de la DECISIÓN 038 en `trend.py` (el `TEST_WARNING_SMALL_SAMPLE` de Mann-Kendall no llega a la lista agregada).
- [ ] Búsqueda del historial por nombre de archivo; `tipo_variable` extensible (hoy cerrado a dos valores).
- [ ] Después de M5: pruebas adicionales que confirmó Carlos (Durbin-Watson, Ljung-Box, Mann-Whitney, Mood, Spearman, Kn).

---

## 8. Ya cerrado — no perseguir

- ~~Chow, valor crítico~~ — confirmado por Carlos (addendum de DECISIÓN 018). La verificación de una cola vs. dos colas sigue
  como confirmación de Octavio (§2), no como pregunta a los directores.
- ~~Ceros en Gamma 3p, Exponencial x₀-β, Gen. Pareto, LN3p, Gen. Exponencial~~ — política definitiva (addendum de DECISIÓN 061).
  Ojo: `pendientes-facundo.md` todavía tiene el texto viejo de esa sección.
- ~~Umbral de `DIST_HIGH_EEA`~~ — DECISIÓN 070, se mantiene en 5%.
- ~~Gen. Pareto por Mínimos Cuadrados (IV-153)~~ — cerrado el 04/09/2026 (DECISIÓN 068).
- ~~Gen. Exponencial Momentos-L~~ — cerrado el 09/09/2026 (DECISIÓN 069): era un desfasaje de índice, no una nota faltante.
- ~~`timestamps_efectivos` desalineado de `serie_efectiva`~~ — PR #90.
- ~~Preguntas 1 a 5 del plan a Catalini~~ — cerradas por Kevin el 20/09/2026 (el what-if elimina, sin imputar; el flujo de Chow no se toca).
