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
   la suite hasta que se saca la marca y se cierra el issue (D-10).

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
| D-10 | [#123](https://github.com/CarpinetiOctavio/PI_METIS/issues/123) | El warning de muestra chica de Mann-Kendall no llega a la lista agregada | baja | revisión | **abierto** | `test_trend.py::test_muestra_chica_de_mann_kendall_llega_a_los_warnings_agregados` (`xfail(strict=True)`) | — |

Las rutas de los tests del backend son relativas a `backend/tests/` (`integration/`, `unit/core/…`, `unit/api/`).

**Lectura rápida.** 5 de los 10 son críticos, y los cinco son resultados incorrectos en silencio: el motor siguió
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
