# DECISIÓN 077: pruebas de carga y esfuerzo sostenido, cobertura y quality gate en CI, SonarCloud por CI

**Fecha:** 8 de octubre de 2026
**Estado:** Decidida — implementación en los Bloques B1 y B7 de `docs/plan-tp-calidad-software.md`. La migración de
SonarCloud y los checks requeridos quedan para el último PR del plan, porque necesitan permisos de administración
del repositorio.
**Decide:** Kevin.
**Origen:** el TP integrador de Calidad de Software (Nivel 3) exige un pipeline con cobertura, quality gate y
reportes automáticos, y pruebas de stress y de esfuerzo sostenido con umbrales. Resuelve también la "pregunta de
gobernanza abierta" (D3) de DECISIÓN 044.

### Contexto

- **Carga.** `constraints.md`, "Scope V1.0 — lo que NO entra", lista "Tests de carga o performance" desde el commit
  `6d2df20` (PR #2), sin decisión que lo justifique (mismo origen que la exclusión de E2E, ver DECISIÓN 046). METIS
  tiene dos puntos que justifican medir: Etapa 2 ajusta 13 distribuciones y es CPU intensiva, y la sesión del stream
  vive en memoria del proceso (`session_store`, DECISIÓN 053), así que una carga sostenida puede acumular memoria.
- **Cobertura.** Medida el 08/10/2026: backend 91,4 % sentencias y 76,7 % decisiones; frontend 97,5 % y 87,8 %.
  Ninguno de esos números lo produce el pipeline: `ci.yml` no mide cobertura.
- **SonarCloud** corre en Análisis Automático, que no admite importar cobertura, y su check no es requerido en el
  ruleset (DECISIÓN 044, D3): el gate es consultivo.

### Decisión

1. **Cobertura en CI.** Backend con `pytest-cov` (`--cov-branch`, XML + HTML + JUnit); frontend con
   `@vitest/coverage-v8` en la misma versión que `vitest` (lcov). Los reportes se suben como artefactos y se resumen
   en `$GITHUB_STEP_SUMMARY`. Se quita la tolerancia al exit code 5 del job `test`, en su propio commit.
2. **Gate propio, independiente de Sonar:** `diff-cover --fail-under=80` sobre el código nuevo del PR y
   `jscpd --threshold 5` para duplicación. No necesitan permisos especiales y van primero.
3. **SonarCloud por CI** (acción oficial, secret `SONAR_TOKEN`, cobertura de los dos lados importada) en lugar del
   Análisis Automático, que se desactiva en el mismo paso (son excluyentes). Gate "Sonar way" o uno propio con los
   umbrales de la consigna; Sonar way es más estricto en duplicación (3 % sobre código nuevo) y en fiabilidad
   (cualquier bug, no solo críticos).
4. **Checks requeridos.** Se adopta la opción 1 de DECISIÓN 044, D3: los jobs de CI y el gate de SonarCloud pasan a
   ser requeridos en el ruleset de `staging` y `main`.
5. **Carga y esfuerzo sostenido** contra el despliegue efímero del pipeline y el local: stress (rampa hasta el punto
   de quiebre sobre `preview-columns`, `simulate-exclusion` y `stream` con `etapas=1`) y esfuerzo sostenido (30 a 60
   min, vigilando memoria del backend y tasa de error). Umbrales fijados con la primera corrida y congelados; el job
   falla si se superan. Stress en el pipeline; el sostenido, manual o programado, no en cada PR.
6. **Herramienta de carga: k6, provisoria.** Umbrales nativos que cortan el proceso, resumen exportable, acción para
   GitHub Actions, scripts en JavaScript. Se confirma o se cambia con la prueba de concepto del proceso de 5 pasos
   del Bloque B7 (`docs/calidad/herramienta-carga.md`); si la PoC elige otra, se agrega un addendum a esta decisión.
7. **Sale de `constraints.md`** la línea "Tests de carga o performance", con referencia a esta decisión.

### Orden de implementación y permisos

Los puntos 3 y 4 necesitan administración del repositorio (cargar el secret, desactivar el Análisis Automático,
editar el ruleset), y Kevin no la tiene: el repo es de Octavio. Por eso:

- Los puntos 1, 2, 5 y 6 se implementan primero, con jobs que fallan de verdad aunque todavía no sean requeridos.
- Los puntos 3 y 4 van juntos en el **último PR** del plan, una vez que Octavio cargue `SONAR_TOKEN` y dé el
  acceso. No pueden adelantarse: con el Análisis Automático activo, el job de análisis por CI falla en todos los PR.
- Si el acceso no llega antes de la entrega, el gate del punto 2 es el que se presenta, y el informe lo explica.

### Alternativas evaluadas

- **Mantener SonarCloud en Análisis Automático y medir cobertura solo localmente.** Descartada: la consigna pide que
  el pipeline produzca los números, y el gate de Sonar sin cobertura no puede exigir el 80 % sobre código nuevo.
- **Solo Sonar, sin gate propio.** Descartada: dejaría todo el gate en manos de un acceso que no está garantizado a
  tiempo, y de un servicio externo que también puede caer (va al plan de contingencia).
- **Locust, JMeter, Artillery para carga.** Se evalúan en la PoC del Bloque B7. Locust está en Python pero no trae
  umbrales que corten el proceso; JMeter versiona mal (XML) y es pesado para un runner; Artillery tiene menos
  tracción.

### Consecuencias

- El pipeline se alarga; se mitiga con caché y corriendo lo pesado (E2E, stress) solo en PR a `staging`/`main`.
- Los umbrales de carga dependen del runner de GitHub Actions, que no es la máquina de la UCC: se presentan como
  línea de base del ambiente efímero, no como capacidad de producción.
- DECISIÓN 044 queda con D3 resuelta por esta decisión; `testing.md` y `CLAUDE.md` describen el nuevo pipeline cuando
  se implemente.

### Addendum (09/10/2026) — B7: k6 confirmado y carga en el pipeline

- **Prueba de concepto** (`docs/calidad/herramienta-carga.md`): el mismo escenario en k6 2.3.0 y Locust 2.46.6 contra
  el despliegue local. Midieron lo mismo (26,5 y 26,6 req/s); la diferencia está en los umbrales: k6 los trae nativos
  y salió con código 99 ante uno violado; Locust sale con 1 ante cualquier request fallida, pero un umbral de latencia
  o una tasa tolerada hay que programarlos. Matriz ponderada: k6 4,65, Locust 3,95. **El punto 6 deja de ser
  provisorio.**
- **Implementado:** `carga/k6/` (stress con perfiles `quiebre` y `ci`, sostenido), `carga/umbrales.json`,
  `scripts/carga.sh`, job `carga` en `ci.yml` (perfil `ci` en cada PR, umbrales bloqueantes) y workflow
  `carga-sostenida.yml` (manual y semanal). k6 corre en un contenedor dentro de la red del despliegue efímero.
- **Hallazgo:** el punto de quiebre está entre 20 y 40 usuarios concurrentes; el sistema se degrada por latencia (un
  solo proceso de uvicorn), sin errores. Registrado en `docs/pendientes-tecnicos.md`.
