# DECISIÓN 067 — Colisión de clave en la agregación: se conserva el máximo, no el último
**Fecha:** 28 de Agosto de 2026
**Estado:** Decidida y aplicada (backend)
**Origen:** hallazgo F1 de [`docs/revision-resolucion-diaria.md`](../revision-resolucion-diaria.md),
revisión de código independiente del plan de resolución diaria.

### Contexto

`core/validacion/aggregation.py` quedó, después de [DECISIÓN 065](decision065.md), con **dos
funciones que se llaman "máximos" y resuelven la colisión de clave de forma opuesta**:

```python
# agregar_a_maximos_anuales() — asignaba: ganaba la ÚLTIMA fila del archivo
por_periodo.setdefault(periodo, {})[clave] = float(valor)

# agregar_a_maximos_mensuales() — maximizaba: ganaba la MAYOR
if clave not in por_mes or v > por_mes[clave]:
    por_mes[clave] = v
```

Una colisión de clave son dos filas del archivo que caen en la misma unidad de agregación. El
caso real es un **timestamp duplicado** — y `CONTRACT_DUPLICATE_TIMESTAMPS` es warning **no
bloqueante** (`contract.py`), así que el pipeline llega hasta la agregación con duplicados sin
detenerse. No es un caso hipotético: es un caso que el propio contrato de datos deja pasar a
propósito.

**Reproducido antes de decidir.** Serie diaria de 2001 completa, con el pico real del año
(999,0) el 15/06 y una fila duplicada para esa misma fecha con valor 0,5 al final del archivo:

```
agregar_a_maximos_anuales   -> [1.0]     ← el pico real del año desapareció
agregar_a_maximos_mensuales -> [500.0]   ← correcto sobre el caso equivalente
```

El máximo anual sale mal y **nada lo señala**: la serie tiene la longitud correcta, el año no se
descarta (la completitud no se rompe — es el mismo día, no uno faltante) y el único warning
relacionado, `CONTRACT_DUPLICATE_TIMESTAMPS`, dice que hay duplicados, no que se perdió un pico.
Aguas abajo, Etapa 2 ajusta las 13 distribuciones sobre esa serie y los eventos de diseño
heredan el error sin ningún rastro.

**No es una regresión del plan de resolución diaria.** La asignación directa venía de
[DECISIÓN 057](decision057.md) y el mismo agujero existía para carga mensual desde entonces —
verificado: el test mensual nuevo de esta decisión también falla contra el código anterior. Lo
que cambió es que ahora es **más probable** (las exportaciones largas de limnígrafo repiten
fechas más que 480 filas mensuales) y **visible** (dos funciones del mismo módulo, con la
semántica opuesta a la vista).

### Opciones evaluadas

1. **Arreglar solo `agregar_a_maximos_anuales()`.** Descartada: corrige la instancia y deja la
   causa. Las dos funciones seguirían pudiendo divergir de nuevo en el próximo cambio, que es
   exactamente cómo se llegó acá.
2. **Bloquear ante timestamps duplicados.** Descartada de plano: violaría el principio central
   de `constraints.md` ("METIS detecta y advierte, pero no bloquea") y agregaría una tercera
   excepción real a las dos que hay (`CONTRACT_SERIES_TOO_SHORT`, `CONTRACT_WRONG_ORDER`). Un
   duplicado tiene una resolución razonable y sin ambigüedad — no hace falta detener nada.
3. **Extraer la acumulación a una sola función compartida.** Elegida.

### Decisión

**La acumulación vive en una sola función, `_acumular_maximo()`, que las dos usan.** Ante
colisión de clave se conserva el **mayor**, nunca el último del archivo.

```python
def _acumular_maximo(unidades: dict, clave: tuple, valor) -> None:
    v = float(valor)
    if clave not in unidades or v > unidades[clave]:
        unidades[clave] = v
```

Conservar el mayor es lo único coherente con lo que la función calcula: una serie de **máximos**.
Quedarse con la última fila del archivo hace depender el resultado del orden de escritura del
archivo, que no es un dato del dominio.

**Por qué una función compartida y no dos correcciones.** La causa raíz no era la línea, era que
la regla de acumulación estaba escrita dos veces. Con una sola función no pueden volver a
divergir, y el `git blame` de la regla apunta a un solo lugar.

### Efecto lateral: cambia la razón por la que `_clave_unidad()` lleva el día

El docstring de `_clave_unidad()` justificaba incluir el día en la clave diaria diciendo que sin
él la agregación "se quedaría con el ÚLTIMO día de cada mes (asigna, no maximiza) — un máximo
anual plausible pero incorrecto". **Eso deja de ser cierto con este fix:** colapsar los días de
un mes a una sola clave ahora daría el máximo mensual, y el máximo del período seguiría siendo
correcto.

La razón por la que el día tiene que estar en la clave pasa a ser **la cuenta de completitud**:
sin día, un período diario tendría a lo sumo 12 entradas en vez de 365/366, `cobertura = 12/366`,
y el año entero se descartaría como incompleto. El docstring se corrigió para decir eso, y
conserva el registro de las dos razones — el día era además la segunda línea de defensa del
máximo, y ahora ya no la necesita.

### Criterio de hecho

- `_acumular_maximo()` en `core/validacion/aggregation.py`, usado por
  `agregar_a_maximos_anuales()` **y** `agregar_a_maximos_mensuales()`.
- Tres tests nuevos en `tests/unit/core/validacion/test_aggregation.py`
  (`test_diaria_timestamp_duplicado_conserva_el_maximo_no_el_ultimo`,
  `test_mensual_timestamp_duplicado_conserva_el_maximo_no_el_ultimo`,
  `test_maximos_mensuales_duplicado_conserva_el_maximo`).
  **Verificado que los tres fallan contra el código anterior al fix y pasan contra el nuevo** —
  revirtiendo las dos líneas y volviendo a correrlos, no por inspección.
- **Las 9 series de regresión dan salida byte a byte idéntica** a `origin/staging` antes del fix
  (14.156 bytes, `cmp` limpio): volcado de Etapa 1 completa —contrato, tres niveles, descriptiva,
  las 8 pruebas, warnings, `serie_efectiva`— más Etapa 2 con todas las combinaciones
  distribución/método/status/EEA. Ninguna de las 9 tiene timestamps duplicados, así que el fix no
  las toca — pero eso se verificó, no se asumió.
- Smoke test diario con `docs/series prueba/serie_diaria_40anios.csv` sin cambios: 39 años,
  evento `result_etapa1` de 35,5 KB.
- `ruff check metis/` y `ruff format --check metis/` limpios; `pytest -m "unit or integration"`
  sin fallos nuevos.

**Ver también:** [DECISIÓN 057](decision057.md) (origen de la asignación directa),
[DECISIÓN 065](decision065.md) (donde quedaron las dos funciones con semántica opuesta),
`docs/revision-resolucion-diaria.md` §3 F1 (el hallazgo y su reproducción).
