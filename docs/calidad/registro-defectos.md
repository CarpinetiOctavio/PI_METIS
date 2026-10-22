# Registro de defectos

TP integrador de Calidad de Software, bloque B10 (`docs/plan-tp-calidad-software.md`). Herramienta: GitHub Issues
(decisión D5 del plan), con la plantilla `.github/ISSUE_TEMPLATE/defecto.yml` y los labels de abajo.

## 1. Cómo se registra un defecto

1. Se abre un issue con la plantilla **Defecto**, que pide pasos, resultado esperado (con su fuente: contrato, ecuación
   de la tesis o decisión), resultado obtenido, severidad, prioridad, fase de detección, ambiente, commit, caso de
   prueba relacionado y test de regresión.
2. Se le ponen los labels `defecto`, `sev:…`, `prio:…` y `fase:…`.
3. Se escribe el test que lo reproduce y se comprueba que **falla** antes del fix.
4. El fix va en su PR; el mismo test tiene que **pasar** después.
5. **Un defecto se cierra solo con un test que lo cubra.** El comentario de cierre nombra el test (`ruta::nombre`) y el
   commit o PR del fix.
6. Un defecto que queda abierto a propósito puede tener ya su test de aceptación escrito con
   `pytest.mark.xfail(strict=True)`: documenta lo esperado y, cuando alguien lo corrige, el xfail estricto hace fallar
   la suite hasta que se saca la marca y se cierra el issue. Así se llevó D-10: abierto con su test en xfail
   el 09/10/2026 y corregido el mismo día en un PR propio, que sacó la marca.

## 2. Criterios

**Severidad**: el impacto en el usuario o en el resultado, no la urgencia.

| Label | Criterio |
|---|---|
| `sev:critica` | Resultado incorrecto en silencio o pérdida de datos. En METIS es lo más grave: un número de diseño mal calculado sin ninguna advertencia |
| `sev:alta` | Un flujo principal (análisis, login, historial) no se puede completar |
| `sev:media` | Falla visible con alternativa, o mensaje engañoso |
| `sev:baja` | Cosmético o información incompleta |

**Prioridad**: cuándo se corrige.

| Label | Criterio |
|---|---|
| `prio:alta` | Antes del próximo merge a `staging` |
| `prio:media` | En el sprint actual |
| `prio:baja` | Cuando haya lugar |

**Fase de detección**: alimenta la métrica "defectos por fase" (B11).

| Label | Dónde se encontró |
|---|---|
| `fase:auditoria` | Contrastando contra la tesis o las fuentes bibliográficas |
| `fase:desarrollo` | Un test nuevo lo encontró antes del merge |
| `fase:revision` | Revisión de PR, plan o análisis dirigido del código |
| `fase:ci` | El pipeline |
| `fase:uso-real` | Usando la app (navegador, demo, usuario) |

## 3. Defectos registrados

Los nueve defectos históricos del §2.7 del plan, cargados el 09/10/2026 con su evidencia. El 8 del plan se separó en
dos (D-08 y D-09): son dos fallas distintas, con tests distintos.

| ID | Issue | Defecto | Sev. | Fase | Estado | Test de regresión | Fix |
|---|---|---|---|---|---|---|---|
| D-01 | [#114](https://github.com/CarpinetiOctavio/PI_METIS/issues/114) | El stream se abortaba solo bajo StrictMode (F1) | alta | uso real | cerrado | `frontend/src/routes/stream/StreamPage.lifecycle.test.tsx` › "deja exactamente un stream vivo tras el doble montaje de StrictMode" | 5968713 (#19) |
| D-02 | [#115](https://github.com/CarpinetiOctavio/PI_METIS/issues/115) | Login 200 sin sesión confirmada, botón "muerto" (F3) | alta | uso real | cerrado | `frontend/src/auth/AuthProvider.test.tsx` › "login() throws SESSION_NOT_ESTABLISHED…" | 3a6c8ab (#19) |
| D-03 | [#116](https://github.com/CarpinetiOctavio/PI_METIS/issues/116) | Índice de Chow mapeado contra la serie mensual cruda | crítica | desarrollo | cerrado | `test_stream_agregacion_mensual.py::test_rechazar_atipico_sobre_serie_mensual_agregada_no_rompe_el_indice` | 67d96d0 (#49) |
| D-04 | [#117](https://github.com/CarpinetiOctavio/PI_METIS/issues/117) | Timestamps desalineados con una celda vacía en carga anual | crítica | revisión | cerrado | `test_stream_anual_celda_vacia.py::test_rechazar_atipico_con_celda_vacia_borra_el_anio_correcto` | 72b070c (#90) |
| D-05 | [#118](https://github.com/CarpinetiOctavio/PI_METIS/issues/118) | Archivo mensual desordenado perdía un año en silencio | crítica | revisión | cerrado | `test_pipeline_etapa1.py::test_bug_agregacion_mensual_desordenada_pierde_periodos_en_silencio_antes_bloquea_ahora` | 2ca473d (#74) |
| D-06 | [#119](https://github.com/CarpinetiOctavio/PI_METIS/issues/119) | Partición de Cramer personalizada respondía 500 | media | revisión | cerrado | `test_stream_cramer_particion.py::test_particion_custom_invalida_da_400_no_500` | 2e83068 (#26) |
| D-07 | [#120](https://github.com/CarpinetiOctavio/PI_METIS/issues/120) | Errores envueltos en `detail`, texto genérico en el login | media | uso real | cerrado | `test_estructura_error.py::test_error_con_codigo_responde_la_estructura_estandar` | b24eaaa (#106) |
| D-08 | [#121](https://github.com/CarpinetiOctavio/PI_METIS/issues/121) | GVE Momentos-L con la serie en orden ascendente | crítica | auditoría | cerrado | `test_gve.py::test_gve_ml_q100_serie_facundo` | auditoría de 4 fases (#15) |
| D-09 | [#122](https://github.com/CarpinetiOctavio/PI_METIS/issues/122) | Log-Normal 3p con exponente 1/4 en σ̂y (IV-116) | crítica | auditoría | cerrado | `test_lognormal3p.py::test_lognormal3p_momentos_sigma_y_raiz_cuadrada` | DECISIÓN 015 (#15) |
| D-10 | [#123](https://github.com/CarpinetiOctavio/PI_METIS/issues/123) | El warning de muestra chica de Mann-Kendall no llega a la lista agregada | baja | revisión | cerrado (09/10/2026) | `test_trend.py::test_muestra_chica_de_mann_kendall_llega_a_los_warnings_agregados` y `test_pipeline_etapa1.py::test_muestra_chica_de_wald_y_mann_kendall_sale_como_un_solo_warning` | `fix/mann-kendall-muestra-chica` |
| D-11 | [#130](https://github.com/CarpinetiOctavio/PI_METIS/issues/130) | El PDF declara α = 5 % en el subtítulo y 95 % en el correlograma con cualquier α (DECISIÓN 078) | media | uso real | cerrado (19/10/2026) | `unit/reportes/test_pdf.py::test_subtitulo_declara_el_alfa_del_analisis` y `unit/reportes/test_pdf.py::test_correlograma_rotula_la_confianza_del_analisis` | Kevinmass/PI_METIS#6, en el original por #132 |
| D-12 | [#134](https://github.com/CarpinetiOctavio/PI_METIS/issues/134) | Una celda vacía generaba dos advertencias (`CONTRACT_MISSING_VALUES` y `CONTRACT_NON_NUMERIC_VALUES`) | baja | revisión | corregido en `fix/revision-manual-21-10` | `casos_dinamicos/test_clases_equivalencia.py::test_celda_vacia_y_no_numerico_son_clases_distintas` (CE-07a–c) | `fix/revision-manual-21-10` |
| D-13 | [#135](https://github.com/CarpinetiOctavio/PI_METIS/issues/135) | Texto secundario del diálogo de pausa de Chow en 2,9:1 con el tema claro (RNF-07): la tarjeta al 55 % sobre el scrim | media | revisión | corregido en `fix/revision-manual-21-10` | `frontend/src/theme/contrast.test.ts` › "contraste del diálogo de pausa de Chow" (lee el % de `StreamPage.css`) | `fix/revision-manual-21-10` |
| D-14 | [#136](https://github.com/CarpinetiOctavio/PI_METIS/issues/136) | El CSV sin los puntos seleccionados se descargaba como `_sin_atipicos.csv` aunque no fueran atípicos | baja | uso real | corregido en `fix/revision-manual-21-10` | `frontend/src/routes/results/exclusiones.test.ts` › "nombreCsvSinExcluidos" y `Etapa1GraficosView.test.tsx` › "descargar entrega el CSV sin los excluidos…" | `fix/revision-manual-21-10` |
| D-15 | [#137](https://github.com/CarpinetiOctavio/PI_METIS/issues/137) | "Ver archivados" listaba también los análisis activos | media | uso real | corregido en `fix/revision-manual-21-10` | `frontend/src/routes/history/HistoryPage.test.tsx` › "D-15 — cada vista muestra solo lo suyo…" | `fix/revision-manual-21-10` |
| D-16 | [#138](https://github.com/CarpinetiOctavio/PI_METIS/issues/138) | El detalle del historial no mostraba las decisiones ante Chow: la serie se veía más corta sin explicación | media | uso real | corregido en `fix/revision-manual-21-10` | `HistoryDetailPage.test.tsx` › "C1 — …" (las dos formas y `{}`), `test_analysis_service_archive.py::test_chow_rechazados_lee_las_dos_formas` y `test_persistencia.py::test_cu01_persiste_una_decision_por_atipico_con_su_codigo` | `fix/revision-manual-21-10` |
| D-17 | [#139](https://github.com/CarpinetiOctavio/PI_METIS/issues/139) | El PDF marcaba un solo atípico de Chow cuando había varios (DECISIÓN 079) | media | uso real | corregido en `fix/revision-manual-21-10` | `unit/reportes/test_pdf.py::test_pdf_marca_todos_los_atipicos_de_chow`, `::test_pdf_de_un_analisis_anterior_a_la_079_marca_el_unico_atipico` y `::test_simulacion_nombra_todos_los_atipicos_que_quedan` | `fix/revision-manual-21-10` |
| D-18 | [#140](https://github.com/CarpinetiOctavio/PI_METIS/issues/140) | La partición personalizada de Cramer no se informaba en Resultados ni en el historial | baja | uso real | corregido en `fix/revision-manual-21-10` | `frontend/src/i18n/cramer.test.ts`, `Etapa1ResultView.test.tsx` › "partición de Cramer (D-18…)", `ResultsPage.test.tsx` › "D-18 — …" y `HistoryDetailPage.test.tsx` › "D-18 — …" | `fix/revision-manual-21-10` |
| D-19 | [#141](https://github.com/CarpinetiOctavio/PI_METIS/issues/141) | El tooltip de la serie temporal y del gráfico de Chow rotulaba el año como "T" (período de retorno); sin aclaración entre las vistas Configurado y Calendario | baja | uso real | corregido en `fix/revision-manual-21-10` | `Etapa1SerieTemporalChart.test.tsx` y `Etapa1ChowChart.test.tsx` › "tooltip del año (D-19)"; `InteractiveChart.test.tsx` › "xTooltipFormat…" | `fix/revision-manual-21-10` |

Las rutas de los tests del backend son relativas a `backend/tests/` (`integration/`, `unit/core/…`, `unit/api/`).

**Lectura rápida.** De los diez históricos (D-01 a D-10), 5 son críticos, y los cinco son resultados incorrectos en silencio: el motor siguió
corriendo y entregó un número o una serie mal armada sin avisar. Ninguno de los críticos lo encontró el uso de la
app: salieron de auditar contra la tesis (D-08, D-09), de un test escrito al desarrollar (D-03) o de revisar el
código (D-04, D-05). Los dos de uso real con severidad alta (D-01, D-02) son de la interfaz y motivaron las capas 1 y
2 de testing del frontend; los que solo son visibles con el sistema completo corriendo son los que hoy cubre el E2E
(B6).

## 4. Contraste rojo/verde: D-07

El test de regresión de D-07 corrido en dos commits, con la misma imagen del backend (Python 3.11):

| Corrida | Commit | Resultado |
|---|---|---|
| Rojo | `18e3019`, el padre del fix, con el test copiado de `b24eaaa` | **1 falla, 3 pasan**: `assert 'detail' not in {'detail': {'error': {'codigo': 'DIST_SELECTION_INVALID', …}}}` |
| Verde | `b24eaaa`, el fix (PR #106) | **4 pasan** |

La falla en rojo es exactamente el defecto: el body llega envuelto en `detail`. Las otras tres pruebas del archivo
(que un `detail` de texto, una ruta inexistente y un 422 de Pydantic siguen igual) pasan en los dos commits: el fix
no cambió lo que no tenía que cambiar. Salida completa en `evidencia/D07-rojo.txt` y `evidencia/D07-verde.txt`.

Cómo reproducirlo:

```bash
git worktree add /tmp/rojo 18e3019
git show b24eaaa:backend/tests/unit/api/test_estructura_error.py > /tmp/rojo/backend/tests/unit/api/test_estructura_error.py
cd /tmp/rojo/backend && pytest tests/unit/api/test_estructura_error.py -v     # rojo
git -C /tmp/rojo checkout b24eaaa -- . && pytest tests/unit/api/test_estructura_error.py -v   # verde
```

D-01 tiene el mismo contraste en la historia del repo: su test se commiteó en rojo (`3ce3aae`, "red before
fixing") antes del fix (`5968713`).

## 5. Lo que falta

- **Tablero de GitHub Projects** (D5 del plan): el token de `gh` de esta máquina no tiene el scope `project`. Con
  `gh auth refresh -s project` se puede crear y sumar los issues con el label `defecto`; los issues ya están
  completos sin él.
- Los defectos que encuentren los casos de prueba de B8 y los E2E de B6 se registran con la plantilla, igual que
  estos.
