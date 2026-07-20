# DECISIÓN 030 — Elevar CONTRACT_WRONG_ORDER a error bloqueante (orden cronológico), distinto de datos faltantes
**Fecha:** 18 de Julio de 2026
**Estado:** PENDIENTE DE IMPLEMENTAR — contradice el "único caso: n<10"
documentado hoy en CLAUDE.md, architecture.md y constraints.md; esos
tres archivos deben actualizarse en la misma sesión donde esto se
implemente, no antes.

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

**Ver también:** `docs/auditoria/fases/pendientes-cableado-fase2.md`
centraliza este pendiente junto con el de [DECISIÓN 022](decision022.md)
(deuda de mantenibilidad, sin riesgo numérico) — punto único de
referencia para la próxima sesión dedicada a core/.