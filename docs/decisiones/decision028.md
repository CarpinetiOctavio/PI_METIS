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
acceso entrante (callback de OAuth falló por eso — [DECISIÓN 001](decision001.md)) y
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
