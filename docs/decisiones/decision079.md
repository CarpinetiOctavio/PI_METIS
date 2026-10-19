# DECISIÓN 079: Chow marca todos los valores fuera de los umbrales, altos y bajos, con una sola pausa y una decisión por punto

**Fecha:** 18 de octubre de 2026
**Estado:** Decidida y aplicada (backend + frontend + informe PDF) — bloque C de
`docs/historico/planes/plan-significancia-y-fixes-18-10-2026.md`.
**Decide:** Kevin, a partir de un caso encontrado al usar el sistema.
**Depende de:** DECISIÓN 078 (el α de Chow, en cada extremo).

### Problema

`calcular_chow` tomaba solo el valor de mayor |z| (`argmax`) y lo comparaba con `K_N`. Si había más de un valor
más allá del umbral, marcaba uno solo. El gráfico de Chow, en cambio, dibuja la franja `exp(ȳ ± K_N·S)`, así que
el usuario veía dos puntos fuera de la franja y el resultado y la pausa hablaban de uno. En la serie diaria de 40
años de `docs/series prueba/` el gráfico dejaba afuera 1994 y 2005, y la pausa ofrecía decidir solo sobre 1994.
El gráfico y la prueba se contradecían.

### Fundamento

Bulletin 17B (Apéndice 4) no prueba solo el valor más extremo: calcula un umbral alto `y_H = ȳ + K_N·S` y uno bajo
`y_L = ȳ − K_N·S` sobre los logaritmos, y **todo** valor por encima de `y_H` es un atípico alto y todo valor por
debajo de `y_L` es un atípico bajo. Cada lado es una prueba de un extremo, que es la lectura de "α en cada
extremo" de la DECISIÓN 078. Implementarlo así hace coincidir el resultado con la franja del gráfico.

### La decisión

- **Núcleo (`core/etapa1/outliers.py`).** `z_i = (ln x_i − ȳ)/S` con signo. `TestResult.valores_atipicos` lista
  todos los `i` con `z_i > K_N` (lado `"alto"`) o `z_i < −K_N` (lado `"bajo"`), como
  `{indice, valor, z, lado}`, ordenados por |z| descendente. `None` en las demás pruebas y en Chow no ejecutada.
- **Compatibilidad.** `estadistico = max|z_i|`, y `valor_atipico`/`indice_atipico` siguen siendo el más extremo:
  los leen los análisis guardados, el informe y `simulate-exclusion`. Que la lista no esté vacía equivale a
  `max|z_i| > K_N`, el criterio anterior, así que el veredicto no cambia en ninguna serie.
- **Umbrales del servidor.** `explicacion.terminos` suma `limite_inferior = exp(ȳ − K_N·S)` y
  `limite_superior = exp(ȳ + K_N·S)`. El gráfico de Chow dibuja exactamente esos valores. Antes los calculaba el
  cliente, y el núcleo es el único que calcula. Se queda con un respaldo para los análisis viejos que no los traen.
  Cada fila del `desglose` (addendum de la DECISIÓN 064) suma `fuera`.
- **Una sola pasada.** `ȳ`, `S` y `K_N` se calculan sobre la serie completa y no se vuelve a probar después de
  quitar un valor. Un atípico muy grande puede inflar `S` y esconder a otro (enmascaramiento): queda declarado acá
  y en el libro, y la exclusión de puntos (DECISIÓN 071) permite ver qué pasa sin él.
- **Una sola pausa** (`outlier_detected`) con la lista completa:
  `{session_id, atipicos: [{indice, periodo, valor, z, lado}], valor_atipico}`. `indice` es la posición en
  `datos.serie_efectiva`. `valor_atipico` se conserva por compatibilidad.
- **Una decisión por punto.** `POST /analysis/outlier-decision` recibe
  `{session_id, decisiones: [{indice, decision: "rechazar" | "aceptar"}]}`. El conjunto de índices tiene que ser
  exactamente el de la pausa (`SessionState.atipicos_pendientes`). Si falta uno, sobra uno ajeno, hay uno repetido
  o la sesión no está en la pausa de Chow, responde 400 `OUTLIER_DECISION_INVALID`. Si la sesión no existe,
  404 `SESSION_NOT_FOUND`. En ninguno de los dos casos se desbloquea el stream.
- **Los rechazados se excluyen juntos**, con `aplicar_exclusiones` (la misma operación que `simulate-exclusion`).
  Reemplaza al `del serie_filtrada[indice]` de un solo índice. Rechazar k puntos en la pausa da lo mismo que
  excluirlos por simulación (`test_simulate_exclusion_equivale_a_chow.py`).
- **La segunda pasada no vuelve a pausar**, como hasta ahora y como la simulación (DECISIÓN 071). Si sin los
  rechazados aparecen valores nuevos fuera de los umbrales, el warning de Chow lo dice en una línea y quedan
  sugeridos en el panel de exclusión. Si todo se aceptó, el warning deja de decir "decisión pendiente" y nombra
  los años aceptados (`_describir_chow_tras_decision`).
- **Auditoría (CU-01).** `decisiones.chow = {atipicos: [{indice, periodo, valor, z, lado, decision, codigo}]}`, con
  `codigo` `TEST_OUTLIER_REJECTED_BY_USER` o `TEST_OUTLIER_ACCEPTED_BY_USER` por punto. Los análisis guardados
  antes conservan la forma `{accion, dato}`. El historial y el PDF leen las dos formas.
- **Interfaz.** Modal `routes/stream/DecisionAtipicos.tsx`: una fila por atípico (año, valor, lado, distancia en
  desvíos), dos botones iguales por fila, sin opción preseleccionada, y "Continuar con estas decisiones"
  habilitado recién cuando todas las filas tienen decisión. Se mantiene "METIS no recomienda ninguna respuesta",
  y Escape no cierra. El gráfico de Chow marca todos los puntos de la lista con un rombo y leyenda de texto, sin
  depender solo del color. En el panel de exclusión todos aparecen como sugeridos y ninguno viene seleccionado. El
  paso a paso muestra los dos umbrales y la regla de Bulletin 17B, y el desglose resalta las filas fuera.

### Efecto sobre resultados ya verificados

Ninguno. En las 9 estaciones de la tesis Chow no marca ningún atípico, antes ni después
(`test_las_9_estaciones_de_la_tesis_siguen_sin_atipicos`), y la no regresión de la DECISIÓN 078 con α = 5 % sigue
idéntica. La serie diaria de 40 años da 1994 y 2005, los dos del lado bajo
(`test_serie_diaria_de_40_anios_marca_1994_y_2005`). La consistencia gráfico–prueba está cubierta por
`test_fuera_de_las_franjas_si_y_solo_si_esta_en_la_lista`, con series aleatorias y los tres α.

### Códigos

- Nuevo: `OUTLIER_DECISION_INVALID` (HTTP 400, no evento SSE). Suma el prefijo `OUTLIER` a
  `scripts/check-error-catalog.sh` (addendum del 18/10/2026 a la DECISIÓN 038).
- `SESSION_NOT_FOUND` pasa a usarse también en `outlier-decision`.

### Pendiente

- El gráfico de Chow dentro del diálogo de la pausa (arrastrado de la DECISIÓN 018 / RF-CU01-07). Con varios
  puntos a decidir ayudaría verlos en la franja. No entró en este bloque.

### Relación con otras decisiones

- **DECISIÓN 018** — K_N de Grubbs-Beck; esta decisión aplica la regla completa de los dos umbrales.
- **DECISIÓN 038** — catálogo de errores, prefijo `OUTLIER`.
- **DECISIÓN 053** — `session_store`; la misma pausa, ahora con la lista de pendientes.
- **DECISIÓN 064** — paso a paso y desglose.
- **DECISIÓN 071** — exclusión de puntos; misma operación para los rechazados.
- **DECISIÓN 078** — α de Chow en cada extremo.
