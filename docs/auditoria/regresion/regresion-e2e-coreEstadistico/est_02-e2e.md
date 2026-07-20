## est_02 — Vado de Río Seco – Río Barrancas — Análisis E2E desde cero (14/07/2026)

Detalle completo del análisis Fase 4 (regresión E2E) para esta estación.
Índice y tabla de consolidación de las 9 estaciones: `fase4-e2e.md`.

**Nota de encuadre — por qué se rehace una estación ya marcada "Aprobado":**
est_02 tenía clasificación "Aprobado — único que cumple el estándar completo
hoy" heredada de la ronda de Fase 2 (Bloque 6/7), con solo 28/34 métodos
reconstruidos y sin el estándar de las 4 columnas de Fase 4. Por instrucción
explícita ("todas las estaciones se analizan desde 0, de forma exhaustiva,
nada se infiere ni establece que esta determinado"), se rehizo íntegro sin
asumir esa etiqueta previa como válida. **El resultado confirma que la
sustancia de "Aprobado" se sostiene, pero el proceso encontró dos casos
concretos donde los documentos de auditoría previos (`est_02...unitaria.md`)
ya no coinciden con lo que produce el código actual** — ver hallazgo D. Esto
valida la instrucción de no inferir nada de rondas anteriores.

### Método y alcance

Mismo método que est_01: `ejecutar_etapa1()` + `ejecutar_etapa2()` en vivo
contra el working tree actual, con reconstrucción manual/aislada de cada
estadístico y cada una de las 13 distribuciones × sus métodos, sin usar los
documentos previos (`est_02_vado_rio_seco_rioBarrancas-pipeline.md`,
`est_02_vado_rio_seco_rioBarrancas0-unitaria.md`) como fuente de verdad de
ningún resultado de METIS — solo como fuente de la serie y de los valores
de referencia de la tesis.

**Nota importante sobre el estado del working tree:** `git status` muestra
cambios sin commitear en `gamma2p.py`, `gumbel.py`, `gve.py`,
`lognormal3p.py` y `logpearson3.py` — parte del esfuerzo de
reimplementación de Etapa 2 documentado en `reimplementacion-etapa2.md` y
en DECISIÓN013 (decisions-log.md). Esto explica por qué algunos valores de
esta corrida difieren de los que aparecen en los documentos de Fase 1/2
para esta misma estación (ver hallazgo D) — no es inconsistencia del
código, es que el código evolucionó después de que esos documentos se
escribieran.

---

### 1. Etapa 1 — reconstrucción completa

**Estadística descriptiva** — las 5 pruebas de Etapa 1 se reconstruyeron a
mano de forma independiente (Anderson lag por lag, Wald-Wolfowitz,
Helmert secuencia por secuencia, t-Student, Cramer) y coinciden **exacto**
con la salida del pipeline en los 5 casos — cableado confirmado.

| Variable | METIS | Tesis | diff% | Nivel |
|---|---|---|---|---|
| n | 24 | 24 | 0.00% | PASS |
| Media | 142.5833 | 142.583 | 0.00% | PASS |
| Varianza (no sesgada) | 11818.9493 | 11818.949 | 0.00% | PASS |
| Desvío | 108.7150 | 108.715 | 0.00% | PASS |
| M0/M1/M2/M3 | 142.583/99.741/79.402/66.866 | 142.583/99.741/79.402/66.866 | ~0.00% | PASS |
| Suma ln(xi) | 113.2460 | 113.246 | 0.00% | PASS |
| Máximo/Mínimo | 458.0 / 42.0 | 458.0 / 42.0 | 0.00% | PASS |
| Asimetría no sesgada (g) | 1.6686 | 1.565 | +6.62% | DECISIÓN013, patrón conocido |
| Curtosis no sesgada (k) | 5.9769 | 5.489 | +8.89% | DECISIÓN013, patrón conocido |
| CV | 0.7625 | 0.762 | +0.06% | PASS |

**A diferencia de est_01, acá no hay ningún indicio de discrepancia de
datos base** — media, varianza, M0-M3, suma_log, máximo y mínimo coinciden
prácticamente exactos con la tesis. Solo g/k muestran el diff ya conocido
y documentado (DECISIÓN013, ddof). Esto confirma que la discrepancia de
datos encontrada en est_01 es específica de esa estación, no un problema
sistemático de transcripción del dataset completo.

**Independencia** — Anderson: 1/8 lags fuera de banda (k_max=ceil(24/3)=8,
umbral=ceil(8×0.10)=1) → aprobada. Coincide exacto con "1 punto fuera... no
supera el límite admisible de 1" de la tesis. Wald-Wolfowitz reconstruido a
mano: n1=10, n2=14, R=8, Z=-2.0062 — **n1/n2/R coinciden exacto con la
tesis** (n1=10, n2=14, R=8, Z=-2.01). Rechaza a α=0.05 pero se acepta por
tolerancia a α=0.01 en ambos. Nivel de independencia: `independiente` en
ambos — PASS total.

**Homogeneidad** — Helmert reconstruido secuencia por secuencia: S=16, C=7,
S-C=9 — **coincide exacto con la tesis** (S=16, C=7, S-C=9). t-Student:
-1.7643 vs tesis -1.76 (diff 0.24%, PASS). Cramer reconstruido a mano:
τ1=0.18289, τ2=0.35206, tw1=1.1397, tw2=1.08774 — **coincide exacto con la
tesis** en los 4 valores (esta es la estación que ya sirvió para verificar
DECISIÓN011 en Fase 1 — se reconfirma acá con el mismo rigor de Fase 4).
Nivel de homogeneidad: `homogeneidad_warning` en METIS (Helmert rechaza,
resto aprueba) — coincide en sustancia con "Serie Homogénea (Aprobada por
mayoría)" de la tesis (Cramer y t-Student, las dos pruebas de mayor peso
según la tesis, aprueban unánimemente).

**Veredicto general Etapa 1: Habilitada para Etapa 2, en ambos.**
**Aprobado, sin reservas — la reconstrucción completa no encontró ningún
Pendiente de dominio en Etapa 1 para esta estación** (a diferencia de
est_01).

**Tendencia y atípicos** (sin referencia de tesis): Mann-Kendall aprueba
(Z=1.662, TEST_WARNING_SMALL_SAMPLE por n≤40), KS aprueba (Z=1.021), Chow
aprueba (estadístico=2.0147 < K_N=2.6439, sin atípico detectado).
Comportamiento consistente, sin hallazgos.

---

### 2. Etapa 2 — cableado completo (34/34, extiende las 28/34 de Fase 2)

**13/13 distribuciones, 34/34 combinaciones distribución×método
verificadas — 0 hallazgos de cableado.** La reconstrucción aislada
(`ajustar`+`cuantil`+`calcular_eea`, fuera de `pipeline2.py`) reproduce
exacto — parámetros y EEA, no solo status — lo que produce
`ejecutar_etapa2()` para las 13 distribuciones. Esto **extiende
formalmente** la verificación de Fase 2 (que había cubierto 28/34 métodos
para est_02) a las 34/34, cerrando el gap que dejaba pendiente la tabla de
consolidación de Fase 4.

Diferencia notable respecto de est_01: en est_02, `gen_pareto`/mc converge
a `no_converge` (en est_01 convergía) — confirma que el comportamiento de
Gen. Pareto MC es sensible a la serie particular, consistente con lo ya
señalado en Fase 1 (§3.10) sobre la fragilidad de este método.

---

### 3. Etapa 2 — parámetros y EEA, comparación completa contra tesis

| Distribución | Método | Param. | METIS | Tesis | diff% |
|---|---|---|---|---|---|
| Uniforme | Momentos | α, β | -45.717 / 330.883 | -45.72 / 330.88 | ~0% |
| Uniforme | Momentos | EEA | 52.0788 | 52.0788 | ~0% |
| Uniforme | MV | α, β, EEA | 42.00 / 458.00 / 125.1454 | igual | 0% |
| Exponencial β | Mom/MV | β, EEA | 0.0070134 / 20.9118 | 0.007 / 20.9118 | +0.19% / ~0% |
| Exponencial x0β | Momentos | x0, β, EEA | 33.868 / 108.715 / 24.7462 | 33.87 / 108.71 / 24.7462 | ~0% |
| Exponencial x0β | MV | x0, β, EEA | 37.627 / 104.957 / 27.0591 | 37.63 / 104.96 / 27.0591 | ~0% |
| Gen. Exponencial | Momentos | α, λ | 1.8910 / 0.010212 | **2.85 / 0.0040** | **-33.65% / +155.29%** |
| Gen. Exponencial | MV | α, λ, EEA | 2.6281 / 0.012202 / 35.6104 | 2.63 / 0.0122 / 35.6104 | ~0% |
| Gen. Exponencial | ML | α, λ | 0.3434 / -0.004898 | 0.80 / -0.0033 | -57.08% / -48.41% |
| Normal | Mom/MV | µ, σ | 142.583 / 108.715 | 142.58 / 108.7150 | ~0% |
| Normal | Mom/MV | EEA | 47.0577 | 47.6235 | -1.19% |
| Normal | ML | σ, EEA | 100.8242 / 47.6573 | 100.8242 / 48.6812 | 0% / -2.10% |
| Log-Normal 2p | Mom/MV | µy, σy | 4.7186 / 0.6990 | 4.72 / 0.699 | ~0% |
| Log-Normal 2p | Mom/MV | EEA | 27.6359 | 33.2187 | -16.81% |
| Log-Normal 3p | Momentos | x0, µy, σy | -69.932 / 5.2428 / 0.4821 | -82.04 / 5.3092 / 0.4588 | +14.76% / -1.25% / +5.09% (Causa A) |
| Log-Normal 3p | Momentos | EEA | 29.6942 | 34.2380 | -13.27% |
| Log-Normal 3p | MV | x0, µy, σy | 38.469 / 4.0031 / 1.2927 | 38.47 / 4.0031 / 1.2927 | **~0.00% los 3** |
| Log-Normal 3p | MV | EEA | 29.6102 | 20.7985 | **+42.37%** — ver hallazgo B |
| Gamma 2p | Momentos | α, β | 82.892 / 1.7201 | 82.89 / 1.720 | ~0% |
| Gamma 2p | Momentos | EEA | 26.9310 | 31.2572 | -13.84% |
| Gamma 2p | MV | α, β, EEA | 64.031 / 2.2268 / 34.8765 | 64.03 / 2.227 / 38.78 | ~0% / ~0% / -10.07% |
| Gamma 2p | ML | α, β, EEA | 82.246 / 1.7336 / 27.1573 | 82.25 / 1.734 / 31.4762 | ~0% / ~0% / -13.72% |
| Gamma 3p | Momentos | x0, α, β | 12.273 / 90.699 / 1.4367 | 3.683 / 85.089 / 1.632 | +233.2%* / +6.59% / -11.96% (Causa A) |
| Gamma 3p | Momentos | EEA | 26.7550 | 31.8321 | -15.95% — ver hallazgo D |
| Gamma 3p | MV | — | NO_CONVERGE | NO_CONVERGE | coincide |
| Gamma 3p | MPP | — | EXCLUIDO (no implementado) | x0=35.355, α=141.841, β=0.756, EEA=25.2045 | mismo pendiente de código que est_01 |
| Gumbel | los 4 métodos | α, µ, EEA | ver tabla completa arriba (script) | — | todos ≤0.01% — PASS total |
| GVE | Momentos | ν, α, β | 2328.97 / 76.413 / -0.0715 | 176.590 / 94.250 / -0.059 | +1218.9% / -18.93% / -21.24% |
| GVE | Momentos | EEA | 2385.28 | 143.1475 | +1566% — ver hallazgo D |
| GVE | MV | ν, α, β, EEA | 77.660 / 44.261 / -0.7002 / 37.6088 | igual | ~0% los 4 |
| GVE | ML | β | -0.2783 | -0.278 | -0.10% (muy cerca) |
| GVE | ML | α, ν, EEA | 58.836 / 86.567 / 28.2976 | **80.352 / 163.884 / 91.8783** | -26.78% / -47.18% / -69.20% — ver hallazgo E |
| LP3 | Directo | — | **NO_APLICABLE** (B=2.683 ∉ (3,6]) | α=0.333, β=37.229, y0=4.818, EEA=94.1897 | ver hallazgo C |
| LP3 | Indirecto | α, β, y0 | 0.1221 / 32.766 / 0.7173 | 0.351 / 0.509 / 0.454 | -65.21% / **+6337%** / +58.00% — ver hallazgo F |
| LP3 | Indirecto | EEA | 23.5367 | 30.1143 | -21.84% |
| LP3 | MV | α, β, y0, EEA | 0.8422 / 1.1758 / 3.7284 / 83.5049 | 0.115 / 2.242 / 3.577 / 325.6784 | grandes — Causa B (convergencia a óptimo distinto), ya documentado |
| Gen. Pareto | todos | — | (calculados) | no listada en tabla de tesis | SKIP |

\* diff% de x0 poco informativo por denominador cercano a cero (3.683) —
ver hallazgo D para el análisis correcto en términos absolutos.

---

### 4. Hallazgos relevantes — con causa e implicancia

**A. Modelo seleccionado (Exponencial β) — PASS total, incluidos los 7
cuantiles de diseño.** A diferencia de est_01, acá el modelo que Facundo
efectivamente eligió como ganador **sí está implementado en METIS y
reproduce exacto**: β=0.0070134 (diff +0.19%), EEA=20.9118 (diff ~0.00%),
y los 7 cuantiles de diseño (T=2 a 100) con diff ≤0.001% en todos los
casos. **Esta es la primera estación, junto con la reconstrucción de Fase
1/2 ya hecha, donde el ciclo completo — parámetros, EEA, selección de
modelo y cuantiles de diseño — cierra sin ningún pendiente.**

**B. Testigo (Log-Normal 3p MV) — Causa C confirmada con la señal más
limpia vista hasta ahora.** Los 3 parámetros coinciden con la tesis a
menos de 0.01% (x0, µy, σy) — es, literalmente, el mismo punto en el
espacio de parámetros. Y sin embargo el EEA diverge +42.37% y los
cuantiles divergen de forma creciente con T: PASS casi exacto en T=2
(-0.003%) hasta **+43.28% en T=100**. Con parámetros idénticos no puede
haber ninguna explicación de fórmula ni de cableado (ambos ya verificados
— IV-120 fiel a la tesis desde Fase 1, cableado 34/34 confirmado en esta
sesión). **Es el caso más limpio del proyecto hasta ahora de "Causa C":
mismos parámetros exactos, resultado final distinto — refuerza
directamente el hallazgo I de est_01 (la fórmula documentada, con los
parámetros de la tesis, no reproduce la tabla de la tesis) con una segunda
estación independiente.** Clasificación: **Pendiente de dominio — Causa C.**

**C. Log-Pearson III Directo — un documento de auditoría previo
(`est_02...unitaria.md`, Fase 1/2) ya no coincide con el código actual.**
El documento previo reportaba esta combinación como **PASS exacto**
(EEA=94.19 = tesis, "0.0%"). La reconstrucción de esta sesión, verificada
a mano de forma independiente (B=(ln(µ3)-3ln(µ1))/(ln(µ2)-2ln(µ1))=2.683,
fuera del rango (3,6] exigido por IV-249/252), confirma que el código
actual devuelve correctamente **NO_APLICABLE** — la restricción de rango de
B está aplicándose tal como está documentada, y B=2.683 está claramente
fuera. **No es un hallazgo contra METIS** (el comportamiento actual es el
correcto, verificado desde la fórmula) — es evidencia de que el documento
previo quedó desactualizado, probablemente escrito comparando directo
contra los valores de tesis sin ejecutar el guard B∈(3,6] que se agregó o
confirmó después. **Sirve como caso de estudio concreto de por qué la
instrucción de "no asumir nada de rondas anteriores" es necesaria** — un
documento marcado como fuente de verdad tenía una fila incorrecta.

**D. Gamma 3p Momentos y GVE Momentos — los números de EEA de esta sesión
difieren de los que registran los documentos de Fase 1/2 para la misma
estación y método, por evolución legítima del código, no por error.**
- Gamma 3p Momentos: esta sesión obtiene EEA=26.7550; el documento previo
  registraba EEA=37.00 para la misma combinación. Verificado a mano
  (IV-137/138/139 con g=1.6686, ddof=0 — DECISIÓN013): α=90.699,
  β=1.4367, x0=12.273 — coincide exacto con lo que produce el código hoy.
  DECISIÓN013 (decisions-log.md) documenta explícitamente que
  `gamma3p.py::_skewness` fue corregido de ddof=1 a ddof=0 **después** de
  que se generara el documento de auditoría previo — el cambio de EEA es
  consecuencia directa y esperada de ese fix, no un bug nuevo.
- GVE Momentos: esta sesión obtiene EEA=2385.28 (ν=2328.97, α=76.41,
  β=-0.0715); el documento previo registraba EEA=1144.00. `git status`
  confirma que `gve.py` tiene cambios sin commitear en este working tree
  — el documento previo se generó contra una versión anterior del archivo.
  Los parámetros que produce el código de hoy siguen sin ser reproducibles
  con IV-203/204 contra el β de tesis (mismo pendiente ya documentado en
  Fase 1, "GVE Momentos — beta no reproducible"), así que la clasificación
  de fondo no cambia — sigue siendo Pendiente Facundo — pero el número
  concreto de EEA sí cambió.

**Implicancia metodológica, no solo puntual de est_02:** los archivos
`gamma2p.py`, `gumbel.py`, `gve.py`, `lognormal3p.py` y `logpearson3.py`
tienen cambios sin commitear en el working tree actual (parte del esfuerzo
de reimplementación de Etapa 2). Cualquier documento de auditoría anterior
(Fase 1, Fase 2, Fase 3) que reporte números para estas 5 distribuciones
debe tratarse como **potencialmente desactualizado** hasta ser re-verificado
contra el código actual — exactamente lo que exige el encuadre "desde
cero" de esta fase, y exactamente lo que ya pasó acá dos veces en una sola
estación.

**E. GVE Momentos-L — tercera estación consecutiva con el mismo patrón
exacto (β cerca, ν/α lejos).** β=-0.2783 (METIS) vs -0.278 (tesis, diff
-0.10%, prácticamente idéntico); ν=86.57 vs 163.88 (-47.2%), α=58.84 vs
80.35 (-26.8%). Método cerrado, sin iteración (IV-234 a IV-241, ya
verificado fiel a la tesis en Fase 1) — no puede ser "convergencia a
óptimo distinto". Mismo síntoma exacto que est_01 (hallazgo D) y que
est_05/est_06 (Fase 1, §3.12). **Con cuatro estaciones mostrando el mismo
patrón, esto deja de ser una curiosidad puntual — es evidencia consistente
de que la fuente/tabla que usó Facundo para ν y α en GVE Momentos-L no se
deriva de aplicar IV-240/241 directo a M̂0/M̂1/M̂2 como está documentado.
Candidato de alta prioridad para pregunta directa a Facundo** (ya está en
`pendientes-facundo.md`, esta sesión aporta un cuarto punto de datos).

**F. Log-Pearson III Indirecto — el β de tesis es ~64x menor que el de
METIS; hipótesis no confirmada sobre el origen.** METIS: β=32.766 (IV-255,
β̂=4/gy², verificado a mano: gy=0.34939, β=4/gy²=32.766 — coincide exacto,
fórmula y cableado correctos). Tesis: β=0.509. **Observación, no
confirmada:** el α que reporta la tesis (0.351) está sorprendentemente
cerca del gy que calcula METIS (0.34939, diff 0.5%) — abre la hipótesis de
que la columna "alfa" de la tesis para esta fila podría estar reportando
gy en lugar del parámetro α real, pero no hay forma de confirmarlo sin la
planilla original. **Clasificación: Pendiente de dominio, causa no
confirmada — se deja la hipótesis anotada, no como hallazgo cerrado.**

**G. Generalizada Exponencial Momentos — parámetros de tesis internamente
inconsistentes con el CV de su propia serie (mismo patrón ya documentado
en otras 3 estaciones, reconfirmado acá con el cálculo exacto).**
CV_datos = S/x̄ = 0.76247. Con α=1.8910 (METIS), el CV teórico de la
Generalizada Exponencial (fórmula IV-77, digamma/trigamma) da 0.76247 —
coincide hasta la sexta cifra decimal con el CV real de los datos. Con
α=2.85 (tesis), el CV teórico da 0.64882 — no coincide con el CV real de
la serie (diff -14.9%). **METIS es matemáticamente consistente con sus
propios datos; el valor de tesis no lo es. No es un hallazgo contra
METIS.**

---

### 5. Clasificación final est_02

| Columna | Resultado |
|---|---|
| **Etapa 1** | **Aprobado**, sin reservas — las 5 pruebas reconstruidas a mano coinciden exacto con el pipeline y con la tesis (incluidos n1/n2/R de Wald y S/C de Helmert, algo que en est_01 no cerraba). Sin Pendientes de dominio en Etapa 1. |
| **Cableado (13 dist.)** | **Aprobado** — 34/34 combinaciones distribución×método, reconstrucción propia completa, 0 hallazgos. Extiende formalmente el 28/34 que dejó Fase 2. |
| **Selección de modelo** | **Aprobado** — el modelo ganador de Facundo (Exponencial β) está implementado, converge, y sus parámetros/EEA coinciden con la tesis (diff ≤0.2%). |
| **Cuantiles** | **Aprobado** para el modelo seleccionado — 7/7 cuantiles con diff ≤0.001%. El testigo (Log-Normal 3p MV) queda **Pendiente de dominio — Causa C** (parámetros idénticos, EEA/cuantiles divergen crecientemente con T), pero no es el modelo que el usuario experto elegiría según el sistema. |

**Clasificación general de la estación: Aprobado, con hallazgos anexos que
no cambian la clasificación pero son relevantes para el informe.** A
diferencia de est_01, en est_02 el ciclo completo (Etapa 1 → cableado →
selección de modelo → cuantiles del modelo seleccionado) cierra sin ningún
Pendiente de código ni Pendiente de dominio en la ruta que efectivamente
usaría un usuario experto. Los Pendientes de dominio que sí aparecen
(hallazgos B, E, F, G) están todos en distribuciones/métodos que no son
el modelo ganador — relevantes para el informe integral y para
`pendientes-facundo.md`, pero no bloquean la operación del sistema para
esta estación. El hallazgo más importante para el proceso de auditoría en
sí (no para el resultado hidrológico) es el **D**: dos números de un
documento de Fase 1/2 ya no coinciden con el código actual, por evolución
legítima (DECISIÓN013, working tree de Etapa 2 en curso) — confirma
empíricamente por qué esta fase exige rehacer todo desde cero en vez de
heredar clasificaciones previas. **Ningún hallazgo de esta ronda requiere
modificar código de `metis/core/` — no se aplicó ni se propone ningún
cambio.**

## est_02 — Contraverificación independiente (Auditoría, 14/07/2026)

Verificación independiente del análisis E2E de Code para est_02, antes y
después de recibir su reporte. Método: reconstrucción manual con las
fórmulas ya fieles de Fase 1, series y parámetros propios, sin usar el
documento de Code como fuente de ningún resultado de METIS hasta
confirmarlo por cuenta propia.

### Etapa 1 — CONFIRMADO 5/5 (independiente de la corrida de Code)
Helmert (S=16/C=7/S-C=9), t-Student (t=-1.764307), Anderson (max|r_k| en
k=1, 1/8 lags fuera de banda con límite dependiente de k), Wald-Wolfowitz
(n1=10/n2=14/R=8/Z=-2.006240) y Cramer (τ60=0.18289, τ30=0.35206) —
reconstruidos a mano, los 5 coinciden exacto con el pipeline y con la
ficha de Facundo. Sin hallazgos de cableado. Confirma independientemente
la sección 1 del documento de Code.

### Hallazgo B (LN3p MV, Causa C) — confirmado con reconstrucción propia
ANTES de leer el reporte de Code, con números casi idénticos:
- Reconstruí el método de perfil de verosimilitud sobre x0 (DECISIÓN020,
  formula documentada) de forma independiente: x0=38.4692 — coincide
  exacto con el pipeline y con la tesis (38.47).
- Reconstruí el EEA con Weibull/T=(n+1)/i usando estos parámetros:
  **29.55** (mío) vs **29.6102** (Code/pipeline) vs **20.7985** (tesis).
  Doble confirmación independiente del mismo hallazgo — parámetros
  prácticamente idénticos a la tesis, EEA no reproducible desde ellos.
  Refuerza el hallazgo I de est_01 con una segunda estación.

### Autocorrección durante la verificación — aclara el alcance de DECISIÓN013
Al verificar a mano Gamma 3p Momentos (hallazgo D de Code) y la hipótesis
de LP3 Indirecto (hallazgo F), mi primer intento usó la fórmula clásica
de ajuste de sesgo (Fisher-Pearson, `n²/((n-1)(n-2)) · m3/S³` con S
muestral ddof=1) y NO reprodujo los números de Code. Antes de reportar
discrepancia, se investigó: esa fórmula clásica reproduce el **g de la
tesis** (1.565368 ≈ 1.565 — es lo que calcula Excel SKEW()), no el **g de
METIS** (1.668559). La fórmula correcta de METIS es
`n²/((n-1)(n-2)) · m3/m2^1.5` (momentos poblacionales ddof=0 en ambos
términos, no solo en m3). **Precisión sobre DECISIÓN013:** no es un
cambio de ddof sobre la misma fórmula — son dos fórmulas
estructuralmente distintas que coinciden en nombre ("g"). Vale la pena
dejar esta distinción explícita en `decisions-log.md` si no lo está.

Con la fórmula corregida, reconstrucción a mano:
- **Gamma 3p Momentos** (IV-137/138/139, g=1.668559): beta=1.4367,
  alfa=90.6987, x0=12.2733 — coincide exacto con los tres valores de
  Code (hallazgo D confirmado).
- **LP3 Indirecto** (β=4/gy²): gy=0.34939 (exacto a Code), beta=32.7664
  (exacto a Code). Hipótesis del hallazgo F — que el "alfa"=0.351 de la
  tesis sea en realidad gy, no el parámetro real — verificada:
  gy=0.34939 vs tesis 0.351, **diff=+0.46%**. Hipótesis bien fundada,
  no especulativa.

### Sin re-derivar (fuera de foco de esta pasada)
Hallazgo E (GVE Momentos-L) y G (Gen. Exponencial, chequeo de CV vía
digamma/trigamma) no se re-verificaron de forma independiente — requieren
fórmulas de momentos-L / digamma-trigamma ya cerradas en Fase 1, y
reabrirlas no es el foco de esta fase. Ambos son consistentes con el
patrón ya establecido en estaciones previas, sin motivo para dudar de
ellos.

### Veredicto sobre el documento de Code
Aprobado sin cambios. Todo lo verificable de forma independiente en esta
pasada (Etapa 1 completa, hallazgo B, hallazgo D, hallazgo F) coincide
exacto o casi exacto con lo reportado. Sin objeciones ni adiciones que
cambien la clasificación general de **Aprobado** para est_02.