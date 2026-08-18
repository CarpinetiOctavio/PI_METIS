## est_09 — La Suela – Río La Suela — Análisis E2E desde cero (15/07/2026)

Detalle completo del análisis Fase 4 (regresión E2E) para esta estación —
la última de las 9. Índice y tabla de consolidación: `fase4-e2e.md`.

**Nota de encuadre — estación distinta a las 8 anteriores.** n=7, por debajo
del piso mínimo de METIS (n≥10, único caso de bloqueo duro documentado en
`CLAUDE.md`: "< 10 datos → error bloqueante. Pipeline se detiene. Único
caso."). El objetivo principal acá no es reproducir los números de Facundo
— es **verificar que el contrato real bloquea correctamente**, y en segundo
lugar, reconstruir de forma aislada (fuera del flujo real, igual que ya se
hizo para est_01 con fines de control académico) los cálculos que la tesis
sí hizo "a los solos efectos del desarrollo de la tesis" (texto literal de
la fuente).

Se rehizo íntegro desde cero, sin usar `regresion-pipeline/est_09...md` ni
`regresion-unitaria/est_09...md` como fuente de ningún resultado de METIS
— solo como fuente de la serie y de los valores de referencia de tesis.
Ninguna afirmación de este documento se apoya en `git log`/`git show`/
historial de commits — todo sale de llamar a las funciones reales de
`metis/core/` y de matemática verificable de forma independiente.

---

### 1. Confirmación del contrato — el hallazgo principal de esta estación

```python
serie = [24.32, 10.99, 33.9, 31.91, 39.55, 22.0, 30.52]  # n=7
r1 = ejecutar_etapa1(serie=serie, tipo_variable="caudal_precipitacion",
                      resolucion_temporal="anual", timestamps=None,
                      cramer_particion="default")
```

Resultado real:
```
r1.contract.bloqueante   = True
r1.contract.codigo_error = 'CONTRACT_SERIES_TOO_SHORT'
r1.descriptive            = None
r1.independencia          = []
r1.homogeneidad           = []
r1.tendencia               = []
r1.atipicos                = []
r1.nivel_confianza         = 'rechazado'
```

**Confirmado: el pipeline real bloquea exactamente como especifica la
arquitectura.** Ninguna prueba estadística se ejecuta — el contrato corta
la ejecución en el primer paso. Por diseño ("el pipeline siempre arranca
por Etapa 1 — nunca se puede ejecutar Etapa 2 directamente"), Etapa 2
tampoco corre en el flujo real para esta estación. Es la primera de las 9
estaciones donde se ejercita este camino del código — todas las demás
tenían n≥19.

Todo lo que sigue (secciones 2 a 5) es **`ejecutar_etapa1()`/`ejecutar_etapa2()`
invocadas fuera de secuencia**, llamando a las funciones de `core/`
directamente sin pasar por el contrato — el mismo mecanismo dual ya usado
para est_01, con el mismo alcance: verificación académica/de fidelidad,
no validación de resultados de diseño hidrológico.

---

### 2. Etapa 1 (aislada) — reconstrucción completa

| Variable | METIS | Tesis | diff% | Nivel |
|---|---|---|---|---|
| n | 7 | 7 | 0.00% | PASS |
| Media | 27.598571 | 27.598 | +0.0021% | PASS |
| Varianza (no sesgada) | 87.934248 | 87.926 | +0.0094% | PASS |
| Desvío | 9.377326 | 9.377 | +0.0035% | PASS |
| M0/M1/M2/M3 | 27.599/16.587/11.806/9.201 | 27.598/16.586/11.805/9.201 | ~0% | PASS |
| Suma ln(xi) | 22.761610 | 22.761 | +0.0027% | PASS |
| Máximo/Mínimo | 39.55/10.99 | 39.5*/11.0* | — | INFO |
| Asimetría no sesgada (g) | -0.973368 | -0.773 | +25.92% | DECISIÓN013, amplificado por n chico |
| CV | 0.339776 | 0.34 | -0.07% | PASS |

\* Máximo/mínimo de tesis (39.5/11.0) no coinciden con la serie transcripta
(39.55/10.99) — ya señalado como probable redondeo de display en la propia
ficha original, no discrepancia de datos base: media y suma_log coinciden
a <0.01% usando los valores reales de la serie (39.55/10.99), lo que
confirma que esos son los datos correctos.

**Sin discrepancia de datos base.** g/k con la mayor magnitud de
divergencia de las 9 estaciones (n=7 amplifica el factor `n²/((n-1)(n-2))`
de IV-5 al máximo posible: 49/30≈1.63) — mismo mecanismo DECISIÓN013 ya
documentado, sin hallazgo nuevo.

**Helmert** — reconstruido secuencia por secuencia: S=3, C=3, S-C=0 —
**coincide exacto con la tesis**. Aprobada en ambos (0 dentro de ±√6=±2.449).

**t-Student** — METIS (partición floor, n1=3/n2=4) da t=-0.94404. Con
partición ceil (n1=4/n2=3, la convención de tesis ya documentada en
est_03/05/07/08) se obtiene t=-0.61548 — **coincide casi exacto con el
-0.62 de tesis**. Mismo patrón de convención de partición para n impar,
no es hallazgo nuevo.

**Hallazgo — segunda confirmación del valor crítico de una cola (después
de est_08).** METIS calcula el crítico de t-Student/Cramer con
`t.ppf(0.975, df=5) = 2.570582` (dos colas, Ec. III-8). La tesis imprime
**2.015** para ambas pruebas en esta estación — verificado
independientemente: `t.ppf(0.95, df=5) = 2.015048`, exactamente el crítico
de **una cola**. Ya no es un caso aislado de est_08 — es la **segunda de 9
estaciones** con esta misma desviación de convención. No cambia ningún
veredicto (los `t_w`/`t` de ambas pruebas quedan del mismo lado de los dos
valores críticos posibles en esta estación). Actualizar
`pendientes-facundo.md` con este segundo punto de datos.

**Cramer** — reconstruido con `_cramer_bloque()` real. `n×0.3=2.1` →
`ceil=3`, `round=floor=2` — **sí discrimina** (a diferencia de lo que
decía una redacción previa de este párrafo). Con n_w2=2: τ_w2=-0.14275,
t_w2=0.20270 — **coincide exacto con la tesis** (τ_w2=-0.14274,
t_w2=0.20275); con n_w2=3 (ceil) el τ_w2 no coincide (0.32967, muy lejos).
Confirma la regla ya establecida en DECISIÓN011 para n_w2 (`round`), sin
excepción — no es un caso nuevo de ambigüedad, es una reconfirmación más.

**Hallazgo — cuarta estación que discrimina n_w1, y segunda que contradice
`ceil` (después de est_07).** `n×0.6=4.2` → `ceil=5`, `round=floor=4` —
sí discrimina. Con n_w1=5 (lo que usa el pipeline por default): τ_w1=0.42415,
no coincide con tesis (0.36219). Con **n_w1=4** (round/floor): τ_w1=0.36220,
t_w1=1.02955 — **coincide exacto con la tesis** (τ_w1=0.36219, t_w1=1.02953).
Con esto, el censo de DECISIÓN011 para n_w1 queda **empatado 2 a 2** entre
las estaciones que discriminan: est_02 y est_05 confirman `ceil`; est_07 y
est_09 (ahora) contradicen con `round`/`floor`. Ya no es "regla mayoritaria
con una excepción" — es un empate real. No cambia el veredicto de Cramer en
esta estación (con cualquiera de las dos particiones, `t_w1` queda muy por
debajo de cualquiera de los dos valores críticos posibles).

**Anderson** — reconstruido lag por lag (k_max=ceil(7/3)=3): los 3 lags
dentro de banda, **0 lags fuera, coincide exacto** con "0 puntos fuera" de
la tesis (umbral de tesis "0.3" ≈ redondeado a 0; umbral de METIS
`ceil(3×0.10)=1` — ambos aprueban con 0 lags fuera, sin diferencia
práctica).

**Wald-Wolfowitz** — reconstruido a mano (excluyendo empates con la media,
DECISIÓN017): n1=4, n2=3, R=4 — **coincide exacto con la tesis** (n1=4,
n2=3, R=4). Z=-0.363803 vs tesis Z=-0.364 (diff 0.05%, prácticamente
exacto). `TEST_WARNING_SMALL_SAMPLE` emitido (n≤40) — correcto.

**Veredicto de Etapa 1 (aislado):** homogeneidad y independencia aprueban
en ambos. La tesis narra la aprobación "con salvedad académica por tamaño
muestral" — **primera estación de las 9 donde el propio texto de la fuente
reconoce explícitamente la limitación de n como condición de la
aprobación**, coherente con que METIS bloquea por completo el mismo caso
en su flujo real.

**Tendencia y atípicos (aislado, sin referencia de tesis para estas 3):**
Mann-Kendall → `no_ejecutada` (`TEST_NOT_EXECUTED_MIN_SAMPLES`, n=7<10 —
primera estación de las 9 donde se ejercita esta rama del código en la
práctica, tal como documenta `formulas-etapa1.md`). KS aprueba (Z=0.5455 <
1.358). **Chow rechaza** (estadístico=2.0074 > K_N=1.9381) — detecta como
atípico el valor 10.99 (el mínimo de la serie, índice 1). Es la primera de
las 9 estaciones donde Chow aislado detecta un atípico real. No forma
parte de la tesis (agregado por Carlos), sin comparación posible.

---

### 3. Etapa 2 (aislada) — cableado completo (35/35)

**13/13 distribuciones, 35/35 combinaciones distribución×método
verificadas mediante llamada aislada a `ajustar()`+`cuantil()`+
`calcular_eea()`, comparada contra `ejecutar_etapa2()` — 0 hallazgos de
cableado.** Sin ceros en la serie (mínimo=10.99), `STATUS_DISABLED_ZEROS`
sigue sin ejercitarse en ninguna de las 9 estaciones auditadas.

`lognormal3p/momentos` da `no_aplicable` — **coincide exacto con la tesis**
("NO_APLICABLE"), primera vez que este status específico coincide sin
ambigüedad entre METIS y tesis en las 9 estaciones. `logpearson3/momentos_directo`
da `no_aplicable` (B=2.6022 ∉ (3,6], guard IV-249 aplicado correctamente
— mismo desacuerdo real ya documentado en est_03/07/08, tesis reporta
valores igual). `gve/mv` y `gen_pareto/mv` dan `no_converge`, coincidiendo
con la tesis en ambos casos.

---

### 4. Etapa 2 — parámetros y EEA, comparación completa contra tesis

| Distribución | Método | Param. | METIS | Tesis | diff% |
|---|---|---|---|---|---|
| Uniforme | Momentos | α,β,EEA | 11.3566/43.8406/2.7761 | 11.36/43.83/2.7768 | **~0% — modelo seleccionado, PASS total** |
| Uniforme | MV | α,β,EEA | 10.99/39.55/4.1603 | 10.99/39.55/4.1627 | ~0% |
| Exponencial β | Mom/MV | β,EEA | 0.036234/12.0435 | 0.036/12.0441 | ~0% |
| Exponencial x0β | Momentos | x0,β,EEA | 18.2212/9.3773/5.2975 | 18.22/9.38/5.2981 | ~0% |
| Exponencial x0β | MV | x0,β,EEA | 8.2219/19.3767/7.7270 | 8.22/19.38/7.7298 | ~0% |
| Gen. Exponencial | Momentos | α,λ | 22.7850/0.134974 | 5.23/0.0511 | +335.7%/+164.1% (ver Hallazgo A) |
| Gen. Exponencial | MV | α,λ,EEA | 9.9341/0.103672/3.5637 | 9.93/0.1037/3.5647 | ~0% |
| Gen. Exponencial | ML | α,λ | 0.5805/-0.016957 | 0.71/-0.0198 | -18.2%/+14.4% (pendiente IV-84, patrón conocido) |
| Normal | Mom/MV | µ,σ,EEA | 27.5986/9.3773/3.0378 | 27.6/9.3769/3.1667 | ~0%/-4.07% (Causa C, mild) |
| Normal | ML | σ,EEA | 9.8785/2.7934 | 9.877/2.9141 | ~0%/-4.14% (Causa C, mild) |
| Log-Normal 2p | Mom/MV | µy,σy,EEA | 3.2517/0.4258/3.6828 | 3.25/0.426/3.6601 | **~0%/+0.62% — verificado independientemente (denom n-2), sin Causa C apreciable, caso atípico real — ver Hallazgo G** |
| Log-Normal 3p | Momentos | — | NO_APLICABLE | NO_APLICABLE | **coincide exacto** |
| Log-Normal 3p | MV | x0,µy,σy,EEA | -176.557/5.3180/0.04314/3.8382 | NO_CONVERGE | ver Hallazgo B — verificación parcial, pendiente de confirmar con Code |
| Gamma 2p | Momentos | α,β,EEA | 3.1862/8.6619/3.6081 | 3.19/8.662/3.7052 | ~0%/-2.62% (Causa C, mild) |
| Gamma 2p | MV | α,β,EEA | 3.5718/7.7268/3.4466 | 3.57/7.726/3.5299 | ~0%/-2.36% (Causa C, mild) |
| Gamma 2p | ML | α,β,EEA | 3.6567/7.5474/3.4199 | 3.66/7.548/3.5 | ~0%/-2.29% (Causa C, mild) |
| Gamma 3p | Momentos | x0,α,β,EEA | 8.3308/4.5638/4.2219/4.3983 | 3.446/3.626/6.689/4.2505 | Causa A (g-propagación, parámetros verificados exacto con la fórmula α=escala=√(var/β), β=forma=4/g²) / +3.48% |
| Gamma 3p | MV | x0,α,β | 10.7608/15.3488/1.0970 | 10.758/15.351/1.097 | **~0% los 3** |
| Gamma 3p | MV | EEA | 6.4821 | 6.3409 | +2.23% (Causa C, la más leve del proyecto) |
| Gamma 3p | MPP | — | EXCLUIDO (no implementado) | x0=37.579,α=-5.008,β=1.993,EEA=17.4168 | pendiente de código ya conocido — nota: α negativo en tesis, ya señalado como atípico en la ficha original |
| Gumbel | los 4 métodos | α,µ,EEA | ver tabla — **PASS total, ≤0.01% en los 4** | igual | 0% — 9ª estación consecutiva |
| GVE | Momentos | ν,α,β,EEA | 26.1507/10.1935/0.674959/3.2124 | NO_CONVERGE | METIS converge donde tesis no — 2ª vez que Momentos converge limpio (después de est_01) |
| GVE | MV | — | NO_CONVERGE | NO_CONVERGE | **coincide** |
| GVE | ML | β | 0.665242 | 0.666 | ~0.11% (casi exacto) |
| GVE | ML | α,ν,EEA | 11.1234/25.9685/2.6775 | 10.389/26.396/3.0643 | +7.07%/-1.62%/-12.62% — mismo patrón GVE-ML, 9ª estación consecutiva, **magnitud más leve del proyecto — ver Hallazgo G** |
| LP3 | Directo | — | NO_APLICABLE (B=2.602 ∉ (3,6]) | α=0.333,β=0.075,y0=3.287,EEA=9.9861 | METIS aplica correctamente la restricción IV-249 — 4ª estación con este desacuerdo real |
| LP3 | Indirecto | α,β,y0 | 0.4195/1.0298/2.8196 | 0.333/1.633/2.707 | +26.0%/-36.9%/+4.2% — ver Hallazgo C |
| LP3 | Indirecto | EEA | 6.6836 | 6.1286 | +9.06% |
| LP3 | MV | — | NO_CONVERGE | α=0.775,β=1.123,y0=2.382 (tabla params) / NO_CONVERGE (tabla EEA) | inconsistencia interna de la propia tesis — ver Hallazgo D |
| Gen. Pareto | Momentos | µ,σ,ε,EEA | 3.6083/90.5042/2.7725/5229.55 | NO_CONVERGE | METIS converge (degenerado) — patrón conocido |
| Gen. Pareto | MV | — | NO_CONVERGE | NO_CONVERGE | coincide |
| Gen. Pareto | MC | µ,σ,ε,EEA | 10.9641/60.3964/1.8816/800.24 | NO_CONVERGE | METIS converge (pobre) donde tesis no — patrón conocido |
| Gen. Pareto | MPP | µ,σ,ε,EEA | -34.24/759.98/9.80/2.76e10 | NO_CONVERGE | degenerado extremo — patrón conocido, mismo problema de plausibilidad de ε que en las 8 estaciones anteriores |

**Nota posterior — DECISIÓN 060 (17/08/2026).** El guard de dominio
bloquea el resultado de Exponencial x0-β Momentos de esta tabla
(fila anterior, no visible en este extracto): x0=18.2212 >
min(serie)=10.99 viola IV-68/69 — METIS hoy devuelve `NO_APLICABLE`.
Cambia el mejor método de la distribución: antes, Momentos (EEA=5.2975)
era mejor que MV (EEA=7.7270) y ocupaba el puesto 9/13; ahora pasa a MV,
puesto 10/13.

Gen. Pareto de esta estación (tabla de arriba) no está afectado por este
guard — µ=3.61 < min(serie)=10.99, no viola el soporte. Sin cambios en
esa distribución.

DECISIÓN 061 no aplica — sin ceros reales. Detalle completo en
`docs/decisiones/decision060.md`.

---

### 5. Hallazgos relevantes — con causa e implicancia

**A. Generalizada Exponencial Momentos — la mayor divergencia de CV de
todo el proyecto, novena estación con el mismo patrón.** CV_datos=0.33978.
Con α=22.785 (METIS) el CV teórico (digamma/trigamma, IV-77) coincide
exacto (0.33978, verificado). Con α=5.23 (tesis) el CV teórico da 0.52181
— diff **+53.6%** respecto del CV real, la mayor divergencia de este
chequeo en las 9 estaciones (récord previo: est_08 con +26.1%). METIS es
el matemáticamente consistente con sus propios datos — mismo patrón,
magnitud extrema esperable dado que n=7 es la muestra más chica del
dataset.

**B. Log-Normal 3p MV — diagnóstico corregido tras verificación cruzada
Octavio↔Code. La explicación original de Code (mínimo genuino cerca de
`lo`) quedó refutada por evidencia directa, no solo pendiente de
confirmar.** METIS converge a `x0=-176.5565`, un valor físicamente
implausible (muy por debajo del mínimo de la serie, 10.99) donde la tesis
reporta `NO_CONVERGE`.

**Verificado por Octavio de forma independiente, con la función real
(no una reconstrucción):** evaluando `f(x0)` para `x0` acercándose a
`xi_min=10.99` desde abajo (`x0=xi_min-1e-3, 1e-5, 1e-7, ...`), la función
**no** se vuelve errática cerca de `hi` como describía la versión anterior
de este hallazgo — **diverge de forma monótona y sin límite hacia -∞**
según `x0→xi_min`: `f=19.25` en `xi_min-1e-3`, cayendo a `f=4.64` en
`xi_min-1e-13`, hasta que la precisión de punto flotante rompe el guard
`diff<=0` alrededor de `xi_min-1e-17`. Es la degeneración clásica de
verosimilitud no acotada de la log-normal de 3 parámetros (ya advertida en
DECISIÓN020) — pero ocurre en el borde **opuesto** al que se había
identificado.

**Confirmado por Code, instrumentando la llamada real a `ajustar()`**
(interceptando `minimize_scalar` dentro del propio módulo, sin
reimplementar la función objetivo — se envuelve la closure real que el
código construye internamente): con el dominio completo tal como está
codeado hoy (`lo` a `hi`, ancho≈187.5), Brent evalúa 37 puntos, todos
entre `x0=-176.557` y `x0=-60.646` — **ninguno a menos de 71 unidades de
`hi`**. En ese rango la función varía apenas de `f=15.222934068` a
`f=15.366017988` — prácticamente plana. Brent converge ahí porque su
tolerancia (`xatol=1e-7`) se satisface en una región casi constante, sin
haber explorado nunca la zona donde la función realmente se derrumba.
Confirmado también que acotar `minimize_scalar` artificialmente cerca de
`hi` (`bounds=(xi_min-1, xi_min-1e-15)` y más ajustado aún) **tampoco**
hace que Brent encuentre el verdadero comportamiento — se conforma con un
punto intermedio en cada caso, sin llegar al valor mucho más bajo
disponible cerca del propio límite superior del rango dado.

**Conclusión, ahora sí verificada por ambas partes con la función real:**
no es que `lo` sea un óptimo genuino aceptado por error (como decía la
versión anterior de este hallazgo) — **la función no tiene mínimo finito
en absoluto** en este dominio. La región cerca de `lo` tampoco es un
"borde falso" en el sentido de DECISIÓN019 (donde existe un óptimo
genuino cerca de un borde específico) — es simplemente donde Brent se
detiene por su criterio de tolerancia en una zona casi plana, sin haber
visto jamás la parte del dominio donde vive la verdadera degeneración.
Es un modo de falla distinto al de `logpearson3.py::mv` (DECISIÓN019) y al
de `gamma3p.py::mv` (DECISIÓN023) — no alcanza con calcar ninguno de esos
dos guards.

**Función y dominio exactos, del archivo `lognormal3p.py` tal como está
hoy (líneas 119-141, método `mv`):**

```python
S = np.std(serie, ddof=1)
xi_min = np.min(serie)

def _neg_profile_ll(x0):
    diff = serie - x0
    if any(diff <= 0.0): return inf
    zi = ln(diff)                          # zi = ln(xi - x0)
    mu_y = mean(zi)                        # IV-117
    sigma2 = mean((zi - mu_y)**2)          # IV-118, ddof=0 (poblacional)
    if sigma2 <= 0.0: return inf
    return (n/2)·ln(sigma2) + Σ ln(diff)   # perfil, ∝ -log-verosimilitud

lo = xi_min - 20·S
hi = xi_min - 1e-9
```

Para est_09: `lo = -176.55652502144378`, `hi = 10.989999999`.

**RESUELTO — 15 de Julio de 2026 (DECISIÓN 025, decisions-log.md).**
Con la causa raíz confirmada por verificación cruzada (arriba), se
prototipó un guard de "ausencia de óptimo finito" (mismo mecanismo de
escaneo grueso de DECISIÓN023, criterio distinto: verifica que el mínimo
del escaneo no caiga exactamente en el primer o último punto finito —
evidencia de que la función gira genuinamente en algún punto interior, no
que decrece sin límite hasta un borde). Octavio verificó el prototipo por
su cuenta contra las 9 series reales antes de aprobarlo, incluida
inspección manual de los casos con argmin cercano al borde (est_01,
est_07) para descartar que fuera un artefacto de índice. Un primer diseño
con margen porcentual fijo (2% de los puntos del escaneo) se descartó por
dar falsos positivos en 6 de las 8 estaciones buenas — detalle completo
del diseño descartado en DECISIÓN025.

**Aplicado a `metis/core/etapa2/distributions/lognormal3p.py`.**
Verificación post-aplicación, llamando a `ajustar()` real (no el
prototipo aislado) para las 9 estaciones:

| Estación | status | x0/µy/σy | vs. valor pre-fix |
|---|---|---|---|
| est_01 a est_08 | `ok` | idénticos a los ya reportados en cada `est_0X-e2e.md` | **sin cambio — 0 regresiones** |
| est_09 | **`no_converge`** | — | antes: `ok` con x0=-176.56 (implausible); ahora **coincide con NO_CONVERGE de la tesis** |

`pytest tests/` → 109 passed, 1 failed (mismo failing preexistente de
`gen_pareto/mc`, sin relación — mismo conteo que antes del fix). `ruff
check` → limpio. Ranking de Etapa 2 para est_09 recalculado con el fix:
`lognormal3p` queda sin EEA (ambos métodos, momentos y mv, sin resultado
válido) — no afecta la selección de modelo de esta estación (Uniforme
Momentos, ya PASS exacto, sección 6) ni el top del ranking (GVE ML sigue
#1 en el ranking propio de METIS, sin cambios).

**Clasificación final: Pendiente de código — RESUELTO.** Causa raíz
confirmada por verificación cruzada independiente (Octavio + Code, cada
uno con evidencia propia); fix prototipado, verificado sin regresión
contra las 8 estaciones donde el método converge, aprobado por Octavio, y
aplicado. Detalle completo del guard, las opciones evaluadas y el diseño
descartado en decisions-log.md, DECISIÓN 025.

**C. LP3 Indirecto — divergencia de parámetros mayor que la propagación de
g habitual, sin explicación cerrada.** α diverge +26.0%, β -36.9% — mayor
magnitud que el patrón típico de Causa A visto en otras estaciones para
este método (habitualmente 5-15%). Se probó la hipótesis ya usada en
est_02 (que el "alfa" de tesis fuera en realidad `gy`, no el parámetro
real) — **descartada explícitamente para est_09**: `gy` de esta serie es
`-1.97087`, nada cerca del `0.333` que reporta la tesis (diff -116.9%). La
hipótesis no generaliza; el "0.333" de tesis en LP3 Indirecto queda sin
explicación en dos estaciones con valores completamente distintos entre sí
(0.333 en est_02 y est_09), lo que sugiere que podría no ser una relación
sistemática sino coincidencia o error de transcripción puntual en cada
caso. Sin resolver — queda como Pendiente de dominio.

**D. LP3 MV — la propia tesis se contradice entre su tabla de parámetros y
su tabla de EEA, mismo patrón ya visto en otras estaciones (GVE MV en
est_08, Gumbel MV/ME en est_01).** La tabla de "Parámetros" de la ficha
original reporta valores reales para LP3 MV (α=0.775, β=1.123, y0=2.382).
La tabla de "EEA" de la misma ficha marca este mismo método como
`NO_CONVERGE`. METIS da `no_converge` — coincide con la tabla de EEA, no
con la de parámetros. No es un hallazgo contra METIS — es la propia fuente
contradiciéndose internamente, ya un patrón reconocido en el proyecto (3ª
vez).

**E. Gumbel — PASS perfecto en los 4 métodos, novena estación
consecutiva, sin una sola excepción en todo el dataset auditado.**

**F. GVE Momentos-L — mismo patrón, novena estación consecutiva.** Ver
Hallazgo G para el detalle de magnitud y su relación con el tamaño de
muestra.

**G. La divergencia de Causa C no crece de forma uniforme al bajar n —
en algunos casos se atenúa, en otros se amplifica, y hay que documentar
las dos direcciones por separado.** Esta estación (n=7, la muestra más
chica del proyecto) permite ver ambos comportamientos en un mismo dataset:

- **Divergencias que se amplifican con n chico** (mecanismo: factores de
  corrección de ddof tipo `n²/((n-1)(n-2))`, que crecen cuando n baja):
  - g (DECISIÓN013): +25.92%, el máximo de las 9 estaciones (orden
    ascendente por n: est_08 n=43 → +3.57%; est_07 n=19 → +8.42%; est_09
    n=7 → +25.92%).
  - Gen. Exponencial Momentos (CV, Hallazgo A): +53.6%, también el máximo
    (est_08 → +26.1%; est_07 → +23.2%; est_09 → +53.6%).

- **Divergencias que se atenúan con n chico** (mecanismo no identificado
  con la misma claridad — no depende de un factor de ddof simple):
  - GVE Momentos-L: α diverge solo +7.07% y ν solo -1.62% en est_09 — la
    brecha más chica de las 9 estaciones (el resto ronda 10% a 60%). β
    sigue casi exacto en las 9 (0.11% acá).
  - Log-Normal 2p (Hallazgo, sección 4): Causa C prácticamente ausente
    (+0.62%, verificado independientemente) — único caso en las 9
    estaciones donde esta familia de distribuciones no muestra el
    patrón sistémico de EEA divergente pese a parámetros casi idénticos.
  - Testigo de cuantiles (Normal Momentos-L, sección 6): degradación con
    T mucho más contenida que el resto del proyecto (+6.00% en T=100,
    contra +18% a +54% en las demás estaciones con Causa C confirmada).

**Implicancia para la consolidación final:** el tamaño de muestra no tiene
un efecto único y predecible sobre la magnitud de las discrepancias —
depende del mecanismo subyacente de cada una. Las divergencias ligadas a
convenciones de ddof (DECISIÓN013 y su familia) se comportan de forma
matemáticamente predecible y creciente al bajar n. Las divergencias de
Causa C (EEA/cuantil que no se explica por parámetros) no siguen ese mismo
patrón — en esta estación se atenúan, lo que sugiere que la causa raíz de
Causa C no es simplemente un problema de tamaño de muestra, sino algo más
específico de cada distribución/método que amerita seguir la línea de
investigación abierta en est_08 (Hallazgo A) antes de sacar conclusiones
generales en la consolidación.

---

### 6. Selección de modelo y cuantiles

**Modelo ganador de Facundo — Uniforme (Momentos), EEA tesis=2.7768, EEA
METIS=2.7761 (~0%, PASS exacto).** Cuantiles:

| T | q_METIS | q_tesis | diff% |
|---|---|---|---|
| 2 | 27.5986 | 27.60 | -0.005% |
| 5 | 37.3438 | 37.34 | +0.010% |
| 10 | 40.5922 | 40.59 | +0.005% |
| 20 | 42.2164 | 42.21 | +0.015% |
| 25 | 42.5412 | 42.54 | +0.003% |
| 50 | 43.1909 | 43.19 | +0.002% |
| 100 | 43.5157 | 43.51 | +0.013% |

**PASS 7/7, diff ≤0.015% en todos los casos — la reproducción más ajustada
de todo el proyecto**, incluso mejor que Gumbel ML en otras estaciones.

**Testigo — Normal Momentos-L, EEA tesis=2.9141, EEA METIS=2.7934
(-4.14%, Causa C leve).** Cuantiles: PASS en T=2 (-0.005%), degrada
progresivamente pero de forma mucho más contenida que el patrón típico de
Causa C del resto del proyecto: +0.37% en T=5, hasta **+6.00% en T=100** —
la degradación más leve entre todos los testigos de Causa C documentados
(el resto del proyecto va de +18% a +54% en T=100) — ver Hallazgo G para
la discusión de por qué esta estación atenúa el efecto en vez de
amplificarlo.

---

### 7. Clasificación final est_09

| Columna | Resultado |
|---|---|
| **Contrato/Etapa 1 (flujo real)** | **Aprobado — confirmación exitosa del único caso de bloqueo duro de todo METIS.** `ejecutar_etapa1()` bloquea correctamente para n=7<10, sin ejecutar ninguna prueba. |
| **Etapa 1 (aislada, académica)** | **Aprobado** — sin discrepancias de datos base, Helmert/Anderson/Wald-Wolfowitz exactos. 2 hallazgos de convención ya conocidos (partición t-Student, valor crítico una/dos colas — 2ª confirmación) y 1 hallazgo nuevo (n_w1 de Cramer, empata el censo 2-2). |
| **Cableado (13 dist., 35 combinaciones)** | **Aprobado** — 35/35, reconstrucción propia completa, 0 hallazgos de wiring. |
| **Selección de modelo (académica)** | **Aprobado** — el modelo elegido por Facundo (Uniforme Momentos) es fiel, PASS exacto en parámetros, EEA y los 7 cuantiles. |
| **Cuantiles** | **Aprobado** para el modelo seleccionado (PASS 7/7, diff ≤0.015% — el mejor resultado del proyecto). |

**Clasificación general de la estación: Parcial.** El bloqueo real del
contrato — el objetivo principal de esta estación — es un **Aprobado
limpio**. La reconstrucción académica de Etapa 1 y 2 es la más limpia de
las 9 en varios aspectos (Log-Normal 2p sin Causa C apreciable, testigo con
la menor degradación de cuantiles, modelo seleccionado con el mejor PASS
del proyecto), y aporta además un hallazgo metodológico transversal
(Hallazgo G — la relación entre tamaño de muestra y magnitud de
discrepancia no es uniforme, depende del mecanismo). Tiene un **hallazgo
de Pendiente de código con verificación incompleta** (Hallazgo B — posible
guard de borde faltante en `lognormal3p.py::mv`, requiere confirmación
matemática independiente con la función real antes de proponer cualquier
fix) y confirma/actualiza 2 hallazgos transversales ya en seguimiento
(valor crítico una cola — segunda confirmación; n_w1 de Cramer — empate
2-2, ya no mayoría). **Ningún hallazgo de esta ronda requiere modificar
código de `metis/core/` — el Hallazgo B está en fase de verificación, no
de propuesta de fix.**

---

**Con est_09, las 9 estaciones del dataset quedan analizadas con el
estándar completo de Fase 4.** Pendiente: (1) pedirle a Code la función
exacta de `lognormal3p.py::mv` para cerrar el Hallazgo B; (2) consolidar
el informe final integral (ver sección "Próximo paso" de `fase4-e2e.md`).

---

## ADDENDUM (15/07/2026) — Cierre del Hallazgo B, diagnóstico corregido y verificado

### Corrección — Hallazgo B (Log-Normal 3p MV)

El diagnóstico original de este hallazgo (sección 4/5: "converge a un x0 físicamente
implausible, pegado al borde inferior del dominio, con la función objetivo monótona y sin
óptimo interior") **quedó refutado por verificación independiente, no confirmado como se
había dejado planteado.** Se reemplaza por el diagnóstico corregido abajo — el texto
original permanece más arriba en este documento, sin editar, como registro de cómo
evolucionó el hallazgo.

**Diagnóstico corregido y verificado de forma independiente (función real, no narrativa):**

La función objetivo (`_neg_profile_ll`, perfil de verosimilitud negativa sobre x0) **no
tiene mínimo finito en el dominio de búsqueda.** Sube de forma suave desde `lo` (f=15.22)
hasta un máximo cerca de x0≈10.9 (f≈19.7), y a partir de ahí **diverge a -∞** a medida que
x0 se acerca al mínimo muestral (`xi_min=10.99`, el borde `hi` del dominio):

```
x0 = xi_min - 1e-03  ->  f = 19.2463
x0 = xi_min - 1e-09  ->  f = 11.5560
x0 = xi_min - 1e-13  ->  f = 4.6427
x0 = xi_min - 1e-15  ->  f = 1.4259
x0 = xi_min - 1e-16  ->  f = inf   (diff=0 exacto por redondeo de punto flotante)
```

Verificado independientemente por partida doble (Chat y Code, cada uno con su propia
instrumentación, sin depender uno del otro):

1. **Divergencia hasta el límite de precisión numérica** — reproducida exacta, valor por
   valor, hasta que el redondeo de punto flotante hace `diff=0` y el guard existente
   (`if diff<=0: return inf`) dispara.
2. **Instrumentación directa de `minimize_scalar`** (envolviendo la función real para
   contar y registrar cada punto evaluado, sin reimplementar nada): con el dominio completo
   (`lo`, `hi`) de hoy, Brent evalúa 37 puntos, ninguno a menos de ~71 unidades de `hi`.
   Nunca explora la región donde la función se derrumba.
3. **Bounds angostados a mano cerca de `hi`** (`bounds=(xi_min-1, xi_min-1e-12)`): Brent
   converge a un punto intermedio (x0≈9.99), a 0.38 unidades del borde angosto — ni
   siquiera forzando la búsqueda cerca de la divergencia el optimizador se acerca lo
   suficiente para encontrarla.

**Conclusión — modo de falla distinto a los dos ya catalogados en el proyecto.** No es
convergencia falsa *en* un borde por ausencia de guard (el caso ya resuelto de
`logpearson3.py::mv`, DECISIÓN019, donde el óptimo genuino existe cerca de un borde y solo
falta rechazarlo). Acá **no existe un óptimo finito en absoluto** — la verosimilitud
perfilada es genuinamente no acotada (degeneración clásica de modelos de 3 parámetros
cuando el parámetro de posición se acerca al mínimo muestral). `x0=-176.5565` no es un
óptimo real ni siquiera espurio de borde: es el punto donde Brent deja de encontrar cambios
significativos de la función (zona casi plana entre `lo` y x0≈4) y se detiene por
tolerancia de convergencia (`xatol`), sin haber visto nunca la región — angosta en términos
absolutos, aunque muy alejada en la búsqueda inicial — donde la función realmente colapsa.

Un guard de proximidad a borde (análogo a DECISIÓN019) **no resolvería este caso**: `x0`
está cerca de `lo` en términos absolutos, así que ese guard dispararía y marcaría
`NO_CONVERGE` — probablemente el resultado correcto en la práctica — pero por el motivo
equivocado (creería que rechaza una convergencia de borde genuina, cuando en realidad
rechaza la ausencia total de óptimo). Cualquier solución real necesitaría detectar la
ausencia de mínimo finito en sí (por ejemplo, verificar que la función no sigue
decreciendo sin estabilizarse hacia ningún extremo del dominio), no solo la proximidad
numérica a un borde.

**Clasificación final: Pendiente de código — diagnóstico cerrado y verificado
independientemente por dos vías. Sin fix propuesto** — la naturaleza del problema (ausencia
de óptimo finito, no falsa convergencia de borde) requiere una solución de otro tipo a la ya
usada en `logpearson3.py`, y proponerla es un paso posterior que necesita aprobación
explícita de Octavio antes de tocar `lognormal3p.py`.

### Corrección — sección 7, fila "Etapa 2 / Selección de modelo académica"

La fila de Log-Normal 3p MV en la clasificación general pasa de "hallazgo en verificación"
a **"Pendiente de código — diagnóstico cerrado, sin fix"**. No afecta la clasificación de
"Selección de modelo" (sección 7 original), ya que Log-Normal 3p MV no es el modelo
seleccionado por Facundo ni compite por el primer puesto del ranking académico de esta
estación (Uniforme Momentos, PASS total, sigue siendo el ganador sin objeciones).

---

## Cierre de est_09

Con este addendum, **est_09 queda cerrada.** Resumen de estado final:

| Columna | Resultado |
|---|---|
| Contrato/Etapa 1 (flujo real) | Aprobado — bloqueo confirmado |
| Etapa 1 (aislada) | Aprobado — 2 hallazgos de convención reconfirmados (valor crítico una cola, 2ª vez; n_w1 de Cramer, empate 2-2) |
| Cableado | Aprobado — 35/35, 0 hallazgos de wiring |
| Selección de modelo | Aprobado — Uniforme Momentos, PASS total |
| Cuantiles | Aprobado — PASS 7/7, mejor resultado del proyecto |
| Hallazgo adicional | Pendiente de código — diagnóstico cerrado y verificado (Log-Normal 3p MV, ausencia de óptimo finito), sin fix propuesto, requiere aprobación de Octavio para el siguiente paso |

**Con est_09, las 9 estaciones del dataset quedan analizadas y cerradas con el estándar
completo de Fase 4.** Punto de partida para la consolidación final: `fase4-e2e.md`.

---

## ACTUALIZACIÓN FINAL (15/07/2026) — Fix aplicado (DECISIÓN 025), fila "Hallazgo adicional" de la tabla de arriba queda superada

Octavio aprobó el prototipo del guard descripto en el ADDENDUM (con
verificación propia contra las 9 series, incluida inspección manual de
los casos con argmin cercano al borde en est_01/est_07 para descartar
artefacto de índice). Aplicado a
`metis/core/etapa2/distributions/lognormal3p.py`. Detalle completo del
guard, las opciones evaluadas y el diseño descartado (margen porcentual
fijo, que daba falsos positivos en 6 de las 8 estaciones buenas) en
`decisions-log.md`, DECISIÓN 025.

**Verificación post-aplicación, llamando a `ajustar()` real para las 9
estaciones (no el prototipo aislado):**

| Estación | status | x0/µy/σy | vs. valor pre-fix |
|---|---|---|---|
| est_01 a est_08 | `ok` | idénticos a los ya reportados en cada `est_0X-e2e.md` | sin cambio — 0 regresiones |
| est_09 | `no_converge` | — | antes: `ok` con x0=-176.56 (implausible); ahora coincide con NO_CONVERGE de la tesis |

`pytest tests/` → 109 passed, 1 failed (mismo failing preexistente de
`gen_pareto/mc`, sin relación, mismo conteo que antes del fix). `ruff
check` → limpio. No afecta la selección de modelo de esta estación
(Uniforme Momentos, ya PASS exacto) ni el top del ranking de METIS para
est_09.

**La fila "Hallazgo adicional" de la tabla de cierre, arriba, queda
superada por esta actualización — no se edita esa fila, queda como
registro de dónde estaba el hallazgo antes del fix.** Estado real y
final: **Pendiente de código — RESUELTO.** Sin nada abierto en est_09.