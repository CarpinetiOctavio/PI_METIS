# Auditoría Fase 3 — Integridad de Suite de Tests (Etapa 2)
### Estado — Cerrado al 13/07/2026

---

## Contexto y alcance

Esta auditoría es posterior y separada de:
- **Fase 1** (fidelidad de código a la tesis, `fase1-unitarias.md`) — CERRADA.
- **Fase 2** (cableado/integración de Etapa 1, en curso en otro chat) — Etapa 1
  de cableado cerrada (Bloques 1-5); Etapa 2 de cableado bloqueada hasta que
  esta Fase 3 cierre.

**Importante — qué es y qué no es esta auditoría:** esta sesión NO reabre ni
repite la verificación de fidelidad a la tesis. Esa verificación ya está hecha
y cerrada (Fase 1, `fase1-unitarias.md`, DECISIÓN 022). Cuando en el detalle
por archivo de más abajo se dice que un método "reproduce lo que dice la
tesis", eso es un subproducto necesario para clasificar la causa de una
falla de test — no una re-auditoría de fidelidad ni una re-certificación de
"cerrado — fiel a la tesis". Esa etiqueta pertenece a Fase 1 y no se reutiliza
acá.

El objeto de esta Fase 3 es exclusivamente: para cada uno de los 17 tests
fallando en `backend/tests/unit/core/etapa2/`, determinar si la causa es

- **(a)** el código de la distribución está mal → se reabre Fase 1 para ese
  archivo puntual, con autorización explícita antes de tocar
  `metis/core/etapa2/distributions/`, o
- **(b)** el test quedó desactualizado o mal escrito respecto a decisiones ya
  tomadas → se corrige el test, no el código.

## Origen

Durante Fase 2 (cableado), al correr la suite completa tras un fix de Etapa 1,
aparecieron 17 tests fallando en 6 archivos:
`test_gamma2p.py`, `test_gamma3p.py`, `test_gve.py`, `test_lognormal3p.py`,
`test_logpearson3.py`, `test_gen_pareto.py`. Confirmado con `git status`/`git log`
que ninguno de los 6 archivos de test fue commiteado nunca (quedan como `??`,
untracked) — no hay historial git real, solo `mtime` de filesystem como proxy
(27/05/2026 para 5 de los 6, 27/05/2026 también para el sexto con unos minutos
de diferencia), anterior al commit que aplicó DECISIÓN013 al código
(`b0b9196`, 18/06/2026). Consistente con la hipótesis de que los tests quedaron
congelados en una versión previa del código o de convenciones internas, pero
no se asume — se verifica archivo por archivo.

## Fuente autoritativa

La misma que Fase 1: tesis escrita de Facundo Ganancias Martínez (Cap. III,
IV, VIII). El Excel de Facundo no es autoritativo cuando difiere (DECISIÓN
013). Rasterización a 250 DPI mínimo (600 si la densidad tipográfica lo
exige) antes de aceptar una hipótesis de fórmula nueva — OCR no es
aceptable. Para fórmulas ya ancladas en Fase 1, no hace falta re-rasterizar;
se cita el ancla existente.

## Anclas heredadas de Fase 1 (no re-derivar)

- DECISIÓN013: g (asimetría) usa ddof=0 (IV-4/IV-5), no ddof=1.
- DECISIÓN015: LN3p, IV-116, exponente 1/2 en sigma_y, no 1/4.
- IV-123/IV-124 (Gamma 2p): α=escala=S²/x̄, β=forma=(x̄/S)² — invertido
  respecto a la convención más común.
- `_ut()` (Abramowitz-Stegun, IV-102 a IV-105): constantes universales,
  confianza máxima, ya validada en Fase 1 §3.5 (Normal).
- `_skewness` reimplementada localmente en 5 de las 6 distribuciones de este
  barrido (gamma3p, gve, lognormal3p, logpearson3, gen_pareto) — verificado
  bit-idéntico a `descriptive.py` en Fase 1. No es causa de falla por sí
  sola, pero es la razón por la que cada archivo puede tener su propia
  convención de cálculo de `g` a mano dentro del test (punto de atención
  recurrente en este barrido).

## Framework de clasificación

- **Categoría (a) — bug de código:** el test está bien, el código no
  reproduce la tesis. Reabre Fase 1 para ese archivo puntual. Requiere
  autorización explícita antes de tocar `distributions/`.
- **Categoría (b) — bug de test:** el código reproduce la tesis
  correctamente (verificado con reproducción numérica propia, no aceptado
  de Code sin más), el test tiene la fórmula, la etiqueta o el valor
  hardcodeado mal. Se corrige el test.
- **Sin causa identificada (pendiente):** ni (a) ni (b) se puede confirmar
  todavía — falta información (fixture real, git log, `_ut`/`utils.py` reales,
  etc.) o el valor no es reproducible por ninguna vía razonable agotada. No
  se cierra el archivo hasta resolver esto. No se asume (b) por descarte ni
  se fuerza una Categoría 1/2/3 de Fase 1 si el caso no es genuinamente una
  ambigüedad tesis-vs-Excel (ese framework es de Fase 1, no aplica
  automáticamente acá).

## Reglas de operación (no negociables, heredadas de Fase 1/Fase 2)

- Ningún fix se aplica sin aprobación explícita de Octavio.
- No se acepta ningún reporte de Code sin reproducción numérica propia,
  contra la serie/fixture real correspondiente.
- No se aprueba ningún fix sin ver el fragmento exacto de código real —
  nunca un resumen o paráfrasis.
- No se avanza al archivo siguiente sin cerrar (o dejar explícitamente
  pendiente, documentado) el archivo actual.
- No se clasifica una discrepancia como "sin causa identificada / pendiente"
  sin agotar antes las hipótesis internas razonables (swap de parámetros,
  método equivocado, exponente/fórmula alternativa, valores de p/T
  alternativos, etc.).
- Los resultados de esta auditoría se cargan en este documento
  (`fase3-testing.md`), no en `docs/decisiones/` — esas decisiones son de Fase 1.
  Si algún hallazgo de esta Fase 3 termina reabriendo Fase 1 (categoría a),
  ESE fix sí se loguea como una decisión nueva en `docs/decisiones/` como
  corresponde, con referencia cruzada a esta sección.

## Estado global de avance

**Cierre: de 17 tests fallando originalmente a 1 sin resolver (pendiente
documentado), con 3 pendientes anotados en total (ninguno bloqueante) y
cero cambios en `metis/core/etapa2/distributions/` en toda la auditoría —
confirmado con `git diff --stat` archivo por archivo. Suite completa final:
109 passed, 1 failed (el pendiente de `gen_pareto.py`, fallando de forma
intencional y documentada).**

| Archivo | Tests fallando (de 17) | Estado | Pendientes documentados |
|---|---|---|---|
| `test_gamma2p.py` | 3 | **CERRADO — 4/4 en verde** | — |
| `test_gamma3p.py` | 4 | **CERRADO — 4/4 en verde** | gap de cobertura: método `mv` sin test |
| `test_gve.py` | 2 | **CERRADO — 7/7 en verde** | — |
| `test_lognormal3p.py` | 3 | **CERRADO — 3/3 en verde** | — |
| `test_logpearson3.py` | 3 | **CERRADO — 5/5 en verde** | test vacío: `directo_alpha_hat_formula` (B fuera de rango, assert nunca corre) |
| `test_gen_pareto.py` | 2 | **CERRADO — 4/5, 1 sin resolver** | `mc_q100` sin resolver — posible singularidad evitable en IV-153/154, cruza con Fase 1 §3.10 (IV-153 no legible ni a 600 DPI) |

---

## Detalle por archivo

### `test_gamma2p.py` — CERRADO

Módulo auditado: `metis/core/etapa2/distributions/gamma2p.py`.
Fixture: `serie_facundo` (n=40, x̄=42.7675, S=17.7261, Fase 1 no lo había
usado con estos decimales — reproducido independientemente acá).

**1. `test_gamma2p_momentos_parametros_serie_facundo` — categoría (b).**
El test calcula `alpha_esp=(x̄/S)²` y `beta_esp=S²/x̄` — invertido respecto
a IV-123 (α=escala=S²/x̄) / IV-124 (β=forma=(x̄/S)²). El propio comentario
del test delata la confusión de convención. Confirmado estructuralmente
(no depende de la serie): el código siempre calculará lo opuesto de lo que
el test espera, para cualquier dato de entrada.
Fix propuesto: `alpha_esp = S**2/xbar`, `beta_esp = (xbar/S)**2`.

**2. `test_gamma2p_ml_parametros_serie_facundo` — categoría (b).**
Reproducción numérica propia contra `serie_facundo`: código da
alpha=7.5504 (escala, IV-134), beta=5.6643 (forma, IV-126/IV-130). El
test tiene los dos valores correctos pero asignados a la clave contraria
(`assert alpha==5.6643, beta==7.5504`).
Fix propuesto: intercambiar las claves — `alpha≈7.5504`, `beta≈5.6643`.

**3. `test_gamma2p_ml_z_correcto_pi_tau2_cuadrado` — sin acción.**
No estaba entre los 17 fallando (confirmado por Code: PASSED en la corrida
original). Verificado igual que la fórmula IV-131 (z=π·τ2²) coincide con
el código. No se toca.

**4. `test_gamma2p_ml_q100_serie_facundo` — categoría (b), origen del valor
hardcodeado sin identificar.**
El test espera q100=95.2016 (abs=1e-1). Reproducción independiente con
`_ut()` real (`metis/core/etapa2/utils.py`, Abramowitz-Stegun IV-102/105) y
los parámetros ML ya confirmados (alpha=7.5504, beta=5.6643) da **95.3259**
— confirmado además contra la salida cruda de pytest en runtime real
(`Obtained: 95.32591472488642`), sin drift entre lo auditado y lo ejecutado.

Hipótesis descartadas antes de dejarlo como "sin causa identificada" (no se
fuerza cierre sin agotarlas):
- Swap de alpha/beta → 87.10 (más lejos, no).
- Parámetros de Momentos → 94.48 (no entra en tolerancia).
- Parámetros de MV/Thom → 91.14 (no).
- Exponente 2 en vez de 3 en IV-135 → 72.98 (no).
- Barrido de p entre 0.90 y 0.999 → ningún p limpio da 95.2016; el p exacto
  que lo reproduciría es 0.9899 (T≈98.93), no es un valor redondo ni sugiere
  un error de T=100 vs T=50 u otro caso limpio.
- Fórmula histórica pre-fix de IV-131 (z=π²·τ2, la que el propio test #3
  documenta como versión incorrecta) → tau2 cae fuera del rango válido de la
  aproximación, no genera un beta utilizable.

**Conclusión de este punto:** no hay combinación de parámetro, método, p o
exponente que reproduzca 95.2016. No es un caso de ambigüedad tesis-vs-Excel
(no aplica framework Causa A/B/C de Fase 1) — es un valor de test sin origen
reproducible. Fix propuesto: reemplazar el valor hardcodeado por 95.3259
(con la tolerancia que Code prefiera mantener). No requiere consulta a
Facundo — no es una ambigüedad de fórmula.

**Estado final `test_gamma2p.py`:** 3 tests con fix de test aprobado pendiente
de aplicación por Code, 1 sin acción. Ninguno reabre Fase 1.

---

### `test_gamma3p.py` — CERRADO

Módulo auditado: `metis/core/etapa2/distributions/gamma3p.py`.
Fixture: `serie_facundo`. 4 tests en el archivo, los 4 en la lista de los 17,
los 4 cubren únicamente método `momentos` (ver hallazgo de cobertura al
final — no hay ningún test de método `mv` en el archivo).

**Causa raíz única para los 4 tests: el test recalcula `g` (asimetría) con
la convención de Excel (ddof=1), no con IV-4/IV-5 (ddof=0, DECISIÓN013).**

- `g_código` (IV-4/IV-5, ddof=0, `_skewness()` interno del módulo) =
  **0.847313** — coincide exacto con el valor ya anclado en Fase 1 para esta
  misma serie (confianza cruzada alta).
- `g_test` (fórmula recalculada a mano dentro de cada test, usa `S` con
  ddof=1 — es literalmente la fórmula de Excel `SKEW()`) = **0.815738** —
  coincide exacto con lo adelantado en el diagnóstico preliminar de Code.
- Ratio entre ambos: 0.9627 = `((n-1)/n)^1.5` exacto — firma algebraica del
  bug de convención, no casualidad ni redondeo.

**1. `test_gamma3p_momentos_alpha_raiz_beta` — categoría (b).**
El nombre sugiere que testea la raíz cuadrada de IV-138 (α̂=S/√β̂, no S/β̂),
y esa parte está bien en ambos lados. Falla porque el `g` que calcula a
mano usa la convención equivocada, lo que produce un `beta` distinto y por
lo tanto un `alpha_esp` distinto al que da el código real.

**2. `test_gamma3p_momentos_x0_raiz_beta` — categoría (b).**
Mismo root cause exacto que el punto 1, aplicado a IV-139.

**3. `test_gamma3p_momentos_parametros_serie_facundo` — categoría (b).**
Hardcodeados (beta=6.0112, alpha=7.2299, x0=-0.6927) coinciden **exacto**
con lo que da la fórmula usando `g_test` (convención Excel) — confirma que
se generaron con la convención equivocada, no que vengan de otra fuente.
Código real da: beta=5.5715, alpha=7.5098, x0=0.9269.

**4. `test_gamma3p_momentos_q100_serie_facundo` — categoría (b).**
Hardcodeado (94.3179) coincide **exacto** (94.31791966...) con el cuantil
calculado usando los parámetros bugueados del punto 3. Con los parámetros
correctos del código: q100=94.6964. A diferencia del q100 de `gamma2p.py`,
acá no queda ningún residuo sin explicar — el root cause único explica los
4 tests sin excepción.

**Fix propuesto (los 4 tests):** reemplazar el cálculo manual de `g` por
la fórmula IV-4/IV-5 (ddof=0) ya anclada, y recalcular los valores
hardcodeados con esa convención: beta≈5.5715, alpha≈7.5098, x0≈0.9269,
q100≈94.6964. Oportunidad de aprovechar para importar `_skewness` desde
`descriptive.py` en vez de reimplementarla (pendiente de cableado ya
anotado en Fase 1, punto 4 — no obligatorio en esta ronda, pero si Code
toca el archivo igual por el fix de aserciones, puede resolverlo de paso).

**Estado final `test_gamma3p.py`:** 4/4 tests con causa (b) confirmada y
fix propuesto. Ninguno reabre Fase 1.

**Hallazgo aparte, fuera de alcance de esta ronda — laguna de cobertura:**
`gamma3p.py` implementa método `mv` (`METODOS_APLICABLES = ("momentos", "mv")`,
IV-140 a IV-143), pero no existe ningún test de `mv` en el archivo — ni
pasando ni fallando, directamente ausente. Es una ausencia de cobertura,
no una aserción incorrecta; no encaja en el framework (a)/(b) de esta Fase 3
(que clasifica causas de falla de tests existentes, no cobertura faltante).
Queda anotado, sin resolver acá — a decidir en otro momento si se agrega el
test de `mv` ahora, en una sesión de refactor/cobertura dedicada, o cuando
Code toque el archivo por los fixes de arriba.

### `test_gve.py` — CERRADO

Módulo auditado: `metis/core/etapa2/distributions/gve.py`.
Fixture: `serie_facundo` + una serie sintética propia en un test. 7 tests en
el archivo, 2 en la lista de los 17 (confirmado con corrida aislada, número
por número contra la reproducción propia).

Mismo root cause que `gamma3p.py`: convención de `g` (ddof=1 Excel-style en
el test vs ddof=0 IV-4/IV-5 en el código).

**1. `test_gve_momentos_parametros_serie_facundo` — categoría (b).**
Con `g_código` (0.847313) el código da: nu=34.8565, alpha=14.1620,
beta=0.0191. El test espera nu=34.8922, alpha=14.3234, beta=0.0284 —
coincide **exacto** con la fórmula usando `g_test` (0.815738).
Fix aplicado por Code: `nu≈34.8565, alpha≈14.1620, beta≈0.0191`.

**2. `test_gve_momentos_g_en_rango_iv204_usa_polinomio_correcto` — categoría (b).**
Variante distinta del mismo bug: usa una serie sintética propia (no
`serie_facundo`), calcula su propio `g` con la convención bugueada y deriva
`beta_iv204` dinámicamente a partir de ese `g`, comparando con tolerancia
muy ajustada (`abs=1e-6`). `g_test`=4.651940 vs `g_código`=4.795071 — ambos
caen en el mismo rango IV-204 (no es problema de selección de rama), pero
el polinomio de 5to grado amplifica la diferencia: beta_test=-0.244094 vs
beta_código=-0.249061, diff=0.00497, muy por encima de la tolerancia.
Fix aplicado por Code: corregir la línea de cálculo de `g` dentro del test
a ddof=0 — al ser un valor derivado dinámicamente, no hizo falta
hardcodear un nuevo beta.

**Sin acción, confirmado con reproducción, no forman parte de los 2 fallando:**
- `test_gve_momentos_converge_serie_facundo` — solo chequea `STATUS_OK`, no
  depende de precisión de `g`.
- `test_gve_ml_converge_serie_facundo` — ídem, método `ml` no usa `g`
  (usa Momentos-L).
- `test_gve_ml_q100_serie_facundo` — reproducción independiente con
  Momentos-L (M0/M1/M2 → E → beta → A/B/C/D → alpha/nu → cuantil) da
  **109.05410264...**, coincide exacto con el hardcodeado 109.0541.
- `test_gve_cuantil_beta_cero_retorna_gumbel` y
  `test_gve_cuantil_p_fuera_rango_levanta_error` — chequeos estructurales de
  fórmula/excepción, sin dependencia de serie ni de `g`.

**Estado final `test_gve.py`:** 2/2 tests con causa (b) confirmada, fixes
aplicados por Code y verificados en verde (7/7). Ninguno reabre Fase 1. Sin
hallazgos de cobertura nuevos en este archivo.

---

### `test_lognormal3p.py` — CERRADO

Módulo auditado: `metis/core/etapa2/distributions/lognormal3p.py`.
Fixture: `serie_facundo`. 3 tests en el archivo, los 3 en la lista de los 17.

**Causa raíz combinada, única para los 3 tests: convención de `g` equivocada
(ddof=1 Excel-style) Y exponente pre-DECISIÓN015 (0.25 en vez de 0.5) para
`sigma_y`, aplicados simultáneamente.**

Verificación exacta: calculando con `g_test`=0.815738 (bugueado) + exponente
0.25 (bugueado) se obtiene mu_y=4.166464, sigma_y=0.511025, x0=-23.956388,
q100=187.815490 — coincide **exacto** (a la 5ta/6ta cifra decimal) con los
4 valores hardcodeados en los 3 tests. Confirmado además con corrida
aislada real (sigma_y=0.27044823870824025, q100=94.81722308993048,
mu_y=4.127741997350786 — coinciden con el código correcto).

**1. `test_lognormal3p_momentos_sigma_y_cuarta_raiz` — categoría (b).**
El nombre y el docstring razonan sobre la premisa de que
σ̂y²=[ln(nz²+1)]^(1/2) (de ahí el exponente 1/4) — premisa ya descartada
por DECISIÓN015 (rasterizado, exponente correcto es 1/2 directo sobre σ̂y).
Además usa la convención de `g` equivocada. Test congelado de antes de que
DECISIÓN015 se aplicara al código, con el bug de `g` encima.
Fix aplicado por Code: corregir `g` a ddof=0 y el exponente a 0.5 (sigma_y_esp≈0.2704).
Nota dejada para Code, no bloqueante: renombrar el test y corregir el
comentario para reflejar IV-116 correctamente — no indispensable para que
pase, a criterio de Code si lo hace de una vez.

**2. `test_lognormal3p_momentos_q100_serie_facundo` — categoría (b).**
El docstring dice "calculado independientemente con IV-116 corregido" —
no lo estaba, arrastraba ambos bugs. Fix aplicado: q100≈94.8172.

**3. `test_lognormal3p_momentos_parametros_serie_facundo` — categoría (b).**
Fix aplicado: mu_y≈4.1277, sigma_y≈0.2704, x0≈-21.5810.

**Estado final `test_lognormal3p.py`:** 3/3 tests con causa (b) confirmada,
fixes aplicados por Code y verificados en verde. Ninguno reabre Fase 1.
Ambos fixes de Fase 1 (DECISIÓN013 y DECISIÓN015) confirmados correctamente
aplicados en el código — el módulo no se tocó.

---

### `test_logpearson3.py` — CERRADO

Módulo auditado: `metis/core/etapa2/distributions/logpearson3.py`.
Fixture: `serie_facundo`. 5 tests en el archivo, 3 en la lista de los 17.

**Causa raíz de 3 tests: mismo patrón de convención de `g`, aplicada sobre
`yi=ln(xi)` (no sobre la serie original).**

`gy_código` (correcto) = 0.314398. `gy_test` (bugueado, ddof=1) = 0.302682.

**1. `test_logpearson3_indirecto_alpha_raiz_beta` — categoría (b).**
`alpha_esp` con `gy_test` = 0.060135. Código real (`gy_código`) da
alpha=0.062463. Fix: corregir `gy` a ddof=0 dentro del test (valor derivado
dinámicamente, no hardcodeado).

**2. `test_logpearson3_indirecto_q100_serie_facundo` — categoría (b).**
Hardcodeado 108.7852 coincide exacto con q100 calculado usando `gy_test`.
Fix aplicado: q100≈109.1515.

**3. `test_logpearson3_indirecto_parametros_serie_facundo` — categoría (b).**
Hardcodeados (beta=43.6604, alpha=0.0601, y0=1.0515) coinciden exacto con
el cálculo usando `gy_test`. Fix aplicado: beta≈40.4671, alpha≈0.0625,
y0≈1.1493.

**Sin acción, confirmado:**
- `test_logpearson3_directo_no_aplicable_serie_facundo` — B=2.85613,
  coincide con el comentario del test, `≤3` → `STATUS_NO_APLICABLE` tal
  como espera. Método `momentos_directo` no usa `g`, no le afecta el bug.

**Hallazgo aparte, no bloqueante — test que pasa vacío:**
`test_logpearson3_directo_alpha_hat_formula` — con `seed=42` (determinístico)
la serie sintética da B=2.9677, **fuera** del rango (3, 6] que exige el
método. `res.status` da `STATUS_NO_APLICABLE`, no `STATUS_OK`, por lo que
el `if res.status == STATUS_OK:` nunca se ejecuta y el `assert` de adentro
nunca corre. El test "pasa" pero de forma vacía — nunca ejercita IV-251
(rango 3.5<B≤6) como dice su propio comentario. Confirmado por Code con
corrida real: `status: no_aplicable`, `parametros: None`. Mismo tipo de
hallazgo que el gap de `mv` en `gamma3p.py`. Queda anotado, no resuelto en
esta ronda — reconstruir una serie sintética que caiga confiablemente en
(3.5, 6] no es un fix de una línea (requiere iterar semillas o derivar la
serie analíticamente).

**Estado final `test_logpearson3.py`:** 3/3 tests con causa (b) confirmada,
fixes aplicados por Code y verificados en verde (5/5). Ninguno reabre Fase 1.

---

### `test_gen_pareto.py` — CERRADO (con 1 pendiente sin resolver)

Módulo auditado: `metis/core/etapa2/distributions/gen_pareto.py`.
Fixture: `serie_facundo`. 6 tests en el archivo, 2 en la lista de los 17.

**Confirmado sin problema:**
- `test_gen_pareto_mv_no_converge_serie_facundo` — sistema `fsolve`
  (IV-151/152) reproducido completo, no converge (residual máximo 1.09 >>
  tolerancia 1e-4), da `STATUS_NO_CONVERGE` tal como espera el test.
- `test_gen_pareto_momentos_parametros_serie_facundo` — categoría (b),
  mismo patrón de convención de `g`. Con `g_test` (0.815738): eps=0.355587,
  sigma=31.433070, mu=19.579714 — coincide exacto con el hardcodeado
  (0.3556, 31.4331, 19.5797). Con `g_código` (0.847313): eps=0.339841,
  sigma=30.780708, mu=19.794088. Fix aplicado: mu≈19.7941, sigma≈30.7807,
  epsilon≈0.3398.
- `test_gen_pareto_cuantil_epsilon_cero_usa_limite` — chequeo estructural
  de fórmula, sin dependencia de serie.
- `test_gen_pareto_mc_converge_serie_facundo` — solo chequea `STATUS_OK`,
  pasa (con la reserva del punto siguiente sobre qué tan confiable es el
  resultado subyacente del método `mc`).

**`test_gen_pareto_mc_q100_serie_facundo` — SIN RESOLVER, pendiente
documentado por decisión explícita de Octavio.**

El hardcodeado (90.6333) no coincide con ninguna raíz que el algoritmo `mc`
encuentra hoy (115.04 en reproducción propia, 384.80 confirmado con
corrida real de Code — los dos entornos difieren entre sí). No es el
patrón de convención de `g` de los demás archivos — es un problema distinto:

La ecuación IV-153/IV-154 tiene una singularidad evitable (forma 0/0)
cuando ε→0 — el denominador de σ̂ (IV-154) colapsa a cero al mismo ritmo
que el numerador. Evaluar la fórmula tal cual está escrita cerca de esa
zona implica restar cantidades de punto flotante casi iguales (cancelación
catastrófica), lo que hace que el resultado del método `mc` sea sensible a
diferencias de redondeo entre entornos — confirmado empíricamente: mi
entorno y el de Code, con el mismo código exacto, convergen a raíces
distintas (`denom_sigma` en la raíz cercana a cero da 3.39e-10 en mi
entorno, apenas por encima del guard de 1e-10 — al borde de la navaja).
No es error de transcripción, es una propiedad matemática de la ecuación
tal como está planteada.

Se cruza con el pendiente ya documentado en Fase 1 (`fase1-unitarias.md`
§3.10): IV-153 no cede ni a 600 DPI, y MC quedó cerrado "con esta
excepción" sin verificación completa. No se puede descartar que la parte
ilegible de la tesis (o IV-166, con los valores iniciales de ε y µ —
`mu_init = eps_init` en el código usa el mismo valor numérico para ambos,
lo cual es sospechoso) contenga un guard o una forma alternativa de la
ecuación que el código actual no está implementando — no se puede
confirmar sin leer esa parte.

**Decisión explícita de Octavio:** queda pendiente sin resolver, no forma
parte del cierre de esta Fase 3. `metis/core/etapa2/distributions/gen_pareto.py`
no se toca por este punto — confirmado con `git diff --stat` sin salida.
Riesgo adicional a anotar fuera de esta auditoría (no resuelto acá): el
método `mc` puede dar resultados distintos según el entorno de ejecución
para los mismos datos de entrada — relevante para producción si `mc` llega
a usarse con datos reales, más allá de este archivo de test puntual.

**Estado final `test_gen_pareto.py`:** 1/2 tests con causa (b) confirmada y
fix aplicado. El otro (`mc_q100`) queda pendiente sin clasificar (ni a ni
b) — suite final: 109 passed, 1 failed (este mismo test, fallando de forma
intencional y documentada).

---

## Pendientes abiertos (no bloqueantes, cierre de la auditoría)

Tres pendientes quedan documentados al cierre de esta Fase 3, ninguno
bloqueante para dar por cerrada la ronda de clasificación de los 17 tests
originales:

1. **Gap de cobertura — `gamma3p.py`:** método `mv` implementado
   (IV-140 a IV-143) sin ningún test, ni pasando ni fallando. A decidir si
   se agrega en una sesión de refactor/cobertura dedicada.

2. **Test vacío — `logpearson3.py`:** `test_logpearson3_directo_alpha_hat_formula`
   pasa sin ejecutar su `assert` (serie sintética con `seed=42` no cae en
   el rango que el test dice verificar). Requiere reconstruir la serie
   sintética o derivarla analíticamente para que caiga en (3.5, 6].

3. **Sin resolver — `gen_pareto.py`, método `mc`:** valor hardcodeado de
   `test_gen_pareto_mc_q100_serie_facundo` no reproducible con ninguna raíz
   que el algoritmo encuentra hoy. Cruza con el pendiente ya abierto en
   Fase 1 (§3.10, IV-153 ilegible ni a 600 DPI). Además, hallazgo de
   robustez fuera del alcance de esta auditoría: el método `mc` puede no
   ser determinístico entre entornos de ejecución distintos, por
   cancelación catastrófica cerca de una raíz espuria en ε≈0 — candidato a
   anotar en `pendientes-facundo.md` o como pendiente de cableado.

## Cierre de la ronda

De 17 tests fallando originalmente a 1 sin resolver. Los 6 archivos de
`backend/tests/unit/core/etapa2/` quedaron clasificados. Cero cambios en
`metis/core/etapa2/distributions/` en toda la auditoría — confirmado
archivo por archivo con `git diff --stat`. Ningún fix se aplicó sin
aprobación explícita de Octavio; ningún hallazgo se aceptó de Code sin
reproducción numérica propia. Fase 2 (cableado, Etapa 2) queda desbloqueada
para retomar Bloque 6/7 en la sesión correspondiente.