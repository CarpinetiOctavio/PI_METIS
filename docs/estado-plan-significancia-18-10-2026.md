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
| `feature/chow-todos-los-atipicos` | `feature/significancia-configurable` | **Bloque C a medias**, commit WIP |
| (sin crear) bloque D | saldría de la rama de C | sin empezar |

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

## Bloque C — hecho hasta acá (DECISIÓN 079, el archivo todavía no existe)

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

**Falta del bloque C:**
1. Escribir `docs/decisiones/decision079.md` y sumarla al `README.md` del índice. El contenido está en la
   sección C del plan: problema, regla de Bulletin 17B, una sola pasada, enmascaramiento declarado, una sola
   pausa, compatibilidad y códigos.
2. `formulas-etapa1.md` §9: reemplazar el veredicto de `max(Z_i)` por la regla de los dos umbrales y la lista.
3. Tests de frontend que faltan: la interpretación de Chow con `valores_atipicos` en `explicaciones.test.ts`,
   la fila `data-fuera` en `Etapa1Desglose.test.tsx` y `sugeridos` múltiples en el panel de exclusión.
4. Opcional, del plan: el gráfico de Chow dentro del diálogo de la pausa. Si no entra, anotarlo como pendiente
   en la 079.
5. E2E (`frontend/e2e/`): revisar si algún escenario pasa por la pausa de Chow y adaptar los clicks (ahora hay
   que hacer clic en "Continuar con estas decisiones").
6. Revisar `git diff` por cambios que sean solo de formato de `ruff format` en archivos ajenos, y revertirlos
   (ya pasó en B).

## Bloque D — sin empezar

Ver la sección D del plan (Chow no ejecutado por negativos o ceros: mensaje, marcas y revisión de la DECISIÓN
073). Sugerencia: no poner `valores_no_validos` dentro de `explicacion`, porque el frontend usa
`explicacion === null` como señal de "no ejecutada". Mejor un campo propio de `TestResult` (como
`valores_atipicos`), y en el panel de exclusión una prop `noValidos` con una marca distinta de "sugerido".

## Verificación final pendiente (de todo el plan)

- Recorrido en el navegador de A–D. El stack de desarrollo (`pi_metis-*`) monta el clon principal, no el
  worktree: hay que levantar un despliegue desde el worktree (`scripts/deploy-local.sh`, ocupa el puerto 80) o
  pedirle a Kevin que lo haga.
- Push de las ramas, PRs al `staging` del fork y CI de los ocho jobs en verde.
- Cifras para el libro: la cantidad de tests sale de la última corrida.
- Obsidian: actualizar `Proyectos/PI_METIS/Estado.md` y `Próximos pasos.md` cuando se cierre.
