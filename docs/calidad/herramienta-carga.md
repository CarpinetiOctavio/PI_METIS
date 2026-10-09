# Herramienta nueva: pruebas de carga con k6

TP integrador de Calidad de Software, bloque B7 (`docs/plan-tp-calidad-software.md`). Decisión: DECISIÓN 077, punto 6
(k6, provisoria hasta esta prueba de concepto). Proceso de adopción en cinco pasos.

## 1. Requisitos

| # | Requisito | Por qué en METIS |
|---|---|---|
| R1 | Umbrales que corten el job (latencia por endpoint y tasa de error) | La consigna pide que el pipeline falle si se superan |
| R2 | HTTP multipart y respuestas SSE | `preview-columns` y `stream` reciben un archivo; `stream` responde `text/event-stream` |
| R3 | Reporte exportable (JSON y HTML) | Evidencia como artefacto de CI y números para el informe |
| R4 | Corre en GitHub Actions | El stress corre sobre el despliegue efímero (B5) |
| R5 | Scripts versionables y legibles | Viven en el repo y se revisan en el PR |
| R6 | Costo del generador de carga | El generador comparte máquina con el sistema bajo prueba (local y runner) |
| R7 | Curva de aprendizaje | Lo mantiene una persona; el equipo ya usa Python (backend) y JavaScript (frontend) |

## 2. Mercado

| Herramienta | Lenguaje de los scripts | Umbrales | Observación |
|---|---|---|---|
| **k6** (Grafana) | JavaScript | Nativos (`thresholds`), exit code 99 | Acción oficial de GitHub Actions, dashboard HTML exportable |
| **Locust** | Python | No; hay que programarlos con hooks | Reporte HTML y CSV, UI web |
| JMeter | XML (GUI) | Con plugins o aserciones | Planes en XML, difíciles de revisar en un PR; pesado para un runner |
| Artillery | YAML + JS | Sí (`ensure`) | Menos tracción y comunidad |

JMeter y Artillery se descartaron sin prueba de concepto: JMeter por R5 y R6, Artillery por menor soporte. La prueba
se hizo con las dos candidatas que cumplían todos los requisitos sobre el papel.

## 3. Prueba de concepto

El mismo escenario en las dos herramientas, contra el despliegue local (`scripts/deploy-local.sh`), con el generador
en un contenedor dentro de la red del despliegue: 10 usuarios durante 60 s; cada iteración es el recorrido completo de
CU-02 (subir el archivo, Etapa 1 por el stream, simular la exclusión de un punto con Etapa 2) más 1 s de espera.
Scripts en `carga/poc/` (`k6-poc.js`, `locustfile.py`). Corrida del 09/10/2026, k6 2.3.0 y Locust 2.46.6.

| Medida | k6 | Locust |
|---|---|---|
| Requests | 1.620 | 1.586 |
| Throughput | 26,5 req/s | 26,6 req/s |
| Tasa de error | 0 % | 0 % |
| p95 global | 103 ms | 120 ms |
| CPU / memoria del generador | 5,4 % / 20 MiB | 5,2 % / 40 MiB |
| Líneas del escenario | 18 (+ 75 del módulo `metis.js`, reutilizado después) | 63 |
| SSE (`stream` hasta `complete`) | Lee la respuesta entera; `check` sobre el cuerpo | Igual, con `catch_response` |
| Umbral de latencia que corta el job | Nativo: con `p(95)<1` salió con **código 99** | No existe: hay que programarlo en un hook |
| Umbral de tasa de error | Nativo (`rate<0.01`) | Sale con código 1 ante **cualquier** request fallida; una tolerancia hay que programarla |
| Detalle por endpoint | Con tags + umbrales por submétrica | De serie |
| Reporte | `--summary-export` (JSON) + dashboard HTML (`K6_WEB_DASHBOARD_EXPORT`) | `--html` + `--csv` |

Las dos midieron lo mismo (26,5 contra 26,6 req/s): la diferencia de p95 está dentro de la variación entre corridas.
La diferencia que importa es R1, verificada a propósito con un umbral imposible y con un endpoint inexistente.

## 4. Matriz de decisión ponderada

Puntaje de 1 a 5 a partir de la prueba de concepto.

| Requisito | Peso | k6 | Locust |
|---|---|---|---|
| R1 Umbrales que cortan el job | 25 % | 5 | 3 |
| R2 Multipart y SSE | 15 % | 4 | 4 |
| R3 Reporte exportable | 15 % | 5 | 4 |
| R4 GitHub Actions | 15 % | 5 | 4 |
| R5 Scripts versionables | 10 % | 4 | 5 |
| R6 Costo del generador | 10 % | 5 | 4 |
| R7 Curva de aprendizaje | 10 % | 4 | 5 |
| **Total ponderado** | | **4,65** | **3,95** |

**Resultado: se confirma k6** (DECISIÓN 077, punto 6, deja de ser provisoria). Locust gana en R5 y R7 por estar en
Python como el backend, pero el requisito que define la elección es R1: con k6 un umbral es una línea de
configuración y el código de salida lo maneja la herramienta; con Locust es código propio que hay que probar y
mantener.

## 5. Despliegue incremental

| Etapa | Qué | Dónde |
|---|---|---|
| 1. Script local | `scripts/carga.sh quiebre\|ci\|sostenido` contra `scripts/deploy-local.sh` | Máquina local |
| 2. Job manual | Workflow `carga-sostenida.yml` con `workflow_dispatch` (duración como input) | GitHub Actions |
| 3. Job programado | El mismo workflow, semanal (domingo 06:00 UTC) sobre la rama por defecto | GitHub Actions |
| 4. Umbrales bloqueantes | Job `carga` de `ci.yml`: perfil `ci` en cada PR; falla si se supera un umbral | GitHub Actions |

## 6. Escenarios, resultados y umbrales

Los tres comparten el recorrido de CU-02 de la prueba de concepto (`carga/k6/metis.js`) y sus requests van con el tag
`endpoint`, así latencias y umbrales se leen por endpoint. Umbrales en `carga/umbrales.json`.

### Stress hasta el quiebre (`scripts/carga.sh quiebre`)

Rampa de 10 a 120 usuarios, un minuto por escalón (09/10/2026, despliegue local, Docker Desktop con 8 GB):

| Minuto | Usuarios | Req | Error | p95 preview-columns | p95 simulate-exclusion | p95 stream |
|---|---|---|---|---|---|---|
| 1 | 9 | 751 | 0 % | 27 ms | 93 ms | 51 ms |
| 2 | 19 | 2.368 | 0 % | 41 ms | 160 ms | 79 ms |
| 3 | 39 | 2.758 | 0 % | 540 ms | 777 ms | 597 ms |
| 4 | 59 | 2.536 | 0 % | 1.521 ms | 2.139 ms | 1.240 ms |
| 5 | 79 | 2.607 | 0 % | 1.699 ms | 2.154 ms | 2.052 ms |
| 6 | 119 | 2.695 | 0 % | 2.290 ms | 2.704 ms | 2.722 ms |

**Lectura.** El throughput se estanca en unos 2.600 requests por minuto (≈ 45 req/s) a partir de los 20 usuarios: es
la capacidad de un solo proceso de uvicorn (el `CMD` del Dockerfile no levanta workers). Desde ahí, cada usuario
más solo agrega espera en la cola: el p95 pasa de decenas de milisegundos a más de 2 s entre 20 y 60 usuarios. **No
aparecen errores ni con 120 usuarios**: el sistema se degrada por latencia, no por fallas. El punto de quiebre, con
el criterio de p95 < 500 ms en el endpoint más pesado, está entre 20 y 40 usuarios concurrentes con este recorrido.

Mejora posible, fuera del alcance del TP: levantar varios workers de uvicorn (`--workers N`) en el despliegue de
producción. Las sesiones del stream viven en memoria del proceso (DECISIÓN 053), así que antes habría que moverlas a
un almacenamiento compartido o fijar la sesión a un worker.

### Stress de CI (`scripts/carga.sh ci`, job `carga`)

15 usuarios (por debajo del codo) durante 2 min, más 30 s de rampa. Línea de base local:

| Endpoint | p95 medido | Umbral congelado |
|---|---|---|
| preview-columns | 43 ms | 150 ms |
| stream (Etapa 1) | 72 ms | 250 ms |
| simulate-exclusion (Etapa 2) | 147 ms | 500 ms |
| Tasa de error | 0 % | < 1 % |

Los umbrales son unas tres veces la línea de base: el runner de GitHub Actions no es esta máquina y la carga corre
en el mismo runner que el sistema. Se presentan como línea de base del ambiente efímero, no como capacidad de
producción (DECISIÓN 077, consecuencias).

### Esfuerzo sostenido (`scripts/carga.sh sostenido`)

5 usuarios constantes durante 30 minutos (09/10/2026, despliegue local), con los mismos umbrales de latencia y error
del stress de CI, y la memoria del backend muestreada cada 15 s con `docker stats`:

| Medida | Resultado | Umbral |
|---|---|---|
| Requests | 24.393 (13,6 req/s) | — |
| Tasa de error / checks | 0 % / 100 % (40.655 checks) | < 1 % |
| p95 preview-columns | 30 ms | 150 ms |
| p95 stream | 57 ms | 250 ms |
| p95 simulate-exclusion | 118 ms | 500 ms |
| Memoria del backend | 181,6 a 183,9 MiB en 106 muestras | — |
| Pendiente de memoria (después de 5 min) | **+0,3 MB/h** | 50 MB/h |

**Lectura.** Sin crecimiento sostenido de memoria: el `session_store` (sesiones del stream en memoria, DECISIÓN 053)
no acumula con streams que terminan en `complete`. Lo que esta corrida no cubre son los streams abandonados en una
pausa (Chow o elección de distribución): k6 lee la respuesta entera y no puede cortar a mitad de stream. Esas sesiones
dependen del TTL de `session_store`, y quedan fuera de este escenario.

## 7. Primera corrida en el pipeline

El job `carga` del PR #126 (runner `ubuntu-latest`) midió, con los mismos 15 usuarios: p95 de 5 ms en
`preview-columns`, 7 ms en `stream` y 45 ms en `simulate-exclusion`, con 0 % de error y 36,9 req/s. El runner resultó
entre 3 y 10 veces más rápido que el Docker Desktop local, así que en CI los umbrales tienen mucho margen: detectan
degradaciones grandes (de un orden de magnitud), no regresiones finas.

Los umbrales congelados no se cambiaron con esta corrida: siguen sirviendo para la máquina local (donde se corre la
demo) y para el pipeline. Si se quiere un gate más sensible en CI, la alternativa es separar umbrales por ambiente
en `carga/umbrales.json`.
