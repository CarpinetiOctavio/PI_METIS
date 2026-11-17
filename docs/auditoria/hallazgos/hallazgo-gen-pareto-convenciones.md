# Hallazgo — Generalizada de Pareto: dos convenciones de signo mezcladas, IV-167 con el signo cambiado y Mínimos Cuadrados que no recupera el parámetro

**Fecha:** 1 de octubre de 2026. **Autores:** Kevin, con Claude.
**Veredicto:** **CONFIRMADO** (problemas 1 y 2); **CONFIRMADO el síntoma, causa hipotética** (problema 3).
**Qué se hizo en V1.0:** mitigación en pantalla, sin tocar ninguna fórmula ni ningún número —
[DECISIÓN 074](../../decisiones/decision074.md). **Qué queda para la V2:** la corrección de las fórmulas, con la guía de §8.

---

## 1. Resumen

La sección IV.3.10 de la tesis (páginas 73 a 76 del PDF, ecuaciones IV-145 a IV-174) tiene tres
inconsistencias, y `core/etapa2/distributions/gen_pareto.py` las reproduce fielmente porque copia la tesis:

1. **Dos convenciones de signo del parámetro de forma mezcladas.** Los cuatro métodos de estimación están
   escritos en la convención de Hosking (con ε > 0 la distribución tiene techo). La densidad IV-145, la
   distribución IV-146 y el cuantil IV-174 están en la de Coles (con ε > 0 la cola es pesada). METIS estima ε
   con un significado y calcula los eventos de diseño con el contrario.
2. **IV-167 (Momentos de Probabilidad Pesada) tiene el signo del numerador cambiado.** Con "+" el estimador
   da ε ≈ 4 sea cual sea la serie; despejado de las propias IV-168 a IV-171 lleva "−".
3. **Mínimos Cuadrados no recupera el parámetro.** IV-153, tal como quedó transcrita en la DECISIÓN 068, da
   ε ≈ 1 sea cual sea la serie, e IV-155 no es dimensionalmente consistente.

**Impacto:** Etapa 1 y las otras 12 distribuciones no se ven afectadas. En la mayoría de las estaciones el
error se ve (Pareto queda abajo en el ranking con EEA absurdos) y nadie la elegiría. **El caso peligroso es
est_02**: Pareto sale primera con "menor EEA" y sus eventos de diseño salen inflados entre un 32 % y un 47 %.
La tesis marca Pareto como "No converge" en todas sus tablas, así que **ningún valor de referencia de la
tesis se rompe** al corregirla.

**Postura ante el tribunal:** METIS es fiel a la fuente, detectó la inconsistencia, la midió, la contuvo y la
dejó documentada.

---

## 2. Las dos convenciones

La Pareto Generalizada se escribe en dos convenciones con el parámetro de forma de signo opuesto (ε_Hosking =
k, ε_Coles = ξ = −k). Con z = (x − µ)/σ:

| | Hosking (k) | Coles (ξ = −k) |
|---|---|---|
| Distribución F(x) | `1 − (1 − k·z)^(1/k)` | `1 − (1 + ξ·z)^(−1/ξ)` |
| Densidad f(x) | `(1/σ)·(1 − k·z)^(1/k − 1)` | `(1/σ)·(1 + ξ·z)^(−1/ξ − 1)` |
| Cuantil x(F) | `µ + (σ/k)·[1 − (1 − F)^k]` | `µ + (σ/ξ)·[(1 − F)^(−ξ) − 1]` |
| Media | `µ + σ/(1 + k)` | `µ + σ/(1 − ξ)` |
| Varianza | `σ²/[(1 + k)²·(1 + 2k)]` | `σ²/[(1 − ξ)²·(1 − 2ξ)]` |
| Con el parámetro > 0 | **techo** en `µ + σ/k` | **cola pesada**, sin techo |

### A qué convención pertenece cada ecuación de la tesis

| Ecuaciones | Qué son | Convención | Cómo se reconoce |
|---|---|---|---|
| IV-145 | Densidad | **Coles** | `(1/σ)·(1 + ε(x−µ)/σ)^(−1/ε − 1)` |
| IV-146 | Distribución | **Coles** | `1 − (1 + ε(x−µ)/σ)^(−1/ε)` |
| IV-147 a IV-149 | Momentos (media, asimetría, varianza) | **Hosking** | media `µ + σ/(1+ε)`, varianza `σ²/((1+2ε)(1+ε)²)` |
| IV-150 a IV-152 | Máxima Verosimilitud | **Hosking** | `((1−ε)/ε)·Σ ln(1 − ε(x−µ)/σ)` |
| IV-153 a IV-166 | Mínimos Cuadrados | **Hosking** | variable auxiliar `z = (1 − F)^ε` |
| IV-167 a IV-173 | Momentos de Probabilidad Pesada | **Hosking** (IV-167 con signo cambiado) | `σ = (1+ε)(2+ε)·I2`, `µ = x1 − σ/(n+ε)` |
| IV-174 | Cuantil | **Coles** | `[(1/(1−F))^ε − 1]·σ/ε + µ` |

IV-145 e IV-146 se leyeron del texto extraído del PDF (páginas 73 y 74); IV-147 a IV-174, de su transcripción en
[`formulas-etapa2.md`](../../../.claude/rules/core/formulas-etapa2.md) §10, verificada contra el PDF el 01/10/2026.

---

## 3. Problema 1 — convenciones mezcladas (afecta a los cuatro métodos)

METIS estima ε con fórmulas de Hosking y lo pasa a `cuantil()`, que implementa IV-174 (Coles). Con ε > 0 el
modelo estimado tiene techo, pero IV-174 lo evalúa como de cola pesada y los cuantiles altos explotan. Con
ε < 0 pasa lo contrario: el cuantil se queda corto.

**Cuantil coherente con los estimadores:** `x = µ + (σ/ε)·[1 − (1 − F)^ε]` (límite ε → 0: `x = µ − σ·ln(1 − F)`,
el mismo que hoy).

**Evidencia:** Momentos recupera el parámetro real en la convención de Hosking (tabla de §4), así que los
estimadores son de Hosking. Y el EEA de Momentos con el cuantil coherente es creíble en todas las estaciones
donde se puede calcular (tabla de §6): con el cuantil de la tesis llega a 5229 en est_09.

---

## 4. Problema 2 — IV-167 tiene el signo del numerador cambiado

La tesis imprime `ε = (n·I1 + 2·I2·(n−1)) / (I2·(n−1) − I1)`. Despejando ε de las propias IV-168 a IV-171 de la
tesis, que son consistentes con Hosking:

1. **El mínimo de la muestra.** Para una Pareto de Hosking (µ, σ, k), `P(X > x) = (1 − k·z)^(1/k)`, así que el
   mínimo de n valores cumple `P(min > x) = (1 − k·z)^(n/k) = (1 − (k/n)·(n·z))^(1/(k/n))`: es otra Pareto de
   Hosking con parámetros (µ, σ/n, k/n). Su esperanza es `µ + (σ/n)/(1 + k/n)`, es decir
   `E[x(1:n)] = µ + σ/(n + k)`. Es exactamente IV-169 (`µ = x1 − σ/(n+ε)`) leída al revés. Entonces:
   `I1 = M0 − x1 = [µ + σ/(1+k)] − [µ + σ/(n+k)] = σ·(n − 1) / ((1 + k)·(n + k))`.
2. **Los momentos de probabilidad pesada.** Para Hosking, `α0 = µ + σ/(1+k)` y `α1 = µ/2 + σ/(2·(2+k))`. Entonces:
   `I2 = M0 − 2·M1 = σ/(1+k) − σ/(2+k) = σ / ((1 + k)·(2 + k))`. De acá sale IV-168: `σ = (1+k)(2+k)·I2`.
3. **El cociente:** `I1/I2 = (n − 1)·(2 + k)/(n + k)`.
4. **Despejando k:** `I1·(n + k) = I2·(n − 1)·(2 + k)` ⇒ `k·(I1 − I2·(n−1)) = 2·I2·(n−1) − n·I1` ⇒

   **`ε = (n·I1 − 2·I2·(n − 1)) / (I2·(n − 1) − I1)`**

   El denominador coincide con el de la tesis; el segundo término del numerador cambia de signo.

**Evidencia — recuperación del parámetro.** Mediana de 400 muestras simuladas por fila (n = 40, µ = 50, σ = 30,
semilla 1), generadas en la convención de Hosking:

| ε real | MPP de la tesis (+) | MPP con signo corregido (−) | Momentos | Mínimos Cuadrados |
|---|---|---|---|---|
| −0,2 | 3,98 | −0,21 | −0,02 | 0,94 |
| 0,1 | 4,28 | 0,06 | 0,18 | 0,97 |
| 0,4 | 4,54 | 0,30 | 0,44 | 0,99 |

MPP con "+" da alrededor de 4 siempre. Esto explica el "épsilon físicamente implausible en las 9 estaciones"
que [`consolidacion-e2e.md`](../regresion/regresion-e2e-coreEstadistico/consolidacion-e2e.md) §8 registraba sin
causa.

---

## 5. Problema 3 — Mínimos Cuadrados no recupera el parámetro

**Lo verificado:**

- IV-153, tal como quedó transcrita en la [DECISIÓN 068](../../decisiones/decision068.md), tiene **una sola
  raíz, cerca de ε = 1, sea cual sea la serie**: sobre una muestra con k = 0,1 (semilla 2) la raíz es 0,975.
  En la tabla de §4, Mínimos Cuadrados da entre 0,94 y 0,99 para cualquier ε real.
- Un ajuste de mínimos cuadrados común (x contra z(ε) con `z = (1 − F)^ε`) **sí** recupera el parámetro: 0,18
  sobre esa misma muestra.
- IV-155, `µ = x1 − (ε/µ)·(1 − z1)`, **no es dimensionalmente consistente**: resta una cantidad en 1/unidades a
  un valor con unidades.

**La hipótesis (no verificada):** lo coherente con `x = µ + (σ/ε)·(1 − z)` evaluado en i = 1 es
`µ = x1 − (σ/ε)·(1 − z1)`, lo que también explicaría el "valor inicial de µ" de IV-166 (µ aparece en el
denominador solo por un error de transcripción). Y que la IV-153 correcta sea la condición de un ajuste de
mínimos cuadrados común. Ninguna de las dos se puede confirmar sin el autor.

Ya había una duda abierta sobre este método: `Bibliografia/Facundo/Tesis de Maestria/Dudas/Pareto - Minimos
Cuadrados.docx` (fuera del repo). La DECISIÓN 068 corrigió la transcripción de IV-153 contra la tesis; lo que
se agrega acá es que la ecuación de la tesis, bien transcrita, no recupera el parámetro.

---

## 6. Impacto en las 9 estaciones

Momentos es el único método que a veces da un EEA creíble. "EEA actual" es el de Momentos con el cuantil de la
tesis; "puesto actual", el de la distribución en el ranking antes de la DECISIÓN 074 (que usa el mejor de sus
cuatro métodos).

| Estación | Puesto actual | EEA actual | EEA con cuantil coherente | Mejor de las otras 12 | T=100 actual / coherente | T=500 actual / coherente |
|---|---|---|---|---|---|---|
| est_01 | 13 | 279,54 | 17,56 | 25,26 | 2456,8 / 456,2 | 4863,3 / 503,7 |
| **est_02** | **1 ("menor EEA")** | 16,25 | 24,23 | 20,91 | 684,7 / 517,2 (+32 %) | 964,1 / 657,2 (+47 %) |
| est_03 | 10 | 49,75 | 29,40 | 13,59 | 190,5 / 361,1 | 234,2 / 553,2 |
| est_05 | 2 | 7,18 | 8,88 | 6,33 | 223,3 / 208,0 | 305,9 / 277,9 |
| est_06 | 13 | 28,43 | 5,18 | 5,74 | 325,4 / 129,4 | 530,6 / 150,0 |
| est_09 | 12 | 5229,55 | 3,04 | 2,68 | 11451237,5 / 36,3 | 992588509,7 / 36,3 |

En est_04, est_07 y est_08 Momentos es `no_aplicable` (DECISIÓN 060) y Pareto queda última por Mínimos Cuadrados
y MPP, con EEA de 10² a 10⁹.

**Lectura:**

- **est_02** es el caso peligroso: hoy Pareto aparece primera con la etiqueta "menor EEA" y sus eventos de diseño
  salen inflados entre un 32 % y un 47 %. Es lo que justifica mitigar en V1.0 y no solo documentar.
- **est_01 y est_06**, al revés: el cálculo coherente la dejaría como el mejor ajuste (17,56 frente a 25,26;
  5,18 frente a 5,74), y hoy aparece última. Corregirla en la V2 cambia el ranking de esas estaciones.
- **est_09** tiene 7 datos numéricos: en el flujo real, Etapa 1 la rechaza (menos de 10) y Etapa 2 nunca corre.
  Su fila es teórica (Etapa 2 corrida directo sobre `core/`).
- La serie sintética con negativos (`docs/series prueba/serie_con_negativos_otro.csv`) también da EEA absurdos;
  la causa son estas inconsistencias, no los negativos.

---

## 7. Qué se hizo en V1.0 y por qué no se corrigió

**Decisión de Kevin (01/10/2026), registrada como [DECISIÓN 074](../../decisiones/decision074.md):** corregir es
apartarse de la tesis, y la regla del proyecto exige referencia bibliográfica explícita y aval del director para
cada fórmula (`formulas-etapa2.md`, "Regla de uso"). En V1.0 se mitiga en pantalla para que nadie pueda elegir un
resultado que sabemos que está mal:

- Pareto se sigue calculando y mostrando, con su tabla de métodos (trazabilidad docente).
- `core/etapa2/distributions/__init__.py::PENDIENTES_VALIDACION` la marca; `DistResult.pendiente_validacion`
  viaja en el ranking y queda persistido.
- Va al **final del ranking**, después de las sin ajuste. Nunca lleva "menor EEA". El orden relativo de las otras
  12 no cambia y ningún número cambia (verificado contra las 9 estaciones: solo se mueve Pareto, en est_02, est_03
  y est_05).
- Elegirla o explorarla devuelve 400 `DIST_PENDING_VALIDATION` (`distribution-decision` y
  `POST /analysis/{id}/design-events`).
- El frontend la atenúa, sin botones, con la píldora "pendiente de validación". Para análisis guardados antes de la
  DECISIÓN 074 (sin el campo) usa un respaldo local, así un análisis viejo de est_02 tampoco muestra "menor EEA".

---

## 8. Guía para la V2

1. **Confirmar con Facundo** las tres preguntas de
   [`pendientes-facundo.md`](../pendientes/pendientes-facundo.md), sección "Generalizada de Pareto — convenciones
   de signo". Sin su respuesta, corregir los problemas 1 y 2 igual es defendible con Hosking y Wallis (1987) como
   referencia; el problema 3, no.
2. **Conseguir y verificar las referencias** antes de citarlas: Hosking y Wallis (1987) y Coles (2001)
   (ver §10). **Ninguna de las dos está en `Bibliografia/`**, y las páginas de §10 no están verificadas: no se
   citan en `formulas-etapa2.md` hasta tener el texto delante. Pendiente registrado también en
   `docs/pendientes-tecnicos.md`. Después, agregarlas a `formulas-etapa2.md` §10 y reescribir IV-145, IV-146 e
   IV-174 en la convención de los estimadores.
3. **Código** (`backend/metis/core/etapa2/distributions/gen_pareto.py`): cambiar `cuantil()` a
   `µ + (σ/ε)·[1 − (1 − F)^ε]` (un solo lugar; el límite ε → 0 no cambia) y el signo del segundo término del
   numerador de IV-167 en la rama `mpp`. Mínimos Cuadrados, **solo** con la ecuación confirmada por el autor.
4. **Tests nuevos:** recuperación del parámetro en muestras simuladas con semilla fija para cada método
   (tolerancia amplia: es la mediana de 400 muestras); ida y vuelta `F(x(F)) = F` con la función de distribución
   en la misma convención; las 9 estaciones con la expectativa de §6 (solo cambia Pareto).
5. **Cerrar la mitigación:** sacar `gen_pareto` de `PENDIENTES_VALIDACION` (el mecanismo queda para futuros
   casos), sacar el respaldo `PENDIENTES_VALIDACION_V1` del frontend solo si ya no quedan análisis viejos que lo
   necesiten, addendum de cierre en `decision074.md` y nota fechada en este hallazgo.
6. **Revisar el impacto en el ranking:** en est_01 y est_06 Pareto pasaría a ser el mejor ajuste por Momentos.

---

## 9. Cómo reproducirlo

Script: [`scripts/analisis_gen_pareto.py`](scripts/analisis_gen_pareto.py). Desde la raíz del repo, con numpy,
scipy y pandas instalados (dentro del contenedor del backend también funciona):

```bash
python docs/auditoria/hallazgos/scripts/analisis_gen_pareto.py
```

Solo lee `core/` y las series de `docs/`; no modifica nada. Imprime cuatro tablas: **A** (recuperación de
parámetros, la de §4), **B** (raíces de IV-153 frente a un ajuste común, §5), **C** (EEA de Mínimos Cuadrados y
MPP por serie, actual frente a coherente/corregido) y **D** (puesto y EEA de Momentos, eventos de diseño T=100 y
T=500, la de §6). Salida esperada (corrida del 01/10/2026, repetida antes de escribir este documento con
resultados idénticos):

```text
A. Recuperación de parámetros (400 muestras de n=40, mu=50, sigma=30, semilla 1)
 k real | MPP tesis(+) |  MPP (-) |  Momentos |     MC
   -0.2 |         3.98 |    -0.21 |     -0.02 |   0.94
   +0.1 |         4.28 |     0.06 |      0.18 |   0.97
   +0.4 |         4.54 |     0.30 |      0.44 |   0.99

B. IV-153 sobre una muestra con k=0.1 (semilla 2)
  raíces de IV-153: [0.975] | eps de mínimos cuadrados común: 0.18 | k real: 0.1

C. EEA por serie (mejor otra = menor EEA de las 12 distribuciones restantes)
serie        n mejor otra |  MC actual MC coher. | MPP actual MPP corr.+coher. eps corr.
est_01      40     25.255 |   1.89e+03    46.156 |   6.79e+08           24.673     0.072
est_02      24     20.912 |   1.13e+03    61.762 |   6.78e+07           23.976    -0.148
est_03      41     13.594 |        697    56.894 |   2.12e+08           34.289    -0.052
est_04      36      3.618 |        286    10.237 |    1.8e+08            5.843     0.267
est_05      39      6.325 |        562    25.615 |   1.26e+08            7.990    -0.070
est_06      38      5.736 |        430    12.915 |   1.37e+08            5.462     0.070
est_07      19      2.965 |        428     9.542 |    4.5e+08            7.187     0.801
est_08      43      8.838 |   1.79e+03    30.111 |    3.6e+09           12.015     0.477
est_09       7      2.678 |        132     4.281 |   2.76e+10            2.806     2.335
negativos   40      0.093 |       27.1     0.175 |    3.5e+09            0.245     1.604

D. Puesto actual de gen_pareto y Momentos con los dos cuantiles
est_01     puesto 13/13 | Momentos eps=0.363 EEA actual=279.54 coherente=17.56 | T100 2456.8 vs 456.2 | T500 4863.3 vs 503.7
est_02     puesto  1/13 | Momentos eps=0.064 EEA actual=16.25 coherente=24.23 | T100 684.7 vs 517.2 | T500 964.1 vs 657.2
est_03     puesto 10/13 | Momentos eps=-0.137 EEA actual=49.75 coherente=29.40 | T100 190.5 vs 361.1 | T500 234.2 vs 553.2
est_04     puesto 13/13 | Momentos: no_aplicable
est_05     puesto  2/13 | Momentos eps=0.015 EEA actual=7.18 coherente=8.88 | T100 223.3 vs 208.0 | T500 305.9 vs 277.9
est_06     puesto 13/13 | Momentos eps=0.212 EEA actual=28.43 coherente=5.18 | T100 325.4 vs 129.4 | T500 530.6 vs 150.0
est_07     puesto 13/13 | Momentos: no_aplicable
est_08     puesto 13/13 | Momentos: no_aplicable
est_09     puesto 12/13 | Momentos eps=2.773 EEA actual=5229.55 coherente=3.04 | T100 11451237.5 vs 36.3 | T500 992588509.7 vs 36.3
negativos  puesto  8/13 | Momentos: no_aplicable
```

Los "puestos" de la tabla D son los de antes de la DECISIÓN 074: con la mitigación, Pareto queda en el puesto 13
en todas. En una consola de Windows con codificación cp1252 las tildes salen rotas; los números no cambian.

---

## 10. Referencias

- **Tesis de Facundo Ganancias Martínez**, sección IV.3.10, páginas 73 a 76 del PDF, ecuaciones IV-145 a IV-174.
- **Hosking, J. R. M. y Wallis, J. R. (1987).** "Parameter and quantile estimation for the generalized Pareto
  distribution". *Technometrics* 29(3), 339-349. Convención k y estimación por momentos de probabilidad pesada.
  **Pendiente: no está en `Bibliografia/`; páginas exactas sin verificar.**
- **Coles, S. (2001).** *An Introduction to Statistical Modeling of Extreme Values*. Springer. Convención ξ.
  **Pendiente: no está en `Bibliografia/`; capítulo y páginas sin verificar.**

Las dos últimas se citan acá para orientar la búsqueda, no como fuente ya verificada: no se pasan a
`formulas-etapa2.md` hasta tener el texto delante (§8, paso 2).
