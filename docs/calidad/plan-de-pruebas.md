# Plan de pruebas — METIS V1.0

TP integrador de Calidad de Software, bloque B9 (`docs/plan-tp-calidad-software.md`). Estructura basada en IEEE 829
(plan de pruebas): identificador, ítems, alcance, enfoque, criterios, entregables, ambientes, responsabilidades y
cronograma.

| Versión | Fecha | Autor | Cambios |
|---|---|---|---|
| 1.0 | 09/10/2026 | Kevin Massholder | Primera versión. Formaliza la estrategia que vivía en `.claude/rules/testing.md` y suma lo construido en B1–B8 |
| 1.1 | 09/10/2026 | Kevin Massholder | Cronograma: B9 y B11 hechos |

Este documento se versiona con el repo: un cambio de alcance, criterio o ambiente sube la versión y se anota en la
tabla de arriba, en el mismo PR que lo introduce.

---

## 1. Identificador y propósito

**METIS-PP-1.0.** Define qué se prueba de METIS V1.0, con qué técnicas y herramientas, en qué ambientes, y con qué
criterios se acepta, se suspende o se da por terminada cada actividad de prueba.

Documentos relacionados, todos en `docs/calidad/`:

| Documento | Qué aporta a este plan |
|---|---|
| [`objetivos-de-calidad.md`](objetivos-de-calidad.md) | Las metas medibles que estos criterios verifican |
| [`riesgos.md`](riesgos.md) | La priorización: qué se prueba primero y con más profundidad |
| [`matriz-iso25010.md`](matriz-iso25010.md) | Las características de calidad y su evidencia |
| [`trazabilidad.md`](trazabilidad.md) | Requisito → caso → test → defecto |
| [`casos-de-prueba.md`](casos-de-prueba.md) | Los casos de caja negra (B8) |
| [`registro-defectos.md`](registro-defectos.md) | Cómo se registra y se cierra un defecto (B10) |
| [`contingencia.md`](contingencia.md) | Qué hacer si cae una dependencia |
| [`plantillas.md`](plantillas.md) | Plantillas de caso y de defecto |

---

## 2. Ítems de prueba

| Ítem | Ubicación | Versión bajo prueba |
|---|---|---|
| Motor estadístico (Etapa 1, Etapa 2, agregación, contrato) | `backend/metis/core/` | El commit de cada corrida de CI |
| API REST y stream SSE | `backend/metis/api/`, `backend/metis/services/` | ídem |
| Autenticación y verificación por mail | `backend/metis/auth/` | ídem |
| Persistencia | `backend/metis/db/`, `backend/alembic/` | ídem |
| Informe PDF | `backend/metis/reportes/` | ídem |
| Frontend (7 pantallas) | `frontend/src/` | ídem |
| Despliegue | `docker-compose.yml` + `docker-compose.ci.yml`, `nginx/`, `scripts/deploy-local.sh` | ídem |

**Base de requisitos:** *METIS — Manual de Requerimientos v5.0* (octubre de 2026), 40 requisitos funcionales
(RF-GEN-P-01 a P-10, RF-GEN-O-01 a O-13, RF-CU01-01 a 08, RF-CU02-01 a 05, RF-CU03-01 a 04). El manual no define
requisitos no funcionales; las características de calidad salen de ISO/IEC 25010 (`matriz-iso25010.md`).

---

## 3. Características a probar

Por prioridad de riesgo (`riesgos.md`):

1. **Exactitud del motor estadístico:** los estadísticos, valores críticos y veredictos de la Etapa 1, y los
   parámetros, el EEA y los eventos de diseño de la Etapa 2. Es lo que, si falla, falla en silencio: un número de
   diseño mal calculado sin advertencia (5 de los 10 defectos registrados fueron así).
2. **Reglas de negocio:** contrato de datos, los dos bloqueantes (menos de 10 datos y orden cronológico), jerarquías
   de independencia y homogeneidad, nivel de confianza, casos especiales de la Etapa 2.
3. **Flujo interactivo del stream:** las dos pausas (atípico de Chow y elección de distribución), su reanudación y
   su timeout.
4. **Persistencia y aislamiento de CU-01:** el análisis se guarda con sus decisiones; un usuario no ve análisis
   ajenos; CU-02 no persiste nada.
5. **Contratos de API:** la estructura de error estándar y el catálogo de códigos sincronizado en backend,
   documentación y frontend.
6. **Integración con SMTP:** registro, envío del mail y verificación.
7. **Desempeño bajo carga:** latencia y tasa de error con carga concurrente y sostenida.

## 4. Características que no se prueban, y por qué

| Fuera de alcance | Motivo |
|---|---|
| CU-03 (`POST /validate/`, API Keys) | No está implementado (RF-CU03-01 a 04). Se prueba cuando exista |
| Regresión matemática contra las 9 estaciones de la tesis, automatizada | La lleva Octavio por su lado (`testing.md`). La exactitud se cubrió con la auditoría manual de 4 fases (`docs/auditoria/`) y con tests unitarios por fórmula |
| SMTP real de la UCC o Gmail | Se prueba con Mailpit, un servidor SMTP real de captura (DECISIÓN 049). El relay real va con el despliegue en la UCC (`integracion-smtp.md` §4) |
| Despliegue en los servidores de la UCC | Depende de IT (DECISIÓN 028). Este plan cubre el despliegue efímero en CI y el local |
| Navegadores distintos de Chromium | Los E2E corren en un solo navegador (DECISIÓN 046, alcance chico y deliberado) |
| Accesibilidad automatizada | Se verificó contraste WCAG AA a mano (DECISIÓN 043); no hay herramienta automática en el pipeline |
| Requisitos no implementados (RF-GEN-O-04, O-06, RF-CU01-05, RF-CU02-05) | No hay nada que probar. Figuran como brecha en `trazabilidad.md` |

---

## 5. Enfoque

### 5.1 Mapa de niveles

Cantidades medidas el 09/10/2026 sobre `staging` (`d8d80dc`), con `pytest --collect-only -m <marker>` y los
archivos de test del frontend.

| Nivel | Qué verifica | Herramienta | Dónde | Tests | Cuándo corre |
|---|---|---|---|---|---|
| **Unidad** | Funciones puras del motor, validadores del borde de la API, servicios con dobles | pytest | `backend/tests/unit/` | 665 | Cada push y PR (job `test`) |
| | Componentes, hooks, cliente HTTP, páginas bajo `StrictMode` | Vitest + Testing Library | `frontend/src/**/*.test.ts(x)` (59 archivos) | 497 | Cada push y PR (job `frontend`) |
| **Integración** | El stream de punta a punta con sus pausas, la agregación, la exclusión ≡ rechazo de Chow | pytest | `backend/tests/integration/` | 14 | Cada push y PR (job `test`) |
| | Persistencia contra PostgreSQL real; registro contra Mailpit | pytest | `backend/tests/integration/db/` | 6 | ídem, con `postgres:15` y `mailpit` como servicios |
| **Sistema** | Smoke del sistema desplegado detrás de nginx | pytest + httpx | `backend/tests/smoke/` | 7 | Cada push y PR (job `despliegue`) |
| | Flujos completos de CU-01 y CU-02 desde el navegador | Playwright | `frontend/e2e/` | 6 escenarios (7 tests) | Cada PR a `staging`/`main` (job `despliegue`) |
| | Carga: stress con umbrales | k6 | `carga/k6/` | 1 escenario | Cada PR (job `carga`) |
| | Esfuerzo sostenido (30 min) | k6 | `carga/k6/` | 1 escenario | Manual y semanal (`carga-sostenida.yml`) |
| **Aceptación** | Que el resultado coincida con la tesis y con lo que esperan los directores | Revisión manual contra la tesis; uso por los directores | `docs/auditoria/`, reuniones | — | Por hito (auditoría de 4 fases; revisiones de Facundo y Carlos) |

**Forma de la pirámide.** 1.162 tests de unidad, 20 de integración y 13 de sistema. La base ancha es deliberada:
el riesgo principal está en el motor estadístico, que es una librería pura (`core/` no importa nada de HTTP ni de
la base) y se prueba barato y rápido. Los niveles de arriba cubren lo que la unidad no ve: los defectos F1, F4,
F5, F6 y F9 del informe de diagnóstico de la UI solo aparecían con el sistema completo corriendo (DECISIÓN 046).

### 5.2 Técnicas de diseño

| Técnica | Dónde se aplica |
|---|---|
| Valores límite, clases de equivalencia y tablas de decisión | `casos-de-prueba.md` (74 casos) |
| Oráculo de referencia externo | Valores publicados en la tesis de Facundo y tablas de la bibliografía: un test de fórmula compara contra el número de la fuente, no contra la salida previa de METIS |
| Comparación con otras herramientas | R, SciPy, LibreOffice y SAMHIA sobre las 9 series de la tesis (`docs/auditoria/comparacion-herramientas/`, PR #109) |
| Regresión por defecto | Todo defecto se cierra con un test que lo reproduce, en rojo antes del fix y en verde después (`registro-defectos.md`) |
| Cobertura estructural | Sentencia y decisión (`pytest-cov --cov-branch`, `@vitest/coverage-v8`), como medida de lo que falta probar, no como objetivo en sí |
| Pruebas basadas en riesgo | El orden de §3 y la profundidad de cada nivel salen de `riesgos.md` |

### 5.3 Estructura de un test

Arrange-Act-Assert: se prepara la entrada, se ejecuta una sola acción y se verifica el resultado. Los tests de
`tests/unit/casos_dinamicos/` son el ejemplo explícito. Un test con el resultado esperado tomado de la salida actual
del código no es un test de exactitud: el valor esperado sale de la fuente (tesis, bibliografía, contrato) y se
escribe **antes** de correr el test, que es lo que pide el criterio de §6.1.

---

## 6. Criterios

### 6.1 Criterio de aceptación de un ítem

| Ítem | Pasa si |
|---|---|
| Prueba estadística de Etapa 1 | Estadístico, valor crítico y veredicto coinciden con la tesis o la planilla de Facundo para la misma serie (`pytest.approx`, tolerancia según la precisión publicada) |
| Distribución y método de Etapa 2 | Parámetros y EEA coinciden con la tesis, o la discrepancia está explicada y registrada (`docs/auditoria/pendientes/`) |
| Regla de negocio | La acción coincide con la columna correspondiente de la tabla de decisión (`casos-de-prueba.md`) |
| Endpoint | Respuesta y código de error coinciden con `api-contracts.md`; el error tiene la estructura `{"error": {...}}` |
| Pantalla | El flujo se completa en el navegador sobre el sistema desplegado (E2E o verificación manual con evidencia) |
| Desempeño | p95 por endpoint y tasa de error dentro de `carga/umbrales.json` |

### 6.2 Criterios de entrada, por nivel

| Nivel | Se empieza cuando |
|---|---|
| Unidad | La fórmula o regla tiene referencia en `formulas-etapa{1,2}.md` o en una decisión; el resultado esperado está escrito |
| Integración | Los tests de unidad del módulo pasan; PostgreSQL y Mailpit están levantados con las migraciones aplicadas |
| Sistema | El build de producción se desplegó con `deploy-local.sh` (o el job `despliegue`) y el smoke pasa |
| Aceptación | El hito tiene sus tests de sistema en verde |

### 6.3 Criterios de salida (para mergear un PR)

Los siete jobs del CI en verde (`.github/workflows/ci.yml`):

- `lint`: ruff check y format sin hallazgos.
- `test`: 0 fallas en unidad e integración, sin tests salteados por servicio caído (`METIS_REQUIRE_DB=1`,
  `METIS_REQUIRE_MAILPIT=1`).
- `error-catalog`: catálogo de errores sincronizado.
- `frontend`: lint, tests y build.
- `quality-gate`: cobertura del código nuevo ≥ 80 % (backend y frontend, `diff-cover`) y duplicación ≤ 5 % (`jscpd`).
- `despliegue`: smoke y, en PR, los seis E2E.
- `carga` (en PR): p95 y tasa de error dentro de los umbrales.

Y además: si el PR toca `frontend/`, evidencia del flujo en el navegador (Capa 4 de `testing.md`). Si corrige un
defecto, su issue cerrado con el test que lo cubre. SonarCloud informa pero hoy no bloquea; pasa a requerido con
B13 (DECISIÓN 077).

### 6.4 Criterios de suspensión y reanudación

| Se suspende la prueba si | Se reanuda cuando |
|---|---|
| Falla el despliegue efímero o el smoke: nada de lo de arriba es confiable | El smoke vuelve a pasar |
| Un servicio externo del pipeline (GitHub Actions, el registry de imágenes) no responde | El servicio vuelve; no se mergea saltando el job (`contingencia.md`) |
| Un test de exactitud falla contra la tesis y no se sabe si el error es del código o de la fuente | Se escala a Facundo y se registra en `pendientes-facundo.md`; el resto de la suite sigue |
| Más de un E2E falla por la misma causa de ambiente (por ejemplo, la base sin migrar) | Se corrige el ambiente y se corre de nuevo la suite completa |

---

## 7. Entregables

| Entregable | Dónde |
|---|---|
| Este plan, versionado | `docs/calidad/plan-de-pruebas.md` |
| Casos de prueba documentados | `docs/calidad/casos-de-prueba.md` |
| Scripts de prueba | `backend/tests/`, `frontend/src/**/*.test.*`, `frontend/e2e/`, `carga/k6/` |
| Reportes por corrida | Artefactos de CI: `reporte-backend`, `reporte-frontend`, `reporte-e2e`, `reporte-carga`, `reporte-calidad/metricas.json`, y el resumen del job |
| Registro de defectos | GitHub Issues con label `defecto`, resumido en `registro-defectos.md` |
| Matriz de trazabilidad | `docs/calidad/trazabilidad.md` |
| Informe final | Informe PDF del TP (B12) |

---

## 8. Ambientes

| Ambiente | Para qué | Cómo se levanta |
|---|---|---|
| Desarrollo local | Unidad e integración mientras se programa | `docker-compose up -d backend postgres` y `docker exec <backend> pytest …`, o `npm test` en `frontend/` |
| Despliegue local | Smoke, E2E y carga en la máquina propia; la demo | `scripts/deploy-local.sh`: configuración de producción (`docker-compose.ci.yml`), base propia (`metis-ci`), migraciones, usuario sembrado y smoke. Ocupa el puerto 80 |
| Efímero en CI | Todo el pipeline, en cada push y PR | Runner `ubuntu-latest` de GitHub Actions; el job `despliegue` usa el mismo `deploy-local.sh` |
| Producción (servidores UCC) | Fuera de este plan | Pendiente de IT (DECISIÓN 028) |

Los datos de prueba son series sintéticas construidas para forzar cada comportamiento y las 9 series de la tesis
(`docs/auditoria/`). Los fixtures del E2E están copiados en `frontend/e2e/fixtures/` para que un cambio en
`docs/series prueba/` no los rompa en silencio.

---

## 9. Responsabilidades

| Rol | Quién |
|---|---|
| Diseño y ejecución de este plan, E2E, carga y documentos de calidad | Kevin Massholder (el TP de la materia lo cursa solo él, D6 del plan) |
| Motor estadístico de Etapa 1, regresión matemática contra la tesis | Octavio Carpineti (antecedente del repo; no es aporte de este TP) |
| Oráculo de dominio: confirma fórmulas y resultados esperados | Mgter. Ing. Facundo Ganancias |
| Aceptación de uso y requisitos de CU-03 | Dr. Ing. Carlos Catalini |
| Admin del repo: secrets, ruleset, checks requeridos (B13) | Octavio Carpineti |

---

## 10. Cronograma

Del plan del TP (`plan-tp-calidad-software.md` §7), con lo hecho a la fecha de esta versión:

| Semana | Bloques | Estado al 09/10/2026 |
|---|---|---|
| 1 (08/10 a 12/10) | B0, B1a, B10 | Hechos (#110, #111, #124) |
| 2 (13/10 a 19/10) | B2, B3, B4, B5, B7 | Hechos antes de la fecha (#111 a #113, #126) |
| 3 (20/10 a 23/10) | B6, B7, B8, B9, B11 | B6 (#113), B8 (#127), B9 (#128) y B11 (`metricas.md`) hechos |
| Cierre (24/10 a 26/10) | B13, B12 | Pendientes. B13 depende del acceso de admin |

---

## 11. Riesgos del plan

Los riesgos del producto, con su probabilidad e impacto, están en `riesgos.md`. Los del propio plan de pruebas:

- **Una sola persona ejecuta todo.** Si se atrasa, el orden de recorte es el de `plan-tp-calidad-software.md` §7.
- **El oráculo de dominio responde con demora.** Hay preguntas abiertas a Facundo (Mann-Kendall 1,64 frente a 1,96,
  redondeo de Cramer, Generalizada de Pareto). Mientras tanto se prueba contra la implementación documentada y la
  divergencia queda registrada.
- **El gate de SonarCloud no bloquea** hasta B13, que necesita permisos que Kevin no tiene. Mientras tanto, el gate
  propio (`quality-gate`) cubre cobertura nueva y duplicación.
