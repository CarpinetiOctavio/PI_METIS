# DECISIÓN 026 — Ancla de trazabilidad para requerimientos externos (RF-XXX)
**Fecha:** 17 de Julio de 2026
**Estado:** ESTABLECIDA — aplicar a toda cita futura de RF-XXX en el repo

### Contexto
Durante la reorganización de `full_pipeline.py` (sesión de reorganización
de repo, pre-commit de `feature/core-etapa2`), se citó `RF-GEN-P-03`
(principio de no-bloqueo de Etapa 2 ante warnings de Etapa 1, sin
distinguir crítico/normal) en un docstring y en un test. El identificador
es válido y existe en METIS — Manual de Requerimientos v2.0, pero ese
documento no vive en ningún lugar del repositorio — la cita no era
verificable por nadie que clonara el repo sin acceso externo al manual.

### Opciones evaluadas
Duplicar el manual completo dentro del repo (`docs/requisitos/` con el
PDF o una transcripción) — descartado: crea dos copias del mismo
contenido con riesgo de desincronización si el manual se actualiza, y es
sobre-alcance para lo que necesita un repositorio de código.

### Decisión
El manual permanece externo al repo, gestionado por separado. Se
documenta el ancla de trazabilidad en `docs/README.md`, sección
"Trazabilidad de requerimientos (RF-XXX)": qué documento es, quién lo
autoría, y que toda cita `RF-XXX` en el repo corresponde a esa versión.
Cualquier cita futura a un RF debe poder resolverse a través de esa
ancla sin necesidad de acceso al PDF original para saber de dónde sale
el identificador.

### Alcance
Aplica a toda cita `RF-XXX` presente o futura en código, tests o
documentación de este repositorio. Si el Manual de Requerimientos se
actualiza a una versión posterior, `docs/README.md` debe reflejar la
versión vigente y confirmar que las citas existentes siguen siendo
válidas contra el nuevo contenido.
