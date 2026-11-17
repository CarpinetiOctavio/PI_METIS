# Plan de implementación: pendientes de la revisión manual del 21/10/2026

**Fecha:** 21 de octubre de 2026
**Autor del plan:** Kevin Massholder (con asistencia)
**Ejecución:** Claude Code, un solo pedido de incorporación desde `staging`, con un commit por bloque
**Base verificada:** `staging` en `66720eb` (19 de octubre de 2026, PR #133). Antes de empezar, `git fetch` y confirmar contra `origin/staging` las rutas y los nombres que cita este plan.

---

## 0. Contexto y reglas para quien ejecuta

### Por qué existe este plan

Kevin recorrió METIS a mano el 21/10/2026 y encontró siete problemas. A eso se suman tres pendientes chicos detectados al armar el prototipo 5 del informe y un pedido nuevo (un segundo usuario de prueba). Son cambios chicos o medianos que se agrupan en un único pedido de incorporación para no gastar una ronda completa de integración continua por cada uno.

| Bloque | Origen | Tipo | Tamaño |
|---|---|---|---|
| A. "Ver archivados" muestra también los activos | Revisión manual | Defecto | Chico |
| B. Simular la exclusión de puntos desde el historial | Revisión manual | Mejora (cierra un pendiente declarado) | Mediano |
| C. Los puntos eliminados no se ven en el historial (pausa de Chow y exclusión posterior) | Revisión manual | Defecto (C1) y mejora con decisión nueva (C2) | Mediano |
| D. El PDF marca un solo atípico de Chow | Revisión manual | Defecto | Chico |
| E. Nombre del CSV descargado: `_sin_atipicos` | Revisión manual | Defecto de texto | Muy chico |
| F. La partición personalizada de Cramer no se informa en pantalla | Revisión manual | Defecto | Chico |
| G. Gráficos con eje de años: tooltip "T" y diferencia entre vistas | Revisión manual | Defecto de texto y aclaración | Chico |
| H. Una celda vacía genera dos advertencias | Prototipo 5 | Defecto | Muy chico |
| I. Contraste del diálogo de pausa de Chow por debajo de 4,5:1 | Prototipo 5 | Defecto (incumple RNF-07) | Muy chico |
| J. "Lag" en lugar de "rezago" en el PDF | Respuesta de Facundo, 21/10 | Terminología | Muy chico |
| K. Segundo usuario de prueba y verificación de aislamiento | Pedido de Kevin | Mejora de pruebas | Chico |

### Reglas del repositorio que aplican a todo el plan

- Rama `fix/revision-manual-21-10` desde `staging`, pedido de incorporación a `staging`. Nada directo a `main`.
- **Cada defecto** (bloques A, C, D, E, F, G, H, I) abre su issue con la plantilla *Defecto* y los labels `defecto`, `sev:`, `prio:` y `fase:`, y se cierra solo con un test que lo cubra, nombrado en el comentario de cierre (`docs/calidad/registro-defectos.md`).
- Si un bloque agrega un borde o una regla de decisión nueva (el bloque H lo hace), su caso va a `docs/calidad/casos-de-prueba.md` con el test que lo implementa.
- Este plan no crea códigos de error nuevos. Si alguno hiciera falta, va al catálogo del contrato de la API y a `frontend/src/i18n/errors.es.ts` en el mismo commit.
- Este plan necesita **una decisión numerada nueva**, la **DECISIÓN 080** (exclusiones guardadas en el historial, bloque C2), y **una migración nueva**, la `006`. Antes de numerarlas, verificar el máximo real en `origin/staging`: al 19/10 la última decisión es la 079 (la 072 y la 035 están reservadas) y la última migración es la `005`. El bloque B es una revisión fechada de la DECISIÓN 071.
- Las migraciones se escriben a mano (`backend/alembic/versions/`) y nada las corre al arrancar: documentar en el pedido que hay que correr `alembic upgrade head` en cada entorno, incluido el servidor de la UCC.
- Umbrales vigentes de la integración continua: 80 % de cobertura del código nuevo y duplicación por debajo del 5 %.
- El pedido toca `frontend/`: después del último commit, recorrer en el navegador los flujos de cada bloque y dejar evidencia (capturas) en el pedido.

### Orden sugerido

H, I, J y E primero (una línea cada uno); después A, C1, D, F y G; después B; al final C2, que depende de B, y K, que suma una prueba sobre C2.

---

## Bloque A. "Ver archivados" muestra también los análisis activos

### Problema

En el historial, "Ver archivados" lista todos los análisis, archivados y activos. Archivar sí funciona: el análisis desaparece de la vista de activos. Lo que falla es la vista de archivados.

### Causa

`HistoryPage.tsx` pide `listHistory(viewArchived)`, que llama a `GET /history/?archivados=true`. Según el contrato (DECISIÓN 048) ese parámetro **incluye** los archivados además de los activos, no los selecciona. La interfaz muestra esa lista tal cual.

### Tareas

1. En `HistoryPage.tsx`, con `viewArchived`, quedarse solo con los ítems con `archivado_at !== null`. El contrato de la API no cambia.
2. Revisar que en la vista de archivados todos los ítems muestren "Desarchivar" y ninguno "Archivar".
3. Test en `HistoryPage.test.tsx`: con una respuesta que mezcla activos y archivados, la vista de archivados muestra solo los archivados y la de activos solo los activos.

### Criterio de aceptación

Un análisis aparece en una sola de las dos vistas. Archivar lo pasa a la otra y desarchivar lo devuelve.

---

## Bloque B. Simular la exclusión de puntos desde el historial

### Problema

En el detalle de un análisis del historial, el panel "Excluir puntos de la serie" deja marcar puntos y descargar el CSV, pero no recalcula el análisis sin ellos. En Resultados sí lo hace. El informe lo declara hoy como pendiente (Tabla 12: "Exclusión de puntos desde el historial: el detalle en el historial todavía no ofrece recalcular sin puntos").

### Causa

`HistoryDetailPage.tsx` monta `Etapa1ResultView` sin la función `simular`. `ResultsPage.tsx` la arma con los datos del router (`tipoVariable`, `cramerParticion`, `etapas`) y la pasa. Sin esa función, el panel funciona en modo selección y descarga, sin comparación.

### Decisión de diseño

- El detalle del historial ya tiene todo lo que pide `POST /analysis/simulate-exclusion`:
  - `etapa1.datos.serie_efectiva` y `timestamps_efectivos`;
  - `tipo_variable`, `etapas`, `configuracion.cramer_particion` y `configuracion.alfa`;
  - la elección registrada (`etapa2.seleccion`).
- El servidor no cambia.
- Sigue valiendo "explorar no es decidir" (DECISIÓN 062): la simulación no se guarda ni modifica el registro.

### Tareas

1. Extraer de `ResultsPage.tsx` la construcción de `simular` a una función compartida, por ejemplo `routes/results/simulacion.ts::crearSimulacion(datos, configuracion, seleccion)`. Que la usen las dos páginas, para no duplicar código (el umbral de duplicación es 5 %).
2. En `HistoryDetailPage.tsx`, pasar `simular` a `Etapa1ResultView` con los datos del detalle. La partición de Cramer persistida puede venir como `"default"` o como objeto: convertirla a texto igual que `cramerParticionComoTexto`.
3. Con puntos simulados, `ExportarPdfButton` del historial recibe `indicesExcluidos`, como en Resultados, para ofrecer el PDF con la simulación (`POST /export/{id}/simulacion`).
4. Si el análisis es anterior a DECISIÓN 058 (`timestamps === null`), no ofrecer la simulación y explicar por qué, igual que ya se explica la falta de gráficos.
5. Revisión fechada en `docs/decisiones/decision071.md`: la simulación también está disponible desde el historial, con los datos persistidos.
6. Tests:
   - el detalle del historial con puntos marcados llama a `simulate-exclusion` con la serie, los años, el α y la partición persistidos;
   - la comparación aparece;
   - no se llama a ningún endpoint que modifique el análisis.

### Criterio de aceptación

Desde el historial, marcar 1983 y 1993 en la serie diaria de 40 años muestra la misma comparación que desde Resultados, y el PDF con simulación incluye esos dos puntos.

---

## Bloque C. Los puntos eliminados no se ven en el historial

Hay dos formas de quitar puntos de un análisis, y el historial hoy no muestra ninguna:

- **En la pausa de Chow:** el usuario rechaza atípicos y el análisis se recalcula sin ellos. Es una decisión y queda guardada, pero el historial no la muestra (C1).
- **Con "Excluir puntos de la serie", después del análisis:** el usuario quita cualquier punto y ve los resultados sin él. Hoy es una exploración que no se guarda en ningún lado (C2).

### C1. Mostrar en el historial las decisiones tomadas ante Chow

#### Causa

`GET /history/{id}` devuelve `decisiones.chow` (forma nueva `{atipicos: [...]}` y forma vieja `{accion, dato}`), pero `HistoryDetailPage.tsx` no lo usa. Como el análisis guardado corresponde a la serie sin los rechazados, la serie se ve más corta sin explicación. El PDF sí lo informa.

#### Tareas

1. Bloque "Decisiones ante Chow" en el detalle del historial: una fila por punto con año, valor, lado, desvío y decisión (rechazado o aceptado). Leer las dos formas, como ya hace el PDF (`reportes/pdf.py`, alrededor de la línea 829).
2. Si hubo rechazados, una línea que diga que los resultados guardados corresponden a la serie sin esos puntos.
3. En la lista del historial, una etiqueta chica en el análisis: "1 punto rechazado ante Chow" o "2 puntos rechazados ante Chow". Si el endpoint de la lista no trae `decisiones`, sumar al ítem solo un contador (`chow_rechazados`), sin traer el registro completo.
4. Tests con las dos formas de `decisiones.chow` y con `decisiones` vacío (`{}`).

### C2. Guardar en el historial las exclusiones hechas después del análisis (DECISIÓN 080)

#### Decisión de diseño

La DECISIÓN 062 ("explorar no es decidir") sigue en pie: excluir puntos después del análisis **no modifica** el resultado guardado ni el registro de decisiones. Lo que cambia es que la exclusión ya no se pierde: se guarda **aparte**, como una exclusión registrada del análisis.

- **Qué se guarda:**
  - los índices excluidos y, para cada uno, el año y el valor;
  - la fecha;
  - el α y la partición con que se simuló.

  Los resultados no se guardan: se recalculan al abrirla con `simulate-exclusion`, que es determinístico. Así no se duplica ningún resultado y no crece la base.
- **Cuándo se guarda:** solo cuando el usuario aprieta "Guardar esta exclusión en el historial", en la vista comparativa. Una exclusión probada y descartada no ensucia el historial.

  Si Kevin prefiere que se guarde sola cada vez que se simula, el cambio es solo dónde se llama al endpoint.
- **Quién puede:** solo CU-01, porque CU-02 no tiene historial y el botón no aparece.
- **Dónde se ve:**
  - en el detalle del historial, un bloque "Exclusiones guardadas" con la fecha y los años excluidos de cada una, y dos acciones: "Ver" carga la selección en el panel y muestra la comparación (bloque B); "Quitar" la borra;
  - en la lista del historial, una etiqueta "N exclusiones guardadas".

#### Tareas del servidor

1. Migración `006_add_exclusiones_analysis_results.py`: columna `exclusiones JSONB NOT NULL DEFAULT '[]'` en `analysis_results`. Sin backfill: los análisis anteriores quedan con lista vacía.
2. `POST /api/v1/history/{id}/exclusiones`:
   - **cuerpo:** `{"indices_excluidos": [3, 13]}`;
   - **validación:** JWT requerido y pertenencia (404 `ANALYSIS_NOT_FOUND` si no es del usuario, igual que el resto del historial). Índices dentro de `etapa1.datos.serie_efectiva`, sin repetidos y sin vaciar la serie; si no, 400 `CONTRACT_EXCLUSION_INVALID`, el código que ya existe;
   - **qué guarda:** `{id, creado_at, indices, puntos: [{indice, periodo, valor}], alfa, cramer_particion}`, con los años y los valores tomados del análisis persistido, no del cliente;
   - **respuesta:** la entrada creada. Si la misma selección ya existe, no la duplica y devuelve la existente.
3. `DELETE /api/v1/history/{id}/exclusiones/{exclusion_id}`: misma autenticación y pertenencia; 404 si la exclusión no existe.
4. `GET /history/{id}` devuelve `exclusiones` (lista, `[]` si no hay). `GET /history/` suma `exclusiones_guardadas` (cantidad) a cada ítem.
5. Nada de esto toca `decisiones`, `etapa1` ni `etapa2`. Un test lo verifica comparando el registro antes y después.
6. Tests de integración contra PostgreSQL (`tests/integration/db/`):
   - guardar, listar y quitar;
   - pertenencia (404 con otro usuario);
   - índices inválidos (400);
   - selección repetida (no duplica);
   - el resultado original y las decisiones quedan intactos.

#### Tareas de la interfaz

1. En la vista comparativa de Resultados (con `analysisId`) y del historial (bloque B), el botón "Guardar esta exclusión en el historial". Después de guardar, el botón confirma "Guardada" y no vuelve a ofrecerse para la misma selección.
2. En el detalle del historial, el bloque "Exclusiones guardadas" con "Ver" y "Quitar". "Ver" reutiliza la simulación del bloque B.
3. En la lista del historial, la etiqueta con la cantidad.
4. Tests:
   - el botón no aparece en CU-02;
   - guardar llama al endpoint con los índices;
   - "Ver" carga la selección y simula;
   - "Quitar" la saca de la lista.

#### Documentación

- `docs/decisiones/decision080.md`: qué se guarda, por qué los resultados se recalculan en vez de guardarse, por qué se guarda a pedido y no siempre, y cómo convive con la DECISIÓN 062. Agregar a la 062 y a la 071 una revisión fechada que remita a la 080.
- `.claude/rules/architecture/api-contracts.md`: los dos endpoints nuevos y los campos nuevos de `GET /history/` y `GET /history/{id}`.
- `.claude/rules/architecture/architecture.md`: la columna nueva en el esquema de `analysis_results`.
- `docs/calidad/casos-de-prueba.md`: los bordes de la validación (índices fuera de rango, repetidos, serie vacía).
- `docs/calidad/` (trazabilidad): el requerimiento que esto amplía.

### Criterio de aceptación del bloque C

Con la serie diaria de 40 años:

- se rechaza 1994 en la pausa de Chow y se acepta 2005;
- en Resultados se excluyen 1983 y 1993 y se guarda la exclusión;
- en el historial, el detalle muestra la decisión ante Chow (1994 rechazado, 2005 aceptado) y la exclusión guardada (1983 y 1993);
- "Ver" reproduce la comparación;
- la lista marca el análisis con las dos etiquetas;
- el resultado guardado y las decisiones no cambiaron.

---

## Bloque D. El PDF marca un solo atípico de Chow

### Problema

Desde la DECISIÓN 079, Chow marca todos los valores fuera de los umbrales. El PDF sigue mostrando uno solo: en la serie diaria de 40 años marca 1994 y no 2005.

### Causa

`reportes/pdf.py` sigue usando `indice_atipico` y `valor_atipico`, que guardan solo el más extremo, en tres lugares:
- **gráfico de la serie** (`_grafico_serie`, alrededor de la línea 414): un solo círculo;
- **nota de la tabla de pruebas** (alrededor de la línea 704): "Atípico: <valor>";
- **página de la simulación** (alrededor de la línea 1213): "Chow marca otro dato como atípico".

La sección de decisiones (línea 829) ya lee la lista completa.

### Tareas

1. Los tres lugares pasan a leer `valores_atipicos` (`[{indice, valor, z, lado}]`). Si no existe (análisis anteriores a la DECISIÓN 079), se vuelve a `indice_atipico`.
2. Gráfico: un marcador por atípico, y la leyenda en plural cuando hay más de uno.
3. Nota: "Atípicos: 296,93 (1994), 296,99 (2005)".
4. Tests del PDF con dos atípicos y con un análisis viejo sin `valores_atipicos`.

### Criterio de aceptación

El PDF de la serie diaria de 40 años marca 1994 y 2005, igual que el gráfico de Chow de la pantalla.

---

## Bloque E. Nombre del CSV descargado

### Problema

El CSV sin los puntos seleccionados se descarga como `<archivo>_sin_atipicos.csv`, aunque los puntos pueden no ser atípicos (el panel deja quitar cualquiera).

### Tareas

1. `routes/results/exclusiones.ts`: el nombre pasa a `<archivo>_sin_puntos_excluidos.csv`, o `serie_sin_puntos_excluidos.csv` si no se conoce el nombre del archivo. Actualizar el comentario de la línea 77.
2. Actualizar el test del nombre.

---

## Bloque F. La partición personalizada de Cramer no se informa en pantalla

### Problema

Con una partición personalizada (por ejemplo 70 % / 35 %), ni Resultados ni el historial lo dicen. El PDF sí ("Partición de Cramer: Personalizada (70 % / 35 %)").

### Tareas

1. En `Etapa1ResultView`, junto a la fila de Cramer (o en la línea de configuración donde ya se muestra α), informar la partición:
   - por defecto: "últimos 60 % y 30 % (n₁ = …, n₂ = …)";
   - personalizada: "personalizada: últimos 70 % y 35 % (n₁ = …, n₂ = …)".

   Los tamaños salen de `n1` y `n2` del resultado de Cramer: la interfaz no los calcula.
2. Origen del dato: en Resultados, `locationState.cramerParticion`; en el historial, `configuracion.cramer_particion`. Pasarlo como prop, igual que `mesInicioAnio`.
3. Tests con partición por defecto, personalizada y ausente (análisis viejo: no mostrar nada en lugar de inventar).

---

## Bloque G. Gráficos con eje de años: tooltip "T" y diferencia entre vistas

### Lo que se vio

En la serie temporal, con "Configurado", 1994 vale 296,93. Con "Calendario", 299,64.

### No es un defecto de cálculo

Lo verificamos contra `docs/series prueba/serie_diaria_40anios.csv`:
- **Configurado (julio a junio):** el año 1994 va de julio de 1994 a junio de 1995. Su máximo es 296,93, en julio de 1994.
- **Calendario:** el año 1994 va de enero a diciembre de 1994. Su máximo es 299,64, en abril de 1994, que en la otra vista cae dentro del año 1993.

Cada vista toma el máximo de una ventana de doce meses distinta. 2005 coincide en las dos porque su máximo cae en un mes que está en las dos ventanas.

### Lo que sí hay que corregir

1. **Tooltip:** la serie temporal y el gráfico de Chow muestran "T = 1994". "T" es el período de retorno. Pasar `xName="Año"` a `InteractiveChart` en `Etapa1SerieTemporalChart.tsx` y `Etapa1ChowChart.tsx`.
2. **Año con otro mes de inicio:** en la vista configurada, cuando el mes de inicio no es enero, el tooltip muestra el año como "1994-95". El eje puede seguir con el año de inicio.
3. **Aclaración:** una línea bajo el selector "Criterio de año": "Cada vista toma el máximo de doce meses distintos, así que un mismo año puede tener valores distintos en una y otra."
4. Tests del texto del tooltip en las dos vistas.

---

## Bloque H. Una celda vacía genera dos advertencias

### Problema

Una celda vacía produce `CONTRACT_MISSING_VALUES` y también `CONTRACT_NON_NUMERIC_VALUES`, así que el mismo dato se cuenta dos veces.

### Causa

En `core/validacion/contract.py`, `no_numericos` usa `es_numerico(v)`, que devuelve `False` también para `None` y `NaN`, los mismos valores que cuenta `faltantes`.

### Tareas

1. `no_numericos` excluye los faltantes: un valor es no numérico si no es numérico **y** no es `None` ni `NaN`.
2. Tests:
   - solo celdas vacías: aparece únicamente `CONTRACT_MISSING_VALUES`;
   - solo texto ("x"): aparece únicamente `CONTRACT_NON_NUMERIC_VALUES`;
   - las dos cosas: aparecen las dos advertencias, cada una con su conteo.

   `test_multiples_warnings_se_acumulan` ya mezcla `None` y `"z"`: tiene que seguir en verde.
3. Caso nuevo en `docs/calidad/casos-de-prueba.md` (clase de equivalencia: faltante frente a no numérico).

---

## Bloque I. Contraste del diálogo de pausa de Chow

### Problema

En la pausa de Chow, el texto secundario (párrafo explicativo, encabezados de la tabla y "METIS no recomienda ninguna respuesta") queda en 2,9:1 con el tema claro. RNF-07 y WCAG 1.4.3 piden 4,5:1. El título y los botones sí cumplen (9,6:1).

### Causa

El color del texto cumple sobre blanco (5,9:1). Lo que falla es el fondo: `.modal-backdrop .card` usa `color-mix(in srgb, var(--surf) 55%, transparent)` sobre una capa oscura al 40 %, y el fondo efectivo queda gris (181 de 255). La prueba automática de contraste (DECISIÓN 043) compara contra `--surf` puro y no ve esta composición.

### Tareas

1. En `routes/stream/StreamPage.css`, subir la opacidad de la tarjeta de 55 % a 90 %. Con 90 % el texto secundario queda en 5,2:1; desde 82 % ya cumple.
2. Verificar los dos temas: medir el contraste sobre una captura del diálogo en claro y en oscuro.
3. Sumar a la prueba de contraste un par que componga el fondo real del modal (90 % de `--surf` sobre la capa) contra el color del texto secundario, para que una regresión de la opacidad se detecte.
4. Captura nueva del diálogo para el informe (Figura de la pausa de Chow).

---

## Bloque J. "Lag" en lugar de "rezago" en el PDF

### Contexto

Facundo confirmó el 21/10/2026 que el término usado en hidrología es *lag* y que el 10 % de la prueba de Anderson es una regla fija de la prueba que no cambia con α. La pantalla ya dice "lag"; el PDF no.

### Tareas

1. `reportes/pdf.py`:
   - línea 457: el eje del correlograma pasa de "Rezago k" a "Lag k";
   - línea 795: "la tolerancia de rezagos de Anderson" pasa a "la tolerancia de Anderson (10 % de los coeficientes fuera de banda)".
2. Revisar `docs/` y `.claude/rules/`:
   - "tolerancia de rezagos" pasa a "tolerancia de coeficientes fuera de banda" en `api-contracts.md`, `constraints.md` y `formulas-etapa1.md`;
   - dejar constancia de que la regla del 10 % fija la confirmó Facundo el 21/10/2026, en `decision012.md` y en la revisión de `decision078.md`.

---

## Bloque K. Segundo usuario de prueba y verificación de aislamiento entre perfiles

### Objetivo

Tener dos usuarios de prueba para verificar que cada uno ve solo sus análisis y que no puede abrir los del otro ni por la dirección directa.

### Tareas

1. Usuario: `2200002@ucc.edu.ar`, mismo patrón que el `2200001@ucc.edu.ar` que crea hoy `scripts/seed-dev-user.sh`.

2. `scripts/seed-dev-user.sh` ya acepta el email como argumento. Documentar en `docs/calidad/despliegue-y-e2e.md` cómo crear los dos usuarios: `./scripts/seed-dev-user.sh` y `./scripts/seed-dev-user.sh 2200002@ucc.edu.ar`.
3. `scripts/deploy-local.sh` siembra también un segundo usuario de humo (`SMOKE_EMAIL_2`, por defecto `smoke2@ucc.edu.ar`).
4. Prueba de humo nueva en `backend/tests/smoke/`. El usuario 1 corre un análisis; el usuario 2:
   - no lo ve en `GET /history/`;
   - recibe 404 en `GET /history/{id}`, `GET /export/{id}` y `POST /analysis/{id}/design-events`;
   - recibe 404 en `POST /history/{id}/archive`;
   - recibe 404 en `POST /history/{id}/exclusiones` y no ve las exclusiones guardadas del usuario 1 (bloque C2).

   Los tests de integración ya cubren la pertenencia contra la base. Esta prueba lo verifica sobre el sistema desplegado detrás de nginx, que es lo que se va a mostrar en la defensa.
5. En el servidor de la UCC, crear los dos usuarios con el mismo script al desplegar (paso manual, documentado).

### Criterio de aceptación

Con los dos usuarios logueados en navegadores distintos, ninguno ve ni abre los análisis del otro. La prueba de humo pasa en el trabajo `despliegue` de la integración continua.

---

## Verificación final del conjunto

1. `scripts/test.sh all` en verde y los ocho trabajos de la integración continua en verde.
2. Recorrido en el navegador con la serie diaria de 40 años:
   - pausa de Chow legible en los dos temas;
   - rechazar 1994 y aceptar 2005;
   - en el historial se ven las dos decisiones;
   - simular la exclusión de 1983 y 1993 desde el historial, guardarla, volver a abrirla con "Ver" y quitarla;
   - descargar el CSV (nombre nuevo) y el PDF con la simulación (marca 1994 y 2005 donde corresponde y dice "Lag k");
   - archivar y desarchivar.
3. Repetir con una partición de Cramer personalizada y verificar que se informa en pantalla.
4. Con los dos usuarios, verificar el aislamiento a mano.
5. Actualizar `docs/sprint.md` con el conteo de pruebas y cerrar los issues con el test que los cubre.

---

## Impacto en el libro (lo resuelve Kevin con asistencia, no Claude Code)

- **Tabla 12:** quitar la fila "Exclusión de puntos desde el historial".
- **§6.2, "Registro de decisiones y archivado":** describir las exclusiones guardadas (DECISIÓN 080) y cómo conviven con "explorar no es decidir". Sumar la columna nueva al modelo de datos y los dos endpoints a la tabla de la API.
- **Anexo A:** sumar la DECISIÓN 080 al índice y a la síntesis.
- **Figura de la pausa de Chow:** reemplazarla por la captura nueva del bloque I.
- **Conteo de pruebas:** actualizar el número del servidor y del cliente, y la fecha.
- **Estimación económica:** sumar este pedido al conteo de la Tabla 37 (pedidos por banda de tamaño).
- **Anexo G:** si se agrega la prueba de humo de aislamiento, sumarla a la descripción del despliegue.
