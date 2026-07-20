# Pendientes para Facundo — Auditoría de Regresión METIS

## Decisiones implementadas que requieren confirmación

### Pregunta relacionada a DECISIÓN 013 — Fórmula de asimetría (g)
METIS usa IV-4/IV-5 (ddof=0). Facundo usó Excel SKEW() (ddof=1).
Impacto: diferencia de ~4% en g que se propaga a LP3 Indirecto
y LN3p Momentos. GVE Momentos tiene problema separado — ver sección
"GVE Momentos — beta no reproducible" más abajo.
Pregunta: ¿La implementación correcta de METIS debe usar IV-4/IV-5
o replicar el comportamiento de Excel SKEW()?

### Pregunta relacionada a DECISIÓN 011 — Partición de Cramer (n_w1, n_w2)
METIS usa ceil(n×0.60) para n_w1 y round(n×0.30) para n_w2.
Inferido del comportamiento numérico de la tesis. La tesis no
explicita la regla de redondeo.

Evidencia por estación:
| n   | n×0.30 | METIS round() | Facundo | Coincide |
|-----|--------|---------------|---------|----------|
| 24  | 7.2    | 7             | 7       | ✓        |
| 36  | 10.8   | 11            | 11      | ✓        |
| 41  | 12.3   | 12            | 12      | ✓        |
| 39  | 11.7   | 12            | 13      | ✗        |

Para n=39: n×0.30=11.7 → round=12, pero Facundo usó 13 (=n/3=13.0
exacto para este caso). No hay fórmula única consistente entre
todas las estaciones auditadas.

Pregunta: ¿Qué función usás en Excel para calcular n_w1 y n_w2?
Para n=39 en particular, ¿por qué usaste 13 en lugar de 12?
¿Aplicás REDONDEAR, ENTERO, o mirás n/3 directamente?

**ACTUALIZACIÓN 14/07/2026 (Fase 4, est_07) — el mismo problema aparece
en n_w1, no solo en n_w2.** DECISIÓN011 daba por confirmado que n_w1
usa `ceil(n×0.60)`, respaldado en est_02 (n=24) y est_04 (n=36). Pero
est_04 nunca pudo distinguir `ceil` de `round`: n×0.60=21.6, y tanto
`ceil(21.6)` como `round(21.6)` dan 22 — coincidencia que no discrimina
entre las dos reglas. est_07 (n=19) sí discrimina, y contradice la regla:

| n  | n×0.60 | ceil() | round()/floor() | n_w1 real (Facundo) | Coincide con |
|----|--------|--------|------------------|----------------------|---------------|
| 24 | 14.4   | 15     | 14               | 15                   | **ceil**      |
| 36 | 21.6   | 22     | 22               | 22                   | ambas (no discrimina) |
| 19 | 11.4   | 12     | 11               | 11                   | **round/floor** |

Verificado a mano contra la serie real de est_07: con n_w1=11,
τ1=-0.16779 y tw1=0.82742 — coincide exacto con la tesis. Con n_w1=12
(la regla `ceil` que usa el código hoy), τ1=-0.19317, tw1=1.07787 — no
coincide. **No existe una única regla de redondeo (ni `ceil`, ni
`round`, ni `floor`) que reproduzca los n_w1 confirmados de las tres
estaciones a la vez** — est_02 necesita específicamente `ceil` (no
`round`, que daría 14, no 15) y est_07 necesita específicamente
`round`/`floor` (no `ceil`, que daría 12, no 11). Mismo tipo de
inconsistencia ya documentada arriba para n_w2 (n=39), ahora confirmada
también para n_w1 con un segundo par de estaciones contradictorias.

Pregunta ampliada para Facundo: además de n_w2, ¿qué función usás para
n_w1? Con los datos de est_02 (n=24→15) y est_07 (n=19→11), ¿qué
fórmula de Excel reproduce las dos a la vez?

**CORRECCIÓN (15/07/2026) — censo completo, no es empate 1 a 1.** El
párrafo de arriba solo comparaba est_02 y est_07, dando la impresión de un
empate entre `ceil` y `round`. Censo real contra las 7 series de est_01 a
est_07 (`_cramer_bloque()` real, verificado por Code y recontrastado por
Chat):

| Estación | n | n×0.6 | ceil | round=floor | ¿Discrimina? | Reproduce tesis |
|---|---|---|---|---|---|---|
| est_01 | 40 | 24.00 | 24 | 24 | No | único candidato |
| est_02 | 24 | 14.40 | 15 | 14 | **Sí** | **ceil** |
| est_03 | 41 | 24.60 | 25 | 25 | No | — |
| est_04 | 36 | 21.60 | 22 | 22 | No | — |
| est_05 | 39 | 23.40 | 24 | 23 | **Sí** | **ceil** |
| est_06 | 38 | 22.80 | 23 | 23 | No | — |
| est_07 | 19 | 11.40 | 12 | 11 | **Sí** | **round/floor** |
| est_08 | 43 | 25.80 | 26 | 26 | No | único candidato (frac=.8, no discrimina) |

Solo 3 de 8 estaciones discriminan entre `ceil` y `round` para n_w1 (las
demás tienen fracción ≥0.5, donde `ceil==round`, y no aportan evidencia
entre las dos reglas). De esas 3: **2 confirman `ceil`** (est_02, est_05) y
**1 lo contradice** (est_07) — no es un empate, es una regla mayoritaria con
una excepción real. Dato adicional: est_02, est_05 y est_07 tienen las tres
una fracción `n×0.6` de exactamente `.4` — y aun así 2 redondean hacia
arriba (contra la convención estándar) y 1 hacia abajo (con la convención).
Descarta cualquier hipótesis simple de redondeo basada solo en la fracción.
No cambia el código (`ceil` sigue siendo la regla implementada, es la
mayoritaria confirmada). Detalle completo en
`regresion-e2e/est_07-e2e.md`.

**ACTUALIZACIÓN (15/07/2026, est_09) — deja de ser mayoría, es empate real.**

| Estación | n | n×0.6 | ceil | round=floor | ¿Discrimina? | Reproduce tesis |
|---|---|---|---|---|---|---|
| est_08 | 43 | 25.80 | 26 | 26 | No | único candidato (frac=.8) |
| est_09 | 7 | 4.20 | 5 | 4 | **Sí** | **round/floor** (τ_w1=0.36220 con n_w1=4, coincide con tesis 0.36219; n_w1=5 da 0.42415, no coincide) |

Con est_09 (n=7, `n×0.6=4.2`, fracción `.2` — no `.4` como las tres
anteriores, así que tampoco es un patrón de fracción específica) el censo
de estaciones que discriminan pasa de 3 a **4**, y el resultado queda
**empatado 2 a 2**: est_02 y est_05 confirman `ceil`; est_07 y est_09
contradicen con `round`/`floor`. Ya no corresponde describir esto como
"regla mayoritaria con una excepción" — es un empate genuino entre las dos
convenciones, sin ninguna preferencia estadística clara entre `ceil` y
`round` para n_w1. El código sigue sin cambiar (`ceil`, la regla ya
implementada, no tiene más respaldo que la alternativa). Pregunta para
Facundo reforzada: con 4 estaciones de evidencia real (no 1, no 3), ¿qué
función de Excel reproduce las 4 a la vez? Detalle completo en
`regresion-e2e/est_09-e2e.md`.

Nota: no cambia ningún veredicto de homogeneidad en ninguna de las
estaciones auditadas — Cramer aprueba con cualquiera de las dos
particiones en todos los casos verificados hasta ahora. Es un hallazgo
de precisión de fórmula, no de resultado práctico.

---

## Fórmulas con comportamiento no reproducible

### Gen. Exponencial — Método Momentos (IV-77)
METIS produce alpha=0.625, lambda=0.0116 para est_03.
Tesis reporta alpha=0.76, lambda=0.0023 — internamente inconsistente
(CV(alpha=0.76)=1.131 ≠ CV_datos=1.238; lambda=0.0023 implica µ=362 ≠ 62.39).
Presente también en est_04.
Pregunta: ¿Qué fórmula usaste para resolver IV-77? ¿Hay una tabla
o aproximación numérica que no figura en el capítulo?

**NOTA 10/07/2026:** las referencias a "est_04" en esta sección y en
las tres siguientes (Gen. Exp. Momentos-L, LP3 Directo, LN2p, Gamma 3p
x0>min) no fueron cruzadas contra los datos de est_05/est_06 auditados
en esta sesión — no coinciden los parámetros de referencia con ninguna
de las dos series que tengo a mano, así que no puedo confirmar ni
corregir la numeración acá. Dado que ya se encontró al menos un caso
de rotulado cruzado dentro de este mismo archivo (ver corrección en
la tabla de GVE Momentos, más abajo), recomiendo un repaso manual de
la numeración de estación en estas cuatro secciones antes de
consolidar todo para Facundo.

**ACTUALIZACIÓN 15/07/2026 — confirmado con verificación de CV explícita en
est_07 y est_08, sin ambigüedad de numeración.** Mismo patrón: el α de
METIS reproduce exacto el CV real de los datos (CV=S/x̄); el α de tesis no.
est_07: CV_datos=0.53816, CV_teórico(α_METIS=4.778)=0.53816 exacto;
CV_teórico(α_tesis=2.69)=0.663 (diff +23.2%). est_08: CV_datos=0.56288,
CV_teórico(α_METIS=4.200)=0.56288 exacto; CV_teórico(α_tesis=2.26)=0.70985
(diff +26.1%, la mayor divergencia de este chequeo en las 8 estaciones
auditadas). El método (comparar CV teórico de IV-77, vía digamma/trigamma,
contra el CV real de la serie) es más riguroso que la nota anterior — no
depende de qué estación es cuál, solo de la serie y el α reportado.

### Gen. Exponencial — Método Momentos L (IV-83/84)
METIS produce lambda negativo (est_03: -0.013, est_04: -0.00013).
Tesis reporta lambda negativo también en est_03 (-0.0069) pero con
magnitud diferente.
Pregunta: ¿Hay alguna restricción de signo o dominio en IV-84 que
no está explicitada en el texto?

### LP3 Método Directo — restricción B ∈ (3, 6]
METIS aplica NO_APLICABLE cuando B ∉ (3, 6] (est_03: B=2.63).
Facundo reporta parámetros y EEA=64.37 para el mismo caso.
Pregunta: ¿Aplicás algún guard sobre B, o calculás los parámetros
independientemente del valor de B?

**ACTUALIZACIÓN 15/07/2026 — dos estaciones más con el mismo desacuerdo.**
est_07 (B=2.7302) y est_08 (B=2.7178), ambas fuera de (3,6], con la tesis
reportando parámetros y EEA reales en las dos (est_07: α=0.359, β=0.158,
y0=3.884, EEA=26.4022; est_08: α=0.036, β=157.69, y0=4.967, EEA=76.4185).
Son ya 3 estaciones (est_03, est_07, est_08) con B fuera de rango donde la
tesis reporta valores de todas formas — la pregunta original sigue sin
resolver, ahora con más evidencia de que no es un caso aislado de est_03.

### Log-Normal 2p — NO_APLICABLE sin ceros en la serie
Facundo reporta NO_APLICABLE para LN2p en est_03 y est_04 aunque
la serie no tiene ceros. METIS calcula EEA normalmente.

**NOTA 10/07/2026:** en est_06 (Las Tapias) el patrón se rompe —
la tesis SÍ reporta EEA=7.4379 para LN2p ahí, sin marcar NO_APLICABLE.
El criterio de Facundo para esta restricción no es universal entre
estaciones. Ver también sección "Discrepancias en EEA — Causa C" más
abajo, donde LN2p en est_06 queda catalogado como Causa C (params
casi idénticos, EEA diverge) en vez de NO_APLICABLE.

Pregunta: ¿Bajo qué condición marcás LN2p como no aplicable? ¿Por qué
no se aplica en est_06 si sí se aplicó en est_03/est_04?

### Gamma 3p — parámetros calculados con x0 > min(serie)
Facundo reporta parámetros para Gamma 3p Momentos y MPP en est_03
y est_04 aunque x0 > min(serie), pero marca EEA=NO_APLICABLE.
METIS marca NO_APLICABLE desde la estimación de parámetros.
Pregunta: ¿Calculás los parámetros aunque x0 > min, y solo
inhibís el EEA? ¿O es otro criterio?

---

## Discrepancias en EEA sin explicación (Causa C)

**ACTUALIZADO 10/07/2026:** las filas de Gamma 2p y LN3p MV ya NO son
"sin acceso al código fuente no son verificables" — se reconstruyeron
desde cero (serie real de est_05 y est_06 + fórmula de cuantil
documentada, IV-135 para Gamma 2p y IV-120 para LN3p + posiciones de
ploteo Weibull) y en ambos casos el EEA reconstruido coincide con
METIS, no con la tesis. Esto no resuelve la discrepancia — la mueve:
ya no es "no sabemos si es bug de METIS", es "confirmado que no es bug
de METIS, el EEA de referencia de Facundo no sale de aplicar la
fórmula documentada a sus propios parámetros". Ver detalle numérico
en las dos entradas nuevas más abajo.

| Distribución     | Método    | EEA METIS | EEA Tesis | Estaciones     | Estado 10/07/2026 |
|------------------|-----------|-----------|-----------|----------------|--------------------|
| Gamma 2p         | Momentos  | 8.958 (est_05) / 6.460 (est_06) | 12.086 (est_05) / 6.965 (est_06) | est_02, est_03, est_05, est_06 | Verificado en est_05/06 — ver abajo |
| Gamma 2p         | MV        | distinto  | distinto  | est_02, est_03, est_05, est_06 | Sin verificar en est_02/03 |
| Gamma 2p         | ML        | distinto  | distinto  | est_02, est_03, est_05, est_06 | Sin verificar en est_02/03 |
| LN2p             | Momentos  | distinto  | distinto  | est_02, est_03, est_06         | Ver nota LN2p arriba (no universal) |
| LN3p             | MV        | 8.774 (est_05) / 8.736 (est_06) | 5.784 (est_05) / 7.204 (est_06) | est_05, est_06 (antes "est_03") | Verificado — ver abajo |
| Normal           | Momentos  | distinto  | distinto  | est_02, est_03 | Sin verificar |
| Normal           | ML        | distinto  | distinto  | est_03         | Sin verificar |

Pregunta general: ¿Podés compartir el archivo Excel con las fórmulas
de cálculo de EEA para estas distribuciones?

### Verificación Gamma 2p Momentos EEA — 10/07/2026
Reconstruido desde cero con la serie real (est_05, n=39 y est_06, n=38),
posiciones de ploteo Weibull (T=(n+1)/m) y cuantil Wilson-Hilferty (IV-135):

| Estación | EEA con params tesis (reconstruido) | EEA con params METIS (reconstruido) | METIS reportó | Tesis reportó |
|----------|--------------------------------------|--------------------------------------|----------------|----------------|
| est_05   | 8.949                                | 8.957                                | 8.958          | **12.086**     |
| est_06   | —                                    | 6.460                                | 6.460          | **6.965**      |

En los dos casos la reconstrucción (con cualquiera de los dos juegos
de parámetros — son casi idénticos) coincide con METIS, no con la
tesis. No es Causa A (params ya casi idénticos, la diferencia de `g`
no alcanza para explicar esta magnitud de diferencia en EEA).

### Verificación LN3p MV EEA — 10/07/2026
Misma metodología, con cuantil IV-120:

| Estación | EEA con params tesis (reconstruido) | EEA con params METIS (reconstruido) | METIS reportó | Tesis reportó |
|----------|--------------------------------------|--------------------------------------|----------------|----------------|
| est_05   | 8.792                                | 8.775                                | 8.774          | **5.784**      |
| est_06   | —                                    | 8.736                                | 8.736          | **7.204**      |

Se probaron además posiciones de ploteo alternativas (Cunnane, Hazen,
Gringorten) para est_05 buscando si alguna reproducía el EEA de la
tesis — ninguna se acerca (valores de 92 a 99, claramente incorrectos
para esa combinación). Weibull sigue siendo la posición correcta
documentada y la única que reproduce algo coherente (que resulta ser
el número de METIS).

---

## Bugs corregidos durante la auditoría (para información)
Estos no requieren respuesta — son correcciones internas de METIS
documentadas por si Facundo quiere revisarlas.

### Informativo — DECISIÓN 014 ya resuelta — IV-202 GVE variable reducida
El MD de fórmulas tenía IV-202 transcripta incorrectamente como
(xi-ν)/(α·β) en lugar de β·(xi-ν)/α. Corregido contra rasterización
de pág. 78 de la tesis a 250 DPI. Impacto: GVE MV ahora converge
correctamente en est_03.

### LP3 MV — falsa convergencia en borde de intervalo
**ACTUALIZADO 10/07/2026 — ver DECISIÓN 019 en decisions-log.md.**
minimize_scalar con Brent acotado reportaba success=True cuando
el perfil de log-verosimilitud era monótono. Corregido con post-check
de proximidad al borde inferior en su momento; el 10/07/2026 se agregó
guard simétrico para el borde superior (aplicado y verificado contra
6 estaciones, ver decisions-log.md DECISIÓN 019). No resuelve la
discrepancia de est_06 — ver sección nueva "LP3 MV — est_06,
convergencia genuina verificada" más abajo.

---

## Fórmulas con comportamiento no reproducible (ampliación)

### LN3p MV est_05 — cuantiles no reproducibles con IV-120
IV-120 con los parámetros reportados (x0=-2.15, µy=3.3323,
σy=1.1137) produce xT≈371 para T=100. La referencia de la
tesis es 268.51. La discrepancia no es atribuible a diferencia
de parámetros — METIS con sus propios parámetros produce el
mismo resultado (~371). Origen desconocido.
Pregunta: ¿Podés verificar los cuantiles de LN3p MV para
est_05 en tu planilla original?

**NOTA 10/07/2026:** esta sección ya tenía la numeración correcta
(est_05 = Piedra Blanca) — sin cambios. Confirma además el patrón de
EEA de LN3p MV documentado arriba: mismos parámetros, resultado de
referencia no reproducible con la fórmula documentada, en dos
magnitudes distintas del cálculo (cuantiles y EEA) para la misma
estación y método.

---

### Cuantiles est_04 — error en tabla de referencia
La columna 'LP3 MMI' de la tesis contiene cuantiles calculados con IV-245
y parámetros GVE MV (nu=13.995, alpha=10.610, beta=-0.312), verificado
numéricamente al 0.05% para todos los T=2,5,10,20,25,50,100.
La columna 'GVE MV' no es reproducible con ningún parámetro GVE de est_04.
METIS calcula correctamente ambas distribuciones.
Pregunta: ¿Podés verificar la tabla de cuantiles de est_04 en tu planilla
original? Las dos columnas parecen estar intercambiadas.

**NOTA 10/07/2026:** los parámetros GVE MV citados acá (nu=13.995,
alpha=10.610, beta=-0.312) no coinciden con los de est_05 (Piedra
Blanca: nu=19.579, alpha=21.386, beta=-0.478) ni con los de est_06
(Las Tapias: nu=27.675, alpha=13.505, beta=-0.531). Es una tercera
estación que no está entre las auditadas en esta sesión — no se puede
confirmar ni corregir el rótulo "est_04" con la evidencia disponible.
Verificar directamente contra la planilla de esa estación puntual.

---

### GVE Momentos — beta no reproducible (est_02, est_03, est_05)
IV-203/IV-204 no reproducen el beta reportado por Facundo en ninguna
estación con ninguna variante de g conocida.

**CORRECCIÓN 10/07/2026:** la fila marcada "est_04" (g_tesis=1.849) se
corrige a **est_05** (Piedra Blanca) — el valor de g coincide (con
diferencia de redondeo de tercera cifra) con el g_tesis=1.838 verificado
en la auditoría de est_05 de esta sesión, y la sección "LN3p MV est_05"
más arriba, en el mismo archivo, ya usaba la numeración correcta para
la misma estación. Es una inconsistencia interna del propio documento,
no una corrección aportada desde afuera.

| Estación | g_tesis | beta IV-204(g_tesis) | beta_tesis |
|----------|---------|----------------------|------------|
| est_02   | 1.565   | -0.055               | -0.278     |
| est_03   | 3.170   | -0.188               | -0.435     |
| est_05   | 1.838–1.849 | -0.090 a -0.091   | -0.210     |
| est_06   | 1.104   | -0.056 (rama IV-203) | -0.416     |

Hipótesis agotadas: IV-203/IV-204 con g_insesgado METIS, g_tesis,
g_sesgado, 2g, g², g de variable reducida — ninguna reproduce beta.
METIS implementa IV-203/IV-204 correctamente (verificado por
rasterización de la tesis, y por auditoría de código en gve.py el
10/07/2026 — sin bugs de fórmula). El error de EEA resultante es muy
alto (est_02: 1144 vs 143; est_03: 530 vs NO_CONVERGE; est_05: 697.54
vs 41.33; est_06: 45598.69 vs 26.86).

**NOTA 10/07/2026 — hallazgo adicional, mismo patrón en otro método:**
GVE Momentos-L (método cerrado, sin iteración) presenta el mismo tipo
de discrepancia: β coincide con la tesis, pero ν y α no. Reconstruido
desde M0/M1/M2 (mismos valores que ya pasan PASS en estadística
descriptiva) en est_05 y est_06:

| Estación | Reconstrucción manual (IV-234 a IV-241) | METIS reportó | Tesis reportó |
|----------|-------------------------------------------|-----------------|-----------------|
| est_05   | ν=21.686, α=25.056, β=-0.2543             | ν=21.688, α=25.057, β=-0.2543 | ν=54.129, α=33.307, β=-0.254 |
| est_06   | ν=29.886, α=17.340, β=-0.2022             | ν=29.886, α=17.337, β=-0.2024 | ν=52.147, α=21.841, β=-0.202 |

METIS coincide exacto con la reconstrucción manual (código verificado
correcto) en las dos estaciones. La tesis no. Como el método no itera,
esto no puede explicarse como "convergencia a un óptimo distinto" —
es la fórmula aplicada literal, sin ambigüedad de código de por medio.

Pregunta: ¿Qué fuente o tabla usaste para calcular beta en GVE por
Momentos? ¿Hay bibliografía adicional al capítulo IV? Y para Momentos-L:
¿qué procedimiento usaste para ν y α si no fue aplicar IV-240/241
directo a partir de β y los M̂ ya reportados?

---

### Gamma 3p MV — parámetros de tesis no satisfacen IV-140/141 (est_06)
**NUEVO 10/07/2026.** Verificado independientemente:

- est_06: METIS NO_CONVERGE; tesis reporta x0=5.241, α=15.612, β=2.129.
  IV-142 no tiene raíz en todo el dominio válido (scan de 5000 puntos).
  Evaluando IV-140/141 directo con x0=5.241 (el de la tesis): β=2.7357,
  α=14.2352 — no coincide con lo que la tesis reporta (β=2.129, α=15.612).

**CORRECCIÓN 14/07/2026 (Fase 4, est_05-e2e.md):** la fila "est_05: mismo
patrón — parámetros de tesis no satisfacen el sistema al evaluarlo
directo" que estaba acá era incorrecta — se corrige, no se borra, para
dejar registro del error. La ficha de est_05 (Sheet 3 de la tesis) marca
Gamma 3p MV como **NO_APLICABLE**, sin ningún valor de x0/α/β reportado
— no hay parámetros de tesis contra los cuales evaluar nada, a diferencia
de est_06, que sí trae valores concretos. La afirmación de que "los
parámetros de tesis no satisfacen el sistema" no podía ser cierta para un
caso donde la tesis nunca llegó a reportar parámetros. Reverificado en
Fase 4 con escaneo fino de 200.000 puntos sobre todo el dominio de
búsqueda (`lo=xi_min-20S≈-915.52` hasta `hi=xi_min≈0.9`): el residuo de
IV-142 es negativo y monótonamente decreciente en magnitud a lo largo de
**todo** el dominio, sin un solo cambio de signo — no existe raíz
interior para esta serie, no solo "en el escaneo actual" sino en el
dominio completo evaluado punto por punto. Esto es consistente con — y
explica — el NO_APLICABLE de la propia tesis: el método simplemente no
produce una solución para esta serie, y tanto Facundo como METIS llegan
al mismo resultado práctico (sin parámetros) por el mismo motivo
matemático genuino, no por una falla de ninguna herramienta en particular.

Pregunta: ¿posible método o tabla adicional no documentada en el
Capítulo IV para este caso?

---

### LP3 MV — est_06, convergencia genuina verificada con función exacta
**NUEVO 10/07/2026.** METIS converge (β=3.695, α=0.3225, y0=2.4205,
EEA=10.9881); tesis reporta NO_CONVERGE.

Se verificó el sistema **literal** IV-257/258/259 (con `scipy.special.digamma`
exacta, sin la sustitución de Thom que usa `logpearson3.py::mv`), escaneando
5000 puntos en el dominio válido `(yi_min - 20σy, yi_min - 1e-9)`. El
sistema literal tiene raíz única en y0=2.42046, β=3.6939, α=0.3226 —
coincide hasta la tercera cifra decimal con lo que reporta METIS usando
Thom. No hay raíz espuria introducida por la sustitución: la solución
que encuentra METIS es la solución matemáticamente correcta y única del
sistema tal como está escrito en el Capítulo IV.

No es un caso de "convergencia a óptimo distinto" (no hay ambigüedad
entre varias soluciones válidas) — es una raíz única, verificada con la
función exacta, que la herramienta de Facundo no encontró pese a existir.

Pregunta: ¿por qué tu herramienta no convergió en est_06 si la solución
existe y es alcanzable?

(El guard simétrico de borde superior fue aplicado el 10/07/2026 de
todas formas — ver DECISIÓN 019 en decisions-log.md — como prevención
para otra serie donde sí ocurra una convergencia de borde real. No
resuelve este caso puntual, que no es de esa naturaleza.)

---

### Generalizada Pareto — Mínimos Cuadrados (IV-153), verificación de baja confianza
**NUEVO 10/07/2026.** A diferencia del resto del capítulo, la ecuación
IV-153 no pudo verificarse con la misma confianza que las demás —
la tipografía de la fuente (fracción con siete cantidades entremezcladas
en numerador y denominador) no cede ni con rasterización a 600 DPI.
La implementación en `gen_pareto.py` tiene una forma estructuralmente
coherente con una condición de mínimos cuadrados con zi dependiente de
ε, pero no se pudo confirmar signo por signo contra la tesis.

Dado que MC "frecuentemente no converge" según la propia tesis,
Generalizada Pareto no está en el listado original de las 12
distribuciones de IV.1, y en ninguna estación auditada MC apareció
como método seleccionado ni como testigo — se marca como pendiente
de baja prioridad, no como pregunta activa para Facundo todavía.
Si en algún momento aparece una estación con Generalizada Pareto MC
como referencia real, se cierra por verificación numérica directa en
vez de seguir intentando leer la ecuación de la fuente.

---

### Gamma 3p MV — Causa D extrema en est_08, cambia el #1 del ranking
**NUEVO 15/07/2026.** Caso más severo de "Causa C" (fórmula documentada +
parámetros idénticos a tesis, EEA no reproducible) encontrado hasta ahora.
En est_08 (Ume Pay), Gamma 3p MV converge con parámetros que coinciden con
la tesis a <0.03% (x0=34.357 vs 34.351, α=72.616 vs 72.623, β=1.684 vs
1.684), pero METIS calcula EEA=8.838 mientras la tesis reporta EEA=11.6228
para esos mismos parámetros — diff -23.96%.

Verificado por 3 vías independientes, todas dan resultados entre 8.6 y 8.8
(ninguna cerca de 11.62): (1) función real `gamma3p.cuantil()` +
`calcular_eea()` con parámetros propios de METIS → 8.838; (2) misma función
real, parámetros exactos de tesis inyectados → 8.8445 (prácticamente igual
a 1 — descarta que sea diferencia de ajuste de parámetros); (3) cuantil
exacto de la distribución Gamma vía `scipy.stats.gamma.ppf`, sin pasar por
la aproximación Wilson-Hilferty IV-144 → 8.6055 (descarta que sea un
artefacto de la aproximación IV-144).

**Consecuencia práctica:** en el ranking que expondría METIS para est_08,
Gamma 3p MV queda #1 de las 13 distribuciones — por debajo incluso del
EEA=10.599 que la tesis reporta para su propio modelo ganador (Gamma 3p
MPP, no implementable) y del EEA=10.925 del modelo que Facundo eligió
(Gumbel ML, que en el ranking de METIS queda recién en el puesto #6). Un
usuario que confiara en el ranking automático vería una recomendación
distinta de la que hizo Facundo — con el número más alejado de todos los
casos de Causa D/C documentados en el proyecto.

Pregunta para Facundo: ¿podés compartir el detalle de cómo calculaste el
EEA de Gamma 3p MV para Ume Pay? Con los parámetros que vos mismo reportás
(x0=34.351, α=72.623, β=1.684), la fórmula IV-144 aplicada a la serie de
Ume Pay da un EEA de ~8.6-8.8, no 11.6228 — verificado por tres métodos de
cálculo distintos, incluido el cuantil exacto de la Gamma sin aproximación.

Detalle completo, con las tres verificaciones paso a paso, en
`regresion-e2e/est_08-e2e.md`, Hallazgo A.

---

### Valor crítico de tabla — una cola vs. dos colas (est_08, Cramer/t-Student)
**NUEVO 15/07/2026.** La tesis imprime 1.6829 como valor crítico de Cramer
y t-Student para est_08 (GL=41). Verificado (`scipy.stats.t.ppf`) que ese
valor es el crítico de **una cola** al 5% (`t.ppf(0.95, 41)=1.6829`), no el
de **dos colas** a α/2=0.025 (`t.ppf(0.975, 41)=2.0195`) que exige Ec. III-8
y que METIS aplica de forma consistente. Las 8 estaciones auditadas hasta
ahora antes de est_08 usaban todas la convención de dos colas sin excepción
(est_02: 2.0739 para GL=22; est_06: 2.0281 para GL=36; est_07: 2.1098 para
GL=17 — los tres coinciden con `t.ppf(0.975, df)`). Es la primera vez que
el valor impreso en la fuente no sigue esa convención — inconsistencia
interna de la propia tesis entre estaciones, no de METIS. No cambia ningún
veredicto en est_08 (ambos t_w quedan del mismo lado de los dos valores
críticos posibles).

Pregunta para Facundo: ¿usaste una tabla distinta o un criterio de una
cola específicamente para Ume Pay, o es un error de transcripción puntual
de esa celda?

**ACTUALIZACIÓN (15/07/2026, est_09) — segunda confirmación, ya no es un
caso aislado de est_08.** est_09 (GL=5) imprime 2.015 como crítico de
Cramer/t-Student — verificado que `t.ppf(0.95, 5)=2.015048` (una cola)
coincide exacto, mientras `t.ppf(0.975, 5)=2.570582` (dos colas, lo que
usa METIS) no. Van 2 de 9 estaciones con esta desviación de convención.
Pregunta ampliada: ¿hay algún patrón en qué estaciones usan una cola vs.
dos colas (est_08 y est_09, las dos últimas del dataset en orden de
auditoría, ¿coincidencia o algo compartido entre ellas — por ejemplo,
ambas fueron procesadas en una sesión distinta del resto de la tesis)?

---

### Log-Normal 3p MV — causa raíz confirmada por verificación cruzada, sin fix (est_09, n=7)
**ACTUALIZADO 15/07/2026 — diagnóstico corregido, la explicación original
quedó refutada por evidencia, no solo pendiente.** `lognormal3p.py::mv`
converge a `x0=-176.5565` para est_09 — un valor físicamente implausible
(muy por debajo del mínimo de la serie, 10.99), donde la tesis reporta
NO_CONVERGE.

La primera versión de este hallazgo (Code) afirmaba que la función
objetivo era monótona hacia `lo` y que ese era el "mínimo genuino" del
dominio. **Esa afirmación era incorrecta — refutada por Octavio con
evaluación directa de la función en puntos muy cercanos a `xi_min`**
(`x0=xi_min-1e-3` hasta `xi_min-1e-13`): la función **diverge sin límite
hacia -∞** acercándose a `xi_min` (`hi`), no hacia `lo` — es la
degeneración clásica de verosimilitud no acotada de la log-normal de 3
parámetros (ya advertida en DECISIÓN020), del lado opuesto al que se
había identificado primero.

Confirmado por Code, instrumentando la llamada real a `ajustar()`
(interceptando `minimize_scalar` dentro del módulo, envolviendo la
función objetivo real sin reimplementarla): con el dominio completo tal
como está codeado hoy, Brent evalúa 37 puntos, **ninguno a menos de 71
unidades de `hi`** — converge en una región donde la función es casi
plana (varía de 15.222934 a 15.366018 en 116 unidades) por su tolerancia
de convergencia, sin haber explorado nunca la zona donde realmente se
derrumba. Confirmado también que forzar `minimize_scalar` con bounds
mucho más ajustados cerca de `hi` tampoco resuelve el problema — Brent se
conforma con puntos intermedios sin llegar al verdadero comportamiento.

**Conclusión verificada por ambas partes con la función real, no
descripción aceptada de una sola:** la función no tiene mínimo finito en
este dominio. `x0=-176.56` no es un óptimo genuino ni una falsa
convergencia de borde en el sentido de DECISIÓN019 (donde sí existe un
óptimo real cerca de un borde) — es simplemente donde Brent se detiene en
una región casi plana sin haber visto la parte relevante del dominio. Es
un modo de falla distinto a los dos ya resueltos en el proyecto
(DECISIÓN019 para `logpearson3.py`, DECISIÓN023 para `gamma3p.py`) — no
corresponde calcar ninguno de esos dos guards sin pensarlo para esta
forma específica.

**Estado: causa raíz confirmada por verificación cruzada independiente.
Sin fix propuesto** — el modo de falla es distinto a los dos precedentes
del proyecto y amerita pensarse aparte, no copiarse. Detalle completo en
`regresion-e2e/est_09-e2e.md`, Hallazgo B.

**RESUELTO — 15 de Julio de 2026 (DECISIÓN 025, decisions-log.md).**
Octavio aprobó el prototipo (verificación propia contra las 9 series,
incluida inspección manual de casos con argmin cercano al borde en
est_01/est_07). Aplicado a `lognormal3p.py::mv`: guard de "ausencia de
óptimo finito" vía escaneo grueso (mismo mecanismo de DECISIÓN023, criterio
distinto — el mínimo del escaneo no debe caer exactamente en el primer o
último punto finito). Verificado sin regresión contra las 9 estaciones
llamando a `ajustar()` real: est_01 a est_08 dan parámetros idénticos a
los ya reportados antes del fix; est_09 ahora da `NO_CONVERGE`, coincidiendo
con la tesis. `pytest tests/` → 109 passed, 1 failed (mismo failing
preexistente de `gen_pareto/mc`, sin relación). Ya no queda ninguna
pregunta abierta para Facundo sobre este caso puntual — era un problema
de implementación de METIS, no de interpretación de la tesis, y quedó
resuelto sin necesitar su intervención. Detalle completo en
`decisions-log.md`, DECISIÓN 025, y en `regresion-e2e/est_09-e2e.md`.

---
### Correcciones pendientes post-auditoría (verificadas, no aplicadas) - 09/07/2026

#### Anderson k_max — ceil(n/3)
APLICADO — 9 de Julio de 2026, Auditoría Fase 1 Bloque 2.1. Ver DECISIÓN 016
en decisions-log.md.

Implementación anterior: n//3 (división entera)
Corrección aplicada: ceil(n/3), en `metis/core/etapa1/independence.py`
Fundamento: confirmado en dos Excels de Facundo. La tesis define
"k = 1,2,...,n/3" y Facundo aplica ceil consistentemente cuando
n/3 no es entero exacto (confirmado n=40 en ambos Excels).
Casos no reproducibles con ninguna fórmula: n=24 (Facundo=9,
ceil=8) y n=39 (Facundo=14, ceil=13) — pendiente confirmar con
Facundo si hubo error manual en esos casos.
Impacto: diferencia de 1 lag en k_max para algunos n. Verificado tras
aplicar el fix: 6/6 estaciones (est_02 a est_07) mantienen el veredicto
"aprobada" documentado por la tesis, incluidas est_03/est_06/est_07 donde
floor(n/3)≠ceil(n/3) (ver DECISIÓN 016 para el detalle estación por
estación).

#### Wald-Wolfowitz — exclusión de valores iguales al valor de corte
APLICADO — 9 de Julio de 2026, Auditoría Fase 1 Bloque 2.1. Ver DECISIÓN 017
en decisions-log.md — reclasificado tras revisión puntual del Excel de
Facundo (ver nota de fundamento más abajo, corregida).

Implementación anterior: todos los valores se clasificaban como
éxito (>media) o fracaso (<media), sin exclusión de empates.
Corrección aplicada: excluir de n, n1, n2 y del cálculo de rachas los
valores exactamente iguales a la media, en
`metis/core/etapa1/independence.py::calcular_wald_wolfowitz`. Esos
valores no clasifican como éxito ni como fracaso.

Fundamento (corregido — NO es herencia confirmada de Facundo): se había
anotado acá que esta regla estaba "confirmada en Excel de Facundo (TP1
Estadística 2013)". Al consultar puntualmente ese Excel (dataset
Despeñaderos, n=40, media=64.902756), se determinó que ningún valor de
esa serie coincide con la media — el caso de empate nunca se dispara en
los datos que Facundo proporcionó, y su Excel asigna binario estricto
(> media → 1, < media → 0) sin manejo visible de igualdad. Eso no prueba
una convención del autor porque el caso nunca ocurrió ahí. No existe
evidencia, en ningún recurso de Facundo (tesis ni Excel), de que él haya
aplicado o necesitado aplicar esta regla.

Es una **decisión de diseño propia de METIS**, no una convención
heredada del autor: se aplica por fundamento estadístico independiente
— tratamiento estándar de "ties" en pruebas de corridas según literatura
consolidada (Gibbons & Chakraborti, *Nonparametric Statistical
Inference*; Wald & Wolfowitz, formulación original), donde un valor
exactamente igual a la media no aporta información direccional y no
debe forzarse a ninguna de las dos categorías.

Nota: el caso est_03 (n=40 en lugar de n=41) NO se explica por
este mecanismo — el valor excluido (35.0) no coincide con la
media (62.39). Ese caso sigue siendo off-by-one en rango Excel,
sin resolver.
Decisión de diseño no explicitada en la fuente original: el warning
TEST_WARNING_SMALL_SAMPLE (n≤40) ahora se evalúa sobre el n efectivo
(tras excluir empates), no sobre len(serie) original — es el n que
efectivamente alimenta la aproximación normal de la prueba, por lo que
es el criterio internamente consistente. Verificado con test dedicado
(serie con n=42 original que baja a n=40 efectivo tras excluir 2 empates
con la media → warning se activa).
Tests actualizados/agregados: test_wald_empates_con_media_se_excluyen_de_la_serie,
test_wald_empates_con_media_reducen_n_bajo_umbral_small_sample
(tests/unit/core/test_independence.py).

#### LP3 MV — guard de borde superior
APLICADO — 10 de Julio de 2026. Ver DECISIÓN 019 en decisions-log.md.

El guard actual protegía únicamente contra falsa convergencia en el
borde inferior del intervalo de búsqueda. Se agregó el guard simétrico
para el borde superior. Verificado contra 6 estaciones sin regresiones
(17 tests preexistentes fallando, no relacionados — propagación de
DECISIÓN 013 en `_skewness`, documentados aparte).

No resuelve la discrepancia de est_06 (ver sección "LP3 MV — est_06,
convergencia genuina verificada con función exacta" más arriba) — ese
caso no era de borde disfrazado, es una convergencia genuina a una
solución que la tesis no encontró.

---

## Pendientes trasladados desde los archivos de implementación (18/07/2026)

Movidas acá desde `core-etapa1-implementation.md` y
`core-etapa2-implementation.md` durante la reorganización de esa sesión —
son preguntas a Facundo, no documentación de comportamiento de código, y
por eso viven acá en vez de en los archivos de implementación.

### Mann-Kendall — Tabla A.4, valor crítico de S para n=7
El valor crítico de S para n=7 no está confirmado por Facundo. La prueba
retorna `no_ejecutada` con `TEST_NOT_EXECUTED_CONDITION` para n=7 hasta
que se confirme.
Pregunta: ¿Cuál es el valor crítico de S para n=7 en la Tabla A.4 de
Mann-Kendall a α=5%?

### Etapa 2 — ¿ME y MC = Mínimos Cuadrados Estándar y Corregidos?
La tabla de métodos por distribución (IV.1) lista ME (Máxima Entropía,
confirmado para Gumbel, IV-190 a IV-198) y MC (Mínimos Cuadrados,
confirmado para Generalizada de Pareto, IV-153 a IV-155) sin aclarar si
MC admite variantes (Estándar y Corregidos) o si aplican a otras
distribuciones además de las ya confirmadas.
Pregunta: ¿MC tiene variantes "Estándar" y "Corregidos"? ¿ME y MC aplican
a alguna otra distribución fuera de Gumbel y Generalizada de Pareto
respectivamente?

### Etapa 2 — comportamiento ante ceros de 5 distribuciones
Pendiente de confirmación el comportamiento ante series con ceros
(`caudal_precipitacion`) para: Gamma 3p, Exponencial (x₀, β),
Generalizada de Pareto, Log-Normal 3p, Generalizada Exponencial.
Implementadas hoy con `PENDING_ZEROS_CONFIRMATION = True` visible en el
código (ver `metis/core/etapa2/distributions/__init__.py`), tratadas
como `disabled_zeros` hasta recibir confirmación — no se asume
comportamiento.
Pregunta: ¿estas 5 distribuciones deben deshabilitarse ante ceros (mismo
tratamiento que Log-Normal 2p, Log-Pearson III, Gamma 2p y Exponencial β),
o alguna admite un comportamiento distinto (por ejemplo, un método
alternativo de estimación que sí tolere ceros)?

### Normal y Log-Normal 2p — Tabla IV-1 solo lista MV, no Momentos
Movida acá desde `decisions-log.md` (bloque sin número de decisión,
migración a archivos individuales, 18/07/2026) — es una pregunta abierta,
no una decisión cerrada, por eso no correspondía vivir ahí.

Tabla IV-1 de la tesis lista Normal y Log-Normal 2p solo bajo MV, no bajo
Momentos. Pendiente confirmar con Facundo si es porque Momentos y MV
coinciden (y por eso se listan como uno solo) o si Momentos no debe
implementarse como método separado.

Actualmente ambas distribuciones tienen `METODOS_APLICABLES = ("momentos",
"mv")` con estimadores idénticos.
Pregunta: si Facundo confirma que deben listarse como un solo método,
¿corresponde eliminar "momentos" del tuple y dejar solo "mv"?