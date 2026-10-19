# Plan de implementación: nivel de significancia configurable, Chow con todos los atípicos y fixes de resultados

**Fecha:** 18 de octubre de 2026
**Autor del plan:** Kevin Massholder (con asistencia)
**Ejecución:** Claude Code, un pedido de incorporación por bloque, cada uno desde `staging`
**Base verificada:** `staging` en `9e4403b` (9 de octubre de 2026, PR #129). Los pedidos de la etapa de calidad posteriores pueden haber movido archivos: antes de cada bloque, hacer `git fetch` y confirmar contra `origin/staging` las rutas y los nombres que cita este plan.

---

## 0. Contexto y reglas para quien ejecuta

### Por qué existe este plan

1. **Respuesta de Facundo Ganancias Martínez (18/10/2026)** a la consulta sobre el nivel de significancia de Chow:

   > "La prueba de K_N de Chow y todas las pruebas de estadística para hidrología se hacen con un nivel de significancia del 5 %, eso es como estandarización de las pruebas estadísticas de hidrología a nivel mundial. Algunos programas estadísticos que se pueden usar para otras cuestiones que no sean hidrología te dan la opción de trabajar con un nivel de significancia del 10 %, que es más exigente porque la zona de rechazo es más amplia, o con el 1 %, que es la más permisiva porque la zona de rechazo es muy chiquitita. Si vos tenés la opción de poner las 2 alternativas y que el usuario elija sería un golazo; si no, pondría solamente la del 5 %, apuntando el programa a análisis estadístico hidrológico."

   Se decidió implementar el selector: **1 %, 5 % (valor por defecto, estándar en hidrología) y 10 %**, aplicado a toda la Etapa 1, incluida Chow.

2. **Tres problemas encontrados por Kevin al usar el sistema** (capturas en la conversación del 18/10/2026):
   - La exploración de otra distribución no respeta la simulación de exclusión de puntos.
   - Con una serie de caudal con negativos, no queda claro por qué Chow no marca nada.
   - En la serie diaria de 40 años, Chow marca un atípico (1994) pero no otro dato que también queda fuera de las franjas del gráfico (2005).

### Reglas del repositorio que aplican a todos los bloques

- Rama propia por bloque (`feature/...` o `fix/...`) desde `staging`, pedido de incorporación a `staging`. Nada directo a `main`.
- **Antes de numerar una decisión nueva**, verificar el máximo real en `origin/staging` (`git ls-tree -r --name-only origin/staging -- docs/decisiones/`). Al 9/10 el último es 077 y el 072 está reservado. Este plan asume **078, 079 y 080**; si alguno ya está tomado, usar el siguiente libre y corregir las referencias.
- Ninguna fórmula sin referencia a su ecuación de origen (tesis, Caamaño Nelli y Colladon 2003 o Bulletin 17B).
- El núcleo (`core/`) calcula; la interfaz no deriva ningún estadístico ni valor crítico. Si la interfaz necesita un número, lo manda el servidor.
- Todo código de error nuevo va al catálogo del contrato de la API y a `frontend/src/i18n/errors.es.ts` en el mismo cambio, porque el trabajo `error-catalog` de la integración continua lo verifica en tres direcciones.
- Umbrales de la integración continua vigentes: 80 % de cobertura en el código nuevo y duplicación por debajo del 5 %.
- Cada bloque cierra con: pruebas en verde, recorrido manual en el navegador después del último commit, y documentación actualizada en el mismo cambio (decisión, contrato de la API y, si corresponde, fórmulas).

### Orden de ejecución

| Orden | Bloque | Tamaño estimado | Depende de |
|---|---|---|---|
| 1 | A. Exploración sobre la serie simulada | Chico, casi todo en la interfaz | Nada |
| 2 | B. Nivel de significancia configurable | Mediano | Nada |
| 3 | C. Chow: todos los atípicos fuera de los umbrales | Mediano | B (comparten el cálculo de K_N) |
| 4 | D. Chow no ejecutado por negativos o ceros: mensaje y marcas | Chico | C (comparten el gráfico y el panel de exclusión) |

Hacerlos en este orden evita conflictos en `outliers.py`, en el gráfico de Chow y en el panel de exclusión.

---

## Bloque A. La exploración de otra distribución debe respetar la simulación de exclusión

### Problema

En `ResultsPage`, después de excluir puntos y recalcular, el bloque "Evento de diseño" de la elección registrada ofrece el selector "Original / Sin los puntos excluidos". La exploración de otra distribución (columna derecha, `Etapa2Explorador`) llama siempre a `POST /analysis/{id}/design-events`, que usa el ranking persistido de la serie original. Por eso la exploración muestra la curva ajustada con el atípico incluido (en la captura, el punto de 950 sigue en el gráfico de Log-Pearson III) aunque la simulación vigente lo haya quitado, y no hay forma de verla sin los puntos excluidos.

### Decisión de diseño

- **Un único selector de vista para las dos columnas**, ubicado sobre la comparación: "Ver resultados: Original | Sin los puntos excluidos". Comparar la elección "sin puntos" contra una exploración "con puntos" no tiene sentido, y dos selectores independientes invitan a ese error. El selector solo aparece si hay una simulación vigente con Etapa 2.
- **Para la vista simulada de la exploración no se agrega un punto de acceso nuevo.** `POST /analysis/simulate-exclusion` ya acepta `seleccion: {distribucion, metodo, periodos_retorno}` y devuelve en `etapa2.seleccion` los eventos de esa combinación reajustada sin los puntos. Explorar bajo simulación es llamar a ese mismo punto de acceso con la combinación explorada. Sigue sin estado y no toca ninguna decisión (DECISIÓN 062: explorar no es decidir).
- La vista simulada de la exploración usa `simulacion.etapa2.puntos_empiricos` (las posiciones de Weibull sin los puntos excluidos), no las del análisis original.

### Tareas

1. **Servidor (verificar, cambiar solo si hace falta).**
   - Confirmar qué devuelve `simulate-exclusion` cuando la combinación pedida en `seleccion` no ajusta sobre la serie simulada (no converge, no aplicable, deshabilitada o pendiente de validación). Si hoy devuelve `seleccion: null` sin motivo, agregar en la respuesta el estado de esa combinación (por ejemplo `seleccion_estado: "no_converge"`), para que la interfaz pueda explicarlo. Si hace falta un código de error nuevo, sumarlo al catálogo.
   - Prueba unitaria: pedir una combinación que ajusta en la serie original y no en la simulada, y verificar la respuesta.
2. **Cliente.**
   - Subir el estado de vista (`vistaEventos`, hoy local de `ResultsPage`) a la comparación, y pasárselo a `Etapa2Explorador` junto con la simulación vigente y una función `explorarSimulado(distribucion, metodo, periodosRetorno)` que llama a `postSimularExclusion` con la misma serie, los mismos índices excluidos, la misma configuración y la `seleccion` explorada.
   - En `Etapa2Explorador`, guardar por separado `exploracionOriginal` y `exploracionSimulada`. Al explorar con una simulación vigente, pedir las dos en paralelo; sin simulación, solo la original, como hoy.
   - Si la simulación cambia (otro conjunto de puntos) o se limpia, invalidar `exploracionSimulada` y volver a pedirla si hay una exploración abierta. Ninguna vista puede quedar mostrando una simulación vieja.
   - Si la combinación no ajusta sin los puntos, la vista simulada muestra una línea que lo explica, con el mismo tono que el aviso "Sin los puntos excluidos no hay Etapa 2 que recalcular".
   - Rótulos: en la vista simulada, el encabezado de la exploración dice "Exploración sin los años X, Y: {distribución} · {método}. No es la elección registrada del análisis."
3. **Pruebas.**
   - `Etapa2Explorador.test.tsx`: con simulación vigente, explorar pide las dos vistas, el selector cambia ambas columnas y la vista simulada usa los puntos empíricos de la simulación.
   - `ResultsPage.simulacion.test.tsx`: cambiar la simulación invalida la exploración simulada; limpiar la simulación oculta el selector.
   - Caso de borde: combinación que no ajusta sin los puntos.
4. **Documentación.** Revisión fechada en la DECISIÓN 071 (exclusión de puntos) que describa la vista simulada de la exploración y el selector único.

### Criterios de aceptación

- Con la serie de prueba de la captura (atípico de 950, simulación sin 2000), explorar Log-Pearson III por momentos directo y elegir "Sin los puntos excluidos" muestra la curva reajustada sin el 950, y el punto deja de aparecer en el gráfico de ajuste.
- El selector cambia a la vez la elección registrada y la exploración.
- La elección registrada no cambia en ningún caso (verificable en el historial).

---

## Bloque B. Nivel de significancia configurable en la Etapa 1 (DECISIÓN 078)

### Alcance

Un parámetro `alfa` con tres valores: **0,01, 0,05 (por defecto) y 0,10**, elegido en la configuración del análisis y aplicado a las ocho pruebas de la Etapa 1. La Etapa 2 no tiene nivel de significancia y no cambia. El umbral de advertencia de EEA (5 % de la media, DECISIÓN 070) **no es un nivel de significancia** y no se toca.

### Requisito central: con α = 5 % nada cambia

Con `alfa = 0,05` todos los resultados de la Etapa 1 deben ser **idénticos** a los actuales, en las nueve estaciones de la tesis y en el caso de Las Tapias. Esto incluye Chow: hoy usa α = 0,10 repartido en dos colas, cuantil `1 − 0,10/(2n)`, que es exactamente `1 − 0,05/n`. La reescritura en función de α no puede mover ningún valor. Antes de tocar código, generar un volcado de referencia del resultado de la Etapa 1 de las nueve estaciones y de Las Tapias, y compararlo al final (prueba de no regresión obligatoria del bloque).

### Valor crítico de cada prueba en función de α

| Prueba | Hoy | Con α configurable | Fuente |
|---|---|---|---|
| Anderson | Bandas con `z = 1,96` | Bandas con `z_{1−α/2}` | Ec. III-3 |
| Anderson, tolerancia | `⌈0,10 · k_max⌉` rezagos fuera | **Sin cambio** (es la regla de la tesis, no α). Ver la consulta opcional al final | DECISIONES 012 y 016 |
| Wald-Wolfowitz | `|Z| ≤ 1,96` | `|Z| ≤ z_{1−α/2}` | Ec. III-4 a III-6 |
| Helmert | `|S − C| ≤ √(n − 1)` | **Sin cambio**: no depende de α | Ec. III-7 |
| t de Student | `t_{1−0,05/2, ν}` | `t_{1−α/2, ν}` | Ec. III-8 |
| Cramer | `t_{1−0,05/2, n−2}` en los dos bloques | `t_{1−α/2, n−2}` | Ec. III-9 a III-11 |
| Mann-Kendall | `pymannkendall` con α = 0,05, `|Z| ≤ 1,96` | Pasar `alfa` a la librería y usar `z_{1−α/2}` | Ec. A.55 |
| Kolmogorov-Smirnov | `Z ≤ 1,358` (Tabla A.5, 5 %) | Valor de la Tabla A.5 para cada α si la tabla lo trae; si no, `c(α) = √(−ln(α/2)/2)`: 1,224 (10 %), 1,358 (5 %), 1,628 (1 %). A 5 % debe quedar exactamente 1,358 | Ec. A.56 y A.57, Tabla A.5 |
| Chow | `t_{1−0,10/(2n), n−2}` | `t_{1−α/n, n−2}`, prueba de un extremo por lado (ver bloque C) | Bulletin 17B, Ap. 4 |

Para Chow, la tabla de Bulletin 17B a 10 % sirve de verificación externa: con `α = 0,10` y `n = 30`, `K_N` tiene que dar 2,563 con una diferencia menor que 0,005. Con `α = 0,05` y `n = 30` tiene que dar 2,745, el valor actual.

### Tareas

1. **Núcleo.**
   - Reemplazar las constantes `ALPHA` de `independence.py`, `homogeneity.py` y `trend.py`, y `ALPHA_CHOW` de `outliers.py`, por un parámetro `alfa: float = 0.05` en cada función de prueba, propagado desde `ejecutar_etapa1(...)` y desde el pipeline de exclusión (`core/pipeline/exclusiones.py`).
   - Cada `Explicacion` agrega a sus términos `alfa` y el cuantil efectivamente usado (por ejemplo `z_critico`, `t_critico` o `t_bonferroni`), para que el modo paso a paso lo muestre sin calcular nada en el navegador.
   - Corregir los comentarios que dicen que Chow usa 10 % "distinto del 5 % global".
2. **API y servicios.**
   - `POST /analysis/stream`: nuevo campo de formulario `alfa` (por defecto `0.05`), validado contra el conjunto `{0.01, 0.05, 0.10}` en el borde. Fuera de ese conjunto: 400 con código nuevo `CONTRACT_ALFA_INVALID` (grupo "parámetros de request").
   - Pasarlo a la segunda ejecución de la Etapa 1 que corre después de rechazar un atípico. El mismo defecto ya ocurrió con `mes_inicio_anio`: hoy esa llamada repite los parámetros a mano, y `alfa` tiene que estar ahí.
   - Persistirlo en la configuración del análisis (columna JSONB, sin migración). Al leer análisis anteriores que no lo tienen, tratarlos como `0.05` y marcarlo como valor por defecto.
   - `POST /analysis/simulate-exclusion`: aceptar y aplicar `alfa`. La interfaz manda el del análisis original.
   - Informe PDF: mostrar α en la sección de configuración y en la tabla de pruebas.
3. **Cliente.**
   - Pantalla de configuración: selector "Nivel de significancia de la Etapa 1" con tres opciones (1 %, 5 %, 10 %). El 5 % viene seleccionado y lleva la etiqueta "estándar en hidrología". Línea explicativa debajo: "Con 10 % las pruebas rechazan con más facilidad, porque la zona de rechazo es más amplia; con 1 % solo rechazan ante evidencia muy fuerte."
   - Que el 5 % venga marcado es una configuración de la prueba, no una sugerencia sobre los resultados, y no contradice el principio de no decidir por el usuario. Registrarlo así en la decisión.
   - Historial y detalle: mostrar el α del análisis. Si no es 5 %, mostrarlo destacado.
   - Modo paso a paso: quitar todo valor crítico escrito a mano en las plantillas (por ejemplo "1,96" o el texto "α = 0,10 (no el 0,05 del resto de Etapa 1)" de Chow) y usar los términos que manda el servidor. Revisar también el modo experto y el desglose de Anderson (bandas).
   - Tipos: `alfa` en la configuración, en `SimulateExclusionRequest` y en el resultado persistido.
4. **Pruebas.**
   - Unitarias por prueba con α = 0,01, 0,05 y 0,10 contra valores de tabla: `z` de 2,576, 1,960 y 1,645; `t` con scipy; KS 1,628, 1,358 y 1,224; `K_N(30)` de 2,563 con α = 0,10 y 2,745 con α = 0,05.
   - Monotonía: con la misma serie, un rechazo con α = 0,01 implica rechazo con 0,05 y con 0,10, nunca al revés.
   - **No regresión con α = 0,05**: volcado de las nueve estaciones y de Las Tapias idéntico al de referencia.
   - Integración: el stream con `alfa=0.10` aplica el valor a las ocho pruebas y lo persiste. `alfa=0.2` da `CONTRACT_ALFA_INVALID`. Rechazar un atípico conserva el α en la segunda ejecución.
   - Interfaz: el selector envía el valor, el paso a paso muestra el α elegido y el historial lo muestra.
   - El escenario de extremo a extremo del análisis completo sigue pasando con el valor por defecto.
5. **Documentación.**
   - **DECISIÓN 078** (nivel de significancia configurable): la cita de Facundo, el alcance, la tabla de valores críticos, por qué 5 % viene marcado, por qué Helmert y la tolerancia de Anderson no cambian, y el requisito de no regresión.
   - **Revisión fechada de la DECISIÓN 018**: "Respondido por Facundo Ganancias Martínez el 18/10/2026: 5 % como estándar hidrológico. La implementación anterior (α = 0,10 repartido en dos colas) ya equivalía a 5 % por extremo; se reescribe en función de α sin cambiar valores." El estado pasa a resuelto.
   - Documento de fórmulas de la Etapa 1, contrato de la API (campo `alfa`, código nuevo) y catálogo de errores.

### Criterios de aceptación

- Con α = 5 %, resultados idénticos a los actuales en las diez series de referencia.
- Con α = 10 %, `K_N(30)` de Chow coincide con la tabla de Bulletin 17B.
- El α elegido se ve en la configuración, en el paso a paso, en el modo experto, en el historial y en el PDF, y se conserva al rechazar un atípico y al simular una exclusión.

### Consulta opcional a Facundo (no bloquea el bloque)

La tolerancia de Anderson (`⌈0,10 · k_max⌉` rezagos fuera de banda) queda fija. Con α = 1 % o 10 % podría argumentarse que debería acompañar a α. Preguntar en una línea: "¿la tolerancia del 10 % de rezagos fuera de banda en Anderson se mantiene fija aunque se cambie el nivel de significancia?". Hasta que responda, queda fija y declarada en la DECISIÓN 078.

---

## Bloque C. Chow: marcar todos los valores fuera de los umbrales, altos y bajos (DECISIÓN 079)

### Problema

`calcular_chow` toma solo el valor con mayor |z| (`argmax`) y lo compara con `K_N`. Si hay más de un valor más allá del umbral, marca uno solo. El gráfico de Chow, en cambio, dibuja las franjas `exp(ȳ ± K_N · S)`, y por eso el usuario ve dos puntos fuera de la franja (1994 y 2005 en la serie diaria de 40 años) pero el resultado y la pausa hablan de uno. Es una contradicción entre lo que muestra el gráfico y lo que decide la prueba.

### Fundamento

Bulletin 17B no prueba solo el valor más extremo. Calcula un umbral alto `X_H = ȳ + K_N · S` y uno bajo `X_L = ȳ − K_N · S` (sobre logaritmos), y **todo** valor por encima de `X_H` es un atípico alto y todo valor por debajo de `X_L` es un atípico bajo, cada lado como prueba de un extremo. Esa es también la lectura de "5 % por extremo" del bloque B. Implementarlo así hace coincidir el resultado con las franjas del gráfico.

Efecto sobre resultados ya verificados: en las nueve estaciones de la tesis Chow no marca ningún atípico, así que este bloque no cambia la regresión. Confirmarlo con el volcado de no regresión del bloque B.

### Decisión de diseño

- **Una sola pasada** (Bulletin 17B): se calculan `ȳ`, `S` y `K_N` sobre la serie completa y se listan todos los valores fuera de los umbrales. No se vuelve a probar después de quitar uno. El enmascaramiento queda declarado en el libro, y la exclusión de puntos permite explorar qué pasa sin ellos.
- **Una sola pausa** que presenta la lista completa, con una decisión por punto (rechazar o aceptar), los dos botones con el mismo estilo, sin opción preseleccionada y con el foco en el diálogo, igual que hoy. El botón para continuar se habilita recién cuando todos los puntos tienen decisión.
- Los puntos rechazados se excluyen **juntos**, con la misma operación que usa la simulación de exclusión.
- La segunda ejecución de la Etapa 1, sobre la serie sin los rechazados, sigue informando Chow **sin pausar**, como hoy y como la simulación (DECISIÓN 071). Si esa pasada encuentra valores nuevos fuera de los umbrales, la pantalla de resultados lo dice en una línea y los marca como sugeridos en el panel de exclusión. No se abre una segunda pausa.

### Tareas

1. **Núcleo (`outliers.py`).**
   - Calcular `z_i` con signo sobre logaritmos. Atípicos altos: `z_i > K_N`. Atípicos bajos: `z_i < −K_N`.
   - Nuevo campo en `TestResult` (o en la explicación de Chow, según lo que menos rompa): `atipicos: list[{indice, valor, z, lado: "alto" | "bajo"}]`, ordenada por |z| descendente.
   - Mantener `estadistico = max |z_i|`, y `valor_atipico` e `indice_atipico` como el más extremo, por compatibilidad con análisis guardados y con el informe.
   - `veredicto = "rechazada"` si la lista no está vacía.
   - La explicación agrega los umbrales en escala original, `limite_inferior = exp(ȳ − K_N · S)` y `limite_superior = exp(ȳ + K_N · S)`. **El gráfico tiene que dibujar exactamente estos valores**: verificar si hoy los calcula el cliente y, en ese caso, pasarlo a leerlos del servidor.
   - Prueba de consistencia: todo punto fuera de `[limite_inferior, limite_superior]` está en `atipicos`, y todo punto de `atipicos` está fuera.
2. **Servicios y API.**
   - Evento SSE `outlier_detected`: `{session_id, atipicos: [{indice, periodo, valor, z, lado}], valor_atipico}`. El último campo se conserva por compatibilidad.
   - `POST /analysis/outlier-decision`: cuerpo `{session_id, decisiones: [{indice, decision: "rechazar" | "aceptar"}]}`. Validar que el conjunto de índices coincida exactamente con el detectado; si no, 400 con código nuevo `OUTLIER_DECISION_INVALID`.
   - `session_store`: guardar la lista de decisiones en el `dict` de decisión (DECISIÓN 053).
   - Aplicar los rechazos con una sola llamada a la operación de exclusión sobre `serie_efectiva` y sus `timestamps_efectivos`, mapeando cada índice con `_mapear_indice_a_serie_original`. Reemplaza el `del serie_filtrada[indice_real]` de un solo índice.
   - Persistencia (`decisiones["chow"]`): `{atipicos: [{indice, periodo, valor, lado, decision}]}`. El historial y el PDF tienen que seguir leyendo la forma vieja (`{decision, dato}`) de los análisis ya guardados.
   - Auditoría: un código por punto (`TEST_OUTLIER_REJECTED_BY_USER` / `TEST_OUTLIER_ACCEPTED_BY_USER`) con el año y el valor en la descripción.
   - Informe PDF: tabla con todos los atípicos detectados, su lado y la decisión de cada uno.
3. **Cliente.**
   - Diálogo de la pausa: lista de los puntos (año, valor, lado alto o bajo, distancia en desvíos), dos botones iguales por fila y un botón "Continuar con estas decisiones" habilitado cuando todas las filas están decididas. Se mantiene la línea "METIS no recomienda ninguna respuesta". Escape no cierra.
   - Pendiente arrastrado de la DECISIÓN 018 / RF-CU01-07: si entra en el bloque, incluir en el diálogo el gráfico de Chow con las franjas, porque ahora el usuario decide sobre varios puntos y verlos en el gráfico ayuda. Si no entra, dejarlo anotado como pendiente.
   - Gráfico de Chow: marcar con su propio símbolo todos los puntos de la lista, sin depender solo del color.
   - Panel de exclusión: todos los atípicos detectados aparecen como sugeridos y ninguno viene seleccionado.
   - Modo paso a paso de Chow: mostrar los dos umbrales y la regla "todo valor más allá de los umbrales es atípico (Bulletin 17B)". El desglose por observación resalta las filas con |z| > K_N.
4. **Pruebas.**
   - Núcleo: una serie con dos atípicos bajos y uno alto devuelve los tres con su lado. Una serie sin atípicos devuelve la lista vacía. La serie diaria de 40 años devuelve 1994 y 2005.
   - Servicio: decidir los tres puntos (dos rechazos y una aceptación) excluye exactamente los dos rechazados. Decisiones incompletas o con índices ajenos dan `OUTLIER_DECISION_INVALID`.
   - Actualizar `test_simulate_exclusion_equivale_a_chow.py`: excluir los k puntos rechazados por simulación tiene que dar el mismo resultado que rechazarlos en la pausa.
   - Interfaz: el diálogo no permite continuar con filas sin decidir, los botones de cada fila son idénticos y el foco inicial no cae en ningún botón.
   - Extremo a extremo: actualizar el escenario del análisis completo si su serie de prueba pasa por la pausa de Chow.
5. **Documentación.**
   - **DECISIÓN 079**: el problema (gráfico y prueba en contradicción), la regla de Bulletin 17B, una sola pasada, una sola pausa con decisión por punto, el enmascaramiento declarado, la compatibilidad con análisis viejos y los códigos nuevos.
   - Contrato de la API: evento SSE, cuerpo del punto de acceso de decisión y forma persistida. Catálogo de errores.

### Criterios de aceptación

- En la serie diaria de 40 años, la pausa presenta 1994 y 2005, y el gráfico marca los dos.
- Ningún punto queda fuera de las franjas del gráfico sin estar en la lista, y ningún punto de la lista queda dentro.
- Las nueve estaciones de la tesis siguen sin atípicos.
- Los análisis guardados antes del cambio se abren en el historial y se exportan a PDF sin errores.

---

## Bloque D. Chow no ejecutado por negativos o ceros: mensaje y marcas en la serie (revisión de la DECISIÓN 073)

### Problema

Con la serie `negativos otro.csv` cargada como caudal/precipitación (40 datos, cinco negativos, mínimo de −0,74), Chow no se ejecuta, porque trabaja sobre logaritmos (DECISIÓN 073, `TEST_NOT_EXECUTED_NEGATIVES`). Sin embargo, el gráfico de Chow se dibuja igual que la serie temporal, sin franjas y sin ninguna indicación de que la prueba no corrió, y los valores negativos no tienen ninguna marca. El usuario espera verlos marcados como atípicos.

### Por qué no se marcan como atípicos (no hay contradicción con la teoría)

Un atípico es un concepto estadístico: un valor demasiado alejado del resto en relación con la dispersión de la serie. En esta serie, −0,74 está a unos 1,9 desvíos de la media (0,99 con un desvío de 0,90), dentro de lo esperable. Un caudal negativo es otra cosa: un valor **físicamente imposible**, que delata un error de carga o de medición. Eso no lo detecta Chow sino el contrato de datos, que ya lo advierte (`CONTRACT_NEGATIVE_VALUES`). Marcarlo como "atípico de Chow" mezclaría dos conceptos y además no es posible calcularlo, porque el logaritmo de un negativo no existe. Lo que falta no es cambiar la prueba sino **mostrar mejor** lo que ya se sabe.

### Tareas

1. **Servidor.** En el resultado de Chow no ejecutado por negativos o por ceros, agregar a la explicación la lista de índices y valores que impidieron la prueba (`valores_no_validos: [{indice, periodo, valor}]`). Es dato, no cálculo, y evita que el cliente lo infiera por su cuenta.
2. **Gráfico de Chow.** Si la prueba no se ejecutó, no dibujar franjas y mostrar arriba del gráfico: "La prueba de Chow no se ejecutó: hay N valores negativos (o ceros), y la prueba trabaja sobre logaritmos. Estos valores son físicamente imposibles en una serie de caudal o precipitación; podés excluirlos abajo y recalcular." Marcar esos puntos con un símbolo propio y una leyenda distinta de la de atípico.
3. **Panel de exclusión.** Marcar esos años como "valor no válido para Chow", con una marca distinta de "sugerido por Chow" y sin preseleccionar ninguno.
4. **Recálculo.** Verificar que al excluir los negativos y recalcular, Chow se ejecuta en la simulación y muestra su resultado normal.
5. **Tipo "Otro".** Con tipo "Otro" un negativo puede ser válido. El mensaje no dice "físicamente imposible", sino: "Chow no se ejecutó porque la serie tiene valores negativos y la prueba trabaja sobre logaritmos."
6. **Pruebas.** Gráfico sin franjas y con el mensaje cuando la prueba no corrió; marcas en los puntos; textos distintos para caudal y para "Otro"; recálculo sin negativos que ejecuta Chow.
7. **Documentación.** Revisión fechada de la DECISIÓN 073 con el cambio de presentación.

### Criterios de aceptación

- Con `negativos otro.csv`, el gráfico de Chow explica por qué no hay franjas y señala los cinco negativos.
- Al excluirlos y recalcular, Chow se ejecuta y se ve su resultado.

---

## Verificación final del conjunto (después de los cuatro bloques)

- [ ] Volcado de la Etapa 1 de las nueve estaciones y de Las Tapias con α = 5 %, idéntico al de referencia.
- [ ] Recorrido manual en el navegador con: Las Tapias, la serie de la captura con el atípico de 950, la serie diaria de 40 años y `negativos otro.csv`, en modo experto y paso a paso, como usuario anónimo y con sesión.
- [ ] Informe PDF de un análisis con α = 10 % y dos atípicos decididos, y de un análisis guardado antes de los cambios.
- [ ] Los ocho trabajos de la integración continua en verde, sin bajar la cobertura del código nuevo.
- [ ] DECISIONES 078 y 079 escritas, revisiones de 018, 071 y 073, contrato de la API y catálogo actualizados.
- [ ] Avisar a Kevin las cifras nuevas para el libro: cantidad de pruebas del servidor y del cliente, decisiones totales y pedidos de incorporación.

## Impacto en el libro (lo resuelve Kevin con asistencia, no Claude Code)

- §6.1.6 y Tabla 9: α configurable con 5 % por defecto; Chow como prueba de un extremo por lado con todos los valores fuera de los umbrales; se elimina la "consulta abierta" sobre Chow.
- RNF-02: "nivel de significancia configurable en la Etapa 1 (1 %, 5 % o 10 %), 5 % por defecto como estándar hidrológico".
- Marco Teórico §5.2.2 y §5.2.6: el 5 % como estándar hidrológico, citado como comunicación personal de F. M. Ganancias Martínez (18 de octubre de 2026); Bulletin 17B usa 10 %.
- Tabla de hallazgos de la auditoría: la fila de Chow pasa a resuelta.
- Caso Las Tapias: K_N = 2,824 con α = 5 %; se quita la comparación con la variante de dos colas.
- Pantallas nuevas para capturas: selector de α en la configuración, pausa de Chow con varios atípicos y exploración con la vista "Sin los puntos excluidos".
