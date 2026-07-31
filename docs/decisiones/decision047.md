# DECISIÓN 047 — Endpoint `preview-columns`: parseo de cabeceras del lado del servidor
**Fecha:** 31 de Julio de 2026
**Estado:** Decidida — implementación en curso (Bloque D, pasada 4)

### Contexto
`docs/frontend/plan-mejora-frontend-pasada4.md` (punto 2 del feedback de UX)
pide que `ConfigPage` deje de pedir "Columna X"/"Columna Y" como texto libre
y ofrezca un dropdown con las columnas reales del archivo subido.

### Opciones evaluadas
1. **Parsear el archivo en el navegador** (librería JS tipo `sheetjs` para
   leer cabeceras de CSV/Excel). Descartada: las columnas que el dropdown
   ofrecería podrían no coincidir con las que `pandas.read_excel`/`read_csv`
   ve realmente en `core/validacion/parser.py` — distintas librerías
   interpretan encabezados, tipos y filas vacías de forma distinta. El
   usuario podría elegir una columna que el pipeline real no encuentra,
   moviendo el error de "antes de enviar" a "en medio del análisis". Además
   suma ~400 KB al bundle del frontend para leer Excel, sin necesidad —el
   backend ya tiene `pandas`/`openpyxl` en `requirements.txt`, costo cero de
   dependencias nuevas.
2. **Endpoint de previsualización que reusa el mismo parser que el pipeline
   real.** Elegida. Garantiza que lo que el dropdown ofrece es exactamente
   lo que `POST /analysis/stream` va a leer, porque es literalmente la misma
   función (`core/validacion/parser.py`) la que resuelve ambos caminos.

### Decisión
`POST /api/v1/analysis/preview-columns` — multipart/form-data con el
archivo. JWT opcional (mismo criterio que `/analysis/stream`: sirve a CU-01
y CU-02 por igual). A diferencia de `/analysis/stream`, el endpoint no
declara ninguna dependencia de usuario en absoluto — no hay ninguna
diferencia de comportamiento según quién llama, así que "JWT opcional" acá
se cumple trivialmente por no inspeccionar la cookie, no por una dependencia
FastAPI que la lea y la ignore.

**Completamente stateless** — no genera `session_id`, no toca
`session_store`, no escribe en BD. Es una previsualización, no el arranque
de un análisis.

**`core/validacion/parser.py::leer_columnas_preview()`** — extraída del
mismo módulo que ya parsea para `/analysis/stream`, para que ambos caminos
compartan una sola lectura de cabeceras y no puedan divergir. Desviación
consciente de la letra del plan ("leyendo solo las primeras filas, no el
archivo completo"): la respuesta necesita un conteo real de filas (`filas`
en el contrato), y las series hidrológicas de este dominio son
características por ser chicas (registros anuales o mensuales — decenas a
unos pocos miles de filas, nunca datasets masivos), así que leer el archivo
completo con `pandas` es barato en la práctica. Lo que la advertencia del
plan busca evitar de verdad —correr el pipeline estadístico completo o la
validación de contrato sobre el archivo— sigue evitado: `leer_columnas_preview()`
no llama a `validar_contrato()` ni a ninguna prueba de `core/etapa1`/`core/etapa2`.
Solo lee cabeceras, muestra un puñado de valores por columna, y cuenta filas.

**Catálogo de errores:**
- Archivo no parseable → `PARSE_ERROR` (ya catalogado, `api-contracts.md`),
  reusado acá como respuesta HTTP 400 en vez de evento SSE — el catálogo no
  ata un código a un transporte específico.
- **Addendum (implementación):** el plan original preveía un código nuevo
  `PARSE_NO_USABLE_COLUMNS` para "archivo sin ninguna columna utilizable".
  Verificado con pandas real (`tests/unit/core/validacion/test_parser.py`):
  para el camino CSV, `pd.read_csv` levanta `EmptyDataError` (subclase de
  `ValueError`) para cualquier contenido vacío o solo-espacios *antes* de
  devolver un `DataFrame` — no existe un contenido que produzca
  `len(df.columns) == 0` sin haber lanzado ya. La guarda quedaría como código
  muerto, así que no se agrega: `PARSE_ERROR` solo, sin un segundo código,
  cubre el 100% de los casos reales de este endpoint.

**El contrato de `/analysis/stream` no cambia** — `columna_x`/`columna_y`
siguen viajando como string; el dropdown de `ConfigPage` solo mejora cómo se
elige ese string, no lo que el backend recibe.

### Criterio de hecho
- `POST /api/v1/analysis/preview-columns` responde
  `{"columnas": [{"nombre", "indice", "muestra"}, ...], "filas": N}` para un
  archivo válido.
- `core/validacion/parser.py::leer_columnas_preview()` no importa nada de
  `core/etapa1`, `core/etapa2` ni `validacion/contract.py`.
- Ningún código nuevo agregado al catálogo — `PARSE_ERROR` cubre el único
  camino de error real de este endpoint (ver addendum arriba).

**Ver también:** [DECISIÓN 038](decision038.md) — regla de sincronización
del catálogo de errores en las tres direcciones.
