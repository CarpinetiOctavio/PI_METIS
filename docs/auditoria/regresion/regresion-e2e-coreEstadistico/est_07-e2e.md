## est_07 — Tincunaco – Río Chocancharagua — Análisis E2E desde cero (14/07/2026)

Detalle completo del análisis Fase 4 (regresión E2E) para esta estación.
Índice y tabla de consolidación de las 9 estaciones: `fase4-e2e.md`.

**Nota de encuadre:** primera de las 3 estaciones "desde cero" (nunca
tuvo ninguna ronda de Fase 2/4 previa — solo Fase 1/3 vía pipeline y
unitaria.md). La tabla de parámetros de Etapa 2 de la tesis para est_07
en `est_07_tincunaco_rioChocancharagua-pipeline.md` estaba originalmente
contaminada con valores de est_08 (Ume Pay) — ya corregida en una sesión
anterior, verificada por consistencia interna (media/varianza
reproducidas por Normal y Uniforme Momentos). Esta sesión usa la tabla ya
corregida como referencia, sin volver a auditar esa corrección puntual
(ya está resuelta), pero sin asumir que el resto del contenido es
correcto — todo lo demás se verificó desde cero.

**Nota de cierre (15/07/2026):** este documento fue revisado y corregido
después de una ronda de verificación cruzada Chat↔Code. Las correcciones
están marcadas inline con fecha, sin borrar el contenido/redacción
original — ver notas "**CORRECCIÓN (15/07/2026)**" en las secciones 1, 4
y 6. Est_07 queda cerrado con este documento como versión final.

### Método y alcance

Mismo método que est_01-06. Los documentos previos
(`est_07_tincunaco_rioChocancharagua-pipeline.md`,
`est_07_tincunaco_rioChocancharagua-unitarias.md`) se usaron solo como
fuente de la serie y de los valores de referencia de la tesis (tabla ya
corregida).

---

### 1. Etapa 1 — reconstrucción completa

Las 5 pruebas se reconstruyeron a mano de forma independiente. 4/5
coinciden **exacto** con la salida del pipeline; Cramer coincide con el
pipeline pero reveló un hallazgo nuevo al compararlo contra la tesis (ver
más abajo).

| Variable | METIS | Tesis | diff% | Nivel |
|---|---|---|---|---|
| n | 19 | 19 | 0.00% | PASS |
| Media | 52.6947 | 52.695 | ~0% | PASS |
| Varianza (no sesgada) | 804.1994 | 804.199 | ~0% | PASS |
| Desvío | 28.3584 | 28.358 | ~0% | PASS |
| M0/M1/M2/M3 | 52.695/34.384/26.139/21.337 | 52.695/34.384/26.139/21.337 | ~0% | PASS |
| Suma ln(xi) | 72.5602 | 72.56 | ~0% | PASS |
| Máximo/Mínimo | 120.0 / 11.8 | 120.0 / 11.8 | 0.00% | PASS |
| Asimetría no sesgada (g) | 0.9476 | 0.874 | +8.42% | DECISIÓN013, mayor magnitud vista (n chico) |
| Curtosis no sesgada (k) | 4.2382 | 3.804 | +11.42% | DECISIÓN013, mayor magnitud vista |
| CV | 0.5382 | 0.538 | ~0% | PASS |

Sin discrepancia de datos base. g/k con la mayor magnitud de diff vista
en las 7 estaciones auditadas hasta ahora — consistente con que n=19 es
la muestra más chica de las auditadas con Etapa 2 completa hasta ahora,
lo que amplifica la sensibilidad del ddof (DECISIÓN013).

**Independencia** — Anderson: k_max=ceil(19/3)=7, 0/7 lags fuera →
aprobada, coincide con "0 puntos fuera cumple idealmente con el límite
admisible de 0.7" de la tesis. Wald-Wolfowitz reconstruido a mano: METIS
n1=8, n2=11, R=12, Z=0.8423 — **coincide exacto con la tesis** (n1=8,
n2=11, R=12, Z=0.84). Nivel de independencia: `independiente` en
ambos — PASS total.

**Homogeneidad** — Helmert: S=7, C=11, S-C=-4 — **coincide exacto con la
tesis**. t-Student: METIS 0.3206 (partición floor, n1=9/n2=10) vs tesis
-0.06 — **misma discrepancia de convención de partición para n impar ya
documentada en est_03/est_05**. Verificado a mano: con partición ceil
(n1=10/n2=9, la convención de tesis) se obtiene t=-0.06325 — coincide
casi exacto con el -0.06 de tesis. Confirma, con una tercera estación,
que la tesis usa `n1=ceil(n/2)` y METIS usa `n1=floor(n/2)` — mismo
patrón ya conocido, no un hallazgo nuevo. Ambos aprueban en cualquiera de
las dos particiones (|t| « crítico=2.11 en los dos casos).

**Hallazgo — Cramer, n_w1: contraejemplo real a la convención "siempre
ceil" de DECISIÓN011.** METIS calcula `n_w1=ceil(19×0.6)=ceil(11.4)=12`,
dando τ1=-0.19317, tw1=1.07787. La tesis reporta τ1=-0.16779,
tw1=0.82742 — **verificado a mano que este valor exacto solo se
reproduce con n_w1=11, no 12** (n_w1=10 da τ1=-0.07563, tampoco
coincide). Fórmula τ_w→t_w verificada como Ec. III-15 exacta (sin
ambigüedad — confirmado contra código real y reconstrucción propia): la
discrepancia es 100% de partición, no de fórmula.

~~DECISIÓN011 (decisions-log.md) había establecido "n_w1 usa ceil
(correcto, confirmado con est_02 tau_w1=0.18289 ✓ y est_04
tau_w1=-0.186 ✓)" — pero ese respaldo tiene un punto ciego: para est_04
(n=36, n×0.6=21.6), `ceil` y `round` dan el mismo resultado (22), así que
esa estación nunca pudo distinguir entre las dos reglas. Solo est_02
(n=24, n×0.6=14.4 → necesita 15, que es `ceil`, no `round`=14) y ahora
est_07 (n=19, n×0.6=11.4 → necesita 11, que es `round`/`floor`, no
`ceil`=12) son estaciones que sí distinguen entre las reglas — y dan
resultados contradictorios entre sí. No hay una única regla de
redondeo (`ceil`, `round`, ni `floor`) que reproduzca los tres casos
confirmados (est_02 necesita ceil, est_07 necesita round/floor).~~

**CORRECCIÓN (15/07/2026):** el párrafo tachado arriba subestimaba el
censo real — quedaba planteado como empate 1 a 1. Censo completo,
verificado por Code contra las 7 series reales (est_01-07) y
recontrastado por Chat con las series crudas de est_02 y est_05:

| Estación | n | n×0.6 | ceil | round=floor | ¿Discrimina? | Qué reproduce tesis |
|---|---|---|---|---|---|---|
| est_01 | 40 | 24.00 | 24 | 24 | No | único candidato |
| est_02 | 24 | 14.40 | 15 | 14 | **Sí** | **ceil** (τ1=0.18289 exacto con n_w1=15; n_w1=14 da 0.26204, no coincide) |
| est_03 | 41 | 24.60 | 25 | 25 | No | — |
| est_04 | 36 | 21.60 | 22 | 22 | No | — |
| est_05 | 39 | 23.40 | 24 | 23 | **Sí** | **ceil** (τ1=-0.16143 exacto con n_w1=24, ya reconstruido en est_05-e2e.md) |
| est_06 | 38 | 22.80 | 23 | 23 | No | — (verificado contra est_06-e2e.md) |
| est_07 | 19 | 11.40 | 12 | 11 | **Sí** | **round/floor** (τ1=-0.16779 exacto con n_w1=11; n_w1=12 da -0.19317, no coincide) |

**Son 3 estaciones discriminantes, no 2** (est_02, est_05, est_07): **2
confirman ceil** (est_02, est_05) y **1 lo contradice** (est_07). No es
un empate — es una regla mayoritaria (ceil, 2 de 3) con una excepción
real y verificada, no una ausencia total de regla. El n_w2 (30%) no
muestra este problema en est_07: `round(19×0.3)=6` coincide exacto con
tesis (τ2=0.18061, tw2=0.50977 — verificado independientemente por Chat
y Code, fórmula Ec. III-15 confirmada exacta).

**Clasificación: Pendiente de dominio** — la regla de redondeo de n_w1 en
Cramer tiene una excepción real frente a la mayoría (ceil, 2 de 3 casos
discriminantes). No cambia ningún veredicto (Cramer aprueba con
cualquiera de las dos particiones en est_07, tw1 muy por debajo del
crítico 2.11 en ambos casos) — es un hallazgo de precisión de fórmula,
no de resultado práctico. Candidato de consulta a Facundo con evidencia
numérica de 3 estaciones (2 a favor de ceil, 1 en contra), no 2.

**Veredicto general Etapa 1: Habilitada para Etapa 2, en ambos.
Aprobado** — el veredicto final no se ve afectado por ninguno de los dos
hallazgos de convención de partición (t-Student, Cramer n_w1).

**Tendencia y atípicos** (sin referencia de tesis): Mann-Kendall aprueba
(Z=-0.210, TEST_WARNING_SMALL_SAMPLE por n≤40), KS aprueba (Z=0.605),
Chow aprueba (2.3367 < K_N=2.5312). Sin hallazgos.

---

### 2. Etapa 2 — cableado completo (34/34, primera vez para esta estación)

**13/13 distribuciones, 34/34 combinaciones distribución×método
verificadas — 0 hallazgos de cableado.** Primera verificación completa
de cableado para est_07 (nunca se había reconstruido ni siquiera
parcialmente en rondas de Fase 2). Corrido con los fixes de
`gamma3p.py::mv` (DECISIÓN 023) y el docstring de
`exponencial_x0_beta.py` (DECISIÓN 024) ya aplicados.

`gamma3p`/mv converge acá sin necesitar el fix de escaneo denso (raíz ya
encontrable con el escaneo original) — coincide con lo ya observado en
la verificación de regresión de est_04 (est_07 listado ahí como estación
"sin cambios, ya convergía correctamente con el scan viejo").

---

### 3. Etapa 2 — parámetros y EEA, comparación completa contra tesis

| Distribución | Método | Param. | METIS | Tesis | diff% |
|---|---|---|---|---|---|
| Uniforme | Momentos | α, β, EEA | 3.5765 / 101.813 / 8.4927 | 3.58 / 101.81 / 8.4927 | ~0% |
| Uniforme | MV | α, β, EEA | 11.80 / 120.00 / 16.6835 | igual | 0% |
| Exponencial β | Mom/MV | β, EEA | 0.018977 / 15.3565 | 0.019 / 15.3565 | -0.12% / ~0% |
| Exponencial x0β | Momentos | x0, β, EEA | 24.336 / 28.358 / 6.8458 | 24.34 / 28.36 / 6.8458 | ~0% |
| Exponencial x0β | MV | x0, β, EEA | 9.528 / 43.167 / 8.4850 | 9.53 / 43.17 / 8.485 | ~0% |
| Gen. Exponencial | Momentos | α, λ | 4.7776 / 0.042550 | **2.69 / -0.125** | **+77.6% / signo distinto** — ver hallazgo D |
| Gen. Exponencial | MV | α, λ, EEA | 4.3923 / 0.041012 / 4.5495 | 4.39 / 0.041 / 4.5495 | ~0% |
| Gen. Exponencial | ML | α, λ | 0.4427 / -0.011306 | 0.76 / -0.0095 | -41.8% / +19.0% (pendiente IV-84) |
| Normal | Mom/MV | µ, σ, EEA | 52.695 / 28.358 / 7.3730 | 52.69 / 28.3584 / 7.7741 | ~0% / -5.16% |
| Normal | ML | σ, EEA | 28.4826 / 7.3363 | 28.4826 / 7.8195 | 0% / -6.18% |
| Log-Normal 2p | Mom/MV | µy, σy | 3.8190 / 0.5781 | 3.82 / 0.578 | **~0%** |
| Log-Normal 2p | Mom/MV | EEA | **2.9653** | **3.9748** | **-25.40% — ver hallazgo A (modelo seleccionado, sin invertir ranking)** |
| Log-Normal 3p | Momentos | x0, µy, σy, EEA | -39.897/4.4834/0.2994/5.3395 | -42.79/4.5663/0.2782/6.3714 | Causa A / -16.20% |
| Log-Normal 3p | MV | x0, µy, σy | -13.709 / 4.1110 / 0.4150 | -13.71 / 4.111 / 0.415 | **~0% los 3** |
| Log-Normal 3p | MV | EEA | 5.2059 | 6.3517 | **-18.04% — Causa C** |
| Gamma 2p | Momentos | α, β, EEA | 15.261 / 3.4528 / 4.9214 | 15.26 / 3.453 / 5.9656 | ~0% / -17.51% |
| Gamma 2p | MV | α, β, EEA | 14.661 / 3.5943 / 5.3216 | 14.66 / 3.594 / 6.3467 | ~0% / -16.15% |
| Gamma 2p | ML | α, β, EEA | 16.665 / 3.1620 / 4.0824 | 16.67 / 3.162 / 5.154 | ~0% / -20.79% |
| Gamma 3p | Momentos | x0, α, β, EEA | -7.161/13.436/4.4550/5.1136 | -12.218/12.389/5.24/6.1764 | Causa A / -17.21% |
| Gamma 3p | MV | x0, α, β | 4.4082 / 16.8245 / 2.8700 | 4.408 / 16.825 / 2.87 | **~0% los 3** |
| Gamma 3p | MV | EEA | 5.0036 | 6.107 | **-18.07% — Causa C** |
| Gamma 3p | MPP | — | EXCLUIDO (no implementado) | x0=2.682, α=18.8, β=2.66, EEA=4.7393 | pendiente de código ya conocido |
| Gumbel | los 4 métodos | α, µ, EEA | ver tabla — **PASS total, ≤0.01% en los 4 métodos** | igual | 0% |
| GVE | Momentos | ν, α, β, EEA | 4325.07 / 21.812 / -0.01024 / 4668.29 | 45.035 / 20.487 / -0.215 / **61.2567** | β degenerado — no reproducible con IV-203/204 |
| GVE | MV | ν, α, β, EEA | 39.690 / 21.192 / -0.03166 / 5.6755 | 39.69 / 21.192 / -0.032 / 5.6755 | **~0% los 4 — PASS exacto** |
| GVE | ML | β | -0.04706 | -0.047 | ~0.13% (casi exacto) |
| GVE | ML | α, ν, EEA | 22.161 / 38.825 / 4.3940 | **24.63 / 91.307 / 57.0234** | -10.03% / -57.47% / -92.29% — mismo patrón GVE-ML, 7ª estación consecutiva |
| LP3 | Directo | — | NO_APLICABLE (B=2.730 ∉ (3,6]) | α=0.359, β=0.158, y0=3.884, EEA=26.4022 | METIS aplica correctamente la restricción IV-249 — ver Hallazgo F |
| LP3 | Indirecto | α, β, y0 | 0.1461 / 15.648 / 1.5321 | 0.135 / 18.404 / 1.339 | +8.25% / -14.97% / +14.42% (Causa A) |
| LP3 | Indirecto | EEA | 4.4182 | 4.414 | +0.10% — prácticamente PASS |
| LP3 | MV | — | NO_CONVERGE | α=0.677, β=2.121, y0=2.382, EEA=77.2356 | ver hallazgo E — dirección inversa a lo usual |

---

### 4. Hallazgos relevantes — con causa e implicancia

**A. Log-Normal 2p — modelo seleccionado por Facundo; Causa C presente,
pero sin invertir el ranking (a diferencia de est_05).** Los 2 parámetros
coinciden con la tesis a menos de 0.03% — el mismo punto en el espacio de
parámetros. El EEA diverge -25.40% (METIS=2.9653 vs tesis=3.9748) —
**en dirección contraria a la mayoría de los casos de Causa C del
proyecto**: acá METIS calcula un EEA *menor* (mejor ajuste aparente) que
el que reporta la tesis para sus propios parámetros, no mayor. Verificado
que esto no invierte el ranking: en la tabla de tesis, LN2p (3.9748) ya
es el mejor de toda la lista; con el EEA de METIS (2.9653), LN2p sigue
siendo el mejor en el ranking que produciría METIS (el segundo lugar,
Gumbel Momentos-L, tiene EEA=4.3188 en ambos, sin cambios). **No es Causa
D** — la selección de modelo no se ve afectada, aunque el valor absoluto
del EEA sí diverge. Cuantiles: PASS en T=2 (-0.01%), degrada a **+18.25%
en T=100** — mismo patrón sistémico de Causa C, magnitud menor que los
casos de est_01/03/05 (+38% a +54%).

**CORRECCIÓN — agregado (15/07/2026):** test de aislamiento corrido con
la función real `calcular_eea()` (Code) y reconstrucción propia (Chat),
inyectando los parámetros exactos de tesis (µy=3.82/σy=0.578) en vez de
los ajustados por METIS: **EEA=2.9291** — más bajo aún que el 2.9653 de
METIS, y lejos del 3.9748 que la tesis reporta para sus propios
parámetros. Confirma que ni con los parámetros perfectos de Facundo se
reproduce su propio EEA. Proporción: **~99.5% Causa C**, verificado por
dos vías independientes (Chat y Code, diff <0.1 punto porcentual entre
ambas en T=100).

**B. Gumbel — PASS perfecto en los 4 métodos, quinta estación
consecutiva** (est_03 a est_07 — confirmado contra est_06-e2e.md, que
reporta "cuarta estación consecutiva, est_03-est_06").

**C. GVE MV — PASS exacto en los 4 valores, cuarta estación consecutiva**
(est_04 a est_07 — confirmado contra est_06-e2e.md, que reporta "tercera
estación consecutiva, est_04-est_06").

**D. Generalizada Exponencial Momentos — divergencia más severa que en
otras estaciones, con signo de λ invertido en la tesis.** METIS:
α=4.7776, λ=0.042550 (ambos positivos, consistente con el resto del
dataset). Tesis: α=2.69, **λ=-0.125** (negativo) — es la primera vez en
7 estaciones que la propia tesis reporta λ negativo para el método
Momentos de esta distribución (en el resto de las estaciones el λ
negativo aparece en Momentos-L, no en Momentos). Verificado con el
mismo chequeo de consistencia interna ya usado en otras 6 estaciones:
CV_datos=0.53816; con α=4.7776 (METIS) el CV teórico coincide exacto;
con α=2.69 (tesis) el CV teórico da 0.66329 — diff +23.2% respecto del
CV real, la mayor divergencia de este chequeo vista hasta ahora.
**Clasificación: Pendiente de dominio — mismo patrón ya documentado
(pendiente IV-77), con la divergencia más severa del dataset.**

**E. Log-Pearson III MV — METIS no converge donde la tesis reporta
valores, en la dirección opuesta al patrón habitual del proyecto.** En
la mayoría de los casos ya vistos (GVE Momentos, Gen. Pareto en est_01),
es METIS el que converge donde la tesis no. Acá es al revés: tesis
reporta α=0.677, β=2.121, y0=2.382 con EEA=77.2356 — **el peor EEA de
toda su propia tabla para est_07** (el siguiente peor es GVE Momentos con
61.26). METIS no encuentra bracket en su escaneo.

**Verificado (Code + Chat, 15/07/2026):** escaneo fino de la
verosimilitud perfilada (Thom, DECISIÓN021 — no el sistema literal con
digamma) sobre el dominio completo [-9.093826, 2.468100]: monótonamente
decreciente hacia el borde inferior, mínimo en y0=-9.093826, a 2.3e-7 del
borde — dentro del guard de convergencia de borde (1e-4). Sin mínimo
interior real. Es el mismo tipo de falsa convergencia de borde inferior
ya confirmado en est_03. `no_converge` es el resultado correcto, no un
guard que esté descartando de más. Dado que el resultado de tesis para
este caso ya es de calidad muy pobre (EEA casi 14x peor que el mejor
modelo de la tabla) y no es candidato a ganador, se documenta por
completitud — bajo valor de señal para priorización activa.

**F. LP3 Directo — tesis reporta valores fuera del dominio válido de sus
propias fórmulas (agregado 15/07/2026, elevado desde nota de tabla).**
B=2.7302 (verificado independientemente con fórmula IV-249 sobre
momentos crudos µ1/µ2/µ3 de la serie original, no de ln(xi) — Chat y
Code coinciden al sexto decimal), fuera del rango (3,6] donde los
polinomios IV-251/252 (aproximación de A(C)) tienen respaldo. El guard de
METIS (`logpearson3.py:104`) dispara correctamente y es consistente con
el mismo criterio aplicado sin excepción en est_02/03/05/06 (todas con B
fuera de rango y NO_APLICABLE correcto). La diferencia real es que en
esas estaciones la tesis también excluía el caso — acá reporta α=0.359,
β=0.158, y0=3.884 de todos modos, sin que quede claro qué método usó
Facundo para B fuera del dominio documentado. **Clasificación: Pendiente
de dominio.** No es un bug de METIS — el guard está correctamente puesto
según la fuente. Pregunta directa a Facundo: ¿qué fórmula alternativa
usó para B fuera de (3,6]?

---

### 5. Selección de modelo y cuantiles

**Modelo ganador de Facundo — Log-Normal 2p, EEA tesis=3.9748, EEA
METIS=2.9653 (-25.40%, sin invertir el ranking — ver hallazgo A).**
Parámetros PASS exacto. Cuantiles: PASS en T=2, degrada a +18.25% en
T=100 (Causa C, ~99.5%, verificado por dos vías independientes).

**Testigo — Gumbel Momentos-L, EEA tesis=4.3188, EEA METIS=4.3188 (PASS
exacto).** Cuantiles PASS 7/7, diff ≤0.005%.

---

### 6. Clasificación final est_07

| Columna | Resultado |
|---|---|
| **Etapa 1** | **Aprobado** — sin discrepancias de datos base. Dos hallazgos de convención de redondeo (partición t-Student ya conocida; **n_w1 de Cramer, con censo corregido: 3 estaciones discriminantes, mayoría ceil 2/3, una excepción real**), ninguno afecta el veredicto. |
| **Cableado (13 dist.)** | **Aprobado** — 34/34 combinaciones distribución×método, primera verificación completa para esta estación, 0 hallazgos. |
| **Selección de modelo** | **Aprobado** — el modelo ganador de Facundo (LogNormal 2p) coincide en parámetros; el EEA diverge (Causa C, ~99.5%, verificado con test de aislamiento por dos vías) pero no cambia cuál sería la distribución recomendada. |
| **Cuantiles** | Modelo seleccionado degrada con T (hasta +18.25% en T=100, Causa C, magnitud moderada); testigo (Gumbel MomentosL) PASS exacto 7/7. |

**Clasificación general de la estación: Parcial.** Etapa 1, cableado y
selección de modelo **Aprobados** sin reservas de fondo. El hallazgo más
relevante de esta ronda no es de esta estación en particular sino
**transversal**: el contraejemplo a la convención de redondeo de `n_w1`
en Cramer (DECISIÓN011), que con el censo completo de 3 estaciones
discriminantes (est_02, est_05, est_07) muestra una regla mayoritaria
(ceil) con una excepción real, no una ausencia total de regla —
pendiente de dominio de prioridad media-alta para `pendientes-facundo.md`
(junto con Hallazgo D — Gen. Exponencial Momentos, divergencia más severa
del dataset, y Hallazgo F — LP3 Directo, tesis fuera del dominio válido
de sus propias fórmulas). **Ningún hallazgo de esta ronda requiere
modificar código de `metis/core/` — no se aplicó ni se propone ningún
cambio.**

**Estado: CERRADO (15/07/2026).** Verificación independiente completa
por dos vías (Chat, sin acceso a repo; Code, con acceso a repo y función
real) en los 4 puntos que quedaron abiertos tras el cierre inicial —
todos coinciden. Est_07 queda listo para la tabla de consolidación de las
9 estaciones.