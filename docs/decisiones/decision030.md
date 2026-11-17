# DECISIÓN 030 — Elevar CONTRACT_WRONG_ORDER a error bloqueante (orden cronológico), distinto de datos faltantes
**Fecha:** 18 de Julio de 2026 — **aplicada** 18 de Agosto de 2026 (Bloque H3
del [plan post-avance](../plan-post-avance.md)).
**Estado:** Aplicada. Ver "Cerrado (18/08/2026)" más abajo para la
implementación real, verificación contra las 9 series de referencia, y un
segundo hallazgo más grave que esta decisión original no contemplaba
(pérdida silenciosa de períodos en la agregación mensual). El resto del
documento queda como diagnóstico y decisión histórica, sin reescribir.

### Contexto
Durante las primeras reuniones de recopilación de requerimientos con
Facundo (según recuerda Octavio; no quedó registrado con precisión en
la toma de notas de esa etapa, por falta de tiempo en el momento),
Facundo indicó que las series de estaciones hidrológicas siempre se
ingresan en orden cronológico ascendente por año — es una garantía de
dominio, no una condición a validar caso por caso. Facundo enmarcó
esto en términos de responsabilidad: quien usa el software es
responsable de ingresar los datos correctamente.

`pendientes-cableado-fase2.md` documenta que `calcular_cramer` toma
`arr[-n_w:]` asumiendo orden cronológico sin validarlo, y que
`contract.py` ya detecta desorden (`CONTRACT_WRONG_ORDER`) pero lo
trata como warning nivel `normal`, no bloqueante — el pipeline
continúa sin corregir el orden.

### Por qué esto amerita una segunda excepción al principio de no bloqueo
La responsabilidad del usuario ya es el fundamento del comportamiento
no bloqueante en el resto del sistema (RF-GEN-P-03) — por sí sola, esa
frase no distingue por qué el orden cronológico debería tratarse
distinto de, por ejemplo, un warning crítico de homogeneidad. La
distinción real es estructural: en los warnings existentes, el
resultado sigue siendo válido aunque subóptimo (el usuario puede
interpretarlo con la salvedad en mano). El desorden cronológico es de
otra naturaleza — si Cramer toma `arr[-n_w:]` asumiendo que son los
últimos datos cronológicos y no lo son, el resultado no mide lo que
dice medir. Es estructuralmente más cercano al caso de n<10 (falta la
condición mínima para que el estadístico tenga sentido) que a un
warning típico.

### Decisión
Elevar `CONTRACT_WRONG_ORDER` a error bloqueante — segunda excepción
al principio de no bloqueo, junto a n<10. Datos faltantes (fechas sin
valor, o valores sin fecha ya contemplados en el contrato) NO se ven
afectados por esta decisión — siguen su tratamiento actual, no
bloqueante. La distinción es exclusivamente sobre el **orden** de la
serie, no sobre su completitud.

### Pendiente de implementación
- Modificar `contract.py` para que `CONTRACT_WRONG_ORDER` bloquee el
  pipeline (mismo tratamiento que el bloqueo actual de n<10).
- Escribir tests que distingan explícitamente "desorden bloquea" de
  "datos faltantes no bloquea", sin mezclar los dos casos.
- Verificar contra las 9 series de referencia de Fase 4 que ninguna
  tiene desorden cronológico que ahora empezaría a bloquear donde
  antes pasaba con warning (si alguna lo tuviera, este cambio
  invalidaría resultados ya auditados y cerrados en Fase 4 — revisar
  antes de implementar).
- Actualizar `CLAUDE.md`, `architecture.md` y `constraints.md`, que
  hoy documentan "único caso: n<10" — dejaría de ser cierto.
- Ver `docs/auditoria/fases/pendientes-cableado-fase2.md` para el
  detalle técnico completo del hallazgo original en `calcular_cramer`.

---

### Cerrado (18/08/2026) — Bloque H3 del plan post-avance

**Paso 1 — verificación contra las 9 series de referencia, primero.**
Se leyeron las 9 transcripciones de
`docs/auditoria/regresion/regresion-unitaria/est_0[1-9]*.md` (los
comentarios `# NN-NN` de cada elemento de `serie`, que rotulan la
temporada hidrológica de cada dato) — **ninguna de las 9 tiene desorden
cronológico**, incluidos los huecos "S/D" (que interrumpen la serie pero
nunca invierten el orden). Este cambio no invalida ningún resultado ya
auditado y cerrado en la Fase 4.

**Paso 2 — un segundo problema, más grave, que esta decisión original no
contemplaba.** Encontrado leyendo el código durante la implementación (ver
también H3 en `plan-post-avance.md`, escrito antes de tocar código):
`core/validacion/aggregation.py::agregar_a_maximos_anuales()` toma
`timestamps[0]`/`timestamps[-1]` como el dato más antiguo/reciente del
registro para fijar `range(periodo_inicio, periodo_fin + 1)` — el rango de
períodos que agrega. Con un archivo desordenado, ese rango puede excluir
períodos reales del registro **en silencio**: verificado antes de
implementar (contra el código sin parchear) que 3 años completos de datos
mensuales (36 meses reales), con dos bloques anuales invertidos entre sí
(orden real: 2000, 2002, 2001), agregaban solo **2** años —
`periodos_descartados=[]`, sin ningún warning — el año 2002 completo
desaparecía sin dejar rastro. Peor todavía: **evaluar el orden después de
agregar (como hacía `validar_contrato()` antes de este bloque) es código
muerto para cualquier serie mensual** — `agregar_a_maximos_anuales()`
construye sus propios timestamps con `range()`, siempre ascendentes por
construcción, así que el desorden de origen ya se perdió para cuando
`validar_contrato()` los vería.

**Implementación real:**

1. `core/validacion/contract.py::timestamps_desordenados()` — función pura
   nueva, extraída de la lógica que antes vivía inline en
   `validar_contrato()` (comparación directa `!=`/`sorted()`, funciona
   igual para años enteros y fechas ISO-8601 de texto — es la aritmética
   de fechas, no la comparación, la que falla para texto).
2. `core/pipeline/pipeline_etapa1.py::ejecutar_etapa1()` — nuevo paso 0a,
   **antes** del paso 0 (agregación): si `timestamps is not None and
   timestamps_desordenados(timestamps)`, retorna
   `Etapa1Result(contract=ContractResult(bloqueante=True,
   codigo_error="CONTRACT_WRONG_ORDER", warnings=[]), nivel_confianza="rechazado", ...)`
   — mismo tratamiento que `CONTRACT_SERIES_TOO_SHORT`.
3. `validar_contrato()` **pierde** el chequeo de orden por completo (era
   el único lugar donde vivía) — ya no tiene sentido ahí por los dos
   motivos del "Paso 2" de arriba.
4. `services/analysis_service.py` no cambió — el camino `contract_error`
   SSE ya era genérico sobre `result.contract.codigo_error`, cualquier
   código bloqueante nuevo fluye sin tocar nada ahí.
5. Frontend: `CONTRACT_WRONG_ORDER` se movió del grupo warning al
   bloqueante en `errors.es.ts`, con el mensaje reescrito para reflejar
   que ya no se puede analizar — el manejo de `contract_error` en
   `useAnalysisStream` ya era genérico, sin cambios de lógica.

### Criterio de hecho
- `tests/unit/core/pipeline/test_pipeline_etapa1.py` — cuatro tests
  nuevos: desorden bloquea (serie anual), datos faltantes en orden NO
  bloquean (distinción explícita, sin mezclar los dos casos), sin
  timestamps no evalúa nada, y el test específico del bug de agregación
  (3 años completos desordenados → antes perdía uno en silencio, ahora
  bloquea antes de llegar a agregar).
- `tests/unit/core/validacion/test_contract.py` — el test que antes
  verificaba el warning ahora verifica que `validar_contrato()` en
  aislamiento ya NO detecta el desorden (la responsabilidad se movió, no
  desapareció — el test real vive en `test_pipeline_etapa1.py`).
- `pytest -m "unit or integration"` en verde (338 passed, 1 skipped, +4
  sobre la línea base).
- `CLAUDE.md`, `.claude/rules/architecture/api-contracts.md` y
  `.claude/rules/core/statistical-pipeline.md` actualizados en el mismo
  commit — dejan de decir "único caso: n<10".

**Ver también:** `docs/auditoria/fases/pendientes-cableado-fase2.md`
centraliza este pendiente junto con el de [DECISIÓN 022](decision022.md)
(deuda de mantenibilidad, sin riesgo numérico) — punto único de
referencia para la próxima sesión dedicada a core/.