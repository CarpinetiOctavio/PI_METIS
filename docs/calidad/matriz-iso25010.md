# Matriz ISO/IEC 25010 — METIS V1.0

TP integrador de Calidad de Software, bloque B9. Las ocho características del modelo de calidad de producto de
ISO/IEC 25010, con la evidencia concreta que tiene METIS para cada una, su estado y lo que falta.

| Versión | Fecha | Cambios |
|---|---|---|
| 1.0 | 09/10/2026 | Primera versión |

**Estado:** **Cubierta** = hay evidencia medida y una prueba automática que la vigila. **Parcial** = hay evidencia,
pero falta una subcaracterística o la verificación es manual. **Débil** = casi no hay evidencia.

## 1. Matriz

| Característica | Subcaracterísticas que aplican | Evidencia | Estado | Brecha |
|---|---|---|---|---|
| **Adecuación funcional** | Completitud, corrección, pertinencia | **Corrección:** auditoría de 4 fases contra las 9 estaciones de la tesis; tests de fórmula con el valor de la fuente; comparación con R, SciPy, LibreOffice y SAMHIA (diferencia 0 donde la definición es la misma, PR #109); 74 casos de caja negra (`casos-de-prueba.md`). **Completitud:** 31 de 40 RF implementados, total o parcialmente (`trazabilidad.md`). **Pertinencia:** los directores usan la herramienta y sus observaciones se convierten en requisitos (feedback del 02/09 y del 20/09) | Cubierta en corrección; parcial en completitud | CU-03 sin implementar (4 RF); FDP y normalidad visual (RF-GEN-O-04, O-06); decisiones ante problemas del contrato (RF-CU01-05, CU02-05). Preguntas de dominio abiertas (`riesgos.md`, R-02) |
| **Eficiencia de desempeño** | Comportamiento temporal, uso de recursos, capacidad | **Temporal:** p95 de 43/72/147 ms con 15 usuarios, con umbrales en CI (job `carga`). **Recursos:** memoria estable con 5 usuarios durante 30 min (+0,3 MB/h). **Capacidad:** quiebre medido entre 20 y 40 usuarios, sin errores hasta 120 (`herramienta-carga.md`) | Cubierta | Un solo worker de uvicorn: escalar requiere sesiones compartidas (`riesgos.md`, R-06 y R-09) |
| **Compatibilidad** | Coexistencia, interoperabilidad | **Interoperabilidad:** API REST documentada con OpenAPI (FastAPI la genera), contratos en `api-contracts.md`; entrada en CSV y Excel (RF-GEN-P-01). **Coexistencia:** los servicios corren en contenedores aislados, detrás de un único nginx | Parcial | La interoperabilidad con sistemas externos es CU-03, sin implementar. Los E2E solo corren en Chromium |
| **Usabilidad** | Reconocimiento de adecuación, aprendizaje, operabilidad, protección contra errores, estética, accesibilidad | **Aprendizaje:** modo paso a paso con la fórmula sustituida por cada prueba (DECISIÓN 064). **Protección contra errores:** validación en el borde con código y mensaje traducido para cada error (catálogo verificado en CI); el frontend no decide por el usuario (opciones con el mismo peso visual). **Accesibilidad:** contraste WCAG AA (DECISIÓN 043), gráficos navegables por teclado, selectores accesibles exigidos en los E2E (`getByRole`) | Parcial | No hay pruebas de usabilidad con usuarios ni una herramienta de accesibilidad automática en el pipeline; la evidencia es la revisión de los directores en uso |
| **Fiabilidad** | Madurez, disponibilidad, tolerancia a fallos, capacidad de recuperación | **Madurez:** 10 defectos registrados, todos cerrados con test de regresión. **Tolerancia a fallos:** ningún caso especial de Etapa 2 detiene el pipeline (RF-GEN-P-09); un período de retorno que falla devuelve `null` sin tumbar el resto; timeout de 300 s en las pausas del stream. **Disponibilidad:** 0 % de error en el stress y en la prueba sostenida. **Recuperación:** plan de contingencia (`contingencia.md`); con la base caída, CU-02 sigue funcionando (verificado el 09/10/2026) | Cubierta, con brechas puntuales | `/ping` no detecta la base caída; la base caída devuelve 500 sin código; sin backup automático (`contingencia.md` §2) |
| **Seguridad** | Confidencialidad, integridad, autenticidad, responsabilidad | **Autenticidad:** registro con mail institucional y verificación por token; contraseñas con bcrypt; JWT en cookie HttpOnly (`auth/`, tests en `tests/unit/auth/`). **Confidencialidad:** un análisis ajeno responde 404, no 403 (no revela que existe), probado contra PostgreSQL real y por HTTP. **Integridad:** el análisis persistido no se modifica; explorar no altera lo registrado (DECISIÓN 062). **Responsabilidad:** cada decisión del usuario queda registrada en el historial. Security Rating y hotspots de SonarCloud en cada PR | Parcial | Sin análisis de dependencias vulnerables en el pipeline ni pruebas de penetración. CORS estricto y HTTPS dependen de la configuración de producción en la UCC, no probada |
| **Mantenibilidad** | Modularidad, reusabilidad, analizabilidad, modificabilidad, capacidad de ser probado | **Modularidad:** `core/` no importa nada de HTTP, base ni sesiones: el motor se prueba sin levantar la app. **Testeabilidad:** 1.162 tests de unidad, cobertura del backend de 94,7 % en sentencias y 84,1 % en decisión. **Analizabilidad:** 75 decisiones registradas con contexto y alternativas; duplicación de 0,63 %. **Modificabilidad:** gate de cobertura nueva ≥ 80 % en cada PR; SonarCloud con Reliability A | Cubierta | Deuda conocida en `docs/pendientes-tecnicos.md` (estadísticos duplicados en `etapa2/`, DECISIÓN 022) |
| **Portabilidad** | Adaptabilidad, instalabilidad, reemplazabilidad | **Instalabilidad:** `deploy-local.sh` despliega desde cero con la configuración de producción y lo verifica, el mismo script que usa CI. **Adaptabilidad:** todo en contenedores Docker; año hidrológico configurable (`mes_inicio_anio`) para registros de otras regiones (DECISIÓN 057) | Parcial | El despliegue en los servidores de la UCC no está probado (DECISIÓN 028, `riesgos.md` R-10) |

## 2. Las tres características prioritarias

**1. Adecuación funcional, por la corrección.** METIS existe para reemplazar una planilla de Excel en un cálculo
cuyo resultado es un valor de diseño hidrológico: un caudal o una precipitación con la que después se dimensiona una
obra. Un error ahí no se ve: la pantalla muestra un número plausible. Por eso es el riesgo de mayor impacto
(`riesgos.md`, R-01), la característica con más inversión de prueba (auditoría de 4 fases, oráculo externo, casos
de caja negra) y la razón de que la regla del proyecto sea "ninguna fórmula sin referencia a la ecuación de la
tesis".

**2. Fiabilidad.** El uso es docente e interactivo: el análisis se pausa dos veces esperando una decisión, y un
corte a la mitad le hace perder el trabajo al usuario. El principio de negocio central ("detecta y advierte, pero no
bloquea") es una decisión de fiabilidad: ante datos imperfectos, el sistema sigue y avisa en lugar de fallar. Los
dos defectos de severidad alta registrados (D-01 y D-02) fueron de este tipo: la app dejaba de responder.

**3. Mantenibilidad.** Es un proyecto integrador que se defiende ante un tribunal de ISI y que va a seguir
creciendo (CU-03, la versión 2 de Generalizada de Pareto, las respuestas pendientes de Facundo, que pueden cambiar
una fórmula). Cada respuesta del oráculo de dominio puede obligar a tocar el motor; si el motor no fuera una librería
aislada y cubierta por tests, cada cambio sería un riesgo de romper otro resultado en silencio.

**Por qué no las otras como prioritarias.** Desempeño: el uso previsto (docentes dentro de la intranet) queda por
debajo del punto de quiebre medido. Seguridad: los datos son series hidrológicas públicas, no datos personales
sensibles, y la autenticación cubre lo que hay que proteger (que nadie vea ni modifique el historial ajeno).
Compatibilidad y portabilidad dependen sobre todo de CU-03 y del despliegue en la UCC, que están fuera de este TP.
