# Objetivos de calidad — METIS V1.0

TP integrador de Calidad de Software, bloque B9. Qué significa "calidad" para METIS, escrito como objetivos medibles:
cada uno con métrica, umbral, valor actual, de dónde sale el número y qué práctica lo sostiene.

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0 | 09/10/2026 | Primera versión. Valores actuales del 09/10/2026 |

Los valores de pipeline salen de `reporte-calidad/metricas.json` (artefacto del job `quality-gate`) y del resumen de
cada corrida; los de carga, de `docs/calidad/herramienta-carga.md`.

## 1. Para el usuario (docentes y estudiantes, CU-01 y CU-02)

| ID | Objetivo | Métrica | Umbral | Valor actual | Fuente | Práctica que lo sostiene |
|---|---|---|---|---|---|---|
| OC-U1 | **Los resultados reproducen la tesis de referencia** | Veredictos de Etapa 1 y parámetros/EEA de Etapa 2 contra las 9 estaciones de la tesis | Etapa 1: igual veredicto; Etapa 2: parámetros ±1 % (`docs/auditoria/regresion/README.md`) | Etapa 1 reproduce los veredictos en las estaciones auditadas, con pendientes de dominio puntuales; Etapa 2: ciclo completo aprobado en est_02, est_06 y est_09, el resto parcial por diferencias de la planilla (Causa C, explicada por el hallazgo de U_T, PR #109) | Auditoría de 4 fases; comparación con R y SciPy (diferencia 0 donde la definición es la misma) | `core/` aislado y testeado contra la fuente; ninguna fórmula sin referencia en `formulas-etapa{1,2}.md` |
| OC-U2 | **Ningún resultado incorrecto en silencio** | Defectos de severidad crítica que llegan a un usuario | 0 | 0. Los 5 críticos registrados se encontraron en auditoría, desarrollo o revisión (`registro-defectos.md`) | Registro de defectos (label `sev:critica`, `fase:uso-real`) | Principio "detecta y advierte, no bloquea": todo límite conocido viaja como warning con código |
| OC-U3 | **Respuesta ágil del análisis** | p95 por endpoint con 15 usuarios concurrentes | `preview-columns` < 150 ms, `stream` (Etapa 1) < 250 ms, `simulate-exclusion` (Etapa 2) < 500 ms | 43, 72 y 147 ms (local); 5, 7 y 45 ms (CI) | Job `carga`, `carga/umbrales.json` | Stress con umbrales en cada PR (DECISIÓN 077) |
| OC-U4 | **Disponible sin errores bajo uso sostenido** | Tasa de error y crecimiento de memoria con 5 usuarios durante 30 min | Error < 1 %; memoria < 50 MB/h | 0 % y +0,3 MB/h | `carga-sostenida.yml` | Esfuerzo sostenido manual y semanal |
| OC-U5 | **Los errores se entienden** | Códigos emitidos por el backend sin traducción en el frontend | 0 | 0 | Job `error-catalog` | Catálogo sincronizado en tres lugares (DECISIÓN 038); estructura de error estándar (#106) |
| OC-U6 | **Los flujos principales funcionan de punta a punta** | Escenarios E2E de CU-01 y CU-02 en verde | 6 de 6 en cada PR | 6 de 6 | Job `despliegue`, `reporte-e2e` | Playwright contra el build de producción (DECISIÓN 046) |

## 2. Para el equipo de desarrollo

| ID | Objetivo | Métrica | Umbral | Valor actual | Fuente | Práctica que lo sostiene |
|---|---|---|---|---|---|---|
| OC-E1 | **Lo que se agrega llega probado** | Cobertura de líneas del código nuevo de cada PR | ≥ 80 %, backend y frontend por separado | Gate activo desde #111; #126 y #127 lo pasaron | `diff-cover` en el job `quality-gate` | El gate bloquea el merge |
| OC-E2 | **El código existente está cubierto** | Cobertura de sentencias y de decisión | ≥ 80 % en las dos | Backend 94,7 % sentencias / 84,1 % decisión; frontend 97,8 % / 87,7 % | `metricas.json` de la corrida de `staging` del 09/10/2026 (`d8d80dc`) | B2 subió la decisión del backend de 76,7 % a más de 80 % |
| OC-E3 | **Poca duplicación** | Líneas duplicadas sobre el total | ≤ 5 % | 0,63 % (139 de 22.156 líneas, 10 clones) | `jscpd` en el job `quality-gate` | El gate bloquea el merge |
| OC-E4 | **Estilo y análisis estático sin hallazgos** | Hallazgos de ruff y ESLint | 0 | 0 | Jobs `lint` y `frontend` | Corre en cada push |
| OC-E5 | **Un defecto corregido no vuelve** | Defectos cerrados sin test de regresión | 0 | 0 de 10 | `registro-defectos.md` | Un defecto se cierra solo con un test que lo cubra |
| OC-E6 | **El pipeline es confiable** | Corridas de CI que fallan sin un problema real (flaky) | Ninguna conocida | 6 fallas en las primeras 222 corridas (2,7 %); B11 clasifica cuáles detectaron un problema real | API de GitHub Actions | Servicios que fallan en lugar de saltearse (`METIS_REQUIRE_DB`, `METIS_REQUIRE_MAILPIT`) |

## 3. Para la organización (UCC, tribunal de ISI, directores)

| ID | Objetivo | Métrica | Umbral | Valor actual | Fuente | Práctica que lo sostiene |
|---|---|---|---|---|---|---|
| OC-O1 | **Cada decisión técnica se puede justificar** | Decisiones con contexto, alternativas y consecuencias escritas | Toda decisión que cambia un comportamiento | 75 archivos en `docs/decisiones/`, de la 001 a la 077 (035 y 072 reservadas sin archivo) | `docs/decisiones/README.md` | Regla de `CLAUDE.md`: decisión nueva antes del código que la aplica |
| OC-O2 | **Cada requisito es rastreable a su prueba** | RF implementados con al menos un test que los verifica | 100 % | Ver `trazabilidad.md` | `trazabilidad.md` | Casos de prueba con el requisito o la regla de la que salen |
| OC-O3 | **Auditoría de lo que decidió el usuario** | Análisis de CU-01 que persisten sus decisiones (atípico, distribución) | 100 % | Cubierto por los tests de persistencia contra PostgreSQL real y E2E-3/E2E-4 | `tests/integration/db/`, `frontend/e2e/` | "Explorar no es decidir" (DECISIÓN 062): explorar no altera lo registrado |
| OC-O4 | **Se puede desplegar desde cero de forma reproducible** | Despliegue desde un clon limpio con la configuración de producción | Sin pasos manuales fuera del script | `deploy-local.sh` en cada push, con smoke | Job `despliegue` | Mismo script en CI y en local (B5) |

## 4. Cómo se revisan

Al cerrar cada bloque del plan del TP se actualiza la columna "Valor actual" con la última corrida del pipeline. Un
objetivo que no se cumple se resuelve con una acción o se renegocia el umbral por escrito, con la razón; no se borra
la fila. El informe final (B12) muestra la evolución de cada valor.
