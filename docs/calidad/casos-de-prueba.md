# Casos de prueba dinámicos

TP integrador de Calidad de Software, bloque B8 (`docs/plan-tp-calidad-software.md`, §2.5). Casos diseñados con tres
técnicas de caja negra: valores límite (VL), clases de equivalencia (CE) y tablas de decisión (TD). Cada caso apunta al
test que lo implementa. Todos pasan en `feature/tp-calidad-b8` (09/10/2026).

**Cómo leer las tablas.**
- **Test:** ruta relativa a `backend/`. Los tests nuevos de este bloque viven en `tests/unit/casos_dinamicos/` y llevan
  el ID del caso en el id de `parametrize`, así que `pytest -v` muestra, por ejemplo, `[VL-01a n=9]`. Para un caso que
  ya cubría otro test, se nombra ese test y no se lo duplicó.
- **Regla:** de dónde sale el resultado esperado: una decisión, un documento de reglas o el catálogo de errores
  (`.claude/rules/architecture/api-contracts.md`). Los IDs del Manual de Requerimientos (RF-…) se citan solo cuando ya
  están en el repo (RF-GEN-P-03 y RF-GEN-P-06). El resto de la trazabilidad a RF la cierra `trazabilidad.md` (B9).

Para correr solo estos casos: `pytest tests/unit/casos_dinamicos -v` (con `backend/` como directorio de trabajo, o vía
`docker exec`).

---

## 1. Valores límite

Cada borde se prueba de los dos lados: el último valor válido y el primero inválido.

| ID | Parámetro | Entrada | Esperado | Regla | Test |
|---|---|---|---|---|---|
| VL-01a | Longitud de la serie | n = 9 | Bloqueante, `CONTRACT_SERIES_TOO_SHORT` | `CLAUDE.md`, "Principio de negocio central" | `casos_dinamicos/test_valores_limite.py::test_longitud_de_la_serie[VL-01a n=9]` |
| VL-01b | | n = 10 | Continúa con `CONTRACT_LENGTH_WARNING` | ídem | `…::test_longitud_de_la_serie[VL-01b n=10]` |
| VL-01c | | n = 29 | Continúa con `CONTRACT_LENGTH_WARNING` | ídem | `…::test_longitud_de_la_serie[VL-01c n=29]` |
| VL-01d | | n = 30 | Continúa sin warning de longitud | ídem | `…::test_longitud_de_la_serie[VL-01d n=30]` |
| VL-02a | Tamaño del archivo | Exactamente 10 MB | Se lee completo | DECISIÓN 050 | `tests/unit/api/test_upload_limits.py::test_leer_archivo_limitado_exactamente_en_el_limite_pasa` |
| VL-02b | | 10 MB + 1 byte | 400 `PARSE_FILE_TOO_LARGE` | ídem | `casos_dinamicos/test_valores_limite.py::test_archivo_un_byte_sobre_el_limite_da_400` |
| VL-03a | `mes_inicio_anio` | 0 | 400 `CONTRACT_MES_INICIO_INVALID` | DECISIÓN 057 | `…::test_mes_inicio_fuera_del_rango[VL-03a mes=0]` |
| VL-03b | | 1 | Válido (año calendario) | ídem | `…::test_mes_inicio_en_el_rango[VL-03b mes=1]` |
| VL-03c | | 12 | Válido | ídem | `…::test_mes_inicio_en_el_rango[VL-03c mes=12]` |
| VL-03d | | 13 | 400 `CONTRACT_MES_INICIO_INVALID` | ídem | `…::test_mes_inicio_fuera_del_rango[VL-03d mes=13]` |
| VL-04a | Período de retorno T | T = 1 | 400 `DIST_SELECTION_INVALID` (F = 1 − 1/T necesita T > 1) | DECISIÓN 052 | `…::test_periodos_retorno_invalidos[VL-04a T=1]` |
| VL-04b | | T = 1,0001 | Válido | ídem | `…::test_periodos_retorno_validos[VL-04b T=1.0001]` |
| VL-05a | Cantidad de períodos | 0 | 400 `DIST_SELECTION_INVALID` | ídem | `…::test_periodos_retorno_invalidos[VL-05a 0 elementos]` |
| VL-05b | | 1 | Válido | ídem | `…::test_periodos_retorno_validos[VL-05b 1 elemento]` |
| VL-05c | | 20 | Válido | ídem | `…::test_periodos_retorno_validos[VL-05c 20 elementos]` |
| VL-05d | | 21 | 400 `DIST_SELECTION_INVALID` | ídem | `…::test_periodos_retorno_invalidos[VL-05d 21 elementos]` |
| VL-06a | Partición de Cramer | `n1_pct` = 0 o 101 | 400 `CONTRACT_CRAMER_PARTICION_INVALID` | DECISIÓN 036 | `tests/unit/api/test_stream_cramer_particion.py::test_parsear_forma_o_rango_invalido_da_400` |
| VL-06b | | `n1_pct` = 100, `n2_pct` = 99 | Válida | ídem | `casos_dinamicos/test_valores_limite.py::test_cramer_particion_en_los_bordes_validos[VL-06b n1=100 n2=99]` |
| VL-06c | | `n1_pct` = 2, `n2_pct` = 1 | Válida | ídem | `…::test_cramer_particion_en_los_bordes_validos[VL-06c n1=2 n2=1]` |
| VL-06d | | `n1_pct` = `n2_pct` = 100 | 400 (n1 tiene que ser estrictamente mayor) | ídem | `…::test_cramer_particion_en_los_bordes_invalidos[VL-06d n1=n2=100]` |
| VL-06e | | `n1_pct` = `n2_pct` = 1 | 400 | ídem | `…::test_cramer_particion_en_los_bordes_invalidos[VL-06e n1=n2=1]` |
| VL-06f | | `n2_pct` = 0 | 400 | ídem | `…::test_cramer_particion_en_los_bordes_invalidos[VL-06f n2=0]` |
| VL-07a | Wald-Wolfowitz | n = 40 | Ejecuta con `TEST_WARNING_SMALL_SAMPLE` | `constraints.md`, "Wald-Wolfowitz con n ≤ 40" | `tests/unit/core/etapa1/test_independence.py::test_wald_n_igual_40_emite_small_sample` |
| VL-07b | | n = 41 | Ejecuta sin warning de muestra chica | ídem | `tests/unit/core/etapa1/test_independence.py::test_wald_n_mayor_40_sin_small_sample` |
| VL-08a | Mann-Kendall | n = 9 | `no_ejecutada`, `TEST_NOT_EXECUTED_MIN_SAMPLES` | `formulas-etapa1.md` §7 | `casos_dinamicos/test_valores_limite.py::test_mann_kendall_umbrales_de_n[VL-08a n=9]` |
| VL-08b | | n = 10 | Ejecuta con `TEST_WARNING_SMALL_SAMPLE` | ídem | `…::test_mann_kendall_umbrales_de_n[VL-08b n=10]` |
| VL-08c | | n = 30 | Ejecuta con `TEST_WARNING_SMALL_SAMPLE` | ídem | `…::test_mann_kendall_umbrales_de_n[VL-08c n=30]` |
| VL-08d | | n = 31 | Ejecuta sin warning | ídem | `…::test_mann_kendall_umbrales_de_n[VL-08d n=31]` |

---

## 2. Clases de equivalencia

Un representante por clase, válida o inválida.

| ID | Variable | Clase | Representante | Esperado | Regla | Test |
|---|---|---|---|---|---|---|
| CE-01a | Resolución temporal | Anual | Columna de años | `anual` | `api-contracts.md`, `CONTRACT_NO_TEMPORAL_RESOLUTION` | `tests/unit/core/validacion/test_parser.py::test_columna_de_anio_puro_infiere_resolucion_anual` |
| CE-01b | | Mensual | Fechas año-mes | `mensual`, se agrega a máximos anuales | DECISIÓN 057 | `…/test_parser.py::test_columna_de_anio_y_mes_como_fecha_sigue_siendo_mensual` |
| CE-01c | | Diaria | Fechas diarias | `diaria`, se agrega a máximos anuales | DECISIÓN 065 | `…/test_parser.py::test_columna_de_fechas_diarias_infiere_resolucion_diaria` |
| CE-01d | | Otra (semanal, quincenal) | Fechas cada 7 y 15 días | `None` → bloqueante | ídem | `…/test_parser.py::test_serie_semanal_y_quincenal_no_se_confunden_con_diaria` |
| CE-01e | | Otra (sub-diaria) | Fechas horarias | `None` → bloqueante | ídem | `…/test_parser.py::test_serie_horaria_cae_en_none_por_el_truncamiento_de_days` |
| CE-01f | | Sin resolución | `resolucion_temporal=None` | Bloqueante, `CONTRACT_NO_TEMPORAL_RESOLUTION` | ídem | `tests/unit/core/validacion/test_contract.py::test_sin_resolucion_temporal_es_bloqueante` |
| CE-02a | `tipo_variable` × signo, en Chow | Positivos | Serie sin ceros | Ejecuta | `formulas-etapa1.md` §9 | `tests/unit/core/etapa1/test_outliers.py::test_sin_atipico_aprobada` |
| CE-02b | | Cero en `caudal_precipitacion` | `[0, 10, …]` | `no_ejecutada`, `TEST_NOT_EXECUTED_ZEROS` | ídem | `…/test_outliers.py::test_cero_en_caudal_no_ejecutada` |
| CE-02c | | Cero en `otro` | `[0, 10, …]` | `no_ejecutada`, `TEST_NOT_EXECUTED_CONDITION` | ídem | `…/test_outliers.py::test_cero_en_otro_no_ejecutada` |
| CE-02d | | Negativos, cualquier tipo, con o sin cero | `[-5, …]`, `[-5, 0, …]` | `no_ejecutada`, `TEST_NOT_EXECUTED_NEGATIVES` | DECISIÓN 073 | `…/test_outliers.py::test_negativo_no_ejecutada_con_codigo_propio` (4 ids) |
| CE-02e | `tipo_variable` × signo, en el contrato | Negativos en `caudal_precipitacion` | | Warning `CONTRACT_NEGATIVE_VALUES` | `api-contracts.md` | `tests/unit/core/validacion/test_contract.py::test_negativos_en_caudal_activa_warning` |
| CE-02f | | Negativos en `otro` | | Sin warning | ídem | `…/test_contract.py::test_negativos_en_tipo_otro_sin_warning` |
| CE-03a | Formato del archivo | CSV válido | 3 filas | Columnas y muestra | DECISIÓN 047 | `casos_dinamicos/test_clases_equivalencia.py::test_formatos_validos_dan_las_mismas_columnas[CE-03a CSV válido]` |
| CE-03b | | Excel válido | El mismo contenido en `.xlsx` | Las mismas columnas y muestra que el CSV | ídem | `…::test_formatos_validos_dan_las_mismas_columnas[CE-03b Excel válido]` |
| CE-03c | | Ilegible | Bytes binarios | 400 `PARSE_ERROR` | ídem | `tests/unit/api/test_analysis_preview_columns.py::test_preview_columns_archivo_no_parseable_da_400_parse_error` |
| CE-03d | | Ilegible: extensión que no coincide | CSV con nombre `.xlsx` | Excepción del lector, el endpoint responde `PARSE_ERROR` | ídem | `casos_dinamicos/test_clases_equivalencia.py::test_excel_con_extension_pero_contenido_csv_no_se_parsea` |
| CE-03e | | Vacío | 0 bytes | 400 `PARSE_ERROR` | ídem | `tests/unit/api/test_analysis_preview_columns.py::test_preview_columns_archivo_vacio_da_400_parse_error` |
| CE-04a | `etapas` | `"1"` | | Termina en `result_etapa1`, sin pausa de Etapa 2 | DECISIÓN 054 | `tests/integration/test_etapa2_stream_distribution_decision.py::test_etapas_1_solo_no_pausa_en_etapa_2` |
| CE-04b | | `"1,2"` | | Válido | ídem | `tests/unit/api/test_stream_etapas_validacion.py::test_etapas_uno_dos_no_lanza` |
| CE-04c | | Inválido | `"3"`, `"2,1"`, … | 400 `CONTRACT_ETAPAS_INVALID` | ídem | `…/test_stream_etapas_validacion.py::test_etapas_invalida_da_400_no_500`, `::test_etapas_vacia_da_400` |
| CE-05a | `variable_diaria` | `pico`, `media` | | Válido | DECISIÓN 065 | `tests/unit/api/test_stream_variable_diaria_validacion.py::test_valores_validos_no_lanzan` |
| CE-05b | | Otro valor | | 400 `CONTRACT_VARIABLE_DIARIA_INVALID` | ídem | `…/test_stream_variable_diaria_validacion.py::test_valor_invalido_da_400` |

---

## 3. Tablas de decisión

Una columna por combinación de condiciones. **A** = aprobada, **R** = rechazada.

### TD-01. Nivel de independencia

Anderson manda; Wald-Wolfowitz verifica y no decide (`constraints.md`, "Anderson acepta, Wald-Wolfowitz rechaza").

| | c1 | c2 | c3 | c4 |
|---|---|---|---|---|
| Anderson | A | A | R | R |
| Wald-Wolfowitz | A | R | A | R |
| **Nivel** | independiente | independiente | dependiente | dependiente |
| **Warning crítico** | no | no | sí | sí |

Test: `casos_dinamicos/test_tablas_decision.py::test_tabla_independencia[TD-01 c1 … c4]`.

### TD-02. Nivel de homogeneidad

Cramer manda; Helmert o t de Student solo degradan a warning normal (RF-GEN-P-06, `statistical-pipeline.md`).

| | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 |
|---|---|---|---|---|---|---|---|---|
| Cramer | A | A | A | A | R | R | R | R |
| Helmert | A | R | A | R | A | R | A | R |
| t de Student | A | A | R | R | A | A | R | R |
| **Nivel** | ok | warning | warning | warning | crítica | crítica | crítica | crítica |
| **Código** | — | `TEST_WARNING_HOMOGENEITY` | ídem | ídem | `TEST_CRITICAL_HOMOGENEITY` | ídem | ídem | ídem |

Test: `casos_dinamicos/test_tablas_decision.py::test_tabla_homogeneidad[TD-02 c1 … c8]`.

### TD-03. Nivel de confianza global

| | c1 | c2 | c3 | c4 |
|---|---|---|---|---|
| Bloqueante del contrato | sí | no | no | no |
| Algún warning crítico | — | sí | no | no |
| Algún warning normal | — | — | sí | no |
| **`nivel_confianza`** | `rechazado` | `con_warnings` | `con_warnings` | `validado` |
| **Test** | `tests/unit/core/pipeline/test_pipeline_etapa1.py::test_serie_bloqueante_detiene_pipeline` | `…/test_pipeline_etapa1.py::test_warning_critico_produce_con_warnings` | `casos_dinamicos/test_tablas_decision.py::test_tabla_confianza_c3_solo_warnings_normales_da_con_warnings` | `…/test_pipeline_etapa1.py::test_serie_valida_nivel_confianza_validado` |

### TD-04. Entrada a Etapa 2

Etapa 2 corre solo si se pidió y Etapa 1 no quedó rechazada; con warnings, incluso críticos, corre igual (RF-GEN-P-03,
`statistical-pipeline.md`, "Condiciones para entrar a Etapa 2").

| | c1 | c2 | c3 | c4 |
|---|---|---|---|---|
| `etapas` | `[1]` | `[1, 2]` | `[1]` | `[1, 2]` |
| Etapa 1 `rechazado` | no | no | sí | sí |
| **Corre Etapa 2** | no | sí | no | no |

Test: `casos_dinamicos/test_tablas_decision.py::test_tabla_entrada_a_etapa2[TD-04 c1 … c4]`, sobre
`simular_exclusion()`, que aplica la misma condición que el stream. El rechazo se provoca excluyendo 3 de 12 datos (quedan
9). El stream lo cubre además `tests/integration/test_etapa2_stream_distribution_decision.py`.

### TD-05. Estado de las distribuciones deshabilitables

Las cinco de `DISABLED_WITH_NEGATIVES` y las cuatro de `DISABLED_WITH_ZEROS` (`core/etapa2/distributions/__init__.py`).

| | c1 | c2 | c3 | c4 |
|---|---|---|---|---|
| Ceros | no | sí | no | sí |
| Negativos | no | no | sí | sí |
| **Estado** | se ajustan | `disabled_zeros` (las de ceros) | `disabled_negatives` (las de negativos) | `disabled_negatives` (gana sobre ceros) |
| **Regla** | — | DECISIÓN 061 | DECISIÓN 073 | DECISIÓN 073 |
| **Test** | `casos_dinamicos/test_tablas_decision.py::test_tabla_distribuciones_c1_sin_ceros_ni_negativos_no_deshabilita_ninguna` | `tests/unit/core/pipeline/test_disabled_negatives.py::test_solo_ceros_no_cambia` | `…/test_disabled_negatives.py::test_las_cinco_quedan_en_disabled_negatives_en_todos_sus_metodos` | `…/test_disabled_negatives.py::test_con_negativos_y_ceros_gana_disabled_negatives` |

Las que toleran ceros con advertencia (`DIST_ZEROS_TOLERATED`, DECISIÓN 061) se prueban distribución por distribución en
`tests/unit/core/etapa2/distributions/` (por ejemplo `test_gen_exponencial.py`, donde el método MV sí queda en
`disabled_zeros`).

---

## 4. Resultado

- **74 casos:** 28 de valores límite, 22 de clases de equivalencia y 24 columnas de cinco tablas de decisión. 45 tests
  nuevos en `tests/unit/casos_dinamicos/` (contando cada id de `parametrize`); el resto ya existía.
- **Ningún caso encontró un defecto.** Si uno lo hubiera encontrado, se registraría con la plantilla de
  `registro-defectos.md`.
- **Bordes que no se probaban en el borde:** antes de este bloque, la longitud se probaba con n = 8, 15 y 30 (no con
  9, 10 y 29); el tamaño de archivo, con 5 MB de más (no con 1 byte); Mann-Kendall, con n < 10 genérico; y
  `mes_inicio_anio` no tenía ningún test del rango en el endpoint.
