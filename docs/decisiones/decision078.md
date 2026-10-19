# DECISIÓN 078: nivel de significancia configurable en la Etapa 1 (1 %, 5 % o 10 %)

**Fecha:** 18 de octubre de 2026
**Estado:** Decidida y aplicada (backend + frontend + informe PDF) — bloque B de
`docs/historico/planes/plan-significancia-y-fixes-18-10-2026.md`.
**Decide:** Kevin, a partir de la respuesta de Facundo Ganancias Martínez.
**Origen:** la consulta sobre el nivel de significancia de Chow, abierta desde la DECISIÓN 018.

### Contexto

Hasta acá α era una constante: 0,05 en siete pruebas y "0,10 repartido en dos colas" en Chow, con un comentario
que lo presentaba como distinto del resto de la Etapa 1. `constraints.md` lo listaba como no configurable en V1.0.

El 18/10/2026 Facundo respondió:

> "La prueba de K_N de Chow y todas las pruebas de estadística para hidrología se hacen con un nivel de
> significancia del 5 %, eso es como estandarización de las pruebas estadísticas de hidrología a nivel mundial.
> Algunos programas estadísticos que se pueden usar para otras cuestiones que no sean hidrología te dan la opción
> de trabajar con un nivel de significancia del 10 %, que es más exigente porque la zona de rechazo es más amplia,
> o con el 1 %, que es la más permisiva porque la zona de rechazo es muy chiquitita. Si vos tenés la opción de
> poner las 2 alternativas y que el usuario elija sería un golazo; si no, pondría solamente la del 5 %, apuntando
> el programa a análisis estadístico hidrológico."

### La decisión

- **Un parámetro `alfa ∈ {0,01; 0,05; 0,10}`**, elegido en la configuración del análisis, que se aplica a las ocho
  pruebas de la Etapa 1. **0,05 por defecto.** La Etapa 2 no tiene nivel de significancia y no cambia. El umbral
  de `DIST_HIGH_EEA` (5 % de la media, DECISIÓN 070) no es un nivel de significancia y tampoco cambia.
- **Valor crítico de cada prueba en función de α** (`core/etapa1/significancia.py`):

  | Prueba | Valor crítico | Fuente |
  |---|---|---|
  | Anderson | bandas `(−1 ± z_{1−α/2}·√(n−k−1))/(n−k)` | Ec. III-3 |
  | Wald-Wolfowitz | `\|Z\| ≤ z_{1−α/2}` | Ec. III-4 a III-6 |
  | Helmert | `\|S − C\| ≤ √(n − 1)` — **no depende de α** | Ec. III-7 |
  | t de Student | `t_{1−α/2, ν}` | Ec. III-8 |
  | Cramer | `t_{1−α/2, n−2}` en los dos bloques | Ec. III-9 a III-15 |
  | Mann-Kendall | `\|Z\| ≤ z_{1−α/2}`; `pymannkendall` decide con el mismo α | Ec. A.55 |
  | Kolmogorov-Smirnov | 1,628 / **1,358** / 1,224 para 1 / 5 / 10 % | Ec. A.57, Tabla A.5 |
  | Chow | `K_N` con `t_{1−α/n, n−2}`: α en cada extremo | Bulletin 17B, Ap. 4 |

  Para Kolmogorov-Smirnov, la Tabla A.5 de Caamaño Nelli y Colladon da 1,358 a 5 %; para 1 % y 10 % se usa
  `c(α) = √(−ln(α/2)/2)`, la aproximación asintótica de la que sale 1,358, redondeada igual a tres decimales.
- **El 5 % viene marcado** en la pantalla de configuración con la etiqueta "estándar en hidrología". No contradice
  el principio de que METIS no decide por el usuario: es una configuración de la prueba, como el mes de inicio del
  año (DECISIÓN 057), no una sugerencia sobre los resultados. Las tres opciones tienen el mismo peso visual salvo
  ese rótulo.
- **Lo que no depende de α y queda fijo:** Helmert (su regla no tiene nivel de significancia) y la tolerancia de
  Anderson de `⌈0,10·k_max⌉` rezagos fuera de banda (DECISIONES 012 y 016: es la regla de la tesis, no un α). Se
  podría argumentar que la tolerancia acompañe a α; la consulta a Facundo queda abierta y no bloquea: "¿la
  tolerancia del 10 % de rezagos fuera de banda en Anderson se mantiene fija aunque se cambie el nivel de
  significancia?".
- **Chow usa el mismo α que el resto.** La implementación anterior, `t_{1−0,10/(2n)}`, ya era `t_{1−0,05/n}`: el
  5 % por extremo que pide Facundo. Se reescribe en función de α sin mover ningún valor. Con α = 0,10 y n = 30,
  `K_N` da 2,5651, contra 2,563 de la tabla de Bulletin 17B a 10 % (diferencia 0,002); con α = 0,05, 2,7451.

### Requisito: con α = 5 % nada cambia

`tests/unit/core/pipeline/test_no_regresion_alfa.py` compara, de forma exacta y también en los floats, la Etapa 1
de las 9 estaciones de la tesis, el caso Las Tapias del libro (1942–1979, n = 36) y las series de
`docs/series prueba/` contra una referencia generada con el código previo al cambio
(`generar_referencia_etapa1.py`). Solo se toleran claves nuevas (`alfa`, `z_critico`, `t_critico` en
`explicacion.terminos`). Pasa sin diferencias: `norm.ppf(1 − α/2)` con α = 0,05 es el mismo `norm.ppf(0.975)` de
antes, y `0,10/(2n)` y `0,05/n` son la misma división redondeada.

### Borde, transporte y persistencia

- `POST /analysis/stream`: campo `alfa` (texto, `"0.05"` por defecto) validado en el borde; fuera del conjunto, o
  no numérico, 400 `CONTRACT_ALFA_INVALID`. `POST /analysis/simulate-exclusion` acepta y valida el mismo campo.
- La segunda pasada de la Etapa 1, la que corre después de rechazar un atípico, recibe el mismo α: esa llamada
  repite los parámetros a mano, y el mismo defecto ya ocurrió con `mes_inicio_anio` (hallazgo V2).
- `result_etapa1.alfa` y `analyses.configuracion.alfa`. Sin migración (JSONB). Un análisis anterior se lee con
  `alfa: 0.05, alfa_implicito: true` (`GET /history/{id}`) y `alfa: 0.05` en la lista del historial, sin backfill
  (mismo criterio que `timestamps`, DECISIÓN 058 §4).
- `core/` valida α también (`validar_alfa`): no confía en el borde.
- Cada `Explicacion` suma `alfa` y el cuantil usado, para que el paso a paso los muestre sin calcularlos en el
  navegador. El frontend dejó de escribir a mano "1,96", "95 %" y "α = 0,10" en las plantillas.
- Se ve en la configuración, en los resultados (destacado si no es 5 %), en el historial y en el PDF.

### Consecuencias

- La regla "α = 5 % fijo, no configurable en V1.0" de `constraints.md`, `core-etapa1-implementation.md`,
  `formulas-etapa1.md` y `statistical-pipeline.md` queda reemplazada por esta decisión.
- La DECISIÓN 018 deja de estar abierta en el nivel de significancia (revisión del 18/10/2026 en ese archivo).
- Test de monotonía: con la misma serie, lo que rechaza con 1 % rechaza con 5 % y con 10 %, nunca al revés.

### Relación con otras decisiones

- **DECISIÓN 018** — K_N de Chow; esta decisión resuelve su nivel de significancia.
- **DECISIONES 012 y 016** — tolerancia de Anderson, que no cambia.
- **DECISIÓN 057** — mismo criterio para un parámetro del análisis: se persiste y se repite en la segunda pasada.
- **DECISIÓN 070** — el umbral de EEA no es un nivel de significancia.
- **DECISIÓN 079** — Chow con todos los valores fuera de los umbrales, prueba de un extremo por lado.
