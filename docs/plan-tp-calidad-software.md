# Plan de implementación: TP Integrador de Calidad de Software sobre METIS

**Versión 2, 08/10/2026.** Entrega: **26/10/2026** (18 días corridos).
**Fuente:** consigna "TP Integrador, Calidad de Software aplicada al TFG".
**Base del análisis:** `origin/staging` en `b9e471e` (PR #109). La copia local estaba en `fe0025c`, dos PR atrás: hacer `git pull` antes de arrancar.

| Versión | Fecha | Cambios |
|---|---|---|
| 1 | 08/10/2026 | Análisis inicial y plan |
| 2 | 08/10/2026 | Decisiones de Kevin: la materia la cursa solo él (sin reparto), Nivel 3 fijo, despliegue local con Docker para la demo y efímero en GitHub Actions para el pipeline (el servidor UCC queda para la defensa de la tesis), integración externa probada con Mailpit (Gmail real queda para el despliegue en la UCC), herramienta nueva: k6. Se agrega el origen de la exclusión de E2E y carga y qué es DECISIÓN 046 |
| 3 | 08/10/2026 | Origen exacto de la exclusión (PR #2) y explicación de Kevin; DECISIÓN 049 (escotilla SMTP de desarrollo, reservada) pasa a cubrir Mailpit; B6 (E2E) reescrito como instrucciones ejecutables para Claude Code, con selectores, fixtures y trampas ya relevadas en el código |
| 4 | 08/10/2026 | Kevin no tiene admin del repo: B1 se parte en B1a (cobertura, gate propio con diff-cover y jscpd, reportes; sin permisos) y B13 (SonarCloud por CI, Análisis Automático desactivado, checks requeridos), que pasa a ser el último PR. B0 escrito: DECISIÓN 046, 049 y 077 |

Este documento tiene dos partes: qué de la consigna ya existe en el repo (con evidencia medida, no estimada) y qué falta, ordenado en bloques de trabajo con criterio de hecho.

---

## 1. Línea de base medida hoy

Todo lo de esta tabla salió de ejecuciones reales del 08/10/2026, no de documentos.

| Medida | Valor | Cómo se obtuvo |
|---|---|---|
| Tests backend (unit + integration) | 500 pasan, 0 fallan (132 s) | `pytest -m "unit or integration"` en Python 3.11 |
| Cobertura backend, sentencias | **91,4 %** (3016 / 3301) | `pytest-cov --cov-branch` |
| Cobertura backend, decisiones (ramas) | **76,7 %** (704 / 918) | ídem |
| Tests frontend | 497 pasan en 59 archivos (84 s) | `vitest run --coverage` |
| Cobertura frontend, sentencias | **97,5 %** (6158 / 6314) | `@vitest/coverage-v8` 2.1.9 |
| Cobertura frontend, ramas | **87,8 %** (1493 / 1701) | ídem |
| Tamaño | ~9.400 líneas Python (`metis/`), ~10.100 líneas TS/TSX (sin tests) | `wc -l` |
| Ejecuciones de CI | 222 en total, 6 fallidas (2,7 %) | API de GitHub Actions |
| Issues en GitHub | 0 | API de GitHub |
| `tests/e2e/`, `tests/regression/` | vacíos (solo `__init__.py`) | repo |

Módulos backend más flojos en cobertura (candidatos para la "mejora medida antes y después"):

| Módulo | Cobertura |
|---|---|
| `auth/dependencies.py` | 27 % |
| `auth/jwt.py` | 50 % |
| `auth/router.py` | 60 % |
| `core/etapa2/distributions/logpearson3.py` | 76 % (ramas de guard sin ejercitar) |
| `core/etapa2/distributions/gamma2p.py` | 78 % |
| `api/v1/history.py` | 82 % |

Lectura rápida: la cobertura sobre el código existente ya supera el 80 % del Nivel 3 en sentencias, pero **la cobertura de decisión del backend (76,7 %) está debajo**, y hoy **ninguna de estas cifras la produce el pipeline**: no hay cobertura en `ci.yml` y SonarCloud corre en Análisis Automático, que no admite importar cobertura (DECISIÓN 044).

---

## 2. Qué ya tenemos y qué falta, eje por eje

### 2.1 Introducción a la calidad

| Pide | Tenemos | Falta |
|---|---|---|
| Objetivos de calidad medibles (usuario, equipo, organización) | Implícitos: reproducir los resultados de la tesis de Facundo (auditoría fases 1 a 4), "detecta y advierte, no bloquea", contratos de error | Escribirlos como objetivos con métrica, umbral y fuente (ej.: "las 9 estaciones reproducen el veredicto de la tesis", "p95 de `/analysis/stream` etapas=1 < X s", "0 bugs de Reliability en Sonar") |
| Prácticas de proceso que los sostienen | Sí, documentadas: GitHub Flow con ruleset, PR obligatorio, CI de 4 jobs, 76 decisiones registradas, catálogo de errores verificado en CI, DoD de frontend con evidencia en navegador | Agruparlas y vincularlas a cada objetivo |
| Plan de contingencia ante caída de dependencia crítica | Nada formal. Caso real: BD sin migrar devolvía 500 en `/history/` (05/08/2026) | Plan para: SMTP caído (registro responde 500 `AUTH_VERIFICATION_EMAIL_FAILED`), PostgreSQL caído, migraciones sin aplicar, GitHub Actions o SonarCloud caídos |

### 2.2 Fundamentos del testing

| Pide | Tenemos | Falta |
|---|---|---|
| Unitarias en Arrange-Act-Assert | ~1000 tests; estructura AAA en la práctica, pero ningún test lo marca | Marcar AAA explícito en los tests nuevos y en una muestra representativa |
| Criterio de aceptación fijado antes de ejecutar | Sí: "coincidir con el Excel de Facundo" (`testing.md`) y los valores esperados de la tesis | Dejarlo escrito por caso en el plan de pruebas, con fecha anterior a la ejecución |
| Un defecto real con contraste rojo/verde | Varios candidatos con test de regresión (§2.7) | Elegir uno, correr su test en el commit previo al fix (rojo) y en el del fix (verde), con capturas |
| Los siete principios aplicados | Hay ejemplos de sobra (ver nota) | Redactar la sección |

Ejemplos reales para los siete principios: "la ausencia de errores es una falacia" = F1 (98 tests en verde y la app rota bajo StrictMode); "el testing exhaustivo es imposible" = 13 distribuciones × 6 métodos × resoluciones; "agrupación de defectos" = Etapa 2 (GVE, LN3p, Gen. Pareto concentraron los hallazgos); "paradoja del pesticida" = por qué se agregó la Capa 2 de integración en frontend; "testing temprano" = auditoría de fórmulas antes de la UI.

### 2.3 Modelos de calidad y niveles de prueba

| Pide | Tenemos | Falta |
|---|---|---|
| Matriz ISO/IEC 25010 (8 características) con evidencia | Evidencia dispersa | Matriz completa (B9) |
| Top 3 justificado | No | Propuesta: Adecuación funcional (exactitud contra la tesis), Fiabilidad (pausas SSE, timeouts, tolerancia a falla de SMTP/BD), Mantenibilidad (`core/` aislado, testabilidad) |
| Mapa de niveles de prueba | `testing.md` describe 4 niveles backend + 4 capas frontend | Mapa único: unidad, integración, sistema (E2E), aceptación, con herramienta y cantidad de tests por nivel |
| Despliegue verificado en cada instancia | Docker Compose funciona local; sin despliegue en el pipeline | Despliegue efímero verificado por el pipeline (B5) |

### 2.4 Métricas y análisis estático

| Pide | Tenemos | Falta |
|---|---|---|
| Análisis estático | ruff (check + format), ESLint, `tsc`, SonarCloud consultivo, `check-error-catalog.sh` | Que Sonar reciba cobertura y que su gate bloquee |
| Tabla de métricas interpretadas | No | LOC, complejidad ciclomática y cognitiva, duplicación, cobertura sentencia/decisión, smells, deuda, con interpretación |
| Una métrica de proceso | Datos disponibles | Ej.: tasa de fallo de CI (6/222 = 2,7 %), lead time de PR, defectos por fase de detección |
| Una métrica de proyecto | Datos en `sprint.md` y `planes-implementados.md` | Ej.: avance de bloques de este plan contra el cronograma, esfuerzo por bloque |
| Mejora medida antes y después | Antecedente: limpieza de SonarCloud (61 issues, 6 bloqueantes) | Una mejora nueva medida por el pipeline: cobertura de `auth/` o cobertura de decisión backend (76,7 % → ≥ 80 %) |

### 2.5 Pruebas dinámicas

| Pide | Tenemos | Falta |
|---|---|---|
| Clases de equivalencia | Tests que ya las cubren, sin documentarlas | Documentarlas (lista abajo) |
| Valores límite | Ídem | Ídem |
| Tablas de decisión | Las reglas existen en código y en `statistical-pipeline.md` | Tablas explícitas + tests parametrizados por columna |
| Cobertura de sentencia y de decisión | Medible (§1), no reportada | Reportarla desde el pipeline |

Candidatos concretos del dominio:

- **Valores límite:** n de la serie (9 bloquea, 10 y 29 warning, 30 sin warning); archivo de 10 MB exactos vs 10 MB + 1 byte; `mes_inicio_anio` (0, 1, 12, 13); `periodos_retorno` (T = 1 inválido, T = 1,0001 válido; 0, 1, 20 y 21 elementos); `cramer_particion` (`n1_pct` 1 y 100, `n1_pct == n2_pct`); Wald-Wolfowitz n = 40 y 41; Mann-Kendall n = 9, 10, 30, 31.
- **Clases de equivalencia:** resolución temporal (anual, mensual, diaria, otra → bloqueante); `tipo_variable` × ceros y negativos; formato de archivo (CSV, Excel, ilegible, vacío); `etapas` (`"1"`, `"1,2"`, inválido).
- **Tablas de decisión:** jerarquía Anderson/Wald-Wolfowitz; niveles de homogeneidad (Cramer × Helmert × t); `nivel_confianza` global; entrada a Etapa 2 (`etapas` × `rechazado`); estado de cada distribución ante ceros/negativos (DECISIÓN 061 y 073).

### 2.6 Aseguramiento de la calidad

| Pide | Tenemos | Falta |
|---|---|---|
| Plan de pruebas | Estrategia en `.claude/rules/testing.md` | Plan formal versionado (estilo IEEE 829): alcance, ítems, enfoque, criterios de entrada, salida y suspensión, entregables, ambiente, cronograma |
| Riesgos probabilidad × impacto | No | Matriz priorizada (B9) |
| Prácticas QA distinguidas de QC | Ambas, sin separar | QA (proceso): decisiones registradas, ruleset, revisión de PR, CLAUDE.md, DoD, catálogo de errores. QC (producto): tests, auditorías fase 1 a 4, comparación con herramientas externas (PR #109) |
| Plantillas de caso y de defecto con trazabilidad | No | Plantillas + matriz requisito → caso → defecto. Los requisitos salen del anteproyecto (`RF-GEN-...`); en el repo solo aparecen RF-GEN-P-01 a P-06 y O-11, hay que traer la lista completa |

### 2.7 Automatización del testing

| Pide | Tenemos | Falta |
|---|---|---|
| Pirámide automatizada | ~1000 unitarios, 5 de integración backend sin BD real, 0 E2E | Integración con PostgreSQL real, E2E, smoke; pirámide con números del pipeline |
| Pruebas de API | 12 archivos en `tests/unit/api/` con `TestClient` | Pruebas contra el sistema desplegado (smoke/E2E) |
| Integración con la plataforma externa | SMTP probado solo con dobles (`AsyncMock` sobre `aiosmtplib.send`) | Mailpit (B4) |
| Smoke en cada despliegue | No existe (en el repo "smoke" significa verificación manual de desarrollo) | B5 |
| Pipeline CI/CD | CI sí (4 jobs); CD no | Job de despliegue efímero + verificación |
| Regresión por cada defecto corregido | Práctica existente, sin registro que lo demuestre | Registro defecto → test (B10) |

Defectos reales con test de regresión, candidatos para el registro y para el rojo/verde (verificar qué test cubre cada uno):

1. Stream que se abortaba solo bajo StrictMode (F1, `informe-diagnostico-ui-rota.md`).
2. Login 200 sin sesión confirmada, botón "muerto" (F3).
3. Índice de Chow mapeado contra la serie mensual cruda en lugar de la agregada (`test_stream_agregacion_mensual.py`).
4. Timestamps desalineados con celdas vacías en carga anual (`test_stream_anual_celda_vacia.py`).
5. Archivo desordenado que perdía un año en silencio al agregar (DECISIÓN 030).
6. `cramer_particion` personalizada devolvía 500 (DECISIÓN 036).
7. Errores envueltos en `detail`: el login con contraseña incorrecta mostraba texto genérico (`test_estructura_error.py`).
8. GVE Momentos-L con la serie en orden ascendente; LN3p con exponente 1/4.
9. Abierto: el warning de muestra chica de Mann-Kendall no se promueve a la lista agregada (DECISIÓN 038). Sirve como defecto en estado "abierto".

### 2.8 Herramientas del ecosistema

| Pide | Tenemos | Falta |
|---|---|---|
| Mapa de herramientas | pytest, Vitest, Testing Library, ruff, ESLint, SonarCloud, GitHub Actions, Docker | Mapa por actividad del ciclo |
| Herramienta nueva con proceso de 5 pasos | No | k6 (B7) |
| Registro en Jira u otra | Defectos en markdown, 0 issues | B10 |
| Stress y esfuerzo sostenido | Nada, y excluido del scope V1.0 (§4) | B0 y B7 |

### 2.9 Documentación (transversal)

Es el punto más fuerte del proyecto: 76 decisiones, auditorías, planes con informe de resultados, contratos. Falta consolidar lo de la materia en `docs/calidad/` y el informe PDF.

---

## 3. Contra la tabla de metas (Nivel 3, decidido)

| Aspecto | Exigido (Nivel 3) | Estado hoy | Brecha |
|---|---|---|---|
| Pipeline | Compilación, pruebas, estático, cobertura, quality gate, reporte automático | Compilación, pruebas, estático | Cobertura, gate bloqueante, reportes |
| Quality gate | Bloquea bugs críticos, duplicación > 5 %, cobertura código nuevo < 80 % | Sonar consultivo, sin cobertura | Sonar por CI con cobertura + check requerido |
| Cobertura código nuevo | 80 % | No se mide | Cobertura diferencial en el PR |
| Plan de pruebas y riesgos | Versionado, entrada/salida, P × I, trazabilidad | Estrategia sin formato de plan | Todo el documento |
| Defectos | Pasos, esperado, obtenido, vinculados al caso en una herramienta | En markdown, sin herramienta | Registro en herramienta |
| Herramienta nueva | Proceso de 5 pasos | No | Todo |
| Cobertura código existente | 80 % | 91,4 % sentencias / 76,7 % decisión (backend); 97,5 / 87,8 (frontend) | Decisión backend ≥ 80 %, medido por el pipeline |
| Smoke | Ejecutado por el pipeline tras el despliegue | No existe | Todo |
| Integración externa | Flujo E2E automatizado en cada despliegue | Solo dobles | Mailpit + E2E en el despliegue efímero |
| Stress y sostenido | Ejecutado, con resultados y umbrales | Nada | Todo |

---

## 4. La exclusión de E2E y carga, y DECISIÓN 046

**De dónde sale.** `constraints.md`, sección "Scope V1.0, lo que NO entra", lista "Tests de carga o performance" y "Tests end-to-end de UI automatizados (Selenium/Playwright)" desde el segundo día del repo: commit `6d2df20` (05/05/2026, Octavio), que crea `.claude/rules/constraints.md` completo dentro del PR #2 (`feature/db-models` → `staging`, autor y merge de Octavio). El mensaje del commit solo habla del GitHub Flow; la lista de alcance entró en el mismo archivo sin mención. El archivo se movió a `.claude/rules/architecture/` en `5e9edaf` (PR #15, 20/07/2026, también de Octavio) sin tocar esas líneas. **El repo no registra ninguna justificación**: no hay una decisión que los excluya, solo la línea en la lista. Por cómo está armada la lista (al lado de bandas de confianza, raster y CD a la UCC), es un recorte de alcance de la V1.0 heredado de la planificación inicial, no una decisión técnica. Las razones razonables en ese momento eran tiempo, un uso previsto chico (docentes dentro de la intranet) y que todavía no había un sistema desplegable completo.

**Explicación de Kevin (08/10/2026).** Octavio hizo la mayor parte de su trabajo en el backend, en una etapa en la que el proyecto todavía no tenía frontend; en ese contexto, "no hay E2E de UI" era una descripción del momento, y quedó escrita en `constraints.md` como si fuera una restricción del proyecto. A lo largo del desarrollo se leyó como regla. El frontend lo desarrolló en su mayoría Kevin, por lo que las pruebas E2E le corresponden a él. Esto va como contexto de la DECISIÓN 046: se revisa un recorte de alcance de la fase solo backend que nunca se justificó, no se revierte una decisión fundamentada.

**Qué pasó después.**
- 31/07/2026, plan de arreglo de UI rota (`plan-arreglo-ui-rota.md` §4.3): cinco de los doce defectos de esa pasada (F1, F4, F5, F6, F9) solo eran detectables con el sistema completo corriendo, es decir con E2E. Se propuso agregar Playwright, pero como contradice `constraints.md`, se reservó el número **DECISIÓN 046** para escribir primero la revisión de esa exclusión.
- `plan-post-pasada4-roadmap.md` (Bloque C1): ofreció dos vías, C1a (verificación manual con capturas) o C1b (escribir 046 y habilitar Playwright). Se eligió C1a, con la recomendación de implementar C1b recién cuando Etapa 2 estuviera cableada, porque un E2E sobre un flujo a medio mockear rinde poco.
- Desde entonces 046 figura en `docs/decisiones/README.md` como "reservado, E2E con Playwright, revisa la exclusión de `constraints.md`", sin archivo.

**Qué es DECISIÓN 046, entonces:** un número apartado para la decisión que habilita los E2E automatizados y saca esa línea de "lo que NO entra". Nunca se escribió. Hoy se dan las dos condiciones que faltaban: Etapa 2 está cableada de punta a punta y la materia exige el flujo E2E en cada despliegue.

**Qué hay que escribir:**
- **DECISIÓN 046:** E2E con Playwright contra el despliegue efímero del pipeline. Contexto (los cinco defectos F que solo esta capa detecta), alcance chico y deliberado (dos flujos, no la UI entera), costo y fragilidad aceptados.
- **DECISIÓN 049** (ya reservada en `docs/decisiones/README.md` como "escotilla SMTP de desarrollo en `auth/email.py`"): Mailpit como servidor SMTP de captura en los compose de desarrollo, E2E y CI. Es exactamente lo que recomendaba `plan-arreglo-ui-rota.md` §1.3(b) ("MailHog en `docker-compose`, no una rama `if dev` en el camino crítico de auth"); Mailpit es el sucesor mantenido de MailHog. El único cambio de código es `SMTP_STARTTLS` configurable, con default `true` (ver B4). Las alternativas descartadas a registrar: escotilla por `ENV` que loguea el token (toca el camino crítico, DECISIÓN 032) y quedarse solo con `seed-dev-user.sh` (no ejercita el envío real).
- **DECISIÓN 077:** pruebas de carga y esfuerzo sostenido con k6, cobertura y quality gate en CI, y migración de SonarCloud de Análisis Automático a análisis por CI (resuelve la "pregunta de gobernanza abierta" de DECISIÓN 044).
- Actualizar `constraints.md` (sacar las dos líneas de "lo que NO entra", con referencia a 046 y 077) y `testing.md`.

Sin esto, el tribunal de ISI ve en el repo una restricción vigente que el mismo repo viola.

---

## 5. Decisiones tomadas

| # | Decisión | Resolución |
|---|---|---|
| D1 | Nivel | **Nivel 3** (la tesis va en primera fecha) |
| D2 | Despliegue | **Efímero en GitHub Actions** (Docker Compose dentro del runner) para cada corrida de pruebas; **local con Docker** para la demo. El servidor de la UCC queda fuera de este TP: es para la defensa de la tesis |
| D3 | Integración externa | **SMTP probado con Mailpit** en el despliegue efímero y en el local. La prueba contra Gmail real se hace cuando METIS esté en los servidores de la UCC (intranet, con su propio debugging); en este TP se declara como trabajo posterior, con la razón |
| D4 | Herramienta nueva | **k6** (ver B7 para el porqué y el proceso de 5 pasos) |
| D5 | Registro de defectos | **GitHub Issues + Projects** con plantilla de defecto. Si la cátedra exige Jira, Jira Free con la integración de GitHub |
| D6 | Autoría | La materia la cursa solo Kevin: todo el trabajo y los commits de este TP son de él. Lo previo del repo hecho por Octavio se cita como antecedente, no como aporte de este TP |
| D7 | Scope del repo | DECISIÓN 046, 049 y 077 antes del código (§4) |
| D8 | E2E | Los hace Kevin (autor de la mayor parte del frontend), con Playwright en `frontend/e2e/` |

**Sobre D3, un riesgo de evaluación a tener presente:** la tabla de metas pide en el Nivel 2 "una integración probada contra entorno real" y en el Nivel 3 "flujo E2E automatizado en cada despliegue". Mailpit es un servidor SMTP real (habla el protocolo, recibe y guarda el mail), no un doble en memoria, y el E2E lo usa en cada despliegue: eso cubre el Nivel 3. Igual conviene que el informe lo explique en una línea y diga por qué Gmail real va con el despliegue en la UCC.

---

## 6. Bloques de trabajo

Cada bloque es un PR (o dos) contra `staging`, con su criterio de hecho. Horas estimadas, gruesas.

### B0. Gobernanza y scope (2 h)
- DECISIÓN 046, 049 y 077 (§4). 046 y 049 son números ya reservados: se escribe el archivo y se reemplaza la fila "reservado" del índice. Para 077: `git fetch` y revisar el máximo en `origin/staging` (hoy 076).
- Actualizar `constraints.md` y `testing.md`.
- **Hecho:** decisiones mergeadas antes de cualquier código de B5 a B7.

### B1. Pipeline con cobertura, reportes y quality gate (6 a 8 h)

**Versión 4:** este bloque se parte en dos. **B1a** (va en la semana 1) es todo lo que no necesita admin del
repo: cobertura backend y frontend, quitar la tolerancia al exit code 5, `diff-cover` y `jscpd` como gate propio,
resumen en `$GITHUB_STEP_SUMMARY` y `scripts/test.sh`. **B13** (último PR) es lo que sí lo necesita: SonarCloud
por CI con `SONAR_TOKEN`, desactivar el Análisis Automático (son excluyentes: con el automático activo, el job de
CI falla en todos los PR) y checks requeridos en el ruleset. Ver DECISIÓN 077, "Orden de implementación y
permisos". El token se le pide a Octavio en la semana 1 aunque se use al final.
- Backend: `pytest-cov` en `requirements.txt`; job `test` con `--cov=metis --cov-branch --cov-report=xml --cov-report=html --junitxml=...`; artefactos.
- Quitar la tolerancia al exit code 5, en su propio commit (CLAUDE.md ya dice que sobra).
- Frontend: `@vitest/coverage-v8` (misma versión que vitest, 2.1.9), `npm run test:coverage` con `lcov`, artefacto. Revisar `include`/`exclude` para no contar archivos de configuración.
- SonarCloud por CI: secret `SONAR_TOKEN`, acción oficial de SonarCloud con `sonar.python.coverage.reportPaths` y `sonar.javascript.lcov.reportPaths`, desactivar el Análisis Automático (son excluyentes).
- Quality gate: "Sonar way" exige cobertura de código nuevo ≥ 80 %, duplicación en código nuevo ≤ 3 % (más estricto que el 5 % de la consigna) y Reliability A (bloquea cualquier bug, no solo críticos). Verificar si la organización permite un gate propio con los umbrales exactos; si no, justificar que Sonar way es más estricto.
- Red propia, independiente de Sonar: `diff-cover --fail-under=80` sobre el XML de cobertura del PR, `jscpd --threshold 5`.
- Ruleset: checks de CI y de SonarCloud como requeridos. Necesita admin del repo, que es de Octavio: pedirle el acceso la primera semana.
- Resumen en `$GITHUB_STEP_SUMMARY` con tests, cobertura y duplicación, para que los números del informe salgan de ahí.
- Un comando: `scripts/test.sh {unit|integration|smoke|e2e|stress|soak|all}`.
- **Hecho:** un PR con el gate en verde y otro bloqueado por el gate.

### B2. Cobertura: subir lo débil y medir la mejora (5 h)
- Tests de `auth/dependencies.py`, `auth/jwt.py`, `auth/router.py` (login, logout, me, verify, token vencido, cookie ausente o adulterada).
- Ramas de guard de Etapa 2 hasta cobertura de decisión backend ≥ 80 %.
- Tests nuevos en AAA explícito.
- **Hecho:** tabla antes/después generada por el pipeline (la "mejora medida").

### B3. Integración con PostgreSQL real (4 h)
- `services: postgres:15` en el job, `alembic upgrade head`, marker `integration`.
- Cubre compromisos de `testing.md` nunca hechos: persistencia en CU-01, ausencia de persistencia en CU-02, archivado, pertenencia (404 a un análisis ajeno).
- **Hecho:** tests corriendo en CI contra Postgres, no contra mocks.

### B4. Integración externa: SMTP con Mailpit (4 h)
- Documento de la integración: contrato (qué se manda a `aiosmtplib.send`, variables de entorno, errores, `AUTH_VERIFICATION_EMAIL_FAILED`), dobles usados y por qué, y qué queda para Gmail en la UCC.
- Nivel de dobles (ya está): `test_email.py`, `test_router_register.py`.
- **Detalle técnico a resolver primero:** `auth/email.py` llama a `aiosmtplib.send(..., start_tls=True)` fijo, y aiosmtplib valida el certificado por defecto. Mailpit sin TLS rechaza STARTTLS, y con certificado autofirmado falla la validación. Hay que hacer configurable `start_tls` (o la validación del certificado) por variable de entorno, con el default actual intacto para producción. Cambio chico en `backend/`, con su test.
- `FRONTEND_URL` arma el link del mail (`auth/email.py` y `auth/router.py`, default `http://localhost:5173`). En el compose de E2E tiene que apuntar a nginx (`http://localhost`), si no el link del mail lleva al servidor de desarrollo de Vite, que no está levantado.
- Mailpit como servicio en el compose de CI y en el local (DECISIÓN 049). Test de integración: registrar, leer el mail con la API HTTP de Mailpit, extraer el token, verificar, loguear.
- Plan de contingencia de SMTP caído (timeout, mensaje al usuario, `seed-dev-user.sh` como bypass operativo).
- **Hecho:** flujo registro → mail → verificación probado contra Mailpit en cada corrida.

### B5. Despliegue efímero, despliegue local y smoke (6 h)
- `docker-compose.ci.yml` (override de producción): sin `--reload` ni bind mount, como ya anticipa `architecture.md`; Mailpit incluido; `alembic upgrade head` como paso explícito (el incidente del 05/08 es el ejemplo de por qué).
- Job `deploy` en CI: build de imágenes, `compose up`, espera de healthcheck.
- Smoke (`tests/smoke/`, marker `smoke`, httpx contra nginx): `GET /` (SPA), `GET /ping`, `POST /analysis/preview-columns` con una serie de prueba, `POST /analysis/stream` con `etapas=1` hasta `complete`, login con usuario sembrado y `GET /history/`.
- Corre después de cada despliegue; si falla, falla el pipeline.
- Despliegue local para la demo: el mismo compose con un script (`scripts/deploy-local.sh`) que levanta todo desde cero, migra, siembra un usuario y corre el smoke.
- **Hecho:** pipeline con `deploy → smoke` en verde y el mismo procedimiento reproducible en la máquina local.

### B6. E2E automatizado con Playwright (8 a 10 h)

Instrucciones pensadas para ejecutarse con Claude Code sobre el repo. Todo lo de esta sección se relevó leyendo el código de `staging` (`b9e471e`); si algo cambió, el código manda.

**Requisitos previos (no arrancar sin esto):**
1. DECISIÓN 046 y 049 escritas y mergeadas (B0). `testing.md`, "Capa 3", dice explícitamente que no se implementa sin 046.
2. `SMTP_STARTTLS` configurable en `auth/email.py` (B4).
3. Compose de E2E (B5) con: imágenes de producción (sin `--reload` ni bind mount), Mailpit, `alembic upgrade head` como paso, `FRONTEND_URL=http://localhost`, `SMTP_HOST=mailpit`, `SMTP_PORT=1025`, `SMTP_STARTTLS=false`, credenciales SMTP de relleno (el código exige que `SMTP_USER`/`SMTP_PASSWORD`/`SMTP_FROM_ADDRESS` existan aunque Mailpit no autentique; verificar que Mailpit acepte AUTH o configurarlo con `MP_SMTP_AUTH_ACCEPT_ANY=1` y `MP_SMTP_AUTH_ALLOW_INSECURE=1`).

**Antecedente que se retoma:** `docs/historico/planes/frontend/plan-arreglo-ui-rota.md` §4.3 ya había diseñado cinco escenarios (E2E-1 a E2E-5), el directorio `frontend/e2e/` y los fixtures en `frontend/e2e/fixtures/`. Se usa esa misma estructura y numeración, y se agregan el registro con Mailpit y la exportación PDF.

**Estructura:**
- `@playwright/test` como devDependency de `frontend/` (versión exacta, no rango). Solo Chromium.
- `frontend/playwright.config.ts`: `testDir: "./e2e"`, `baseURL` desde `E2E_BASE_URL` (default `http://localhost`, nginx), `MAILPIT_URL` (default `http://localhost:8025`), `trace: "retain-on-failure"`, `video: "retain-on-failure"`, `screenshot: "only-on-failure"`, reporter `html` + `list`, `workers: 1` (los flujos comparten base de datos), `expect.timeout` amplio (Etapa 2 ajusta 13 distribuciones).
- Script `npm run test:e2e`.
- **Excluir `e2e/` de Vitest**: el `include` por defecto de Vitest toma `*.spec.ts`. En `vite.config.ts`, `test.exclude: [...configDefaults.exclude, "e2e/**"]`. Sin esto, `npm test` (y el job `frontend` de CI) intentan correr los specs de Playwright con jsdom y fallan.
- `tsconfig` propio para `e2e/` (o sumarlo a `tsconfig.node.json`), para que `tsc -b` del build no lo mezcle con `src/`. Que ESLint lo cubra.
- `frontend/e2e/helpers/mailpit.ts`: esperar el mail por destinatario (`GET {MAILPIT_URL}/api/v1/search?query=to:"<email>"`, con reintentos), leer el cuerpo (`GET /api/v1/message/{ID}`, campo `Text`), extraer el link con una regex sobre `/auth/verify?token=`. Confirmar los endpoints contra la documentación de la versión de Mailpit que se fije en el compose.
- Fixtures: copiar `docs/series prueba/serie_con_atipico.csv` (40 años, `anio,caudal`, un 950 forzado: Chow detecta el atípico y el stream pausa) a `frontend/e2e/fixtures/`, y crear `serie_8_datos.csv` para E2E-5. Copiados, no referenciados: si cambia la serie de docs, el E2E no se rompe en silencio.

**Escenarios (selectores reales relevados):**

| ID | Flujo | Pasos y selectores | Verifica |
|---|---|---|---|
| E2E-0 | Registro + Mailpit + verificación (CU-01) | `/` → botón "Registrate" → `#register-email` (email único, `e2e-<timestamp>@ucc.edu.ar`), `#register-password`, `#register-nombre` → "Crear cuenta" → banner `role="alert"` de éxito. Mail en Mailpit → `page.goto(link)` → `<output>` con "Cuenta verificada. Ya podés iniciar sesión." → "Ir a la puerta de entrada" | Integración SMTP de punta a punta (Nivel 3 de la tabla de metas) |
| E2E-1 | Login | `#login-email`, `#login-password`, "Ingresar" → URL `/config`, `getByTestId("user-email")` con el email | F2, F3 |
| E2E-3 + PDF | Análisis completo CU-01 | En `/config`: `setInputFiles` sobre `getByLabel("Archivo (CSV o Excel)")`; esperar que aparezcan los `<select>` `#config-columna-x` y `#config-columna-y` (la preselección elige `anio` y `caudal`; igual afirmarlo). Botón "Validación + análisis de frecuencia (Etapa 1 y 2)", modo "Experto" o "Paso a paso", "Ejecutar análisis ▸". En `/stream`: `getByRole("dialog", { name: "Dato atípico detectado" })` → "Rechazar". Esperar el heading "Elegí una distribución" → primer botón "Elegir este ajuste" habilitado. Navega sola a `/results`: heading "Resultados de Etapa 1". "Exportar PDF" con `page.waitForEvent("download")`: nombre `metis_*.pdf` y que el archivo empiece con `%PDF` | F1, decisión de Chow, pausa de Etapa 2, PDF (DECISIÓN 075) |
| E2E-4 | Historial | Link "Historial" de la barra → fila con `serie_con_atipico.csv` → detalle | F4, persistencia de CU-01 |
| E2E-2 | Anónimo (CU-02) | `/` → "Entrar como anónimo (solo resultados)" → mismo archivo, "Solo validación (Etapa 1)" → modal → "Rechazar" → `/results` | F1; que **no** aparezcan "Exportar PDF" ni el link "Historial" |
| E2E-5 | Serie corta | Anónimo con `serie_8_datos.csv` → banner `role="alert"` con "La serie tiene menos de 10 datos. No se puede analizar." | El único bloqueante por longitud, sin cuelgue |

**Trampas ya identificadas en el código:**
- **Correr contra el build de producción (nginx), nunca contra `npm run dev`.** En desarrollo, StrictMode monta dos veces: `AuthVerifyPage` llama a `verify` dos veces (la segunda falla con el token ya usado) y `StreamPage` abre dos streams. Además, con `import.meta.env.DEV` el registro muestra un aviso de "modo dev" si falla el SMTP en vez del error real.
- **No navegar directo a `/stream` ni a `/results`:** el formulario y los resultados viajan como estado del router (`location.state`); sin él, las dos pantallas redirigen a `/config`. Siempre llegar con clicks.
- **El modal de atípico no se cierra con Escape** (decisión de producto, M3.2): hay que hacer click en "Rechazar" o "Aceptar". Los dos botones tienen el mismo estilo a propósito; elegir por nombre accesible.
- **El PDF se descarga con un `<a download>` sobre un blob** (`api/export.ts::guardarPdf`): se captura con el evento `download` de Playwright, no con la respuesta de red.
- **Emails únicos por corrida** para que el registro no choque con `AUTH_EMAIL_ALREADY_REGISTERED` si la base no se recrea (en local). En CI la base es efímera.
- **Dominio:** el registro exige `@ucc.edu.ar`; Mailpit acepta cualquier destinatario.
- **Preferir `getByRole`/`getByLabel`** sobre clases CSS: las clases del tema "Instrumento" cambian seguido; los nombres accesibles ya están cuidados (pasadas de accesibilidad y limpieza de Sonar).

**CI:** job `e2e` que depende del despliegue efímero (B5): `docker compose -f docker-compose.yml -f docker-compose.e2e.yml up -d --build`, esperar `/ping`, `alembic upgrade head`, `npx playwright install --with-deps chromium`, `npm run test:e2e`, y subir `frontend/playwright-report/` y `frontend/test-results/` como artefactos **siempre** (no solo al fallar: el reporte en verde es evidencia del TP y de la "Capa 4" de `testing.md`). Correr solo en PR a `staging`/`main` para no alargar cada push.

**Local (para la demo):** el mismo compose en la máquina de Kevin y `npm run test:e2e` contra `http://localhost`, con la interfaz de Mailpit en `http://localhost:8025` abierta para mostrar el mail recibido.

**Después:** todo defecto que encuentren estos tests va al registro de defectos (B10) con su test de regresión; actualizar `testing.md` ("Capa 3: implementada") y `docs/pendientes-tecnicos.md`.

- **Hecho:** los seis escenarios en verde en cada despliegue del pipeline, reporte HTML como artefacto, y una corrida local grabada para la demo.

### B7. Herramienta nueva (k6) + stress y esfuerzo sostenido (8 h)

**Por qué k6.** Lo que define la elección es que la consigna pide umbrales y reportes generados por el pipeline. k6 trae umbrales nativos (`thresholds`) que hacen fallar el proceso con código de salida distinto de cero, exporta el resumen a JSON/HTML (`handleSummary`) y tiene acción oficial para GitHub Actions; los scripts son JavaScript, que ya se usa en el frontend. Locust tiene a favor que es Python, pero no trae umbrales que corten el job (hay que programarlos a mano). JMeter es pesado de versionar (XML) y Artillery tiene menos tracción. Contra k6: no habla SSE de forma nativa; se resuelve porque con `etapas=1` el stream termina solo en `complete` y k6 lee la respuesta completa, y Etapa 2 se carga por `simulate-exclusion`, que es sin estado. Esto queda como hipótesis hasta la prueba de concepto: si la PoC la contradice, la matriz decide otra cosa y se documenta.

Proceso de 5 pasos, en `docs/calidad/herramienta-carga.md`:
1. **Requisitos:** HTTP + respuestas SSE, umbrales que fallen el job, reporte exportable, corre en GitHub Actions, scripts versionables, curva de aprendizaje.
2. **Mercado:** k6, Locust, JMeter, Artillery.
3. **Prueba de concepto:** el mismo escenario corto en k6 y Locust contra el despliegue local.
4. **Matriz de decisión ponderada** con los resultados de la PoC.
5. **Despliegue incremental:** script local → job manual (`workflow_dispatch`) → job programado → umbrales bloqueantes.

Escenarios (Etapa 2 ajusta 13 distribuciones y es CPU intensiva; la sesión vive en memoria del proceso, y eso es justamente lo que interesa observar):
- **Stress:** rampa de usuarios sobre `preview-columns`, `simulate-exclusion` y `stream` con `etapas=1`, hasta el punto de quiebre.
- **Esfuerzo sostenido:** carga moderada 30 a 60 min, vigilando memoria del backend (`session_store` con TTL) y tasa de error.
- **Umbrales:** se fijan con la primera corrida y se congelan: p95 por endpoint, tasa de error < 1 %, memoria sin crecimiento sostenido.
- Reportes como artefactos. Stress en el pipeline sobre el despliegue efímero; soak manual o programado, no en cada PR.
- **Hecho:** stress y soak ejecutados, con resultados, umbrales y un job que falla si se superan.

### B8. Casos de prueba dinámicos documentados (5 h)
- Documento con los casos de §2.5: ID, requisito, técnica, entrada, esperado, test que lo implementa.
- Lo que falte, como tests parametrizados (`pytest.mark.parametrize` con IDs legibles).
- **Hecho:** cada caso apunta a un test que existe y pasa.

### B9. Documentos de QA (8 h)
En `docs/calidad/`:
- `plan-de-pruebas.md` (versionado): alcance, criterios de entrada, salida y suspensión, ambientes (efímero CI, local), cronograma, mapa de niveles de prueba.
- `matriz-iso25010.md`: adecuación funcional, eficiencia de desempeño, compatibilidad, usabilidad, fiabilidad, seguridad, mantenibilidad, portabilidad; evidencia concreta y estado de cada una; top 3 justificado.
- `riesgos.md`: probabilidad × impacto. Ejemplos: resultados distintos de la tesis (impacto máximo), pendientes de Facundo sin respuesta (Chow, Mann-Kendall 1,64 vs 1,96, Gen. Pareto), SMTP caído, migraciones sin aplicar, sesión en memoria con más de un worker, SSE detrás de nginx (buffering), dependencias desactualizadas (FastAPI 0.111, DECISIÓN 033), y que el despliegue en la UCC no esté probado en este TP.
- `objetivos-de-calidad.md`, `contingencia.md`, `qa-vs-qc.md`, plantillas, `trazabilidad.md`, `principios.md`, `mapa-herramientas.md`.

### B10. Registro de defectos (3 h)
- Plantilla de issue "Defecto": pasos, esperado, obtenido, severidad, prioridad, ambiente, commit, caso de prueba, test de regresión.
- Cargar los defectos históricos de §2.7 con su evidencia; el de Mann-Kendall queda abierto.
- Rojo/verde con uno (el 3 o el 7 son los más claros), con dos corridas y capturas.
- **Hecho:** cada defecto cerrado enlaza a un test que lo cubre.

### B11. Métricas (4 h)
- Producto: Sonar y `radon` (complejidad ciclomática, índice de mantenibilidad); duplicación; cobertura sentencia/decisión.
- Proceso: tasa de fallo de CI, lead time de PR, defectos por fase (auditoría, revisión, CI, uso real).
- Proyecto: avance de bloques contra el cronograma.
- Interpretación de cada una.

### B12. Informe PDF y demo (6 h)
- Informe: nivel declarado, metas cumplidas y no cumplidas (tabla de §3 actualizada), evolución de métricas (antes de B1 vs final), análisis crítico, conclusiones, y qué queda para el despliegue en la UCC (Gmail real).
- Demo: despliegue local desde cero, pipeline completo en GitHub Actions, E2E con Mailpit, corrida de carga.
- Ensayo de preguntas individuales sobre todo el trabajo, incluido lo heredado del repo que se use como evidencia.

---

## 7. Cronograma

| Semana | Fechas | Bloques |
|---|---|---|
| 1 | 08/10 a 12/10 | B0, B1a, B10 (plantilla y carga de históricos) |
| 2 | 13/10 a 19/10 | B2, B3, B4, B5, B7 (pasos 1 a 3) |
| 3 | 20/10 a 23/10 | B6, B7 (corridas y umbrales), B8, B9, B11 |
| Cierre | 24/10 a 26/10 | B13 (si Octavio dio el acceso), B12, congelar métricas, corrida final completa, informe |

Son unas 75 a 80 horas para una sola persona en 18 días. Si hay que recortar, el orden de sacrificio es: soak programado (queda manual), parte de B8 (documentar menos casos), el flujo CU-02 de B6. No se recorta nada que figure en la tabla de metas del Nivel 3.

---

## 8. Riesgos de este plan

- **Permisos del repo:** el secret `SONAR_TOKEN`, el cambio a análisis por CI y los checks requeridos del ruleset necesitan admin. El repo es de Octavio y está de intercambio: conseguir el acceso la primera semana.
- **Tiempo de CI:** despliegue + E2E + Sonar puede llevar el pipeline a 15 o 20 minutos. Mitigar con caché de imágenes y E2E solo en PR a `staging`/`main`.
- **Ejecución fallida "que detectó un problema real":** hay 6 en el historial (lint de frontend, `ruff format`, pytest). Confirmar en Actions cuál detectó un problema real y guardar el enlace antes de que venzan los logs. Si ninguna sirve, la primera que bloquee el gate nuevo lo cubre.
- **Coherencia de números:** todo número del informe sale del pipeline, no de corridas locales como las de §1.
