# DECISIÓN 073 — Valores negativos: estado propio `disabled_negatives` en Etapa 2 y código propio para Chow

**Fecha:** 1 de octubre de 2026
**Estado:** Decidida y aplicada (backend; el frontend ya estaba preparado)
**Decide:** Kevin (opción elegida el 20/09/2026; implementada en el PR 3 del plan de fixes post-verificación).
**Origen:** pedido de Catalini en el feedback de directores (ítem C,
[`plan-backend-feedback-directores-20-09-2026.md`](../plan-backend-feedback-directores-20-09-2026.md) §1).

### Contexto

Con tipo de variable "Otro" un valor negativo es un dato válido (un nivel referido a un cero de escala, una
temperatura). Pero cinco distribuciones no están definidas para negativos: Log-Normal 2p, Log-Pearson III,
Gamma 2p y Exponencial (β) devolvían `no_aplicable` con `serie <= 0`, y Generalizada Exponencial con
`serie < 0`. Ese `no_aplicable` era indistinguible de un fallo numérico: el usuario no tenía forma de saber que el
motivo eran los negativos de su serie. Lo mismo pasaba con Chow, que trabaja sobre logaritmos: un negativo caía en
`TEST_NOT_EXECUTED_CONDITION`, el código genérico.

### Alternativas evaluadas

- **(1) Trasladar la serie, `x' = x + c`.** Descartada: el resultado depende de `c`, que es arbitrario, y elegir
  `c` a mano equivale a fijar un tercer parámetro de posición que las distribuciones de 3 parámetros ya
  **estiman** (Log-Normal 3p, Gamma 3p, Exponencial x0-β, Generalizada de Pareto).
- **(2) Chow sin logaritmos para "Otro" (Grubbs 1969).** Pendiente, no descartada: exige una referencia
  bibliográfica nueva en `formulas-etapa1.md` y el aval de los directores.
- **(3) Elegida: estado propio, análogo a `disabled_zeros`.** No cambia ningún número; solo la trazabilidad.

### La decisión

- `core/etapa2/types.py`: `STATUS_DISABLED_NEGATIVES = "disabled_negatives"`, junto a `STATUS_DISABLED_ZEROS`.
- `core/etapa2/distributions/__init__.py`: `DISABLED_WITH_NEGATIVES` con las cinco. Las de 3 parámetros no entran:
  estiman su parámetro de posición y deciden por su cuenta con su chequeo `x0 >= min(serie)` (DECISIÓN 060).
- `ejecutar_etapa2(serie, tiene_ceros=False, tiene_negativos=False)`: default `False` para no romper a quien no
  lo pase (`services/analysis_service.py` y `core/pipeline/full_pipeline.py` lo pasan). **Precedencia:** con
  negativos y ceros a la vez gana `disabled_negatives`, el motivo más fuerte.
  `gen_exponencial.ajustar()` devuelve además el estado nuevo con su propio chequeo `serie < 0`, por si se la
  llama directo.
- `tiene_negativos` se guarda en `SessionState` junto a `tiene_ceros`.
- **Chow:** código nuevo `TEST_NOT_EXECUTED_NEGATIVES`, evaluado **primero**, antes del de ceros (misma
  precedencia que en Etapa 2). Va al catálogo (`api-contracts.md`) y a `errors.es.ts` en el mismo commit;
  `DIST_DISABLED_NEGATIVES` se documenta junto a `DIST_DISABLED_ZEROS`, igual que ese.
- **Depende de los datos, no de `tipo_variable`**, igual que `tiene_ceros`. Una serie Caudal/Precip. con
  negativos (que ya recibe `CONTRACT_NEGATIVE_VALUES`) recibe el mismo estado.
- **Análisis ya persistidos:** conservan su `no_aplicable`. `POST /analysis/{id}/design-events` no reajusta, lee el
  ranking guardado. Sin backfill (DECISIÓN 058 §4); la card atenuada del frontend (F3 del plan de fixes
  post-verificación) los cubre igual con el rótulo genérico "sin ajuste posible con esta serie".

### Consecuencias

- Ningún estadístico ni EEA cambia. Ninguna de las 9 series de regresión tiene negativos: su salida es byte a byte
  idéntica (verificado con la herramienta del Apéndice C de `hallazgo-timestamps-desalineados.md`).
- Cambia un código: una serie Caudal/Precip. con un negativo **y** un cero antes recibía `TEST_NOT_EXECUTED_ZEROS`
  en Chow y ahora recibe `TEST_NOT_EXECUTED_NEGATIVES`.
- En pantalla, las cinco aparecen al final del ranking, atenuadas, con "no aplica: la serie tiene valores
  negativos".

### Nota de alcance

"Otro" sigue agregando a **máximos** anuales. Si Catalini piensa en variables donde el extremo de interés es el
mínimo (estiajes, temperaturas mínimas), es otra funcionalidad, no esta (pregunta abierta en
`pendientes-facundo.md`, "Función de agregación para tipo_variable == otro").

### Revisión 19/10/2026 — presentación de Chow no ejecutada

Bloque D de `docs/historico/planes/plan-significancia-y-fixes-18-10-2026.md`. Con `serie_con_negativos_otro.csv` cargada como
caudal/precipitación, Chow no se ejecutaba (como corresponde), pero el gráfico de Chow se dibujaba igual que la
serie temporal, sin franjas ni aviso, y los cinco negativos no tenían marca. El usuario esperaba verlos como
atípicos.

**No se marcan como atípicos.** Un atípico es un valor demasiado alejado del resto según la dispersión de la
serie: −0,74 está a unos 1,9 desvíos de la media en esa serie. Un caudal negativo es otra cosa, un valor
físicamente imposible que delata un error de carga o de medición, y eso ya lo advierte el contrato
(`CONTRACT_NEGATIVE_VALUES`). Además Chow no se puede calcular con él: no tiene logaritmo. La prueba no cambia;
cambia cómo se muestra lo que ya se sabe.

- **Servidor.** `TestResult.valores_no_validos` = `[{indice, valor}]`: los negativos con
  `TEST_NOT_EXECUTED_NEGATIVES` y los ceros con `TEST_NOT_EXECUTED_ZEROS`/`TEST_NOT_EXECUTED_CONDITION`, en el
  espacio de `serie_efectiva`. Es un campo propio y no va dentro de `explicacion`, porque el frontend usa
  `explicacion === null` como señal de "no ejecutada". El año lo pone el cliente desde `timestamps_efectivos`,
  igual que con `valores_atipicos` (DECISIÓN 079).
- **Gráfico de Chow.** Sin franjas, con un aviso arriba que dice por qué no corrió y cuántos valores lo
  impidieron. Esos puntos van con un cuadrado (`--warn`) y una leyenda propia, distinta del rombo de atípico.
- **Texto.** "Físicamente imposible" se dice solo de un **negativo en caudal o precipitación**, con la sugerencia
  de excluirlos y recalcular. Con tipo "Otro" un negativo puede ser válido: "Chow no se ejecutó porque la serie
  tiene valores negativos y la prueba trabaja sobre logaritmos", sin sugerencia. Para los ceros se explica el
  logaritmo de cero y no se los llama imposibles: un caudal o una precipitación nula es un dato posible. Esto
  corrige el texto del plan, que decía "negativos (o ceros) físicamente imposibles".
- **Panel de exclusión.** Esos años llevan la marca "valor no válido para Chow" (borde y marca cuadrada
  `--crit`), distinta de "sugerido por Chow", y ninguno viene seleccionado.
- **Recálculo.** Excluidos los negativos, la simulación (DECISIÓN 071) ejecuta Chow y muestra su resultado
  normal (`test_al_excluir_los_negativos_la_simulacion_ejecuta_chow`).
- **Análisis anteriores.** No traen el campo: el gráfico avisa que Chow no corrió, sin marcas.

### Relación con otras decisiones

- **DECISIÓN 060** — chequeo `x0 >= min(serie)` de las distribuciones de 3 parámetros.
- **DECISIÓN 061** — ceros en las distribuciones de 3 parámetros; `disabled_zeros` sigue como antes.
- **DECISIÓN 071** — exclusión de puntos; el recálculo sin los negativos.
- **DECISIÓN 079** — Chow con todos los atípicos; misma forma de lista y mismo gráfico.
- **DECISIÓN 070** — umbral de `DIST_HIGH_EEA`. Con "Otro" y una media cerca de cero, el 5 % de la media deja de
  significar algo; anotado en `pendientes-tecnicos.md`, sin cambiar el umbral.
