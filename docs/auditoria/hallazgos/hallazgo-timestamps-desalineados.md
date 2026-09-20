# Hallazgo — `timestamps_efectivos` desalineado de `serie_efectiva` en cargas anuales con celda vacía

**Fecha:** 20/09/2026 · **Tipo:** verificación de una hipótesis (NO es un arreglo) ·
**Origen de la hipótesis:** Kevin · **Verificación:** Claude Code sobre este repo, con salida real
(core directo + API real levantada en Docker). No se modificó ningún archivo de `backend/` ni de
`frontend/`; los únicos artefactos creados son los dos scripts de prueba (en `/tmp` dentro del
contenedor, pegados completos al final) y este informe.

---

## Veredicto: **CONFIRMADO**

En una carga **anual** con una celda de valor vacía, `ejecutar_etapa1()` devuelve `serie_efectiva`
con un elemento menos que `timestamps_efectivos` (14 vs. 15 en el caso de prueba), y esa
desalineación llega intacta al payload SSE `result_etapa1` de la API real, hace que el rechazo de
un atípico de Chow borre el valor correcto con el año equivocado, y desplaza un año todas las
etiquetas posteriores al faltante. Los tres puntos de la hipótesis se reprodujeron, con un matiz
en el tercero (ver abajo). El contraste sin celda vacía da largos iguales y el atípico en 2000, lo
que atribuye el desvío al faltante y no a otra cosa.

| # | Consecuencia | Resultado |
|---|--------------|-----------|
| 1 | Desalineación de etiquetas al aparear por posición | **Verificada** (core y API real) |
| 2 | El rechazo de Chow borra el VALOR correcto pero el AÑO equivocado | **Verificada** (borra 900 y el año 1999, no 2000) |
| 3 | La 2ª pasada emite `CONTRACT_IRREGULAR_SPACING` por un año que no es el que se quitó | **Verificada con matiz**: el código de warning también sale en el control (por diseño); lo que cambia es *dónde* queda el hueco: 1998→2000 en vez de 1999→2001. Ver punto 3 |

---

## Cómo se detectó

Por lectura de código, no por un síntoma en pantalla:

- `backend/metis/core/pipeline/pipeline_etapa1.py:338-339` (camino normal) y `:265-266`, `:215-216`
  (los dos retornos bloqueantes) construyen `serie_efectiva=filtrar_numericos(serie)` junto con
  `timestamps_efectivos=timestamps`, es decir: la serie sale filtrada y los timestamps salen como
  llegaron.
- `backend/metis/core/validacion/parser.py:55-60` conserva los `None` **a propósito**
  (`# Preservar None — validar_contrato() detecta CONTRACT_MISSING_VALUES`), tanto en la serie como
  en los timestamps.
- `backend/metis/services/analysis_service.py:606-622` filtra `timestamps_efectivos` con el mismo
  índice que borra de `serie_efectiva`, bajo un comentario que asume que ambas listas están
  "alineadas 1:1 … (misma construcción en ejecutar_etapa1())" (hallazgo V2, 14/08/2026). Esa
  premisa solo vale si la serie no tuvo `None`.
- `Etapa1SerieTemporalChart.tsx:40` y `Etapa1ChowChart.tsx:44-52` aparean `serie_efectiva[i]` con
  `timestamps[i]` por posición.

`grep` sobre `backend/tests` no encontró ningún test de una serie anual con `None` que verifique el
largo de `timestamps_efectivos`; los tests existentes de alineación cubren series completas
(`test_pipeline_etapa1.py:287`, `test_serializar_etapa1.py:57`) y carga mensual/diaria
(`test_stream_agregacion_*.py`).

## Cómo se reprodujo — comandos exactos

El stack ya estaba levantado (`docker ps`: `pi_metis-backend-1`, `pi_metis-postgres-1`,
`pi_metis-frontend-1`, `pi_metis-nginx-1`, Up); no corrí `docker-compose up` ni `alembic upgrade
head` (la tabla `analyses` ya existía). Desde Git Bash en Windows hace falta
`MSYS_NO_PATHCONV=1`, si no reescribe `/tmp` a una ruta de Windows.

```bash
export MSYS_NO_PATHCONV=1
docker ps --format '{{.Names}} {{.Status}}'

# Nivel 1 — core directo (script pegado en el apéndice A)
docker exec -i pi_metis-backend-1 sh -c 'cat > /tmp/verif_nivel1.py' < verif_nivel1.py
docker exec -e PYTHONPATH=/app pi_metis-backend-1 python /tmp/verif_nivel1.py

# Nivel 2 — API real, CU-02 anónimo (script pegado en el apéndice B)
docker exec -i pi_metis-backend-1 sh -c 'cat > /tmp/verif_nivel2.py' < verif_nivel2.py
docker exec -e PYTHONPATH=/app pi_metis-backend-1 python /tmp/verif_nivel2.py

# Persistencia — SQL de solo lectura contra la BD local (ver "Análisis ya persistidos")
docker exec pi_metis-postgres-1 sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "<consulta>"'
```

Nivel 2 usa `httpx` desde dentro del contenedor contra `http://localhost:8000/api/v1/analysis`:
`POST /stream` (multipart, `etapas=1`, sin JWT) → al llegar `outlier_detected` toma el `session_id`
→ `POST /outlier-decision`. Casos corridos:

| Caso | Carga | Decisión ante Chow |
|------|-------|--------------------|
| A | anual, celda vacía en 1993, atípico 900 en 2000 | `rechazar` (lo pedido) |
| B | **contraste**: anual, 125 en 1993 en vez de celda vacía | `rechazar` |
| C | opcional: mensual 2000-2014, celda vacía en 2005-03, pico 900 en 2010-06, `mes_inicio_anio=1` | `rechazar` |
| D | como A | `aceptar` (agregado: en esta ruta el `result_etapa1` final es el de la 1ª pasada) |
| E | como B | `aceptar` |

Se agregaron D y E porque en la ruta "rechazar" el atípico ya no figura en el payload final
(`datos.indice_atipico = null`), y la ruta "aceptar" es la que muestra el desfase sobre el gráfico
de Chow.

Datos: años 1990-2004; valores `[120, 135, 110, None, 128, 140, 115, 125, 132, 118, 900, 122, 130,
127, 119]`, es decir 1993 vacío y 900 en el año **2000** (posición 10 de la lista original).

---

## Punto por punto

### 1. Desalineación de etiquetas — VERIFICADA

- Core (Nivel 1, caso A): `len(serie_efectiva)=14`, `len(timestamps_efectivos)=15`.
- API real (Nivel 2, casos A y D): mismo largo desigual en el evento `result_etapa1`
  (`13 vs 14` tras rechazar; `14 vs 15` tras aceptar). El frontend recibe listas de largo distinto.
- Apareadas por posición, **todo valor posterior al faltante queda un año antes**, y el último año
  (2004) queda sin par (el `.map` sobre `serie_efectiva` lo descarta en silencio):

| Año real en el archivo | Valor | Etiqueta al aparear por posición (ruta `aceptar`) | Etiqueta (ruta `rechazar`) |
|---|---|---|---|
| 1990 | 120 | 1990 ✔ | 1990 ✔ |
| 1991 | 135 | 1991 ✔ | 1991 ✔ |
| 1992 | 110 | 1992 ✔ | 1992 ✔ |
| **1993** | *(vacío)* | — el año faltante no aparece como hueco | — |
| 1994 | 128 | **1993** ✘ | **1993** ✘ |
| 1995 | 140 | **1994** ✘ | **1994** ✘ |
| 1996 | 115 | **1995** ✘ | **1995** ✘ |
| 1997 | 125 | **1996** ✘ | **1996** ✘ |
| 1998 | 132 | **1997** ✘ | **1997** ✘ |
| 1999 | 118 | **1998** ✘ | **1998** ✘ |
| **2000** | **900** | **1999** ✘ | *(borrado)* |
| 2001 | 122 | **2000** ✘ | **2000** ✘ |
| 2002 | 130 | **2001** ✘ | **2001** ✘ |
| 2003 | 127 | **2002** ✘ | **2002** ✘ |
| 2004 | 119 | **2003** ✘ | **2003** ✘ |

  11 de 14 valores mal etiquetados en la ruta `aceptar`; 10 de 13 en la ruta `rechazar`. Solo los
  tres anteriores al faltante quedan bien.
- El 900 queda etiquetado **1999** (real: 2000) y `datos.indice_atipico = 9` apunta a esa
  etiqueta (Nivel 2, caso D; Nivel 1, sección B2).
- Contraste (casos B y E): largos `15 = 15` (o `14 = 14` tras rechazar), 900 en **2000**,
  `indice_atipico = 10`.

### 2. El rechazo borra el valor correcto y el año equivocado — VERIFICADA

Emulación literal de `analysis_service.py:598-638` (Nivel 1, caso A):

- `indice_atipico = 9`, `indice_real = 9` (`_mapear_indice_a_serie_original(9, serie_efectiva)` es
  la identidad porque `serie_efectiva` ya está filtrada).
- **Valor borrado: 900.0** (correcto). **Año borrado de `timestamps_efectivos`: 1999**
  (`timestamps_efectivos[9]`) — el año real del atípico es 2000, y el año realmente ausente del
  archivo (1993) sigue dentro de los timestamps como si tuviera dato.
- Largos resultantes: `serie_filtrada = 13`, `timestamps_filtrados = 14`: la 2ª pasada arranca ya
  desalineada.
- En el contraste (caso B) el mismo código borra 900 y el año **2000**, y los largos quedan
  `14 = 14`.

### 3. `CONTRACT_IRREGULAR_SPACING` en la 2ª pasada — VERIFICADA CON MATIZ

- 2ª pasada del caso A: emite `CONTRACT_IRREGULAR_SPACING`, con el hueco en
  **(1998 → 2000)**, es decir, falta 1999. Ese año tiene dato real (118); el año quitado fue 2000 y
  el año realmente vacío del archivo (1993) nunca se marca como hueco en ninguna de las dos
  pasadas.
- **Matiz importante:** el mismo código de warning también sale en el control B (hueco
  **(1999 → 2001)**, el correcto), porque quitar un atípico de una serie de años consecutivos abre
  un hueco por diseño. Por lo tanto la *presencia* del warning no distingue el caso roto del sano;
  lo que difiere es el año del hueco, y el texto del warning (`"Espaciado temporal irregular
  detectado"`) no nombra ningún año — el usuario no puede ver la diferencia en el warning, solo en
  el eje del gráfico.
- El evento `contract_warning` de la iteración 2 del caso A (API real) trae
  `CONTRACT_IRREGULAR_SPACING` igual que en el core.

---

## Alcance real: qué queda mal y qué queda bien

**Queda mal (verificado):**

- Las **etiquetas de año** de `Etapa1SerieTemporalChart` y `Etapa1ChowChart`: desplazadas un año
  hacia atrás desde el faltante en adelante, con el último año sin par; el hueco real (1993) no se
  ve y aparece un hueco falso donde se rechazó el atípico.
- El **año que se descarta** al rechazar un atípico (1999 en vez de 2000) en `timestamps_efectivos`
  del resultado final.
- El **contenido del warning** de espaciado, en cuanto a *qué* hueco describe (aunque su texto no
  lo nombra).
- El payload `result_etapa1` en sí: `datos.serie_efectiva` y `datos.timestamps_efectivos` viajan
  con largo distinto (contradice el supuesto "1:1" del comentario en `analysis_service.py:606`).

**Queda bien (verificado con salida real):**

- **Los estadísticos, valores críticos y veredictos de las 8 pruebas de Etapa 1, los niveles de
  independencia/homogeneidad/confianza** (Nivel 1, sección C: comparación de la corrida con el
  faltante contra una corrida con serie y timestamps alineados — resultados idénticos en las 8
  pruebas). Es esperable por construcción: las pruebas consumen `valores_numericos`, nunca los
  timestamps (`pipeline_etapa1.py:273-309`); la comparación lo confirma con números.
- El **valor** que se borra al rechazar el atípico (900, correcto).
- El **ranking de Etapa 2**: `ejecutar_etapa2(serie: np.ndarray, tiene_ceros)` no recibe
  timestamps. **Ojo con lo que prueba mi corrida**: la comparación de la sección C usa dos
  `serie_efectiva` que resultan ser la misma lista, así que la igualdad del ranking es trivial. La
  evidencia real es estructural — la firma de la función y la llamada
  (`analysis_service.py`, `ejecutar_etapa2(serie_np, …)`) — y no encontré ningún camino por el que
  los timestamps entren al ajuste.
- **Carga mensual con faltante (caso C): protegida.** La agregación arma valores y timestamps
  juntos; el año 2005 (una celda vacía) se descarta completo con
  `CONTRACT_INCOMPLETE_YEARS_DISCARDED`, `serie_efectiva` y `timestamps_efectivos` salen ambos de
  largo 13 y el rechazo del 900 borra el año 2010 correctamente (la 1ª pasada ya emite
  `CONTRACT_IRREGULAR_SPACING` por el hueco de 2005, esperable al descartar un año interior). Es coherente con la lectura de que
  el defecto es propio de la carga anual. **Carga diaria no probada.**
- La serie cruda subida (`serie_original`/`timestamps_originales`, y `analyses.serie`/
  `analyses.timestamps` en BD): se arma con las listas originales completas, alineadas entre sí.
  Es lo que permitiría reconstruir el análisis. (Por lectura de `_persistir()`, no por corrida
  CU-01, ver siguiente sección.)

En resumen: **solo se ve afectada la presentación por año y el registro de qué año se descartó;
los números de Etapa 1 y Etapa 2 no cambian.**

## ¿Toca análisis ya persistidos en el historial?

**Sí, por construcción, para cualquier análisis anual con celda vacía guardado hasta hoy.**
`stream_analysis()` llama `_persistir(..., result=result_final)` (`analysis_service.py:818-829`), y
`_persistir()` guarda `etapa1=_serializar_etapa1(result, mes_inicio_anio)` (`:900`), el mismo
payload que se emitió. Por lo tanto `analysis_results.etapa1.datos.serie_efectiva` y
`.timestamps_efectivos` quedan guardados con largo distinto, y `HistoryDetailPage` reusa los mismos
gráficos. Demostración con el serializador real en el Nivel 1, sección B2:

```
1ª pasada (ruta 'aceptar'): len(serie_efectiva)=14 len(timestamps_efectivos)=15 indice_atipico=9
   valor en indice_atipico=900.0  timestamp en ese índice={'iso': '1999-01-01', 'anio': 1999}
2ª pasada (ruta 'rechazar'): len(serie_efectiva)=13 len(timestamps_efectivos)=14 indice_atipico=None
```

Lo que **no** se ve afectado es la entrada auditada: `analyses.serie`/`analyses.timestamps`
guardan lo subido, alineado (por lectura de código; no corrí un flujo CU-01, para no escribir filas
en la BD).

**En la BD local hoy no hay ningún análisis afectado.** Consulta de solo lectura ejecutada:

```
select a.id, a.created_at, jsonb_array_length(a.serie) as n_serie_cruda,
       jsonb_array_length(a.timestamps) as n_ts_crudos,
       jsonb_array_length(r.etapa1->'datos'->'serie_efectiva') as n_serie_ef,
       jsonb_array_length(r.etapa1->'datos'->'timestamps_efectivos') as n_ts_ef,
       a.configuracion->>'nombre_archivo' as archivo
from analyses a join analysis_results r on r.analysis_id=a.id order by a.created_at;

                  id                  |         created_at         | n_serie_cruda | n_ts_crudos | n_serie_ef | n_ts_ef |            archivo
--------------------------------------+----------------------------+---------------+-------------+------------+---------+-------------------------------
 43eb02a1-051a-493a-af9d-7b05ed1a301c | 2026-09-20 15:07:59.17034  |           304 |         304 |         25 |      25 | UCC-DAT-ESR-AH-001-26-00.xlsx
 56bd0a8e-6c51-4736-a86c-beb6f6cbfe2f | 2026-09-20 15:44:56.852189 |           304 |         304 |         25 |      25 | UCC-DAT-ESR-AH-001-26-00.xlsx
 b5e6dcac-0b6a-4028-a688-d96f8958c238 | 2026-09-20 15:45:05.369901 |            40 |          40 |         39 |      39 | serie_con_atipico.csv
(3 rows)
```

Las 3 filas son de hoy y tienen `n_serie_ef = n_ts_ef`. Esto no dice nada de otras bases (staging,
producción de la UCC): para detectar afectados en cualquier base basta comparar
`jsonb_array_length` de ambos campos y ver dónde difieren. **Limitación de esa consulta:** solo
detecta la desalineación cuando hay *largos distintos*, que es exactamente el síntoma de este
defecto en una carga anual.

## Hallazgos secundarios (anotados, sin investigar a fondo)

1. **Una sola celda vacía dispara dos warnings por el mismo dato:** `CONTRACT_NON_NUMERIC_VALUES`
   ("1 valor(es) no numérico(s) detectado(s)") **y** `CONTRACT_MISSING_VALUES` ("1 valor(es)
   faltante(s) o celda(s) vacía(s)"). Visible en la 1ª pasada de los casos A y D (Nivel 1, Nivel 2).
2. **`CONTRACT_IRREGULAR_SPACING` sale siempre tras rechazar un atípico en una serie anual sana**
   (control B): por diseño abre un hueco. Como el texto no nombra el año, el warning no aporta
   información en ese flujo.
3. **`_mapear_indice_a_serie_original(indice, serie_efectiva)` es hoy la identidad** en el rechazo
   de atípico: `serie_efectiva` ya está filtrada, mientras que el docstring del helper describe su
   uso sobre `serie_original` con `None` intercalados.
4. **`Etapa1ChowChart.tsx:45` / `Etapa1SerieTemporalChart.tsx:40`** usan `timestamps[i]?.anio ?? 0`:
   si algún día los timestamps quedaran más cortos que la serie, el año caería a `0` en silencio.
   En este defecto los timestamps son *más largos*, así que ese camino no se ejerció.
5. **`CONTRACT_LENGTH_WARNING` cuenta valores numéricos** (14 en el caso A aunque el archivo tiene
   15 filas). Coherente con el resto del pipeline; solo se anota para no confundir al comparar
   contra `len(timestamps)`.
6. **Timestamps con `None` (celda vacía en la columna de fecha/año, no en la de valor):** el parser
   también los conserva (`parser.py:57-60`). No se probó qué ocurre.

## Qué no se verificó

- Carga diaria con dato faltante.
- Un flujo CU-01 completo (JWT + persistencia + `GET /history/{id}` + render en `HistoryDetailPage`):
  la conclusión sobre el historial sale de leer `_persistir()` y de reproducir la serialización con
  la función real, no de guardar y releer una fila.
- El render real de los gráficos en el navegador. Las etiquetas erróneas se derivan de aparear las
  listas del payload real tal como lo hacen las líneas citadas del frontend; no abrí la UI.
- Timestamps con `None` (ver hallazgo secundario 6) y series anuales con más de una celda vacía
  (el desfase se acumula por construcción, pero no se probó).

---

## Salida cruda

Salida completa y sin editar de cada script, tal como la produjo el contenedor `pi_metis-backend-1` el 20/09/2026. Los `session_id` cambian entre corridas. Los JSON completos de `result_etapa1` de cada caso quedaron en `/tmp/e2e_<caso>_result_etapa1.json` dentro del contenedor (no se copiaron al repo); acá va lo que el script imprime de ellos: `datos`, warnings, niveles y las 8 pruebas.

### Nivel 1 — core directo (`verif_nivel1.py`)

```text
##############################################################################
# A) CON celda vacía en 1993 (hipótesis)
##############################################################################
==============================================================================
CASO: anual, celda vacía en 1993, atípico 900 en 2000
==============================================================================
contract.bloqueante=False nivel_confianza=con_warnings
len(serie_efectiva)=14  len(timestamps_efectivos)=15  IGUALES=False
serie_efectiva      = [120.0, 135.0, 110.0, 128.0, 140.0, 115.0, 125.0, 132.0, 118.0, 900.0, 122.0, 130.0, 127.0, 119.0]
timestamps_efectivos= [1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004]
--- pares (año, valor) apareados POR POSICIÓN (lo que hacen los gráficos) ---
   1990: 120.0
   1991: 135.0
   1992: 110.0
   1993: 128.0
   1994: 140.0
   1995: 115.0
   1996: 125.0
   1997: 132.0
   1998: 118.0
   1999: 900.0
   2000: 122.0
   2001: 130.0
   2002: 127.0
   2003: 119.0
   (elementos de timestamps_efectivos sin par: [2004])
Chow: veredicto=rechazada warning=TEST_WARNING_OUTLIER_DETECTED indice_atipico=9 valor_atipico=900.0
El 900.0 queda etiquetado por posición con el año: 1999  (año real en el archivo: 2000)  DESALINEADO=True
warnings 1ª pasada:
   CONTRACT_LENGTH_WARNING :: Serie con 14 datos — resultados no certificables
   CONTRACT_NON_NUMERIC_VALUES :: 1 valor(es) no numérico(s) detectado(s)
   CONTRACT_MISSING_VALUES :: 1 valor(es) faltante(s) o celda(s) vacía(s)
   TEST_WARNING_SMALL_SAMPLE :: Wald-Wolfowitz ejecutado con n ≤ 40 — aproximación normal menos precisa
   TEST_WARNING_HOMOGENEITY :: Cramer aprobó homogeneidad, pero Helmert o t de Student rechazaron
   TEST_WARNING_OUTLIER_DETECTED :: Chow detectó un dato atípico — decisión pendiente del usuario
------------------------------------------------------------------------------
EMULACIÓN DEL RECHAZO DE ATÍPICO (analysis_service.py:598-638)
------------------------------------------------------------------------------
indice_atipico (Chow)=9  indice_real (mapeado)=9
VALOR borrado de la serie: 900.0
AÑO borrado de timestamps: 1999   (año real del atípico: 2000; año del faltante: 1993)
len(serie_filtrada)=13  len(timestamps_filtrados)=14
timestamps_filtrados = [1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 2000, 2001, 2002, 2003, 2004]
saltos (a->b con b-a != 1) en timestamps_filtrados: [(1998, 2000)]
2ª pasada: bloqueante=False nivel_confianza=con_warnings
2ª pasada: len(serie_efectiva)=13 len(timestamps_efectivos)=14
warnings 2ª pasada:
   CONTRACT_LENGTH_WARNING :: Serie con 13 datos — resultados no certificables
   CONTRACT_IRREGULAR_SPACING :: Espaciado temporal irregular detectado
   TEST_WARNING_SMALL_SAMPLE :: Wald-Wolfowitz ejecutado con n ≤ 40 — aproximación normal menos precisa
   TEST_WARNING_HOMOGENEITY :: Cramer aprobó homogeneidad, pero Helmert o t de Student rechazaron
Chow 2ª pasada: aprobada None

##############################################################################
# B) CONTRASTE: SIN celda vacía (125 en 1993)
##############################################################################
==============================================================================
CASO: anual, SIN celda vacía, atípico 900 en 2000
==============================================================================
contract.bloqueante=False nivel_confianza=con_warnings
len(serie_efectiva)=15  len(timestamps_efectivos)=15  IGUALES=True
serie_efectiva      = [120.0, 135.0, 110.0, 125.0, 128.0, 140.0, 115.0, 125.0, 132.0, 118.0, 900.0, 122.0, 130.0, 127.0, 119.0]
timestamps_efectivos= [1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004]
--- pares (año, valor) apareados POR POSICIÓN (lo que hacen los gráficos) ---
   1990: 120.0
   1991: 135.0
   1992: 110.0
   1993: 125.0
   1994: 128.0
   1995: 140.0
   1996: 115.0
   1997: 125.0
   1998: 132.0
   1999: 118.0
   2000: 900.0
   2001: 122.0
   2002: 130.0
   2003: 127.0
   2004: 119.0
   (elementos de timestamps_efectivos sin par: [])
Chow: veredicto=rechazada warning=TEST_WARNING_OUTLIER_DETECTED indice_atipico=10 valor_atipico=900.0
El 900.0 queda etiquetado por posición con el año: 2000  (año real en el archivo: 2000)  DESALINEADO=False
warnings 1ª pasada:
   CONTRACT_LENGTH_WARNING :: Serie con 15 datos — resultados no certificables
   TEST_WARNING_SMALL_SAMPLE :: Wald-Wolfowitz ejecutado con n ≤ 40 — aproximación normal menos precisa
   TEST_WARNING_HOMOGENEITY :: Cramer aprobó homogeneidad, pero Helmert o t de Student rechazaron
   TEST_WARNING_OUTLIER_DETECTED :: Chow detectó un dato atípico — decisión pendiente del usuario
------------------------------------------------------------------------------
EMULACIÓN DEL RECHAZO DE ATÍPICO (analysis_service.py:598-638)
------------------------------------------------------------------------------
indice_atipico (Chow)=10  indice_real (mapeado)=10
VALOR borrado de la serie: 900.0
AÑO borrado de timestamps: 2000   (año real del atípico: 2000; año del faltante: 1993)
len(serie_filtrada)=14  len(timestamps_filtrados)=14
timestamps_filtrados = [1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2001, 2002, 2003, 2004]
saltos (a->b con b-a != 1) en timestamps_filtrados: [(1999, 2001)]
2ª pasada: bloqueante=False nivel_confianza=con_warnings
2ª pasada: len(serie_efectiva)=14 len(timestamps_efectivos)=14
warnings 2ª pasada:
   CONTRACT_LENGTH_WARNING :: Serie con 14 datos — resultados no certificables
   CONTRACT_IRREGULAR_SPACING :: Espaciado temporal irregular detectado
   TEST_WARNING_SMALL_SAMPLE :: Wald-Wolfowitz ejecutado con n ≤ 40 — aproximación normal menos precisa
Chow 2ª pasada: aprobada None

##############################################################################
# B2) PAYLOAD que se emite/persiste: _serializar_etapa1() sobre cada pasada
##############################################################################
1ª pasada (ruta 'aceptar'): len(serie_efectiva)=14 len(timestamps_efectivos)=15 indice_atipico=9
   valor en indice_atipico=900.0  timestamp en ese índice={'iso': '1999-01-01', 'anio': 1999}
   timestamps_efectivos=[1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004]
2ª pasada (ruta 'rechazar'): len(serie_efectiva)=13 len(timestamps_efectivos)=14 indice_atipico=None
   timestamps_efectivos=[1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 2000, 2001, 2002, 2003, 2004]
CONTRASTE 1ª pasada (sin faltante): len(serie_efectiva)=15 len(timestamps_efectivos)=15 indice_atipico=10
   valor en indice_atipico=900.0  timestamp en ese índice={'iso': '2000-01-01', 'anio': 2000}
   timestamps_efectivos=[1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004]

##############################################################################
# C) ALCANCE: ¿cambian estadísticos/veredictos/ranking si los timestamps estuvieran alineados?
##############################################################################
len(serie_efectiva) faltante=14  consistente=14
serie_efectiva idéntica: True
resultados de las 8 pruebas idénticos (prueba, estadístico, crítico, veredicto, n1, n2, idx): True
   faltante  : ('anderson', -0.12114960246368058, 0.44534726188131, 'aprobada', None, None, None)
   consistente: ('anderson', -0.12114960246368058, 0.44534726188131, 'aprobada', None, None, None)
   faltante  : ('wald_wolfowitz', 0.4082482904638628, 1.959963984540054, 'aprobada', None, None, None)
   consistente: ('wald_wolfowitz', 0.4082482904638628, 1.959963984540054, 'aprobada', None, None, None)
   faltante  : ('helmert', 9.0, 3.605551275463989, 'rechazada', None, None, None)
   consistente: ('helmert', 9.0, 3.605551275463989, 'rechazada', None, None, None)
   faltante  : ('t_student', -0.9246554402560575, 2.1788128296634177, 'aprobada', 7, 7, None)
   consistente: ('t_student', -0.9246554402560575, 2.1788128296634177, 'aprobada', 7, 7, None)
   faltante  : ('cramer', 0.6784329389990164, 2.1788128296634177, 'aprobada', 9, 4, None)
   consistente: ('cramer', 0.6784329389990164, 2.1788128296634177, 'aprobada', 9, 4, None)
   faltante  : ('mann_kendall', 0.10948978029027179, 1.959963984540054, 'aprobada', None, None, None)
   consistente: ('mann_kendall', 0.10948978029027179, 1.959963984540054, 'aprobada', None, None, None)
   faltante  : ('kolmogorov_smirnov', 0.5345224838248487, 1.358, 'aprobada', None, None, None)
   consistente: ('kolmogorov_smirnov', 0.5345224838248487, 1.358, 'aprobada', None, None, None)
   faltante  : ('chow', 3.4483592445372167, 2.37165358034381, 'rechazada', None, None, 9)
   consistente: ('chow', 3.4483592445372167, 2.37165358034381, 'rechazada', None, None, 9)
nivel_independencia/homogeneidad/confianza idénticos: True
warnings faltante   : ['CONTRACT_LENGTH_WARNING', 'CONTRACT_NON_NUMERIC_VALUES', 'CONTRACT_MISSING_VALUES', 'TEST_WARNING_SMALL_SAMPLE', 'TEST_WARNING_HOMOGENEITY', 'TEST_WARNING_OUTLIER_DETECTED']
warnings consistente: ['CONTRACT_LENGTH_WARNING', 'CONTRACT_IRREGULAR_SPACING', 'TEST_WARNING_SMALL_SAMPLE', 'TEST_WARNING_HOMOGENEITY', 'TEST_WARNING_OUTLIER_DETECTED']
ranking Etapa 2 idéntico (13 distribuciones, mejor método y EEA): True
   gamma3p                      momentos 146.7842569832495
   exponencial_beta             momentos 149.80638900505468
   gen_exponencial              momentos 151.85983712531342
   gamma2p                      momentos 152.24691714301863
   lognormal3p                  momentos 156.3917422591871
2ª pasada faltante vs sin-faltante: len(serie_efectiva) 13 14
```

### Nivel 2 — API real, CU-02 (`verif_nivel2.py`)

Casos A y D = con celda vacía (`rechazar` y `aceptar`); B y E = contraste sin celda vacía; C = mensual.

```text
==============================================================================
E2E CASO A_anual_con_faltante
==============================================================================
HTTP stream status: 200
outlier_detected -> {"session_id": "df2ac990-ec50-4f3b-b827-71a6f1dc5ebf", "valor_atipico": 900.0}
outlier-decision -> (200, {'ok': True, 'pipeline_continua': True})
secuencia de eventos: ['contract_warning', 'contract_warning', 'contract_warning', 'descriptive_stats', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'outlier_detected', 'contract_warning', 'contract_warning', 'descriptive_stats', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'result_etapa1', 'complete']
contract_warning {"codigo": "CONTRACT_LENGTH_WARNING", "nivel": "normal", "iteracion": 1}
contract_warning {"codigo": "CONTRACT_NON_NUMERIC_VALUES", "nivel": "normal", "iteracion": 1}
contract_warning {"codigo": "CONTRACT_MISSING_VALUES", "nivel": "normal", "iteracion": 1}
test_result chow: {"prueba": "chow", "estadistico": 3.4483592445372167, "valor_critico": 2.37165358034381, "veredicto": "rechazada", "warning_codigo": "TEST_WARNING_OUTLIER_DETECTED", "warning_nivel": "normal", "n1": null, "n2": null, "valor_atipico": 900.0, "indice_atipico": 9, "iteracion": 1}
contract_warning {"codigo": "CONTRACT_LENGTH_WARNING", "nivel": "normal", "iteracion": 2}
contract_warning {"codigo": "CONTRACT_IRREGULAR_SPACING", "nivel": "normal", "iteracion": 2}
test_result chow: {"prueba": "chow", "estadistico": 1.8187911563816765, "valor_critico": 2.330540210276905, "veredicto": "aprobada", "warning_codigo": null, "warning_nivel": null, "n1": null, "n2": null, "valor_atipico": null, "indice_atipico": null, "iteracion": 2}
cantidad de eventos result_etapa1: 1
resolucion_original=anual resolucion_serie_original=anual
len(serie_efectiva)=13  len(timestamps_efectivos)=14  IGUALES=False
serie_efectiva       = [120.0, 135.0, 110.0, 128.0, 140.0, 115.0, 125.0, 132.0, 118.0, 122.0, 130.0, 127.0, 119.0]
timestamps_efectivos = ['1990-01-01', '1991-01-01', '1992-01-01', '1993-01-01', '1994-01-01', '1995-01-01', '1996-01-01', '1997-01-01', '1998-01-01', '2000-01-01', '2001-01-01', '2002-01-01', '2003-01-01', '2004-01-01']
datos.indice_atipico = None
--- pares (año, valor) por POSICIÓN, como los dibujan Etapa1SerieTemporalChart/Etapa1ChowChart ---
   pos  0: año 1990 -> 120.0
   pos  1: año 1991 -> 135.0
   pos  2: año 1992 -> 110.0
   pos  3: año 1993 -> 128.0
   pos  4: año 1994 -> 140.0
   pos  5: año 1995 -> 115.0
   pos  6: año 1996 -> 125.0
   pos  7: año 1997 -> 132.0
   pos  8: año 1998 -> 118.0
   pos  9: año 2000 -> 122.0
   pos 10: año 2001 -> 130.0
   pos 11: año 2002 -> 127.0
   pos 12: año 2003 -> 119.0
   timestamps sin par: [2004]
nivel_confianza: con_warnings | nivel_independencia: independiente | nivel_homogeneidad: homogeneidad_warning
warnings (result_etapa1 final):
    CONTRACT_LENGTH_WARNING :: Serie con 13 datos — resultados no certificables
    CONTRACT_IRREGULAR_SPACING :: Espaciado temporal irregular detectado
    TEST_WARNING_SMALL_SAMPLE :: Wald-Wolfowitz ejecutado con n ≤ 40 — aproximación normal menos precisa
    TEST_WARNING_HOMOGENEITY :: Cramer aprobó homogeneidad, pero Helmert o t de Student rechazaron
pruebas (prueba, estadistico, valor_critico, veredicto, indice_atipico):
    ('anderson', 0.5852508722379132, 0.4583720949441075, 'aprobada', None)
    ('wald_wolfowitz', 0.8971226080325131, 1.959963984540054, 'aprobada', None)
    ('helmert', -4.0, 3.4641016151377544, 'rechazada', None)
    ('t_student', -0.008888529763626075, 2.200985160082949, 'aprobada', None)
    ('cramer', 0.6023625712655291, 2.200985160082949, 'aprobada', None)
    ('mann_kendall', -0.061008887608656304, 1.959963984540054, 'aprobada', None)
    ('kolmogorov_smirnov', 0.5991446895152781, 1.358, 'aprobada', None)
    ('chow', 1.8187911563816765, 2.330540210276905, 'aprobada', None)

==============================================================================
E2E CASO B_anual_sin_faltante
==============================================================================
HTTP stream status: 200
outlier_detected -> {"session_id": "eeeadec1-a9d7-4fce-b40c-730324e29e94", "valor_atipico": 900.0}
outlier-decision -> (200, {'ok': True, 'pipeline_continua': True})
secuencia de eventos: ['contract_warning', 'descriptive_stats', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'outlier_detected', 'contract_warning', 'contract_warning', 'descriptive_stats', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'result_etapa1', 'complete']
contract_warning {"codigo": "CONTRACT_LENGTH_WARNING", "nivel": "normal", "iteracion": 1}
test_result chow: {"prueba": "chow", "estadistico": 3.5878139143111607, "valor_critico": 2.4090384205901003, "veredicto": "rechazada", "warning_codigo": "TEST_WARNING_OUTLIER_DETECTED", "warning_nivel": "normal", "n1": null, "n2": null, "valor_atipico": 900.0, "indice_atipico": 10, "iteracion": 1}
contract_warning {"codigo": "CONTRACT_LENGTH_WARNING", "nivel": "normal", "iteracion": 2}
contract_warning {"codigo": "CONTRACT_IRREGULAR_SPACING", "nivel": "normal", "iteracion": 2}
test_result chow: {"prueba": "chow", "estadistico": 1.8977486697280612, "valor_critico": 2.37165358034381, "veredicto": "aprobada", "warning_codigo": null, "warning_nivel": null, "n1": null, "n2": null, "valor_atipico": null, "indice_atipico": null, "iteracion": 2}
cantidad de eventos result_etapa1: 1
resolucion_original=anual resolucion_serie_original=anual
len(serie_efectiva)=14  len(timestamps_efectivos)=14  IGUALES=True
serie_efectiva       = [120.0, 135.0, 110.0, 125.0, 128.0, 140.0, 115.0, 125.0, 132.0, 118.0, 122.0, 130.0, 127.0, 119.0]
timestamps_efectivos = ['1990-01-01', '1991-01-01', '1992-01-01', '1993-01-01', '1994-01-01', '1995-01-01', '1996-01-01', '1997-01-01', '1998-01-01', '1999-01-01', '2001-01-01', '2002-01-01', '2003-01-01', '2004-01-01']
datos.indice_atipico = None
--- pares (año, valor) por POSICIÓN, como los dibujan Etapa1SerieTemporalChart/Etapa1ChowChart ---
   pos  0: año 1990 -> 120.0
   pos  1: año 1991 -> 135.0
   pos  2: año 1992 -> 110.0
   pos  3: año 1993 -> 125.0
   pos  4: año 1994 -> 128.0
   pos  5: año 1995 -> 140.0
   pos  6: año 1996 -> 115.0
   pos  7: año 1997 -> 125.0
   pos  8: año 1998 -> 132.0
   pos  9: año 1999 -> 118.0
   pos 10: año 2001 -> 122.0
   pos 11: año 2002 -> 130.0
   pos 12: año 2003 -> 127.0
   pos 13: año 2004 -> 119.0
nivel_confianza: con_warnings | nivel_independencia: independiente | nivel_homogeneidad: homogeneidad_ok
warnings (result_etapa1 final):
    CONTRACT_LENGTH_WARNING :: Serie con 14 datos — resultados no certificables
    CONTRACT_IRREGULAR_SPACING :: Espaciado temporal irregular detectado
    TEST_WARNING_SMALL_SAMPLE :: Wald-Wolfowitz ejecutado con n ≤ 40 — aproximación normal menos precisa
pruebas (prueba, estadistico, valor_critico, veredicto, indice_atipico):
    ('anderson', -0.4071810542398777, 0.44534726188131, 'aprobada', None)
    ('wald_wolfowitz', 0.6502032202644622, 1.959963984540054, 'aprobada', None)
    ('helmert', -3.0, 3.605551275463989, 'aprobada', None)
    ('t_student', 0.0, 2.1788128296634177, 'aprobada', None)
    ('cramer', 0.3566692892048218, 2.1788128296634177, 'aprobada', None)
    ('mann_kendall', 0.0, 1.959963984540054, 'aprobada', None)
    ('kolmogorov_smirnov', 0.5345224838248487, 1.358, 'aprobada', None)
    ('chow', 1.8977486697280612, 2.37165358034381, 'aprobada', None)

==============================================================================
E2E CASO C_mensual_con_faltante
==============================================================================
HTTP stream status: 200
outlier_detected -> {"session_id": "b58fe224-6a09-45fb-b2bf-bdf5c8349465", "valor_atipico": 900.0}
outlier-decision -> (200, {'ok': True, 'pipeline_continua': True})
secuencia de eventos: ['contract_warning', 'contract_warning', 'descriptive_stats', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'outlier_detected', 'contract_warning', 'contract_warning', 'descriptive_stats', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'result_etapa1', 'complete']
contract_warning {"codigo": "CONTRACT_LENGTH_WARNING", "nivel": "normal", "iteracion": 1}
contract_warning {"codigo": "CONTRACT_IRREGULAR_SPACING", "nivel": "normal", "iteracion": 1}
test_result chow: {"prueba": "chow", "estadistico": 3.4641990626550974, "valor_critico": 2.37165358034381, "veredicto": "rechazada", "warning_codigo": "TEST_WARNING_OUTLIER_DETECTED", "warning_nivel": "normal", "n1": null, "n2": null, "valor_atipico": 900.0, "indice_atipico": 9, "iteracion": 1}
contract_warning {"codigo": "CONTRACT_LENGTH_WARNING", "nivel": "normal", "iteracion": 2}
contract_warning {"codigo": "CONTRACT_IRREGULAR_SPACING", "nivel": "normal", "iteracion": 2}
test_result chow: {"prueba": "chow", "estadistico": 1.614680643193412, "valor_critico": 2.330540210276905, "veredicto": "aprobada", "warning_codigo": null, "warning_nivel": null, "n1": null, "n2": null, "valor_atipico": null, "indice_atipico": null, "iteracion": 2}
cantidad de eventos result_etapa1: 1
resolucion_original=mensual resolucion_serie_original=mensual
len(serie_efectiva)=13  len(timestamps_efectivos)=13  IGUALES=True
serie_efectiva       = [97.0, 101.0, 105.0, 109.0, 96.0, 104.0, 108.0, 109.0, 99.0, 107.0, 109.0, 99.0, 103.0]
timestamps_efectivos = ['2000-01-01', '2001-01-01', '2002-01-01', '2003-01-01', '2004-01-01', '2006-01-01', '2007-01-01', '2008-01-01', '2009-01-01', '2011-01-01', '2012-01-01', '2013-01-01', '2014-01-01']
datos.indice_atipico = None
--- pares (año, valor) por POSICIÓN, como los dibujan Etapa1SerieTemporalChart/Etapa1ChowChart ---
   pos  0: año 2000 -> 97.0
   pos  1: año 2001 -> 101.0
   pos  2: año 2002 -> 105.0
   pos  3: año 2003 -> 109.0
   pos  4: año 2004 -> 96.0
   pos  5: año 2006 -> 104.0
   pos  6: año 2007 -> 108.0
   pos  7: año 2008 -> 109.0
   pos  8: año 2009 -> 99.0
   pos  9: año 2011 -> 107.0
   pos 10: año 2012 -> 109.0
   pos 11: año 2013 -> 99.0
   pos 12: año 2014 -> 103.0
nivel_confianza: con_warnings | nivel_independencia: independiente | nivel_homogeneidad: homogeneidad_ok
warnings (result_etapa1 final):
    CONTRACT_INCOMPLETE_YEARS_DISCARDED :: Se descartaron 1 año(s) incompleto(s) dentro del registro: 2005.
    CONTRACT_LENGTH_WARNING :: Serie con 13 datos — resultados no certificables
    CONTRACT_IRREGULAR_SPACING :: Espaciado temporal irregular detectado
    TEST_WARNING_SMALL_SAMPLE :: Wald-Wolfowitz ejecutado con n ≤ 40 — aproximación normal menos precisa
pruebas (prueba, estadistico, valor_critico, veredicto, indice_atipico):
    ('anderson', 0.45091408874732763, 0.4583720949441075, 'aprobada', None)
    ('wald_wolfowitz', -0.269136782409754, 1.959963984540054, 'aprobada', None)
    ('helmert', 0.0, 3.4641016151377544, 'aprobada', None)
    ('t_student', -1.000534519169975, 2.200985160082949, 'aprobada', None)
    ('cramer', 1.1293737043881018, 2.200985160082949, 'aprobada', None)
    ('mann_kendall', 0.67700320038633, 1.959963984540054, 'aprobada', None)
    ('kolmogorov_smirnov', 0.727532837268552, 1.358, 'aprobada', None)
    ('chow', 1.614680643193412, 2.330540210276905, 'aprobada', None)

==============================================================================
E2E CASO D_anual_con_faltante_ACEPTAR
==============================================================================
HTTP stream status: 200
outlier_detected -> {"session_id": "fac67283-d08b-4921-b3a9-1dc786c7d9c1", "valor_atipico": 900.0}
outlier-decision -> (200, {'ok': True, 'pipeline_continua': True})
secuencia de eventos: ['contract_warning', 'contract_warning', 'contract_warning', 'descriptive_stats', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'outlier_detected', 'result_etapa1', 'complete']
contract_warning {"codigo": "CONTRACT_LENGTH_WARNING", "nivel": "normal", "iteracion": 1}
contract_warning {"codigo": "CONTRACT_NON_NUMERIC_VALUES", "nivel": "normal", "iteracion": 1}
contract_warning {"codigo": "CONTRACT_MISSING_VALUES", "nivel": "normal", "iteracion": 1}
test_result chow: {"prueba": "chow", "estadistico": 3.4483592445372167, "valor_critico": 2.37165358034381, "veredicto": "rechazada", "warning_codigo": "TEST_WARNING_OUTLIER_DETECTED", "warning_nivel": "normal", "n1": null, "n2": null, "valor_atipico": 900.0, "indice_atipico": 9, "iteracion": 1}
cantidad de eventos result_etapa1: 1
resolucion_original=anual resolucion_serie_original=anual
len(serie_efectiva)=14  len(timestamps_efectivos)=15  IGUALES=False
serie_efectiva       = [120.0, 135.0, 110.0, 128.0, 140.0, 115.0, 125.0, 132.0, 118.0, 900.0, 122.0, 130.0, 127.0, 119.0]
timestamps_efectivos = ['1990-01-01', '1991-01-01', '1992-01-01', '1993-01-01', '1994-01-01', '1995-01-01', '1996-01-01', '1997-01-01', '1998-01-01', '1999-01-01', '2000-01-01', '2001-01-01', '2002-01-01', '2003-01-01', '2004-01-01']
datos.indice_atipico = 9
--- pares (año, valor) por POSICIÓN, como los dibujan Etapa1SerieTemporalChart/Etapa1ChowChart ---
   pos  0: año 1990 -> 120.0
   pos  1: año 1991 -> 135.0
   pos  2: año 1992 -> 110.0
   pos  3: año 1993 -> 128.0
   pos  4: año 1994 -> 140.0
   pos  5: año 1995 -> 115.0
   pos  6: año 1996 -> 125.0
   pos  7: año 1997 -> 132.0
   pos  8: año 1998 -> 118.0
   pos  9: año 1999 -> 900.0
   pos 10: año 2000 -> 122.0
   pos 11: año 2001 -> 130.0
   pos 12: año 2002 -> 127.0
   pos 13: año 2003 -> 119.0
   timestamps sin par: [2004]
nivel_confianza: con_warnings | nivel_independencia: independiente | nivel_homogeneidad: homogeneidad_warning
warnings (result_etapa1 final):
    CONTRACT_LENGTH_WARNING :: Serie con 14 datos — resultados no certificables
    CONTRACT_NON_NUMERIC_VALUES :: 1 valor(es) no numérico(s) detectado(s)
    CONTRACT_MISSING_VALUES :: 1 valor(es) faltante(s) o celda(s) vacía(s)
    TEST_WARNING_SMALL_SAMPLE :: Wald-Wolfowitz ejecutado con n ≤ 40 — aproximación normal menos precisa
    TEST_WARNING_HOMOGENEITY :: Cramer aprobó homogeneidad, pero Helmert o t de Student rechazaron
    TEST_WARNING_OUTLIER_DETECTED :: Chow detectó un dato atípico — decisión pendiente del usuario
pruebas (prueba, estadistico, valor_critico, veredicto, indice_atipico):
    ('anderson', -0.12114960246368058, 0.44534726188131, 'aprobada', None)
    ('wald_wolfowitz', 0.4082482904638628, 1.959963984540054, 'aprobada', None)
    ('helmert', 9.0, 3.605551275463989, 'rechazada', None)
    ('t_student', -0.9246554402560575, 2.1788128296634177, 'aprobada', None)
    ('cramer', 0.6784329389990164, 2.1788128296634177, 'aprobada', None)
    ('mann_kendall', 0.10948978029027179, 1.959963984540054, 'aprobada', None)
    ('kolmogorov_smirnov', 0.5345224838248487, 1.358, 'aprobada', None)
    ('chow', 3.4483592445372167, 2.37165358034381, 'rechazada', 9)

==============================================================================
E2E CASO E_anual_sin_faltante_ACEPTAR
==============================================================================
HTTP stream status: 200
outlier_detected -> {"session_id": "9d7ac671-5398-4068-9f1c-b46871bf22d0", "valor_atipico": 900.0}
outlier-decision -> (200, {'ok': True, 'pipeline_continua': True})
secuencia de eventos: ['contract_warning', 'descriptive_stats', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'progress', 'test_result', 'outlier_detected', 'result_etapa1', 'complete']
contract_warning {"codigo": "CONTRACT_LENGTH_WARNING", "nivel": "normal", "iteracion": 1}
test_result chow: {"prueba": "chow", "estadistico": 3.5878139143111607, "valor_critico": 2.4090384205901003, "veredicto": "rechazada", "warning_codigo": "TEST_WARNING_OUTLIER_DETECTED", "warning_nivel": "normal", "n1": null, "n2": null, "valor_atipico": 900.0, "indice_atipico": 10, "iteracion": 1}
cantidad de eventos result_etapa1: 1
resolucion_original=anual resolucion_serie_original=anual
len(serie_efectiva)=15  len(timestamps_efectivos)=15  IGUALES=True
serie_efectiva       = [120.0, 135.0, 110.0, 125.0, 128.0, 140.0, 115.0, 125.0, 132.0, 118.0, 900.0, 122.0, 130.0, 127.0, 119.0]
timestamps_efectivos = ['1990-01-01', '1991-01-01', '1992-01-01', '1993-01-01', '1994-01-01', '1995-01-01', '1996-01-01', '1997-01-01', '1998-01-01', '1999-01-01', '2000-01-01', '2001-01-01', '2002-01-01', '2003-01-01', '2004-01-01']
datos.indice_atipico = 10
--- pares (año, valor) por POSICIÓN, como los dibujan Etapa1SerieTemporalChart/Etapa1ChowChart ---
   pos  0: año 1990 -> 120.0
   pos  1: año 1991 -> 135.0
   pos  2: año 1992 -> 110.0
   pos  3: año 1993 -> 125.0
   pos  4: año 1994 -> 128.0
   pos  5: año 1995 -> 140.0
   pos  6: año 1996 -> 115.0
   pos  7: año 1997 -> 125.0
   pos  8: año 1998 -> 132.0
   pos  9: año 1999 -> 118.0
   pos 10: año 2000 -> 900.0
   pos 11: año 2001 -> 122.0
   pos 12: año 2002 -> 130.0
   pos 13: año 2003 -> 127.0
   pos 14: año 2004 -> 119.0
nivel_confianza: con_warnings | nivel_independencia: independiente | nivel_homogeneidad: homogeneidad_warning
warnings (result_etapa1 final):
    CONTRACT_LENGTH_WARNING :: Serie con 15 datos — resultados no certificables
    TEST_WARNING_SMALL_SAMPLE :: Wald-Wolfowitz ejecutado con n ≤ 40 — aproximación normal menos precisa
    TEST_WARNING_HOMOGENEITY :: Cramer aprobó homogeneidad, pero Helmert o t de Student rechazaron
    TEST_WARNING_OUTLIER_DETECTED :: Chow detectó un dato atípico — decisión pendiente del usuario
pruebas (prueba, estadistico, valor_critico, veredicto, indice_atipico):
    ('anderson', -0.11211508519331441, 0.43333933173727673, 'aprobada', None)
    ('wald_wolfowitz', 0.392232270276368, 1.959963984540054, 'aprobada', None)
    ('helmert', 10.0, 3.7416573867739413, 'rechazada', None)
    ('t_student', -0.8701047473379759, 2.1603686564610127, 'aprobada', None)
    ('cramer', 0.7515599535207284, 2.1603686564610127, 'aprobada', None)
    ('mann_kendall', 0.2477393699381441, 1.959963984540054, 'aprobada', None)
    ('kolmogorov_smirnov', 0.5520524474738834, 1.358, 'aprobada', None)
    ('chow', 3.5878139143111607, 2.4090384205901003, 'rechazada', 10)
```

---

## Apéndice A — `verif_nivel1.py` (completo)

```python
"""Verificación NIVEL 1 — core directo. Hipótesis: serie_efectiva y timestamps_efectivos
quedan de distinto largo cuando una carga ANUAL trae una celda vacía.

Correr dentro del contenedor backend:  python /tmp/verif_nivel1.py
NO modifica nada de backend/. Replica (copia literal de la lógica) el rechazo de atípico de
services/analysis_service.py::stream_analysis() líneas 598-638, reusando los mismos helpers.
"""

import numpy as np

from metis.core.pipeline.pipeline_etapa1 import ejecutar_etapa1
from metis.core.pipeline.pipeline_etapa2 import ejecutar_etapa2
from metis.services.analysis_service import (
    _extraer_indice_atipico,
    _mapear_indice_a_serie_original,
    _serializar_etapa1,
)

TS = list(range(1990, 2005))  # 1990..2004 (15 años)
SERIE_FALTANTE = [120, 135, 110, None, 128, 140, 115, 125, 132, 118, 900, 122, 130, 127, 119]
SERIE_SIN_FALTANTE = [120, 135, 110, 125, 128, 140, 115, 125, 132, 118, 900, 122, 130, 127, 119]
# (contraste: misma serie con 125 en 1993 en lugar de la celda vacía)
ANIO_REAL_900 = 2000


def cods(r):
    return [(w.codigo, w.descripcion) for w in r.warnings]


def resumen_tests(r):
    out = []
    for t in r.independencia + r.homogeneidad + r.tendencia + r.atipicos:
        out.append((t.prueba, t.estadistico, t.valor_critico, t.veredicto, t.n1, t.n2, t.indice_atipico))
    return out


def resumen_ranking(e2):
    return [(d.distribucion, d.mejor_metodo, d.mejor_eea) for d in e2.ranking]


def gaps(ts):
    return [(a, b) for a, b in zip(ts, ts[1:]) if b - a != 1]


def caso(nombre, serie, ts):
    print("=" * 78)
    print(f"CASO: {nombre}")
    print("=" * 78)
    r = ejecutar_etapa1(
        serie=serie,
        tipo_variable="caudal_precipitacion",
        resolucion_temporal="anual",
        timestamps=ts,
        cramer_particion="default",
        mes_inicio_anio=7,
        variable_diaria="pico",
    )
    se, te = r.serie_efectiva, r.timestamps_efectivos
    print(f"contract.bloqueante={r.contract.bloqueante} nivel_confianza={r.nivel_confianza}")
    print(f"len(serie_efectiva)={len(se)}  len(timestamps_efectivos)={len(te)}  "
          f"IGUALES={len(se) == len(te)}")
    print("serie_efectiva      =", se)
    print("timestamps_efectivos=", te)
    print("--- pares (año, valor) apareados POR POSICIÓN (lo que hacen los gráficos) ---")
    pares = list(zip(te, se))
    for a, v in pares:
        print(f"   {a}: {v}")
    print(f"   (elementos de timestamps_efectivos sin par: {te[len(se):]})")
    chow = r.atipicos[0]
    print(f"Chow: veredicto={chow.veredicto} warning={chow.warning_codigo} "
          f"indice_atipico={chow.indice_atipico} valor_atipico={chow.valor_atipico}")
    idx = chow.indice_atipico
    if idx is not None:
        etiqueta = te[idx] if idx < len(te) else None
        print(f"El {chow.valor_atipico} queda etiquetado por posición con el año: {etiqueta}  "
              f"(año real en el archivo: {ANIO_REAL_900})  DESALINEADO={etiqueta != ANIO_REAL_900}")
    print("warnings 1ª pasada:")
    for c, d in cods(r):
        print(f"   {c} :: {d}")

    if idx is None:
        return r, None

    print("-" * 78)
    print("EMULACIÓN DEL RECHAZO DE ATÍPICO (analysis_service.py:598-638)")
    print("-" * 78)
    indice_atipico = _extraer_indice_atipico(r)
    indice_real = _mapear_indice_a_serie_original(indice_atipico, se)
    serie_filtrada = se.copy()
    valor_borrado = serie_filtrada[indice_real]
    del serie_filtrada[indice_real]
    timestamps_filtrados = (
        None if te is None else [t for i, t in enumerate(te) if i != indice_real]
    )
    anio_borrado = te[indice_real]
    print(f"indice_atipico (Chow)={indice_atipico}  indice_real (mapeado)={indice_real}")
    print(f"VALOR borrado de la serie: {valor_borrado}")
    print(f"AÑO borrado de timestamps: {anio_borrado}   (año real del atípico: {ANIO_REAL_900};"
          f" año del faltante: 1993)")
    print(f"len(serie_filtrada)={len(serie_filtrada)}  len(timestamps_filtrados)={len(timestamps_filtrados)}")
    print("timestamps_filtrados =", timestamps_filtrados)
    print("saltos (a->b con b-a != 1) en timestamps_filtrados:", gaps(timestamps_filtrados))
    r2 = ejecutar_etapa1(
        serie=serie_filtrada,
        tipo_variable="caudal_precipitacion",
        resolucion_temporal="anual",
        timestamps=timestamps_filtrados,
        cramer_particion="default",
        mes_inicio_anio=7,
        variable_diaria="pico",
    )
    print(f"2ª pasada: bloqueante={r2.contract.bloqueante} nivel_confianza={r2.nivel_confianza}")
    print(f"2ª pasada: len(serie_efectiva)={len(r2.serie_efectiva)} "
          f"len(timestamps_efectivos)={len(r2.timestamps_efectivos)}")
    print("warnings 2ª pasada:")
    for c, d in cods(r2):
        print(f"   {c} :: {d}")
    print("Chow 2ª pasada:", r2.atipicos[0].veredicto, r2.atipicos[0].warning_codigo)
    return r, r2


def main():
    print("#" * 78)
    print("# A) CON celda vacía en 1993 (hipótesis)")
    print("#" * 78)
    r_f, r2_f = caso("anual, celda vacía en 1993, atípico 900 en 2000", SERIE_FALTANTE, TS)

    print()
    print("#" * 78)
    print("# B) CONTRASTE: SIN celda vacía (125 en 1993)")
    print("#" * 78)
    r_s, r2_s = caso("anual, SIN celda vacía, atípico 900 en 2000", SERIE_SIN_FALTANTE, TS)

    print()
    print("#" * 78)
    print("# B2) PAYLOAD que se emite/persiste: _serializar_etapa1() sobre cada pasada")
    print("#" * 78)
    for nombre, rr in (("1ª pasada (ruta 'aceptar')", r_f), ("2ª pasada (ruta 'rechazar')", r2_f),
                       ("CONTRASTE 1ª pasada (sin faltante)", r_s)):
        d = _serializar_etapa1(rr, 7)["datos"]
        ia = d["indice_atipico"]
        print(f"{nombre}: len(serie_efectiva)={len(d['serie_efectiva'])} "
              f"len(timestamps_efectivos)={len(d['timestamps_efectivos'])} indice_atipico={ia}")
        if ia is not None:
            print(f"   valor en indice_atipico={d['serie_efectiva'][ia]}  "
                  f"timestamp en ese índice={d['timestamps_efectivos'][ia]}")
        print(f"   timestamps_efectivos={[t['anio'] for t in d['timestamps_efectivos']]}")

    print()
    print("#" * 78)
    print("# C) ALCANCE: ¿cambian estadísticos/veredictos/ranking si los timestamps estuvieran alineados?")
    print("#" * 78)
    # Versión "consistente": mismos valores numéricos, sin el par (1993, None) — timestamps alineados.
    serie_c = [v for v in SERIE_FALTANTE if v is not None]
    ts_c = [t for t, v in zip(TS, SERIE_FALTANTE) if v is not None]
    r_c = ejecutar_etapa1(
        serie=serie_c, tipo_variable="caudal_precipitacion", resolucion_temporal="anual",
        timestamps=ts_c, cramer_particion="default", mes_inicio_anio=7, variable_diaria="pico",
    )
    print(f"len(serie_efectiva) faltante={len(r_f.serie_efectiva)}  consistente={len(r_c.serie_efectiva)}")
    print("serie_efectiva idéntica:", r_f.serie_efectiva == r_c.serie_efectiva)
    tf, tc = resumen_tests(r_f), resumen_tests(r_c)
    print("resultados de las 8 pruebas idénticos (prueba, estadístico, crítico, veredicto, n1, n2, idx):", tf == tc)
    for a, b in zip(tf, tc):
        print("   faltante  :", a)
        print("   consistente:", b)
    print("nivel_independencia/homogeneidad/confianza idénticos:",
          (r_f.nivel_independencia, r_f.nivel_homogeneidad, r_f.nivel_confianza)
          == (r_c.nivel_independencia, r_c.nivel_homogeneidad, r_c.nivel_confianza))
    print("warnings faltante   :", [c for c, _ in cods(r_f)])
    print("warnings consistente:", [c for c, _ in cods(r_c)])
    e2_f = ejecutar_etapa2(np.array(r_f.serie_efectiva), tiene_ceros=False)
    e2_c = ejecutar_etapa2(np.array(r_c.serie_efectiva), tiene_ceros=False)
    print("ranking Etapa 2 idéntico (13 distribuciones, mejor método y EEA):",
          resumen_ranking(e2_f) == resumen_ranking(e2_c))
    for d, m, e in resumen_ranking(e2_f)[:5]:
        print(f"   {d:28s} {m} {e}")
    # Etapa 2 sobre la serie posterior al rechazo (2ª pasada): también solo usa valores
    print("2ª pasada faltante vs sin-faltante: len(serie_efectiva)",
          len(r2_f.serie_efectiva), len(r2_s.serie_efectiva))


if __name__ == "__main__":
    main()
```

## Apéndice B — `verif_nivel2.py` (completo)

```python
"""Verificación NIVEL 2 — end to end contra la API real (CU-02, anónimo, sin JWT).

Correr dentro del contenedor backend:  PYTHONPATH=/app python /tmp/verif_nivel2.py
Flujo por caso:
  1. POST /api/v1/analysis/stream (multipart, etapas=1) y consumo del SSE
  2. al llegar `outlier_detected` -> POST /api/v1/analysis/outlier-decision {rechazar}
  3. se guarda TODO evento recibido; se imprime el resumen y se vuelca el JSON de
     `result_etapa1` final a /tmp/e2e_<caso>_result_etapa1.json
No toca backend/ ni frontend/. CU-02 no persiste nada en la BD.
"""

import asyncio
import json

import httpx

BASE = "http://localhost:8000/api/v1/analysis"

ANIOS = list(range(1990, 2005))
VAL_FALTANTE = ["120", "135", "110", "", "128", "140", "115", "125", "132", "118", "900", "122", "130", "127", "119"]
VAL_SIN_FALTANTE = ["120", "135", "110", "125", "128", "140", "115", "125", "132", "118", "900", "122", "130", "127", "119"]


def csv_anual(valores):
    filas = ["anio,caudal"] + [f"{a},{v}" for a, v in zip(ANIOS, valores)]
    return "\n".join(filas) + "\n"


def csv_mensual():
    """15 años (2000-2014) mensuales, celda vacía en 2005-03, pico 900 en 2010-06."""
    filas = ["fecha,caudal"]
    i = 0
    for anio in range(2000, 2015):
        for mes in range(1, 13):
            v = 60 + (i * 17) % 50
            if (anio, mes) == (2005, 3):
                v = ""
            if (anio, mes) == (2010, 6):
                v = 900
            filas.append(f"{anio}-{mes:02d}-01,{v}")
            i += 1
    return "\n".join(filas) + "\n"


def parsear_sse(buffer):
    """Devuelve (eventos_completos, resto)."""
    eventos = []
    while "\n\n" in buffer:
        bloque, buffer = buffer.split("\n\n", 1)
        tipo, data = None, None
        for linea in bloque.splitlines():
            if linea.startswith("event:"):
                tipo = linea[6:].strip()
            elif linea.startswith("data:"):
                data = linea[5:].strip()
        if tipo is not None:
            eventos.append((tipo, json.loads(data) if data else None))
    return eventos, buffer


async def correr(nombre, csv_text, columna_x, columna_y, extra=None, decision="rechazar"):
    print("=" * 78)
    print(f"E2E CASO {nombre}")
    print("=" * 78)
    campos = {
        "columna_x": columna_x,
        "columna_y": columna_y,
        "tipo_variable": "caudal_precipitacion",
        "etapas": "1",
        "modo": "experto",
        "cramer_particion": "default",
    }
    campos.update(extra or {})
    eventos = []
    decision_resp = None
    async with httpx.AsyncClient(timeout=60) as cli:
        files = {"archivo": ("serie.csv", csv_text.encode(), "text/csv")}
        async with cli.stream("POST", f"{BASE}/stream", data=campos, files=files) as resp:
            print("HTTP stream status:", resp.status_code)
            if resp.status_code != 200:
                print((await resp.aread()).decode())
                return None
            buf = ""
            async for chunk in resp.aiter_text():
                buf += chunk
                nuevos, buf = parsear_sse(buf)
                for tipo, data in nuevos:
                    eventos.append((tipo, data))
                    if tipo == "outlier_detected":
                        print("outlier_detected ->", json.dumps(data))
                        r = await cli.post(
                            f"{BASE}/outlier-decision",
                            json={
                                "session_id": data["session_id"],
                                "decision": decision,
                                "dato_atipico": data["valor_atipico"],
                            },
                        )
                        decision_resp = (r.status_code, r.json())
                        print("outlier-decision ->", decision_resp)
    print("secuencia de eventos:", [t for t, _ in eventos])

    # test_result de cada iteración: dónde quedó el atípico de Chow
    for tipo, data in eventos:
        if tipo == "test_result" and data.get("prueba") == "chow":
            print("test_result chow:", json.dumps(data, ensure_ascii=False))
        if tipo in ("contract_warning", "contract_error"):
            print(tipo, json.dumps(data, ensure_ascii=False))

    finales = [d for t, d in eventos if t == "result_etapa1"]
    print("cantidad de eventos result_etapa1:", len(finales))
    if not finales:
        return eventos
    res = finales[-1]
    datos = res["datos"]
    se, te = datos["serie_efectiva"], datos["timestamps_efectivos"]
    print(f"resolucion_original={datos['resolucion_original']} "
          f"resolucion_serie_original={datos['resolucion_serie_original']}")
    print(f"len(serie_efectiva)={len(se)}  len(timestamps_efectivos)={len(te)}  IGUALES={len(se) == len(te)}")
    print("serie_efectiva       =", se)
    print("timestamps_efectivos =", [t["iso"] if isinstance(t, dict) else t for t in te])
    print("datos.indice_atipico =", datos["indice_atipico"])
    print("--- pares (año, valor) por POSICIÓN, como los dibujan Etapa1SerieTemporalChart/Etapa1ChowChart ---")
    for k, v in enumerate(se):
        etiqueta = te[k] if k < len(te) else None
        etiqueta = etiqueta["anio"] if isinstance(etiqueta, dict) else etiqueta
        print(f"   pos {k:2d}: año {etiqueta} -> {v}")
    if len(te) > len(se):
        print("   timestamps sin par:", [t["anio"] if isinstance(t, dict) else t for t in te[len(se):]])
    print("nivel_confianza:", res["nivel_confianza"], "| nivel_independencia:", res["nivel_independencia"],
          "| nivel_homogeneidad:", res["nivel_homogeneidad"])
    print("warnings (result_etapa1 final):")
    for w in res["warnings"]:
        print("   ", w["codigo"], "::", w["descripcion"])
    print("pruebas (prueba, estadistico, valor_critico, veredicto, indice_atipico):")
    for grupo in ("independencia", "homogeneidad", "tendencia", "atipicos"):
        for t in res[grupo]:
            print("   ", (t["prueba"], t["estadistico"], t["valor_critico"], t["veredicto"], t.get("indice_atipico")))
    with open(f"/tmp/e2e_{nombre}_result_etapa1.json", "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    with open(f"/tmp/e2e_{nombre}_eventos.json", "w") as f:
        json.dump(eventos, f, ensure_ascii=False)
    return eventos


async def main():
    await correr("A_anual_con_faltante", csv_anual(VAL_FALTANTE), "anio", "caudal")
    print()
    await correr("B_anual_sin_faltante", csv_anual(VAL_SIN_FALTANTE), "anio", "caudal")
    print()
    await correr("C_mensual_con_faltante", csv_mensual(), "fecha", "caudal",
                 extra={"mes_inicio_anio": "1"})
    print()
    # Variante: el usuario ACEPTA el atípico -> el result_etapa1 final es el de la 1ª pasada
    await correr("D_anual_con_faltante_ACEPTAR", csv_anual(VAL_FALTANTE), "anio", "caudal",
                 decision="aceptar")
    print()
    await correr("E_anual_sin_faltante_ACEPTAR", csv_anual(VAL_SIN_FALTANTE), "anio", "caudal",
                 decision="aceptar")


if __name__ == "__main__":
    asyncio.run(main())
```
