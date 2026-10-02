# Planes implementados — índice

**Qué es.** Un resumen, en orden cronológico, de cada plan de implementación que se ejecutó en el proyecto: qué pedía,
qué se hizo de verdad, qué decisiones dejó y qué quedó abierto. Es lo que se lee; los planes originales están
archivados tal cual en [`historico/planes/`](historico/planes/) y se consultan solo si hace falta el detalle.

**Criterio.** Una entrada por **frente de trabajo**, no por archivo: el plan, su informe de resultados y su revisión van
juntos. Fechas y PRs sacados de `git log` y `gh pr list` (01/10/2026), no de lo que dice cada plan: varios quedaron con
estados atrasados (por ejemplo, "PR abierto" sobre algo ya mergeado). Antes de archivar cada plan se verificó que todo
pendiente que siguiera abierto figure en un documento vivo: [`pendientes-tecnicos.md`](pendientes-tecnicos.md),
[`checklist-pendientes-feedback-directores.md`](checklist-pendientes-feedback-directores.md),
[`auditoria/pendientes/pendientes-facundo.md`](auditoria/pendientes/pendientes-facundo.md) o
[`frontend/frontend-implementation-plan.md`](frontend/frontend-implementation-plan.md) §10. Archivar no es una forma
de que algo abierto desaparezca.

**No están acá** porque no son planes sino documentos vivos: `frontend/frontend-implementation-plan.md` (fuente de
verdad decisión por decisión del frontend, §10), `frontend/frontend-integration.md`, `pendientes-tecnicos.md`,
`decisiones/` y `auditoria/`. El backend de Etapa 1 y Etapa 2 (PRs #1 a #16) se hizo antes de que existiera esta
convención de planes en `docs/`; su historia está en `docs/sprint.md` y en `auditoria/`.

---

## Planes activos (no archivados)

| Plan | Qué es |
|---|---|
| [`plan-feedback-directores-20-09-2026.md`](plan-feedback-directores-20-09-2026.md) | Feedback de Catalini y Facundo del 20/09: ítems A a F. Frontend hecho (PRs #91 a #95). |
| [`plan-backend-feedback-directores-20-09-2026.md`](plan-backend-feedback-directores-20-09-2026.md) | Los contratos de backend de ese feedback. C, E y A los ejecutó el frente 16; falta el bloque B. |
| [`checklist-pendientes-feedback-directores.md`](checklist-pendientes-feedback-directores.md) | Pendientes por persona (Octavio, Facundo, Catalini, IT, Kevin). |

Se archivan acá cuando cierren, con su entrada en esta tabla.

---

## Resumen

| # | Frente | Fechas | PRs | Decisiones |
|---|---|---|---|---|
| 1 | [Frontend, Fases 1 a 6](#1-frontend-fases-1-a-6) | 22–29/07 | #17 | 039–042 |
| 2 | [Pasada 2 de mejora del frontend](#2-pasada-2-de-mejora-del-frontend) | 29–30/07 | #18 | 036, 037, 038, 043 (propuesta) |
| 3 | [Pasada 3 (cierre de Fase 6)](#3-pasada-3-cierre-de-fase-6) | 29/07 | #18 | — |
| 4 | [Limpieza de SonarCloud](#4-limpieza-de-sonarcloud) | 29–30/07 | #18 | 044 |
| 5 | [Arreglo de la UI rota en uso real](#5-arreglo-de-la-ui-rota-en-uso-real) | 31/07 | #19 | 046 y 049 reservadas |
| 6 | [Feedback de UX del 31/07](#6-feedback-de-ux-del-3107) | 31/07 | (repartido) | 047, 048 |
| 7 | [Pasada 4: identidad visual](#7-pasada-4-identidad-visual) | 31/07–01/08 | #20, #22, #23 | 045, 047, 048 |
| 8 | [Roadmap post-pasada 4](#8-roadmap-post-pasada-4) | 05/08 | #24 a #28 | 050 |
| 9 | [Pasada 5: pulido visual](#9-pasada-5-pulido-visual) | 06–09/08 | #37 a #41 | 051 |
| 10 | [Etapa 2 de punta a punta](#10-etapa-2-de-punta-a-punta) | 09–12/08 | #42 a #50 | 052–057 |
| 11 | [Cierre de pendientes no-test](#11-cierre-de-pendientes-no-test) | 12/08 | #51 a #56 | 058 |
| 12 | [Fixes pre-reunión](#12-fixes-pre-reunión) | 13–14/08 | #57 a #60 | — |
| 13 | [Plan post-avance](#13-plan-post-avance) | 14–19/08 | #61 a #75 | 030, 036, 043, 059–064 |
| 14 | [Resolución diaria](#14-resolución-diaria) | 28–29/08 | #77 a #82 | 065, 066, 067 |
| 15 | [Feedback de Facundo del 02/09](#15-feedback-de-facundo-del-0209) | 02–15/09 | #88 | addendum 064 |
| 16 | [Fixes post-verificación y Tanda 2 de backend](#16-fixes-post-verificación-y-tanda-2-de-backend) | 01/10 | #96 a #101 | 071, 073, 074, addendum 064 |

Entre los frentes 7 y 9 hubo además fixes visuales y experimentos sueltos sin plan propio (PRs #29 a #36: fondos
animados invisibles, blur del modal, Pill Nav, Magnet, Spotlight, Threads con three.js). Threads con three.js lo
revirtió la pasada 5 (DECISIÓN 051).

---

## 1. Frontend, Fases 1 a 6

- **Fechas y PRs:** 22 a 29/07/2026 (scaffold de Fase 0 del 22/07, en `historico/`); mergeado como **#17** el 30/07.
- **Qué pedía:** pasar del scaffold a la integración real contra el backend: auth, configuración y stream de Etapa 1,
  resultados en tres modos, historial y mocks de Etapa 2.
- **Qué se hizo:** las cinco fases con verificación E2E contra Docker. Dos bugs reales de `useAnalysisStream`
  aparecieron recién en esa verificación (`complete` pisando un error; `result_etapa1` sin desenvolver). Fase 6
  (pulido y accesibilidad) quedó parcial y la cerraron las pasadas 3 y el plan post-avance.
- **Decisiones:** 039 (criterio de promoción), 040 (SSE sobre fetch), 041 (sin TanStack Query, un solo patrón de mock),
  042 (mocks de Etapa 2, superada el 09/08).
- **Quedó abierto:** registro → verify sin SMTP real (checklist §6, DECISIÓN 049 reservada); P1 (CORS y cookie
  `Secure` en producción) y P3 (azul institucional) en `frontend-implementation-plan.md` §10.
- **Archivo:** [`historico/planes/frontend/informe-implementacion-frontend-fase1-6.md`](historico/planes/frontend/informe-implementacion-frontend-fase1-6.md).

## 2. Pasada 2 de mejora del frontend

- **Fechas y PRs:** 29 a 30/07; rama `fix/frontend-pasada2`, mergeada como **#18** junto con las pasadas 3 y la
  limpieza de SonarCloud.
- **Qué pedía:** reintegrar a la documentación del proyecto lo que las Fases 1 a 5 habían dejado escrito solo en sus
  propios archivos, y escalar tres hallazgos de backend que nadie había registrado.
- **Qué se hizo:** bloques A a E completos. Los hallazgos de backend quedaron como decisiones; un `fix-sonarcloud-pr18.md`
  aparte resolvió el primer quality gate (85 de los ~100 issues eran prototipos de diseño mal excluidos).
- **Decisiones:** 036 (partición de Cramer inalcanzable), 037 (`etapas` descartado), 038 (catálogo de errores como fuente
  única), propuesta de 043 (contraste WCAG).
- **Quedó abierto:** nada vigente; 036, 037 y 043 se cerraron después (frentes 10 y 13).
- **Archivo:** [`historico/planes/frontend/plan-mejora-frontend-pasada2.md`](historico/planes/frontend/plan-mejora-frontend-pasada2.md),
  [`informe-pasada2-resultados.md`](historico/planes/frontend/informe-pasada2-resultados.md),
  [`fix-sonarcloud-pr18.md`](historico/planes/frontend/fix-sonarcloud-pr18.md).

## 3. Pasada 3 (cierre de Fase 6)

- **Fechas y PRs:** 29/07, misma rama que la pasada 2, dentro de **#18**.
- **Qué pedía:** cerrar los huecos que encontró una revisión independiente de la pasada 2 y terminar Fase 6.
- **Qué se hizo:** `pytest -m unit` corrido por primera vez de punta a punta (vía Docker: 131 passed); la dirección
  frontend → catálogo de errores que faltaba; auto-foco, Escape y restauración de foco en el modal de atípico. El
  merge a `staging` se difirió (lo hizo el #18).
- **Quedó abierto:** nada vigente.
- **Archivo:** [`plan-mejora-frontend-pasada3.md`](historico/planes/frontend/plan-mejora-frontend-pasada3.md),
  [`informe-pasada3-resultados.md`](historico/planes/frontend/informe-pasada3-resultados.md).

## 4. Limpieza de SonarCloud

- **Fechas y PRs:** 29 a 30/07, dentro de **#18**.
- **Qué pedía:** resolver los 61 issues del PR #17 y documentar SonarCloud, que no figuraba en ningún lado.
- **Qué se hizo:** el gate rompía por solo 6 issues (Reliability y Security en C); se corrigieron los 61. Se descartó
  `<dialog>` nativo a propósito (N3, *Won't fix*).
- **Decisiones:** 044.
- **Quedó abierto:** si SonarCloud pasa a check *required* (checklist §6).
- **Archivo:** [`plan-limpieza-sonarcloud.md`](historico/planes/frontend/plan-limpieza-sonarcloud.md),
  [`informe-limpieza-sonarcloud-resultados.md`](historico/planes/frontend/informe-limpieza-sonarcloud-resultados.md).

## 5. Arreglo de la UI rota en uso real

- **Fechas y PRs:** 31/07; **#19**.
- **Qué pedía:** dos PRs se habían mergeado con CI verde y la app estaba rota en uso real (el stream se abortaba solo
  bajo `StrictMode`). Diagnóstico de doce defectos (F1 a F12) y plan priorizado.
- **Qué se hizo:** los doce, más la estrategia de testing por capas que hoy está en `.claude/rules/testing.md`
  (`renderPage` bajo `StrictMode`, tests de integración componente + hook, Capa 4 de verificación en navegador),
  `scripts/seed-dev-user.sh` y el primer build estático servido por nginx.
- **Decisiones:** reservó 046 (E2E con Playwright) y la escotilla SMTP (hoy 049); ninguna escrita.
- **Quedó abierto:** 035, 046 y 049 sin escribir (checklist §6).
- **Archivo:** [`informe-diagnostico-ui-rota.md`](historico/planes/frontend/informe-diagnostico-ui-rota.md),
  [`plan-arreglo-ui-rota.md`](historico/planes/frontend/plan-arreglo-ui-rota.md),
  [`informe-resultados-arreglo-ui-rota.md`](historico/planes/frontend/informe-resultados-arreglo-ui-rota.md).

## 6. Feedback de UX del 31/07

- **Fechas y PRs:** relevado el 31/07; resuelto en varios frentes.
- **Qué pedía:** cinco observaciones al probar la app: identidad visual, columnas por dropdown, tipo de variable
  extensible, badge de "datos de ejemplo", archivar y buscar en el historial.
- **Qué se hizo:** identidad visual (pasadas 4 y 5), dropdown de columnas (DECISIÓN 047), badge reformulado y luego
  borrado con los mocks, archivado por soft-delete (DECISIÓN 048), nombre de archivo en el historial (frente 12).
- **Quedó abierto:** búsqueda del historial por nombre de archivo y `tipo_variable` extensible (checklist §6).
- **Archivo:** [`feedback-ux-pendiente-analisis.md`](historico/planes/frontend/feedback-ux-pendiente-analisis.md).

## 7. Pasada 4: identidad visual

- **Fechas y PRs:** 31/07 a 01/08; tres PRs apilados: **#20** (identidad, interacción, fondos animados), #21 (columnas
  por dropdown, mergeado dentro de la pila) y **#22**/**#23** (archivado de historial y badge).
- **Qué pedía:** tipografía real, tokens de movimiento, estados de interacción, fondos animados en Canvas 2D, `TopBar`
  dentro del design system, columnas por dropdown y archivado.
- **Qué se hizo:** todo lo pedido; cinco puntos de su verificación final quedaron sin verificar y los cerró el
  frente 8.
- **Decisiones:** 045 (fondos en Canvas 2D), 047 (`preview-columns`), 048 (soft-delete).
- **Quedó abierto:** nada vigente.
- **Archivo:** [`plan-mejora-frontend-pasada4.md`](historico/planes/frontend/plan-mejora-frontend-pasada4.md),
  [`informe-resultados-pasada4.md`](historico/planes/frontend/informe-resultados-pasada4.md).

## 8. Roadmap post-pasada 4

- **Fechas y PRs:** 05/08; su "Pasada 5 de deuda" salió en **#24** a **#28** (límite de subida de 10 MB, higiene de
  decisiones por la colisión del número 045, Cramer personalizada responde 400 y no 500, columna de año puro, aviso de
  que las migraciones no corren solas).
- **Qué pedía:** evaluar la calidad de las dos pasadas anteriores y ordenar el alcance restante hacia M2 y M3 en
  pasadas 5 a 8.
- **Qué se hizo:** la pasada 5 de deuda. Las otras se absorbieron en planes posteriores: la 6 (Etapa 2 real) es el
  frente 10, la 7 (feedback de UX) los frentes 12 y 13. Los números de decisión que proponía para esas pasadas
  (051 a 053) terminaron usados para otros temas.
- **Decisiones:** 050.
- **Quedó abierto:** la pasada 8, exportación PDF y CU-03 (checklist, "sin implementar").
- **Archivo:** [`plan-post-pasada4-roadmap.md`](historico/planes/plan-post-pasada4-roadmap.md).

## 9. Pasada 5: pulido visual

- **Fechas y PRs:** 06 a 09/08; **#37** a **#40** apilados, cierre documental en **#41**.
- **Qué pedía:** paridad del tema claro en los fondos, el tercer fondo animado, elevación de cards, `TopBar` de vidrio,
  dropzone de carga con panel de columnas y blur del modal de atípico.
- **Qué se hizo:** todo, y `three` salió del proyecto (Threads reescrito en Canvas 2D).
- **Decisiones:** 051.
- **Quedó abierto:** nada vigente.
- **Archivo:** [`plan-mejora-frontend-pasada5.md`](historico/planes/frontend/plan-mejora-frontend-pasada5.md),
  [`informe-resultados-pasada5.md`](historico/planes/frontend/informe-resultados-pasada5.md).

## 10. Etapa 2 de punta a punta

- **Fechas y PRs:** 09 a 12/08; **#42** a **#50** (bloques 0, A0, A1-A3, A4-A6, B, C, F2, F3-F4, F5).
- **Qué pedía:** cablear el motor de Etapa 2 al stream con pausa, frontend real sin mocks, gráficos interactivos y
  agregación temporal por año hidrológico. El propio plan decía "se elimina cuando la implementación cierra"; se
  archiva en vez de borrarse porque varias decisiones lo citan.
- **Qué se hizo:** todo lo anterior. El bloque D (regresión matemática) se retiró del plan porque lo lleva Octavio; el
  bloque F se rediseñó a un solo parámetro `mes_inicio_anio`; el bloque E (PDF) nunca empezó.
- **Decisiones:** 052 (SSE con pausa), 053 (`session_store` con TTL), 054 (`etapas`, cierra 037), 055
  (`full_pipeline.py`), 056 (gráficos con d3), 057 (año hidrológico configurable).
- **Quedó abierto:** exportación PDF (checklist); `tests/regression/` vacío (`pendientes-tecnicos.md`).
- **Archivo:** [`plan-etapa2-implementacion.md`](historico/planes/plan-etapa2-implementacion.md).

## 11. Cierre de pendientes no-test

- **Fechas y PRs:** 12/08; **#51** a **#56** (hot reload del backend, DECISIÓN 058, serie en el contrato de Etapa 1,
  serie temporal y Chow, boxplot mensual).
- **Qué se hizo:** cerró FE-16 (la serie no llegaba al frontend). El plan se borró al cerrar y **nunca se versionó**:
  su resumen está en `docs/sprint.md`, sección "Plan de cierre de pendientes no-test".
- **Decisiones:** 058.
- **Archivo:** ninguno.

## 12. Fixes pre-reunión

- **Fechas y PRs:** 13 a 14/08; **#57** a **#60** (spotlight y eje Y cortado, densidad visual de Etapa 2, períodos de
  retorno configurables, nombre de archivo y sparkline en el historial).
- **Qué pedía:** siete arreglos para que la demo de la reunión de avance no tuviera defectos visibles.
- **Qué se hizo:** los siete. El plan **nunca se había commiteado**; entra al repo recién con este archivo.
- **Quedó abierto:** nada vigente.
- **Archivo:** [`plan-fixes-pre-reunion.md`](historico/planes/frontend/plan-fixes-pre-reunion.md).

## 13. Plan post-avance

- **Fechas y PRs:** 14 a 19/08; doce PRs de código, **#61** a **#74**, y el relevamiento final en **#75**.
- **Qué se hizo:** persistencia y recálculo de la elección de Etapa 2 en el historial, selector de intensidad de
  animación, paso a paso con la fórmula sustituida calculada en `core/`, panel de columnas acoplable, contraste WCAG
  AA, partición de Cramer personalizada y orden cronológico bloqueante. El plan en sí (`plan-post-avance.md`) **nunca
  se versionó**; lo que queda es el relevamiento, que verificó bloque por bloque contra `staging`.
- **Decisiones:** 030, 036 (cerrada), 043 (aplicada), 059, 062, 063, 064. En paralelo, la auditoría de restricciones de
  dominio sumó 060 y 061.
- **Quedó abierto:** persistir Etapa 1 si se abandona la pausa de distribución (B4, sin decisión de producto; checklist).
- **Archivo:** [`informe-relevamiento-plan-post-avance.md`](historico/planes/informe-relevamiento-plan-post-avance.md).
  Sus links a `plan-post-avance.md` y los de las decisiones 030, 036, 043, 062, 063 y 064 ya estaban rotos antes de
  archivar (el plan nunca existió en el repo).

## 14. Resolución diaria

- **Fechas y PRs:** 28 a 29/08; **#77** a **#80** apilados, **#81** (selector pico/media) y **#82** (colisión de clave
  en la agregación).
- **Qué pedía:** aceptar series diarias. Un informe de viabilidad previo separó dos caminos: agregar a máximos anuales
  (camino A, barato y estándar) o analizar los valores sin agregar (camino B, que invalida el marco de la tesis).
- **Qué se hizo:** el camino A, directo de diaria a anual, con cobertura asimétrica (extremos al 100 %, interior
  configurable, hoy 100 %). Una revisión independiente verificó las 9 series de regresión byte a byte y encontró la
  colisión de clave que corrigió el #82.
- **Decisiones:** 065 (el sí al camino A), 066 (el no al camino B), 067 (colisión de clave).
- **Quedó abierto:** R0.1 a R0.3 para Facundo (`pendientes-facundo.md`; R0.2 bloquea exponer la carga diaria);
  `variable_diaria` sin decisión escrita (checklist §6); `_espaciado_regular()` inerte para series agregadas
  (`pendientes-tecnicos.md`).
- **Archivo:** [`informe-viabilidad-resoluciones-temporales.md`](historico/planes/informe-viabilidad-resoluciones-temporales.md),
  [`plan-resolucion-diaria.md`](historico/planes/plan-resolucion-diaria.md),
  [`revision-resolucion-diaria.md`](historico/planes/revision-resolucion-diaria.md).

## 15. Feedback de Facundo del 02/09

- **Fechas y PRs:** 02 a 15/09; **#88**.
- **Qué pedía:** cinco observaciones de Facundo en uso real: texto cortado en las tablas de métodos, período de retorno
  elegido sin resaltar, fórmulas en texto plano, card de configuración desalineada y panel de columnas flotante.
- **Qué se hizo:** F1 a F4 y F5(b). Las fórmulas pasaron a KaTeX, revirtiendo en parte DECISIÓN 064. **El panel
  flotante, F5(a), se implementó, se probó en uso real y se descartó**: la zona de colisión era más grande que la card
  y no sumaba lo suficiente. Por eso `decision063.md` no lleva addendum.
- **Decisiones:** addendum a 064 (KaTeX, con su costo de bundle).
- **Quedó abierto:** nada vigente.
- **Archivo:** [`plan-fixes-feedback-facundo-02-09-2026.md`](historico/planes/frontend/plan-fixes-feedback-facundo-02-09-2026.md).

## 16. Fixes post-verificación y Tanda 2 de backend

- **Fechas y PRs:** 01/10; seis PRs desde `staging`, **#96** a **#101**, mergeados el mismo día.
- **Qué pedía:** corregir lo que mostró la verificación en el navegador del PR #95 (texto engañoso de "Otro", panel de
  exclusión, distribuciones sin ajuste), contener el riesgo de Generalizada de Pareto y hacer el backend de la Tanda 2
  del feedback de directores. Octavio no tenía tiempo, así que desde este plan ese backend lo hacen Kevin y Claude,
  con Octavio como reviewer sin bloquear.
- **Qué se hizo:**
  - **#96:** este índice y el archivo de los planes cerrados (Bloque L).
  - **#97:** grilla por década en el panel de exclusión, nota de tipo de variable según la opción elegida y
    distribuciones sin ajuste atenuadas al fondo.
  - **#98:** Generalizada de Pareto "pendiente de validación": se calcula y se muestra, pero no se puede elegir ni
    explorar.
  - **#99:** `disabled_negatives` en Etapa 2 y `TEST_NOT_EXECUTED_NEGATIVES` en Chow.
  - **#100:** `explicacion.desglose` de Anderson y Chow.
  - **#101:** `POST /analysis/simulate-exclusion` (what-if de atípicos), sin el flag `VITE_SIMULATE_EXCLUSION`.

  Ningún estadístico ni veredicto cambió. Las 9 series de regresión dan la misma salida (Pareto solo cambia de
  posición en pantalla). La equivalencia "excluir = rechazar en Chow" la cubre un test de integración, y Kevin la
  verificó en el navegador.
- **Decisiones:** 071 (exclusión por eliminación; el reemplazo por la media quedó postergado), 073 (negativos), 074
  (Pareto pendiente de validación) y el addendum del 01/10 a 064 (desglose). 072 queda reservada para el bloque B.
- **Quedó abierto:**
  - **En el checklist:** el bloque B (exploración sin id para CU-02), `n1_pct`/`n2_pct` de Cramer y el denominador de
    la t de Student en el desglose, y el botón de simulación en `HistoryDetailPage`.
  - **En `pendientes-tecnicos.md`:** el umbral de `DIST_HIGH_EEA` con "Otro" y la corrección de Pareto para la V2.
- **Archivo:** [`plan-fixes-post-verificacion-01-10-2026.md`](historico/planes/plan-fixes-post-verificacion-01-10-2026.md).
