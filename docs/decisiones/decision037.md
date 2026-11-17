# DECISIÓN 037 — Contrato de `/analysis/stream`: `etapas` descartado y `AnalysisRequest` sin cablear
**Fecha:** 29 de Julio de 2026
**Estado:** ~~DOCUMENTADO — no implementado en esta pasada, hoy inocuo, deja de serlo en M2~~ **CERRADA 09/08/2026 por [DECISIÓN 054](decision054.md)**

**Cierre 09/08/2026:** "deja de serlo en M2" (línea de abajo) se cumplió — Etapa 2
se cablea al stream en esta pasada. De las tres opciones que este archivo
dejaba abiertas, se eligió la opción 2 (`AnalysisRequest` se borra, los
`Form(...)` sueltos quedan como el modelo real). Ver DECISIÓN 054 para el
razonamiento completo del cierre; este archivo se conserva sin reescribir
por trazabilidad del diagnóstico original.

### Contexto
`api-contracts.md` documenta `POST /api/v1/analysis/stream` con un campo `etapas:
[1] | [1, 2]`, y `schemas/analysis.py` define `AnalysisRequest` como el modelo
Pydantic tipado de ese contrato completo (`etapas: list[Etapa]`, `cramer_particion:
Literal["default"] | CramerParticionCustom`, etc.). `CLAUDE.md` describe `schemas/`
como la capa de "Modelos Pydantic: analysis.py" y `sprint.md` marca
`feature/schemas` como mergeado y completo — la existencia de este modelo es, hoy,
el argumento de que la validación tipada de contrato está resuelta.

### Diagnóstico confirmado
Verificado directamente contra el código en esta pasada:

- `backend/metis/api/v1/analysis.py:25` declara `etapas: str = Form("1")`, pero la
  llamada a `stream_etapa1(...)` (líneas 35-46) **no incluye `etapas` entre sus
  argumentos**. El valor se recibe, se valida como string por FastAPI, y se
  descarta sin llegar a `services/` ni a `core/`.
- `frontend/src/api/sse.ts::buildFormData` (líneas 61-70) directamente no agrega
  `etapas` al `FormData` — el frontend nunca lo envía, ni con `[1]` ni con `[1,2]`.
- `backend/metis/schemas/analysis.py::AnalysisRequest` — el modelo que representa el
  contrato documentado completo — **no lo importa ninguna ruta**. `grep -rn
  "AnalysisRequest" backend/` solo devuelve la definición del modelo y su export en
  `schemas/__init__.py`. `/stream` redeclara cada campo como `Form(...)` suelto en
  vez de recibir el modelo.

### Por qué importa
Hoy es inocuo: Etapa 2 está mockeada en el frontend (ver
[DECISIÓN 042](decision042.md)) y el pipeline real de Etapa 1 no necesita saber si
el usuario pidió también Etapa 2. Pero:
- `CLAUDE.md` y `sprint.md` afirman que la capa de validación tipada existe y está
  cerrada — es exactamente el tipo de inconsistencia que conviene tener resuelta y
  documentada antes de la defensa ante el tribunal de ISI, no descubierta en ella.
  La capa tipada de Pydantic es un argumento de ingeniería central del proyecto
  (ver `architecture.md` — "FastAPI sobre Flask", validación automática con
  Pydantic).
- Deja de ser inocuo en M2: cuando Etapa 2 se exponga de verdad, el backend
  necesita saber si el usuario pidió `[1]` o `[1, 2]` para decidir si ejecuta el
  motor de Etapa 2 después de Etapa 1. Sin `etapas` cableado, no hay forma de que
  el endpoint sepa qué pipeline correr.

### Opciones evaluadas
1. **Cablear `AnalysisRequest` al endpoint multipart.** Requiere que `/stream` deje
   de declarar `Form(...)` sueltos y reciba el modelo — FastAPI soporta esto
   combinando `Form` por campo con un modelo Pydantic anidado (no directamente con
   `UploadFile` en el mismo modelo sin usar `Form(...)` field-by-field o un
   dependency), o parseando `AnalysisRequest.model_validate_json()` sobre un campo
   string único. Es la opción más fiel al contrato ya documentado, pero exige
   decidir primero cómo conviven `archivo: UploadFile` (no serializable en JSON) con
   el resto de los campos tipados.
2. **Mantener los `Form(...)` sueltos y borrar `AnalysisRequest`.** Reconoce que el
   patrón `Form(...)` por campo es lo que FastAPI recomienda para
   `multipart/form-data` con upload de archivo, y que un modelo Pydantic paralelo
   que nadie importa es peor que no tenerlo — código muerto que miente sobre el
   estado real de la validación. Requiere actualizar `api-contracts.md` para dejar
   de sugerir que hay un modelo único de request.
3. **Mantener ambos: `Form(...)` sueltos en runtime, `AnalysisRequest` como fuente
   de verdad documental del contrato, con una nota explícita de por qué no se usa
   en runtime.** Ninguna decisión se implementa sin elegir entre 1 y 2/3 primero —
   esta opción es la más barata pero perpetúa la inconsistencia que originó este
   hallazgo, solo que ahora documentada en vez de silenciosa.

### Decisión
**No se implementa ninguna opción en esta pasada** — mismo alcance que
[DECISIÓN 036](decision036.md): hallazgos de backend de esta pasada se documentan,
no se implementan. Queda agendado, con prioridad ligada a M2/M3 (cuando Etapa 2 se
exponga de verdad, `etapas` deja de ser inocuo — ver "Por qué importa"). Sin
recomendación cerrada entre las tres opciones.

### Criterio de hecho
- `decision037.md` existe e indexada en `docs/decisiones/README.md`.
- `sprint.md` referencia esta decisión dentro del alcance de M2/M3.
- `CLAUDE.md` no queda afirmando que `schemas/analysis.py` está cableado al
  endpoint cuando no lo está.

**Ver también:** [DECISIÓN 036](decision036.md) — el mismo endpoint, un campo
distinto (`cramer_particion`) con un síntoma relacionado pero no idéntico (ahí sí
hay intento de cablear el dict, acá el campo directamente no se usa).
