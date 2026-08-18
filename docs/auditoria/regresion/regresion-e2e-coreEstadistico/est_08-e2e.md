## est_08 — Ume Pay – Río Grande — Análisis E2E desde cero (15/07/2026)

Detalle completo del análisis Fase 4 (regresión E2E) para esta estación.
Índice y tabla de consolidación de las 9 estaciones: `fase4-e2e.md`.

**Nota de encuadre:** primera de las 2 estaciones restantes (junto con est_09)
que nunca habían tenido ninguna ronda de Fase 2/4 previa — solo existía la
corrida de pipeline diagnóstica en `regresion-pipeline/est_08...md` y el
análisis parcial en `regresion-unitaria/est_08...md`. Se rehizo íntegro desde
cero, sin asumir ningún resultado de esos dos documentos como válido —
usados solo como fuente de la serie y de los valores de referencia de la
tesis (ya verificados como genuinamente de Ume Pay, no contaminados con
est_07 — ver nota de verificación cruzada en la ficha de pipeline).

### Método y alcance

Mismo método que est_01-07: `ejecutar_etapa1()` + `ejecutar_etapa2()` en vivo
contra el working tree actual, con reconstrucción manual/aislada de cada
estadístico de Etapa 1 y de cada combinación distribución×método de Etapa 2.

**Corrección de conteo — hallazgo de esta ronda, aplica retroactivamente a
est_01-07:** el conteo "34/34 combinaciones distribución×método" usado en
los 7 documentos anteriores es un error heredado, nunca recontado desde el
código. El conteo real, sumando `METODOS_APLICABLES` de las 13 distribuciones
(`exponencial_beta`=2, `exponencial_x0_beta`=2, `gamma2p`=3, `gamma3p`=2,
`gen_exponencial`=3, `gen_pareto`=4, `gumbel`=4, `gve`=3, `lognormal2p`=2,
`lognormal3p`=2, `logpearson3`=3, `normal`=3, `uniforme`=2), da **35**, no 34.
No se corrige retroactivamente el texto de est_01-07 en esta sesión (fuera de
alcance puntual), pero queda anotado acá para que el informe de consolidación
final use el número correcto. Para est_08 se usa 35/35.

**Nota de cierre (15/07/2026) — contradicción resuelta sin depender de
git.** El Hallazgo A de este documento (Causa D en Gamma 3p MV) fue
cuestionado contra `regresion-pipeline/est_08...md`, que reporta
`no_converge` para el mismo método en una corrida fechada 14/07/2026 —
misma estación, mismo método, aparente contradicción directa con lo que
reporta este documento (`ok`, con parámetros y EEA). Se resolvió leyendo
únicamente el archivo `gamma3p.py` tal como está hoy (nunca `git log` ni
`git show` — no son fuente válida en esta auditoría, ni para el repo
remoto ni para el propio código de METIS) y matemática pura:

El escaneo *anterior* a la corrección aplicada en este archivo está
descripto explícitamente en su propio comentario (bloque "DECISIÓN 023",
líneas ~162-173 de `gamma3p.py` de hoy): consistía únicamente en
`np.linspace(lo, hi, 200)`, sin el agregado geométrico que el archivo usa
ahora. Se reconstruyó ese escaneo viejo usando solo las funciones de
módulo del archivo actual (`_params_from_x0`, `_psi_thom` — no closures,
no dependen de ninguna versión anterior del código) y se evaluó sobre la
serie real de est_08: **0 cambios de signo en los 200 puntos** — el
escaneo viejo no encuentra ningún bracket en absoluto. La causa: el
dominio de búsqueda para est_08 mide 1763.65 unidades de ancho
(`lo=-1724.4456`, `hi=39.2000`), con paso de ~8.86 unidades para 200
puntos uniformes; la raíz genuina de IV-142 está en x0≈34.35 (coincide con
el x0=34.351 de la tesis), a solo 4.87 unidades de `hi` — una ventana casi
7 veces más angosta que el paso del escaneo viejo, que por eso nunca podía
encontrarla. El escaneo actual del archivo (grueso + geométrico
concentrado hacia `hi`) sí genera el bracket, y `ajustar()` de hoy
converge con los parámetros ya reportados en este documento.

Esto confirma que la discrepancia entre los dos documentos es real y
tiene una causa verificable dentro del propio archivo actual — no es un
bug de cableado (`ajustar()` es la misma función que usa el pipeline, sin
wrapper distinto entre la llamada aislada y la orquestada) sino que el
código de `gamma3p.py` cambió su comportamiento para est_08 en algún
momento entre el 14/07 y hoy. El Hallazgo A se sostiene sin cambios.
Adicionalmente, el texto de DECISIÓN023 en `decisions-log.md` afirmaba
"est_08: sin cambio" al verificar esa corrección contra las 9 estaciones
— esa afirmación no se sostiene con la reconstrucción de arriba, y quedó
corregida en `decisions-log.md` mediante nota agregada (no se editó ni
borró el texto original de esa decisión).

---

### 1. Etapa 1 — reconstrucción completa

Las 5 pruebas se reconstruyeron con las funciones reales de `metis/core/etapa1/`
de forma aislada (Helmert secuencia por secuencia, Anderson lag por lag,
Wald-Wolfowitz con exclusión de empates, Cramer con `_cramer_bloque`, t-Student
con las dos particiones candidatas) y coinciden con el pipeline en vivo.

| Variable | METIS | Tesis | diff% | Nivel |
|---|---|---|---|---|
| n | 43 | 43 | 0.00% | PASS |
| Media | 156.662558 | 156.657 | +0.0035% | PASS |
| Varianza (no sesgada) | 7776.113934 | 7775.688 | +0.0055% | PASS |
| Desvío | 88.182277 | 88.18 | +0.003% | PASS |
| Máximo/Mínimo | 407.9 / 39.2 | 407.86*/39.2 | ~0% | PASS |
| Asimetría no sesgada (g) | 0.950742 | 0.918 | +3.57% | DECISIÓN013, patrón conocido |
| CV | 0.562880 | 0.563 | -0.02% | PASS |

\* 407.86 en la tabla de tesis es redondeo de display; el dato real de la
serie es 407.9 (año 83-84) — ya señalado en `regresion-pipeline/est_08...md`,
no es discrepancia de datos base.

**Sin discrepancia de datos base** — segunda estación (después de est_02/04)
sin ningún indicio de dato transcripto distinto al que usó Facundo.

**Helmert** — reconstruido secuencia por secuencia: S=31, C=11, S-C=20 —
**coincide exacto con la tesis** (S=31, C=11, S-C=20). Rechaza en ambos
(20 > 6.48).

**t-Student** — METIS (partición floor, n1=21/n2=22) da t=1.11672. Con
partición ceil (n1=22/n2=21, la convención de tesis ya documentada en
est_03/05/07) se obtiene t=1.47177 — **coincide casi exacto con el 1.47 de
tesis**. Mismo patrón de convención de partición para n impar ya conocido,
no es un hallazgo nuevo. Ambos aprueban (muy por debajo del crítico en las
dos particiones).

**Cramer** — reconstruido con `_cramer_bloque()` real. `n=43` no discrimina
`ceil` de `round` para ninguna de las dos particiones (n×0.6=25.8, frac=.8;
n×0.3=12.9, frac=.9 — ambas ≥.5, `ceil==round` en los dos casos, a diferencia
de est_02/05/07). n_w1=26: τ_w1=-0.10293, t_w1=0.82177 — **coincide exacto
con la tesis** (τ_w1=-0.10293, t_w1=0.82176). n_w2=13: τ_w2=-0.53175,
t_w2=2.39274 — **coincide exacto** (τ_w2=-0.53174, t_w2=2.3927).

**Hallazgo nuevo — valor crítico de tabla en Cramer/t-Student, convención
distinta a las 8 estaciones anteriores.** Verificado independientemente:
`t.ppf(0.975, df=41) = 2.019541` (dos colas, α/2=0.025 — la fórmula exacta
que documenta Ec. III-8 y que usa `metis/core/etapa1/homogeneity.py`) vs.
`t.ppf(0.95, df=41) = 1.682878`. **La tesis imprime 1.6829 para esta
estación** — coincide con el crítico de **una cola** al 5%, no con el de dos
colas al 2.5% que usan todas las demás estaciones auditadas (est_02: 2.0739
para GL=22; est_06: 2.0281 para GL=36; est_07: 2.1098 para GL=17 — los tres
coinciden con `t.ppf(0.975, df)`, no con `t.ppf(0.95, df)`). Es la primera
vez, en las 8 estaciones auditadas con este nivel de detalle, que el valor
crítico impreso en la fuente no seguiría la convención de dos colas que sí
sigue en el resto — inconsistencia interna de la propia tesis entre
estaciones, no un error de METIS (que aplica la misma fórmula Ec. III-8 de
forma consistente en las 8 estaciones). No cambia ningún veredicto individual
en est_08 (t_w1=0.822 < ambos críticos; t_w2=2.393 > ambos críticos).
**Clasificación: Pendiente de dominio**, candidato de consulta a Facundo.

**Veredicto de homogeneidad — divergencia de clasificación, ya anticipada
por la propia fuente.** METIS: `homogeneidad_critica` (Cramer rechaza en
n_w2 → jerarquía absoluta de METIS, per `constraints.md`: "Cramer rechaza →
homogeneidad_critica, no importa si Helmert o t-Student aprobaron"). Tesis:
"Serie Homogénea (Aprobada bajo consideraciones especiales)" — desempate
narrativo manual (t-Student favorable + un subgrupo de Cramer), no una regla
codificable. **No es un bug** — METIS sigue su propia regla de negocio
documentada de forma estricta y consistente; la tesis aplica una excepción
explícita para este caso puntual que su propio texto reconoce como atípica
("Se registraron resultados dispares"). El pipeline no se detiene por esto
(principio "detecta y advierte, no bloquea") — `nivel_confianza='con_warnings'`.

**Anderson** — reconstruido lag por lag (k_max=ceil(43/3)=15): solo el lag
k=1 fuera de banda (r_1=0.39728 > 0.27500) — **1/15 lags fuera, coincide
exacto con "1 punto fuera" de la tesis**. Aprobada en ambos.

**Wald-Wolfowitz** — reconstruido a mano (excluyendo empates con la media,
DECISIÓN017): n1=19, n2=24, R=12 — **coincide exacto con la tesis**
(n1=19, n2=24, R=12). Z=-3.1958 vs tesis Z=-3.20 (diff 0.13%, prácticamente
exacto). Rechaza con dureza en ambos, muy por fuera de ±1.96 y ±2.58.

**Veredicto de independencia — coincide, pero por mecanismos distintos que
casualmente convergen.** METIS: `independiente` (Anderson aprueba → manda,
jerarquía estándar ya documentada, `constraints.md`). Tesis: "Independiente
bajo criterio especial" (misma jerarquía Anderson-manda, pero la tesis la
presenta como excepción manual explícita pese a que es exactamente la regla
estándar que METIS aplica siempre). A diferencia de homogeneidad, acá la
regla estándar de METIS sí reproduce el resultado práctico de la "excepción"
narrada por la tesis — coincidencia, no by design compartido.

**Veredicto general Etapa 1: Habilitada para Etapa 2, en ambos. Aprobado**
— sin discrepancias de datos base, Helmert/Anderson/Wald-Wolfowitz exactos,
único hallazgo nuevo es el valor crítico de tabla (Pendiente de dominio, sin
efecto en veredictos).

**Tendencia y atípicos** (sin referencia de tesis): Mann-Kendall **rechaza**
(Z=-2.627, TEST_WARNING_TREND). KS aprueba (Z=1.022 < 1.358). Chow aprueba
(2.119 < K_N=2.897, sin atípico). Sin hallazgos de cableado.

---

### 2. Etapa 2 — cableado completo (35/35)

**13/13 distribuciones, 35/35 combinaciones distribución×método verificadas
mediante llamada aislada a `ajustar()`+`cuantil()`+`calcular_eea()`,
comparada contra la salida real de `ejecutar_etapa2()` — 0 hallazgos de
cableado.** Ninguna rama de código nueva respecto de las 7 estaciones
anteriores (sin ceros en la serie, mínimo=39.2 — `STATUS_DISABLED_ZEROS`
sigue sin ejercitarse en ninguna de las 8 estaciones auditadas hasta ahora).

`gamma3p/mv` converge con el fix de DECISIÓN023 ya aplicado, sin necesitar
el escaneo denso (raíz ya encontrable con el escaneo estándar para esta
serie). `logpearson3/mv` da `no_converge`, coincidiendo con la tesis (primera
estación donde ambos coinciden sin necesitar investigación de guard de
borde). `logpearson3/momentos_directo` da `no_aplicable` (B=2.7178 ∉ (3,6],
guard IV-249 aplicado correctamente).

---

### 3. Etapa 2 — parámetros y EEA, comparación completa contra tesis

| Distribución | Método | Param. | METIS | Tesis | diff% |
|---|---|---|---|---|---|
| Uniforme | Momentos | α,β,EEA | 3.9264/309.3987/26.8884 | 3.92/309.39/26.8838 | ~0% |
| Uniforme | MV | α,β,EEA | 39.20/407.90/76.5562 | 39.2/407.86*/76.5387 | ~0% |
| Exponencial β | Mom/MV | β,EEA | 0.006383/52.3252 | 0.006/52.3217 | ~0% (redondeo tesis) |
| Exponencial x0β | Momentos | x0,β,EEA | 68.4803/88.1823/16.5295 | 68.48/88.18/16.5277 | ~0% |
| Exponencial x0β | MV | x0,β,EEA | 36.4033/120.2593/23.0922 | 36.4/120.25/23.0883 | ~0% |
| Gen. Exponencial | Momentos | α,λ | 4.2001/0.013575 | 2.26/0.0121 | +85.8%/+12.2% (ver hallazgo E) |
| Gen. Exponencial | MV | α,λ,EEA | 4.1430/0.013520/11.3754 | 4.14/0.0135/11.367 | ~0% |
| Gen. Exponencial | ML | α,λ | 0.4326/-0.003866 | 0.76/-0.0032 | -43.1%/+20.8% (pendiente IV-84, patrón conocido) |
| Normal | Mom/MV | µ,σ,EEA | 156.6626/88.1823/23.7603 | 156.66/88.1799/24.4824 | ~0%/-2.95% (Causa C) |
| Normal | ML | σ,EEA | 87.0759/23.8953 | 87.0747/24.7527 | ~0%/-3.46% (Causa C) |
| Log-Normal 2p | Mom/MV | µy,σy,EEA | 4.8972/0.579692/10.4100 | 4.9/0.58/11.4193 | ~0%/-8.84% (Causa C) |
| Log-Normal 3p | Momentos | x0,µy,σy,EEA | -130.346/5.6144/0.30034/12.9488 | -140.11/5.6506/0.2909/16.3745 | Causa A / -20.92% |
| Log-Normal 3p | MV | x0,µy,σy | -0.4715/4.9014/0.5705 | -0.51/4.9016/0.5704 | **+7.54%**/~0%/~0% |
| Log-Normal 3p | MV | EEA | 10.7733 | 12.6072 | -14.55% (Causa C) |
| Gamma 2p | Momentos | α,β,EEA | 49.6361/3.1562/10.9492 | 49.64/3.156/14.6747 | ~0%/-25.39% (Causa C) |
| Gamma 2p | MV | α,β,EEA | 46.8192/3.3461/12.7008 | 46.82/3.346/16.474 | ~0%/-22.90% (Causa C) |
| Gamma 2p | ML | α,β,EEA | 52.6469/2.9757/9.3833 | 52.65/2.976/12.9186 | ~0%/-27.37% (Causa C) |
| Gamma 3p | Momentos | x0,α,β,EEA | -28.839/41.919/4.4252/12.0018 | -35.53/40.459/4.75/15.5852 | Causa A / -22.99% |
| Gamma 3p | MV | x0,α,β | 34.3568/72.6161/1.6843 | 34.351/72.623/1.684 | **~0% los 3** |
| Gamma 3p | MV | EEA | 8.8380 | 11.6228 | **-23.96% — ver Hallazgo A (Causa D)** |
| Gamma 3p | MPP | — | EXCLUIDO (no implementado) | x0=12.529,α=62.359,β=2.311,EEA=10.599 | pendiente de código ya conocido |
| Gumbel | los 4 métodos | α,µ,EEA | ver tabla — **PASS total, ≤0.01% en los 4** | igual | 0% |
| GVE | Momentos | ν,α,β,EEA | 12319.96/67.742/-0.01118/12650.12 | NO_CONVERGE | METIS converge (degenerado) donde tesis no — patrón conocido |
| GVE | MV | ν,α,β,EEA | 112.2155/60.8007/-0.14604/12.0014 | 112.214/60.806/-0.146/11.9944 | **~0% los 4 — PASS exacto** |
| GVE | ML | β | -0.06743 | -0.067 | ~0.6% (casi exacto) |
| GVE | ML | α,ν,EEA | 66.349/113.644/10.4742 | 74.766/238.514/131.9477 | -11.26%/-52.35%/-92.06% — mismo patrón GVE-ML, 8ª estación consecutiva |
| LP3 | Directo | — | NO_APLICABLE (B=2.718 ∉ (3,6]) | α=0.036,β=157.69,y0=4.967,EEA=76.4185 | METIS aplica correctamente la restricción IV-249 — mismo desacuerdo real que est_07 |
| LP3 | Indirecto | α,β,y0 | 0.04415/172.381/-2.7138 | 0.043/184.2/-2.971 | +2.68%/-6.42%/+8.66% (Causa A) |
| LP3 | Indirecto | EEA | 12.6822 | 11.5388 | +9.91% |
| LP3 | MV | — | NO_CONVERGE | NO_CONVERGE | **coincide — primera vez sin discrepancia en este método** |

\* 407.86 es redondeo de display de tesis; dato real 407.9.

**Nota posterior — DECISIÓN 060 (17/08/2026).** El guard de dominio
bloquea el resultado de Exponencial x0-β Momentos de esta tabla:
x0=68.4803 > min(serie)=39.2 viola IV-68/69 — METIS hoy devuelve
`NO_APLICABLE`. Cambia el mejor método de la distribución: antes,
Momentos (EEA=16.53) era mejor que MV (EEA=23.09) y ocupaba el puesto
9/13; ahora pasa a MV, puesto 10/13.

Gen. Pareto Momentos no tiene fila propia en esta tabla. Acá el efecto
del guard es una **mejora**, no una degradación: antes, Momentos daba un
ajuste muy pobre (EEA=148.21, puesto 13/13, el peor); bloqueado ese
resultado, el mejor método disponible pasa a ser MC (EEA=21.30), y la
distribución sube al puesto 9/13.

DECISIÓN 061 no aplica — sin ceros reales. Detalle completo en
`docs/decisiones/decision060.md`.

---

### 4. Hallazgos relevantes — con causa e implicancia

**A. Gamma 3p MV — Causa D confirmada, la más severa del proyecto hasta
ahora: cambia el #1 del ranking propio de METIS, no solo el orden entre
dos candidatos.** Los 3 parámetros coinciden con la tesis a menos de 0.03%
(x0, α, β) — el mismo punto en el espacio de parámetros. El EEA diverge
-23.96% (METIS=8.8380 vs tesis=11.6228). Verificado por **tres vías
independientes**, ninguna dependiente de otra:

1. Función real `gamma3p.cuantil()` + `calcular_eea()`, con parámetros
   propios de METIS: EEA=8.8380.
2. Misma función real, inyectando los parámetros **exactos** de tesis
   (x0=34.351, α=72.623, β=1.684): EEA=8.8445 — prácticamente idéntico al
   punto 1 (diff 0.07 puntos porcentuales). Confirma que la divergencia no
   depende de qué parámetros se usen — es la fórmula/cálculo, no el ajuste.
3. Cross-check totalmente independiente del código de METIS, vía
   `scipy.stats.gamma.ppf(p, a=β, loc=x0, scale=α)` (cuantil exacto de la
   Gamma, sin pasar por la aproximación de Wilson-Hilferty IV-144):
   EEA=8.6055 — mismo orden de magnitud que 1 y 2, lejos de 11.6228. Esto
   descarta que el problema sea la aproximación IV-144 en sí — ni siquiera
   el cuantil exacto de la distribución Gamma reproduce el EEA de la tesis.

**Consecuencia práctica — a diferencia de todos los casos de Causa C/D
anteriores del proyecto:** en el ranking propio de METIS para est_08,
Gamma 3p MV queda **#1 de las 13 distribuciones** (EEA=8.838), por debajo
incluso del EEA=10.599 que la tesis reporta para su propio modelo ganador
(Gamma 3p MPP, no implementable en METIS) y del EEA=10.925 del modelo que
Facundo efectivamente seleccionó (Gumbel ML). Un usuario experto que
confiara en el ranking de METIS para esta estación vería **Gamma 3p MV**
como la mejor opción — un modelo que ni siquiera aparece cerca del top en
la propia tabla de la tesis (ahí ocupa el puesto #6, EEA=11.6228). Es el
caso de Causa D más severo documentado en el proyecto: no es una inversión
de 2 puestos (est_05) sino una que coloca en el #1 absoluto un modelo que
la tesis, con sus propios números, ubica en el medio de su tabla.

**Clasificación: Pendiente de dominio — Causa D**, prioridad máxima de
consulta a Facundo (ver `pendientes-facundo.md` — actualizar sección Causa
D con este caso).

**B. Gumbel ML (modelo seleccionado por Facundo) — PASS exacto en los 4
métodos y en los 7 cuantiles de diseño.** α=70.894/µ=115.741 (METIS) vs
α=70.893/µ=115.736 (tesis), diff ≤0.01%. Cuantiles T=2 a 100: diff ≤0.004%
en los 7 casos. Confirma, octava estación consecutiva, que el sistema
reproduce la tesis al dígito cuando el método converge limpio.

**C. GVE MV — PASS exacto en los 4 valores** (ν, α, β, EEA), séptima
estación consecutiva con este resultado.

**D. GVE Momentos-L — mismo patrón (β cerca, ν/α lejos), octava estación
consecutiva sin excepción** (est_01 a est_08). β=-0.06743 (METIS) vs -0.067
(tesis, diff 0.6%); α=66.35 vs 74.77 (-11.3%), ν=113.64 vs 238.51 (-52.3%).
Método cerrado (IV-234 a IV-241, sin iteración) — no puede ser convergencia
a óptimo distinto. Ocho de ocho estaciones auditadas con Etapa 2 completa
muestran el mismo síntoma exacto — máxima prioridad de consulta a Facundo,
ya no admite duda de que sea casualidad de una serie particular.

**E. Generalizada Exponencial Momentos — divergencia más severa del
proyecto en este chequeo, con verificación CV explícita.** CV_datos=0.56288.
Con α=4.2001 (METIS) el CV teórico (digamma/trigamma, IV-77) coincide exacto
(0.56288). Con α=2.26 (tesis) el CV teórico da 0.70985 — diff +26.1%
respecto del CV real de los datos, la mayor divergencia de este chequeo
vista en las 8 estaciones (la anterior más alta era est_07 con +23.2%).
Mismo patrón ya documentado (pendiente IV-77), METIS es el matemáticamente
consistente con sus propios datos.

**F. LP3 Directo — mismo tipo de desacuerdo real que est_07, no est_05.**
B=2.7178 ∉ (3,6], guard aplicado correctamente. La tesis reporta valores
(α=0.036, β=157.69, y0=4.967, EEA=76.4185) pese a que B está fuera del
dominio válido de IV-251/252 — mismo pendiente de dominio abierto en
est_07 (Pedido 2 de esa ronda), sin resolver aún, ahora con una segunda
estación de evidencia.

**G. LP3 MV — primera coincidencia exacta sin necesitar investigación de
guard.** METIS `no_converge`, tesis `NO_CONVERGE` — ambos coinciden
directamente, sin el patrón de "METIS converge donde tesis no" (o viceversa)
que apareció en la mayoría de las estaciones anteriores para este método.

---

### 5. Selección de modelo y cuantiles

**Modelo ganador de Facundo — Gumbel ML, EEA tesis=10.9182, EEA
METIS=10.9252 (+0.06%).** Facundo no eligió el mínimo numérico de su propia
tabla (Gamma 3p MPP, EEA=10.599) — lo descartó por criterio gráfico +
parsimonia (menos parámetros), tal como permite el diseño del sistema.
Parámetros PASS exacto, cuantiles PASS 7/7 (diff ≤0.004%).

**Selección de modelo: Parcial — Aprobado en el sentido de fidelidad del
modelo elegido, pero con una reserva real por el Hallazgo A.** El sistema
reproduce exacto el modelo que Facundo seleccionó (Gumbel ML) si el usuario
elige manualmente esa distribución — coincide con el diseño de "METIS no
decide, expone el ranking". Pero **el ranking que expondría METIS en la
práctica no tiene a Gumbel ML como mejor opción numérica — tiene a Gamma 3p
MV, por Causa D (Hallazgo A)**. A diferencia de est_04 (donde Facundo
también descartó el mínimo numérico de METIS por criterio gráfico, pero ese
mínimo — GVE MV — coincidía exacto con el propio mínimo de la tesis), acá
el mínimo de METIS (Gamma 3p MV) **no** coincide con el mínimo de tesis
(Gamma 3p MPP) ni con ningún candidato razonable de su tabla — es un
artefacto de Causa C que distorsiona el ranking completo.

---

### 6. Clasificación final est_08

| Columna | Resultado |
|---|---|
| **Etapa 1** | **Aprobado** — sin discrepancias de datos base, Helmert/Anderson/Wald-Wolfowitz exactos. 1 hallazgo nuevo (valor crítico de tabla en Cramer/t-Student, una cola vs dos colas) — Pendiente de dominio, sin efecto en veredictos. |
| **Cableado (13 dist., 35 combinaciones — conteo corregido)** | **Aprobado** — 35/35, reconstrucción propia completa, 0 hallazgos de wiring. |
| **Selección de modelo** | **Parcial** — el modelo elegido por Facundo (Gumbel ML) es fiel y disponible en METIS, pero el ranking automático de METIS recomendaría un modelo distinto (Gamma 3p MV) por Causa D — ver Hallazgo A. |
| **Cuantiles** | **Aprobado** para el modelo seleccionado (Gumbel ML, PASS 7/7, diff ≤0.004%). |

**Clasificación general de la estación: Parcial.** Etapa 1 y cableado
**Aprobados** sin reservas de fondo (salvo el hallazgo nuevo de valor
crítico, sin consecuencia práctica). La selección de modelo tiene el
**hallazgo de Causa D más severo de todo el proyecto** — no invierte el
puesto #1 y #2 como en est_05, sino que coloca en el #1 absoluto un modelo
que la propia tesis no considera cerca del top. **Ningún hallazgo de esta
ronda requiere modificar código de `metis/core/`** — las tres verificaciones
independientes del Hallazgo A (función real, parámetros exactos de tesis,
cuantil exacto vía scipy sin aproximación) descartan que sea un bug de
implementación; es Causa C con la consecuencia práctica más grave observada
hasta ahora.

---

## ADDENDUM (15/07/2026) — Hallazgo H y correcciones de trazabilidad

### Corrección — sección 1, párrafo "Veredicto de homogeneidad"

El párrafo original cita `constraints.md` como fuente de la jerarquía Cramer-principal y
concluye "No es un bug" sin elevar la contradicción a hallazgo. Se agrega precisión de fuente
y se formaliza como Hallazgo H (sección 4), sin alterar el texto original.

**Fuente correcta:** RF-GEN-P-06 (`METIS — Manual de Requerimientos v2.0`, p.10):
> "Homogeneidad: Cramer es la prueba principal. Helmert y t de Student actúan como
> complemento... homogeneidad_critica: Cramer rechazó, independientemente de las
> complementarias." — Fuente: Facundo, reunión 14/04.
> "Independencia: Anderson es la prueba principal. Wald-Wolfowitz actúa como verificación.
> Si Anderson acepta independencia, la serie se considera independiente aunque
> Wald-Wolfowitz rechace." — Fuente: Facundo, reunión 14/04.

`constraints.md` (si existe con ese contenido) sería la implementación de RF-GEN-P-06, no la
fuente — la fuente autorizada para decisiones de diseño es el manual de requerimientos.

### Hallazgo H — Homogeneidad est_08: la tesis contradice su propia jerarquía posterior (RF-GEN-P-06)

METIS ejecuta correctamente la jerarquía Cramer-principal especificada por Facundo (reunión
14/04, RF-GEN-P-06): Cramer rechaza (subgrupo 2, t_w2=2.393>2.020) → `homogeneidad_critica`,
con independencia de que t-Student apruebe (t=1.117) y Helmert también rechace (S-C=20). Los
6 valores subyacentes (Helmert, t-Student en sus dos particiones, ambos subgrupos de Cramer)
coinciden exacto entre METIS y tesis — no hay error de cálculo en ningún lado.

La tesis, para esta estación puntual, da el rol decisivo a t-Student en vez de a Cramer,
llegando a "Homogénea (aprobada bajo consideraciones especiales)" — el criterio inverso al
que el mismo autor fijó después para el software. Es la misma estructura de hallazgo que en
Independencia (donde Anderson-principal sí coincide con el veredicto de tesis, por eso ahí no
hay contradicción) — la asimetría entre los dos módulos de Etapa 1 no es de diseño de METIS,
es de qué tan fiel es la narrativa de la tesis a su propia jerarquía en cada caso.

**Clasificación: Pendiente de dominio — nota de trazabilidad histórica.** No requiere cambio
de código (METIS es fiel a RF-GEN-P-06). Queda para consolidación: ¿la tesis (académica,
2019) usa un criterio que el autor abandonó después al fijar la jerarquía para METIS (2026),
o hay una inconsistencia real sin resolver? Pregunta directa a Facundo — sumar a
`pendientes-facundo.md` junto con el Hallazgo D (GVE Momentos-L) y el Hallazgo A (Causa D
Gamma3p MV) como ítems de prioridad alta de esta estación.

### Corrección — sección 6, fila "Etapa 1"

Reemplazar:
> 1 hallazgo nuevo (valor crítico de tabla en Cramer/t-Student, una cola vs dos colas) —
> Pendiente de dominio, sin efecto en veredictos.

Por:
> 2 hallazgos nuevos — (1) valor crítico de tabla en Cramer/t-Student, una cola vs dos colas;
> (2) Hallazgo H, tesis contradice RF-GEN-P-06 en homogeneidad para esta estación puntual.
> Ambos Pendiente de dominio, sin efecto en veredictos ni en código de `metis/core/`.
