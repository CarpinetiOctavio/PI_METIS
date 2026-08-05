# DECISIÓN 050 — Límite de tamaño de subida: valor, dónde se aplica, código de error

**Fecha:** 5 de Agosto de 2026
**Estado:** Decidida — implementación en curso (Bloque A, Pasada 5, `docs/plan-post-pasada4-roadmap.md`)

### Contexto

`docs/plan-post-pasada4-roadmap.md` (H2, H3) encontró dos problemas reales de
subida de archivos, ninguno ejercitado nunca en un smoke test porque
`npm run dev` pega directo a `:8000` sin pasar por nginx:

- **H2 — bloqueante.** Ni `nginx/nginx.conf` ni `frontend/nginx.conf`
  declaran `client_max_body_size`. El default de nginx es **1 MB**: a través
  del reverse proxy (`http://localhost/...`, el único camino real en
  producción), cualquier Excel/CSV de más de 1 MB recibe **413** en
  `/analysis/stream` y `/analysis/preview-columns` sin que el backend llegue
  a verlo. Es la clase de defecto "anda en dev, roto en producción" —
  exactamente lo que la pasada de arreglo de UI existió para eliminar.
- **H3.** `POST /analysis/preview-columns` es anónimo (DECISIÓN 047), sin cap
  de tamaño, y lee el archivo completo en memoria
  (`await archivo.read()` → `_leer_dataframe()` completo). Sin límite, un
  POST de varios cientos de MB es un OOM del contenedor backend. El mismo
  patrón (`content = await archivo.read()`) existe en `POST /analysis/stream`.

### Opciones evaluadas — valor del límite

Medido con series sintéticas generadas con `pandas`/`openpyxl` (host, fuera
del repo — no se commitean como fixture porque son aleatorias y no aportan
valor de test), reproduciendo el caso real de este dominio (`fecha` +
`caudal`, columnas `IV.1`):

| Caso | Filas | Tamaño |
|---|---|---|
| Anual, 40 años (caso típico — series de la tesis de Facundo son anuales/mensuales) | 40 | 5,9 KB |
| Diaria, 40 años (peor caso realista de resolución) | ~14 600 | 337 KB (.xlsx) / 445 KB (.csv) |
| Horaria, 40 años (caso extremo, improbable en este dominio pero posible si alguien sube datos de estación automática sin agregar) | ~350 400 | 7,68 MB (.xlsx) |

Incluso el caso extremo (resolución horaria sostenida durante 40 años,
resolución que ninguna prueba de Etapa 1/2 de este dominio necesita — el
pipeline trabaja con series anuales de máximos) queda en ~7,7 MB. Un límite
de:
- **1 MB** (default de nginx, opción "no tocar nada") — rechaza el caso
  diario real (337-445 KB pasa, pero queda sin margen para overhead de
  formato/metadata de Excel real exportado desde otra herramienta).
- **5 MB** — cubre diaria con margen amplio, pero deja el caso horario
  extremo (7,68 MB) sin margen.
- **10 MB** (elegida) — ~1700x el caso típico, ~25-30x el caso diario real,
  y ~30% de margen sobre el caso horario extremo. Suficiente para absorber
  el overhead de formato de un `.xlsx` real (estilos, tema, múltiples hojas)
  sin abrir la puerta a subidas de cientos de MB que solo tienen sentido
  como vector de agotamiento de memoria, no como caso de uso real de este
  dominio.

### Decisión

**Límite: 10 MB, aplicado en dos capas independientes — ninguna es
suficiente por sí sola:**

1. **nginx — `client_max_body_size 10m;`** en `nginx/nginx.conf` (bloque
   `location /api/`) y en `frontend/nginx.conf`, mismo valor en los dos.
   `frontend/nginx.conf` no proxea `/api/` (solo sirve el build estático vía
   `try_files`), pero se mantiene igualado por si el contenedor del frontend
   se expone alguna vez de forma standalone sin el nginx externo por medio —
   consistencia sin costo, no hay tráfico de subida real que pase por ahí en
   la topología actual (ver `architecture.md`, "Nginx como reverse proxy").
2. **Backend — cap independiente del proxy.** nginx no es el único camino:
   `:8000` está mapeado al host por diseño para desarrollo/smoke tests (ver
   `architecture.md`, "Exposición de puertos en desarrollo"), así que un
   cliente que le pegue directo al backend salteando nginx tiene que
   encontrar el mismo límite. Se aplica **antes** de leer el archivo
   completo — lectura en chunks de 1 MiB con corte apenas se supera el
   límite, nunca se buffera un archivo entero por encima de 10 MB en
   memoria aunque el cliente mienta el `Content-Length`. Aplica a
   `POST /analysis/preview-columns` y `POST /analysis/stream` — los dos
   únicos endpoints que reciben `UploadFile`.

**No se sube el límite de nginx sin el cap del backend, ni viceversa** —
subir solo el de nginx cambiaría un 413 barato (rechazado en el borde, sin
tocar el proceso del backend) por un OOM caro (el backend igual buferea todo
en memoria antes de fallar). Son un solo cambio atómico, no dos parches
independientes.

### Catálogo de errores

Código nuevo: **`PARSE_FILE_TOO_LARGE`** (prefijo `PARSE_`, mismo prefijo que
`PARSE_ERROR` — ambos son fallas al ingerir el archivo subido, antes de
llegar a `core/validacion/contract.py`). HTTP 400, agregado a
`.claude/rules/architecture/api-contracts.md` y a
`frontend/src/i18n/errors.es.ts` en el mismo commit que lo introduce
(regla de DECISIÓN 038).

### Criterio de hecho

- Subir a través de nginx (`http://localhost/...`) un archivo apenas por
  debajo de 10 MB → pasa el proxy sin 413.
- Subir un archivo apenas por encima de 10 MB, mismo camino → rechazo
  limpio con `PARSE_FILE_TOO_LARGE`/400, no 413 de nginx ni 500/timeout del
  backend — el mensaje llega hasta la UI, no una pantalla colgada.
- Golpear `POST /analysis/preview-columns` y `POST /analysis/stream`
  directo contra `:8000` (salteando nginx) con un archivo por encima del
  límite → mismo rechazo 400/`PARSE_FILE_TOO_LARGE`, memoria del proceso
  backend nunca supera ~10 MB adicionales por la subida.
- `scripts/check-error-catalog.sh` en verde con el código nuevo en las tres
  direcciones (backend, catálogo, diccionario del frontend).

**Ver también:** [DECISIÓN 038](decision038.md) — regla de sincronización
del catálogo de errores. [DECISIÓN 047](decision047.md) — el otro endpoint
que este límite protege, mismo patrón de `UploadFile` sin cap previo.
