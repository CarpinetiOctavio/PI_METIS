# DECISIÓN 028 — Gobernanza de ramas: staging y main
**Fecha:** 18 de Julio de 2026
**Estado:** ESTABLECIDA — recomendada por cátedra de Proyecto Integrador

### Contexto
El flujo de tres niveles (feature → staging → main) ya estaba documentado
como convención técnica, pero sin registro de quién tiene la potestad de
mergear a cada rama ni bajo qué criterio — un dato de gobernanza, no solo
de arquitectura técnica, que la cátedra de PI recomendó formalizar como
buena práctica.

### Decisión
`staging` recibe merges cuando el equipo de desarrollo considera una
feature estable. `main` se pushea únicamente cuando la versión definitiva
está lista para desplegarse — y ese push queda a cargo específicamente
de Facundo, como codirector y responsable del entorno de despliegue en
la intranet de la UCC, no del equipo de desarrollo. El acceso al servidor
de contenedores (portal.ucc.edu.ar, credenciales gestionadas por IT fuera
de este repositorio) es el mecanismo concreto con el que se materializa
ese despliegue.

### Motivo
Práctica recomendada por la cátedra de Proyecto Integrador: separar quién
desarrolla de quién autoriza el release a producción, como punto de
control externo al equipo de desarrollo.

### Push vía PRs, no directo
Los push a `staging` y `main` se realizan mediante Pull Requests, no
push directo — una vez consolidado el entorno de CI/CD correspondiente.
Motivo doble: práctica académica/profesional estándar (revisión antes
de integrar) y política de seguridad (ningún cambio llega a una rama
protegida sin pasar por control de CI — tests, linting — y revisión
explícita).

### Pendiente — confirmar con IT: acceso saliente para registry de imágenes
**Estado:** PENDIENTE DE CONSULTA — no es una decisión tomada, es una
pregunta que debe hacerse antes de diseñar el pipeline de CI/CD

No confirmado si la intranet de la UCC permite acceso saliente desde el
servidor de producción hacia un registry externo (Docker Hub o GitHub
Container Registry) para `docker pull` en el pipeline de CI/CD.

Lo único confirmado hasta ahora sobre el firewall de la UCC: bloquea
acceso entrante (callback de OAuth falló por eso — [DECISIÓN 001](decision001.md),
flujo descartado documentado en `docs/historico/oauth-descartado.md`) y
permite acceso saliente hacia `smtp.gmail.com:587` (SMTP funciona). No
puede asumirse de esto que toda salida esté permitida sin restricción —
es común que firewalls institucionales permitan salida solo hacia una
lista blanca de hosts/puertos autorizados, en cuyo caso SMTP pudo haber
sido autorizado puntualmente sin que eso implique que un registry de
contenedores también lo esté.

Si la salida a registries externos no está permitida, alternativa
estándar: registry privado auto-hospedado dentro de la propia intranet
(`registry:2` en la misma red), evitando dependencia de salida a
internet para el pipeline de CI/CD.

**Acción:** consultar a IT antes de diseñar el pipeline de CI/CD.

#### -------------- Actualización ---------------

### Actualización 20 de Julio de 2026 — aclaración de alcance: "feature estable" es por rama, no por proyecto completo

Surgió una duda legítima al decidir si mergear `feature/auth-parte2` a
`staging` con pendientes abiertos (verificación dentro de la red UCC,
migración de `_pending_tokens` post-M5, ver DECISIÓN 005) — ¿contradice
esto la política de la sección "Decisión" de arriba ("`staging` recibe
merges cuando el equipo de desarrollo considera una feature estable")?

**Aclaración: no hay contradicción, pero la redacción original era
ambigua sobre la unidad de "estable".** "Feature" se refiere al alcance
de la rama que se mergea — no al proyecto completo, ni siquiera al epic
más amplio del que forma parte (ej. "Auth" como iniciativa general,
que sigue teniendo capítulos futuros como la migración post-M5). Una
rama es mergeable cuando su propio diff está terminado, testeado, y sus
pendientes conocidos son de alguno de estos dos tipos aceptables:
- Verificación bloqueada por falta de acceso a infraestructura (no un
  defecto de código) — ej. la red interna de la UCC, ver `sprint.md`.
- Trabajo explícitamente diferido a un milestone posterior ya
  documentado (no un olvido) — ej. `DECISIÓN 005`, migración de tokens
  post-M5.

Esto es distinto de un pendiente que pone en duda si el código produce
el resultado correcto — ej. `feature/core-etapa2` tiene un test
numérico fallando sin causa determinada
(`test_gen_pareto_mc_q100_serie_facundo`) y divergencias de EEA sin
explicación cerrada ("Causa C"/"Causa D", ver
`docs/auditoria/pendientes/pendientes-facundo.md`). Ese tipo de
pendiente sí amerita no mergear todavía, o mergear con el caveat
explícito puesto adelante, nunca escondido.

Precedente ya existente en este mismo repo, anterior a que se
formalizara esta aclaración: `feature/auth-refactor` (Parte 1 de
autenticación) se mergeó a `staging` con `DECISIÓN 004` documentando
explícitamente "Parte 2 pendiente de credenciales SMTP de IT" en ese
momento — el mismo patrón que esta aclaración ahora vuelve explícito.

No cambia la "Decisión" original de la sección de arriba — la precisa.


### Actualización 20 de Julio de 2026 — aclaración de alcance: pushes a main son progresivos, no un evento único

Aclaración adicional a la de arriba, sobre un punto distinto: la
redacción original ("`main` se pushea únicamente cuando la versión
definitiva está lista para desplegarse") se prestaba a leerse como un
único push al final del proyecto completo. No es así — `main` recibe
pushes progresivos a medida que sucesivas versiones estables del
proyecto van quedando listas, cada uno autorizado por Facundo bajo el
mismo criterio de gobernanza ya establecido arriba (separación entre
quién desarrolla y quién autoriza el release).

El push específicamente tageado `v1.0.0` es un evento propio, no
simplemente "el último push de la serie" por default — se coordina
explícitamente con Facundo en el momento, no se infiere automáticamente
de que sea cronológicamente el último merge a `main`.

Nota: los milestones de `sprint.md` (M5–M8, redactados como progresión
lineal hacia "V1.0") están desactualizados respecto a este modelo y
requieren revisión — pendiente, fuera del alcance de esta aclaración.
