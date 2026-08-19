# DECISIÓN 036 — Partición de Cramer personalizada

**Fecha:** 29 de Julio de 2026 — addendum 05/08/2026 (el 500 se cierra, la
funcionalidad sigue sin existir) — **aplicada** 18 de Agosto de 2026 (Bloque
H1 del [plan post-avance](../plan-post-avance.md), opción 1).
**Estado:** Aplicada. Ver "Cerrado (18/08/2026)" más abajo para la
implementación real; el resto del documento queda como diagnóstico
histórico, sin reescribir.

### Addendum (05/08/2026) — Bloque D, Pasada 5: el 500 queda cerrado, no la funcionalidad

`docs/plan-post-pasada4-roadmap.md` (H4) encontró que este `TypeError` no
manejado ya no es solo una limitación conocida del frontend (el botón
"Personalizada" deshabilitado) — es alcanzable por **cualquier cliente HTTP**
que le pegue directo a `POST /api/v1/analysis/stream` con `cramer_particion`
distinto de `"default"`, frontend propio o no, incluido CU-03 el día que
exista.

`backend/metis/api/v1/analysis.py::stream_analysis` ahora valida
`cramer_particion` en el borde, antes de leer el archivo o tocar
`core/`: si no es exactamente `"default"`, responde 400 con el código nuevo
`CONTRACT_CRAMER_PARTICION_UNSUPPORTED` (catalogado en `api-contracts.md` y
`frontend/src/i18n/errors.es.ts`). **Esto no es la opción 1 ni la opción 2
de más abajo** — no se agregó parseo de JSON ni campos `Form` nuevos, solo
una guarda que rechaza cualquier valor no soportado con un error controlado
en vez de un crash. Las tres opciones evaluadas siguen abiertas, ninguna
descartada; sigue pendiente que Kevin/Octavio decidan cuál implementar.

### Contexto
`api-contracts.md` y `statistical-pipeline.md` documentan `cramer_particion` como
`"default" | {n1_pct, n2_pct}`, configurable por el usuario en CU-01/CU-02
(`formulas-etapa1.md` §6, nota de arquitectura: "Aunque el usuario personalice los
tamaños de los bloques (...), el principio de Cramer exige que se extraigan los
últimos datos del registro"). La sesión de implementación de Fase 2 del frontend
(`ConfigPage.tsx`) encontró que el botón "Personalizada" no se podía cablear contra
el backend real y lo dejó `disabled` con un `title` improvisado — sin escalar el
hallazgo a `docs/decisiones/`.

### Diagnóstico confirmado
Verificado directamente contra el código en esta pasada, no solo contra lo que decía
el `title` del botón:

- `backend/metis/api/v1/analysis.py:27` — `cramer_particion: str = Form("default")`.
  Un campo `multipart/form-data` siempre llega como `str` al handler de FastAPI; no
  hay forma de que un objeto JSON llegue tipado como `dict` por esta vía.
- `backend/metis/core/etapa1/homogeneity.py:97-112` — `calcular_cramer(serie,
  particion: dict | str = "default")`. La rama `if particion == "default":` cubre el
  caso por defecto; la rama `else` asume `dict` e indexa `particion["n1_pct"]` /
  `particion["n2_pct"]` directamente.
- Consecuencia: cualquier valor de `cramer_particion` distinto del string literal
  `"default"` entra a la rama `else` como `str` y la indexación `"algo"["n1_pct"]`
  lanza `TypeError: string indices must be integers` — no una respuesta 400
  controlada, un error 500 no manejado.
- `frontend/src/routes/config/ConfigPage.tsx:42` confirma que hoy el frontend nunca
  intenta enviar otra cosa: `cramer_particion: "default"` está hardcodeado en el
  `AnalysisStreamForm`, y el botón "Personalizada" está deshabilitado. No hay ningún
  camino de punta a punta, ni de frontend ni de un cliente HTTP directo, por el que
  la partición personalizada llegue a `calcular_cramer` sin crashear.

### Por qué importa
Contradice tres documentos vigentes a la vez:
- `.claude/rules/architecture/api-contracts.md` — contrato documentado de
  `POST /api/v1/analysis/stream`, campo `cramer_particion`.
- `.claude/rules/core/statistical-pipeline.md` — *"Partición configurable: default =
  últimos 60% y últimos 30%. CU-01/CU-02: usuario configura partición desde la
  interfaz."*
- `.claude/rules/core/formulas-etapa1.md` §6 — nota de arquitectura sobre
  personalización de bloques de Cramer.

### Opciones evaluadas
1. **Recibir `cramer_particion` como JSON string en el `Form` y parsearlo con
   `CramerParticionCustom.model_validate_json()` en la capa `api/`.** Reutiliza el
   modelo Pydantic que ya existe en `schemas/analysis.py` (ver
   [DECISIÓN 037](decision037.md) — ese modelo hoy no lo importa ninguna ruta). No
   requiere cambiar el contrato multipart declarado (`cramer_particion` sigue siendo
   un único campo string desde el punto de vista del cliente HTTP), solo cambia qué
   hace `api/` con el string antes de llamar a `services/`. Riesgo: hay que validar
   explícitamente el JSON malformado con un 400 `CONTRACT`-style, no dejar que
   Pydantic tire un 422 críptico para un campo que hoy es opcional/default.
2. **Recibir dos campos `Form` separados (`cramer_n1_pct`, `cramer_n2_pct`,
   opcionales) y armar el dict en `api/`.** Más simple de validar (dos floats
   opcionales, sin parseo de JSON), pero cambia la forma del contrato documentado en
   `api-contracts.md` (dos campos nuevos en vez de un objeto anidado) — requeriría
   actualizar el contrato, no solo la implementación.
3. **Dejar la partición fija en `"default"` para V1.0 y bajar el requerimiento
   explícitamente.** No requiere tocar `core/` ni `api/`. Bajaría un RF documentado
   sin que quede registrado en ningún lado más que en este archivo, salvo que se
   actualice también `constraints.md`/`sprint.md` con el recorte de alcance.

### Decisión (histórica, 29/07/2026)
**No se implementa ninguna opción en esa pasada** — alcance explícito de
`plan-mejora-frontend-pasada2.md`: los hallazgos de backend de esa pasada se
documentan, no se implementan. Sin una recomendación cerrada entre las tres
opciones — depende de si Kevin/Octavio quieren mantener el contrato anidado
(`opción 1`, más fiel a lo ya documentado) o simplificar el contrato
(`opción 2`). La `opción 3` solo debería tomarse si se decide explícitamente
recortar el alcance de V1.0, no como default por inacción.

Mientras tanto: el botón "Personalizada" sigue deshabilitado en `ConfigPage.tsx`,
pero su `title` deja de decir "rota en el backend actual" (lenguaje de debugging, no
apto para un usuario final) y pasa a referenciar esta decisión.

---

### Cerrado (18/08/2026) — Bloque H1 del plan post-avance: se implementa la opción 1

Kevin decidió: **opción 1**, tal como quedó recomendada en el plan
post-avance — reutiliza el contrato anidado ya documentado
(`"default" | {n1_pct, n2_pct}`) en vez de reabrir el contrato con dos
campos `Form` sueltos (opción 2). La opción 3 (bajar el requerimiento) no
se tomó.

**Implementación real, de punta a punta:**

- `cramer_particion` sigue siendo un único campo `Form(str)` del punto de
  vista del cliente HTTP — el contrato multipart no cambió. Lo que cambió
  es qué hace `api/v1/analysis.py` con ese string: `"default"` pasa tal
  cual; cualquier otro valor se parsea con `json.loads()` y se valida
  contra `CramerParticionCustom` (`schemas/analysis.py`, recreado — se
  había borrado en DECISIÓN 054 como código muerto, ahora sí lo importa una
  ruta real).
- Validación en el borde (`_parsear_cramer_particion()`,
  `api/v1/analysis.py`): `n1_pct`/`n2_pct` entre 1 y 100 (`Field` de
  Pydantic), y `n1_pct > n2_pct` a mano (Pydantic no expresa bien una
  comparación entre dos campos en un solo `Field()` sin un
  `model_validator` aparte — más código que una función normal). JSON
  malformado, forma inválida, fuera de rango, o invertido → 400
  `CONTRACT_CRAMER_PARTICION_INVALID` — reemplaza a
  `CONTRACT_CRAMER_PARTICION_UNSUPPORTED` (retirado, ver
  `api-contracts.md`).
- **`core/etapa1/homogeneity.py::calcular_cramer()` no cambió su firma ni
  su rama `else`** — confirma el diagnóstico original: el bug nunca fue que
  el código de `core/` estuviera mal, fue que la rama que ya sabía indexar
  un `dict` nunca recibía uno. Sí ganó un guard nuevo, fuera del alcance
  del diagnóstico original: si `n_w1 < 2` o `n_w2 < 2` (posible con
  porcentajes chicos sobre una serie corta — algo que solo se puede saber
  después de parsear el archivo, no en el borde del endpoint), la prueba
  responde `no_ejecutada`/`TEST_NOT_EXECUTED_CONDITION` explícitamente. Sin
  este guard, un bloque de 1 dato podía a veces sobrevivir el guard
  incidental de `_cramer_bloque()` (`denom≤0`) y producir un estadístico
  sin sentido estadístico en vez de fallar limpio.
- Frontend: botón "Personalizada" habilitado en `ConfigPage.tsx`. Al
  activarlo, dos campos numéricos (default 60/30, visibles) con la misma
  validación de rango/orden que el backend, mostrada inline antes de
  mandar — mismo patrón que el campo de períodos de retorno en
  `Etapa2RankingView`. Nota de dominio visible en la UI: los dos bloques se
  toman siempre del final del registro, sin importar los porcentajes
  elegidos (`formulas-etapa1.md` §6) — para que un usuario no asuma que
  personalizar los porcentajes también mueve dónde se toman los datos.

### Criterio de hecho
- `tests/unit/api/test_stream_cramer_particion.py` — reescrito: partición
  custom válida ya NO lanza (antes de este bloque, cualquier valor
  no-`"default"` daba 400 sin importar si el JSON era válido); JSON
  malformado, fuera de rango, e `n1_pct ≤ n2_pct` sí dan 400
  `CONTRACT_CRAMER_PARTICION_INVALID`; `"default"` sigue funcionando
  exactamente igual (no regresión).
- `tests/unit/core/etapa1/test_homogeneity.py` — partición con un bloque de
  tamaño 1 da `no_ejecutada`/`TEST_NOT_EXECUTED_CONDITION` (el guard
  nuevo), verificado independiente del guard incidental preexistente.
- `pytest -m "unit or integration"` en verde (334 passed, 1 skipped, +14
  sobre la línea base).
- `scripts/check-error-catalog.sh` — sincronizado en las tres direcciones
  con `CONTRACT_CRAMER_PARTICION_INVALID` nuevo y `_UNSUPPORTED` retirado
  (documentado, no borrado, mismo criterio que `design-events`).

### Criterio de hecho (histórico, 29/07/2026)
- `decision036.md` existe y está indexado en `docs/decisiones/README.md` con
  título/fecha/estado.
- Referenciada desde `.claude/rules/architecture/api-contracts.md` (nota de que el
  contrato documentado no está implementado tal cual para partición personalizada).
- Referenciada desde `frontend/src/routes/config/ConfigPage.tsx` (reemplaza el
  `title` improvisado).

**Ver también:** [DECISIÓN 037](decision037.md) — el modelo Pydantic
`CramerParticionCustom` que la opción 1 reutilizaría ya existía pero no estaba cableado
al endpoint por un motivo relacionado, no idéntico. Ahora sí lo está.
