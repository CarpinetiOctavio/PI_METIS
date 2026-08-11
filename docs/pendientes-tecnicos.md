# Deuda técnica — registro vivo

Registro de lo que sabemos que falta y no tiene otro archivo dónde vivir:
no es una decisión ya tomada (`docs/decisiones/`), no es una pregunta de
dominio para escalar a Facundo o Carlos (`docs/auditoria/pendientes/`), y no
es parte de un plan de trabajo activo que se borra al cerrarse. Creado en el
Bloque 0 del plan de implementación de Etapa 2 (09/08/2026) porque los tres
directorios de test vacíos del proyecto no tenían dónde registrarse — y por
eso se perdían.

**Regla:** cada entrada dice qué falta, qué bloquea, y quién la cierra. Las
entradas que se cierran se tachan con la fecha de cierre, no se borran —
mismo criterio de trazabilidad que rige el resto del proyecto (ver
`docs/decisiones/README.md`, `docs/historico/README.md`).

| Pendiente | Qué bloquea | Quién lo cierra | Estado |
|---|---|---|---|
| ~~`tests/integration/` vacío (solo `__init__.py`)~~ | Ningún test de integración corre en CI | Bloque A6 del plan de Etapa 2 lo estrena | **Cerrado 09/08/2026** — `test_etapa2_stream_distribution_decision.py` |
| `tests/regression/` vacío | Ningún test de regresión matemática corre en CI | Bloque D del plan de Etapa 2 lo estrena | Abierto |
| `tests/e2e/` vacío | `constraints.md` excluye E2E de UI del scope V1.0, pero los E2E de API que `testing.md` §3 compromete no están excluidos y tampoco existen | Sin plan asignado todavía | Abierto |
| El job `test` de CI tolera exit code 5 | Un job de CI en verde no distingue "sin tests que correr" de "tests corridos y en verde" para integration/regression | Deja de hacer falta cuando `tests/integration/` tenga tests reales; se quita en un PR propio, no junto con el que agrega los tests | Abierto |
| FE-16 — `Etapa1Result` no expone la serie cruda | Bloquea la serie temporal, el boxplot mensual y el gráfico de Chow (los tres necesitan la serie cruda, no solo los resultados agregados) | Sin plan asignado todavía | Abierto |
| `resolucion_temporal` se calcula y nunca se consume | Una serie mensual entra al pipeline y se analiza como si fuera anual, sin error ni warning | Bloque F2.1 del plan de Etapa 2 | Abierto |
| `_espaciado_regular()` da falso positivo en toda serie mensual | Cualquier serie mensual real dispara `CONTRACT_IRREGULAR_SPACING` (meses de 28/30/31 días) | Bloque F2.2 del plan de Etapa 2 | Abierto |
| `_inferir_resolucion()` usa el promedio y no la moda de los deltas | Una serie mensual con un hueco largo puede inferirse como `"anual"` sin que nada lo note | Bloque F2.3 del plan de Etapa 2 | Abierto |
| ~~MSW sin uso real si el Bloque B del plan de Etapa 2 borra su último handler~~ | Dependencia de dev mantenida sin ningún caso de uso real en el repo | Evaluar sacarlo del proyecto en el mismo PR que borra el último handler | **Cerrado 09/08/2026** — `msw` salió de `package.json` por completo en el Bloque B (ver DECISIÓN 042, addendum) |
| ~~`schemas/analysis.py::AnalysisRequest` código muerto~~ | Modelo Pydantic que ninguna ruta importa — mantenerlo invita a que alguien lo cablee a medias de nuevo (mismo patrón que produjo DECISIÓN 037) | Se resuelve en A3 del plan de Etapa 2 (cablear como modelo real o borrar) | **Cerrado 09/08/2026** — borrado (DECISIÓN 054) |
| `pi_metis-backend-1` corre `uvicorn` sin `--reload` | `docker cp` actualiza los archivos del contenedor, pero el proceso ya arrancado sigue sirviendo el código que tenía cargado en memoria — solo un `docker restart pi_metis-backend-1` hace que el servidor HTTP vea cambios de código. `pytest`/`ruff` vía `docker exec` no lo sufren (procesos nuevos, importan fresco); solo lo sufre verificar contra el servidor ya corriendo (navegador, `curl` manual). Encontrado en el Bloque C del plan de Etapa 2 (11/08/2026): un smoke test en navegador contra el backend real venía fallando con `curva_ajuste`/`puntos_empiricos` ausentes del payload pese a que el código en disco del contenedor ya los tenía — diagnosticado comparando `docker exec ... python3 -c "..."` (proceso nuevo, código correcto) contra el `curl` directo al servidor HTTP corriendo (proceso viejo, código viejo) | Sin plan asignado — evaluar agregar `--reload` a `docker-compose.yml` para desarrollo, o documentar el `docker restart` como paso obligatorio después de todo `docker cp` | Abierto |
