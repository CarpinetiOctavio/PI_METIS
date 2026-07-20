## est_04 — Las Tapias – Río Las Tapias — Análisis E2E desde cero (14/07/2026)

Detalle completo del análisis Fase 4 (regresión E2E) para esta estación.
Índice y tabla de consolidación de las 9 estaciones: `fase4-e2e.md`.

**Nota de encuadre:** est_04 tenía Etapa 1 y selección de modelo ya
resueltas (Facundo eligió LP3 Indirecto pese a que GVE MV tiene menor EEA
numérico, por criterio gráfico), pero cableado incompleto — solo Gamma 2p
reconstruido, más un hallazgo puntual sobre `gamma3p.py::mv` documentado
como pendiente sin resolver. Se rehizo íntegro desde cero, incluida la
verificación en vivo de ese hallazgo puntual con el código de hoy.

### Método y alcance

Mismo método que est_01/02/03. Los documentos previos
(`est_04_las_tapias_rioLasTapias-pipeline.md`,
`est_04_las_tapias_rioLasTapias-unitarias.md`) se usaron solo como fuente
de la serie y de los valores de referencia de la tesis.

---

### 1. Etapa 1 — reconstrucción completa

Las 5 pruebas se reconstruyeron a mano de forma independiente y coinciden
**exacto** con la salida del pipeline.

| Variable | METIS | Tesis | diff% | Nivel |
|---|---|---|---|---|
| n | 36 | 36 | 0.00% | PASS |
| Media | 24.0278 | 24.028 | 0.00% | PASS |
| Varianza (no sesgada) | 388.0849 | 388.085 | 0.00% | PASS |
| Desvío | 19.6999 | 19.7 | 0.00% | PASS |
| M0/M1/M2/M3 | 24.028/17.088/13.604/11.434 | 24.028/17.088/13.604/11.434 | ~0% | PASS |
| Suma ln(xi) | 103.0219 | 103.022 | 0.00% | PASS |
| Máximo/Mínimo | 100.0 / 2.0 | 100.0 / 2.0 | 0.00% | PASS |
| Asimetría no sesgada (g) | 1.9293 | 1.849 | +4.34% | DECISIÓN013, patrón conocido |
| Curtosis no sesgada (k) | 8.5317 | 8.064 | +5.80% | DECISIÓN013, patrón conocido |
| CV | 0.8199 | 0.82 | ~0% | PASS |

**Sin discrepancia de datos base** — la estación más limpia hasta ahora en
Etapa 1, junto con est_02. Todo coincide al dígito salvo g/k.

**Independencia** — Anderson: k_max=12, 0/12 lags fuera → aprobada,
coincide con "0 puntos fuera, comportamiento ideal" de la tesis.
Wald-Wolfowitz reconstruido a mano: METIS n1=13, n2=23, R=21, Z=1.2450 —
**coincide exacto con la tesis** (n1=13, n2=23, R=21, Z=1.25). Nivel de
independencia: `independiente` en ambos — PASS total, sin ninguna
discrepancia (a diferencia de est_01 y est_03).

**Homogeneidad** — Helmert: S=15, C=20, S-C=-5 — **coincide exacto con la
tesis**. t-Student: 1.6272 vs tesis 1.63 (+0.17%, PASS). Cramer
reconstruido a mano: τ1=-0.18600, τ2=-0.23676, tw1=1.39809, tw2=0.92725 —
**coincide exacto con la tesis** en los 4 valores. Nivel de homogeneidad:
`homogeneidad_ok` en ambos (unanimidad) — PASS total.

**Veredicto general Etapa 1: Habilitada para Etapa 2, en ambos. Aprobado
sin ninguna reserva** — es la primera estación de las 4 auditadas hasta
ahora sin ningún Pendiente de dominio ni discrepancia puntual sin resolver
en Etapa 1.

**Tendencia y atípicos** (sin referencia de tesis): Mann-Kendall aprueba
(Z=-1.174), KS aprueba (Z=0.833), Chow aprueba (2.5336 < K_N=2.8237). Sin
hallazgos.

---

### 2. Etapa 2 — cableado completo (34/34, extiende Gamma 2p de Fase 2)

**13/13 distribuciones, 34/34 combinaciones distribución×método
verificadas — 0 hallazgos de cableado en el sentido de "orquestador pasa
mal un dato".** Extiende formalmente la verificación de Fase 2.

**Hallazgo distinto de cableado — verificado en vivo con el código de
hoy, diagnosticado y RESUELTO en esta sesión:** `gamma3p`/mv devolvía
`NO_CONVERGE` para est_04. Se confirmó que la causa exacta ya documentada
en `fase2-cableado.md` ("Actualización 14/07/2026 — Hallazgo durante
Bloque 8") seguía presente en el código de hoy — no era un problema de
cableado (el orquestador llama bien a la función), sino de resolución
numérica dentro de `gamma3p.py::ajustar()/mv`. Con aprobación explícita
de Octavio se aplicó un fix (DECISIÓN 023, `decisions-log.md`), verificado
contra las 9 estaciones del dataset sin regresiones — ver hallazgo A.

---

### 3. Etapa 2 — parámetros y EEA, comparación completa contra tesis

| Distribución | Método | Param. | METIS | Tesis | diff% |
|---|---|---|---|---|---|
| Uniforme | Momentos | α, β, EEA | -10.093 / 58.149 / 9.7236 | -10.09 / 58.15 / 9.7236 | ~0% |
| Uniforme | MV | α, β, EEA | 2.00 / 100.00 / 31.2294 | igual | 0% |
| Exponencial β | Mom/MV | β, EEA | 0.041618 / 4.4501 | 0.042 / 4.4501 | -0.91% / ~0% |
| Exponencial x0β | Momentos | x0, β, EEA | 4.3279 / 19.6999 / 4.7691 | 4.33 / 19.70 / 4.7691 | ~0% |
| Exponencial x0β | MV | x0, β, EEA | 1.3706 / 22.6571 / 4.2425 | 1.37 / 22.66 / 4.2425 | ~0% |
| Gen. Exponencial | Momentos | α, λ | 1.5857 / 0.055002 | **1.24 / 0.0356** | **+27.88% / +54.50%** — ver hallazgo D |
| Gen. Exponencial | MV | α, λ, EEA | 1.8413 / 0.059879 / 5.4460 | 1.84 / 0.0599 / 5.4460 | ~0% |
| Gen. Exponencial | ML | α, λ | 0.3218 / -0.030047 | 0.80 / -0.00013 | -59.77% / grande (tesis≈0, pendiente IV-84) |
| Normal | Mom/MV | µ, σ, EEA | 24.028 / 19.700 / 8.5216 | 24.03 / 19.6999 / 8.6648 | ~0% / -1.65% |
| Normal | ML | σ, EEA | 17.9830 / 8.5897 | 17.9830 / 8.8456 | 0% / -2.89% |
| Log-Normal 2p | Mom/MV | µy, σy, EEA | 2.8617 / 0.8559 / 3.6177 | 2.86 / 0.856 / **NO_APLICABLE** | params ~0%; tesis no aplica (mismo patrón est_02/03) |
| Log-Normal 3p | Momentos | x0, µy, σy, EEA | -10.023/3.3835/0.5373/5.1530 | -1.25*/3.4275/0.5210/6.1954 | Causa A / -16.82% |
| Log-Normal 3p | MV | x0, µy, σy | -1.9285 / 3.0031 / 0.7266 | -1.93 / 3.0031 / 0.7266 | **~0% los 3** |
| Log-Normal 3p | MV | EEA | 4.3426 | 5.5651 | **-21.96%** — Causa C |
| Gamma 2p | Momentos | α, β, EEA | 16.152 / 1.4876 / 4.9299 | 16.15 / 1.488 / 5.8610 | ~0% / -15.88% |
| Gamma 2p | MV | α, β, EEA | 13.914 / 1.7268 / 5.5989 | 13.91 / 1.727 / 6.5165 | ~0% / -14.08% |
| Gamma 2p | ML | α, β, EEA | 15.835 / 1.5174 / 5.0101 | 15.84 / 1.517 / 5.9428 | ~0% / -15.69% |
| Gamma 3p | Momentos | — | NO_APLICABLE (x0=3.605>min=2.0**) | x0=2.724, α=18.217, β=1.169, EEA=5.9123 | tesis SÍ reporta EEA pese a que su propio x0 también viola x0<min — ver hallazgo B |
| Gamma 3p | MV | x0, α, β | 1.7400 / 17.4081 / 1.2803 | 1.740 / 17.408 / 1.280 | ~0% los 3 — **fix aplicado, ver hallazgo A** |
| Gamma 3p | MV | EEA | 4.9251 | 5.9155 | -16.75% (Causa C, no resuelta por el fix) |
| Gamma 3p | MPP | — | EXCLUIDO (no implementado) | x0=2.307, α=20.545, β=1.057, EEA=5.3833 | pendiente de código ya conocido a nivel proyecto |
| Gumbel | los 4 métodos | α, µ, EEA | ver tabla — **PASS total, ≤0.01% en los 4 métodos** | igual | 0% |
| GVE | Momentos | ν, α, β, EEA | 298.10 / 13.210 / -0.0997 / 294.93 | 25.124 / 15.548 / -0.210 / **36.2597** | +1086.6% / -15.04% / -52.5% / +713% — ambos convergen, a soluciones muy distintas |
| GVE | MV | ν, α, β, EEA | 13.995 / 10.610 / -0.3118 / 3.9893 | 13.995 / 10.61 / -0.312 / 3.9893 | **~0% los 4 — PASS exacto** |
| GVE | ML | β | -0.2049 | -0.205 | -0.05% (casi exacto) |
| GVE | ML | α, ν, EEA | 11.648 / 14.376 / 4.8125 | **14.711 / 29.325 / 17.2659** | -20.82% / -50.98% / -72.13% — mismo patrón GVE-ML, 6ª estación consecutiva |
| LP3 | Directo | — | NO_APLICABLE (B=2.704 ∉ (3,6]) | α=0.333, β=0.398, y0=3.018, EEA=16.4899 | METIS aplica correctamente la restricción IV-249 |
| LP3 | Indirecto | α, β, y0 | 0.1874 / 20.868 / -1.0482 | 0.180 / 22.708 / -1.217 | +4.09% / -8.11% / -13.86% (Causa A) |
| LP3 | Indirecto | EEA | 4.8532 | 4.1405 | +17.22% |
| LP3 | MV | — | NO_CONVERGE | NO_CONVERGE | **coincide exacto** |

\* x0=-1.25 en tesis ya está documentado como typo (`pendientes-facundo.md`)
— el valor derivable de la propia fórmula con el g de tesis da x0≈-11.26,
no -1.25. Comparación de Causa A hecha contra el valor derivado, no contra
el typo literal.

\*\* Gamma3p Momentos: reconstruido a mano con g_METIS=1.9293 → β=4/g²=1.0748,
α=S/√β=19.003, x0=x̄-S√β=3.605 > min(2.0) → NO_APLICABLE, confirmado.

---

### 4. Hallazgos relevantes — con causa e implicancia

**A. `gamma3p.py::mv` — Pendiente de código real, verificado en vivo con
el código de hoy, con causa raíz identificada y raíz matemática ya
localizada.** El método MV para est_04 devuelve `NO_CONVERGE`, pero existe
una raíz real de IV-142 en x0≈1.73997 — verificada con un escaneo fino
(200.000 puntos) sobre el mismo dominio de búsqueda que usa el código
(`lo=xi_min-20S=-391.997`, `hi=xi_min-1e-9=1.999999999`). Esa raíz da
β=1.2803, α=17.4081 — **coincide con los parámetros que reporta la propia
tesis para este método (x0=1.740, α=17.408, β=1.280) hasta la tercera
cifra decimal.**

La causa es puramente de resolución numérica: el código escanea el
dominio (~394 unidades de ancho) con `np.linspace(lo, hi, 200)` — paso de
≈1.98 unidades — pero la raíz real vive en una ventana de apenas ~0.26
unidades de ancho cerca del extremo superior del dominio (entre x0≈1.740
y una segunda raíz, más débil, en x0≈1.997). Ningún par de puntos
consecutivos del escaneo actual cae a ambos lados de ese cruce, así que
`_idx` queda vacío y la función devuelve `NO_CONVERGE` sin haber
detectado que la solución existe y es única en la zona relevante.

Verificado además: aplicando `calcular_eea` con la raíz correcta
(x0=1.73997, β=1.2803, α=17.4081) se obtiene EEA=4.9251 — no coincide con
el EEA=5.9155 que reporta la tesis para el mismo método (diff -16.75%,
mismo patrón "Causa C" que aparece en el resto del proyecto incluso
cuando los parámetros son casi idénticos) — es decir, **arreglar el
escaneo no cerraría el EEA contra la tesis, pero sí convertiría un
NO_CONVERGE (sin información) en un resultado con parámetros que
coinciden casi exacto con los de Facundo** — mejora real, aunque no
resuelve el pendiente de Causa C que persiste en todo el proyecto.

Este hallazgo ya estaba anotado como pendiente sin resolver en
`fase2-cableado.md` desde una sesión anterior ("no requiere consulta a
Facundo — es un problema de implementación de METIS, no de interpretación
de la tesis... Fix propuesto (no aplicado, requiere aprobación explícita
antes de tocar código)"). **Esta sesión lo reconfirmó en vivo contra el
código actual y, con aprobación explícita de Octavio, aplicó el fix.**

**RESUELTO — 14 de Julio de 2026 (DECISIÓN 023, `decisions-log.md`).**
Diagnóstico ampliado antes de tocar código: el mapeo fino del intervalo
reveló que no era solo un problema de densidad de escaneo — coexisten una
raíz genuina (x0≈1.7315–1.7651, coincide con tesis) **y** una
singularidad espuria de borde (S2=Σ1/zi→~10⁹ cuando x0→min(serie), mismo
tipo de patología que Log-Normal 3p/DECISIÓN020, con escala distinta — no
se reutilizó el margen de LN3p). Fix aplicado en `gamma3p.py::mv()`:
escaneo denso concentrado hacia `hi` (espaciado geométrico) + validación
post-`brentq` del candidato (β>0, α>0, cota de plausibilidad sobre S2:
`S2 > 2.0·n` rechaza — umbral justificado contra los valores concretos de
est_04: raíz genuina S2/n≈0.20, raíz espuria S2/n≈9.40). Si el escaneo
detecta múltiples brackets, se valida cada uno y se toma el primero que
pasa, no el primero por orden de iteración.

**Verificación:** est_04 converge a x0=1.739970, α=17.408141, β=1.280309
— coincide con tesis (x0=1.740, α=17.408, β=1.280) hasta la 3ª cifra
decimal. Corrido además sobre las 9 estaciones del dataset (no solo las 3
mínimas exigidas): est_01/02/03/05/06 siguen `no_converge` sin ninguna
convergencia espuria nueva; est_07/08/09 no cambiaron sus valores (ya
convergían correctamente con el escaneo anterior). Suite completa:
109 passed, 1 failed (el pendiente preexistente de `gen_pareto`/mc, Fase
3, sin relación con este cambio). `ruff check` limpio. Detalle completo
de la verificación en DECISIÓN 023, `decisions-log.md`.

Nota importante que **no** se resuelve con este fix: aplicando
`calcular_eea` con la raíz correcta se obtiene EEA=4.9251, que no
coincide con el EEA=5.9155 que reporta la tesis para este método (diff
-16.75%) — mismo patrón "Causa C" que aparece en el resto del proyecto
incluso con parámetros casi idénticos. El fix convierte un
`NO_CONVERGE` (sin información) en parámetros que coinciden con Facundo;
no cierra el pendiente de Causa C, que sigue siendo un patrón transversal
del proyecto, no específico de esta distribución.

**B. Gamma 3p Momentos — tesis reporta EEA pese a que su propio x0
también viola el soporte de la distribución (x0 > mínimo observado).**
Tesis: x0=2.724, mínimo de la serie=2.0 → x0 > min, viola la misma
restricción de soporte que hace que METIS marque este caso
`NO_APLICABLE`. Sin embargo tesis sí reporta un EEA (5.9123) para esta
combinación — comportamiento distinto al de est_03, donde tesis sí marcó
`NO_APLICABLE`/EEA en blanco para el mismo tipo de violación. **Esta
inconsistencia entre estaciones (a veces tesis reporta EEA con soporte
violado, a veces no) ya estaba señalada en la ficha original y se
reconfirma acá. No es un hallazgo contra METIS — el criterio de METIS
(rechazar cuando x0≥min) es matemáticamente consistente en las dos
estaciones; el que varía es el criterio de tesis.**

**C. La columna "LP3 MMI" de la tabla de cuantiles de tesis para est_04
NO contiene cuantiles de LP3 Indirecto — contiene cuantiles de GVE MV,
confirmado con diff ≤0.03% en los 7 valores de T.** Se calcularon los
cuantiles de GVE MV con los parámetros propios de METIS (que ya coinciden
exacto con los de tesis para este método) y se compararon contra las dos
columnas de la tabla de tesis ("LP3 MMI" y "GVE MV"): la columna rotulada
"LP3 MMI" reproduce GVE MV con diff entre -0.01% y +0.03% en los 7
períodos de retorno — **prácticamente idéntico**, mientras que la columna
correctamente rotulada "GVE MV" de la propia tesis diverge de ese mismo
cálculo entre -7.9% y +9.9% — es decir, ni siquiera coincide consigo
misma con precisión, lo que sugiere que las dos columnas de la tabla
impresa están, como mínimo, mal etiquetadas o corresponden a fuentes
distintas de las que dicen ser.

**Implicancia directa: no existe, en la tabla de tesis para est_04,
ninguna columna verificable de cuantiles de LP3 Indirecto — el modelo que
Facundo efectivamente seleccionó como ganador.** Los cuantiles de LP3
Indirecto que calcula METIS (16.44 a T=2, hasta 168.25 a T=100) no tienen
contra qué compararse en esta estación — a diferencia de est_03, donde sí
había una columna genuina de LP3 Indirecto (aunque divergente). Esto ya
estaba documentado como sospecha en `pendientes-facundo.md`
("Verificado al 0.03%... Las dos columnas parecen estar intercambiadas")
— **esta sesión lo reconfirma con reconstrucción independiente y agrega
el dato de que la columna "GVE MV" tampoco es autoconsistente con el
cálculo directo, ampliando la sospecha más allá de un simple intercambio
de columnas.**

**D. Generalizada Exponencial Momentos — parámetros de tesis
internamente inconsistentes con el CV de su propia serie (6ª
confirmación del mismo patrón, verificado con cálculo exacto).**
CV_datos=0.81988. Con α=1.5857 (METIS) el CV teórico (IV-77) da 0.81988 —
coincide hasta la sexta cifra decimal. Con α=1.24 (tesis) el CV teórico
da 0.91019 — no coincide con el CV real (diff +11.0%). Mismo patrón que
est_01/02/03 — no es un hallazgo contra METIS.

**E. GVE Momentos-L — sexta estación consecutiva con el mismo síntoma
exacto.** β=-0.2049 (METIS) vs -0.205 (tesis, diff -0.05%, casi idéntico);
α=11.65 vs 14.71 (-20.8%), ν=14.38 vs 29.33 (-51.0%). Con seis estaciones
mostrando el mismo patrón sin una sola excepción (est_01 a est_04, más
est_05/06 de rondas anteriores), este hallazgo pasa de "patrón sistemático
confirmado" a **"comportamiento universal de la distribución en todo el
dataset disponible"** — máxima prioridad de consulta a Facundo entre
todos los hallazgos del proyecto.

---

### 5. Selección de modelo y cuantiles

**Modelo ganador de Facundo — Log-Pearson III Indirecto, EEA
tesis=4.1405, EEA METIS=4.8532 (+17.22%).** Facundo no eligió el mínimo
numérico (GVE MV, EEA=3.9893) — lo descartó por criterio gráfico, tal
como permite el diseño del sistema ("METIS no decide, expone el ranking").
**Selección de modelo: Aprobado** — el sistema funciona exactamente como
está especificado, ofreciendo ambas opciones en el ranking para que el
usuario experto decida.

**Cuantiles del modelo seleccionado (LP3 Indirecto): sin comparación
posible** — ver hallazgo C, la tabla de tesis no tiene una columna
verificable para este modelo en esta estación.

**Testigo — GVE MV, EEA tesis=3.9893, EEA METIS=3.9893 (PASS exacto).**
Cuantiles PASS 7/7 contra la columna "LP3 MMI" (que en realidad es GVE MV,
ver hallazgo C) con diff ≤0.03%.

---

### 6. Clasificación final est_04

| Columna | Resultado |
|---|---|
| **Etapa 1** | **Aprobado**, sin ninguna reserva — la estación más limpia de las 4 auditadas hasta ahora (junto con est_02), sin ningún Pendiente de dominio. |
| **Cableado (13 dist.)** | **Aprobado** — 34/34, 0 hallazgos de "dato mal pasado". `gamma3p.py::mv` tenía un bug de resolución numérica (no de cableado) — diagnosticado, corregido y verificado en esta sesión (DECISIÓN 023), sin regresiones en las 9 estaciones. |
| **Selección de modelo** | **Aprobado** — el sistema ofrece ambas opciones (GVE MV numérico, LP3 Indirecto elegido por Facundo); el usuario experto decidió con criterio gráfico, exactamente como el sistema está diseñado para permitir. |
| **Cuantiles** | **Sin comparación posible para el modelo seleccionado** — la tabla de tesis no tiene una columna genuina de LP3 Indirecto para esta estación (hallazgo C). El testigo (GVE MV) es PASS exacto 7/7. |

**Clasificación general de la estación: Parcial.** Etapa 1, selección de
modelo y cableado (incluido el fix de `gamma3p.py::mv`, DECISIÓN 023)
**Aprobados** sin reservas — es el primer Pendiente de código de todo el
proyecto que se diagnosticó, corrigió y verificó de punta a punta en la
misma sesión, a diferencia de Gamma3p MPP (que requiere información de
Facundo que no existe y no es resoluble desde el código). Cuantiles del
modelo seleccionado sin verificación posible por un problema de la propia
tabla de tesis (columnas mal rotuladas), no de METIS.
