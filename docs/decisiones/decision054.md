# DECISIÓN 054 — `etapas` cableado de punta a punta
**Fecha:** 09 de Agosto de 2026
**Estado:** Decidida — implementación en curso (Bloque A del [plan de implementación de Etapa 2](../plan-etapa2-implementacion.md)) — cierra [DECISIÓN 037](decision037.md)

### Contexto

[DECISIÓN 037](decision037.md) documentó, sin implementar, que
`POST /api/v1/analysis/stream` recibe `etapas: str = Form("1")`
(`api/v1/analysis.py:87`) y lo descarta sin pasarlo nunca a `stream_etapa1()`
— confirmado de nuevo en esta pasada, la línea sigue igual. El frontend
tampoco lo envía. `schemas/analysis.py::AnalysisRequest` (líneas 23-29) declara
`etapas: list[Etapa] = [1]` como parte del modelo tipado completo del
contrato, pero ninguna ruta lo importa — `grep -rn "AnalysisRequest"
backend/` solo devuelve la definición y su export en `schemas/__init__.py`.

DECISIÓN 037 quedó "inocua hoy, prioridad M2/M3" porque Etapa 2 estaba
mockeada en el frontend. Deja de ser inocua exactamente ahora: sin `etapas`
cableado, `POST /analysis/stream` no tiene forma de saber si el usuario pidió
`[1]` o `[1, 2]`, y [DECISIÓN 052](decision052.md) necesita esa señal para
decidir si el stream entra a Etapa 2 después de `result_etapa1`.

### Decisión

Cuatro capas, en orden:

1. **`api/v1/analysis.py`** — `etapas: str = Form("1")` se parsea a
   `list[int]` en el borde del endpoint. Solo se aceptan los literales `"1"` y
   `"1,2"`; cualquier otro valor responde 400 `CONTRACT_ETAPAS_INVALID`
   (código nuevo, mismo tratamiento de catálogo que los de
   [DECISIÓN 052](decision052.md)). El parseo vive acá, no en `core/` —
   mismo patrón que `cramer_particion` desde [DECISIÓN 036](decision036.md):
   el motor estadístico nunca ve un string sin validar.
2. **`stream_etapa1()` se renombra a `stream_analysis()`**, con el `import`
   actualizado en `api/v1/analysis.py`. La función deja de ser solo-Etapa-1 en
   cuanto puede continuar hacia Etapa 2 — el nombre anterior mentiría sobre lo
   que la función hace. Es el único renombre de todo el Bloque A.
3. **`schemas/analysis.py::AnalysisRequest` se borra.** De las tres opciones
   que DECISIÓN 037 dejó abiertas (cablearlo al endpoint, borrarlo, o
   mantenerlo como documentación paralela con una nota), se elige borrarlo:
   `/stream` es `multipart/form-data` con un `UploadFile`, que no modela bien
   con un `BaseModel` plano sin recurrir a `Form(...)` campo por campo o a un
   parseo JSON dentro de un campo string — y un modelo Pydantic que nadie
   importa ni valida en runtime es exactamente el patrón que produjo
   DECISIÓN 037 en primer lugar: código que afirma que existe una capa de
   validación tipada que en realidad no corre nunca. Mantenerlo "por las
   dudas" perpetúa esa mentira en vez de resolverla.
4. **`frontend/src/api/analysis.ts`** — el `FormData` que arma el request
   empieza a incluir `etapas`, tomado del selector de alcance que agrega
   `ConfigPage` (Bloque B4 del plan de Etapa 2). Hoy no lo manda en absoluto.

### Por qué no las otras dos opciones de DECISIÓN 037

- **Cablear `AnalysisRequest` al endpoint multipart** habría exigido resolver
  primero cómo convive `archivo: UploadFile` (no serializable a JSON) con el
  resto de los campos tipados — una decisión de diseño de FastAPI aparte, sin
  beneficio real sobre `Form(...)` campo por campo, que es lo que el propio
  framework recomienda para este caso y lo que el endpoint ya usa para todos
  los demás campos (`columna_x`, `columna_y`, `modo`, `cramer_particion`).
- **Mantener ambos con una nota explicativa** perpetuaba la inconsistencia
  documentada, solo que señalizada — más barato de escribir, pero deja el
  código muerto en el árbol indefinidamente.

### Criterio de hecho

- `POST /analysis/stream` con `etapas=1,2` hace que el stream continúe a
  Etapa 2 después de `result_etapa1`; con `etapas=1` (o sin el campo) se
  comporta exactamente como antes de esta decisión.
- `etapas` fuera de `{"1", "1,2"}` responde 400 `CONTRACT_ETAPAS_INVALID`.
- `grep -rn "AnalysisRequest" backend/` no devuelve nada.
- `grep -rn "stream_etapa1" backend/metis` no devuelve nada — todas las
  referencias pasan a `stream_analysis`.
- `frontend/src/api/analysis.ts` incluye `etapas` en el `FormData` que arma.
- `CONTRACT_ETAPAS_INVALID` presente en `api-contracts.md` y en
  `frontend/src/i18n/errors.es.ts`; `./scripts/check-error-catalog.sh` en
  verde.
- [DECISIÓN 037](decision037.md) actualizada: marcada como cerrada por esta
  decisión, con su índice en `docs/decisiones/README.md` reflejando el cierre.

**Ver también:** [DECISIÓN 036](decision036.md) — el mismo endpoint, el mismo
patrón de "validar el string en el borde, nunca en `core/`", aplicado antes a
`cramer_particion`. [DECISIÓN 052](decision052.md) — el contrato SSE que
consume la señal `etapas == [1, 2]` que esta decisión hace posible.
