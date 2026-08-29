# Revisión de código — plan de resolución diaria (R1–R6)

**Fecha:** 28/08/2026
**Alcance revisado:** `45ca826..10652cc` — PRs #77, #78, #79 y la rama `docs/resolucion-diaria-r6-decisiones`.
**Revisor:** sesión de asistencia, a pedido de Kevin. Revisión independiente de quien implementó.

**Veredicto: apto para cerrar.** Implementación fiel al plan, con tres desvíos que **mejoran** el
plan original. Se encontró **un hallazgo real de severidad media** (F1) y tres menores. Los tres
puntos del DoD que `sprint.md` daba por pendientes se verificaron en esta revisión y **pasan**.

> **Estado al 28/08/2026 — cerrado.** F1 y F3 resueltos ([DECISIÓN 067](decisiones/decision067.md)
> y test nuevo), F4 corregido en DECISIÓN 065, F2 con vencimiento fijado en `pendientes-facundo.md`.
> Solo queda F5, que es un comando de housekeeping. Ver §6.

---

## 1. Verificaciones ejecutadas

| Verificación | Resultado |
|---|---|
| `pytest -m unit` | **343 passed**, 1 skipped, 6 failed — los 6 en `tests/unit/auth/test_router_register.py` |
| `pytest tests/unit/core/validacion tests/integration` | **63 passed** |
| `ruff check metis/` | **All checks passed** |
| `ruff format --check metis/` | **66 files already formatted** |
| Catálogo de errores, tres direcciones | **Sincronizado** — `CONTRACT_INCOMPLETE_YEARS_ACCEPTED` presente en backend, `api-contracts.md` (3 menciones) y `errors.es.ts` (1) |
| **DoD: las 9 series de regresión dan idéntico** | **VERIFICADO — salida byte a byte idéntica** |
| **DoD: smoke test con el fixture diario** | **VERIFICADO — 39 años, recorte correcto** |
| **DoD: tamaño real del evento SSE diario** | **VERIFICADO — 35,3 KB** |
| Suite de frontend | **No verificable desde acá** — ver §5 |

### 1.1 Los 6 tests que fallan son ambientales, no una regresión

Fallan con `AttributeError: <fastapi.routing.APIRouter object> does not have the attribute
'send_verification_email'` — colisión de nombre entre el módulo `metis/auth/router.py` y la
variable `router = APIRouter()` que define adentro, sensible al orden de importación y a la
versión de Python.

Verificado que **no los causa este trabajo**: `git diff --stat 45ca826..HEAD -- backend/metis/auth
backend/tests/unit/auth` está **vacío** — la capa `auth/` no se tocó en ninguno de los cuatro PRs.
El entorno de esta revisión corre **Python 3.10.12**; el proyecto targetea **3.11** (`backend/Dockerfile`).
CI corre en el contenedor y no los reporta.

### 1.2 Regresión de las 9 estaciones — método y resultado

Se extrajeron las 9 series de `docs/auditoria/regresion/regresion-unitaria/est_*.md`
(preservando los `None` de los cortes de registro) y se corrieron por `ejecutar_etapa1()` +
`ejecutar_etapa2()` en **dos árboles**: un `git worktree` en la base `45ca826` y el `HEAD` actual.

Se comparó un volcado JSON determinístico con: veredicto de contrato, los tres niveles,
estadística descriptiva completa, `(prueba, estadístico, valor_crítico, veredicto, warning)` de
las 8 pruebas, warnings ordenados, `serie_efectiva`, y `(distribución, método, status, EEA)` de
**todas** las combinaciones de Etapa 2.

**Resultado: `cmp` idéntico, 14.156 bytes en ambos.** El camino anual no se movió un dígito.
Era lo esperado por construcción (el paso 0 no se ejecuta con `resolucion_temporal == "anual"`),
pero ahora está verificado, no argumentado.

### 1.3 Smoke test diario

`docs/series prueba/serie_diaria_40anios.csv` (14.600 filas) por `ejecutar_etapa1()`:

```
resolucion inferida: diaria
bloqueante: False
n serie_efectiva: 39   | años: 1980 … 2018
CONTRACT_PARTIAL_YEARS_TRIMMED -> 1979 (182/366 días), 2019 (174/366 días).
                                  Período efectivo: 1980–2018.
```

**Detalle que confirma que el manejo de bisiestos es correcto y no accidental:** con
`mes_inicio_anio = 7`, el período etiquetado 1979 va de julio 1979 a junio 1980 — y espera **366**
días porque febrero de **1980** es bisiesto, no porque 1979 lo sea. El período 2019 (jul 2019 –
jun 2020) espera 366 por febrero de 2020. Es exactamente el caso que `_esperados()` advierte en su
docstring y que `pd.date_range` resuelve solo. Confirmado en datos reales, no solo en el test
sintético `test_esperados_bisiesto_con_mes_inicio_distinto_de_1`.

### 1.4 Payload — la decisión R3.3 opción 2 funcionó mejor de lo proyectado

Medido sobre `_serializar_etapa1()` con el fixture real:

| | Proyectado en el plan | **Medido** |
|---|---|---|
| `serie_original` (ítems) | ~480 | **480** |
| Bloque `datos` | ~24 KB | **30,9 KB** |
| **Evento `result_etapa1` completo** | — | **35,3 KB** |
| Si se hubiera mandado la serie diaria cruda | ~637 KB | — |

**Reducción de 18×**, y el resultado queda **por debajo** del peor caso mensual que DECISIÓN 058
dimensionó en ~59 KB. La corrección al razonamiento de DECISIÓN 058 quedó cerrada en la dirección
correcta: no se relajó el límite, se evitó el problema.

---

## 2. Los tres desvíos del plan — los tres son mejoras

### 2.1 `_espaciado_regular()` — el plan (R1.2) partía de una premisa equivocada

**R1.2 pedía** agregar una rama `"diaria"` a `_espaciado_regular()` y suprimir
`CONTRACT_IRREGULAR_SPACING` para carga diaria, porque "se dispararía en casi todo registro real".

**La implementación no lo hizo, y tiene razón.** Encontró que `validar_contrato()` tiene un solo
call site en producción y corre **después** del paso 0 — que ya forzó `resolucion_temporal = "anual"`
y reemplazó los timestamps por los años-etiqueta que `agregar_a_maximos_anuales()` construye con
`range()`, ascendentes y equiespaciados por construcción. Es decir: **la rama `"mensual"` de
`_espaciado_regular()` (Bloque F2.2) solo la ejecutan los tests unitarios desde DECISIÓN 057.**
La premisa de R1.2 —que la rama correría sobre timestamps diarios crudos— era falsa.

Es el **mismo patrón exacto** que motivó el Bloque H3 con `CONTRACT_WRONG_ORDER`: un chequeo que
corre después de la agregación es código muerto para toda serie agregada.

Y la decisión de **no arreglarlo acá** también es correcta: mover el chequeo antes del paso 0 haría
que **series mensuales ya auditadas** empiecen a emitir `CONTRACT_IRREGULAR_SPACING` donde hoy no
emiten nada. No cambia ningún estadístico, pero sí la salida visible de análisis ya validados —
merece su propio PR y su propia verificación, no venir colgado de un plan que declara en su §0 que
no toca el camino mensual. Quedó registrado en `docs/pendientes-tecnicos.md` con la remediación.

**Esto es mejor criterio de ingeniería que el que traía el plan.** Vale la pena decirlo explícito.

### 2.2 Regla de cobertura asimétrica — refinamiento de diseño no previsto

El plan proponía un único `cobertura_minima`. La implementación lo partió en dos: **los años de los
extremos siempre exigen 100 %**, solo los interiores admiten umbral (`cobertura_minima_interior`).
Es más fiel a DECISIÓN 057, que descarta extremos parciales sin excepción. Ver F4 más abajo por un
matiz de la justificación escrita.

### 2.3 Rótulos del frontend — alcance agregado, y bien agregado

Ni el plan ni la decisión lo pedían: `Etapa1BoxplotMensualChart` ahora distingue en el subtítulo
*"la distribución de los máximos mensuales agregados desde los datos diarios"* de *"la distribución
de los valores mensuales del registro"*. **Mismo dibujo, otra estadística.** En una herramienta con
enfoque docente eso no es cosmético: sin el rótulo, dos boxplots idénticos significarían cosas
distintas sin que nada lo diga.

---

## 3. Hallazgos

### F1 — MEDIA: colisión de clave, dos funciones del mismo archivo con semántica opuesta

> **RESUELTO 28/08/2026 — [DECISIÓN 067](decisiones/decision067.md).** `_acumular_maximo()`
> compartido por las dos funciones; tres tests nuevos, verificados en rojo contra el código
> anterior; las 9 estaciones siguen dando idéntico. El resto de esta entrada se conserva sin
> tocar como registro de cómo se encontró.

`agregar_a_maximos_anuales()` **sobreescribe** en colisión de clave:

```python
por_periodo.setdefault(periodo, {})[clave] = float(valor)   # asigna: gana el ÚLTIMO
```

mientras `agregar_a_maximos_mensuales()`, **en el mismo archivo**, maximiza:

```python
if clave not in por_mes or v > por_mes[clave]:
    por_mes[clave] = v                                       # gana el MAYOR
```

**Reproducido:** una serie diaria de 2001 completa con un pico de 999 el 15/06 y una fila duplicada
para esa misma fecha con valor 0,5 al final del archivo →

```
agregar_a_maximos_anuales  -> [1.0]     ← el pico real desapareció
agregar_a_maximos_mensuales -> [500.0]  ← correcto sobre el caso equivalente
```

**Encuadre honesto:** *no es una regresión de este trabajo* — la línea era `= ` desde DECISIÓN 057
y el mismo agujero existe para mensual. Pero tres cosas lo vuelven accionable ahora:

1. Los timestamps duplicados son un warning **no bloqueante** (`CONTRACT_DUPLICATE_TIMESTAMPS`), así
   que el pipeline continúa y el máximo anual sale mal **sin nada que lo señale**.
2. Es bastante más probable con carga diaria (exportaciones largas de limnígrafo repiten fechas)
   que con 480 filas mensuales.
3. El docstring de `_clave_unidad()` ya advierte *"asigna, no maximiza"* sobre el riesgo de la clave
   equivocada — el razonamiento correcto está escrito, a un paso de notar que aplica igual a la
   clave duplicada.

**Fix sugerido (una línea, en `agregar_a_maximos_anuales()`):**

```python
clave = _clave_unidad(fecha, resolucion)
v = float(valor)
d = por_periodo.setdefault(periodo, {})
if clave not in d or v > d[clave]:
    d[clave] = v
```

Con test: serie con timestamp duplicado donde el duplicado posterior es menor que el pico real.
**Ojo:** cambia la salida de series mensuales con duplicados — verificar contra las 9 estaciones
antes de mergear (ninguna los tiene, así que debería ser inocuo, pero hay que confirmarlo).

### F2 — BAJA: ~40 líneas inalcanzables en producción, con fecha de vencimiento sin fijar

> **ATENDIDO 28/08/2026 — vencimiento fijado.** `pendientes-facundo.md`, R0.1, ahora explicita
> qué hacer con esas 40 líneas según cada respuesta posible: bajar la constante si hay umbral,
> **borrarlas y retirar el código de error del catálogo** si la respuesta es estricto. Queda
> abierto lo que depende de Facundo, no lo que dependía de nosotros.

`PeriodoAceptadoConHueco`, `AgregacionResult.periodos_incompletos_aceptados`, la rama que lo puebla,
el warning `CONTRACT_INCOMPLETE_YEARS_ACCEPTED` y su string de i18n **no se ejecutan nunca hoy**:
`COBERTURA_MINIMA_INTERIOR` está en `1.0` para las dos resoluciones.

Está **bien documentado** (los docstrings lo dicen: *"con el valor provisorio 1.0 esta lista siempre
está vacía"*) y **bien testeado** (tres tests que voltean el umbral), así que es defendible como
"cableado esperando a Facundo" y flipear la constante es un cambio de una línea.

El riesgo no es hoy, es dentro de seis meses: **si R0.1 vuelve con "estricto, sin umbral", esto
tiene que borrarse, no quedarse para siempre.** Sugerencia: dejarlo escrito así de explícito en
`pendientes-facundo.md`, junto a la pregunta.

### F3 — BAJA: falta un test de la lista del plan

> **RESUELTO 28/08/2026.** `test_carga_diaria_el_recorte_deja_n_menor_a_10_y_bloquea` en
> `tests/unit/core/pipeline/test_pipeline_etapa1.py`. Con esto la lista de R5 queda completa.

El plan pedía *"el recorte deja n < 10 → `CONTRACT_SERIES_TOO_SHORT`"*. Existe para mensual
(`test_pipeline_etapa1.py:310-323`) pero **no para diaria**. La lógica es agnóstica a la resolución
(ocurre en `validar_contrato()`, después del paso 0), así que el riesgo real es bajo — pero es el
único ítem de la lista de R5 que no quedó cubierto.

### F4 — INFO: la justificación escrita de la asimetría no es la más fuerte disponible

> **RESUELTO 28/08/2026.** DECISIÓN 065 lleva ahora una precisión agregada (no reemplaza el
> párrafo original, lo complementa) con el argumento epistémico. Código sin cambios.

El docstring justifica que los extremos exijan 100 % con *"en un extremo la parcialidad es la
regla"*. Eso es un argumento de **frecuencia**, y no distingue los dos casos: el sesgo a la baja del
máximo de un año incompleto es **idéntico** en un extremo y en el interior.

El argumento que sí distingue es **epistémico**: en un extremo, los datos que faltan **no existen**
— el registro empieza o termina ahí, la parcialidad es un borde de los datos disponibles. En el
interior, los datos **existían y no se registraron** — hay una crecida que pudo haber ocurrido y no
quedó medida. Aceptar un interior al 95 % es apostar a que el pico cayó en el 95 % observado;
"aceptar" un extremo al 95 % no tiene ni siquiera esa apuesta que hacer, porque no hay un año
completo del cual falte una parte.

No cambia una línea de código. **Sí conviene corregirlo en DECISIÓN 065 antes de la defensa** — es
exactamente el tipo de asimetría que un tribunal pregunta, y la respuesta actual es más débil que la
que el diseño merece.

### F5 — Housekeeping: worktrees fantasma

`git worktree list` reporta tres entradas prunables: `pasada5-cierre` y
`frontend-pasada5-bloque-f` (preexistentes, de trabajo anterior) y `metis-base` (creada por esta
revisión para la comparación de §1.2). No se pudieron borrar desde acá — los metadatos viven en
`.git/worktrees/` y el montaje no tiene permiso de borrado sobre esa ruta.

**Correr desde Windows:** `git worktree prune` — limpia las tres de una.

> **Pendiente 28/08/2026** — sigue sin poder ejecutarse desde el entorno de revisión (los
> metadatos viven en `.git/worktrees/` y el montaje no tiene permiso de borrado). Es un
> comando, no un cambio de código.

---

## 4. Calidad general del código

Lo que se sostiene bien:

- **La estrategia de defaults es la decisión de diseño acertada del PR 2.** `resolucion="mensual"`,
  `cobertura_minima_interior=1.0` hacen que el camino mensual auditado no cambie, y convierten a los
  tests mensuales preexistentes en la prueba de no-regresión sin escribir uno nuevo. Es exactamente
  lo que el plan pedía y se cumplió al pie de la letra — la verificación de §1.2 lo confirma.
- **Los comentarios explican por qué, no qué.** El de `_calcular_serie_calendario()` sobre por qué
  `resolucion=` es obligatorio describe un bug que *no ocurrió* y cómo se habría visto ("silencioso,
  plausible y equivocado"). Ese es el comentario que evita que alguien lo rompa en seis meses.
- **`_motivo_descarte()` extraído** — la cadena if/elif/else quedó como función nombrada y testeable.
- **Trazabilidad intacta.** Cada bloque de código referencia su sección del plan (R2.3, R3.3, R3.4) y
  su decisión. Un lector puede ir del código a la justificación sin preguntar.
- **Los tests apuntan a las trampas, no a la línea feliz.**
  `test_diaria_el_maximo_anual_no_es_el_ultimo_dia_del_mes` es el test del bug de `_clave_unidad`
  antes de que existiera; `test_esperados_bisiesto_con_mes_inicio_distinto_de_1` cubre el borde de
  calendario que §1.3 confirmó en datos reales; los tres tests de asimetría cubren código que hoy no
  corre en producción.
- **`_sse_helpers.py`** — la deduplicación de los helpers de integración se hizo en un commit propio
  (`bd29e2d`), separada del cambio funcional. Correcto.

Lo único que no me convence del todo es F2: el código inalcanzable está bien argumentado, pero
depende de una respuesta externa sin fecha, y esas cosas se vuelven permanentes por olvido.

---

## 5. Lo que esta revisión NO pudo verificar

- **Suite de frontend** (`npm test`, `lint`, `build`). `frontend/node_modules` está instalado con
  binarios nativos de Windows (`rollup`), y este entorno de revisión es Linux — `vitest` no arranca.
  Los cuatro jobs de `ci.yml` sí lo cubren; el PR #79 está mergeado, así que pasó.
- **Verificación en navegador** del PR #79 (rótulos nuevos del boxplot y de la serie temporal). El
  DoD del repo la exige para todo PR que toque `frontend/`. **Confirmar que se hizo.**
- **`scripts/check-error-catalog.sh`** no corrió (`set: pipefail: invalid option name` en este
  shell). Se verificó **a mano** en las tres direcciones — resultado en la tabla de §1.
- El pipeline completo contra el backend real vía HTTP/SSE (no hay Docker en este entorno).

---

## Anexo — comandos de reproducción

```bash
# regresión de las 9 estaciones (§1.2)
git worktree add /tmp/metis-base 45ca826
python /tmp/regres.py <ruta>/backend > /tmp/head.json
python /tmp/regres.py /tmp/metis-base/backend > /tmp/base.json
cmp /tmp/base.json /tmp/head.json          # → idénticos, 14156 bytes

# smoke test diario (§1.3) y payload (§1.4)
python -c "... ejecutar_etapa1(...) ; _serializar_etapa1(...)"
```


---

## 6. Cierre de la revisión — 28/08/2026

| Hallazgo | Severidad | Estado |
|---|---|---|
| F1 — colisión de clave: se conservaba el último, no el máximo | Media | **Resuelto** — [DECISIÓN 067](decisiones/decision067.md), `_acumular_maximo()` compartido + 3 tests |
| F2 — ~40 líneas inalcanzables con los umbrales en `1.0` | Baja | **Atendido** — vencimiento explícito en `pendientes-facundo.md` R0.1; el cierre depende de Facundo |
| F3 — faltaba el test de `n < 10` con carga diaria | Baja | **Resuelto** — `test_carga_diaria_el_recorte_deja_n_menor_a_10_y_bloquea` |
| F4 — justificación de la asimetría más débil que el diseño | Info | **Resuelto** — precisión agregada a DECISIÓN 065 (epistémica, no de frecuencia) |
| F5 — worktrees fantasma | Housekeeping | **Abierto** — `git worktree prune` desde Windows |

**Verificación posterior al fix de F1**, sobre `origin/staging` (que ya incluye el PR 2.5 de
`variable_diaria`):

- Los 3 tests de duplicado **fallan contra el código anterior y pasan contra el nuevo** —
  comprobado revirtiendo las dos líneas y volviendo a correrlos, no por inspección.
- **Las 9 series de regresión: `cmp` limpio, 14.156 bytes**, idénticas a `origin/staging` antes
  del fix (y al baseline `45ca826` de §1.2 — la cadena completa cierra transitivamente).
- Smoke test diario sin cambios: 39 años; evento `result_etapa1` de **35,5 KB** (los 0,2 KB de
  más respecto de §1.4 son el warning `CONTRACT_DAILY_SERIES_AGGREGATED` que agregó el PR 2.5).
- `pytest -m "unit or integration"`: **367 passed**, 1 skipped, los mismos 6 fallos ambientales
  de `auth/` explicados en §1.1.
- `ruff check metis/` y `ruff format --check metis/` limpios.

**Sigue sin verificarse desde acá** lo mismo que §5: la suite de frontend (`node_modules` con
binarios de Windows) y la evidencia de navegador. El fix de F1 es backend puro y no toca ningún
contrato de payload, así que no altera nada del frontend — pero los cuatro jobs de `ci.yml`
siguen siendo el criterio, no esta revisión.

**Una observación fuera del alcance de esta revisión:** el PR 2.5 (`variable_diaria`,
`CONTRACT_DAILY_SERIES_AGGREGATED`) no dejó decisión numerada ni addendum a DECISIÓN 065 — tocó
`api-contracts.md` pero nada en `docs/decisiones/`. Es una decisión de producto real (un campo
nuevo del request, persistido, que cambia el texto que ve el usuario y declara un sesgo del
dominio), del mismo tamaño que otras que sí tienen número. Conviene cerrarlo antes de la defensa,
por la misma regla de trazabilidad que rige el resto del proyecto.
