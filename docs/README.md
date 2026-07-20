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
Un archivo por decisión (`decision001.md` a `decision031.md`, número
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

Contenido nuevo que no encaje claramente en `auditoria/`, `decisiones/`
o `historico/` se discute antes de crear una carpeta nueva o forzarlo
en la que más se le parezca.

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