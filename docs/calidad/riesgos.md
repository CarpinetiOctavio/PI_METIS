# Riesgos de producto — METIS V1.0

TP integrador de Calidad de Software, bloque B9. Riesgos que pueden hacer que METIS entregue un resultado incorrecto,
no esté disponible o no se pueda mantener, evaluados por probabilidad × impacto. Los riesgos del propio plan de
pruebas (tiempo, permisos) están en `plan-de-pruebas.md` §11.

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0 | 09/10/2026 | Primera versión |

## 1. Escalas

| Valor | Probabilidad | Impacto |
|---|---|---|
| 1 | Baja: no pasó y no hay un mecanismo que lo haga probable | Bajo: molestia, con alternativa inmediata |
| 2 | Media: pasó una vez, o hay un mecanismo plausible | Medio: un flujo no funciona, o un resultado queda sin advertencia de un límite conocido |
| 3 | Alta: pasó más de una vez, o es la situación actual | Alto: un número de diseño incorrecto sin advertencia, o el sistema no está disponible |

**Exposición = P × I.** De 6 a 9: alta, se mitiga antes de la entrega. De 3 a 4: media, se mitiga o se acepta por
escrito. De 1 a 2: baja, se acepta.

## 2. Matriz

| | Impacto 1 | Impacto 2 | Impacto 3 |
|---|---|---|---|
| **Probabilidad 3** | | R-02, R-04 | |
| **Probabilidad 2** | R-11, R-12 | R-05, R-08, R-09 | R-01, R-10 |
| **Probabilidad 1** | | R-07 | R-06, R-13 |

R-03 (fórmula de Chow) figura cerrado en el §3.

## 3. Registro de riesgos

Ordenado por exposición. **Evidencia** es por qué se asignó esa probabilidad; **mitigación** es lo que ya existe o
lo que falta.

| ID | Riesgo | P | I | Exp. | Evidencia | Mitigación | Estado |
|---|---|---|---|---|---|---|---|
| R-01 | **Un resultado estadístico distinto de la tesis, en silencio** (fórmula mal transcrita, orden de la serie, índice mal mapeado) | 2 | 3 | 6 | 5 de los 10 defectos registrados son de este tipo (D-03, D-04, D-05, D-08, D-09), todos encontrados antes de llegar a un usuario | Auditoría de 4 fases contra la tesis; tests de fórmula con el valor de la fuente como oráculo; comparación con R, SciPy, LibreOffice y SAMHIA (PR #109); casos de caja negra (B8); `core/` aislado y testeable | Mitigado. Residual: la regresión automatizada de las 9 estaciones la lleva Octavio y todavía no está en el repo |
| R-02 | **Preguntas de dominio sin respuesta del oráculo** (Mann-Kendall 1,96 frente al 1,64 de la tabla, redondeo de la partición de Cramer, fórmula de asimetría, convenciones de Generalizada de Pareto, U_T de la planilla) | 3 | 2 | 6 | Abiertas en `docs/auditoria/pendientes/pendientes-facundo.md`, algunas desde agosto | Cada divergencia está documentada con la decisión tomada mientras tanto; Generalizada de Pareto se calcula pero no se puede elegir (DECISIÓN 074) | Aceptado, con seguimiento |
| R-04 | **Base de datos sin migrar** | 3 | 2 | 6 | Pasó el 05/08/2026 (`/history/` respondía 500) y de nuevo el 09/10/2026 en la base de desarrollo local, que no tenía ninguna tabla. Con la base sin migrar o caída, CU-01 responde un 500 en texto plano; CU-02 sigue funcionando completo; `/ping` responde 200 igual | `deploy-local.sh` y el job `despliegue` corren `alembic upgrade head` siempre; el smoke prueba el login contra la base. Falta: un `/ping` que consulte la base, para que el problema se vea antes del primer usuario (`contingencia.md` §2) | Mitigado en CI y en el despliegue; abierto en desarrollo |
| R-10 | **El despliegue en los servidores de la UCC no está probado** | 2 | 3 | 6 | Depende de IT: registry de imágenes, SSH desde Actions, firewall (DECISIÓN 028) | El despliegue efímero usa la configuración de producción (`docker-compose.ci.yml`: sin `--reload` ni bind mount) y se verifica con smoke y E2E en cada PR | Abierto. Se declara como trabajo posterior en el informe |
| R-05 | **SMTP caído o credenciales vencidas**: nadie se puede registrar | 2 | 2 | 4 | El relay es externo; el App Password lo administra IT | Plan de contingencia (`integracion-smtp.md` §5); prueba de punta a punta con Mailpit en cada PR (E2E-0) | Mitigado |
| R-08 | **Dependencias desactualizadas** (FastAPI 0.111, Starlette con `multipart` deprecado) | 2 | 2 | 4 | DECISIÓN 033 difirió la actualización; hay un warning suprimido en `pytest.ini` | Criterios explícitos para actualizar en DECISIÓN 033; los tests de unidad e integración cubren el borde de la API | Aceptado |
| R-09 | **Capacidad**: el sistema se degrada entre 20 y 40 usuarios concurrentes | 2 | 2 | 4 | Stress hasta el quiebre: el throughput se estanca en ~45 req/s (un solo proceso de uvicorn) y el p95 pasa de 2 s con 60 usuarios, sin errores (`herramienta-carga.md` §6) | Umbrales en CI que detectan una degradación grande. El uso previsto (docentes en la intranet) está por debajo del quiebre. Escalar requiere mover las sesiones a un almacenamiento compartido (ver R-06) | Aceptado para V1.0 |
| R-06 | **Más de un worker de uvicorn rompe las pausas del stream**: la decisión llega a un proceso que no tiene la sesión | 1 | 3 | 3 | Las sesiones viven en memoria del proceso (`session_store`, DECISIÓN 053). Hoy hay un solo worker | Documentado en `herramienta-carga.md` §6 como precondición para escalar | Aceptado; vigilar si alguien agrega `--workers` |
| R-13 | **La interfaz se rompe con todos los tests en verde** | 1 | 3 | 3 | Pasó: F1, el stream se abortaba bajo StrictMode con 98 tests en verde (D-01) | Tests de página bajo `StrictMode` por regla; Capa 2 de integración; seis E2E en cada PR; evidencia en navegador en la DoD | Mitigado |
| R-07 | **SSE detrás de nginx** (buffering o timeout que corten el stream durante una pausa) | 1 | 2 | 2 | Riesgo típico de un reverse proxy | `proxy_buffering off` y `proxy_read_timeout 3600s` en `nginx.conf`, `X-Accel-Buffering: no` en la respuesta; el smoke y los E2E consumen el stream a través de nginx | Mitigado |
| R-11 | **Sesiones abandonadas en una pausa** quedan en memoria hasta el timeout | 2 | 1 | 2 | La prueba sostenida no las cubre: k6 no corta un stream a la mitad (`herramienta-carga.md` §6) | `SESSION_TIMEOUT = 300` s libera la espera con `SESSION_TIMEOUT` | Aceptado |
| R-12 | **Tokens de verificación perdidos** al reiniciar el backend | 2 | 1 | 2 | `_pending_tokens` vive en memoria (`auth/router.py`) | El usuario repite el registro; mover los tokens a la base queda para después de V1.0 (`integracion-smtp.md` §5) | Aceptado |
| R-03 | Fórmula de Chow distinta de la que espera el dominio | — | — | — | Implementada como Grubbs-Beck provisoria (DECISIÓN 018) | Confirmada por Carlos el 09/09/2026 | **Cerrado** |

## 4. Cómo se usa esta matriz

- **Para priorizar pruebas.** Los riesgos de exposición alta definen el orden de `plan-de-pruebas.md` §3: la
  exactitud del motor va primero porque R-01 tiene impacto 3.
- **Para decidir qué entra en el pipeline.** R-04, R-05, R-07 y R-13 se mitigan con jobs que corren en cada PR. Un
  riesgo con impacto 3 sin una prueba automática que lo vigile tiene que tener una razón escrita (R-10: depende de
  terceros).
- **Revisión.** Se revisa al cerrar cada bloque del plan y cuando aparece un defecto nuevo: un defecto de una
  categoría que no está acá es un riesgo que no se había visto, y se agrega.
