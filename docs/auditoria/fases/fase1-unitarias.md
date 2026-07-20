# Auditoría Fase 1 — Fidelidad a la Tesis (backend/metis/core/)
### Estado - Cerrado al 10/07/2026

Contexto: verificación aislada de cada función pública contra la tesis
de Facundo Ganancias Martínez (Cap. III, IV, VIII). NO cubre cableado ni
integración entre archivos — eso es Fase 2, sesión y chat aparte. Cualquier
hallazgo de cableado que aparezca en el camino se anota en el bloque final
"Pendientes de cableado (fuera de alcance)" tal cual se ve, sin resolverlo
ni asumir que ya está contemplado en otro lado.

Fuente autoritativa única: tesis escrita. El Excel de Facundo NO es
autoritativo cuando difiere (DECISIÓN 013, decisions-log.md).

Estado global de avance: Bloque 1 CERRADO, Bloque 2 CERRADO, Bloque 3 CERRADO
(con excepciones y pendientes explícitos documentados por sub-bloque —
ninguno bloqueante para el cierre)

---

## BLOQUE 1 — Estadística Descriptiva

Archivo: metis/core/estadistica_descriptiva/descriptive.py (ruta actualizada
tras la reorganización de directorios de core/, sesión previa)
Estado: CERRADO — FIEL A LA TESIS

Funciones auditadas:
- calcular_descriptiva()

Fix aplicado y verificado:
- Campo `rango` (máximo - mínimo) agregado a DescriptiveStats
  (metis/core/types.py) y al cálculo/retorno de calcular_descriptiva().
  Exigido por tesis IV.5.1 y RF-GEN-P-04 del Manual de Requerimientos.
  - types.py: `rango: float | None = None` agregado al dataclass.
  - descriptive.py: `rango=float(np.max(arr) - np.min(arr))` agregado
    al return de calcular_descriptiva().
  - Test agregado: tests/unit/core/test_descriptive.py::
    test_rango_es_maximo_menos_minimo — verifica contra numpy
    independiente y contra `resultado.maximo - resultado.minimo`.
  - Verificado: 7/7 tests en test_descriptive.py, 62/62 en la suite
    completa de Etapa 1, ruff limpio.

No es hallazgo (aclarado, no tocar):
- Campo `mediana` ya existe en el dataclass y ya está correctamente
  calculado y retornado. No viene de la tesis pero es válido como extra.

Verificado contra tesis (sin objeción):
- Media, varianza sesgada/no sesgada (IV-1, IV-2, IV-3)
- Asimetría sesgada/no sesgada (IV-4, IV-5)
- Curtosis sesgada/no sesgada (IV-6, IV-7)
- Desvío estándar (IV-8, aplicado sobre var. no sesgada)
- Coeficiente de variación (IV-9)
- Rango (IV.5.1, RF-GEN-P-04) — fix aplicado arriba
- Momentos de Probabilidad Pesada m0-m3 (IV-21 a IV-24) — verificado
  numéricamente, incluye criterio de orden mayor-a-menor (IV-20)

---

## BLOQUE 2 — Etapa 1 (Independencia, Homogeneidad, Tendencia y Atípicos, Veredicto)

Estado: CERRADO

Sub-bloques auditados, en este orden:
2.1 Independencia — Anderson, Wald-Wolfowitz — CERRADO
2.2 Homogeneidad — Helmert, t de Student, Cramer — CERRADO
2.3 Tendencia y atípicos — Mann-Kendall, Kolmogorov-Smirnov, Chow — CERRADO
2.4 Veredicto y nivel de confianza global — determinar_nivel_homogeneidad,
    determinar_nivel_independencia, lógica de nivel_confianza (evaluado
    como lógica de agregación, no como fórmula de tesis) — CERRADO

### 2.1 Independencia — Anderson, Wald-Wolfowitz

Archivo: metis/core/etapa1/independence.py
Estado: CERRADO — FIEL A LA TESIS (con 2 correcciones aplicadas)

Funciones auditadas:
- calcular_anderson()
- calcular_wald_wolfowitz()

Fix 1 aplicado y verificado — k_max = ceil(n/3), no floor(n/3):
- `calcular_anderson` usaba `k_max = n // 3` desde el primer commit,
  nunca corregido pese a que la auditoría de regresión ya había
  verificado `ceil(n/3)` contra dos Excels de Facundo.
  Ver DECISIÓN 016 en decisions-log.md — ambigüedad genuina del texto
  de la tesis (no conflicto tesis-vs-Excel como DECISIÓN 013), se
  adopta la convención documentada del autor.
  Verificado contra las 6 estaciones del dataset de regresión (est_02
  a est_07) — 6/6 veredictos coinciden con la tesis, incluidas
  est_03/est_06/est_07 donde floor(n/3)≠ceil(n/3).
  Test actualizado: test_anderson_un_lag_fuera_aprueba_tolerancia_10pct.
  Test nuevo: test_anderson_k_max_ceil_no_floor_est03 (serie real est_03).

Fix 2 aplicado y verificado — Wald-Wolfowitz excluye empates con la media:
- `calcular_wald_wolfowitz` clasificaba todos los valores como éxito/
  fracaso sin excluir los exactamente iguales a la media. Corregido:
  se excluyen de n, n1, n2 y del cálculo de rachas.
  Ver DECISIÓN 017 en decisions-log.md — **no** es herencia confirmada
  de Facundo (se verificó puntualmente su Excel y el caso de empate
  nunca se dispara en sus datos); es criterio propio de METIS fundado
  en tratamiento estándar de "ties" en runs test (Gibbons & Chakraborti;
  Wald & Wolfowitz original). pendientes-facundo.md corregido para no
  atribuir la regla al autor.
  Decisión de diseño adicional (no explicitada en fuente original): el
  warning TEST_WARNING_SMALL_SAMPLE (n≤40) se evalúa sobre el n efectivo
  tras excluir empates, no sobre len(serie) original.
  Tests nuevos: test_wald_empates_con_media_se_excluyen_de_la_serie,
  test_wald_empates_con_media_reducen_n_bajo_umbral_small_sample.

Verificado contra tesis (sin objeción, sin cambios):
- Estadístico r_k y valor_crítico por lag (Ec. III-1, III-3)
- Jerarquía Anderson manda sobre Wald-Wolfowitz en determinar_nivel_independencia
- TEST_WARNING_SMALL_SAMPLE para Wald con n≤40 (ejecuta, no bloquea)
- DECISIÓN 012 (umbral `math.ceil(k_max*0.10)`) — revalidada tras el
  fix de k_max, sigue reproduciendo el veredicto de la tesis (est_02 y
  est_03 como casos de control)

Verificación final: 65/65 tests de Etapa 1 pasando, ruff limpio.

### 2.2 Homogeneidad — Helmert, t de Student, Cramer

Archivo: metis/core/etapa1/homogeneity.py
Estado: CERRADO — sin hallazgos

Funciones auditadas:
- calcular_helmert()
- calcular_t_student()
- calcular_cramer()

Verificación hecha por Octavio directamente contra la tesis (Sección
III.4) en sesión/chat aparte — no por Claude en esta conversación, que
no tiene acceso al documento primario (ver aclaración metodológica
sobre Bloque 1/2.1: el chequeo de Claude solo puede contrastar contra
formulas-etapa1.md, docs/decisiones/ y los datasets de regresión, no
contra la tesis en sí).

Resultado: sin hallazgos. No se requirió ningún fix de código, ninguna
DECISIÓN nueva en docs/decisiones/, ni cambios en tests. `git diff`
sobre homogeneity.py confirma cero cambios de contenido más allá del
rename de la reorganización de directorios de `core/` (sesión previa).

No hay verificación numérica independiente de Claude para este
sub-bloque — a diferencia de 2.1 (donde se corrieron las 6 estaciones
de regresión tras cada fix), acá no hubo fix que verificar.

### 2.3 Tendencia y atípicos — Mann-Kendall, Kolmogorov-Smirnov, Chow

Archivo: metis/core/etapa1/trend.py (Mann-Kendall, KS), metis/core/etapa1/outliers.py (Chow)
Estado: CERRADO

Funciones auditadas:
- calcular_ks_tendencia() — CERRADO, ver fix abajo
- calcular_chow() (outliers.py) — CERRADO (provisorio), ver fix abajo
- calcular_mann_kendall() — CERRADO — FIEL A LA TESIS, sin cambios, ver abajo

Contexto importante para este sub-bloque, aclarado por Octavio durante
la auditoría: **Mann-Kendall, KS y Chow no están en la tesis de
Facundo** — son pruebas adicionales que Carlos (co-director) pidió
agregar. Facundo nunca las corrió, por lo que no existe ningún valor
de referencia suyo (ni tesis ni Excel) contra el cual validar
numéricamente estas tres. El estándar de auditoría para las tres pasa
a ser "implementación correcta y defendible del test con ese nombre,
según la fuente bibliográfica citada por Carlos" — no "reproduce los
números de Facundo", que no existen para estos casos.

Fix aplicado y verificado — KS: Z tipificado (Ec. A.57), no p-valor de scipy:
- Hallazgo traído por Octavio (verificación directa contra la tesis en
  sesión aparte, misma limitación metodológica que 2.2 — Claude no la
  verificó contra el documento primario).
- `calcular_ks_tendencia` calculaba D con `scipy.stats.ks_2samp` (Ec.
  A.56) y aprobaba con `p_valor > 0.05`, con una nota interna que
  afirmaba que ese criterio era "matemáticamente equivalente" a
  contrastar Z=D·√(n1·n2/(n1+n2)) contra 1.358 (Ec. A.57, Tabla A.5).
  Esa nota era incorrecta: son dos aproximaciones distintas del mismo
  test (scipy usa la distribución exacta/asintótica de KS de dos
  muestras; A.57 es una aproximación asintótica más simple con valor
  crítico fijo de tabla). Verificado numéricamente por Octavio: sobre
  500 casos sintéticos con n típico de hidrología (10-30), discrepan
  en 6 casos (1.2%).
- Corregido: se sigue el procedimiento literal de la fuente — D vía
  scipy (Ec. A.56), tipificado manualmente a Z (Ec. A.57), comparado
  contra 1.358. `TestResult.estadistico` ahora reporta Z, no D (es lo
  que efectivamente se compara contra valor_critico).
- `formulas-etapa1.md` Sección 8 corregida — ya no dice que los dos
  criterios son equivalentes.
- Tests agregados: test_ks_estadistico_es_z_tipificado_no_d (verifica
  que estadistico=Z≠D contra cálculo independiente),
  test_ks_criterio_z_difiere_de_criterio_p_valor (caso real de
  discrepancia hallado por búsqueda numérica: n1=25, n2=26, D≈0.3738,
  p≈0.0403 → criterio viejo rechazaría; Z≈1.3346≤1.358 → criterio
  nuevo aprueba; confirma que el código aplica el criterio correcto).
- Verificación: 67/67 tests de Etapa 1 pasando, ruff limpio.

Fix aplicado y verificado — Chow: K_N (Grubbs-Beck, Bulletin 17B), no
cuantil t crudo — DECISIÓN 018, PROVISORIO:
- Hallazgo propio (cross-check contra la propia nota de
  `formulas-etapa1.md`, que ya reconocía la discrepancia sin resolverla:
  "K_N de tabla, 10% significancia" vs. cuantil t crudo a α=0.05 usado
  en el código). No vino de Octavio ni de "otro chat" — surgió de leer
  la nota existente contra el código.
- `calcular_chow` comparaba `max(Z_i)` (estadístico de Grubbs) contra un
  cuantil t crudo con Bonferroni (ν=n-1, α=0.05 heredado del global de
  Etapa 1). La nota interna afirmaba que esto era "estadísticamente
  equivalente" a K_N de la tabla de Bulletin 17B — falso, verificado
  numéricamente: diferencia de 12% a 61% según n, siempre en la misma
  dirección (subestima la sensibilidad del test).
- Investigación intermedia con dos fuentes contradictorias en el repo
  (formulas-etapa1.md citaba Bulletin 17B; statistical-pipeline.md y
  core-implementation.md citaban Escalante Sandoval & Reyes Chávez 2005,
  con una fórmula distinta según confirma Octavio). Sin la fórmula de
  Escalante disponible y sin tiempo para esperar confirmación de
  Facundo/Carlos, se optó por Grubbs-Beck/Bulletin 17B por ser la fuente
  pública, citable y más rigurosa — decisión **explícitamente
  provisoria y revisable**.
- Corregido: `ALPHA_CHOW=0.10` (no 0.05), `K_N = (n-1)/√n·√(t²/(n-2+t²))`
  con `ν=n-2` (no cuantil t crudo con ν=n-1).
- Verificado: K_N(n=30)=2.745, coincide con el valor citado para la
  tabla del Apéndice 4 (no verificado contra la tabla impresa real).
- `core-implementation.md` y `statistical-pipeline.md` también
  corregidos — tenían notas que afirmaban (sin verificar) que el
  cuantil t crudo era la fórmula correcta de Escalante.
- Tests nuevos: test_valor_critico_es_k_n_no_cuantil_t_crudo,
  test_k_n_n30_aproxima_valor_tabla_referencia.
- Verificación: 69/69 tests de Etapa 1 pasando, ruff limpio.

Mann-Kendall — CERRADO, FIEL A LA TESIS, sin cambios de código:
- Se evaluó la aparente discrepancia entre Tabla A.4 del Apéndice
  (valores de una cola: 2.33/1.64/1.28 — coinciden con precisión de
  dos decimales con los Z críticos estándar de una cola para
  α=0.01/0.05/0.10: 2.326/1.645/1.282, lo cual es una fuerte señal de
  que la transcripción de la tabla es correcta) contra el `Z_crit=1.96`
  (dos colas) que usa el código.
- Resuelto por argumento estadístico verificable de forma independiente
  (no depende de confiar en ninguna fuente externa): Mann-Kendall como
  está implementado es un test bidireccional — detecta tendencia
  creciente O decreciente vía `|Z|`. Comparar `|Z|` contra un valor
  crítico de una cola equivale a correr dos tests de una cola al 5%
  cada uno, lo que infla la tasa de error real a ~10% en vez del 5%
  nominal. El valor correcto para un criterio de valor absoluto a
  α=0.05 real es el de dos colas: 1.96. El código es correcto.
- Refuerza la confianza: `aprobada` no recalcula la comparación a mano
  — usa `resultado.h` de `pymannkendall` directamente, que ya aplica
  internamente el test de dos colas correcto. `valor_critico=1.96` es
  solo el valor reportado para mostrar, no una comparación manual
  propensa a error (a diferencia de Chow y KS, donde el bug estaba
  exactamente en una comparación escrita a mano).
- Sin cambios de código, sin tests nuevos, sin DECISIÓN nueva en
  docs/decisiones/ (no hubo fix que documentar).

DECISIÓN 018 (Chow) queda abierta para revisión si Facundo/Carlos
confirman Escalante Sandoval & Reyes Chávez u otra fuente distinta de
Grubbs-Beck — es la única decisión de este sub-bloque marcada como
provisoria.

### 2.4 Veredicto y nivel de confianza global

Archivos: metis/core/etapa1/independence.py (determinar_nivel_independencia),
metis/core/etapa1/homogeneity.py (determinar_nivel_homogeneidad),
metis/core/pipeline/pipeline.py (nivel_confianza)
Estado: CERRADO — sin hallazgos

Evaluado como lógica de agregación propia de METIS contra
`statistical-pipeline.md`/`constraints.md` — no contra la tesis (esto
no es una fórmula estadística de Facundo, es diseño de negocio del
proyecto).

Funciones auditadas:
- `determinar_nivel_independencia`: Anderson manda (aprueba →
  "independiente" sin importar Wald; rechaza → "dependiente" + warning
  crítico); Wald solo agrega TEST_WARNING_SMALL_SAMPLE si corresponde.
  Coincide exactamente con constraints.md ("Anderson acepta,
  Wald-Wolfowitz rechaza → Resultado final = INDEPENDIENTE... Anderson
  manda").
- `determinar_nivel_homogeneidad`: Cramer rechaza → homogeneidad_critica
  (crítico); Cramer aprueba pero Helmert o t-Student rechazan →
  homogeneidad_warning (normal); todos aprueban → homogeneidad_ok.
  Coincide exactamente con statistical-pipeline.md.
- `nivel_confianza` (pipeline.py, líneas 102-108): coincide con el
  pseudocódigo de statistical-pipeline.md (el caso "rechazado" se
  resuelve antes, en `contract.bloqueante`).

No es hallazgo (aclarado, no tocar):
- Las dos primeras ramas de `nivel_confianza` (`any critico` / `elif
  warnings`) asignan el mismo valor `"con_warnings"` — código
  redundante (podría colapsarse a `if warnings: ... else: ...`), pero
  no afecta el resultado y el pseudocódigo fuente tiene la misma
  redundancia. Es observación de calidad de código, no de corrección —
  fuera del alcance de esta auditoría de fidelidad.

Sin cambios de código, sin tests nuevos, sin DECISIÓN nueva.

---

## BLOQUE 3 — Etapa 2 (Parámetros por distribución, EEA y cuantiles)

Estado: CERRADO

**Corrección al alcance original de este bloque:** la lista de
sub-bloques planificada más abajo en versiones anteriores de este
documento (3.1 a 3.9) no incluía dos distribuciones que sí forman
parte del barrido real: **Generalizada Exponencial** (entre
Exponencial y Normal en el orden de la tesis) y **Generalizada
Pareto** (no está en el listado original de 12 distribuciones de
IV.1, pero la tesis la desarrolla en IV.3.10 y METIS la implementa
de todas formas). El barrido real cubrió 13 distribuciones, no 9.

Verificación hecha contra rasterizado de la tesis a 250 DPI (600 DPI
en los tramos de mayor densidad tipográfica), sesión "Auditoría
Código II". Fuente autoritativa: tesis escrita, misma regla que
Bloques 1 y 2.

### 3.0 Métodos genéricos de estimación (IV.2, ecuaciones IV-1 a IV-55)

Estado: CERRADO — FIEL A LA TESIS (con 2 correcciones de documentación,
sin cambios de código)

No corresponde a una distribución específica — son los métodos que
reutilizan las 13 distribuciones (Momentos, Máxima Verosimilitud
genérica, Momentos de Probabilidad Pesada, Mínimos Cuadrados,
Momentos-L, Máxima Entropía). Verificado antes de iniciar el barrido
de distribuciones individuales.

Fixes de documentación aplicados en formulas-etapa1.md (no de código
— descriptive.py ya era correcto):
- Ec. IV-5 (asimetría no sesgada): comentario que sugería equivalencia
  con `scipy.stats.skew(bias=False)` era incorrecto — verificado
  numéricamente (diferencia de 5.94% en muestra de control). El código
  ya calcula manualmente, sin depender de scipy.
- Ec. IV-7 (curtosis no sesgada): nota que sugería "sumar +3 a
  scipy.stats.kurtosis" como alternativa válida era incorrecta —
  verificado numéricamente (diferencia de 13.95%).

Puntos dejados como pendiente de confirmación (no bloquean el cierre
de este sub-bloque):
- Coeficientes de IV-35 a IV-37 (Momentos-L, definición por orden
  estadístico) — lectura del rasterizado ambigua entre coeficiente 1/2
  constante y 1/r (convención Hosking). No bloquea: la vía operacional
  usada por el código (IV-39 a IV-42) sí está confirmada sin ambigüedad.
- Exponente de IV-47 (F² vs F³) — misma naturaleza, no se usa en código.
- Gamma 3p + MPP — Tabla IV-1 marca el método como aplicable pero el
  Capítulo IV no desarrolla las ecuaciones. Hipótesis (no confirmada):
  el método de Greenwood et al. (1979), citado como origen del MPP, es
  explícitamente para distribuciones expresables en forma inversa —
  Gamma no lo es. Pendiente Facundo, ver pendientes-facundo.md.

### 3.1 Uniforme
Estado: CERRADO — FIEL A LA TESIS, sin hallazgos. IV-58 a IV-62 verificadas.

### 3.2 Exponencial (β)
Estado: CERRADO — FIEL A LA TESIS, sin hallazgos. IV-63 a IV-67 verificadas.

### 3.3 Exponencial (x0, β)
Estado: CERRADO — FIEL A LA TESIS, sin hallazgos.
IV-68 a IV-74 verificadas, incluida la reconciliación de IV-73 (forma
expandida en la tesis vs. forma referencial `x1-β̂/n` usada en el md
de fórmulas — misma ecuación, verificado algebraicamente; no es
discrepancia).

### 3.4 Generalizada Exponencial
Estado: CERRADO — FIEL A LA TESIS, sin hallazgos de fórmula.
IV-75 a IV-89 verificadas, incluida la distinción digamma/trigamma
entre Momentos (IV-77, usa ambas) y Momentos-L (IV-83/84, solo
digamma). Pendientes activos, no de fórmula: comportamiento no
reproducible contra los valores de referencia de Facundo en IV-77
(Momentos) y en el signo de λ de IV-83/84 (Momentos-L), en más de una
estación — ver pendientes-facundo.md.

### 3.5 Normal
Estado: CERRADO — FIEL A LA TESIS, sin hallazgos.
IV-92 a IV-105 verificadas, incluidos los 6 coeficientes de la
aproximación racional de Abramowitz-Stegun para UT (constantes
universales, no específicas de la tesis — confianza máxima).

### 3.6 LogNormal 2 parámetros
Estado: CERRADO — FIEL A LA TESIS, sin hallazgos. IV-107 a IV-109 verificadas.

### 3.7 LogNormal 3 parámetros
Archivo: metis/core/etapa2/distributions/lognormal3p.py
Estado: CERRADO — FIEL A LA TESIS

Momentos (IV-111 a IV-116): sin hallazgos nuevos. Incluye el fix ya
aplicado en sesión previa (DECISIÓN 015 — exponente 1/2, no 1/4, en
IV-116).

MV: no resuelve IV-119 directo — perfila la verosimilitud sobre x0
(µy y σy analíticos por IV-117/118), método numérico distinto pero
verificado equivalente algebraicamente en el óptimo. Formalizado como
DECISIÓN 020 en decisions-log.md (Categoría 2 — sin ambigüedad de
fórmula, decisión de método ya implementada sin registro previo).

Cableado (no se resuelve acá — ver "Pendientes de cableado" al final):
`_skewness` reimplementada localmente en vez de importar de
`descriptive.py`. Matemáticamente equivalente, verificado.

### 3.8 Gamma 2 parámetros
Archivo: metis/core/etapa2/distributions/gamma2p.py
Estado: CERRADO — FIEL A LA TESIS, sin hallazgos.
IV-123 a IV-135 verificadas. Nota de convención importante (no
hallazgo): en esta distribución **α es el parámetro de ESCALA y β es
el de FORMA** — invertido respecto a la convención más común (donde
α suele ser forma). Documentado explícitamente en el código
(`docstring` y comentarios inline) y en formulas-etapa2.md, para que
no se mapee al revés al usar `scipy.stats.gamma`.

### 3.9 Gamma 3 parámetros
Archivo: metis/core/etapa2/distributions/gamma3p.py
Estado: CERRADO — FIEL A LA TESIS, sin hallazgos de fórmula.
IV-137 a IV-144 verificadas, misma convención α=escala/β=forma que
Gamma 2p. El método MV usa scan+brentq (DECISIÓN 010) sobre IV-142.
Confirmado en código (no solo en el dataset de regresión) que
reproduce, de forma independiente, el hallazgo ya documentado en
pendientes-facundo.md: IV-142 no tiene raíz en el dominio válido para
al menos dos estaciones (est_05, est_06), consistente con que los
parámetros de referencia de la tesis no satisfacen IV-140/141 al
evaluarlos directo — pendiente Facundo, no bug de código.

Cableado: `_skewness` reimplementada localmente, misma situación que
LN3p.

### 3.10 Generalizada Pareto
Archivo: metis/core/etapa2/distributions/gen_pareto.py
Estado: CERRADO — CON UNA EXCEPCIÓN EXPLÍCITA (método MC, ver abajo)

No forma parte del listado original de 12 distribuciones de IV.1 —
desarrollada en IV.3.10 e implementada de todas formas.

Momentos (IV-147 a IV-149), MV (IV-150 a IV-152, incluida la
verificación de la nota no-obvia del signo +n/σ en IV-152), MPP
(IV-167 a IV-173) y cuantil (IV-174): verificados, sin hallazgos.

**Excepción — método MC (Mínimos Cuadrados, IV-153 a IV-166) no se
pudo verificar con la misma confianza que el resto del capítulo.** La
tipografía de la fuente para IV-153 (fracción con siete cantidades
entremezcladas en numerador y denominador) no cede ni a 600 DPI — no
es un límite de esfuerzo, es un límite de cómo está impresa. La
implementación tiene forma estructuralmente coherente con una
condición de mínimos cuadrados con zi dependiente de ε (consistente
con lo que describe el texto), pero no se confirmó signo por signo.

Dado que MC "frecuentemente no converge" según la propia tesis y
nunca apareció como método seleccionado ni como testigo en ninguna
estación auditada, se cierra el bloque igual, con esto marcado como
pendiente de baja prioridad (ver pendientes-facundo.md) — no
bloqueante, verificable a futuro por vía numérica si aparece una
estación de referencia real con Generalizada Pareto MC.

Cableado: `_skewness` reimplementada localmente, misma situación que
las demás — quinta y última reimplementación encontrada en el barrido.

### 3.11 Gumbel
Archivo: metis/core/etapa2/distributions/gumbel.py
Estado: CERRADO — FIEL A LA TESIS (con 1 corrección de documentación,
sin cambios de código)

IV-177 a IV-199 verificadas, incluida la equivalencia algebraica del
criterio de convergencia de Máxima Entropía (`|δα-1|<tol` y `|δµ|<tol`
≡ `|P-0.577216|` y `|R-1|` en las condiciones de convergencia, IV-193/194).

Fix de documentación aplicado (no de código): docstring de cabecera
tenía el coeficiente de IV-184 transcripto como 1.1; el código ya
usaba 1.11 (correcto, verificado contra rasterizado). Mismo patrón que
el fix de rangos en gve.py — comentario desactualizado, lógica correcta.

Cableado: M̂(1) (MPP, IV-87) reimplementado con un tercer estilo de
indexado (serie ascendente, pesos `arange(n)`) distinto de gve.py y
gamma2p.py (ambos descendentes). Verificado algebraicamente
equivalente a los otros dos — mismo término reindexado, no bug.

### 3.12 GVE (General de Valores Extremos)
Archivo: metis/core/etapa2/distributions/gve.py
Estado: CERRADO — FIEL A LA TESIS (con 1 corrección de documentación,
sin cambios de código nuevos en esta ronda — DECISIÓN 014 ya estaba
aplicada de sesión previa)

IV-200 a IV-245 verificadas.

Fix de documentación aplicado (no de código): docstring de cabecera
tenía los límites de los rangos IV-203/IV-204 con el punto decimal
corrido (11.396 en vez de 1.1396) y describía un "overlap" entre
rangos que no existe en la lógica real — el código ya usaba los
valores correctos (`-11.35 < g < 1.1396` / `1.14 < g < 18.95`),
verificado contra rasterizado. Se dejó documentado además el hueco
real y angosto que sí existe (g entre 1.1396 y 1.14 → NO_APLICABLE,
fiel a la tesis, no corregido sin autorización de Facundo).

Verificado con reconstrucción manual completa (no solo lectura de
código) en dos estaciones: Momentos-L (método cerrado, sin iteración)
reproduce exacto la fórmula IV-234 a IV-241. Como el método no itera,
la discrepancia con los valores de referencia de la tesis (β coincide,
ν/α no) no puede explicarse como "convergencia a óptimo distinto" —
queda documentada como pendiente Facundo, no como hallazgo de código
(la clasificación previa de "Causa B" para este caso queda revisada).

Momentos: el polinomio IV-203/204 en sí reproduce exacto los
coeficientes de la tesis (confirmado coeficiente por coeficiente en
las dos ramas); el β de referencia de Facundo no es reproducible con
ninguna variante de g conocida en ninguna estación auditada —
pendiente Facundo, no bug de `_beta_from_g`.

Cableado: `_skewness` reimplementada localmente (verificado
bit-idéntico a `descriptive.py` en 2000 pruebas aleatorias, diferencia
máxima 0.0); `_momentos_L` (M0/M1/M2, IV-242 a IV-244) también
reimplementada localmente, con un estilo de indexado propio, distinto
del de gamma2p.py y gumbel.py.

### 3.13 Log-Pearson III
Archivo: metis/core/etapa2/distributions/logpearson3.py
Estado: CERRADO — FIEL A LA TESIS (con 1 fix de código aplicado)

Momentos Directo (IV-247 a IV-254, incluida verificación de que la
reescritura de signo de IV-249 en el código es equivalente algebraica
a la forma de la tesis) y Momentos Indirecto (IV-255/256): sin
hallazgos.

Fix de código aplicado y verificado — guard simétrico de borde
superior en método MV: ver DECISIÓN 019 en decisions-log.md. Corrige
que el guard de falsa convergencia solo protegía el borde inferior del
intervalo de búsqueda. Aplicado y reproducido contra las 6 estaciones
del dataset de regresión sin regresiones.

MV no resuelve IV-257/258/259 directo — sustituye la aproximación de
Thom (IV-126, la misma que usa gamma3p.py) dentro de un perfil de
verosimilitud sobre y0. Método numérico distinto, formalizado como
DECISIÓN 021 (Categoría 2). Reforzado por verificación adicional
puntual: en la estación con discrepancia conocida (tesis reporta
NO_CONVERGE, METIS converge), el sistema literal con digamma exacta
(sin la sustitución de Thom) tiene raíz única, coincidente hasta la
tercera cifra decimal con el resultado que da la sustitución — no hay
raíz espuria introducida por el método numérico distinto. La
discrepancia contra la tesis en ese caso puntual queda como pendiente
Facundo (¿por qué su herramienta no convergió si la solución existe?),
no como bug de guard ni de método.

Cableado: `_skewness` reimplementada localmente, misma situación que
las demás distribuciones afectadas.

---

## Entregable final de esta sesión

Bloques 1, 2 y 3 cerrados. Insumo completo para Fase 2 (integración y
cableado) — ver `pendientes-cableado-fase2.md` más abajo para el
detalle consolidado que Fase 2 debe tomar como punto de partida.
Resumen de decisiones de arquitectura formalizadas o corregidas en
esta ronda de Bloque 3: DECISIÓN 019, 020, 021, 022 (decisions-log.md).

---

## Pendientes de Cableado — Insumo para Fase 2 (Integración)

Contexto: estos hallazgos surgieron durante la auditoría de fidelidad
de fórmula a la tesis, archivo por archivo. No son errores de
fórmula — cada función, aislada, es fiel a su fuente. Son dependencias
entre archivos, supuestos no validados sobre el orden o forma de los
datos que llegan desde otras partes del pipeline, o duplicación de
lógica genérica entre módulos.

Ninguno de estos puntos fue resuelto en esta auditoría. Se documentan
tal cual se observaron, sin asumir que ya están contemplados o en
proceso de corrección en otro lado.

### 1. `calcular_cramer` — orden de `arr` para `arr[-n_w:]`
(Bloque 2, Etapa 1)

**Archivo:** `metis/core/etapa1/homogeneity.py`

La función toma "los últimos n_w datos" mediante `arr[-n_w:]`, asumiendo
que corresponden a los últimos n_w datos en orden **cronológico**
(exigido por III-9/III-11/III-12 de la tesis: "n60 = últimos 60% de
los valores de la muestra", "n30 = últimos 30%").

La función no ordena `arr` ni valida su orden en ningún punto interno.
Depende enteramente de que `serie` llegue ya ordenada cronológicamente
ascendente desde quien la invoque (pipeline.py o equivalente).

**Verificar en Fase 2:** confirmar que la serie que llega a
`calcular_cramer` está garantizada en orden cronológico ascendente en
todo call site del pipeline, y no en algún otro orden (por ejemplo,
orden de mayor a menor, que sí se usa en otras funciones de METIS como
MPP en estadística descriptiva — confirmar que no hay confusión de
convención entre módulos).

### 2. Asimetría de superficie: `calcular_t_student` vs `calcular_cramer`
(Bloque 2, Etapa 1)

**Archivo:** `metis/core/etapa1/homogeneity.py`

`calcular_t_student(serie, n1, n2)` recibe la partición mitad/mitad
como parámetros externos (`n1`, `n2`) y **no valida internamente** que
cumplan la condición de III-8 (n1 ≈ n2 ≈ n/2). Confía ciegamente en
que el caller calcule y pase la partición correcta.

`calcular_cramer(serie, particion)` en cambio **calcula su propia
partición** (60%/30%) internamente, sin depender de un caller externo
para eso.

Esta asimetría es el mecanismo exacto que ya causó el bug conocido en
`pipeline.py` (reutilización de la partición de Cramer, pensada para
60%/30%, pasada por error a `calcular_t_student`, que exige 50%/50%) —
ver contexto completo en el md rector de Fase 2.

**Verificar en Fase 2:**
- Confirmar el fix del bug ya conocido en pipeline.py (partición
  correcta 50/50 llega a calcular_t_student).
- Evaluar si conviene agregar una validación interna a
  `calcular_t_student` (assert o warning si `n1`/`n2` no son
  aproximadamente iguales) para que este tipo de error de cableado se
  detecte en el momento en vez de propagarse silenciosamente.

### 3. Partición fija mitad/mitad en `calcular_ks_tendencia`
(Bloque 2, Etapa 1)

**Archivo:** `metis/core/etapa1/tendencia_atipicos.py`

La función divide la serie con `mitad = n_total // 2`, sin aceptar una
partición externa. La tesis (A.5.2 del Apéndice Caamaño Nelli &
Colladon) permite submuestras `n` y `m` genéricas, no necesariamente
iguales ("de los valores Xi disponibles se identifican previamente dos
muestras X1...Xn y Xn+1...Xn+m").

No es un error de fórmula — la partición mitad/mitad es un caso válido
de lo que permite el texto — pero es una limitación de flexibilidad:
si en algún punto del pipeline se necesitara pasar una partición
distinta (análogo a lo que sí permite `calcular_t_student` con sus
parámetros `n1`/`n2` externos), esta función no lo soporta sin
modificarse.

**Verificar en Fase 2:** confirmar si el pipeline necesita en algún
caso una partición no-mitad para KS-tendencia. Si no, no requiere
cambio; si sí, evaluar agregar parámetros opcionales `n1`/`n2` como
tiene `calcular_t_student`.

### 4. `_skewness` (g, IV-4/IV-5) reimplementada en 5 archivos de Etapa 2
(Bloque 3, Etapa 2 — NUEVO)

**Archivos:** `gve.py`, `lognormal3p.py`, `logpearson3.py`, `gamma3p.py`,
`gen_pareto.py` (todos en `metis/core/etapa2/distributions/`)

Cada uno de estos cinco archivos tiene su propia función privada
`_skewness()` que reimplementa IV-4/IV-5 en vez de importar la versión
ya auditada y verificada de `descriptive.py`. Verificado numéricamente
(2000 pruebas aleatorias sobre la versión de `gve.py`) que la
duplicación es bit-idéntica a la fuente — no es un bug hoy, ninguna de
las cinco copias diverge de `descriptive.py`.

**Verificar/resolver en Fase 2 (o en una sesión de refactor dedicada,
ver DECISIÓN 022 en decisions-log.md):** consolidar las cinco en una
única función importada desde `descriptive.py`. El riesgo no es de
corrección actual sino de mantenibilidad futura: si `descriptive.py`
recibe una corrección para algún caso borde, las cinco copias no la
heredan automáticamente.

### 5. M̂0/M̂1/M̂2 (MPP genérico, IV-21 a IV-24) reimplementado con al
menos 3 estilos de indexado distintos (Bloque 3, Etapa 2 — NUEVO)

**Archivos:** `gve.py` (`_momentos_L`, serie descendente, indexado
propio), `gamma2p.py` (método `ml`, serie descendente, pesos
`arange(n-1,0,-1)`), `gumbel.py` (método `ml`, serie **ascendente**,
pesos `arange(n)`)

Los tres estilos fueron verificados algebraicamente equivalentes entre
sí y contra IV-22/IV-87 (mismo término, reindexado) — no hay bug hoy.

**Verificar/resolver en Fase 2 (o en la misma sesión de refactor que
el punto 4):** consolidar en una única función compartida, mismo
razonamiento de mantenibilidad que el punto 4.

### Nota general para Fase 2

Los puntos 1, 2, 4 y 5 comparten la misma raíz: funciones de `core/`
que confían en supuestos sobre el orden, partición, o disponibilidad
de lógica genérica, sin una única fuente de verdad compartida y sin
validación interna. Vale la pena, al auditar el cableado completo,
evaluar si conviene una convención única y explícita en un solo lugar
(qué orden debe tener `serie` en cada etapa del pipeline; una sola
función de MPP/asimetría reutilizada por todos los módulos) en vez de
que cada archivo de `core/` asuma o reimplemente su propio criterio.