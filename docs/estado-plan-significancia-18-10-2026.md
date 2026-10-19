# Estado de ejecución — plan de significancia y fixes (18/10/2026)

Para el agente que siga. Plan: `docs/plan-significancia-y-fixes-18-10-2026.md`. Se trabaja en el **fork
`Kevinmass/PI_METIS`** (Octavio todavía no dio permisos en el original); Kevin mergea después.

## Entorno (importante)

- Worktree aparte: `C:\Users\kevin\Desktop\Tesis\15-10-26\PI_METIS-sig`. El clon principal
  (`...\15-10-26\PI_METIS`, rama `feature/tp-calidad-b12`) tiene trabajo de B12 sin commitear: **no tocarlo**.
- No hay venv ni Node en el host. Todo corre en Docker, con `export MSYS_NO_PATHCONV=1` en Git Bash:
  - Backend: `docker run --rm -v "<worktree>/backend:/app" -w /app pi_metis-backend:latest sh -c "ruff check metis; ruff format --check metis; pytest -m 'unit or integration' -q -p no:cacheprovider"`
  - Tests de BD: Postgres descartable `metis-sig-pg` en la red `metis-sig-test`. Para levantarlo de nuevo:
    `docker run -d --name metis-sig-pg --network metis-sig-test -e POSTGRES_USER=t -e POSTGRES_PASSWORD=t -e POSTGRES_DB=metis postgres:15`.
    Después, en el contenedor del backend, `--network metis-sig-test -e DATABASE_URL=postgresql+asyncpg://t:t@metis-sig-pg:5432/metis -e METIS_REQUIRE_DB=1`,
    con `alembic upgrade head` antes de `pytest tests/integration/db`.
  - Frontend: `docker run --rm -v "<worktree>/frontend:/app" -v metis_fe_nm:/app/node_modules -w /app node:20-alpine sh -c "npx tsc -b; npx eslint .; npx vitest run"`
    (el volumen `metis_fe_nm` ya tiene `npm ci` hecho).
  - Catálogo de errores: `bash scripts/check-error-catalog.sh` desde la raíz del worktree.
- Los heredocs de bash con `\n` o con ciertos caracteres se rompen: para editar, usar Write/Edit o un script
  Python en el scratchpad.
- `ResultsPage.test.tsx` tiene un flake de carga ("renders test groups as collapsed..."): pasa al reintentar.

## Ramas (apiladas, ninguna pusheada ni con PR todavía)

| Rama | Base | Estado |
|---|---|---|
| `feature/exploracion-simulada` | `origin/staging` | **Bloque A completo**, 2 commits (plan + bloque A) |
| `feature/significancia-configurable` | `origin/staging` | **Bloque B completo**, 1 commit (`a3ce5c0` o el amend siguiente) |
| `feature/chow-todos-los-atipicos` | `feature/significancia-configurable` | **Bloque C completo**, commit WIP + cierre |
| `fix/chow-no-ejecutado-valores-no-validos` | `feature/chow-todos-los-atipicos` | **Bloque D completo**, 1 commit |

A y B son independientes; C depende de B. Hay que hacer push y abrir un PR por bloque hacia `staging` del fork
(el de C recién después de mergear B, o apuntado a la rama de B).

## Bloque A — hecho

`Etapa2Explorador` pide cada exploración también sin los puntos excluidos (simulate-exclusion con `seleccion`) y
hay un único selector "Original / Sin los puntos excluidos". El backend suma `etapa2.seleccion.estado`. Hay
revisión de la DECISIÓN 071 y está documentado en `api-contracts.md`. Tests: backend 24, frontend 13 + 12.
**Falta:** el recorrido en el navegador (Capa 4).

## Bloque B — hecho (DECISIÓN 078)

- `core/etapa1/significancia.py`: `NIVELES_ALFA`, `z_bilateral`, `KS_Z_CRIT`. `alfa` en las 8 pruebas y en
  `ejecutar_etapa1`, `simular_exclusion`, el stream (también en la segunda pasada), la persistencia
  (`configuracion.alfa`; los análisis viejos dan `alfa_implicito`), el historial, el PDF, la UI (selector en
  ConfigPage, α en los resultados y en el historial) y el paso a paso (sin 1,96 ni α=0,10 escritos a mano).
- Código nuevo `CONTRACT_ALFA_INVALID`. Revisión de la DECISIÓN 018. `constraints.md`, `formulas-etapa1.md`,
  `statistical-pipeline.md` y `core-etapa1-implementation.md` están actualizados. CE-06 en
  `docs/calidad/casos-de-prueba.md`.
- No regresión: `backend/tests/unit/core/pipeline/test_no_regresion_alfa.py` + `referencia_etapa1_alfa_005.json`
  (las 9 estaciones, Las Tapias y `docs/series prueba`) dan idéntico con α = 0,05. K_N(30, α = 10 %) = 2,5651,
  contra 2,563 de la tabla.
- **Falta:** el recorrido en el navegador. La consulta opcional a Facundo sobre la tolerancia de Anderson queda
  anotada en la DECISIÓN 078.

## Bloque C — hecho (DECISIÓN 079)

Backend completo y probado (893 tests unitarios y de integración + 8 de BD en verde):
- `calcular_chow`: `TestResult.valores_atipicos` `[{indice, valor, z, lado}]` ordenados por |z|;
  `terminos.limite_inferior/limite_superior`; `desglose[i].fuera`. Con α = 5 % la no regresión sigue idéntica.
- La serie diaria de 40 años da 1994 y 2005 (los dos del lado bajo).
- Stream: `outlier_detected` = `{session_id, atipicos:[{indice, periodo, valor, z, lado}], valor_atipico}`. Los
  rechazados se excluyen juntos con `aplicar_exclusiones`, y la segunda pasada no vuelve a pausar.
  `_describir_chow_tras_decision` reescribe el warning de Chow (aceptados, o atípicos nuevos en la segunda
  pasada).
- `POST /outlier-decision` = `{session_id, decisiones:[{indice, decision}]}`. Errores: 400
  `OUTLIER_DECISION_INVALID` y 404 `SESSION_NOT_FOUND`. Se agregó el prefijo `OUTLIER` a
  `scripts/check-error-catalog.sh` y un addendum a la DECISIÓN 038.
- `decisiones.chow = {atipicos:[{..., decision, codigo}]}`, con `codigo` `TEST_OUTLIER_*_BY_USER` por punto. El
  PDF lee la forma nueva y la vieja `{accion, dato}`.
- `api-contracts.md` (outlier-decision, decisiones, catálogo) y `statistical-pipeline.md` están actualizados.

Frontend, hecho y en verde (512 tests, tsc y eslint limpios):
- Tipos `AtipicoChow`/`AtipicoDetectado`/`DecisionAtipico`. `resolveOutlier(Record<indice, decision>)`.
- Modal nuevo `routes/stream/DecisionAtipicos.tsx`: una fila por atípico, dos botones iguales y "Continuar"
  habilitado recién con todas las filas decididas. La tarjeta del modal pasa a 560px.
- `InteractiveChart`: opción `shape` ("diamond"/"square"). `Etapa1ChowChart`: franjas del servidor (con
  respaldo para análisis viejos), todos los atípicos con rombo y leyenda de texto.
- Panel de exclusión: `sugeridos: number[]`. Desglose de Chow con `data-fuera`. Interpretación de Chow con los
  umbrales y la regla de Bulletin 17B.

**Cierre del bloque C (19/10/2026):**
- `docs/decisiones/decision079.md` escrita y sumada al índice. `formulas-etapa1.md` §9 con la regla de los dos
  umbrales, la lista y las condiciones previas en el orden real (negativos primero, DECISIÓN 073).
- La interpretación de Chow con umbrales ya no dice "a la espera de tu decisión": se lee en Resultados, después
  de la pausa.
- Tests de frontend nuevos: interpretación con `valores_atipicos` (y análisis viejo), filas `data-fuera` del
  desglose y varios `sugeridos` en el panel de exclusión.
- E2E: `rechazarAtipico` (`e2e/helpers/flujo.ts`) rechaza todas las filas y confirma con "Continuar con estas
  decisiones". No se corrió Playwright (necesita el despliegue).
- Revisado el diff del WIP: sin cambios de solo formato en archivos ajenos.
- Corrida: backend 896 unitarios + integración, 8 de BD (1 skip de Mailpit), frontend 517, tsc/eslint/ruff de
  `metis/` limpios, catálogo de errores sincronizado.
- **Queda pendiente:** el gráfico de Chow dentro del diálogo (anotado en la 079) y el recorrido en el navegador.

## Bloque D — hecho (revisión 19/10/2026 de la DECISIÓN 073)

- `TestResult.valores_no_validos` = `[{indice, valor}]` en Chow no ejecutada (negativos; ceros con ZEROS o
  CONDITION). Campo propio, `explicacion` sigue en `null`. Serializado en `result_etapa1`.
- Gráfico de Chow: aviso arriba, sin franjas, los valores con un cuadrado `--warn` y leyenda propia.
  `tipoVariable` llega desde `ResultsPage` y `HistoryDetailPage` por `Etapa1ResultView` → `Etapa1GraficosView`.
- Texto: "físicamente imposible" solo para **negativos en caudal**. Un cero en caudal es un dato posible, así que
  no se lo llama imposible: esto se aparta del texto del plan, que decía "negativos (o ceros)". Con "Otro", sin
  sugerencia de excluir.
- Panel de exclusión: prop `noValidos`, marca cuadrada `--crit` y leyenda "valor no válido para Chow".
- Tests: `tests/unit/core/etapa1/test_chow_valores_no_validos.py`,
  `tests/unit/services/test_simular_exclusion_sin_negativos.py` (excluidos los negativos, Chow corre), 4 de
  `Etapa1ChowChart.test.tsx` y 1 de `Etapa1GraficosView.test.tsx`.
- Docs: revisión en `decision073.md` y su fila del índice, y nota en `statistical-pipeline.md`.
- Corrida: backend 903, BD 8 (1 skip de Mailpit), frontend 522, tsc/eslint/ruff limpios, catálogo OK.

## Verificación final pendiente (de todo el plan)

- Recorrido en el navegador de A–D. El stack de desarrollo (`pi_metis-*`) monta el clon principal, no el
  worktree: hay que levantar un despliegue desde el worktree (`scripts/deploy-local.sh`, ocupa el puerto 80) o
  pedirle a Kevin que lo haga.
- Push de las ramas, PRs al `staging` del fork y CI de los ocho jobs en verde.
- Cifras para el libro: la cantidad de tests sale de la última corrida.
- Obsidian: actualizar `Proyectos/PI_METIS/Estado.md` y `Próximos pasos.md` cuando se cierre.
