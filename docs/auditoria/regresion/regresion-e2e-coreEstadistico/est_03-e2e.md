## est_03 — La Tapa – Río Las Cañitas — Análisis E2E desde cero (14/07/2026)

Detalle completo del análisis Fase 4 (regresión E2E) para esta estación.
Índice y tabla de consolidación de las 9 estaciones: `fase4-e2e.md`.

**Nota de encuadre:** est_03 tenía Etapa 1 y selección de modelo ya
resueltas en rondas anteriores (Fase 1/2), pero cableado incompleto — solo
Gamma 2p (3 métodos) reconstruido en profundidad, no las 34/34. Se rehizo
íntegro sin asumir nada de lo escrito antes, mismo criterio que est_01 y
est_02.

### Método y alcance

Mismo método que est_01/02: `ejecutar_etapa1()` + `ejecutar_etapa2()` en
vivo contra el working tree actual, con reconstrucción manual/aislada de
cada estadístico y cada una de las 13 distribuciones × sus métodos. Los
documentos previos (`est_03_la_tapa_rioLasCanitas-pipeline.md`,
`est_03_la_tapa_rioLasCanitas-unitarias.md`) se usaron solo como fuente de
la serie y de los valores de referencia de la tesis.

---

### 1. Etapa 1 — reconstrucción completa

Las 5 pruebas (Anderson lag por lag, Wald-Wolfowitz, Helmert secuencia por
secuencia, t-Student, Cramer) se reconstruyeron a mano de forma
independiente y coinciden **exacto** con la salida del pipeline — cableado
confirmado.

**Estadística descriptiva**

| Variable | METIS | Tesis | diff% | Nivel |
|---|---|---|---|---|
| n | 41 | 41 | 0.00% | PASS |
| Media | 62.3902 | 62.39 | 0.00% | PASS |
| Varianza (no sesgada) | 5963.6939 | 5963.694 | 0.00% | PASS |
| Desvío | 77.2250 | 77.225 | 0.00% | PASS |
| M0/M1/M2/M3 | 62.390/47.228/39.513/34.707 | 62.39/47.228/39.513/34.707 | ~0% | PASS |
| Suma ln(xi) | 149.2283 | 149.228 | 0.00% | PASS |
| Máximo/Mínimo | 402.0 / 2.0 | 402.0 / 2.0 | 0.00% | PASS |
| Asimetría no sesgada (g) | 3.2893 | 3.17 | +3.76% | DECISIÓN013, patrón conocido |
| Curtosis no sesgada (k) | 14.7437 | 14.033 | +5.07% | DECISIÓN013, patrón conocido |
| CV | 1.2378 | 1.238 | ~0% | PASS |

**Sin discrepancia de datos base** — como est_02 y a diferencia de est_01,
todos los estadísticos exactos (media, varianza, M0-M3, suma_log, min,
max) coinciden con la tesis prácticamente al dígito. Solo g/k con el diff
esperado de DECISIÓN013.

**Independencia** — Anderson: k_max=ceil(41/3)=14, 1/14 lags fuera,
umbral=ceil(14×0.10)=2 → aprobada. Coincide con "1 punto fuera... límite
admisible de 1.4" de la tesis. Wald-Wolfowitz reconstruido a mano: METIS
n1=11, n2=30, R=18, Z=0.3661 (n_efectivo=41, ningún valor coincide con la
media exacta) vs tesis n1=11, n2=29, R=18, Z=0.42 (n_efectivo=40 — la
tesis excluye un dato). **Esta discrepancia puntual (n2: 30 vs 29) ya
estaba documentada como no resuelta en `decisions-log.md` (DECISIÓN 017):
"el caso est_03 (n=40 en lugar de n=41) NO se explica por este mecanismo —
el valor excluido (35.0) no coincide con la media (62.39)"** — se
reconfirma acá con la misma conclusión, sin resolverla (no es un hallazgo
nuevo). Ambos aprueban (Z dentro de ±1.96 en los dos casos). Nivel de
independencia: `independiente` en ambos — PASS total.

**Homogeneidad** — Helmert: S=23, C=17, S-C=6 — **coincide exacto con la
tesis** (S=23, C=17, S-C=6). t-Student: 1.8751 vs tesis 1.81 (+3.6%,
dentro de tolerancia INFO). Cramer reconstruido a mano: τ1=0.04364,
τ2=-0.24246, tw1=0.34114, tw2=0.98606 — **coincide exacto con la tesis**
en los 4 valores. Nivel de homogeneidad: `homogeneidad_ok` en ambos
(unanimidad) — PASS total.

**Veredicto general Etapa 1: Habilitada para Etapa 2, en ambos. Aprobado
sin reservas** — el único punto pendiente (Wald n1/n2) ya estaba
identificado y sin resolver desde Fase 1, no es un hallazgo nuevo de esta
ronda.

**Tendencia y atípicos** (sin referencia de tesis): Mann-Kendall aprueba
(Z=-0.787), KS aprueba (Z=0.960), Chow aprueba (2.8096 < K_N=2.8777, sin
atípico — margen ajustado pero dentro). Sin hallazgos.

---

### 2. Etapa 2 — cableado completo (34/34, extiende las 3/34 de Fase 2)

**13/13 distribuciones, 34/34 combinaciones distribución×método
verificadas — 0 hallazgos de cableado.** Extiende formalmente la
verificación de Fase 2, que para est_03 solo había reconstruido Gamma 2p
(3 métodos).

Notas de comportamiento: `gamma3p`/momentos da `no_aplicable` (x0=13.664
calculado > mínimo de la serie=2.0, viola el soporte de la fórmula IV-137
a IV-139 — comportamiento correcto, ya documentado en Fase 1 §3.9 y
confirmado numéricamente en esta sesión). `gamma3p`/mv da `no_converge`.
`gen_pareto` no tiene referencia de tesis en esta estación (SKIP, mismo
patrón que est_02).

---

### 3. Etapa 2 — parámetros y EEA, comparación completa contra tesis

| Distribución | Método | Param. | METIS | Tesis | diff% |
|---|---|---|---|---|---|
| Uniforme | Momentos | α, β, EEA | -71.367 / 196.148 / 59.1524 | -71.37 / 196.15 / 59.1524 | ~0% |
| Uniforme | MV | α, β, EEA | 2.00 / 402.00 / 164.6652 | igual | 0% |
| Exponencial β | Mom/MV | β, EEA | 0.016028 / 35.1081 | 0.016 / 35.1081 | +0.18% / ~0% |
| Exponencial x0β | Momentos | x0, β, EEA | -14.835 / 77.225 / 31.8239 | -14.83 / 77.22 / 31.8239 | ~0% |
| Exponencial x0β | MV | x0, β, EEA | 0.4902 / 61.90 / 35.7549 | 0.49 / 61.90 / 35.7549 | ~0% |
| Gen. Exponencial | Momentos | α, λ | 0.6246 / 0.011607 | **0.76 / 0.0023** | **-17.81% / +404.65%** — ver hallazgo D |
| Gen. Exponencial | MV | α, λ, EEA | 1.2189 / 0.018237 / 38.5855 | 1.22 / 0.0182 / 38.5855 | ~0% |
| Gen. Exponencial | ML | α, λ | 0.2465 / -0.012965 | 0.84 / -0.0069 | -70.66% / +87.90% (pendiente IV-84) |
| Normal | Mom/MV | µ, σ, EEA | 62.390 / 77.225 / 51.6622 | 62.39 / 77.2250 / 51.9636 | ~0% / -0.58% |
| Normal | ML | σ, EEA | 56.8207 / 50.4332 | 56.8207 / 51.5105 | 0% / -2.09% |
| Log-Normal 2p | Mom/MV | µy, σy, EEA | 3.6397 / 1.0488 / 23.3473 | 3.64 / 1.049 / **NO_APLICABLE** | params ~0%; tesis no aplica esta combinación por motivo desconocido (mismo patrón est_02) |
| Log-Normal 3p | Momentos | x0, µy, σy, EEA | -25.973/4.1977/0.7533/30.3361 | -28.35/4.2355/0.7381/35.7169 | -8.38%/-0.89%/+2.05% (Causa A) / -15.07% |
| Log-Normal 3p | MV | x0, µy, σy | -3.893 / 3.7935 / 0.8703 | -3.89 / 3.7935 / 0.8703 | **~0% los 3** |
| Log-Normal 3p | MV | EEA | 33.5550 | 39.3219 | **-14.67%** — Causa C |
| Gamma 2p | Momentos | α, β, EEA | 95.587 / 0.6527 / 28.8459 | 95.59 / 0.653 / 33.6168 | ~0% / -14.19% |
| Gamma 2p | MV | α, β, EEA | 53.856 / 1.1585 / 38.2353 | 53.86 / 1.158 / 41.8453 | ~0% / -8.63% |
| Gamma 2p | ML | α, β, EEA | 67.047 / 0.9305 / 34.5658 | 67.04 / 0.931 / 38.6621 | ~0% / -10.60% |
| Gamma 3p | Momentos | — | NO_APLICABLE (x0=13.664>min=2.0) | x0=13.664, α=122.391, β=0.398, EEA=NO_APLICABLE | mismo status práctico (sin EEA) |
| Gamma 3p | MV | — | NO_CONVERGE | x0=13.664, α=41.040, β=1.187, EEA=NO_APLICABLE | mismo status práctico |
| Gamma 3p | MPP | — | EXCLUIDO (no implementado) | x0=15.00, α=124.462, β=0.381, EEA=NO_APLICABLE | mismo pendiente de código de siempre — acá sin impacto (tesis tampoco reporta EEA) |
| Gumbel | los 4 métodos | α, µ, EEA | ver tabla — **PASS total, ≤0.01% en los 4 métodos** | igual | 0% |
| GVE | Momentos | ν, α, β | 540.34 / 42.878 / -0.1935 | 45.962 / 34.657 / -0.435 | +1075.6% / +23.72% / -55.51% |
| GVE | Momentos | EEA | 529.6995 | NO_CONVERGE | METIS converge, tesis no — pendiente Facundo, mismo patrón que otras 4 estaciones |
| GVE | MV | ν, α, β, EEA | 29.917 / 25.694 / -0.4170 / 31.6660 | 29.917 / 25.694 / -0.417 / 31.6660 | **~0% los 4 — PASS exacto** |
| GVE | ML | β | -0.4596 | -0.460 | -0.09% (cercano) |
| GVE | ML | α, ν, EEA | 23.900 / 28.921 / 31.0467 | **42.412 / 69.198 / 60.5819** | -43.66% / -58.20% / -48.75% — mismo patrón GVE-ML, 5ª estación consecutiva |
| LP3 | Directo | — | NO_APLICABLE (B=2.629 ∉ (3,6]) | α=0.333, β=0.724, y0=3.840, EEA=64.3705 | METIS aplica correctamente la restricción IV-249 |
| LP3 | Indirecto | α, β, y0 | 0.2700 / 15.092 / -0.4346 | 0.260 / 16.252 / -0.588 | +3.83% / -7.14% / -26.09% |
| LP3 | Indirecto | EEA | 13.5944 | 22.6153 | -39.88% — ver hallazgo C |
| LP3 | MV | — | NO_CONVERGE | α=1.459, β=2.084, y0=0.599, EEA=NO_CONVERGE | status coincide (sin EEA en ninguno) |

---

### 4. Hallazgos relevantes — con causa e implicancia

**A. Gumbel — PASS perfecto en los 4 métodos, único caso hasta ahora en el
proyecto.** Momentos, MV, ML y ME reproducen parámetros y EEA con diff
≤0.01% en absolutamente todos los casos (ni siquiera el residuo típico de
redondeo Excel que aparece en otras estaciones). Confirma que, cuando la
serie no tiene la anomalía de datos base de est_01 ni los casos límite de
otras distribuciones, la fidelidad de Gumbel es total.

**B. GVE MV — PASS exacto en los 4 valores (ν, α, β, EEA), y sus
cuantiles de diseño (testigo) reproducen la tabla de tesis con diff
0.00% en los 7 períodos de retorno (T=2 a 100).** Es la comprobación más
limpia posible de que, cuando el método converge a la misma solución, el
sistema completo — parámetros, EEA y cuantiles — es indistinguible del
Excel de Facundo.

**C. Log-Pearson III Indirecto — modelo seleccionado por Facundo; los
cuantiles degradan con T de forma severa (hasta +54% en T=100), mismo
patrón sistémico ya visto en est_01/02 (Causa C / limitación de Excel),
acá con la magnitud más alta registrada hasta ahora.** Parámetros con diff
moderado (α +3.8%, β -7.1%, y0 -26.1% — magnitud algo mayor a lo típico de
solo g-propagación, dado que β=4/gy² con gy=asimetría de ln(x) amplifica
cualquier diferencia). EEA diverge -39.88%. Cuantiles: PASS en T=2
(-0.32%), pero crecen a +54.13% en T=100.

**Test de aislamiento Causa A vs Causa C — ejecutado con la función real
`logpearson3.cuantil()` (no reconstrucción manual), a pedido de la sesión
de contraverificación (Chat).** Se llamó a la función de cuantil real —
la misma que usa el pipeline — inyectando los tres parámetros propios de
la tesis (α=0.260, β=16.252, y0=-0.588) en vez de re-ajustar nada, y se
comparó contra la tabla de cuantiles de la tesis:

| T | Cuantil con params. de tesis (función real) | Tabla de tesis | diff% |
|---|---|---|---|
| 2 | 34.86 | 34.94 | -0.22% |
| 5 | 88.57 | 87.48 | +1.24% |
| 10 | 151.87 | 144.69 | +4.96% |
| 20 | 243.72 | 217.16 | +12.23% |
| 25 | 281.07 | 243.23 | +15.56% |
| 50 | 428.00 | 329.78 | +29.78% |
| 100 | 634.69 | 419.16 | **+51.42%** |

Comparado contra el resultado ya obtenido con los parámetros propios de
METIS (T=100: +54.13%), la diferencia entre usar un juego de parámetros u
otro es de solo **2.7 puntos porcentuales** — el error casi no se mueve al
cambiar de parámetros. **Esto cuantifica la proporción exacta: ~95% del
error total en T=100 (51.42 de 54.13 puntos) persiste usando los
parámetros exactos de la tesis en la fórmula documentada — Causa C
dominante. Solo ~5% (2.7 puntos) es atribuible a la diferencia de
parámetros — Causa A, contribución menor.** Verificado además que el
resultado de la función real (+51.42%) coincide con la estimación manual
previa (~+51%) — no hay discrepancia, por lo tanto **no es un hallazgo de
cableado nuevo** en `logpearson3.py::cuantil`.

**Clasificación revisada: Pendiente de dominio — Causa C dominante
(~95% del error en T=100), con contribución menor de Causa A (~5%).**
Refuerza, con una tercera estación y ahora con proporción cuantificada
(no solo cualitativa), que el patrón de "la fórmula documentada no
reproduce la tabla de la tesis en la cola" no es exclusivo de Gamma 3p
MPP ni de Log-Normal 3p — aparece también en Log-Pearson III, y en los
tres casos el componente de Causa C domina ampliamente sobre cualquier
diferencia de parámetros.

------------------------------------------------------------------------------------------
--> HALLAZGO INDEPENDIENTE POR CHAT COMO AUDITOR

## est_03 — Precisión adicional sobre Hallazgo C (Auditoría, 14/07/2026)

El hallazgo C del documento de Code clasifica la divergencia de cuantiles
de LP3 Indirecto como "Causa A (g-propagación) con un componente adicional
de Causa C", sin cuantificar la proporción entre ambas. Se hizo el test de
aislamiento que faltaba: recalcular los 7 cuantiles de diseño usando los
PROPIOS parámetros de la tesis (α=0.260, β=16.252, y0=-0.588 — no los de
METIS) con la misma fórmula documentada.

Resultado: si la divergencia fuera mayormente Causa A, sustituir los
parámetros de METIS por los de la tesis debería cerrar casi toda la
brecha. No lo hace — la divergencia en T=100 pasa de +54.03% (params
METIS) a +51.32% (params tesis). **Causa A explica ~3 puntos porcentuales
de 54 (≈6% del efecto total); el otro ≈94% es Causa C pura** — la fórmula
documentada, con los parámetros exactos de la tesis, no reproduce la
propia tabla de cuantiles de la tesis. Mismo patrón que el hallazgo I de
est_01 (Gamma 3p MPP) y el hallazgo B de est_02 (LogNormal 3p MV), ahora
con la particularidad de que en est_03 el patrón afecta al modelo
**operativo real** (LP3 Indirecto es el ganador de Facundo, no un
testigo descartable como en los dos casos anteriores).

**Reclasificación sugerida del hallazgo C:** de "Causa A + componente
Causa C" a **"Causa C dominante (~94%), Causa A residual (~6%)"** — no
cambia el Pendiente de dominio ya asignado, pero sí cambia la prioridad de
escalamiento: confirmar el ddof de gy con Facundo (Causa A) va a resolver
una fracción menor del problema; el grueso requiere entender por qué la
tabla de cuantiles de la tesis no se deriva de sus propios parámetros
publicados — pregunta de fondo distinta, no un detalle de convención.
------------------------------------------------------------------------------------------

**D. Generalizada Exponencial Momentos — parámetros de tesis internamente
inconsistentes con el CV de su propia serie (4ª estación con el mismo
patrón, verificado con el cálculo exacto).** CV_datos = S/x̄ = 1.23777.
Con α=0.6246 (METIS), el CV teórico de la fórmula IV-77 (digamma/trigamma)
da 1.23777 — coincide hasta la sexta cifra decimal con el CV real. Con
α=0.76 (tesis), el CV teórico da 1.13119 — no coincide con el CV real de
la serie (diff -8.6%). **METIS es matemáticamente consistente con sus
propios datos; el valor de tesis no lo es. No es un hallazgo contra
METIS** — mismo patrón ya confirmado en est_02 y, según los documentos
previos, también en est_01/est_04 (esta sesión lo reverifica con cálculo
propio para est_03, no lo asume).

**E. GVE Momentos-L — quinta estación consecutiva con el mismo síntoma
exacto (β cerca, ν/α lejos).** β=-0.4596 (METIS) vs -0.460 (tesis, diff
-0.09%, casi idéntico); ν=28.92 vs 69.20 (-58.2%), α=23.90 vs 42.41
(-43.7%). Método cerrado (IV-234 a IV-241, sin iteración) — no puede ser
convergencia a óptimo distinto. Con cinco estaciones mostrando el mismo
patrón exacto (est_01, 02, 03, 05, 06 — todas las auditadas con Etapa 2
completa hasta ahora, sin excepción), esto ya no es una hipótesis — es un
patrón sistemático confirmado de la distribución GVE con Momentos-L,
altísima prioridad para pregunta directa a Facundo.

**F. GVE Momentos — METIS converge, tesis no (patrón ya visto en 4
estaciones anteriores).** nu=540.34 (degenerado, EEA=529.7) — el mismo
tipo de comportamiento mal condicionado ya documentado. Sin novedad
respecto del patrón conocido.

---

### 5. Selección de modelo y cuantiles

**Modelo ganador de Facundo — Log-Pearson III Indirecto, EEA
tesis=22.6153, EEA METIS=13.5944 (-39.88%).** Implementado, converge,
identidad de distribución coincide. Cuantiles: PASS en T bajos, degrada a
+54.13% en T=100 (ver hallazgo C). **A diferencia de est_01 (modelo no
implementable), acá el sistema sí puede ofrecer al usuario experto el
mismo modelo que Facundo eligió — el pendiente es de precisión en la cola,
no de disponibilidad.**

**Testigo — GVE MV, EEA tesis=31.6660, EEA METIS=31.6660 (PASS exacto).**
Cuantiles PASS 7/7, diff 0.00% en todos los T.

---

### 6. Clasificación final est_03

| Columna | Resultado |
|---|---|
| **Etapa 1** | **Aprobado**, sin reservas nuevas — la única discrepancia (Wald n1/n2) ya estaba identificada y sin resolver desde Fase 1 (DECISIÓN 017), reconfirmada acá, no es un hallazgo nuevo. |
| **Cableado (13 dist.)** | **Aprobado** — 34/34 combinaciones distribución×método, reconstrucción propia completa, 0 hallazgos. Extiende formalmente el 3/34 (solo Gamma 2p) que dejó Fase 2. |
| **Selección de modelo** | **Aprobado** — el modelo ganador de Facundo (Log-Pearson III Indirecto) está implementado y converge; identidad coincide. |
| **Cuantiles** | **Pendiente de dominio — Causa C dominante (~95% del error en T=100), Causa A minoritaria (~5%)**, cuantificado con test de aislamiento sobre la función real `logpearson3.cuantil()` — el modelo seleccionado degrada con T (hasta +54% en T=100); el testigo (GVE MV) es PASS exacto 7/7, confirmando que el sistema es capaz de reproducir la tesis al dígito cuando el método converge limpio. |

**Clasificación general de la estación: Parcial.** Etapa 1 y cableado
**Aprobados** sin reservas. Selección de modelo Aprobada (el sistema
ofrece el mismo modelo que Facundo eligió). Los cuantiles de ese modelo
tienen un Pendiente de dominio real (degradación con T, mismo patrón
sistémico ya visto en est_01/02) que sí afecta la ruta que usaría el
usuario experto — a diferencia de est_02, donde el pendiente quedaba
fuera de la ruta principal. **Ningún hallazgo de esta ronda requiere
modificar código de `metis/core/` — no se aplicó ni se propone ningún
cambio.**
