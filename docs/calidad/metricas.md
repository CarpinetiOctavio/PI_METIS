# Métricas de calidad — METIS

TP integrador de Calidad de Software, bloque B11. Métricas de producto, de proceso y de proyecto, cada una con su
interpretación, y la mejora medida antes y después.

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0 | 09/10/2026 | Primera versión. Valores de `staging` en `4903761` (PR #128) |

## 1. De dónde salen los números

| Fuente | Qué mide | Cómo se reproduce |
|---|---|---|
| `reporte-calidad/metricas.json` (job `quality-gate`) | Tests, cobertura de sentencia y decisión, duplicación (jscpd) y, desde este bloque, complejidad del backend (radon) | Se genera en cada corrida de CI; en local, `scripts/test.sh backend|frontend|duplicacion|complejidad` |
| `scripts/metricas_proceso.py` | Tasa de fallo del CI, lead time de PR, defectos por fase y severidad, medidas de SonarCloud | `python scripts/metricas_proceso.py` (necesita `gh` autenticado) |
| SonarCloud, rama `staging` | Complejidad cognitiva, smells, deuda técnica, ratings | API pública: `sonarcloud.io/api/measures/component?component=CarpinetiOctavio_PI_METIS&branch=staging` |

Regla del plan: los números del informe salen del pipeline o de estos scripts, no de corridas sueltas.

---

## 2. Métricas de producto

### 2.1 Tamaño

| Medida | Valor | Fuente |
|---|---|---|
| Líneas de código del backend (`metis/`, sin comentarios ni blancos) | 6.376 (9.474 en total; 2.039 de comentarios y docstrings) | radon |
| Líneas de código del repo, sin comentarios | 31.791: TypeScript 15.226, Python 13.828, CSS 1.901, otros 836 | SonarCloud (incluye los tests) |

**Interpretación.** El backend de producción es chico (6.400 líneas) frente a lo que lo prueba: Sonar cuenta 13.800
líneas de Python, así que más de la mitad son tests. Uno de cada cinco renglones del backend es comentario o
docstring, en buena parte la referencia a la ecuación de la tesis que exige la regla de "ninguna fórmula sin
referencia".

### 2.2 Complejidad

| Medida | Valor | Fuente |
|---|---|---|
| Complejidad ciclomática promedio | **5,41** por función (199 funciones) | radon |
| Distribución por rango | A (1–5): 146 · B (6–10): 23 · C (11–20): 23 · D (21–30): 4 · E (31–40): 3 | radon |
| Funciones con CC > 10 | 30 (15 %) | radon |
| Complejidad cognitiva total | 2.282 | SonarCloud |

Las más complejas:

| Función | CC | Por qué |
|---|---|---|
| `reportes/pdf.py::_seccion_simulacion` | 38 | Arma la página de comparación con y sin los puntos excluidos, con un caso por cada combinación de Etapa 1/2 presente o ausente |
| `services/analysis_service.py::stream_analysis` | 35 | Orquesta el stream completo: parseo, Etapa 1, las dos pausas, Etapa 2, persistencia, y un evento de error por cada salida posible |
| `core/etapa2/distributions/gen_pareto.py::ajustar` | 31 | Cuatro métodos de estimación con sus guards de dominio |
| `core/etapa2/distributions/gve.py::ajustar` | 28 | Ídem, tres métodos con iteración y guards |
| `core/pipeline/pipeline_etapa2.py::ejecutar_etapa2` | 26 | Las 13 distribuciones con sus estados especiales (ceros, negativos, pendiente de validación) |

**Interpretación.** El promedio está en el rango "simple" (A, ≤ 5) y tres de cada cuatro funciones también. La
complejidad se concentra donde el dominio la impone: los ajustes de distribuciones tienen una rama por método y por
guard de la tesis, y partirlas separaría lógica que se lee contra una misma sección del capítulo IV. Los dos casos
que **no** son de dominio son `_seccion_simulacion` y `stream_analysis`: son candidatos a refactor (extraer una
función por bloque de la página y una por fase del stream). No se refactorizan en este TP: están cubiertos por
tests (incluidos los E2E) y no tienen defectos registrados, así que el riesgo de tocarlos hoy es mayor que el
beneficio. Quedan como deuda conocida.

### 2.3 Mantenibilidad

| Medida | Valor | Fuente |
|---|---|---|
| Índice de mantenibilidad por archivo | 72 de 73 archivos en rango A (> 19); 1 en rango C | radon |
| Archivo con menor índice | `reportes/pdf.py`: **0,0** (rango C) | radon |
| Deuda técnica | 1.605 min (~27 h); ratio 0,2 %; rating **A** | SonarCloud |
| Code smells | 219 | SonarCloud |

**Interpretación.** El índice de mantenibilidad combina volumen de Halstead, complejidad y líneas; con 1.350 líneas,
muchas funciones de armado de tablas y pocos comentarios, `pdf.py` cae a 0 (radon recorta en cero). Es el único
archivo fuera de rango A y coincide con la función más compleja (2.2): la señal es consistente. Es código de
presentación (DECISIÓN 075) sin lógica estadística, y su riesgo está acotado por `test_pdf.py` (22 tests) y
el E2E-3, que descarga el PDF; la acción razonable es partirlo en un módulo por sección del informe cuando haya que
modificarlo. La deuda total de Sonar (0,2 % del costo de desarrollo estimado) es baja: el rating A dice que el
código, en conjunto, es barato de mantener.

### 2.4 Duplicación

| Medida | Valor | Fuente |
|---|---|---|
| Líneas duplicadas (`backend/metis` + `frontend/src`) | **0,63 %** (139 de 22.156; 10 clones) | jscpd, gate ≤ 5 % |
| Líneas duplicadas (todo el repo) | 1,5 % (680) | SonarCloud |

**Interpretación.** Las dos herramientas miden cosas distintas: jscpd solo el código de producción con un mínimo de
tokens por clon; Sonar incluye tests, configuración y estilos. Las dos están muy por debajo del 5 % del Nivel 3. La
duplicación conocida que importa (los estimadores muestrales repetidos en `etapa2/`, DECISIÓN 022) es de unas pocas
líneas por archivo y por eso jscpd no la detecta como clon: queda como deuda escrita, no medida.

### 2.5 Cobertura

| | Sentencias | Decisión (ramas) | Fuente |
|---|---|---|---|
| Backend | **94,7 %** (3.137 / 3.314) | **84,1 %** (777 / 924) | `metricas.json`, `staging` en `d8d80dc` |
| Frontend | **97,8 %** (5.953 / 6.084) | **87,7 %** (1.470 / 1.676) | ídem |
| Código nuevo de cada PR | ≥ 80 % (gate) | — | `diff-cover`, job `quality-gate` |

**Interpretación.** Las cuatro cifras superan el 80 % del Nivel 3. La de decisión es siempre la más baja, como se
espera: cada guard de dominio de las distribuciones (por ejemplo, `logpearson3.py`, con 68 % de ramas) agrega ramas
que solo se ejercitan con series construidas a propósito para caer en ese caso. La cobertura dice qué código se
ejecutó, no si el resultado es correcto: la exactitud la mide el oráculo (`objetivos-de-calidad.md`, OC-U1).

### 2.6 Confiabilidad y seguridad según SonarCloud

| Medida | Valor |
|---|---|
| Quality gate de Sonar (código nuevo) | **OK** |
| Reliability rating (código total) | **D**: 1 bug crítico |
| Security rating (código total) | **D**: 7 vulnerabilidades (1 crítica, 5 mayores, 1 menor) |
| Security hotspots | 0 |

Detalle de los 8 hallazgos y su evaluación:

| Hallazgo | Dónde | Evaluación |
|---|---|---|
| BUG crítico `S3518`, división por cero | `core/etapa1/independence.py:132` | **Falso positivo.** El guard de la línea 122 devuelve antes si `n1 == 0` o `n2 == 0`, así que `n1 + n2 ≥ 2` en la división. Sonar no infiere la restricción a través del `return` temprano |
| `S6470` (crítica), copia recursiva al contenedor | `backend/Dockerfile:8` (`COPY . .`) | **Real, de bajo impacto.** No hay `.dockerignore`: la imagen copia `backend/` entero, incluidos `__pycache__` y reportes de cobertura. El `.env` vive en la raíz y no entra en el contexto de `backend/`. Corrección: sumar un `.dockerignore` |
| `S6471` (menor), la imagen corre como root | `backend/Dockerfile:1` | **Real.** Corrección: un usuario sin privilegios en el Dockerfile. Pendiente para el despliegue en la UCC |
| `S8541` / `S8544` (mayores), `pip install` sin `--only-binary` ni hashes | `ci.yml:23`, `ci.yml:74`, `Dockerfile:6` | **Real, aceptado por ahora.** Las versiones están fijadas con `==` en `requirements.txt`, pero sin hashes; un lockfile con hashes (`pip-compile --generate-hashes`) cerraría los tres |

**Interpretación.** Los ratings D vienen de **código total**, no de código nuevo: el gate de Sonar, que mira solo lo
que cambia cada PR, está en OK. Ninguno de los 8 está en el motor estadístico ni en la lógica de negocio: uno es un
falso positivo y siete son de endurecimiento del contenedor y de la cadena de dependencias. Para que el rating refleje
la realidad, el falso positivo tiene que marcarse como tal en SonarCloud, y eso requiere permisos de administración
del proyecto (pendiente, junto con B13). Los siete restantes quedan como riesgo de seguridad de exposición baja
mientras METIS corra en la intranet; deben resolverse antes del despliegue en la UCC.

---

## 3. Métricas de proceso

### 3.1 Tasa de fallo del CI

| Período | Corridas | Exitosas | Fallidas | Tasa de fallo |
|---|---|---|---|---|
| Total (05/05 al 09/10/2026) | 248 | 240 | 8 | **3,2 %** |
| Antes del gate (< 08/10) | 215 | 209 | 6 | 2,8 % |
| Desde el gate (B1a, #111) | 33 | 31 | 2 | 6,1 % |

Las 8 corridas fallidas, clasificadas por causa:

| Fecha | Rama | Qué falló | Causa | ¿Problema real? |
|---|---|---|---|---|
| 06/05 | `feature/github-actions` | ruff format y pytest | Puesta en marcha del pipeline (los logs ya vencieron) | Configuración |
| 20/07 (×2) | `feature/core-etapa2` | ruff format; `test_gen_pareto_mc_q100_serie_facundo`: **384,80 contra 90,63** de la tesis | Error real en Generalizada de Pareto por mínimos cuadrados: el barrido se quedaba con una raíz espuria cerca de ε ≈ 0. El test quedó en `skip` con la causa documentada (`0869cc7`, DECISIÓN 010) porque la fórmula no se podía verificar todavía; DECISIÓN 068 la corrigió el 04/09 y reactivó el test (`a6c16b4`) | **Sí: defecto del producto** |
| 01/08 | `feature/frontend-pasada4` | pytest: `KeyError: 'JWT_SECRET_KEY'` | Variable de entorno faltante en el job | Configuración |
| 05/08 | `fix/cramer-particion-400` | 2 tests de `test_stream_cramer_particion.py` (`DID NOT RAISE HTTPException`) | El test del defecto (D-06) en rojo antes del fix | **Sí: el test detectó el defecto que el PR corregía** |
| 06/08 | `feat/spotlight-cards` | ESLint | Estilo | Estilo |
| 09/10 | `feature/tp-calidad-b5-b6` | El workflow no arrancó (0 jobs) | YAML inválido (`:all: ` sin comillas) | Configuración |
| 09/10 | `feature/tp-calidad-b7` | Stress k6: `permission denied` al escribir el CSV | Permisos del contenedor de k6 | Configuración |

**Interpretación.** Una tasa de fallo de 3,2 % con ninguna falla intermitente conocida (todas tienen una causa
determinista) muestra un pipeline estable. Tres de las ocho corridas detectaron un problema real del producto (dos defectos distintos); cuatro fueron de
configuración del pipeline y una de estilo. El error de Gen. Pareto MC es el ejemplo de "una
ejecución fallida del pipeline que detectó un problema real" que pide la consigna, con un matiz que vale contar: el
test se puso en `skip` para destrabar el merge, pero con la causa escrita y una decisión abierta, y volvió a correr
cuando la fórmula se corrigió. Un `skip` sin esa trazabilidad habría escondido el defecto. La suba desde el gate (6,1 %) no es un deterioro: las dos fallas son de puesta en marcha de los jobs
nuevos (despliegue y carga) y se corrigieron en el mismo PR. Ninguna llegó a `staging`.

### 3.2 Lead time de PR hacia `staging`

115 PR mergeados.

| Desde | Mediana | Promedio | p90 | < 24 h |
|---|---|---|---|---|
| La apertura del PR | 0,1 h | 1,3 h | 1,2 h | 100 % |
| El primer commit de la rama | 0,2 h | 21,2 h | 12,7 h | 94,8 % |

**Interpretación.** Los PR se abren con el trabajo ya terminado y se mergean apenas el CI da verde: el PR funciona
como compuerta de integración, no como cola de revisión. La medida desde el primer commit agrega poco porque la
mayoría de las ramas se commitean al final de la sesión de trabajo, así que tampoco mide el tiempo de desarrollo:
mide el tamaño de los lotes. Las colas largas (promedio de 21 h contra mediana de 0,2 h) son ramas grandes de varias
sesiones, como `feature/core-etapa2`. Lo que esta métrica sí permite afirmar es que nada queda esperando integración:
el riesgo de ramas largas que divergen de `staging` es bajo. Lo que no muestra, y el informe lo tiene que decir, es
revisión entre pares: con un solo autor en el TP (D6 del plan), la revisión la hacen el pipeline y SonarCloud.

### 3.3 Defectos por fase de detección y severidad

| Fase | Defectos | | Severidad | Defectos |
|---|---|---|---|---|
| Auditoría | 2 | | Crítica | 5 |
| Desarrollo | 1 | | Alta | 2 |
| Revisión | 4 | | Media | 2 |
| CI | 0 | | Baja | 1 |
| Uso real | 3 | | | |

10 defectos, ninguno abierto (`registro-defectos.md`).

**Interpretación.** El 70 % se encontró antes de llegar a un usuario (auditoría, desarrollo, revisión), y **los 5
críticos están todos en ese grupo**: los que llegaron al uso real (D-01, D-02, D-07) son de la interfaz, visibles y
con alternativa. La fase CI aparece en 0 porque el registro histórico clasificó cada defecto por la actividad que lo
encontró primero; las dos fallas reales del CI de §3.1 son de defectos que ya estaban siendo corregidos o que no se
registraron como issue (Gen. Pareto MC es anterior al registro de B10). La revisión dirigida del código es la fase
más productiva (4): coincide con que los defectos más graves eran de lógica entre módulos (índices y timestamps),
que un test unitario de una sola función no ve.

---

## 4. Métrica de proyecto: avance del plan contra el cronograma

| Bloque | Horas estimadas | Semana prevista | Mergeado (hora de Argentina) | PR |
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
| B11 Métricas | 4 | 3 | Este PR | — |
| B13 Sonar por CI y checks requeridos | (parte de B1) | Cierre (24–26/10) | Pendiente: requiere admin del repo | — |
| B12 Informe y demo | 6 | Cierre | Pendiente | — |

**Interpretación.** 12 de 14 bloques terminados en dos días de un cronograma de 18: el plan está adelantado unas dos
semanas. Las horas reales no se registraron, así que el esfuerzo por bloque no se puede comparar contra la
estimación; es una limitación de esta métrica. El trabajo se hizo con asistencia de un agente de IA (Claude Code),
lo que explica la velocidad y es un dato que el informe tiene que declarar. El camino crítico ya no es el trabajo
propio sino una dependencia externa: B13 necesita permisos de administración del repo, que tiene Octavio.

---

## 5. Mejora medida antes y después: B2

Línea de base del 08/10/2026 (`plan-tp-calidad-software.md` §1, medida antes de B1) contra la última corrida de
`staging` (`d8d80dc`, 09/10/2026):

| Medida | Antes | Después | Cambio |
|---|---|---|---|
| Cobertura de decisión del backend | 76,7 % (704 / 918) | **84,1 %** (777 / 924) | +7,4 puntos; cruza el 80 % del Nivel 3 |
| Cobertura de sentencias del backend | 91,4 % (3.016 / 3.301) | 94,7 % (3.137 / 3.314) | +3,3 puntos |
| `auth/dependencies.py` (sentencias) | 27 % | **100 %** | +73 |
| `auth/jwt.py` | 50 % | **100 %** | +50 |
| `auth/router.py` | 60 % | **100 %** | +40 |
| `core/etapa2/distributions/logpearson3.py` | 76 % | 87,2 % | +11,2 |
| `core/etapa2/distributions/gamma2p.py` | 78 % | 89,2 % | +11,2 |
| `api/v1/history.py` | 82 % | 89,3 % | +7,3 |
| Tests del backend | 500 | 685 | +185 (B2, B3, B4, B8 y el fix de D-10) |

**Interpretación.** La mejora se eligió por riesgo, no por el número: `auth/` era el código con menos cobertura y el
que, si falla, deja a los docentes sin acceso a su historial. Con la autenticación al 100 %, el riesgo residual de
seguridad de la aplicación pasa a estar en la configuración del despliegue (§2.6), no en el código. La cobertura de
decisión del backend era la única cifra del Nivel 3 que no se cumplía al empezar el TP; desde B2 se cumple y el gate
impide que el código nuevo la baje.

**Antecedente.** Antes del TP, el PR #104 (02/10/2026) llevó de C a A el Reliability rating del código nuevo de
`staging`, que es la condición que mira el quality gate de Sonar, corrigiendo 9 comparaciones de igualdad de punto
flotante y un guard de división. Los hallazgos de §2.6 son de código total: Sonar los fecha en mayo de 2026, cuando
se escribieron esas líneas, así que no los introdujo ningún cambio reciente.

---

## 6. Acciones que salen de estas métricas

| Métrica | Acción | Cuándo |
|---|---|---|
| Reliability D por un falso positivo | Marcarlo como falso positivo en SonarCloud | Con el acceso de admin (B13) |
| Security D (contenedor y dependencias) | `.dockerignore`, usuario sin privilegios en el Dockerfile, requirements con hashes | Antes del despliegue en la UCC |
| `pdf.py` con índice de mantenibilidad 0 y la función más compleja | Partir en un módulo por sección del informe | Al próximo cambio del informe |
| `stream_analysis` con CC 35 | Extraer una función por fase del stream | Al próximo cambio del stream |
| Horas por bloque no registradas | Anotarlas en B12 y B13 para tener al menos un punto de comparación | Ahora |
