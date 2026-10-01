# Plan post-pasada 4 — deuda, hardening y alcance restante hacia M2/M3

**Fecha.** 5 de Agosto de 2026.
**Entradas.** `docs/frontend/informe-resultados-arreglo-ui-rota.md`, `docs/frontend/feedback-ux-pendiente-analisis.md`,
`docs/frontend/plan-mejora-frontend-pasada4.md`, `docs/frontend/informe-resultados-pasada4.md` (cierre real, ya en `staging`).
**Qué es este documento.** Análisis de calidad de las dos últimas pasadas + plan ejecutable. La Pasada 5 (§3) está
escrita para que un agente la ejecute tal cual; las pasadas 6-8 (§4-§6) están acotadas y ordenadas, pero requieren
las decisiones de §7 antes de codear.

---

## 0. Corrección de premisa — el estado que hay que mirar no es el de los documentos citados

Los dos documentos que dispararon este análisis (`informe-resultados-arreglo-ui-rota.md` y
`feedback-ux-pendiente-analisis.md`) describen el estado del **31/07/2026**. Verificado contra `origin/staging`:

- `fix/frontend-ui-integracion` se mergeó como **PR #19** (`3b9d381`).
- La **pasada 4 completa** se ejecutó y mergeó entre el 31/07 y el 01/08 en tres PRs apilados: **#20** (Bloques A/B/C),
  **#21** (Bloque D, `preview-columns`), **#22/#23** (Bloques E+F, archivado de historial y `PendingBadge`).
- Existen `docs/decisiones/decision045.md`, `047.md` y `048.md`, y `docs/frontend/informe-resultados-pasada4.md`.

**El checkout local está desactualizado y parado sobre una rama ya mergeada** (`fix/frontend-ui-integracion`, HEAD
`7406739`, último `fetch` del 31/07). Además hay tres worktrees huérfanos en `.worktrees/` y una copia local sin
commitear de `plan-mejora-frontend-pasada4.md` que ya existe en `staging`. **Paso 0 obligatorio antes de cualquier
otra cosa:** `git fetch origin && git checkout staging && git pull`, borrar los worktrees consumidos
(`git worktree list` → `git worktree remove`), y descartar la copia local del plan.

Los cuatro ítems del feedback de UX que entraron en alcance (1, 2, 4, 5a) **están implementados**. Quedan fuera, tal
como se decidió: punto 3 (`tipo_variable` extensible) y punto 5b (búsqueda por nombre de archivo).

---

## 1. Calidad de lo hecho — evaluación

### 1.1 Lo que está genuinamente bien

- **Reproducir antes de arreglar.** El Bloque 0 de la pasada de arreglo escribió `StreamPage.lifecycle.test.tsx` en
  rojo *antes* de tocar `StreamPage.tsx`, con contraprueba diferencial en el navegador (sacar `<StrictMode>`, ver que
  el stream avanza, revertir). Es la disciplina correcta y es lo que evita "arreglar" un síntoma.
- **La capa de test que faltaba se agregó donde vivía el bug.** `renderPage.tsx` convierte StrictMode en regla, no en
  algo que recordar por archivo; `routes.navigation.test.tsx` recorre el array `routes` real. Antes de esto, "¿existe
  algún camino de clicks que llegue a `/history`?" era una pregunta que ningún test podía responder.
- **Honestidad sobre premisas erradas.** Los tres ítems de §1 del informe de arreglo (Cramer ya resuelto, MSW evitado,
  `FRONTEND_ORIGIN`/`FRONTEND_URL` no eran duplicación) los verifiqué contra el código y son ciertos. Lo mismo con los
  cuatro de la pasada 4 (`z-index: 0` pintaba encima, `PARSE_NO_USABLE_COLUMNS` era código muerto). Un informe que
  contradice a su propio plan y lo justifica vale más que uno que reporta 100 % de cumplimiento.
- **Las decisiones difíciles se escalaron en vez de resolverse unilateralmente.** El conflicto entre `<CountUp>`
  animado y las aserciones síncronas de `StreamPage.integration.test.tsx` se llevó al usuario con archivo y línea, y
  se resolvió con un overlay decorativo (`::before` + `content: attr()`, `aria-hidden="true"`, texto real presente e
  inmediato en el DOM). **Verificado: la solución es correcta** — el nodo accesible nunca desaparece, solo baja a
  `opacity: 0`, y el overlay está fuera del árbol de accesibilidad.
- **G1 (JetBrains Mono nunca cargada) fue un hallazgo de primer orden.** Todo METIS se renderizaba con el monospace
  por defecto del navegador. El diagnóstico del feedback describía el síntoma ("se ve simple"); la pasada 4 encontró
  la causa y la arregló en un commit.
- **DECISIÓN 047 tiene el argumento correcto:** parsear las cabeceras en el backend garantiza que el dropdown ofrezca
  exactamente las columnas que `pandas` va a leer. Un parseo JS paralelo podía divergir del real.

### 1.2 Debilidades reales del proceso, no del código

- **La verificación final del Bloque G quedó a mitad: 5 de 14 puntos sin evidencia directa** (fondo de la entrada,
  micro-interacciones, modal de atípico, `prefers-reduced-motion`, CPU), por límites de la herramienta de navegador de
  esa sesión. Está declarado sin ocultarlo, lo cual es correcto — pero **es exactamente la capa que faltó la vez
  anterior y produjo la UI rota**. Cubrirlo con "cobertura indirecta de tests unitarios" es precisamente el argumento
  que ya falló una vez: 98 tests en verde y la aplicación rota.
- **Tres PRs apilados, mergeados con SonarCloud y CI "a cargo del usuario" mientras el trabajo seguía en paralelo.**
  Funcionó, pero repite en menor escala el patrón de acumular trabajo sin verificación intermedia.
- **Una desviación del plan no quedó registrada.** El plan §6 D2 pedía leer **solo las primeras filas** (`nrows`). La
  implementación real (`leer_columnas_preview`) llama a `_leer_dataframe(content)` completo y después hace
  `.head(MUESTRA_MAX)` — necesita el DataFrame entero para devolver `filas=len(df)`. No es un error de comportamiento,
  pero es una desviación con consecuencia de rendimiento/memoria que ni el informe ni la DECISIÓN 047 mencionan.

---

## 2. Hallazgos nuevos — verificados contra `origin/staging`

| # | Hallazgo | Evidencia | Severidad |
|---|---|---|---|
| **H1** | **Colisión de número de decisión.** `DECISIÓN 045` quedó asignada a "fondos animados en Canvas 2D", pero cuatro documentos vigentes siguen diciendo que 045 es la escotilla SMTP de desarrollo. | `.claude/rules/sprint.md:673`, `informe-resultados-arreglo-ui-rota.md:35,71,197`, `plan-arreglo-ui-rota.md:171` vs. `docs/decisiones/decision045.md:1` y `README.md:151` | Alta (documental) |
| **H2** | **Ningún `client_max_body_size` en las dos configuraciones de nginx.** El default de nginx es **1 MB**: a través del reverse proxy, cualquier Excel/CSV de más de 1 MB recibe **413** en `/analysis/stream` y `/analysis/preview-columns`. En `npm run dev` (Vite → `:8000` directo) funciona. Es literalmente la clase de defecto "anda en dev, roto en producción" que la pasada anterior existió para eliminar. | `nginx/nginx.conf` y `frontend/nginx.conf` — cero coincidencias de `client_max_body_size` | **Bloqueante** |
| **H3** | **`POST /analysis/preview-columns` es anónimo, sin cap de tamaño y lee el archivo completo en memoria** (`await archivo.read()` → `_leer_dataframe` completo). No hay auth, ni límite de bytes, ni rate limit. Un POST de 500 MB es un OOM del contenedor backend. | `backend/metis/api/v1/analysis.py:24-44`, `core/validacion/parser.py:16-41` | Alta |
| **H4** | **DECISIÓN 036 sigue viva y ahora es alcanzable por API.** `cramer_particion` distinto de `"default"` llega como `str` a `calcular_cramer`, que indexa `particion["n1_pct"]` → `TypeError` no manejado = **500**, no 400. Hoy solo lo tapa que el frontend deshabilite el botón. | `decision036.md`, `api-contracts.md` (nota de implementación) | Media |
| **H5** | **`core/etapa2/` está completo y jamás cableado.** `ejecutar_etapa2()` existe con las 13 distribuciones; `analysis_service.py` escribe `etapa2=None` hardcodeado (L413). El costo real de M2 es **cableado + endpoints**, no implementar el motor. Falta una sola pieza de core: nada produce `EventoDiseno` (el tipo existe, ningún módulo lo construye) — se resuelve llamando `cuantil()` de la distribución elegida para cada período de retorno. | `services/analysis_service.py:413`, `core/pipeline/pipeline_etapa2.py:58`, `core/etapa2/types.py:34` | Oportunidad |
| **H6** | **DECISIÓN 037 (`etapas` recibido y descartado) pasa de inocuo a bloqueante** en el momento en que Etapa 2 se exponga: el backend no puede saber si el usuario pidió `[1]` o `[1,2]`. Sube de prioridad como precondición de la Pasada 6. | `api/v1/analysis.py:53` (`etapas: str = Form("1")`, nunca usado) | Media, escala a Alta |
| **H7** | **Los tokens de movimiento nuevos (`--t-fast/mid/slow`, `--ease-out`) están fuera de toda verificación automática.** `tokenParity.test.ts` solo parsea valores hexadecimales. Está reconocido en el plan de pasada 4 y la decisión de no forzarlos ahí es correcta — pero la regla "ninguna duración hardcodeada fuera del bloque de tokens" quedó como convención sin chequeo. | `frontend/src/theme/tokenParity.test.ts` | Baja |
| **H8** | `<CountUp>` — **revisado y sin objeción.** El overlay es `aria-hidden`, el texto real nunca sale del DOM. No requiere acción; se anota para que nadie lo "arregle" sin entender por qué está así. | `frontend/src/components/CountUp.tsx:73-78` | — |

---

## 2.5 Regla de cadencia de PRs — aplica a todas las pasadas de este roadmap

El antecedente concreto: la pasada de arreglo acumuló **18 commits locales sin push ni PR**, y el conjunto
arreglo + pasada 4 llegó a ~60 commits que terminaron partidos en pocos PRs enormes, decididos *después* de que el
trabajo ya estaba hecho. Un PR de ese tamaño no se revisa — se aprueba. Y es precisamente el patrón que produjo la UI
rota: trabajo apilado sin verificación intermedia.

**Las cinco reglas, no negociables en este roadmap:**

1. **El corte de PRs se decide ANTES de escribir código**, en el plan de la pasada — nunca al final, mirando el `git log`.
   Cada pasada de acá en adelante declara su tabla de PRs por adelantado (las de §3-§6 ya la tienen).
2. **Techo duro: 8 commits o ~400 líneas de diff productivo por PR.** Al llegar al techo se corta y se abre el PR,
   aunque el bloque no esté "redondo". Si un bloque no entra en 8 commits, el bloque está mal dividido.
3. **Push al final de cada día de trabajo**, aunque el PR siga en borrador. Nada vive solo en un checkout local más de
   una jornada. La rama en `origin` con PR en borrador es gratis; 18 commits invisibles no.
4. **Un PR no mezcla capas.** Migración de esquema, cambio de contrato de API y trabajo visual **nunca** viajan juntos.
   Es la regla que la pasada 4 ya aplicó bien con sus tres PRs apilados — acá se generaliza.
5. **Cada PR cierra con su propia verificación**, no con la del final de la pasada: suite en verde, lint, y —si toca
   `frontend/`— evidencia de navegador posterior al último commit del PR (`testing.md`, capa 4). Un PR sin su
   verificación no se mergea aunque el siguiente ya esté empezado.

**Parada de control entre PRs.** Después de mergear cada PR: `git checkout staging && git pull`, confirmar los cuatro
jobs de CI y el gate de SonarCloud, y recién entonces abrir la rama siguiente. Los PRs apilados (base = PR anterior)
son válidos cuando hay dependencia real, como en la pasada 4 — pero se mergean en orden y no se abren más de tres a la vez.

---

## 3. Pasada 5 — deuda y hardening (ejecutable, `fix/deuda-pasada4`)

Sale de `staging` actualizada. Es corta a propósito: nada acá inventa alcance, todo cierra algo abierto.

### Cortes de PR de esta pasada — decididos ahora

| PR | Rama | Bloques | Por qué corta acá | Techo |
|---|---|---|---|---|
| **5.1** | `fix/upload-limits` | A1-A3 | Bloqueante de producción, toca nginx + backend + contrato de error. Mergeable y verificable solo. | ~4 commits |
| **5.2** | `docs/higiene-decisiones` | B1-B3 | Solo documentación. No debe esperar a nada ni retrasar a nada — se puede mergear el mismo día. | ~2 commits |
| **5.3** | `fix/cramer-particion-400` | D | Cambio de comportamiento de un endpoint. Diff mínimo, revisión de 5 minutos. | ~2 commits |
| **5.4** | (sin rama de código) | C | Verificación/decisión, no implementación. Si sale C1a → addendum al informe (parte de 5.2). Si sale C1b → PR propio con la DECISIÓN 046 escrita **antes** de tocar nada. | — |

5.1, 5.2 y 5.3 son **independientes entre sí**: se pueden abrir en paralelo desde `staging` y mergear en cualquier
orden. Ninguno espera al otro. Esa independencia es el punto — si uno se traba en revisión, los otros dos igual entran.

### Bloque A — Límites de subida (H2 + H3). Prioridad 0.

**A1.** `client_max_body_size` explícito en las dos configuraciones de nginx (`nginx/nginx.conf` en el `location /api/`
y `frontend/nginx.conf`), con el mismo valor. Proponer **10 MB** y justificarlo con un número real: medir el tamaño de
un Excel de 40 años × 2 columnas (la serie más grande de la tesis de Facundo) y dejar el cálculo escrito en el commit.

**A2.** Cap del lado del backend, independiente de nginx — nginx no es el único camino (`:8000` está mapeado al host
por diseño, ver `architecture.md`). Rechazar por tamaño **antes** de leer el archivo entero, en `preview-columns` y en
`stream`. Código de error nuevo → `api-contracts.md` **en el mismo commit** (regla de DECISIÓN 038, verificada por
`scripts/check-error-catalog.sh`) y su entrada en `i18n/errors.es.ts`.

**A3.** Test de regresión por cada camino: archivo por encima del límite → código correcto y status correcto, no 500 ni
timeout. En el frontend, el error tiene que llegar a la UI como mensaje, no como pantalla colgada.

**Criterio de aceptación:** subir a través de nginx (`http://localhost/...`) un archivo apenas por debajo del límite
(pasa) y otro apenas por encima (rechazo limpio con el código nuevo, en las dos rutas).

### Bloque B — Higiene documental (H1). Prioridad 0, cuesta minutos.

**B1.** Asignar un número **libre** a la escotilla SMTP de desarrollo (hoy 049 es el primero libre — confirmar contra
`docs/decisiones/README.md` al momento de escribir) y corregir las cuatro referencias que apuntan a 045: `sprint.md:673`,
`informe-resultados-arreglo-ui-rota.md:35,71,197`, `plan-arreglo-ui-rota.md:171`. **Corregir, no reescribir la
historia:** anotar la colisión, no borrar el rastro — es el criterio que este repo ya usa (tachado, no eliminado).

**B2.** Addendum a `decision047.md`: la implementación lee el DataFrame completo, no `nrows`, y por qué (necesita
`filas=len(df)`). Si con el cap de A2 el costo deja de importar, decirlo explícitamente.

**B3.** Nota de rendimiento en `decision045.md`: dejar registrado que el presupuesto de CPU de B7 (§4 del plan de
pasada 4) **no se midió** — es uno de los cinco puntos sin verificar del Bloque G.

### Bloque C — Cerrar los 5 puntos sin verificar del Bloque G (H3 del informe de pasada 4). Prioridad 1.

Los cinco (fondo de la entrada, micro-interacciones hover/focus, modal de atípico, `prefers-reduced-motion`, CPU en
reposo) **necesitan un navegador real con DevTools y capacidad de adjuntar archivo**, que la sesión de la pasada 4 no
tuvo. Dos vías, elegir una **antes** de arrancar el bloque:

- **C1a — Verificación manual con evidencia.** Kevin u Octavio corren el recorrido con capturas, y el resultado se
  registra en un addendum de `informe-resultados-pasada4.md`. Costo casi cero, cierra la brecha de evidencia, pero no
  es repetible.
- **C1b — Escribir `docs/decisiones/decision046.md` y habilitar Playwright.** Contradice `constraints.md` ("Scope V1.0
  — lo que NO entra" excluye E2E automatizado), así que **la decisión se escribe primero, y la revisión de esa
  exclusión es el contenido de la decisión**. Argumento a favor ya documentado: cinco de los doce defectos de la
  pasada de arreglo (F1, F4, F5, F6, F9) solo eran detectables desde esa capa.

**Recomendación:** C1a ahora (cierra la deuda de evidencia esta semana) y C1b como decisión escrita pero implementada
recién cuando Etapa 2 esté cableada — un E2E sobre un flujo que todavía es mitad mock rinde poco.

### Bloque D — DECISIÓN 036, dejar de devolver 500 (H4). Prioridad 1.

No implementa la partición personalizada — **cierra el 500**. Validar `cramer_particion` en el borde
(`api/v1/analysis.py`): si no es `"default"`, responder **400** con código catalogado. Es coherente con las tres
opciones abiertas de la DECISIÓN 036 (ninguna queda descartada) y elimina un 500 alcanzable por cualquier cliente HTTP
que no sea nuestro propio frontend — incluido CU-03 el día que exista.

### Bloque E — Verificación de cierre

`npx vitest run`, `npm run lint`, `npm run build`, `ruff check`/`format --check`, `pytest -m unit` (todo dentro del
contenedor, ver `CLAUDE.md`), `scripts/check-error-catalog.sh`, y el stack completo por nginx con las pruebas de A3.
Informe de cierre con el formato de siempre.

---

## 4. Pasada 6 — Etapa 2 real de punta a punta (desbloquea M2)

Es el gap más grande del proyecto y, por H5, **más barato de lo que sugiere el estado del frontend**: el motor está
implementado y probado; lo que falta es exponerlo.

**Precondición dura: cerrar DECISIÓN 037 (H6).** Sin `etapas` cableado, el backend no puede saber si correr Etapa 2.
Es el primer commit de la pasada, no un detalle.

| Bloque | Contenido | Notas |
|---|---|---|
| 6.1 | Cablear `ejecutar_etapa2()` en `analysis_service.py`: emitir `result_etapa2_ranking` por SSE y persistir `etapa2` en `analysis_results` (hoy `None` hardcodeado). | El evento ya está especificado en `statistical-pipeline.md`. |
| 6.2 | Función de eventos de diseño en `core/etapa2/` que produzca `EventoDiseno` llamando `cuantil()` por período de retorno. **Única pieza de core que falta.** | Guard `p ∈ (0,1)` sigue sin propagarse a 11 de las 13 distribuciones (`sprint.md`, "Fase 4.5") — hacerlo acá. |
| 6.3 | `POST /api/v1/analysis/design-events` real, según el contrato ya escrito en `api-contracts.md`. | El contrato existe; implementarlo tal cual, o modificar el contrato explícitamente. |
| 6.4 | Frontend: `RankingPage` y `DesignEventsPage` contra datos reales; retirar `PendingBadge` y los mocks de `src/mocks/`. | Cierra DECISIÓN 042. |
| 6.5 | Gráficos con eje temporal — **dos versiones obligatorias** (calendario e hidrológico) por `constraints.md`. Hoy no existe ninguna. | Es alcance grande; evaluar si se separa en su propia pasada. |

### Cortes de PR de la Pasada 6

| PR | Rama | Bloques | Por qué corta acá |
|---|---|---|---|
| **6.0** | `feat/etapas-cableado` | DECISIÓN 037 | Precondición. PR propio, chico, mergeado **antes** de que empiece 6.1. Nada de Etapa 2 arranca sobre esto sin mergear. |
| **6.1** | `feat/etapa2-cableado` | 6.1 + 6.2 | Backend puro: servicio + core. Sin frontend de por medio, se revisa mirando salida real del pipeline. |
| **6.2** | `feat/design-events-endpoint` | 6.3 | Endpoint nuevo = contrato nuevo. Revisión propia, igual que `preview-columns` en la pasada 4. |
| **6.3** | `feat/etapa2-frontend` | 6.4 | Retira mocks y `PendingBadge`. No mezclar con backend: si el backend falla en revisión, el frontend no queda rehén. |
| **6.4** | `feat/graficos-eje-temporal` | 6.5 | **Evaluar sacarlo a su propia pasada.** Dos versiones obligatorias por `constraints.md` y hoy no existe ninguna — es alcance de pasada entera, no de un PR. |

**Bloqueantes de dominio que hay que llevar a Facundo antes, no durante:** comportamiento ante ceros de las 5
distribuciones pendientes, ME/MC en otras distribuciones, y Gamma 3p + MPP (`pendientes-facundo.md`). Ninguno impide
cablear el ranking, pero sí determinan qué se muestra.

---

## 5. Pasada 7 — feedback UX restante (puntos 3 y 5b)

**7.1 — `tipo_variable` extensible (punto 3). No es UI.** Es un discriminante de reglas de negocio: `outliers.py`
(Chow ante ceros), `DISABLED_WITH_ZEROS` en 4 distribuciones de Etapa 2, y `CONTRACT_NEGATIVE_VALUES`. Decidir primero,
con Facundo: ¿`"caudal_precipitacion"` sigue siendo el único valor mágico y todo lo demás cae en el comportamiento de
`"otro"`, o hace falta una categoría intermedia? Recomendación de diseño: separar **etiqueta libre** (lo que el usuario
escribe y ve en resultados/historial/PDF) de **clase de dominio** (el discriminante cerrado que el core consume). Dos
campos, no uno estirado. Requiere decisión escrita + migración.

**7.2 — Búsqueda por nombre de archivo (punto 5b).** El dato no se persiste hoy. Orden obligado: decidir captura y
normalización → migración `005_add_nombre_archivo` → exponerlo en `HistoryItem` → recién ahí la búsqueda. Definir
también si la búsqueda es client-side (hoy la paginación lo es) o un parámetro de `GET /history/`.

### Cortes de PR de la Pasada 7

| PR | Rama | Contenido |
|---|---|---|
| **7.1** | `feat/tipo-variable-dominio` | Separación etiqueta libre / clase de dominio en `core/` + migración. **No incluye UI** — es el cambio con más potencial de daño invisible del roadmap y merece revisión aislada. |
| **7.2** | `feat/tipo-variable-ui` | Config, resultados, historial usando la etiqueta. Sale recién con 7.1 mergeada. |
| **7.3** | `feat/nombre-archivo-persistencia` | Migración `005` + captura + exposición en `HistoryItem`. Solo persistir, sin buscar. |
| **7.4** | `feat/historial-busqueda` | La búsqueda en sí, sobre un dato que ya existe. |

**Regla que esta pasada hace explícita:** una migración de esquema por PR, nunca dos, y nunca junto a UI.

---

## 6. Pasada 8 — exportación PDF (CU-01) y CU-03

- **`GET /api/v1/export/{id}`** — PDF on-demand, sin almacenar en disco. Contenido variable según modo:
  **paso a paso incluye fórmulas con valores sustituidos** (`constraints.md`) — es la pieza que `FE-14` dejó
  explícitamente fuera del frontend porque pertenece acá. Depende de 6.5 (los gráficos).
- **`POST /api/v1/validate/`** — CU-03: sincrónico, solo Etapa 1, `X-API-Key`, stateless, sin `outlier-decision` ni
  `design-events`. El contrato JSON completo ya está escrito en `api-contracts.md`. Requiere la gestión de API Keys
  (hash bcrypt, tabla `api_clients` ya modelada).

### Cortes de PR de la Pasada 8

| PR | Rama | Contenido |
|---|---|---|
| **8.1** | `feat/export-pdf` | `GET /export/{id}` con los dos modos. Depende de 6.4 (gráficos). |
| **8.2** | `feat/api-keys` | Gestión y hash de API Keys. **Es superficie de seguridad — PR propio, revisión propia, nunca plegado dentro de 8.3.** |
| **8.3** | `feat/cu03-validate` | `POST /validate/` sobre las keys ya existentes. |

---

## 7. Decisiones nuevas que este roadmap requiere

Ninguna se implementa sin el archivo escrito primero. Confirmar números libres contra `docs/decisiones/README.md`.

| Decisión | Tema | Bloquea |
|---|---|---|
| 049 (o siguiente libre) | Escotilla SMTP de desarrollo — reasignación del número que 045 se llevó (H1). Recomendación previa ya registrada: MailHog en `docker-compose`, no una rama `if dev` en el camino crítico de auth. | Nada; higiene |
| 050 | Límite de tamaño de subida — valor, dónde se aplica (nginx + backend) y código de error nuevo | Pasada 5 · Bloque A |
| 046 (reservado) | E2E con Playwright — revisa la exclusión de `constraints.md` | Pasada 5 · Bloque C1b |
| 051 | `etapas` cableado de punta a punta (cierra DECISIÓN 037) | Pasada 6 |
| 052 | `tipo_variable`: etiqueta libre vs. clase de dominio | Pasada 7.1 |
| 053 | Persistencia de `nombre_archivo` y alcance de la búsqueda | Pasada 7.2 |

Siguen abiertas de antes y **fuera de este roadmap**: **043** (contraste WCAG del tema Instrumento — pendiente de
decisión de Kevin/Octavio desde la pasada 3) y **036** (partición de Cramer personalizada; la Pasada 5 · Bloque D
**no la resuelve**, solo deja de devolver 500).

---

## 8. Orden, y la regla de proceso que importa más que cualquier bloque

```
Paso 0   sincronizar el checkout local con staging, limpiar worktrees
Pasada 5 deuda + hardening            3 PRs paralelos    (5.1, 5.2, 5.3) + C como decisión
Pasada 6 Etapa 2 real                 5 PRs secuenciales (6.0 precondición → 6.1 → 6.2 → 6.3 → 6.4*)
Pasada 7 tipo_variable + búsqueda     4 PRs              (7.1 → 7.2, 7.3 → 7.4)
Pasada 8 export PDF + CU-03           3 PRs              (8.1, 8.2 → 8.3)
                                      * 6.4 (gráficos) probablemente sea pasada propia
```

**15 PRs en total contra los 2 de la última vez.** Ese es el punto: ninguno debería tardar más de una jornada de
trabajo ni superar el techo de §2.5, y cada uno es reversible por separado.

**Definition of done, sin excepción** (ya está escrita en `testing.md`, capa 4, y es lo único que habría detectado F1
el mismo día): todo PR que toque `frontend/` lleva evidencia de haber corrido el flujo **en el navegador después del
último commit del PR**. La pasada 4 cerró con 5 de 14 puntos sin esa evidencia y lo declaró — declararlo es correcto,
pero la deuda sigue siendo deuda hasta que el Bloque C la cierre.

### Riesgos

- **Subir el límite de body sin cap en el backend** cambia un 413 barato por un OOM caro. A1 y A2 son un solo cambio,
  no dos independientes.
- **Cablear Etapa 2 sin cerrar 037** obliga a correr siempre las 13 distribuciones aunque el usuario pidiera solo
  Etapa 1 — costo de CPU y semántica equivocada.
- **`tipo_variable` como campo libre sin separar la clase de dominio** rompe silenciosamente Chow y las 4
  distribuciones deshabilitadas ante ceros. Es el ítem con más potencial de daño invisible de todo el roadmap.
- **La cadencia de PRs se erosiona sola cuando el trabajo fluye.** Es lo que pasó la última vez: nadie decidió acumular
  60 commits, simplemente nunca hubo un momento obvio para cortar. Mitigación: el corte está decidido en las tablas de
  §3-§6 **antes** de escribir la primera línea, y el techo de §2.5 es una condición de corte mecánica que no depende de
  que alguien "sienta" que el bloque terminó.
