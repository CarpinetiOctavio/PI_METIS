# docs/ — Documentación del Proyecto Integrador METIS

Esta carpeta contiene la documentación de trazabilidad y auditoría del
proyecto — separada de `.claude/rules/`, que es documentación operativa
para Claude Code (cómo construir y operar el sistema). Acá vive el
registro de qué se decidió, qué se verificó, y por qué el sistema es
como es — pensado para ser legible por cualquiera que abra el repo,
no solo por una sesión de IA.

## Estructura

### `auditoria/`
Auditoría de fidelidad estadística del motor de METIS contra la tesis de
maestría de Facundo Ganancias Martínez (fuente bibliográfica única para
toda fórmula implementada). Incluye:
- `fases/` — las cuatro fases formales de auditoría (fidelidad a la
  tesis, cableado/integración, testing, regresión E2E).
- `regresion/` — verificación numérica contra el Excel de referencia de
  Facundo, en tres capas complementarias que no se reemplazan entre sí:
  `regresion-unitaria/` (fidelidad de fórmula aislada por estación),
  `regresion-pipeline/` (el orquestador real reproduce los valores
  correctos end-to-end) y `regresion-e2e-coreEstadistico/`
  (consolidación de sistema completo — ranking y selección de modelo).
  Las tres se mantienen activas como herramienta de verificación
  continua, no como historial de versiones superadas.
- `pendientes/` — ambigüedades de fórmula o de dominio aún sin resolver,
  pendientes de escalar a Facundo o Carlos Catalini.

### `decisiones/`
Un archivo por decisión (`decision001.md` a `decision042.md`, número
inmutable — citado en código de producción y en toda la documentación),
más `README.md` como índice. No es un ADR estándar en sentido estricto:
mezcla decisiones de arquitectura de software con hallazgos de fidelidad
estadística. Es transversal a todo el proyecto (auth, base de datos,
testing, gobernanza de ramas, etc.) — no es específico de auditoría
estadística, por eso no vive dentro de `auditoria/`.

### `historico/`
Documentos que quedaron superados por trabajo posterior. Nunca se
borran — se mueven acá con una nota en `historico/README.md` explicando
qué eran, cuándo se superaron, y qué los reemplaza. Mismo criterio de
trazabilidad que rige el resto del proyecto: preservar el camino
recorrido, no solo el estado final.

### `frontend/`
Documentación de la implementación real del frontend — no encaja en
`auditoria/` (no es fidelidad estadística) ni en `decisiones/` como archivo
único (son documentos vivos que se actualizan fase a fase, no una decisión
cerrada de una vez):
- `frontend-implementation-plan.md` — plan de integración del frontend,
  fuente de verdad decisión por decisión (§10).
- `frontend-integration.md` — contrato real backend↔frontend observado
  (shapes de eventos SSE, discrepancias con `api-contracts.md`).
- `informe-implementacion-frontend-fase1-6.md` — informe consolidado de
  Fases 1-6, punto único de retoma.
- `plan-mejora-frontend-pasada2.md` — plan de la segunda pasada de revisión
  sobre ese trabajo (29/07/2026).

Contenido nuevo que no encaje claramente en `auditoria/`, `decisiones/`,
`historico/` o `frontend/` se discute antes de crear una carpeta nueva o
forzarlo en la que más se le parezca.

## Trazabilidad de requerimientos (`RF-XXX`)

Los identificadores `RF-XXX` citados en código, tests y documentación de
este repositorio refieren a **METIS — Manual de Requerimientos v2.0**
(Octavio Carpineti, Kevin Massholder), documento de especificación
formal del Proyecto Integrador, gestionado por fuera de este
repositorio de código.

Toda cita `RF-XXX` en este repo corresponde a esa versión del manual.
Si el manual se actualiza a una versión posterior, actualizar esta nota
para reflejar la versión vigente y confirmar que las citas existentes
siguen siendo válidas contra el nuevo contenido.

## Historial de esta estructura

Cada vez que se agregue o modifique un directorio o archivo directamente
bajo `docs/`, se actualiza este README con la fecha y una línea breve de
qué cambió — no se sobreescribe la descripción de arriba sin dejar
registro de cuándo se estableció o modificó.

- **17/07/2026** — Creación de este README. Estructura inicial:
  `auditoria/` (fases, regresión en tres capas, pendientes),
  `decisiones/` (decisions-log.md), `historico/` (reimplementacion-etapa2.md).
  Ancla de trazabilidad `RF-XXX` establecida.
- **18/07/2026** — `decisiones/decisions-log.md` (monolito de 29 entradas)
  separado en un archivo por decisión (`decision001.md` a `decision029.md`)
  más `decisiones/README.md` como índice. RESUELTO — GVE ML pasó a
  `DECISIÓN 029` (no tenía número). CONVENCIÓN — Usuario de prueba movida a
  `sprint.md`; PENDIENTE — Tabla IV-1 movida a `pendientes/pendientes-facundo.md`
  (ninguna de las dos era una decisión cerrada).
- **18/07/2026 (ronda posterior)** — `DECISIÓN 030` (elevar
  `CONTRACT_WRONG_ORDER` a error bloqueante, pendiente de implementar) y
  `DECISIÓN 031` (reorganización de repo post-cierre de Core Etapa 2, con
  árboles de archivos real antes/después) agregadas a `decisiones/`.
  Total actual: `decision001.md` a `decision031.md`.
- **19-20/07/2026** — Cierre de Auth Parte 2 (envío real de mail via
  `aiosmtplib`, primero contra Gmail y luego contra el relay SMTP real de
  la UCC). `DECISIÓN 032` (orden mail-antes-que-commit en `register`),
  `DECISIÓN 033` (bump de FastAPI/Starlette diferido) y `DECISIÓN 034`
  (dos bugs de configuración SMTP encontrados en el smoke test real:
  hostname vs. certificado, y `SMTP_USER` usado indebidamente como
  remitente) agregadas a `decisiones/`. Total actual: `decision001.md` a
  `decision034.md`. `historico/` sumó `oauth-descartado.md` a su propio
  README — no estaba listado ahí pese a existir en el directorio.
  Auditoría de referencias obsoletas a Google OAuth (mecanismo
  descartado por `DECISIÓN 001`): corregidas en `CLAUDE.md`, `sprint.md`,
  `decision001.md` (sección "Estado actual del código", que describía
  OAuth como vigente), `decision002.md` y `decision028.md`.
- **29/07/2026** — `informe-implementacion-frontend-fase1-6.md` agregado:
  informe consolidado de la implementación de Fases 1 a 5 del frontend
  (Auth, Config+Stream, Resultados, Historial, Mocks de Etapa 2) y la
  primera verificación E2E completa contra el backend real, con los 2
  bugs reales encontrados y corregidos en el proceso. Resume y enlaza a
  `frontend-implementation-plan.md` §10 (fuente de detalle decisión por
  decisión) — pensado como punto único de retoma para una persona o para
  otra sesión de Claude Code sin contexto previo.
- **29/07/2026 (pasada de mejora)** — `plan-mejora-frontend-pasada2.md`
  agregado (diagnóstico y plan de una segunda revisión sobre el trabajo de
  Fases 1-5). `frontend-implementation-plan.md` y `frontend-integration.md`
  existían desde el 22-28/07/2026 sin estar listados en este README,
  incumplimiento de la regla de abajo detectado y corregido en esta ronda.
  `decisiones/` pasó de `decision001.md`-`034.md` a `decision001.md`-`042.md`
  (036-042 de esta pasada — DECISIÓN 036/037/038 hallazgos de backend,
  DECISIÓN 039/040/041/042 promoción de las decisiones de frontend).
  `frontend/frontend-design/` (wireframes, identidad, prototipo, `versiones/`)
  commiteado por primera vez — no es parte de `docs/` pero se registra acá
  por ser el mismo evento de trazabilidad.
- **29/07/2026 (pasada de mejora, misma ronda)** — Nueva carpeta `docs/frontend/`
  creada: los cuatro archivos de arriba (`frontend-implementation-plan.md`,
  `frontend-integration.md`, `informe-implementacion-frontend-fase1-6.md`,
  `plan-mejora-frontend-pasada2.md`) movidos con `git mv` (historia
  preservada) desde la raíz de `docs/`. Decisión de Kevin, no ejecutada
  unilateralmente — ver la propuesta que motivó la pregunta en la entrada
  anterior. Todas las referencias cruzadas del repo (`CLAUDE.md`,
  `sprint.md`, `docs/decisiones/`, `frontend/src/`) actualizadas a la ruta
  nueva en el mismo cambio, incluyendo dos enlaces relativos
  (`../docs/decisiones/...` dentro del propio plan, `../plan-mejora...`
  dentro de `decisiones/README.md`) que la profundidad extra de carpeta
  hubiera dejado rotos si no se ajustaban.