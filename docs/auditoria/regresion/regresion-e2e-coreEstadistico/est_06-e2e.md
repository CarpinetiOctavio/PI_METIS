## est_06 — Las Tapias – Río San Bartolomé — Análisis E2E desde cero (14/07/2026)

Detalle completo del análisis Fase 4 (regresión E2E) para esta estación.
Índice y tabla de consolidación de las 9 estaciones: `fase4-e2e.md`.

**Nota de encuadre:** est_06 tenía Etapa 1 y selección de modelo ya
resueltas (coincide, Exponencial x0β MV, cuantiles PASS 7/7 en rondas
previas), pero cableado incompleto — solo Gamma 2p reconstruido. Se
rehizo íntegro desde cero, con el código ya incluyendo el fix de
`gamma3p.py::mv` (DECISIÓN 023).

### Método y alcance

Mismo método que est_01-05. Los documentos previos
(`est_06_las_tapias_rioSanBartolome-pipeline.md`,
`est_06_las_tapias_rioSanBartolome-unitarias.md`) se usaron solo como
fuente de la serie y de los valores de referencia de la tesis.

---

### 1. Etapa 1 — reconstrucción completa

Las 5 pruebas se reconstruyeron a mano de forma independiente y coinciden
**exacto** con la salida del pipeline.

| Variable | METIS | Tesis | diff% | Nivel |
|---|---|---|---|---|
| n | 38 | 38 | 0.00% | PASS |
| Media | 44.1842 | 44.184 | ~0% | PASS |
| Varianza (no sesgada) | 775.3435 | 775.344 | ~0% | PASS |
| Desvío | 27.8450 | 27.845 | ~0% | PASS |
| M0/M1/M2/M3 | 44.184/29.619/23.023/19.035 | 44.184/29.619/23.023/19.035 | ~0% | PASS |
| Suma ln(xi) | 137.2558 | 137.256 | ~0% | PASS |
| Máximo/Mínimo | 109.0 / 14.0 | 109.0 / 14.0 | 0.00% | PASS |
| Asimetría no sesgada (g) | 1.1493 | 1.104 | +4.10% | DECISIÓN013, patrón conocido |
| Curtosis no sesgada (k) | 3.5407 | 3.357 | +5.47% | DECISIÓN013, patrón conocido |
| CV | 0.6302 | 0.63 | ~0% | PASS |

**Sin discrepancia de datos base y sin ninguna ambigüedad de partición**
— n=38 es par, así que no aplica la discrepancia floor/ceil de partición
de t-Student que sí afectó a est_03/est_05 (n impares). La estación más
limpia de las 6 auditadas hasta ahora en Etapa 1.

**Independencia** — Anderson: k_max=ceil(38/3)=13, 0/13 lags fuera →
aprobada, coincide con "0 puntos fuera cumple idealmente con el límite
admisible de 1.3" de la tesis. Wald-Wolfowitz reconstruido a mano: METIS
n1=16, n2=22, R=13, Z=-2.2031 — **coincide exacto con la tesis** (n1=16,
n2=22, R=13, Z=-2.20). Rechaza a α=0.05, se acepta por tolerancia a
α=0.01 en ambos. Nivel de independencia: `independiente` en ambos — PASS
total.

**Homogeneidad** — Helmert: S=25, C=12, S-C=13 — **coincide exacto con la
tesis**, rechaza en ambos (13 > 6.08). t-Student: METIS 0.80746 (n1=n2=19,
sin ambigüedad de partición al ser n par) vs tesis 0.81 — diff -0.31%,
esencialmente exacto. Cramer reconstruido a mano: τ1=-0.06595 (n_w1=23),
τ2=-0.19924 (n_w2=11, `round(38×0.30)=11` — coincide sin ambigüedad con
tesis, a diferencia de est_05) — **coincide exacto con la tesis en los 4
valores** (τ1, τ2, tw1=0.49163, tw2=0.76928). Nivel de homogeneidad:
`homogeneidad_warning` en METIS (Helmert rechaza, resto aprueba) —
coincide en sustancia con "Serie Homogénea (Aprobada por mayoría)" de la
tesis.

**Veredicto general Etapa 1: Habilitada para Etapa 2, en ambos.
Aprobado, sin ninguna discrepancia puntual** — ni siquiera las ya
conocidas de otras estaciones (partición t-Student, n_w2 de Cramer)
aparecen acá, porque n=38 no genera la ambigüedad de redondeo que sí
afecta a n impares.

**Tendencia y atípicos** (sin referencia de tesis): Mann-Kendall aprueba
(Z=-0.365), KS aprueba (Z=0.649), Chow aprueba (1.8194 < K_N=2.8463). Sin
hallazgos.

---

### 2. Etapa 2 — cableado completo (34/34, extiende Gamma 2p de Fase 2)

**13/13 distribuciones, 34/34 combinaciones distribución×método
verificadas — 0 hallazgos de cableado.** Corrido con el fix de
`gamma3p.py::mv` (DECISIÓN 023) ya aplicado.

`gamma3p`/mv sigue dando `no_converge` — **reverificado en esta sesión
con el código corregido (escaneo denso + validación) que sigue sin haber
raíz genuina en el dominio para esta serie**: evaluando IV-140/141
directo con x0=5.241 (el valor que reporta la propia tesis) se obtiene
β=2.7357, α=14.2352 — no coincide con lo que la tesis reporta para su
propia solución (β=2.129, α=15.612). Este es el hallazgo original de
`pendientes-facundo.md` para est_06 (no el que se corrigió para est_05
— ver `est_05-e2e.md` — acá sí hay parámetros de tesis reportados contra
los cuales evaluar, y siguen sin satisfacer el sistema).

`logpearson3`/mv **converge** (β=3.6950, α=0.3225, y0=2.4205,
EEA=10.9881) donde la tesis reporta NO_CONVERGE — comportamiento ya
verificado y documentado en DECISIÓN 019: es una raíz genuina, confirmada
con el sistema literal (digamma exacto, sin la sustitución de Thom) en
una sesión anterior — no es falsa convergencia de borde. Reconfirmado
acá, sin novedad.

---

### 3. Etapa 2 — parámetros y EEA, comparación completa contra tesis

| Distribución | Método | Param. | METIS | Tesis | diff% |
|---|---|---|---|---|---|
| Uniforme | Momentos | α, β, EEA | -4.0447 / 92.4131 / 10.9200 | -4.04 / 92.41 / 10.92 | ~0% |
| Uniforme | MV | α, β, EEA | 14.00 / 109.00 / 20.8429 | igual | 0% |
| Exponencial β | Mom/MV | β, EEA | 0.022633 / 12.5535 | 0.023 / 12.5535 | -1.6% (redondeo tesis) / ~0% |
| Exponencial x0β | Momentos | x0, β, EEA | 16.339 / 27.845 / 6.4958 | 16.34 / 27.84 / 6.4958 | ~0% |
| Exponencial x0β | MV | x0, β, EEA | 13.184 / 31.00 / **5.7364** | 13.18 / 31.00 / **5.7364** | **~0% — modelo seleccionado, PASS total** |
| Gen. Exponencial | Momentos | α, λ | 3.0788 / 0.041993 | 2.15 / 0.0128 | +43.2% / +228.1% |
| Gen. Exponencial | MV | α, λ, EEA | 3.8569 / 0.046915 / 7.7134 | 3.86 / 0.0469 / 7.7134 | ~0% |
| Gen. Exponencial | ML | α, λ | 0.4025 / -0.014396 | 0.78 / -0.0111 | -48.4% / +29.7% (pendiente IV-84) |
| Normal | Mom/MV | µ, σ, EEA | 44.184 / 27.845 / 10.5274 | 44.18 / 27.845 / 10.5 | ~0% / +0.26% |
| Normal | ML | σ, EEA | 26.6745 / 10.5791 | 26.6745 / 10.6605 | 0% / -0.76% |
| Log-Normal 2p | Mom/MV | µy, σy, EEA | 3.6120 / 0.5932 / 6.9098 | 3.61 / 0.593 / 7.4379 | ~0% / -7.10% (tesis SÍ reporta EEA acá, a diferencia de est_02-05) |
| Log-Normal 3p | Momentos | x0, µy, σy, EEA | -31.758/4.2669/0.3552/7.1582 | -34.62/4.3081/0.343/7.6639 | Causa A / -6.60% |
| Log-Normal 3p | MV | x0, µy, σy | 11.654 / 3.0942 / 0.9308 | 11.65 / 3.0942 / 0.9308 | **~0% los 3** |
| Log-Normal 3p | MV | EEA | 8.7361 | 7.2038 | **+21.27% — Causa C** |
| Gamma 2p | Momentos | α, β, EEA | 17.548 / 2.5179 / 6.4601 | 17.55 / 2.518 / 6.9649 | ~0% / -7.25% |
| Gamma 2p | MV | α, β, EEA | 14.764 / 2.9928 / 7.5201 | 14.76 / 2.993 / 8.1993 | ~0% / -8.28% |
| Gamma 2p | ML | α, β, EEA | 17.808 / 2.4811 / 6.3883 | 17.81 / 2.481 / 6.8694 | ~0% / -7.00% |
| Gamma 3p | Momentos | x0, α, β, EEA | -4.273/16.001/3.0284/6.7370 | -6.25/15.373/3.281/7.2912 | Causa A / -7.60% |
| Gamma 3p | MV | — | NO_CONVERGE | x0=5.241, α=15.612, β=2.129, EEA=10.6842 | sin raíz en el dominio, params de tesis no satisfacen IV-140/141 evaluados directo (§2) |
| Gamma 3p | MPP | — | EXCLUIDO (no implementado) | x0=11.81, α=30.244, β=1.07, EEA=5.7459 | pendiente de código ya conocido |
| Gumbel | los 4 métodos | α, µ, EEA | ver tabla — **PASS total, ≤0.01% en los 4 métodos** | igual | 0% |
| GVE | Momentos | ν, α, β, EEA | 43794.15 / 21.683 / -0.000991 / 45598.69 | 35.214 / 17.943 / -0.416 / **26.8594** | β degenerado (≈0) — no reproducible con IV-203/204 |
| GVE | MV | ν, α, β, EEA | 27.675 / 13.505 / -0.5307 / 13.5981 | 27.675 / 13.505 / -0.531 / 13.5981 | **~0% los 4 — PASS exacto** |
| GVE | ML | β | -0.2024 | -0.202 | ~0.17% (casi exacto) |
| GVE | ML | α, ν, EEA | 17.337 / 29.886 / 7.2873 | **21.841 / 52.147 / 26.2049** | -20.62% / -42.68% / -72.19% — mismo patrón GVE-ML, 6ª estación consecutiva |
| LP3 | Directo | — | NO_APLICABLE (B=2.697 ∉ (3,6]) | α=0.333, β=0.259, y0=3.683, EEA=23.9915 | METIS aplica correctamente la restricción IV-249 |
| LP3 | Indirecto | α, β, y0 | 0.1045 / 32.257 / 0.2427 | 0.100 / 34.943 / 0.105 | +4.45% / -7.69% / +131% (y0 cerca de 0, % sensible) — Causa A |
| LP3 | Indirecto | EEA | 7.2840 | 7.2097 | +1.03% |
| LP3 | MV | α, β, y0, EEA | 0.3225 / 3.6950 / 2.4205 / 10.9881 | NO_CONVERGE | METIS converge — raíz genuina verificada, DECISIÓN 019 |

---

### 4. Hallazgos relevantes — con causa e implicancia

**A. Modelo seleccionado (Exponencial x0β MV) — PASS total, incluidos los
7 cuantiles de diseño.** β=31.00 y x0=13.18 coinciden exacto con la
tesis; EEA=5.7364 coincide exacto; los 7 cuantiles de diseño (T=2 a 100)
con diff ≤0.005% en todos los casos. **Segunda estación, después de
est_02, donde el ciclo completo — parámetros, EEA, selección de modelo y
cuantiles de diseño — cierra sin ningún pendiente.**

**B. GVE MV — PASS exacto en los 4 valores, tercera estación consecutiva
con este resultado** (después de est_04 y est_05). Refuerza que, cuando
el método converge a la misma solución, el sistema es indistinguible del
Excel de Facundo.

**C. Gumbel — PASS perfecto en los 4 métodos, cuarta estación consecutiva**
(est_03, est_04, est_05, est_06).

**D. Log-Pearson III MV converge en METIS donde la tesis reporta
NO_CONVERGE — comportamiento ya verificado como raíz genuina, no falsa
convergencia.** Ya documentado en DECISIÓN 019/pendientes-facundo.md: el
sistema literal (digamma exacto) confirma la misma raíz que encuentra la
aproximación de Thom, hasta la tercera cifra decimal — la tesis no
encontró una solución que sí existe y es alcanzable. Reconfirmado sin
novedad en esta sesión.

**E. Log-Normal 3p MV — Causa C reconfirmada, sin llegar a invertir el
ranking (a diferencia de est_05).** Los 3 parámetros coinciden con la
tesis a menos de 0.03% — el mismo punto exacto en el espacio de
parámetros. El EEA diverge +21.27% (METIS=8.7361 vs tesis=7.2038). A
diferencia de est_05, acá esta distribución no es la seleccionada por
Facundo (que eligió Exp x0β MV, con EEA muy inferior, 5.7364) ni la
segunda mejor en la tabla de tesis — así que la divergencia de Causa C no
tiene consecuencia sobre qué modelo vería el usuario experto como mejor
opción en esta estación. Mismo patrón, distinta severidad práctica.

**F. GVE Momentos-L — sexta estación consecutiva con el mismo síntoma
exacto.** β=-0.2024 (METIS) vs -0.202 (tesis, diff +0.17%, casi
idéntico); α=17.34 vs 21.84 (-20.6%), ν=29.89 vs 52.15 (-42.7%). Con seis
de seis estaciones auditadas en esta sesión mostrando el mismo patrón sin
excepción (est_01 a est_06), sigue siendo el hallazgo transversal de
mayor prioridad para escalar a Facundo.

**G. Generalizada Exponencial Momentos — parámetros de tesis
inconsistentes con el CV de su propia serie, reconfirmado.**
CV_datos=0.63020. Con α=3.0788 (METIS) el CV teórico coincide exacto. Con
α=2.15 (tesis) el CV teórico da 0.72405 — diff +14.9% respecto del CV
real. Mismo patrón ya visto en las 5 estaciones anteriores.

**H. GVE Momentos — β degenerado (≈-0.001), no reproducible con
IV-203/204.** Mismo pendiente Facundo ya documentado extensamente para
esta combinación en todas las estaciones auditadas — sin novedad.

---

### 5. Selección de modelo y cuantiles

**Modelo ganador de Facundo — Exponencial x0β MV, EEA tesis=5.7364, EEA
METIS=5.7364 (PASS exacto).** Cuantiles PASS 7/7, diff ≤0.005% en todos
los T.

**Testigo de tesis — Gamma 3p MPP, EEA=5.7459 (segundo lugar, casi
empatado con el ganador).** EXCLUIDO en METIS por falta de fórmula fuente
— mismo pendiente de código ya conocido a nivel de todo el proyecto, sin
comparación posible para este testigo puntual.

---

### 6. Clasificación final est_06

| Columna | Resultado |
|---|---|
| **Etapa 1** | **Aprobado**, sin ninguna reserva — la estación más limpia de las 6 auditadas en Etapa 1 (n par, sin ambigüedad de partición). |
| **Cableado (13 dist.)** | **Aprobado** — 34/34 combinaciones distribución×método, reconstrucción propia completa, 0 hallazgos. Corrido con el fix de `gamma3p.py::mv` ya aplicado — comportamiento correcto (no_converge genuino, reverificado). |
| **Selección de modelo** | **Aprobado** — el modelo ganador de Facundo (Exponencial x0β MV) coincide exacto en parámetros y EEA. |
| **Cuantiles** | **Aprobado** — 7/7 con diff ≤0.005%. Testigo (Gamma3p MPP) sin comparación posible por falta de implementación. |

**Clasificación general de la estación: Aprobado.** Segunda estación,
después de est_02, donde el ciclo completo (Etapa 1 → cableado →
selección de modelo → cuantiles) cierra sin ningún Pendiente de código ni
Pendiente de dominio en la ruta que efectivamente usaría un usuario
experto. Los hallazgos de Causa A/C/GVE-ML que sí aparecen están todos en
distribuciones/métodos que no son el modelo ganador — relevantes para el
informe integral, no bloquean la operación del sistema para esta
estación. **Ningún hallazgo de esta ronda requiere modificar código de
`metis/core/` — no se aplicó ni se propone ningún cambio.**
