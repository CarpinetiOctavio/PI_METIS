# Registro de Decisiones — METIS

Un archivo por decisión (`decision001.md` a `decision031.md`). No es un
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

## Addendums

Un addendum (corrección o ampliación de alcance posterior a la fecha
original de la decisión) vive dentro del mismo archivo que actualiza, no
en uno nuevo — no es una decisión distinta, es la misma decisión con
información más reciente. Addendums fechados existentes: `decision004.md`
(17/07/2026), `decision010.md` (10/07/2026), `decision011.md`
(18/07/2026), `decision023.md` (15/07/2026).

## Historial de esta migración

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

## Índice

| # | Título | Fecha | Estado |
|---|---|---|---|
| [001](decision001.md) | Autenticación CU-01 | 10/05/2026 | Parcialmente implementado — Parte 2 pendiente de credenciales SMTP de IT |
| [002](decision002.md) | Esquema tabla users y refactor de auth/ | 10/05/2026 | Implementado |
| [003](decision003.md) | Gestión de migraciones de esquema: Alembic | 14/05/2026 | Parcialmente implementado |
| [004](decision004.md) | Mecanismo de envío de mail para verificación de cuenta | 14/05/2026 | Parcialmente implementado — mock SMTP, aiosmtplib pendiente de credenciales IT |
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
