# Métricas de calidad de METIS

TP integrador de Calidad de Software, bloque B11. Métricas de producto, de proceso y de proyecto, cada una con su
interpretación, las mejoras medidas antes y después, y la triage de los hallazgos de SonarCloud.

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0 | 09/10/2026 | Primera versión. Valores de `staging` en `4903761` (PR #128) |
| 2.0 | 22/10/2026 | Valores de la corrida final: CI #269 sobre `staging` en `a26402b` (PR #146). SonarCloud por CI (B13) con Security y Reliability en A; triage de los 205 code smells; segunda mejora medida (Security C → A, DECISIÓN 082); proceso y proyecto actualizados al cierre |

## 1. De dónde salen los números

**Corrida final:** CI #269, push a `staging` del 22/10/2026 sobre `a26402b`, en verde con los ocho jobs. Todos los
números de producto de este documento salen de esa corrida o del análisis de SonarCloud que la acompaña; los de
proceso, de la API de GitHub al cierre del mismo día.

| Fuente | Qué mide | Cómo se reproduce |
|---|---|---|
| `reporte-calidad/metricas.json` (job `quality-gate`) | Tests, cobertura de sentencia y decisión, duplicación (jscpd), complejidad del backend (radon) | Se genera en cada corrida de CI; en local, `scripts/test.sh backend\|frontend\|duplicacion\|complejidad` |
| `reporte-backend/junit-backend.xml` y `coverage.xml` | Tests por nivel y cobertura por archivo | Ídem, job `test` |
| `reporte-e2e` (job `despliegue`) | Resultado de los E2E con Playwright | Ídem |
| `reporte-carga` (job `carga`, PR #146) y `reporte-carga-sostenida` (workflow `carga-sostenida.yml`) | Stress y esfuerzo sostenido con k6 | `scripts/carga.sh ci\|sostenido` |
| `scripts/metricas_proceso.py` | Tasa de fallo del CI, lead time de PR, defectos por fase y severidad | `python scripts/metricas_proceso.py` (necesita `gh` autenticado) |
| SonarCloud, rama `staging` | Ratings, issues, complejidad cognitiva, deuda técnica, quality gate | `sonarcloud.io/project/overview?id=CarpinetiOctavio_PI_METIS&branch=staging` |

Regla del plan: los números del informe salen del pipeline o de estos scripts, no de corridas sueltas.

---

## 2. Métricas de producto

### 2.1 Tamaño

| Medida | Valor | Fuente |
|---|---|---|
| Líneas de código del backend (`metis/`, sin comentarios ni blancos) | 6.967 (10.315 en total; 2.220 de comentarios y docstrings) | radon |
| Líneas de código analizadas por SonarCloud (sin tests) | 17.839: TypeScript 8.688, Python 6.846, CSS 1.954, YAML 329, Docker 22 | SonarCloud |
| Tests | 984 del backend, 588 del frontend, 7 E2E, 10 de smoke | `metricas.json`, `reporte-e2e`, `tests/smoke/` |

**Interpretación.** El backend de producción sigue siendo chico (7.000 líneas) y casi uno de cada cinco renglones es
comentario o docstring, en buena parte la referencia a la ecuación de la tesis que exige la regla de "ninguna fórmula
sin referencia". La cifra de SonarCloud no es comparable con la de la versión 1.0 (31.791): desde B13 los tests se
declaran como tests (`sonar.tests`) y ya no cuentan como código fuente.

### 2.2 Complejidad

| Medida | Valor | Fuente |
|---|---|---|
| Complejidad ciclomática promedio | **5,42** por función (224 funciones) | radon |
| Distribución por rango | A (1–5): 160 · B (6–10): 32 · C (11–20): 25 · D (21–30): 4 · E (31–40): 2 · F (> 40): 1 | radon |
| Funciones con CC > 10 | 32 (14,3 %) | radon |
| Complejidad cognitiva total | 1.909 | SonarCloud |

Las más complejas:

| Función | CC | Por qué |
|---|---|---|
| `services/analysis_service.py::stream_analysis` | 41 | Orquesta el stream completo: parseo, Etapa 1, las dos pausas, Etapa 2, persistencia, y un evento de error por cada salida posible |
| `reportes/pdf.py::_seccion_simulacion` | 35 | Arma la página de comparación con y sin los puntos excluidos, con un caso por cada combinación de Etapa 1/2 presente o ausente |
| `core/etapa2/distributions/gen_pareto.py::ajustar` | 31 | Cuatro métodos de estimación con sus guards de dominio |
| `core/etapa2/distributions/gve.py::ajustar` | 28 | Ídem, tres métodos con iteración y guards |
| `reportes/pdf.py::_seccion_etapa1` | 28 | Las ocho pruebas por batería, con sus niveles y la decisión ante los atípicos |

**Interpretación.** El promedio sigue en el rango "simple" (A, ≤ 5) y siete de cada diez funciones también. La
complejidad se concentra donde el dominio la impone: los ajustes de distribuciones tienen una rama por método y por
guard de la tesis, y partirlas separaría lógica que se lee contra una misma sección del capítulo IV.
`stream_analysis` es la excepción que empeoró: pasó de 35 (versión 1.0) a 41 entre el 09/10 y el 22/10, el período en
que se sumaron el α configurable, la pausa con varios atípicos y la cobertura configurable (decisiones 078, 079 y
081), todas orquestadas ahí. Es la primera candidata a refactor (una función por fase del stream). No se hace en
este TP: está cubierta por tests de integración y por los E2E, y tocarla a días de la entrega es más riesgo que
beneficio. Queda como deuda conocida, con la acción en §7.

### 2.3 Mantenibilidad

| Medida | Valor | Fuente |
|---|---|---|
| Índice de mantenibilidad por archivo | 74 de 75 archivos en rango A (> 19); 1 en rango C | radon |
| Archivo con menor índice | `reportes/pdf.py`: **0,0** (rango C) | radon |
| Deuda técnica | 1.372 min (≈ 23 h); ratio 0,3 %; rating **A** | SonarCloud |
| Code smells | 205 (triage en §6) | SonarCloud |

**Interpretación.** `pdf.py` cae a 0 en el índice de radon (que recorta en cero) por volumen, complejidad y funciones
largas de armado de tablas; es el único archivo fuera del rango A y aloja dos de las cinco funciones más complejas: la
señal es consistente. Es código de presentación (DECISIÓN 075) sin lógica estadística, con su riesgo acotado por
`test_pdf.py` y por el E2E-3, que descarga el PDF. La deuda de SonarCloud, 0,3 % del costo de desarrollo estimado,
es baja: el rating A dice que el código, en conjunto, es barato de mantener.

### 2.4 Duplicación

| Medida | Valor | Fuente |
|---|---|---|
| Líneas duplicadas (`backend/metis` + `frontend/src`) | **0,52 %** (128 de 24.550; 10 clones) | jscpd, gate ≤ 5 % |
| Líneas duplicadas (fuentes de SonarCloud) | 0,8 % (192 líneas); 0,0 % en el código nuevo | SonarCloud, gate ≤ 3 % en código nuevo |

**Interpretación.** Las dos herramientas miden cosas distintas: jscpd solo el código de producción con un mínimo de
tokens por clon; SonarCloud incluye estilos, workflows y Dockerfiles. Las dos quedan muy por debajo del 5 % del
Nivel 3. La duplicación conocida que importa (los estimadores muestrales repetidos en `etapa2/`, DECISIÓN 022) es de
pocas líneas por archivo y por eso jscpd no la cuenta como clon: queda como deuda escrita, no medida.

### 2.5 Cobertura

| | Sentencias | Decisión (ramas) | Fuente |
|---|---|---|---|
| Backend | **95,09 %** (3.392 / 3.567) | **85,36 %** (857 / 1.004) | `metricas.json`, CI #269 |
| Frontend | **97,78 %** (6.790 / 6.944) | **88,84 %** (1.815 / 2.043) | ídem |
| Código nuevo (SonarCloud) | 95,5 % | No lo informa | Quality gate de SonarCloud, umbral 80 % |
| Código nuevo de cada PR | ≥ 80 % (gate) | No lo mide | `diff-cover`, job `quality-gate` |

**Interpretación.** Las cuatro cifras del código existente superan el 80 % del Nivel 3. La de decisión es siempre la
más baja, como se espera: cada guard de dominio de las distribuciones (por ejemplo, `logpearson3.py`, con 68 % de
ramas) agrega ramas que solo se ejercitan con series construidas para caer en ese caso. Un archivo bajó desde la
versión 1.0: `api/v1/history.py`, de 89 % a 75 % de sentencias, porque los dos endpoints de exclusiones guardadas
(DECISIÓN 080) tienen probada su lógica en el servicio y contra PostgreSQL real, pero no sus respuestas 400 y 404 por
HTTP. El gate de código nuevo lo dejó pasar porque mide el PR completo, no archivo por archivo: es el límite conocido
de esa métrica, y la acción queda en §7. La cobertura dice qué código se ejecutó, no si el resultado es correcto: la
exactitud la mide el oráculo (`objetivos-de-calidad.md`, OC-U1).

### 2.6 Confiabilidad y seguridad según SonarCloud

| Medida | 09/10/2026 (versión 1.0) | 22/10/2026 (corrida final) |
|---|---|---|
| Quality gate (Sonar way, código nuevo) | OK | **OK** |
| Reliability rating (código total) | D: 1 bug crítico | **A**: 0 bugs |
| Security rating (código total) | D: 7 vulnerabilidades | **A**: 0 vulnerabilidades |
| Maintainability rating | A | **A** |
| Security hotspots | 0 | 0 (100 % revisados) |

Cómo se llegó de D a A, con commits verificables:

| Hallazgo | Corrección | Commit |
|---|---|---|
| Bug crítico `S3518`, división por cero en Wald-Wolfowitz | Falso positivo (el guard previo garantiza n1, n2 ≥ 1): documentado en el código y marcado | `248d1c3` (15/10), junto con tres hallazgos reales de Reliability (`np.where` → `np.nonzero`, `datetime.utcnow()` deprecado) |
| `S6470` (copia del contexto entero a la imagen) y `S6471` (imagen como root) | `COPY` explícitos, `.dockerignore` y usuario sin privilegios | `3bb183e` (15/10). Security pasa de D a C |
| `S8541` y `S8544` (×5): `pip install` sin `--only-binary` ni hashes | Lock con versiones y hashes de las 80 dependencias, instalado con `--require-hashes` en CI y en la imagen | `33f5931`, PR #145 (22/10), DECISIÓN 082. Security pasa de C a A |
| `S7637`: action de terceros fijada por tag | Fijada por SHA de commit | `193b435` (19/10); ver §3.1, corrida #254 |

**Interpretación.** El gate de SonarCloud mira el código nuevo y estuvo siempre en OK; los ratings D venían del
código total, escrito antes de que el análisis los señalara. Ninguno de los hallazgos estaba en el motor estadístico:
eran de endurecimiento del contenedor y de la cadena de dependencias, más un falso positivo. Hoy los tres ratings
están en A.

---

## 3. Métricas de proceso

### 3.1 Tasa de fallo del CI

| Período | Corridas | Exitosas | Fallidas | Tasa de fallo |
|---|---|---|---|---|
| Total (05/05 al 22/10/2026) | 269 | 257 | 12 | **4,5 %** |
| Antes del gate (< 08/10) | 215 | 209 | 6 | 2,8 % |
| Desde el gate (B1a, #111) | 54 | 48 | 6 | 11,1 % |

Las 12 corridas fallidas, clasificadas por causa:

| Corrida | Fecha | Rama | Qué falló | Causa | ¿Problema real? |
|---|---|---|---|---|---|
| #1 | 06/05 | `feature/github-actions` | ruff format y pytest | Puesta en marcha del pipeline | Configuración |
| #13, #14 | 20/07 | `feature/core-etapa2` | ruff format; `test_gen_pareto_mc_q100_serie_facundo`: **384,80 contra 90,63** de la tesis | Error en Generalizada de Pareto por mínimos cuadrados: el barrido se quedaba con una raíz espuria cerca de ε ≈ 0. El test quedó en `skip` con la causa documentada (DECISIÓN 010) hasta que DECISIÓN 068 corrigió la fórmula (04/09) | **Sí: defecto del producto** |
| #29 | 01/08 | `feature/frontend-pasada4` | pytest: `KeyError: 'JWT_SECRET_KEY'` | Variable de entorno faltante en el job | Configuración |
| #38 | 05/08 | `fix/cramer-particion-400` | 2 tests de `test_stream_cramer_particion.py` | El test del defecto D-06 en rojo antes del fix | **Sí: el test detectó el defecto que el PR corregía** |
| #61 | 06/08 | `feat/spotlight-cards` | ESLint | Estilo | Estilo |
| #234 | 09/10 | `feature/tp-calidad-b5-b6` | El workflow no arrancó | YAML inválido (`:all: ` sin comillas) | Configuración |
| #241 | 09/10 | `feature/tp-calidad-b7` | Stress k6: `permission denied` al escribir el CSV | Permisos del contenedor de k6 | Configuración |
| #251, #252 | 19/10 | PR #131, desde el fork | Job `sonarcloud` | Un PR desde un fork no recibe el secret `SONAR_TOKEN`; se reabrió como #132 desde una rama del repo original | Configuración |
| #253, #254 | 19/10 | `sync/fork-a-original` (PR #132) | Job `sonarcloud`: `QUALITY GATE STATUS: FAILED` | El gate de Sonar (Security rating del código nuevo) detectó `githubactions:S7637`: la action de SonarSource referenciada por tag, que se puede mover. Corregida en `193b435`; la #255 pasó y SonarCloud registró el issue como corregido | **Sí: el quality gate bloqueó un problema de seguridad** |

**Interpretación.** Las 12 fallas tienen causa determinista: no hay fallas intermitentes conocidas. Cinco corridas
detectaron un problema real (tres problemas distintos), seis fueron de configuración del pipeline y una de estilo.
La suba de la tasa desde el gate (11,1 %) no es un deterioro del producto: cuatro de esas seis fallas son de puesta en
marcha de jobs nuevos (despliegue, carga, SonarCloud desde un fork) y dos son el gate haciendo su trabajo. Ninguna
falla llegó a `staging`.

**La ejecución fallida que pide la consigna es la #254.** Es la más reciente, tiene los logs disponibles y muestra
el circuito completo: el análisis de SonarCloud dentro del pipeline encontró una vulnerabilidad en código nuevo, el
gate falló, el job falló y el PR no se pudo mergear hasta que el commit siguiente la corrigió. Las #13/#14 (20/07)
superan los 90 días de retención de logs por defecto de GitHub.

### 3.2 Lead time de PR hacia `staging`

123 PR mergeados.

| Desde | Mediana | Promedio | p90 | < 24 h |
|---|---|---|---|---|
| La apertura del PR | 0,1 h | 1,2 h | 1,0 h | 100 % |
| El primer commit de la rama | 0,2 h | 20,8 h | 12,7 h | 94,3 % |

**Interpretación.** Los PR se abren con el trabajo ya terminado y se mergean apenas el CI da verde: el PR funciona
como compuerta de integración, no como cola de revisión. La medida desde el primer commit agrega poco porque la mayoría
de las ramas se commitean al final de la sesión de trabajo: mide el tamaño de los lotes, no el tiempo de desarrollo.
Las colas largas (promedio de 21 h contra mediana de 0,2 h) son ramas grandes de varias sesiones. Lo que esta métrica
no muestra, y el informe lo dice, es revisión entre pares: con un solo autor en el TP, la revisión la hacen el pipeline
y SonarCloud, y desde el 22/10 el Ruleset la vuelve obligatoria (§4).

### 3.3 Defectos por fase de detección y severidad

| Fase | Defectos | | Severidad | Defectos |
|---|---|---|---|---|
| Auditoría | 2 | | Crítica | 5 |
| Desarrollo | 1 | | Alta | 2 |
| Revisión | 6 | | Media | 7 |
| CI | 0 | | Baja | 5 |
| Uso real | 10 | | | |

19 defectos (issues #114 a #141), ninguno abierto, todos con test de regresión (`registro-defectos.md`).

**Interpretación.** Los **5 críticos se encontraron antes de llegar a un usuario** (auditoría, desarrollo, revisión).
Los diez de uso real son de severidad media o menor, salvo D-01 y D-02 (alta), y son de la interfaz o del informe
PDF: visibles y con alternativa. Siete de esos diez salieron de dos pasadas de uso dirigidas (D-11 el 19/10 y D-14 a
D-19 en la revisión manual del 21/10, que además encontró D-12 y D-13 revisando el código): usar la aplicación con
atención sigue encontrando lo que los tests, por construcción, no buscan. La fase CI aparece en 0 porque cada defecto se clasificó por la actividad que lo encontró
primero; las detecciones reales del pipeline (§3.1) son de defectos que ya estaban siendo corregidos o anteriores al
registro.

---

## 4. Métrica de proyecto: avance del plan contra el cronograma

| Bloque | Horas estimadas | Semana prevista | Mergeado | PR |
|---|---|---|---|---|
| B0 Gobernanza | 2 | 1 (08–12/10) | 08/10 | #110 |
| B1a Pipeline con cobertura y gate | 6–8 (con B13) | 1 | 08/10 | #111 |
| B2 Mejora de cobertura | 5 | 2 (13–19/10) | 08/10 | #111 |
| B3 Integración con PostgreSQL | 4 | 2 | 08/10 | #112 |
| B4 SMTP con Mailpit | 4 | 2 | 08/10 | #112 |
| B5 Despliegue y smoke | 6 | 2 | 09/10 | #113 |
| B6 E2E con Playwright | 8–10 | 3 (20–23/10) | 09/10 | #113 |
| B10 Registro de defectos | 3 | 1 | 09/10 | #124 |
| B7 Carga con k6 | 8 | 2 y 3 | 09/10 | #126 |
| B8 Casos de prueba | 5 | 3 | 09/10 | #127 |
| B9 Documentos de QA | 8 | 3 | 09/10 | #128 |
| B11 Métricas | 4 | 3 | 09/10 | #129 |
| B13 Sonar por CI y checks requeridos | (parte de B1) | Cierre (24–26/10) | Sonar por CI: 19/10 (#132). Ruleset activo: 22/10 | #132 |
| Cierre: Security A, E2E en cada despliegue, documentos finales | No estimado | Cierre | 22/10 | #145, #146 y este PR |
| B12 Informe y demo | 6 | Cierre | Informe: 22/10. Demo: 26/10 | Sin PR |

**Interpretación.** Los bloques de construcción terminaron en dos días de un cronograma de 18: el plan se adelantó
unas dos semanas. Lo que estiró el cierre fueron dos dependencias externas: SonarCloud por CI necesitaba llevar el
trabajo del fork al repo original con el secret disponible (#132) y el Ruleset solo lo puede editar el dueño del repo
(activado el 22/10). Las horas reales no se registraron, así que el esfuerzo por bloque no se puede comparar contra la
estimación; es una limitación de esta métrica. El trabajo se hizo con asistencia de un agente de IA (Claude Code), lo
que explica la velocidad y es un dato que el informe declara.

**Ruleset (22/10/2026).** "staging y main", activo sobre las dos ramas, sin excepciones: exige PR, impide borrar la
rama y el force push, y requiere los ocho jobs de `ci.yml`, atados a la app de GitHub Actions. Desde ahí el quality
gate bloquea el merge de derecho, no solo de hecho.

---

## 5. Mejoras medidas antes y después

### 5.1 Cobertura (B2)

Línea de base del 08/10/2026 (`plan-tp-calidad-software.md` §1, antes de B1) contra la corrida final:

| Medida | Antes (08/10) | Después de B2 (09/10) | Corrida final (22/10) |
|---|---|---|---|
| Cobertura de decisión del backend | 76,7 % (704 / 918) | 84,1 % (777 / 924) | **85,36 %** (857 / 1.004) |
| Cobertura de sentencias del backend | 91,4 % (3.016 / 3.301) | 94,7 % (3.137 / 3.314) | **95,09 %** (3.392 / 3.567) |
| `auth/dependencies.py`, `auth/jwt.py`, `auth/router.py` | 27 %, 50 %, 60 % | 100 %, 100 %, 100 % | 100 %, 100 %, 100 % |
| `core/etapa2/distributions/logpearson3.py` | 76 % | 87,2 % | 87,2 % |
| `core/etapa2/distributions/gamma2p.py` | 78 % | 89,2 % | 89,2 % |
| Tests del backend | 500 | 685 | 984 |

**Interpretación.** La mejora se eligió por riesgo, no por el número: `auth/` era el código con menos cobertura y el
que, si falla, deja a los docentes sin acceso a su historial. La cobertura de decisión del backend era la única cifra
del Nivel 3 que no se cumplía al empezar el TP; desde B2 se cumple, y después siguió subiendo aunque el código creció
un 8 % (de 3.314 a 3.567 sentencias): el gate impide que lo nuevo entre sin probar.

### 5.2 Seguridad (DECISIÓN 082)

| Medida | Antes (22/10, análisis previo a #145) | Después (#145 y corrida final) |
|---|---|---|
| Security rating (código total) | C | **A** |
| Vulnerabilidades | 5 (S8541 ×3, S8544 ×2) | **0** |
| Dependencias del backend con versión y hash fijados | 23 de 80 con versión, ninguna con hash | **80 de 80** con versión y hash |

**Interpretación.** El historial de SonarCloud registra el cambio en el análisis del merge de #145 (22/10). Es una
mejora de proceso además de producto: `scripts/check_requirements_lock.py` en el job `lint` impide que el lock quede
desactualizado, así que la mejora no se pierde con la próxima dependencia.

---

## 6. Triage de los code smells de SonarCloud

205 code smells abiertos al 22/10/2026, con Maintainability en A. No se busca llevarlos a cero: se revisaron por regla
para separar los que podían esconder un defecto de los que son estilo o decisiones justificadas.

| Grupo | Cantidad | Dónde | Evaluación |
|---|---|---|---|
| `S7780`: usar `String.raw` para no escapar `\` | 46 | Plantillas LaTeX del modo paso a paso (frontend) | Estilo. Sin efecto en el resultado |
| `S5778`, `S9073`, `S5958`, `S3415`: forma de los tests | 40 | `backend/tests/` | Estilo de tests. No afecta lo que verifican |
| `S3776`: complejidad cognitiva | 15 | 9 en distribuciones de `core/`, 4 en el backend, 2 en el frontend | **Aceptado** en `core/`: una rama por método y por guard de la tesis (§2.2). En `stream_analysis` y `pdf.py`, deuda conocida (§7) |
| `S117`: nombres de variables locales (`A_ml`, …) | 13 | `core/` | **Aceptado**: reproducen la notación de las ecuaciones de la tesis, que es la trazabilidad que pide `formulas-etapa{1,2}.md` |
| `S8415`: documentar las `HTTPException` en OpenAPI | 13 | `api/v1/` | Mejora de documentación de la API, sin efecto en el comportamiento. Candidata para CU-03, cuando la API tenga consumidores externos |
| `S125`: "código comentado" | 6 | `core/` | **Falso positivo** en los seis: son comentarios con la referencia a la ecuación al final del renglón (`# IV-248, r=2`, `# Ec. IV-8, ddof=1`, `# i = 1..n`), no código |
| `S1481`: variables sin usar | 3 | `gen_pareto.py:286` | **Revisado, sin defecto**: el renglón desempaqueta los siete promedios de IV-156 a IV-162; σ̂ (IV-154) usa cuatro y los otros tres se usan en la resolución de ε (IV-153) |
| `S7781`: `replace` en vez de `replaceAll` | 2 | `explicaciones.ts` | **Revisado, sin defecto**: el número formateado tiene una sola coma decimal |
| `S6847`, `S6845`: eventos y `tabIndex` en un elemento no interactivo | 2 | `ConfigPage.tsx` | **Falso positivo**: es un separador redimensionable con `role="separator"`, el patrón de ARIA para un panel ajustable |
| `S6825`: `aria-hidden` en un elemento enfocable | 3 | Fondos animados | **Falso positivo**: son `canvas` decorativos sin foco |
| Resto (ternarios anidados, `!important`, `async` sin `await`, parámetros sin usar, etc.) | 62 | Frontend y backend | Prolijidad, sin efecto en el comportamiento |

**Interpretación.** Ningún code smell resultó ser un defecto. Los grupos grandes son estilo o decisiones con
justificación escrita (la notación de la tesis, la estructura de los métodos de estimación). Refactorizar el motor
para bajar la complejidad cognitiva a días de la entrega habría tocado el código que validó la auditoría contra la
tesis por una mejora que el rating A ya no refleja.

---

## 7. Acciones que salen de estas métricas

| Métrica | Acción | Cuándo |
|---|---|---|
| `stream_analysis` con CC 41, en subida | Extraer una función por fase del stream | Al próximo cambio del stream, antes de CU-03 |
| `pdf.py` con índice de mantenibilidad 0 | Partir en un módulo por sección del informe | Al próximo cambio del informe |
| `api/v1/history.py` en 75 % | Tests HTTP de las respuestas 400 y 404 de las exclusiones guardadas | Próximo PR que toque el historial |
| El gate de código nuevo mide el PR completo, no por archivo | Evaluar un piso por archivo en `diff-cover` o en Sonar | Versión 2 |
| Falsos positivos de §6 | Marcarlos en SonarCloud, con la justificación de esta tabla | Con el permiso de administrar issues del proyecto |
| Horas por bloque no registradas | Registrarlas desde el próximo plan | Versión 2 |
