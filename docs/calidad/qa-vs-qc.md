# Aseguramiento (QA) y control (QC) de la calidad en METIS

TP integrador de Calidad de Software, bloque B9. METIS hace las dos cosas, pero hasta este documento no estaban
separadas. **QA** actúa sobre el proceso, para que los defectos no se produzcan; **QC** actúa sobre el producto,
para encontrar los que igual se produjeron.

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0 | 09/10/2026 | Primera versión |

## 1. Prácticas de aseguramiento (proceso)

| Práctica | Qué previene | Dónde está |
|---|---|---|
| **Decisiones registradas** antes del código que las aplica, con contexto, alternativas y consecuencias | Cambios de comportamiento sin justificación; repetir una discusión ya cerrada | `docs/decisiones/` (75 archivos) |
| **Ninguna fórmula sin referencia** a la ecuación de la tesis | Implementar de memoria o desde otra fuente (el origen de D-08 y D-09) | `formulas-etapa{1,2}.md` |
| **`core/` aislado** de HTTP, base y sesiones | Que el motor dependa de la infraestructura y deje de ser testeable por separado | Regla de `CLAUDE.md` y `architecture.md` |
| **GitHub Flow con ruleset**: ramas desde `staging`, PR obligatorio, push directo bloqueado | Código sin revisar ni verificar en las ramas de integración | `constraints.md`, ruleset del repo |
| **Definition of Done** de un PR: los jobs de CI en verde; evidencia en navegador si toca el frontend; issue cerrado con test si corrige un defecto | Mergear algo que "pasa los tests" pero no funciona (F1) | `CLAUDE.md`, `testing.md` (Capa 4), `plan-de-pruebas.md` §6.3 |
| **Catálogo de errores sincronizado** en backend, contratos y frontend en el mismo commit | Un error que el usuario ve como texto genérico | Regla de `CLAUDE.md`; job `error-catalog` |
| **Gate de calidad** sobre el código nuevo (cobertura ≥ 80 %, duplicación ≤ 5 %) | Deuda nueva sin probar | Job `quality-gate` (DECISIÓN 077) |
| **Contexto para los agentes** que asisten el desarrollo (`CLAUDE.md`, `.claude/rules/`) | Que una sesión nueva repita un error ya corregido o contradiga una decisión | `CLAUDE.md` y `.claude/rules/` |
| **Plan de pruebas, riesgos y objetivos** escritos y versionados | Probar lo fácil en lugar de lo riesgoso | `plan-de-pruebas.md`, `riesgos.md`, `objetivos-de-calidad.md` |
| **Registro de defectos** con plantilla y criterio de cierre | Corregir sin dejar una prueba que impida que vuelva | `registro-defectos.md` |

## 2. Actividades de control (producto)

| Actividad | Qué encuentra | Dónde está |
|---|---|---|
| **Tests automáticos** en cuatro niveles (unidad, integración, sistema, carga) | Regresiones y desvíos del comportamiento esperado | `plan-de-pruebas.md` §5.1 |
| **Auditoría de fórmulas en 4 fases** contra las 9 estaciones de la tesis | Errores de transcripción de fórmulas (D-08, D-09) | `docs/auditoria/fases/` |
| **Comparación con otras herramientas** (R, SciPy, LibreOffice, SAMHIA) | Divergencias de definición y errores de la referencia misma (la U_T de la planilla) | `docs/auditoria/comparacion-herramientas/` |
| **Hallazgos dirigidos**: revisión de un tema puntual del código | Defectos que ningún test buscaba (D-04, D-05) | `docs/auditoria/hallazgos/` |
| **Revisión de PR** y análisis de SonarCloud | Bugs, code smells, hotspots de seguridad | Cada PR |
| **Casos de caja negra** | Bordes, clases y combinaciones sin probar | `casos-de-prueba.md` |
| **Verificación en navegador** y E2E | Fallas que solo aparecen con el sistema completo | Capa 4, `frontend/e2e/` |
| **Revisión de los directores** en uso real | Resultados o rótulos que no tienen sentido para el dominio (DECISIÓN 076) | Reuniones; `docs/checklist-pendientes-feedback-directores.md` |

## 3. Cómo se conectan

Un defecto que encuentra el control se convierte en una mejora del aseguramiento, para que esa clase de defecto no
vuelva a producirse:

| Defecto (QC) | Cambio de proceso que dejó (QA) |
|---|---|
| D-01: el stream se abortaba bajo StrictMode, con 98 tests en verde | Todo test de página corre bajo `StrictMode` por regla; la Capa 4 entró en la DoD |
| D-08 y D-09: fórmulas mal transcritas | Regla de "ninguna fórmula sin referencia a la ecuación" y `formulas-etapa{1,2}.md` como fuente única |
| D-07: errores envueltos en `detail`, el frontend mostraba texto genérico | Estructura de error estándar garantizada por un manejador global, con su test; el E2E-1 la verifica |
| F1, F4, F5, F6 y F9: solo visibles con el sistema completo | E2E con Playwright en el pipeline (DECISIÓN 046) |
| La base sin migrar respondía 500 (05/08/2026) | El despliegue corre las migraciones siempre y el smoke prueba la base |
