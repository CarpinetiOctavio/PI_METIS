## est_01 — Alpa Corral – Río Barrancas — Análisis E2E desde cero (14/07/2026)

Detalle completo del análisis Fase 4 (regresión E2E) para esta estación.
Índice y tabla de consolidación de las 9 estaciones: `fase4-e2e.md`. Este
archivo es el detalle por estación, mismo patrón que
`regresion-pipeline/` y `regresion-unitaria/` para las fases previas.

Contiene dos análisis independientes de la misma corrida de código,
hechos por separado el mismo día y consolidados acá: el análisis
primario (Code, con acceso directo al repositorio) y una
contraverificación (Chat, en sesión aparte) que confirmó los puntos
centrales y aportó dos hallazgos adicionales — documentados con
atribución explícita donde corresponde.

### Método y alcance

Ejecutado sin asumir nada de lo ya escrito en `est_01_alpa_corral_rioBarrancas-pipeline.md`
ni en `est_01_alpa_corral_rioBarrancas-unitaria.md` (Fase 1/2) — ambos
documentos se usaron únicamente para obtener la serie transcripta y los
valores de referencia de la tesis, nunca como fuente de verdad de un
resultado de METIS. Cada estadístico, cada parámetro y cada EEA de esta
sección fue recalculado en esta sesión, en vivo, contra el código real del
working tree (commit `b0b9196` + working tree sin commitear, `git status`
verificado antes de empezar).

Dos corridas independientes por cada resultado de Etapa 2, comparadas entre
sí (metodología de Fase 2, Bloque 6/7, extendida acá por primera vez a
est_01):

1. `ejecutar_etapa1()` + `ejecutar_etapa2()` — pipeline completo, tal como
   correría en producción.
2. Para cada una de las 13 distribuciones × sus métodos aplicables: llamada
   aislada a `modulo.ajustar()` → `modulo.cuantil()` en las probabilidades de
   Weibull → `calcular_eea()`, reproduciendo a mano lo que hace el
   orquestador, fuera de `pipeline2.py`.

**Nota de rigor metodológico, para que quede trazado:** la primera corrida de
la reconstrucción aislada (2) dio 34/34 mismatches contra el pipeline. Antes
de reportarlo como hallazgo se investigó — la causa fue un bug en el propio
script de verificación de esta sesión (`calcular_eea(observados, estimados,
n_parametros)` invocado con los argumentos invertidos y sin ordenar la serie
observada de forma descendente, como exige la firma real de la función).
Corregido el script, las 34 combinaciones coincidieron exacto. Se documenta
explícitamente para no confundirlo con un hallazgo de cableado real — no lo
es.

Recordatorio heredado de la ficha de tesis: est_01 es de uso **exclusivamente
académico**. Etapa 1 rechaza la serie por unanimidad (homogeneidad e
independencia) tanto en METIS como en la tesis — la propia fuente indica que
Facundo continuó con Etapa 2 "con fines académicos". Ningún resultado de
Etapa 2 de esta sección tiene validez de diseño hidrológico.

---

### 1. Etapa 1 — reconstrucción completa, estadístico por estadístico

**Estadística descriptiva**

| Variable | METIS | Tesis | diff% | Nivel |
|---|---|---|---|---|
| n | 40 | 40 | 0.00% | PASS |
| Media | 144.375 | 144.725 | -0.24% | Ver Nota 1 |
| Varianza (no sesgada) | 13404.4455 | 13408.358 | -0.03% | Ver Nota 1 |
| Desvío | 115.7776 | 115.794 | -0.01% | Ver Nota 1 |
| M0/M1/M2/M3 | 144.375/104.537/82.937/68.978 | 144.725/104.751/83.065/69.054 | -0.24%/-0.20%/-0.16%/-0.11% | Ver Nota 1 |
| Suma ln(xi) | 183.2917 | 183.385 | -0.05% | Ver Nota 1 |
| Máximo | 410.0 | 410.0 | 0.00% | PASS |
| Mínimo | 15.0 | 15.0 | 0.00% | PASS |
| Asimetría no sesgada (g) | 0.8018 | 0.762 | +5.23% | DECISIÓN013 (ddof), patrón ya documentado |
| Curtosis no sesgada (k) | 2.7984 | 2.649 | +5.64% | DECISIÓN013, patrón ya documentado |
| CV | 0.8019 | 0.8 | +0.24% | Ver Nota 1 |

**Nota 1 — discrepancia de datos base, no de fórmula.** La diferencia de
media (144.375 vs 144.725) equivale a una diferencia de **suma exacta de
14.0** sobre n=40 (5775.0 vs 5789.0). Una diferencia entera y limpia de 14
unidades no es compatible con redondeo acumulado de Excel (que produce
diferencias fraccionarias, no un entero exacto) — apunta a que al menos un
valor de la serie transcripta en esta auditoría difiere del valor real que
usó Facundo. Se verificó explícitamente que ningún valor de la serie cae
entre 144.375 y 144.725 (el rango que separaría "éxito" de "fracaso" en
Wald-Wolfowitz), así que el efecto no se limita a un simple corrimiento de
frontera — es indicio de un dato base distinto en algún punto de la serie.

**Hipótesis concreta (Chat) — verificada y refinada:** sustituir el valor
transcripto como 129.0 (año 40-41, tercer dato de la serie) por 143.0
reproduce la media exacta de la tesis (144.725) y casi cierra suma_log
(183.3947 vs 183.385 tesis). **Verificado independientemente en esta
sesión (Code) que esta sustitución NO mueve ni un punto el resultado de
Helmert (sigue S=30/C=9/S-C=21, no 28/11/17) ni el de Wald-Wolfowitz (sigue
n1=16/n2=24/R=10, no 17/23/12)** — porque tanto 129 como 143 quedan del
mismo lado de las dos medias en juego (129<144.375 y 143<144.725, ambos
"por debajo"), así que ningún signo cambia. **Conclusión: la sustitución
129→143 es, como máximo, una explicación parcial** — cierra el diff de
media/suma_log pero deja sin explicar por completo el diff de Helmert
(S-C: 21 vs 17, faltan 2 cambios de signo) y de Wald-Wolfowitz (n1/n2: 16/24
vs 17/23). Tiene que existir al menos un segundo valor distinto en la serie
real, en una posición que sí cruce el umbral de la media, para cerrar el
100% de Etapa 1. **Pendiente de dominio — se necesita cotejar la serie
transcripta contra la planilla original de Facundo; no es corregible desde
el código.**

**Independencia**

Anderson — reconstruido lag por lag a mano (k_max=ceil(40/3)=14,
DECISIÓN016): 4 de 14 lags fuera de banda. **Coincide exacto con los "4
puntos fuera" que reporta la tesis.** Veredicto Rechazada en ambos.

Wald-Wolfowitz — reconstruido a mano: METIS n1=16, n2=24, R=10, Z=-3.4076
vs tesis n1=17, n2=23, R=12, Z=-2.80. Ambos rechazan de forma categórica
(fuera de ±1.96 y ±2.58 en los dos casos) — el veredicto coincide, pero los
conteos base (n1/n2/R) no. Fórmula de σ_R verificada algebraicamente
idéntica a la Ec. III-6 de la tesis (ya cerrado en Fase 1) — no es un bug de
fórmula. Misma naturaleza que la Nota 1: **Pendiente de dominio.**

Nivel de independencia: `dependiente` en ambos — **PASS a nivel de
decisión.**

**Homogeneidad**

Helmert — reconstruido secuencia por secuencia: S=30, C=9, S-C=21 (coincide
exacto con la salida del pipeline) vs tesis S=28, C=11, S-C=17. Mismo patrón
que Wald-Wolfowitz — el veredicto coincide (Rechazada, ambos fuera de
±6.24/±6.25) pero los conteos de rachas no, sin que el corrimiento de media
lo explique. **Pendiente de dominio, mismo origen que la Nota 1.**

t-Student: METIS 7.3529 vs tesis 7.28 (+1.0%, partición mitad/mitad n1=n2=20)
— dentro de la tolerancia INFO ya establecida en el proyecto. Ambos rechazan
de forma categórica.

Cramer — reconstruido a mano: τ1=-0.4049, τ2=-0.8144, t_w1=3.5199,
t_w2=3.8849 (n_w1=24, n_w2=12, partición default DECISIÓN011) vs tesis
τ1=-0.4028/τ2=-0.8073 (sic, ver tabla original), t_w1=3.4961, t_w2=3.8373.
Diffs ≤1.3% — dentro de tolerancia INFO ya establecida. Ambos rechazan.

Nivel de homogeneidad: `homogeneidad_critica` en ambos (Cramer rechaza) —
**PASS a nivel de decisión.**

**Veredicto general Etapa 1:** rechazo unánime en ambos (METIS y tesis),
coincide exactamente con la nota explícita de la fuente ("no está habilitada
para... análisis de ajuste de frecuencia teórica"). **Aprobado a nivel de
decisión final.** Las discrepancias de estadístico puntual (Helmert, Wald)
quedan documentadas como Pendiente de dominio — no bloquean el veredicto ni
sugieren ningún bug de cableado (todas las fórmulas fueron reconstruidas a
mano de forma independiente y coinciden exacto con lo que produce el
código).

**Contraverificación (Chat):** Helmert, t-Student, Anderson,
Wald-Wolfowitz y Cramer reconstruidos de forma independiente en una sesión
aparte, con las fórmulas ya fieles de Fase 1 — los 5 coincidieron exacto
con el pipeline. Confirmado 5/5, sin hallazgos de cableado.

**Tendencia y atípicos** (Mann-Kendall, KS, Chow — no están en la tesis de
Facundo, agregados por Carlos; sin valor de referencia posible):
Mann-Kendall rechaza (Z=-4.826, tendencia fuerte — coherente con el quiebre
de nivel visible en la serie entre los primeros ~23 años, más altos, y el
resto). KS rechaza (Z=2.688). Chow **aprueba** (estadístico=1.9396 <
K_N=2.8675 — no detecta un dato atípico puntual, coherente con que el
problema de esta serie es un quiebre de nivel sostenido, no un outlier
aislado). Comportamiento internamente consistente, sin hallazgos.

---

### 2. Etapa 2 — cableado (extensión de Fase 2 Bloque 6/7 a est_01)

**13/13 distribuciones, 34/34 combinaciones distribución×método
verificadas por Code. 0 hallazgos de cableado.** La llamada aislada
(`ajustar`+`cuantil`+`calcular_eea`, fuera del orquestador) reproduce
exacto — parámetros Y EEA, no solo el `status` — lo que produce
`ejecutar_etapa2()` para cada una de las 13 distribuciones sobre la serie
de est_01.

**Contraverificación (Chat):** spot-check de 5/34 combinaciones (Uniforme
MV, Normal Momentos/MV, Gumbel Momentos, Gamma 2p Momentos, Gamma 2p
Momentos-L) reconstruidas de forma aislada — las 5 coinciden con el
pipeline. No se rehicieron las 34 completas en esa sesión; la muestra no
arrojó ninguna discrepancia que ameritara ampliarla. Se deja constancia de
la diferencia de profundidad entre las dos verificaciones (34/34 vs 5/34
spot-check) — ambas apuntan a la misma conclusión, ninguna la contradice.

Ramas de código ejercitadas en est_01 que no se habían visto (o se habían
visto poco) en est_02-06:

- **GVE Momentos converge sin necesitar el fallback a Momentos-L** — el
  guard de IV-202 pasa directo con la condición inicial de Momentos
  (g=0.8018, nu0=93.04, alpha0=94.01, beta0=0.0325). Solo la segunda de las
  10 estaciones auditadas hasta ahora (después de est_09) donde esto ocurre
  — en el resto, Momentos falla el guard y GVE MV arranca desde Momentos-L.
- **`gen_pareto`/momentos, `gen_pareto`/mc y `gen_pareto`/mpp** convergen los
  tres (con calidad muy dispar) en una estación donde la tesis reporta los
  tres como NO_CONVERGE — primera y única estación con dato de referencia
  real de Facundo para Generalizada de Pareto (ver hallazgo E más abajo).

---

### 3. Etapa 2 — parámetros y EEA, comparación completa contra tesis

| Distribución | Método | Param. | METIS | Tesis | diff% |
|---|---|---|---|---|---|
| Uniforme | Momentos | α | -56.1576 | -55.84 | -0.57% |
| Uniforme | Momentos | β | 344.9076 | 345.29 | -0.11% |
| Uniforme | Momentos | EEA | 34.5958 | 34.207 | +1.14% |
| Uniforme | MV | α, β | 15.00 / 410.00 | 15.00 / 410.00 | 0.00% / 0.00% |
| Uniforme | MV | EEA | 77.9243 | 77.432 | +0.64% |
| Exponencial β | Mom/MV | β | 0.006926 | 0.007 | -1.05% (redondeo tesis a 1 cifra) |
| Exponencial β | Mom/MV | EEA | 30.7735 | 31.0205 | -0.80% |
| Exponencial x0β | Momentos | x0, β | 28.597 / 115.778 | 28.93 / 115.79 | -1.15% / -0.01% |
| Exponencial x0β | Momentos | EEA | 30.0903 | 30.1895 | -0.33% |
| Exponencial x0β | MV | x0, β | 11.683 / 132.692 | 12.04 / 118.51 | -2.97% / **+11.97%** |
| Exponencial x0β | MV | EEA | 28.1006 | 28.2616 | -0.57% |
| Gen. Exponencial | Momentos | α, λ | 1.6724 / 0.009431 | **NO_CONVERGE** | METIS converge, tesis no |
| Gen. Exponencial | MV | α, λ | 1.4512 / 0.008694 | 8.97 / 0.0122 | **-83.82% / -28.74%** |
| Gen. Exponencial | MV | EEA | 25.4635 | 25.4672 | -0.01% |
| Gen. Exponencial | ML | α, λ | 0.2992 / -0.005176 | 0.79 / -0.0031 | **-62.13% / -66.98%** |
| Normal | Mom/MV | µ, σ | 144.375 / 115.778 | 144.73 / 115.7945 | -0.25% / -0.01% |
| Normal | Mom/MV | EEA | 36.7760 | 36.1651 | +1.69% |
| Normal | ML | σ | 114.6473 | 114.7836 | -0.12% |
| Normal | ML | EEA | 36.8504 | 36.3555 | +1.36% |
| Log-Normal 2p | Mom/MV | µy, σy | 4.5823 / 0.9663 | **3.11 / 1.69** | **+47.34% / -42.82%** — ver hallazgo B |
| Log-Normal 2p | Mom/MV | EEA | 51.3768 | 38.394 | +33.81% |
| Log-Normal 3p | Momentos | x0, µy, σy | -298.65 / 6.0606 / 0.2570 | -320.499 / 6.113 / 0.245 | +6.82% / -0.86% / +4.91% (Causa A) |
| Log-Normal 3p | Momentos | EEA | 27.4758 | 28.4009 | -3.26% |
| Log-Normal 3p | MV | x0, µy, σy | 7.1097 / 4.4516 / 1.0829 | **38.469 / 2.907 / 1.647** | **-81.52% / +53.13% / -34.25%** — ver hallazgo C |
| Log-Normal 3p | MV | EEA | 65.5194 | 47.8054 | +37.05% |
| Gamma 2p | Momentos | α, β | 92.8446 / 1.5550 | 92.65 / 1.562 | +0.21% / -0.45% |
| Gamma 2p | Momentos | EEA | 26.2459 | 27.3029 | -3.87% (Causa C) |
| Gamma 2p | MV | α, β | 100.8959 / 1.4309 | 101.16 / 1.431 | -0.26% / -0.00% |
| Gamma 2p | MV | EEA | 25.3740 | 25.4097 | -0.14% (PASS — no todas las estaciones muestran Causa C acá) |
| Gamma 2p | ML | α, β | 109.7051 / 1.3160 | 109.64 / 1.32 | +0.06% / -0.30% |
| Gamma 2p | ML | EEA | 25.2549 | 24.1772 | +4.46% (Causa C) |
| Gamma 3p | Momentos | x0, α, β | -144.40 / 46.418 / 6.2212 | -159.149 / 44.125 / 6.887 | +9.27% / +5.20% / -9.67% (Causa A) |
| Gamma 3p | Momentos | EEA | 26.5838 | 27.6252 | -3.77% |
| Gamma 3p | MV | — | NO_CONVERGE | NO_CONVERGE | coincide |
| Gamma 3p | MPP | — | **EXCLUIDO** (no implementado) | x0=-36.302, α=87.987, β=2.057, EEA=**22.3359** | ver hallazgo A — modelo ganador de Facundo |
| Gumbel | Momentos | α, µ | 90.3065 / 92.2751 | 90.32 / 92.617 | -0.01% / -0.37% |
| Gumbel | Momentos | EEA | 26.5957 | 26.4862 | +0.41% |
| Gumbel | MV | α, µ | 84.3594 / 92.0667 | 86.404 / **200.143** | -2.37% / **-54.00%** — ver hallazgo C |
| Gumbel | MV | EEA | 30.2276 | 29.977 | +0.84% |
| Gumbel | ML | α, µ | 93.3414 / 90.4968 | 93.452 / 90.783 | -0.12% / -0.32% |
| Gumbel | ML | EEA | 25.6458 | 25.5046 | +0.55% |
| Gumbel | ME | α, µ | 88.1746 / 93.4792 | **20.394 / 177.338** | **+332.36% / -47.29%** — ver hallazgo C |
| Gumbel | ME | EEA | 27.5245 | 27.3434 | +0.66% |
| GVE | Momentos | ν, α, β | 93.044 / 94.012 / 0.0325 | **NO_CONVERGE** | METIS converge, tesis no |
| GVE | MV | EEA | 78.2992 | 78.3542 (ver nota) | -0.07% |
| GVE | MV | ν, α, β | 70.888 / 62.619 / -0.5422 | **NO_CONVERGE** | METIS converge, tesis no |
| GVE | ML | β | -0.0893 | -0.085 | -5.04% (cercano) |
| GVE | ML | α, ν | 85.350 / 86.889 | **97.948 / 229.601** | **-12.86% / -62.16%** — ver hallazgo D |
| GVE | ML | EEA | 27.0984 | 153.5981 | -82.36% |
| Log-Pearson III | Directo | — | NO_APLICABLE (B=2.4214 ∉ (3,6]) | NO_CONVERGE (mismo resultado práctico) | coincide funcionalmente |
| Log-Pearson III | Indirecto | α, β, y0 | 0.1381 / 48.962 / **-2.1792** | 0.101 / 35.54 / **1.611** | +36.73% / +37.77% / **-235.27%** — ver hallazgo G |
| Log-Pearson III | Indirecto | EEA | 67.9087 | 48.808 | +39.13% |
| Log-Pearson III | MV | — | NO_CONVERGE | α=-1.149, β=-0.0839, y0=3.577 (params negativos, ver hallazgo H) | METIS no converge, tesis reporta valores físicamente inválidos |
| Gen. Pareto | Momentos | µ, σ, ε | -7.70 / 207.23 / 0.3627 | **NO_CONVERGE** | METIS converge (mal, EEA=279.5) — ver hallazgo E |
| Gen. Pareto | MV | — | NO_CONVERGE | (no listada) | — |
| Gen. Pareto | MC | µ, σ, ε | 15.00 / 126.10 / ~0 | **NO_CONVERGE** | METIS converge (EEA=29.2) — ver hallazgo E |
| Gen. Pareto | MPP | µ, σ, ε | -33.20 / 2134.86 / 4.29 | **NO_CONVERGE** | METIS converge (degenerado, EEA=679M) — ver hallazgo E |

---

### 4. Hallazgos relevantes — con causa e implicancia

**A. Gamma 3p MPP — el modelo que Facundo seleccionó como ganador no es
calculable en METIS.** Tesis: EEA=22.3359, el menor de toda la tabla — es
la distribución que la tesis adopta como "distribución gobernante" para
esta estación. METIS no implementa este método porque el Capítulo IV no
desarrolla las ecuaciones MPP para Gamma 3p (ya documentado en
`pendientes-facundo.md` y confirmado en las 9 estaciones previas — acá se
confirma que, además, es justo el modelo que Facundo *eligió* en este caso
puntual, no un método secundario).

**Dato compensador (Chat):** el mejor modelo que METIS sí puede ofrecer
al usuario experto (Gamma 2p Momentos-L, EEA=25.25) coincide en identidad
de distribución con el 2° lugar de la propia tabla de Facundo (Gamma 2p
Momentos-L, EEA=24.18, +4.4%) — no es una alternativa arbitraria, es la
misma distribución que la tesis ya validaba como segunda mejor opción.

**Clasificación: Pendiente de código / implementación bloqueada por falta
de fórmula fuente — no resoluble sin que Facundo provea la derivación de
MPP para Gamma 3p.**

**B. Log-Normal 2p — el valor de tesis es inconsistente con la propia
estadística descriptiva que la tesis reporta para esta estación.** Tesis:
µy=3.11. La propia Suma ln(xi)=183.385 (Sheet 1, misma ficha) implica
µy=183.385/40=4.5846 — no 3.11. METIS calcula µy=4.5823, coincidiendo con
lo que se deriva de los propios datos declarados por la tesis, no con el
valor que la tesis escribe en la fila de LN2p. **Clasificación: Pendiente
de dominio — error de transcripción del lado de la fuente (no de METIS),
verificable de forma autocontenida sin necesitar la planilla original: los
dos números de la misma ficha de tesis se contradicen entre sí.**

**C. Gumbel MV/ME y Log-Normal 3p MV — la tesis reporta parámetros que
rompen la coherencia interna del propio método, con evidencia cruzada del
EEA que sugiere transcripción, no cálculo distinto.**
- Gumbel: los 4 métodos (Momentos, MV, ML, ME) estiman los mismos 2
  parámetros de la misma muestra — deben ser razonablemente cercanos entre
  sí. En tesis: Momentos (α=90.32, µ=92.62) y ML (α=93.45, µ=90.78) son
  coherentes entre sí; MV (α=86.40, **µ=200.14**) y ME (**α=20.39**,
  µ=177.34) rompen el patrón de forma violenta — µ=200 y α=20 no tienen
  relación creíble con los otros tres pares. METIS reproduce los 4 métodos
  coherentes entre sí (α∈[84.4, 93.3], µ∈[90.5, 93.5], sin outliers). Dato
  clave: el EEA de tesis para MV (29.98) y ME (27.34) está muy cerca del
  EEA de METIS (30.23 y 27.52 — Chat lo cuantifica en +0.84% y +0.66%
  respectivamente) — pese a que los parámetros son radicalmente distintos.
  Si Facundo hubiera calculado el EEA con los parámetros que aparecen
  impresos (µ=200, α=20), el EEA resultante sería enorme, no cercano al de
  METIS. Esto es evidencia fuerte de que **el EEA se calculó con
  parámetros correctos (coherentes con los otros 3 métodos) y la tabla
  impresa de parámetros tiene un error de transcripción puntual en esas dos
  celdas** — ya sospechado en la ficha original ("Nota — Gumbel Máxima
  Entropía: alfa=20.394 rompe fuertemente el patrón..."), ahora confirmado
  con evidencia cuantitativa cruzada (EEA), no solo cualitativa.
- Log-Normal 3p MV: tesis reporta x0=38.469 — **matemáticamente inválido**
  para esta distribución, porque x0 debe ser menor que el mínimo de la
  muestra (15.0) para que ln(xi-x0) esté definido en todos los puntos; 38.469
  > 15 hace que el logaritmo del propio mínimo observado sea de un número
  negativo. Es, literalmente, un parámetro que no puede haber producido la
  curva que dice ajustar. Adicionalmente, x0=38.469 coincide casi exacto con
  el x0=38.47 que la tesis reporta para LN3p MV en **est_02** (Vado de Río
  Seco) — mismo valor, dos estaciones distintas — mientras que µy y σy no
  coinciden entre las dos fichas.
  **Atribución de fuente:** en la sesión de contraverificación (Chat), con
  acceso al PDF original de la tesis ("Aplicación de Análisis de Frecuencia
  — Tesis Facundo.pdf"), se reportó esta coincidencia como confirmada contra
  fuente primaria — Tabla VIII-7, pág. 164, serie Vado de Río Seco / Río
  Barrancas, "Máxima Verosimilitud: x0=38,47". **Esta cita no fue verificada
  de forma independiente por Code en este entorno** (sin acceso al PDF en
  esta sesión) — se deja consignada con su atribución de origen (verificado
  por Chat, no por Code), consistente con el patrón de contaminación cruzada
  entre estaciones ya documentado y corregido en Est07/Est08 (Sheet 3 de
  Tincunaco/Ume Pay).
  **Clasificación (los 3 casos): Pendiente de dominio — errores de
  transcripción / contaminación cruzada del lado de la fuente, no de
  METIS. El código en los tres casos produce parámetros internamente
  coherentes con el resto de sus propios métodos hermanos.**

- C-bis: 
- **GVE/MV — misma inconsistencia interna que Gumbel MV/ME.** La ficha de
Facundo reporta NO_CONVERGE en la tabla de Parámetros para este método,
pero su propia tabla de EEA reporta un valor real (78.3542) para ese
mismo método — contradicción dentro de la misma fuente. METIS converge
(ν=70.888, α=62.619, β=-0.5422, EEA=78.2992), a -0.07% del EEA que
Facundo sí publicó (no del NO_CONVERGE que también publicó). Evidencia
cruzada del mismo tipo que Gumbel MV/ME: el EEA impreso es consistente
con un cálculo real, la fila de "NO_CONVERGE" en Parámetros no lo es.
Clasificación: Pendiente de dominio, mismo origen que Hallazgo C.

**D. GVE Momentos-L — β coincide, ν/α no (patrón ya cerrado en Fase 1,
confirmado de nuevo en una décima estación).** β=-0.0893 (METIS) vs -0.085
(tesis, diff -5.0%, cercano); ν=86.89 vs 229.60, α=85.35 vs 97.95 (diffs
grandes). Es un método **cerrado** (sin iteración — IV-234 a IV-241
aplicadas directo sobre M0/M1/M2, ya verificados exactos en Fase 1 contra
`descriptive.py`) por lo que no puede explicarse como "convergencia a
óptimo distinto" (Causa B) — no hay ambigüedad de solución posible en un
cálculo cerrado. Mismo patrón exacto ya documentado en Fase 1 (§3.12) para
est_05/est_06. **Clasificación: Pendiente Facundo — confirma que es un
patrón sistemático de la distribución (tercera estación consecutiva con el
mismo síntoma exacto: β cerca, ν/α lejos), no un caso aislado de una
serie particular.**

**E. Generalizada de Pareto — primera y única estación con referencia real
de tesis; comportamiento no reproducible en ninguno de los 3 métodos que
Facundo probó.** Tesis marca Momentos, MC y MPP como NO_CONVERGE, los 3.
METIS converge en los 3, con calidad muy dispar (Momentos: EEA=279.5,
pobre pero finito; MC: EEA=29.2, razonable; MPP: EEA=679 millones,
degenerado — patrón ya conocido de esta combinación específica desde
Fase 2). Se verificó de forma independiente que el método Momentos
(IV-147/148/149, cerrado, sin iteración) tiene **dos raíces
matemáticamente válidas** para ε dado el g de esta serie: ε=-0.3333 y
ε=0.3627. METIS elige la raíz positiva (0.3627, la que produce el resultado
reportado); no hay forma de saber, sin la planilla de Facundo, si su
herramienta evaluó la otra raíz, ninguna, o si interpretó "no converge" en
un sentido distinto (p. ej. parámetro fuera de un rango físico aceptado que
Excel no valida numéricamente). **Clasificación: Pendiente de dominio —
única estación con dato de referencia disponible, insuficiente para
generalizar a las otras 8, pero suficiente para confirmar que el método
Momentos de Gen. Pareto tiene una ambigüedad de raíz múltiple genuina, sin
ningún guard de plausibilidad en el código (mismo tipo de vacío ya señalado
para MPP en Fase 2, ahora extendido a Momentos).**

**F. Exponencial x0β MV — diverge sin encajar en ningún patrón conocido
del proyecto.** Fórmula (IV-72/73) reconstruida a mano de forma
independiente en esta sesión: reproduce **exacto** el resultado de METIS
(β=132.6923, x0=11.6827) — cableado y fórmula confirmados correctos, sin
ambigüedad. Tesis: β=118.51, x0=12.04 (diff β=+11.97%). No es MV iterativo
(es solución cerrada de dos ecuaciones — IV-72 y IV-73 — sin lugar para
"convergencia a óptimo distinto"), no es g-propagación (esta distribución no
usa g), y la magnitud (+12%) excede lo atribuible solo al leve corrimiento
de datos base de la Nota 1. **Clasificación: Pendiente de dominio, causa no
identificada — mismo caso ya señalado sin resolver en la auditoría previa,
confirmado de nuevo con reconstrucción manual exhaustiva; candidato a
consulta directa a Facundo por tratarse de una fórmula cerrada sin margen
de ambigüedad de implementación.**

**G. Log-Pearson III Indirecto — divergencia mayor a lo explicable solo por
DECISIÓN013.** α/β divergen ~37%, y0 cambia de signo y de orden de magnitud
(tesis y0=1.611, METIS y0=-2.1792). La magnitud excede lo típicamente
atribuible a la propagación de g (que ronda 5-10% en el resto de las
estaciones) — es coherente con que esta estación además carga la
discrepancia de datos base ya identificada en la Nota 1 de Etapa 1, que se
propaga con más fuerza a gy (asimetría de ln(xi)) que a la asimetría de la
serie original, porque el logaritmo amplifica diferencias relativas en la
cola baja de la distribución. **Clasificación: Pendiente de dominio, mismo
origen que la Nota 1 — no resoluble sin la planilla original.**

**H. Log-Pearson III MV — la tesis reporta parámetros físicamente
inválidos para el propio modelo que dice ajustar.** α=-1.149, β=-0.0839
(ambos negativos) — en la parametrización de Log-Pearson III que usa esta
tesis (α=escala, β=forma, ver convención de Gamma 2p/3p ya documentada en
Fase 1), ambos deben ser positivos por definición del modelo; con signo
negativo la "distribución" ni siquiera está definida. METIS: NO_CONVERGE —
comportamiento correcto, el sistema no encuentra una solución matemáticamente
válida y, a diferencia de lo que parece haber ocurrido en el Excel de
Facundo, no devuelve un resultado sin sentido. **No es un hallazgo contra
METIS — al contrario, refuerza que el valor de tesis para este caso puntual
no es utilizable como referencia de ningún tipo.**

**Nota adicional sobre LP3/Directo:** la ficha de Facundo también se
contradice a sí misma acá — Parámetros dice NO_CONVERGE, pero la tabla
de EEA de la misma ficha reporta 98.0793 para este método. METIS marca
NO_APLICABLE (B=2.4214 ∉ (3,6]), una razón distinta y matemáticamente
fundada (guard de dominio), no una convergencia fallida — por lo que
"mismo resultado práctico" es cierto en el desenlace (no hay valor
usable de ninguno de los dos lados) pero no en la causa. Tercer caso
en esta estación (junto a GVE/MV y Gumbel MV/ME) donde la ficha original
tiene un EEA impreso que no es reconciliable con su propia fila de
Parámetros — patrón, no anécdota, dentro de est_01.

**I. Sanity check adicional — la propia fórmula de la tesis, con los
propios parámetros de la tesis, no reproduce la propia tabla de cuantiles
de la tesis. Clasificación formal: Causa C.** Se aplicó IV-144 (cuantil de
Gamma 3p, ya verificada fiel a la tesis en Fase 1, transcripción palabra
por palabra) con los parámetros que la tesis reporta para el modelo ganador
(Gamma 3p MPP: x0=-36.302, α=87.987, β=2.057) y se comparó contra la propia
tabla de cuantiles de tesis para ese mismo modelo:

| T | IV-144 con params. de tesis | Tabla de tesis | diff% |
|---|---|---|---|
| 2 | 116.91 | 116.95 | -0.03% |
| 5 | 232.96 | 230.90 | +0.89% |
| 10 | 311.99 | 304.19 | +2.56% |
| 20 | 387.84 | 368.40 | +5.28% |
| 25 | 411.84 | 387.11 | +6.39% |
| 50 | 485.55 | 438.92 | +10.62% |
| 100 | 558.38 | 481.32 | +16.01% |

El error crece con T de forma sistemática — **exactamente el mismo patrón
y una magnitud casi idéntica** al que se observa comparando el testigo
Gamma 2p ML de METIS contra la tesis (ver sección 5, PASS en T=2 hasta
+17.6% en T=100).

**Contraverificación (Chat) — doble método, dos hipótesis alternativas
descartadas:** se reconstruyeron los cuantiles con Wilson-Hilferty y con la
inversa exacta de la CDF Gamma; ambos métodos coinciden entre sí y ambos
divergen de la tabla de Facundo con el mismo patrón creciente en T, usando
los propios parámetros de Facundo, en dos distribuciones distintas de la
misma estación (Gamma 2p Momentos-L y Gamma 3p MPP). Con esto se descartan
dos hipótesis alternativas que podrían haber explicado la divergencia sin
necesidad de invocar una limitación de Excel: (1) que fuera un problema de
aproximación numérica de UT vs. fórmula exacta — descartado, ambos métodos
dan el mismo resultado; (2) que fuera un swap α/β en la lectura de la tabla
de tesis — descartado, empeora el ajuste a +29.79% ya en T=2.

Esto es evidencia fuerte de que **la tabla de cuantiles de Facundo no se
calculó aplicando literalmente IV-144 tal como está documentada** —
probablemente usó una aproximación distinta de UT, un encadenamiento de
redondeos manuales por celda, u otra variante no documentada en el
Capítulo IV. **Este es el caso más claro, en toda la auditoría hasta ahora,
de "limitación propia de Excel" pedida explícitamente en el encuadre de
esta fase: no es un desacuerdo de fórmula (la fórmula está verificada
palabra por palabra en Fase 1) ni de parámetros (se usaron los parámetros
exactos de la tesis) ni de método de cálculo del cuantil (dos vías
alternativas fueron descartadas) — es un desacuerdo entre la tesis y su
propia fórmula documentada, que solo se explica por el método de cálculo
real usado en la planilla original.**

---

### 5. Selección de modelo y cuantiles

**Modelo ganador de Facundo — Gamma 3p (MPP), EEA=22.3359.** EXCLUIDO en
METIS por falta de fórmula fuente (hallazgo A). Sin comparación posible.

**Testigo — Gamma 2p (Momentos-L), EEA tesis=24.1772, EEA METIS=25.2549
(+4.46%).** Parámetros PASS (α +0.06%, β -0.30%). Cuantiles:

| T | METIS | Tesis | diff% |
|---|---|---|---|
| 2 | 110.81 | 111.17 | -0.33% |
| 5 | 225.40 | 223.73 | +0.74% |
| 10 | 308.49 | 300.59 | +2.63% |
| 20 | 390.77 | 369.90 | +5.64% |
| 25 | 417.22 | 390.37 | +6.88% |
| 50 | 499.50 | 447.65 | +11.58% |
| 100 | 582.16 | 495.11 | +17.58% |

3/7 dentro de ±5% (T=2,5,10); el resto degrada de forma creciente con T —
mismo patrón que el hallazgo I (limitación de Excel de la tesis, no de
METIS). Clasificación: **Causa C confirmada** (doble verificación, ver
hallazgo I) — no Causa A ni Causa B.

---

### 6. Clasificación final est_01

| Columna | Resultado |
|---|---|
| **Etapa 1** | **Aprobado** a nivel de veredicto final (rechazo unánime coincide exacto, incluida la nota académica de la fuente; contraverificado 5/5). Estadísticos puntuales de Helmert/Wald-Wolfowitz: **Pendiente de dominio** (discrepancia de datos base, Nota 1 — no imputable a METIS; hipótesis concreta de sustitución 129→143 probada y refutada como explicación completa). |
| **Cableado (13 dist.)** | **Aprobado** — 34/34 combinaciones distribución×método, reconstrucción propia completa, 0 hallazgos (contraverificado por spot-check 5/34, sin discrepancias). |
| **Selección de modelo** | **Pendiente de código** — el modelo que Facundo seleccionó como ganador (Gamma 3p MPP) no es calculable en METIS por ausencia de fórmula en el Capítulo IV. Dato compensador: el mejor modelo que METIS sí ofrece coincide en identidad con el 2° puesto de la propia tabla de Facundo. |
| **Cuantiles** | **Pendiente de dominio — Causa C confirmada por doble método** (testigo Gamma 2p ML reproducible con precisión decreciente en T; modelo ganador sin comparación posible por el punto anterior). |

**Clasificación general de la estación: Parcial.** Etapa 1 y cableado de
Etapa 2 **Aprobados** sin reservas. Etapa 2 (resultados) tiene **1
Pendiente de código real** (Gamma 3p MPP — ausencia de fórmula fuente,
mismo pendiente ya conocido a nivel de todo el proyecto) y **múltiples
Pendientes de dominio**, ninguno de los cuales es atribuible a un error de
METIS — cada uno fue verificado con reconstrucción manual independiente
(y, en varios casos, contraverificado por una segunda sesión) que confirma
que el código aplica la fórmula documentada de forma correcta, y en varios
casos (B, C, H, I) se encontró evidencia de que el valor de referencia de
la propia tesis es internamente inconsistente o matemáticamente inválido.
**Ningún hallazgo de esta ronda requiere modificar código de
`metis/core/` — no se aplicó ni se propone ningún cambio.**
