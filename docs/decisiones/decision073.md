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

### Relación con otras decisiones

- **DECISIÓN 060** — chequeo `x0 >= min(serie)` de las distribuciones de 3 parámetros.
- **DECISIÓN 061** — ceros en las distribuciones de 3 parámetros; `disabled_zeros` sigue como antes.
- **DECISIÓN 070** — umbral de `DIST_HIGH_EEA`. Con "Otro" y una media cerca de cero, el 5 % de la media deja de
  significar algo; anotado en `pendientes-tecnicos.md`, sin cambiar el umbral.
