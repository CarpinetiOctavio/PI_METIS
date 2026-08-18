# Registro de Decisiones — METIS

Un archivo por decisión (`decision001.md` a `decision063.md`). No es un
ADR estándar en sentido estricto: mezcla decisiones de arquitectura de
software (auth, base de datos, migraciones, gobernanza de ramas) con
hallazgos de fidelidad estadística del motor de METIS contra la tesis de
Facundo Ganancias Martínez. Es transversal a todo el proyecto — no vive
dentro de `auditoria/` porque no es específico de fidelidad estadística.

Cuando el código no coincida con lo que documenta una decisión vigente,
es señal de que algo se rompió o de que la decisión necesita un addendum
— no se asume que el código tiene razón por default.

## El número es inmutable

Una vez asignado, el número de una decisión no se reutiliza ni se
reordena, aunque el archivo se edite o se le agregue un addendum
posterior. Está citado en código de producción (comentarios que
referencian `docs/decisiones/decisionNNN.md`), en tests, y en toda la
documentación de auditoría — renumerar rompería esas citas sin ningún
beneficio real. El orden de este índice es numérico, no cronológico, por
el mismo motivo: nadie cita "la decisión de tal fecha", todo el repo cita
por número.

**Antes de crear `decisionNNN.md` con un número nuevo, correr `git fetch`
y comparar contra `origin/staging`** (`git ls-tree -r --name-only
origin/staging -- docs/decisiones/` para ver el máximo real del remoto).
El siguiente número libre en el checkout local no es necesariamente el
siguiente número libre en el remoto — dos ramas de trabajo pueden tomar
el mismo número en paralelo sin que ninguna de las dos lo sepa hasta el
merge. Ya pasó una vez (17/08/2026): `DECISIÓN 059` se asignó en paralelo
a "selector de intensidad de animación" (mergeado a `staging`) y a un
trabajo de auditoría de Etapa 2 sin pushear — el segundo se renumeró a
`060` antes de commitear, sin conflicto real de Git de por medio porque
se detectó a tiempo con este mismo chequeo.

## Addendums

Un addendum (corrección o ampliación de alcance posterior a la fecha
original de la decisión) vive dentro del mismo archivo que actualiza, no
en uno nuevo — no es una decisión distinta, es la misma decisión con
información más reciente. Addendums fechados existentes: `decision004.md`
(17/07/2026), `decision010.md` (10/07/2026), `decision011.md`
(18/07/2026), `decision023.md` (15/07/2026), `decision038.md` (29/07/2026,
dos addendums — pasada 2 y pasada 3, la de pasada 3 agrega la tercera
dirección del chequeo de códigos de error).

## Historial de esta migración

**29/07/2026 (reserva de números, previa a `decision036.md`-`decision042.md`)** —
[`docs/frontend/plan-mejora-frontend-pasada2.md`](../frontend/plan-mejora-frontend-pasada2.md) (Bloque B0)
reserva 035-042 en el índice antes de escribir ningún contenido, para que ningún
trabajo paralelo pise un número. `035` ya estaba comprometido desde `sprint.md`
(protección de ramas, 20/07/2026) sin archivo propio todavía — no se toca en esta
pasada. `036`-`042` se completan en el mismo trabajo que reserva los números.

**18/07/2026** — `decisions-log.md` (monolito de 29 entradas, algunas sin
número de decisión) separado en archivos individuales. Cambios de
contenido aplicados en la misma ronda:
- El bloque "RESUELTO — GVE ML" (sin número) pasó a ser `DECISIÓN 029`,
  con su fecha original (19 de mayo de 2026, fecha del fix real)
  preservada — la fecha de git (18 de junio de 2026) es cuándo se
  documentó, no cuándo ocurrió, y queda anotada dentro del archivo.
- El bloque "CONVENCIÓN — Usuario de prueba para smoke tests" (no era una
  decisión) se integró a `sprint.md`, sección "Entorno de desarrollo —
  datos de prueba".
- El bloque "PENDIENTE — Tabla IV-1" (una pregunta abierta, no una
  decisión cerrada) se movió a `docs/auditoria/pendientes/pendientes-facundo.md`.
- `DECISIÓN 011` recibió un addendum documentando que la evidencia
  posterior (Fase 4, est_07/est_09) dejó la partición `n_w1` en un
  empate real 2-2 entre `ceil` y `round` — la palabra "confirmado" del
  texto original ya no describe el estado real de la evidencia.

**18/07/2026 (ronda posterior)** — `DECISIÓN 030` agregada (elevar
`CONTRACT_WRONG_ORDER` a error bloqueante, orden cronológico en
`calcular_cramer`). Creada por fuera de esta migración; incorporada acá
tras auditoría — header corregido a `#` (H1, consistente con el resto),
y sus referencias cruzadas con `DECISIÓN 022` y con
`docs/auditoria/fases/pendientes-cableado-fase2.md` verificadas y
corregidas en ambas direcciones.

**18/07/2026 (ronda posterior)** — `DECISIÓN 031` agregada (reorganización
de repo post-cierre de Core Etapa 2, con los árboles de archivos real
antes/después). Header corregido a `#` (mismo problema que tuvo 030).
Hash de commit pendiente — placeholder `[PEGAR HASH ACÁ]` dentro del
archivo, se completa manualmente cuando el commit exista de verdad.

**19/07/2026** — `DECISIÓN 032` (Auth: orden mail-antes-que-commit en
`register`, ventana residual aceptada) y `DECISIÓN 033` (bump de
FastAPI/Starlette diferido, con criterios explícitos de habilitación)
agregadas — cierre de Auth Parte 2. `DECISIÓN 004` actualizada con el
estado final de implementación; su índice y el de `DECISIÓN 001` abajo
corregidos para dejar de decir "pendiente de credenciales IT" (recibidas
10/06/2026, implementación cerrada 19/07/2026) — `DECISIÓN 001` sigue con
contenido más profundo desactualizado (referencia a `auth/google.py`,
eliminado hace varias sesiones) sin resolver en esta ronda — resuelto el
20/07/2026, ver entrada de abajo.

**20/07/2026** — `DECISIÓN 034` agregada (dos bugs de configuración SMTP
encontrados en el smoke test real contra el relay de la UCC: hostname no
coincidía con el certificado, y `SMTP_USER` se usaba indebidamente como
remitente — ambos corregidos y verificados con entrega real de punta a
punta). `DECISIÓN 032` actualizada — pasa de "pendiente de verificación
exhaustiva por test" a verificada con evidencia real. `DECISIÓN 001`
actualizada de punta a punta — header top-level, la sección "Decisión de
reemplazo" (ya no dice "pendiente de confirmación con IT") y "Qué hay
que hacer cuando IT confirme" (ahora "COMPLETADO") todas marcadas
explícitamente como resueltas/históricas, con el texto original de cada
una conservado por trazabilidad en vez de reescrito. Ya no queda como
reescritura pendiente.
Referencias a `docs/historico/oauth-descartado.md` sumadas donde faltaban
(`CLAUDE.md`, `sprint.md`, `decision002.md`, `decision028.md`,
`historico/README.md` — que no listaba ese archivo en absoluto).

**09/08/2026 (A0 del plan de implementación de Etapa 2)** —
`decision052.md`-`decision055.md` agregadas: las cuatro decisiones que el
Bloque A del [plan de implementación de Etapa 2](../plan-etapa2-implementacion.md)
exige escribir antes de tocar código (contrato SSE con pausa,
`session_store` con TTL, `etapas` de punta a punta, y por qué
`full_pipeline.py` no se usa desde `services/`). `DECISIÓN 037` marcada como
cerrada por `DECISIÓN 054` — mismo criterio que `DECISIÓN 011`/`DECISIÓN 038`
para addendums, salvo que acá el cierre completo es una decisión nueva, no
una ampliación de la original, así que se referencia en vez de editarse in
situ.

## Índice

| # | Título | Fecha | Estado |
|---|---|---|---|
| [001](decision001.md) | Autenticación CU-01 | 10/05/2026 | Resuelta — mecanismo OAuth original descartado, se conserva por trazabilidad (actualizado 20/07/2026) |
| [002](decision002.md) | Esquema tabla users y refactor de auth/ | 10/05/2026 | Implementado |
| [003](decision003.md) | Gestión de migraciones de esquema: Alembic | 14/05/2026 | Parcialmente implementado |
| [004](decision004.md) | Mecanismo de envío de mail para verificación de cuenta | 14/05/2026 | Implementado — Parte 1 y Parte 2 completas 19/07/2026 |
| [005](decision005.md) | Almacenamiento de tokens de verificación en memoria | 14/05/2026 | Aceptado para V1.0 — revisión post-M5 |
| [006](decision006.md) | Regla de nullability en migraciones Alembic + SQLAlchemy | 15/05/2026 | Establecida |
| [007](decision007.md) | DATABASE_URL dual-ambiente y convenciones de entorno de desarrollo | 15/05/2026 | Establecida |
| [008](decision008.md) | Estructura del .env y trampas silenciosas de python-dotenv | 15/05/2026 | Establecida |
| [009](decision009.md) | Convención de nombres de distribuciones en el pipeline | 17/05/2026 | Implementado |
| [010](decision010.md) | Estrategia de root-finding para métodos iterativos | 19/05/2026 | Establecida — addendum 10/07/2026 |
| [011](decision011.md) | Fórmula de Cramer: partición y grados de libertad | 16/06/2026 | Implementado — addendum de staleness 18/07/2026 |
| [012](decision012.md) | Criterio de aprobación Anderson: comparación entera vs ratio flotante | 16/06/2026 | Implementado |
| [013](decision013.md) | Fórmula de asimetría no sesgada: ddof=0 (IV-4/IV-5) en todas las distribuciones | 17/06/2026 | Implementado |
| [014](decision014.md) | GVE MV: corrección IV-202 + condiciones iniciales ML como fallback | 20/06/2026 | Implementado |
| [015](decision015.md) | Log-Normal 3p Momentos: IV-116 σ̂y vs σ̂²y | 22/06/2026 | Implementado |
| [016](decision016.md) | Anderson: k_max = ceil(n/3), no floor(n/3) | 09/07/2026 | Implementado |
| [017](decision017.md) | Wald-Wolfowitz: exclusión de empates con la media | 09/07/2026 | Implementado |
| [018](decision018.md) | Chow: K_N vía Grubbs-Beck (Bulletin 17B), no cuantil t crudo | 10/07/2026 | Implementado — provisorio, pendiente Facundo/Carlos |
| [019](decision019.md) | LP3 MV: guard simétrico de borde superior | 10/07/2026 | Implementado — no resuelve est_06 |
| [020](decision020.md) | Log-Normal 3p MV: perfil de verosimilitud sobre x0 | 10/07/2026 | Documentado |
| [021](decision021.md) | Log Pearson III MV: sustitución de Thom (IV-126) | 10/07/2026 | Documentado |
| [022](decision022.md) | Cierre de la 2da auditoría de fidelidad a la tesis (Bloque 3) | 10/07/2026 | Pendiente de implementar — refactor de cableado no iniciado |
| [023](decision023.md) | Gamma 3p MV: escaneo denso hacia el borde superior + validación de raíz | 14/07/2026 | Aplicada — addendum 15/07/2026 |
| [024](decision024.md) | exponencial_x0_beta.py: docstring de cabecera corregido (IV-72) | 14/07/2026 | Aplicada |
| [025](decision025.md) | Log-Normal 3p MV: guard de ausencia de óptimo finito | 15/07/2026 | Aplicada |
| [026](decision026.md) | Ancla de trazabilidad para requerimientos externos (RF-XXX) | 17/07/2026 | Establecida |
| [027](decision027.md) | Migración Alembic `46f270df2e87` renombrada a `003` | 17/07/2026 | Aplicada |
| [028](decision028.md) | Gobernanza de ramas: staging y main | 18/07/2026 | Establecida — pendiente de consulta a IT (registry CI/CD) |
| [029](decision029.md) | GVE ML: error de orden de serie en IV-243/244 | 19/05/2026 | Implementado |
| [030](decision030.md) | Elevar CONTRACT_WRONG_ORDER a error bloqueante (orden cronológico) | 18/07/2026 | Pendiente de implementar — contradice "único caso: n<10" hasta que se aplique |
| [031](decision031.md) | Reorganización de repo post-cierre de Core Etapa 2 | 18/07/2026 | Aplicada — pendiente de hash de commit |
| [032](decision032.md) | Auth: orden mail-antes-que-commit en `register`, ventana residual aceptada | 19/07/2026 | Implementado — pendiente de verificación exhaustiva por test |
| [033](decision033.md) | Bump de FastAPI/Starlette diferido, con criterios explícitos de habilitación | 19/07/2026 | Diferido — condicionado a dos criterios explícitos |
| [034](decision034.md) | Correcciones de configuración SMTP encontradas en smoke test real: hostname y separación de identidad de remitente | 20/07/2026 | Implementado y verificado — envío real de punta a punta confirmado |
| 035 | *(reservado — GitHub Ruleset de protección de ramas, no tocar en esta pasada)* | — | Pendiente — ver `sprint.md`, sección "Estrategia de ramas", 20/07/2026 |
| [036](decision036.md) | Partición de Cramer personalizada inalcanzable por el endpoint multipart | 29/07/2026 | Documentado — no implementado, requerimiento funcional caído |
| [037](decision037.md) | Contrato de `/analysis/stream`: `etapas` descartado y `AnalysisRequest` sin cablear | 29/07/2026 | Cerrada por [DECISIÓN 054](decision054.md) (09/08/2026) |
| [038](decision038.md) | Catálogo de códigos de error como fuente única, en ambas direcciones | 29/07/2026 | Aplicada — gap de propagación en `trend.py` documentado, no corregido |
| [039](decision039.md) | Criterio de promoción de las decisiones de frontend y unificación de numeración | 29/07/2026 | Establecida |
| [040](decision040.md) | SSE sobre fetch para el stream de Etapa 1 | 22/07/2026 | Implementado — verificado contra backend real |
| [041](decision041.md) | Estado de servidor sin TanStack Query; `vi.stubGlobal("fetch")` como patrón único de test | 22-28/07/2026 | Diferido (TanStack Query, con criterio de habilitación) — Establecido (patrón de test) |
| [042](decision042.md) | Alcance de los mocks de Etapa 2 y rol de MSW | 22-28/07/2026 | Superada 09/08/2026 — Etapa 2 dejó de ser mock (Bloque B) |
| [043](decision043.md) | Contraste WCAG AA del tema Instrumento: hallazgos y propuesta, no aplicada | 29/07/2026 | PENDIENTE DE DECISIÓN — Kevin/Octavio |
| [044](decision044.md) | SonarCloud: quality gate, limpieza del PR #17/B, rechazo de `<dialog>` nativo, merge del PR #17 en rojo | 30/07/2026 | Aplicada — gate de gobernanza PENDIENTE DE DECISIÓN — Kevin/Octavio |
| [045](decision045.md) | Fondos animados en Canvas 2D sin dependencias, WebGL descartado — addendum 05/08/2026: excepción acotada para Threads (three.js) en la puerta de entrada, vía code-splitting | 31/07/2026 | Decidida — implementación en curso |
| 046 | *(reservado — E2E con Playwright, revisa la exclusión de `constraints.md`)* | — | Pendiente — ver `docs/plan-post-pasada4-roadmap.md` §3, Bloque C1b |
| [047](decision047.md) | Endpoint `preview-columns`: parseo de cabeceras del lado del servidor, no del cliente | 31/07/2026 | Decidida — implementación en curso |
| [048](decision048.md) | Archivado de análisis por soft-delete, no borrado físico | 31/07/2026 | Decidida — implementación en curso |
| 049 | *(reservado — escotilla SMTP de desarrollo en `auth/email.py`. Corrección 05/08/2026: el plan de arreglo de UI y su informe de resultados citaban 045 para esto, pero 045 quedó asignada a "Fondos animados en Canvas 2D" antes de que la escotilla SMTP se escribiera — ver `docs/plan-post-pasada4-roadmap.md`, H1)* | — | Pendiente — ver `sprint.md`, "Pendiente de esta rama" |
| [050](decision050.md) | Límite de tamaño de subida: valor (10 MB), nginx + backend, código de error nuevo | 05/08/2026 | Decidida — implementación en curso |
| [051](decision051.md) | ThreadsBackground pasa de Three.js a Canvas 2D; Three.js sale del proyecto — supera el addendum de la excepción de DECISIÓN 045 | 06/08/2026 | Implementada |
| [052](decision052.md) | Transporte de Etapa 2 por SSE con pausa; `distribution-decision` reemplaza `design-events` | 09/08/2026 | Decidida — implementación en curso |
| [053](decision053.md) | `session_store` pasa a un estado con TTL, no dos diccionarios sueltos | 09/08/2026 | Decidida — implementación en curso |
| [054](decision054.md) | `etapas` cableado de punta a punta — cierra DECISIÓN 037 | 09/08/2026 | Decidida — implementación en curso |
| [055](decision055.md) | `full_pipeline.py` no se usa desde `services/`, y para qué queda | 09/08/2026 | Decidida — implementación en curso |
| [056](decision056.md) | Gráficos interactivos de Etapa 2: `d3-scale` + `d3-shape` con SVG propio | 11/08/2026 | Decidida — implementación en curso |
| [057](decision057.md) | Agregación temporal por año hidrológico configurable (`mes_inicio_anio`) | 12/08/2026 | Decidida — implementación en curso |
| [058](decision058.md) | Qué serie se expone, en qué versiones y por qué (serie temporal, Chow, boxplot mensual) | 12/08/2026 | Decidida — implementación en curso |
| [059](decision059.md) | Selector de intensidad de animación (alta/media/sin animaciones) | 14/08/2026 | Implementada |
| [060](decision060.md) | Guard de dominio x0/µ ≥ min(serie) en Exponencial x0-β y Generalizada de Pareto (Momentos) | 17/08/2026 | Aplicada |
| [061](decision061.md) | Default "tolerar y advertir" ante ceros en ExpX0Beta/GenPareto/GenExp — resuelve el default de implementación, no la pregunta de dominio | 17/08/2026 | Aplicada |
| [062](decision062.md) | Historial interactivo: explorar otra distribución no es decidir — el recálculo no toca `decisiones` ni `session_store` | 18/08/2026 | Decidida — implementación en curso |
| [063](decision063.md) | Panel de columnas acoplado, no ventana flotante — superposición vs. reflow, y el costo de accesibilidad de un gestor de ventanas propio | 18/08/2026 | Decidida y aplicada |
