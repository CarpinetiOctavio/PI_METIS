## est_05 — Piedra Blanca – Río Piedra Blanca — Análisis E2E desde cero (14/07/2026)

Detalle completo del análisis Fase 4 (regresión E2E) para esta estación.
Índice y tabla de consolidación de las 9 estaciones: `fase4-e2e.md`.

**Nota de encuadre:** est_05 tenía Etapa 1 y (des)selección de modelo ya
señaladas en rondas anteriores (Causa C invierte el orden del ranking
entre el modelo elegido por Facundo y el mejor numérico de METIS), pero
cableado incompleto — solo Gamma 2p reconstruido. Se rehizo íntegro desde
cero, con el código ya incluyendo el fix de `gamma3p.py::mv` (DECISIÓN
023) aplicado en la ronda de est_04.

### Método y alcance

Mismo método que est_01-04. Los documentos previos
(`est_05_piedra_blanca_rioPiedraBlanca-pipeline.md`,
`est_05_piedra_blanca_rioPiedraBlanca-unitarias.md`) se usaron solo como
fuente de la serie y de los valores de referencia de la tesis.

---

### 1. Etapa 1 — reconstrucción completa

Las 5 pruebas se reconstruyeron a mano de forma independiente y coinciden
**exacto** con la salida del pipeline.

| Variable | METIS | Tesis | diff% | Nivel |
|---|---|---|---|---|
| n | 39 | 39 | 0.00% | PASS |
| Media | 44.4667 | 44.466 | ~0% | PASS |
| Varianza (no sesgada) | 2099.5839 | 2099.627 | ~0% | PASS |
| Desvío | 45.8212 | 45.822 | ~0% | PASS |
| M0/M1/M2/M3 | 44.467/33.925/27.853/23.871 | 44.466/33.925/27.853/23.871 | ~0% | PASS |
| Suma ln(xi) | 122.4874 | 122.485 | ~0% | PASS |
| Máximo/Mínimo | 215.0 / 0.9 | 215.0 / 1.0* | ~0% | PASS |
| Asimetría no sesgada (g) | 1.9114 | 1.838 | +3.99% | DECISIÓN013, patrón conocido |
| Curtosis no sesgada (k) | 7.6370 | 7.25 | +5.34% | DECISIÓN013, patrón conocido |
| CV | 1.0305 | 1.03 | ~0% | PASS |

\* mínimo real de la serie es 0.9 (año 69-70); la tesis muestra 1.0 en la
tabla de estadística descriptiva (redondeo de display, ya documentado en
rondas anteriores) — verificado que 0.9 reproduce media/suma_log
correctamente, no es un error de transcripción.

**Sin discrepancia de datos base** — mismo patrón limpio que est_02/03/04.

**Independencia** — Anderson: k_max=ceil(39/3)=13, 0/13 lags fuera →
aprobada, coincide con "0 puntos fuera, comportamiento óptimo" de la
tesis (la tesis usa k_adoptado=14 en su propio texto, con la misma
ambigüedad de redondeo ya señalada para n=39 en Fase 1 — no cambia el
resultado: 0 lags fuera con cualquiera de los dos). Wald-Wolfowitz
reconstruido a mano: METIS n1=14, n2=25, R=20, Z=0.3716 — **coincide
exacto con la tesis** (n1=14, n2=25, R=20, Z=0.37). Nivel de
independencia: `independiente` en ambos — PASS total.

**Homogeneidad** — Helmert: S=19, C=19, S-C=0 — **coincide exacto con la
tesis**. t-Student: METIS 1.8172 (partición floor, n1=19/n2=20) vs tesis
2.08 (partición ceil, n1=20/n2=19) — **misma discrepancia de convención ya
documentada para n impar en `fase2-cableado.md`** ("est_03, est_05: METIS
usa floor(n/2), tesis usa ceil(n/2)"). Consecuencia real en esta
estación: con la partición de METIS, t-Student **aprueba** (1.8172 <
2.0262); con la partición de tesis, t-Student **rechaza** (2.08 > 2.0262)
— la tesis lo señala explícitamente como "rechazo marginal" y aprueba la
homogeneidad igual por mayoría (Cramer + Helmert). METIS llega al mismo
veredicto final por unanimidad en vez de por mayoría — no cambia la
conclusión, reconfirma la discrepancia ya conocida con números frescos.
Cramer reconstruido a mano: τ1=-0.16141 (n_w1=24, coincide con tesis
-0.16143), τ2=-0.31845 (n_w2=12, METIS usa `round(39×0.30)=12`; tesis usa
13 — **DECISIÓN011 ya documentada como pendiente para esta estación
puntual**: "est_05... n×0.30=11.7 → round=12, pero Facundo usó 13").
tw1=1.26861 (~tesis 1.2688), tw2=1.32149 (n_w2=12, tesis 1.49884 con
n_w2=13) — ambos aprueban en los dos casos. Nivel de homogeneidad:
`homogeneidad_ok` en METIS (unanimidad) vs "Serie Homogénea (Aprobada por
desempate)" en tesis (t-Student rechaza, Cramer+Helmert aprueban) — mismo
resultado práctico.

**Veredicto general Etapa 1: Habilitada para Etapa 2, en ambos. Aprobado**
— las dos discrepancias puntuales (partición t-Student, n_w2 de Cramer)
ya estaban documentadas como pendientes conocidos para esta estación
específica desde rondas anteriores; no son hallazgos nuevos, se
reconfirman con reconstrucción fresca.

**Tendencia y atípicos** (sin referencia de tesis): Mann-Kendall aprueba
(Z=-0.956), KS aprueba (Z=0.871), Chow aprueba (2.3524 < K_N=2.8571). Sin
hallazgos.

---

### 2. Etapa 2 — cableado completo (34/34, extiende Gamma 2p de Fase 2)

**13/13 distribuciones, 34/34 combinaciones distribución×método
verificadas — 0 hallazgos de cableado.** Corrido con el código ya
incluyendo el fix de `gamma3p.py::mv` (DECISIÓN 023). `gamma3p`/mv sigue
dando `no_converge` para est_05 — **comportamiento correcto, verificado
en esta sesión con escaneo fino de 200.000 puntos sobre todo el dominio
de búsqueda** (`lo≈-915.52` a `hi≈0.9`): el residuo de IV-142 es negativo
y monótonamente decreciente en magnitud en **todo** el dominio, sin un
solo cambio de signo — no existe raíz interior para esta serie
particular. **Corrección respecto de una nota previa de
`pendientes-facundo.md`:** esa nota decía "los parámetros de tesis no
satisfacen IV-140/141" para est_05, calcada de la redacción de est_06 —
pero la ficha de tesis para est_05 marca esta combinación como
**NO_APLICABLE**, sin ningún x0/α/β reportado, así que no hay parámetros
de tesis contra los cuales evaluar nada. La explicación correcta es que
el perfil de verosimilitud no tiene mínimo interior en el dominio para
esta serie — no que una solución reportada por la tesis falle al
verificarse. Consistente con que la propia tesis marque NO_APLICABLE (no
NO_CONVERGE con valores, como si tuviera una solución candidata que
rechazó): Facundo y METIS llegan al mismo resultado práctico por el mismo
motivo matemático genuino. Corregido también en `pendientes-facundo.md`.
No es el mismo tipo de caso que se corrigió para est_04 (acá no hay raíz
que encontrar en absoluto, con o sin escaneo denso).

---

### 3. Etapa 2 — parámetros y EEA, comparación completa contra tesis

| Distribución | Método | Param. | METIS | Tesis | diff% |
|---|---|---|---|---|---|
| Uniforme | Momentos | α, β, EEA | -34.898 / 123.831 / 23.2826 | -34.90 / 123.83 / 23.2824 | ~0% |
| Uniforme | MV | α, β, EEA | 0.90 / 215.00 / 72.2232 | 0.91* / 215.00 / 72.2272 | -1.10%* / 0% / ~0% |
| Exponencial β | Mom/MV | β, EEA | 0.022489 / 9.4244 | 0.022 / 9.4250 | +2.22% (redondeo tesis) / ~0% |
| Exponencial x0β | Momentos | x0, β, EEA | -1.3546 / 45.8212 / 8.7670 | -1.36 / 45.82 / 8.7670 | ~0% |
| Exponencial x0β | MV | x0, β, EEA | -0.2465 / 44.7132 / 9.4018 | -0.24 / 44.70 / 9.4085 | ~0% (valores chicos, % sensible) |
| Gen. Exponencial | Momentos | α, λ | 0.9347 / 0.021522 | 0.91 / 0.0301 | +2.71% / -28.5% |
| Gen. Exponencial | MV | α, λ, EEA | 0.8796 / 0.020810 / 8.1182 | 0.89 / 0.0208 / 8.1179 | ~0% |
| Gen. Exponencial | ML | α, λ | 0.2377 / -0.018431 | 0.82 / -0.0097 | -71.02% / +90.02% (pendiente IV-84) |
| Normal | Mom/MV | µ, σ, EEA | 44.467 / 45.821 / 20.2873 | 44.47 / 45.8217 / 20.5769 | ~0% / -1.41% |
| Normal | ML | σ, EEA | 41.4356 / 20.4142 | 41.4363 / 20.9960 | ~0% / -2.77% |
| Log-Normal 2p | Mom/MV | µy, σy, EEA | 3.1407 / 1.3799 / 27.1902 | 3.14 / 1.380 / **NO_APLICABLE** | ~0%; tesis no aplica (mismo patrón est_02/03/04) |
| Log-Normal 3p | Momentos | x0, µy, σy, EEA | -35.352/4.2373/0.5337/10.4932 | -38.01/4.2780/0.5187/13.3677 | -7.0%/-0.95%/+2.90% (Causa A) / -21.5% |
| Log-Normal 3p | MV | x0, µy, σy | -2.1576 / 3.3327 / 1.1133 | -2.15 / 3.3323 / 1.1137 | **~0% los 3** |
| Log-Normal 3p | MV | EEA | 8.7739 | 5.7842 | **+51.65% — Causa D, ver hallazgo A** |
| Gamma 2p | Momentos | α, β, EEA | 47.217 / 0.9418 / 8.9581 | 47.22 / 0.942 / 12.0855 | ~0% / -25.87% |
| Gamma 2p | MV | α, β, EEA | 49.122 / 0.9052 / 8.4314 | 49.12 / 0.905 / 11.6154 | ~0% / -27.41% |
| Gamma 2p | ML | α, β, EEA | 50.786 / 0.8756 / 8.0077 | 50.79 / 0.876 / 11.2310 | ~0% / -28.71% |
| Gamma 3p | Momentos | x0, α, β, EEA | -3.479/43.791/1.0949/9.2217 | -5.387/42.117/1.184/12.3058 | Causa A / -25.06% |
| Gamma 3p | MV | — | NO_CONVERGE | NO_APLICABLE (sin params reportados) | mismo resultado práctico — ver §2, sin raíz interior en todo el dominio, no "params de tesis que fallan" |
| Gamma 3p | MPP | — | EXCLUIDO (no implementado) | x0=-1.368, α=54.585, β=0.840, EEA=10.2359 | pendiente de código ya conocido |
| Gumbel | los 4 métodos | α, µ, EEA | ver tabla — **PASS total, ≤0.01% en los 4 métodos** | igual | 0% |
| GVE | Momentos | ν, α, β, EEA | 695.24 / 30.822 / -0.0979 / 697.54 | 25.367 / 20.529 / -0.032 / **41.3296** | +2641% / +50.1% / +206% / +1588% |
| GVE | MV | ν, α, β, EEA | 19.579 / 21.386 / -0.4777 / 6.3250 | 19.578 / 21.386 / -0.478 / 6.3279 | **~0% los 4 — PASS exacto** |
| GVE | ML | β | -0.2543 | -0.254 | ~0.12% (casi exacto) |
| GVE | ML | α, ν, EEA | 25.057 / 21.688 / 9.0127 | **33.307 / 54.129 / 38.2840** | -24.76% / -59.93% / -76.46% — mismo patrón GVE-ML |
| LP3 | Directo | — | NO_APLICABLE (B=2.514 ∉ (3,6]) | α=0.333, β=0.562, y0=3.567, EEA=37.7133 | METIS aplica correctamente la restricción IV-249 |
| LP3 | Indirecto | α, β, y0 | 0.5572 / 6.1327 / -0.2765 | 0.536 / 6.639 / -0.415 | +3.96% / -7.62% / -33.4% (Causa A) |
| LP3 | Indirecto | EEA | 64.6816 | 36.5529 | +76.98% |
| LP3 | MV | — | NO_CONVERGE | NO_CONVERGE | **coincide exacto** |

\* Uniforme MV α: tesis redondea min(serie) a 0.91 en la tabla de
parámetros; el mínimo real es 0.9 — mismo tipo de redondeo de display que
el mínimo de la estadística descriptiva. El EEA (calculado con el valor
real 0.9 en ambos lados) coincide casi exacto, confirmando que es un
problema de redondeo de la tabla, no de cálculo.

---

### 4. Hallazgos relevantes — con causa e implicancia

**A. Log-Normal 3p MV — Causa D confirmada: parámetros casi idénticos,
pero la divergencia de EEA es suficiente para invertir el orden del
ranking entre el modelo que Facundo eligió y el mejor numérico de
METIS.** Los 3 parámetros coinciden con la tesis a menos de 0.4% (x0,
µy, σy) — prácticamente el mismo punto en el espacio de parámetros, igual
que el caso ya visto en est_02 (hallazgo B de esa estación). Pero el EEA
diverge +51.65% (METIS=8.7739 vs tesis=5.7842) y los cuantiles degradan
con T de forma creciente: PASS en T=2 (+0.03%) hasta **+38.32% en
T=100**.

Esto tiene una consecuencia que no tenía est_02: **en la tabla de tesis,
LN3p MV (EEA=5.7842) es el modelo con el EEA más bajo — el que Facundo
efectivamente seleccionó como ganador.** GVE MV queda segundo, muy cerca
(EEA=6.3279). En el ranking que produce METIS, GVE MV (EEA=6.3250,
prácticamente idéntico a tesis) pasa a ser el mejor, porque el EEA de
LN3p MV se infla a 8.7739 por la misma Causa C que ya se documentó en
otras estaciones — **la diferencia entre las dos distribuciones (que en
la tesis es un margen angosto, 5.7842 vs 6.3279) se invierte por
completo en METIS.** Un usuario experto que confíe en el ranking de
METIS para esta estación vería a GVE MV como la mejor opción, no a LN3p
MV — una selección distinta de la que hizo Facundo, no por un error de
METIS en sí (los parámetros de LN3p MV son correctos, verificados) sino
por la misma limitación de "Causa C" (fórmula documentada + parámetros
correctos no reproducen la tabla de tesis) que aparece en toda la
auditoría, acá con consecuencia directa sobre cuál sería la distribución
recomendada.

**Test de aislamiento Causa A vs Causa C — ejecutado con las funciones
reales `lognormal3p.cuantil()` y `calcular_eea()` (no reconstrucción
manual), mismo protocolo que est_03/LP3 Indirecto.** Se llamaron las
funciones reales inyectando los tres parámetros propios de la tesis
(x0=-2.15, µy=3.3323, σy=1.1137) en vez de los ajustados por METIS:

| T | Cuantil con params. de tesis (función real) | Tabla de tesis | diff% |
|---|---|---|---|
| 2 | 25.85 | 25.85 | +0.01% |
| 5 | 69.33 | 68.33 | +1.47% |
| 10 | 114.57 | 109.40 | +4.72% |
| 20 | 172.81 | 156.26 | +10.59% |
| 25 | 194.71 | 172.05 | +13.17% |
| 50 | 273.75 | 221.43 | +23.63% |
| 100 | 371.62 | 268.51 | **+38.40%** |

Comparado contra el resultado con los parámetros propios de METIS
(T=100: +38.32%), la diferencia es de solo **0.08 puntos porcentuales**
— prácticamente toda la divergencia persiste usando los parámetros
exactos de la tesis. **Proporción: ~99.8% Causa C, ~0.2% Causa A** — más
extremo incluso que el ~95%/5% ya cuantificado para LP3 Indirecto en
est_03 (mismo protocolo). Coincide con la estimación manual previa
(~+38.33%), por lo que se descarta que sea un hallazgo de cableado nuevo
en `lognormal3p.py::cuantil`.

**EEA con los parámetros exactos de tesis (función real
`calcular_eea()`):** 8.7924 — prácticamente igual al EEA con parámetros
de METIS (8.7739), y lejos del 5.7842 que reporta la tesis para este
método. **Esto confirma que el ranking no se resolvería a favor de LN3p
MV ni siquiera si METIS usara los parámetros exactos de Facundo** — la
inversión de ranking (Causa D) es consecuencia casi pura de la Causa C en
el cálculo del EEA/cuantil, no de una diferencia de ajuste de parámetros.

**Clasificación: Pendiente de dominio — Causa D, con Causa C dominante al
~99.8%** (Causa C con impacto en el ranking expuesto al usuario experto),
formalmente definida en `fase4-e2e.md`. Ya estaba señalada como sospecha
en una ronda anterior — esta sesión la reconstruye desde cero con
verificación completa (parámetros, EEA, los 7 cuantiles, y ahora el test
de aislamiento cuantificado) y la confirma sin ambigüedad.

**Contraverificación cruzada (Chat, 14/07/2026):** el test de aislamiento
se corrió por dos vías independientes — reconstrucción manual (Chat,
T=100≈+38.33%) y función real del código (Code, `lognormal3p.cuantil()` +
`calcular_eea()`, T=100=+38.401%) — con resultado coincidente en
dirección y magnitud (diferencia atribuible solo a redondeo de la
reconstrucción manual). El dato del EEA con parámetros exactos de tesis
(8.7924, lejos de 5.7842) es el que cierra la duda de fondo: **el ranking
no podría resolverse a favor de LN3p MV con mejores parámetros, porque ni
los parámetros exactos de Facundo reproducen el EEA que la propia tesis
reporta para su propio método.** Con doble vía independiente de
verificación y sin ambigüedad de atribución de causa (~99.8% Causa C, no
una mezcla incierta), este es el hallazgo de Causa D con el nivel de
rigor más alto confirmado en todo el proyecto hasta ahora.

**B. GVE MV — PASS exacto en los 4 valores (ν, α, β, EEA), y sus
cuantiles de diseño reproducen la tabla de tesis con diff ≤0.02% en los 7
períodos de retorno.** Tercera estación consecutiva (después de est_03 y
est_04) con GVE MV completamente limpio — refuerza que, cuando el método
converge a la misma solución, el sistema es indistinguible del Excel de
Facundo.

**C. Gumbel — PASS perfecto en los 4 métodos, tercera estación
consecutiva.** Mismo resultado que est_03 y est_04 — Momentos, MV, ML y
ME con diff ≤0.01% en parámetros y EEA.

**D. GVE Momentos-L — mismo patrón (β cerca, ν/α lejos), reconfirmado
otra vez.** β=-0.2543 (METIS) vs -0.254 (tesis, diff +0.12%, casi
idéntico); α=25.06 vs 33.31 (-24.8%), ν=21.69 vs 54.13 (-59.9%). Con esta
estación son ya 5 de las 5 con Etapa 2 completa auditadas en esta sesión
(est_01 a est_05) mostrando el mismo síntoma exacto, sin una sola
excepción, más est_06 (ronda previa, no Fase 4 completa) — sigue siendo
el hallazgo de mayor prioridad de consulta a Facundo del proyecto.

**E. Generalizada Exponencial Momentos — parámetros de tesis
moderadamente inconsistentes con el CV de la serie (mismo patrón, pero
con la menor magnitud vista hasta ahora).** CV_datos=1.03046. Con
α=0.9347 (METIS) el CV teórico coincide exacto (1.03046). Con α=0.91
(tesis) el CV teórico da 1.04287 — diff solo +1.2% (mucho menor que el
8-15% típico en otras estaciones). METIS sigue siendo el matemáticamente
consistente, pero acá el valor de tesis está más cerca de ser plausible
que en el resto del dataset — vale la pena anotarlo como matiz, no
cambia la conclusión de fondo.

---

### 5. Selección de modelo y cuantiles

**Modelo ganador de Facundo — Log-Normal 3p MV, EEA tesis=5.7842, EEA
METIS=8.7739 (+51.65%).** Implementado, converge, parámetros casi
idénticos. Cuantiles: PASS en T=2, degrada a +38.32% en T=100 (hallazgo A).
**A diferencia de est_04 (sin comparación posible) y de est_03 (modelo
seleccionado con Causa A+C pero orden de ranking no afectado), acá la
Causa C tiene magnitud suficiente para invertir cuál sería la
distribución recomendada — Causa D.**

**Testigo — GVE MV, EEA tesis=6.3279, EEA METIS=6.3250 (PASS exacto).**
Cuantiles PASS 7/7, diff ≤0.02%.

---

### 6. Clasificación final est_05

| Columna | Resultado |
|---|---|
| **Etapa 1** | **Aprobado** — las dos discrepancias puntuales (partición t-Student para n impar, n_w2 de Cramer) son pendientes ya documentados específicamente para esta estación desde rondas anteriores, reconfirmados con reconstrucción fresca, no son hallazgos nuevos. |
| **Cableado (13 dist.)** | **Aprobado** — 34/34 combinaciones distribución×método, reconstrucción propia completa, 0 hallazgos. Corrido con el fix de `gamma3p.py::mv` ya aplicado — comportamiento correcto (no_converge genuino, sin raíz en el dominio). |
| **Selección de modelo** | **Pendiente de dominio — Causa D** — el modelo ganador de Facundo (LN3p MV) tiene parámetros casi idénticos en METIS pero un EEA suficientemente distinto como para que el ranking de METIS recomendaría GVE MV en su lugar. |
| **Cuantiles** | Modelo seleccionado degrada con T (hasta +38.32% en T=100, cuantificado con test de aislamiento: ~99.8% Causa C / ~0.2% Causa A); testigo (GVE MV) PASS exacto 7/7. |

**Clasificación general de la estación: Parcial.** Etapa 1 y cableado
**Aprobados** sin reservas nuevas. Selección de modelo con **Pendiente de
dominio — Causa D**, la clasificación de mayor severidad práctica del
framework (afecta directamente cuál sería la distribución recomendada al
usuario experto), confirmada con verificación completa por primera vez en
esta ronda de Fase 4. **Ningún hallazgo de esta ronda requiere modificar
código de `metis/core/` — no se aplicó ni se propone ningún cambio.**
