# Matriz de trazabilidad — requisito → caso → test → defecto

TP integrador de Calidad de Software, bloque B9. Para cada requisito funcional, los casos de prueba que lo
verifican, los tests que los implementan y los defectos registrados contra él.

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0 | 09/10/2026 | Primera versión, sobre el Manual de Requerimientos v5.0 |

**Fuente de los requisitos:** *METIS — Manual de Requerimientos v5.0* (octubre de 2026), que vive fuera del repo
(documentación escrita del proyecto integrador). La columna **Estado** es la del manual al 08/10/2026. El manual no
define requisitos no funcionales: las características de calidad se trazan en `matriz-iso25010.md`.

**Cómo leer las columnas.**
- **Casos:** IDs de `casos-de-prueba.md` (VL, CE, TD) y escenarios E2E de `despliegue-y-e2e.md` (E2E-0 a E2E-5).
- **Tests:** archivos, no funciones. Backend relativo a `backend/tests/`; frontend relativo a `frontend/src/`.
- **Defectos:** IDs de `registro-defectos.md` (issues #114 a #123).

## 1. Requisitos generales del pipeline (RF-GEN-P)

| RF | Requisito | Estado | Casos | Tests | Defectos |
|---|---|---|---|---|---|
| P-01 | Formatos de entrada aceptados | Implementado | CE-03a–e, VL-02a–b | `unit/core/validacion/test_parser.py`, `unit/api/test_analysis_preview_columns.py`, `unit/api/test_upload_limits.py`, `unit/casos_dinamicos/test_clases_equivalencia.py`; `routes/config/ConfigPage.test.tsx` | — |
| P-02 | Validaciones del contrato de datos | Implementado con desvío | VL-01a–d, CE-01a–f, CE-02e–f, E2E-5 | `unit/core/validacion/test_contract.py`, `unit/core/pipeline/test_pipeline_etapa1.py` | D-05 |
| P-03 | Nivel de confianza del resultado | Implementado | TD-03 c1–c4 | `unit/core/pipeline/test_pipeline_etapa1.py`, `unit/casos_dinamicos/test_tablas_decision.py`; `routes/results/Etapa1ResultView.test.tsx` | — |
| P-04 | Estadística descriptiva | Implementado | — (oráculo: tesis) | `unit/core/estadistica_descriptiva/test_descriptive.py` | — |
| P-05 | Ejecución de la Etapa 1 | Implementado | E2E-2, E2E-3 | `unit/core/etapa1/` (4 archivos), `integration/test_stream_*.py`; `routes/stream/StreamPage*.test.tsx` | D-01 |
| P-06 | Jerarquía de pruebas | Implementado (el gap de Mann-Kendall que cita el manual se cerró el 09/10/2026) | TD-01 c1–c4, TD-02 c1–c8, VL-07a–b, VL-08a–d | `unit/core/etapa1/test_independence.py`, `test_homogeneity.py`, `test_trend.py`, `unit/casos_dinamicos/` | D-10 |
| P-07 | Resultado individual por prueba | Implementado | — | `unit/core/etapa1/test_desglose.py`, `unit/services/test_serializar_etapa1.py`; `routes/results/Etapa1Desglose.test.tsx`, `i18n/explicaciones.test.ts` | — |
| P-08 | Ejecución de la Etapa 2 | Implementado con salvedad | VL-04a–b, VL-05a–d | `unit/core/etapa2/` (12 archivos), `unit/core/pipeline/test_pipeline_etapa2.py`, `integration/test_etapa2_stream_distribution_decision.py`; `routes/results/Etapa2RankingView.test.tsx` | D-08, D-09 |
| P-09 | Comportamiento ante casos especiales | Implementado | TD-05 c1–c4, CE-02a–d | `unit/core/pipeline/test_disabled_negatives.py`, `test_pendientes_validacion.py`, `unit/core/etapa2/distributions/test_guards_dominio.py`, `unit/core/etapa1/test_outliers.py` | — |
| P-10 | Agregación temporal a máximos anuales | Implementado | VL-03a–d, CE-01b–c, CE-05a–b | `unit/core/validacion/test_aggregation.py`, `integration/test_stream_agregacion_mensual.py`, `test_stream_agregacion_diaria.py`, `test_stream_anual_celda_vacia.py`, `unit/api/test_stream_variable_diaria_validacion.py` | D-03, D-04, D-05 |

## 2. Requisitos generales de salida (RF-GEN-O)

| RF | Requisito | Estado | Casos | Tests | Defectos |
|---|---|---|---|---|---|
| O-01 | Representación dual según el criterio de año | Implementado con alcance acotado | — | `unit/services/test_serializar_etapa1.py`; `routes/results/Etapa1GraficosView.test.tsx` | — |
| O-02 | Gráfico de Chow | Implementado | — | `routes/results/Etapa1ChowChart.test.tsx` | — |
| O-03 | Serie temporal | Implementado | — | `routes/results/Etapa1SerieTemporalChart.test.tsx`, `charts/InteractiveChart.test.tsx` | — |
| O-04 | FDP con histograma y KDE | **No implementado** | — | — | — |
| O-05 | Boxplot mensual y anual | Implementado parcialmente | — | `routes/results/Etapa1BoxplotMensualChart.test.tsx`, `charts/BoxPlot.test.tsx`, `charts/quartiles.test.ts` | — |
| O-06 | Análisis de normalidad visual | **No implementado** | — | — | — |
| O-07 | Correlograma de autocorrelación | Implementado parcialmente | — | `unit/core/etapa1/test_desglose.py`; `routes/results/Etapa1Desglose.test.tsx` | — |
| O-08 | Tabla de EEA rankeada | Implementado | — | `unit/services/test_serializar_etapa2.py`; `routes/results/Etapa2RankingView.test.tsx` | — |
| O-09 | Tabla de eventos de diseño | Implementado | VL-04a–b, VL-05a–d | `unit/core/etapa2/test_design_events.py`, `unit/api/test_distribution_decision.py`; `routes/results/Etapa2EventosView.test.tsx`, `i18n/periodoRetorno.test.ts` | — |
| O-10 | Gráfico de ajuste | Implementado | — | `routes/results/Etapa2AjusteChart.test.tsx`, `Etapa2EventosChart.test.tsx` | — |
| O-11 | Bandas de confianza | Fuera de alcance de V1.0 | — | — | — |
| O-12 | Exclusión interactiva de puntos y recálculo | Implementado | TD-04 c1–c4 | `unit/core/pipeline/test_exclusiones.py`, `unit/api/test_simulate_exclusion.py`, `integration/test_simulate_exclusion_equivale_a_chow.py`; `routes/results/exclusiones.test.ts`, `useSimulacionExclusion.test.ts`, `ResultsPage.simulacion.test.tsx` | — |
| O-13 | Exploración de distribuciones | Implementado parcialmente | — | `unit/api/test_analysis_design_events.py`, `unit/services/test_recalcular_eventos_diseno.py`; `routes/results/Etapa2Explorador.test.tsx` | — |

## 3. CU-03 — API (RF-CU03)

| RF | Requisito | Estado | Casos | Tests | Defectos |
|---|---|---|---|---|---|
| CU03-01 | Configuración de integración API | **No implementado** | — | — | — |
| CU03-02 | Modelo de integración push | **No implementado** | — | — | — |
| CU03-03 | Contrato de entrada HTTP | **No implementado** | — | — | — |
| CU03-04 | Estructura de respuesta JSON | **No implementado** | — | — | — |

## 4. CU-02 — Anónimo (RF-CU02)

| RF | Requisito | Estado | Casos | Tests | Defectos |
|---|---|---|---|---|---|
| CU02-01 | Acceso sin autenticación | Implementado | E2E-2 | `unit/auth/test_dependencies.py`; `auth/guards.test.tsx` | — |
| CU02-02 | Sesión efímera sin persistencia | Implementado | E2E-2 | `integration/db/test_persistencia.py` (`test_cu02_anonimo_no_persiste_nada`) | — |
| CU02-03 | Outputs en sesión sin exportación | Implementado | E2E-2 | `routes/results/ResultsPage.test.tsx` ("CU-02 (anónimo, sin analysisId) — no muestra 'Exportar PDF'") | — |
| CU02-04 | Elección de alcance del pipeline | Implementado | CE-04a–c, TD-04 | `unit/api/test_stream_etapas_validacion.py`; `routes/config/ConfigPage.test.tsx` | — |
| CU02-05 | Decisiones ante problemas del contrato | **No implementado** | — | — | — |

## 5. CU-01 — Docencia (RF-CU01)

| RF | Requisito | Estado | Casos | Tests | Defectos |
|---|---|---|---|---|---|
| CU01-01 | Autenticación con mail institucional | Implementado | E2E-0, E2E-1 | `unit/auth/` (5 archivos), `integration/db/test_registro_mailpit.py`; `auth/AuthProvider.test.tsx`, `routes/auth-verify/AuthVerifyPage.test.tsx` | D-02, D-07 |
| CU01-02 | Persistencia de análisis por usuario | Implementado | E2E-3, E2E-4 | `integration/db/test_persistencia.py`, `unit/api/test_history_archive.py`; `routes/history/HistoryPage.test.tsx`, `HistoryDetailPage.test.tsx` | — |
| CU01-03 | Modos de uso internos | Implementado | — | `routes/results/Etapa1ResultView.test.tsx`, `routes/config/ConfigPage.test.tsx` | — |
| CU01-04 | Elección de alcance del pipeline | Implementado | CE-04a–c, TD-04 | Los de CU02-04, más `integration/db/test_persistencia.py` | — |
| CU01-05 | Decisiones ante problemas del contrato | **No implementado** | — | — | — |
| CU01-06 | Configuración de partición de Cramer | Implementado | VL-06a–f | `unit/api/test_stream_cramer_particion.py`, `unit/core/etapa1/test_homogeneity.py`; `routes/config/ConfigPage.test.tsx` | D-06 |
| CU01-07 | Registro de decisión ante atípicos de Chow | Implementado con desvío | E2E-2, E2E-3 | `unit/services/test_analysis_service.py`, `integration/test_stream_agregacion_mensual.py`, `test_stream_anual_celda_vacia.py`; `routes/stream/StreamPage.test.tsx` | D-03, D-04 |
| CU01-08 | Exportación de reporte | Implementado con desvío | E2E-3 | `unit/reportes/test_pdf.py`, `unit/api/test_export.py`, `unit/services/test_export_service.py`; `routes/results/ExportarPdfButton.test.tsx`, `api/export.test.ts` | — |

## 6. Resumen

| | RF | Con al menos un test | Sin test |
|---|---|---|---|
| Implementados (total, parcial, con desvío o salvedad) | 31 | 31 | 0 |
| No implementados | 8 | — | 8 (nada que probar) |
| Fuera de alcance de V1.0 | 1 | — | 1 |
| **Total** | **40** | **31** | **9** |

- **Todo requisito implementado tiene al menos un test.** Los que solo tienen tests de componente del frontend
  (O-02, O-03, O-05, O-10) son gráficos: se verifican además a mano en la evidencia de navegador de cada PR que los
  toca (Capa 4).
- **Los 10 defectos registrados** se reparten en 8 requisitos: la mayor concentración está en P-10 (agregación
  temporal, 3 defectos) y P-08 (Etapa 2, 2), coherente con el principio de agrupación de defectos
  (`principios.md`).
- **Los 8 no implementados** son la brecha de completitud de la adecuación funcional (`matriz-iso25010.md`).
- **Sentido inverso:** todo caso de `casos-de-prueba.md` y todo E2E aparece en al menos una fila de esta matriz.
