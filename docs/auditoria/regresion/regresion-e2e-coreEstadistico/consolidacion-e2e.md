# INFORME DE CONSOLIDACIÓN — Auditoría de Funcionamiento METIS, Fase 4 (E2E)
**Fecha:** 15 de Julio de 2026 (Revisión 2 — incorpora est_01, est_03 y est_04)
**Alcance:** síntesis de las 9 estaciones auditadas contra la tesis de Facundo Ganancias
Martínez, con verificación numérica independiente (sesión de Chat, sin acceso a repo) y
verificación de código real (sesión de Code, con acceso a repo), cruzadas entre sí en cada
punto relevante.

**Propósito de este documento:** a diferencia de los `est_0X-e2e.md` (que documentan cómo
opera METIS estación por estación), este informe responde una sola pregunta: **¿dónde está
parado el proyecto?** Qué está bien, qué está mal, qué es ambiguo, qué requiere una
decisión de Octavio, y qué requiere una respuesta puntual de Facundo.

Las 9 estaciones quedan cubiertas con el mismo nivel de detalle en esta revisión.

---

## 1. Resumen — dónde está parado el proyecto, en cinco ideas

**1. El motor estadístico central (Etapa 1, 5 pruebas) es fiel en las 9 estaciones.** Las
5 pruebas de Etapa 1 (Helmert, t-Student, Cramer, Anderson, Wald-Wolfowitz) reproducen los
números de la tesis al dígito casi siempre, cuando se aplica la misma convención de
partición o redondeo. La única excepción real es est_01, donde la reconstrucción de
Helmert y Wald-Wolfowitz no cierra por completo contra la tesis (ver §6, Q15) — un indicio
de dato transcripto distinto al real, no un problema de fórmula ni de cableado.

**2. El motor de ajuste de las 13 distribuciones también es fiel, medido en parámetros.**
En prácticamente todos los casos donde se pudo reconstruir la fórmula de forma
independiente, los parámetros que calcula METIS coinciden exacto o casi exacto con los de
tesis, o divergen por una causa identificada y ya conocida (DECISIÓN013, el ddof de "g").
No se encontró ningún bug de cableado real en ninguna de las 9 estaciones — cada vez que
un status o un parámetro difería de lo esperado, tuvo una explicación matemática
identificable.

**3. Hay una pregunta sin resolver que es más importante que todas las demás juntas: Causa
C.** En Normal, Log-Normal (2p y 3p), Gamma (2p y 3p) y Log-Pearson III, el EEA/cuantil que
calcula METIS diverge sistemáticamente de la tesis **incluso cuando los parámetros
coinciden casi exacto** — no es un problema de ajuste, es un problema de la fórmula de
error o de cuantil en sí. Esto se repite en las 9 estaciones, sin excepción, en esa familia
de distribuciones. En est_01 se descartaron explícitamente dos hipótesis alternativas
(aproximación de Wilson-Hilferty vs. inversa exacta de la CDF; intercambio α/β) sin que
ninguna cerrara la brecha — es la evidencia más rigurosa del proyecto de que el fenómeno no
es un artefacto de METIS. En est_03 se cuantificó por primera vez la proporción exacta:
~95% Causa C, ~5% Causa A. En 2 de las 9 estaciones (est_05, est_08) la magnitud es
suficiente para que el modelo que METIS recomendaría sea distinto al que Facundo eligió
(Causa D) — en est_08, cambia el primer puesto absoluto del ranking. No puede determinarse
si esto es un bug de METIS o si METIS es más riguroso que el Excel de 2011 sin inspeccionar
el Excel mismo — es la pregunta que más necesita resolverse, y requiere el archivo, no solo
la tesis en PDF.

**4. En al menos 5 estaciones (est_01, est_02, est_04, est_06, y en menor medida
est_07/08) hay evidencia concreta de que la propia ficha de tesis contiene errores de
transcripción, contaminación cruzada entre estaciones, columnas mal etiquetadas, o
parámetros que no se derivan de las propias ecuaciones documentadas — no ambigüedad de
interpretación, sino errores verificables de forma autocontenida.** Ejemplos: en est_01,
el µy que la tesis imprime para Log-Normal 2p (3.11) contradice la propia suma de
logaritmos que la misma ficha reporta (que implica µy=4.58); los parámetros de Gumbel MV/ME
en est_01 rompen la coherencia interna con los otros dos métodos de la misma distribución,
mientras que el EEA impreso sí es coherente con parámetros "normales" — evidencia de que se
transcribió mal la fila de parámetros, no el cálculo. En est_04, la columna de cuantiles
rotulada "LP3 MMI" reproduce GVE MV casi exacto, mientras la columna rotulada "GVE MV" no
coincide ni siquiera consigo misma. En est_06, tomando el x0 que la propia tesis publica
para Gamma 3p MV y aplicando las ecuaciones que la propia tesis documenta para ese método,
se obtienen α y β distintos a los que la tesis imprime como resultado — un caso puramente
aritmético, sin ninguna fórmula aguas abajo de por medio. Esto no es un pendiente de
METIS — es evidencia de calidad de la fuente que se confirmaría con certeza total viendo
el Excel (celdas y fórmulas vivas), aunque ya es verificable por contradicción interna sin
necesitar el archivo.

**5. Se encontraron y corrigieron 2 bugs de código reales, con verificación de regresión
completa contra las 9 estaciones — no requieren más intervención, salvo auditoría propia:**
DECISIÓN023 (`gamma3p.py`, escaneo de raíz insuficientemente denso más una singularidad
espuria de borde, diagnosticado y corregido en est_04) y DECISIÓN025 (`lognormal3p.py`,
ausencia de guard para detectar cuando la verosimilitud no tiene óptimo finito, corregido
en est_09).

---

## 2. Estado por estación

| Est. | Etapa 1 | Cableado | Selección de modelo | Estado general |
|---|---|---|---|---|
| est_01 | Aprobado a nivel de veredicto (rechazo unánime); estadísticos puntuales con Pendiente de dominio real (discrepancia de datos base, Q15) | Aprobado — 34/34 | Pendiente de código (Gamma 3p MPP, el modelo ganador, no implementable) | Parcial |
| est_02 | Aprobado | Aprobado | Aprobado | **Aprobado — sin ningún pendiente en la ruta del usuario experto** (la única de las 9 en este estado) |
| est_03 | Aprobado sin reservas nuevas | Aprobado — 34/34 | Aprobado | Parcial (Causa C cuantificada, ~95%, en el modelo seleccionado) |
| est_04 | Aprobado sin ninguna reserva — la más limpia de las 9 en esta capa | Aprobado — 34/34, con fix DECISIÓN023 aplicado en esta misma sesión | Aprobado | Parcial (cuantiles del modelo seleccionado sin comparación posible por columnas de tesis mal etiquetadas) |
| est_05 | Aprobado | Aprobado | Pendiente de dominio — Causa D (LN3p MV, no invierte ranking) | Parcial |
| est_06 | Aprobado | Aprobado | Aprobado | **Aprobado — sin ningún pendiente en la ruta del usuario experto** |
| est_07 | Aprobado (Cramer n_w1, ver §6.Q1) | Aprobado | Aprobado (Causa C sin invertir ranking) | Parcial |
| est_08 | Aprobado (valor crítico 1 cola, ver §6.Q2; homogeneidad, ver §6.Q8) | Aprobado | Pendiente de dominio — Causa D más severa del proyecto (invierte el #1 absoluto) | Parcial |
| est_09 | Aprobado (n_w1 Cramer, ver §6.Q1) | Aprobado | Aprobado | **Aprobado — bloqueo de contrato confirmado; único pendiente de código de la estación (DECISIÓN025) resuelto y aplicado** |

**Lectura:** 2 de las 9 estaciones (est_02, est_06) no tienen ningún pendiente. Las otras 7
tienen pendientes de dominio (preguntas a Facundo), hallazgos de calidad de fuente, o ambos
— ninguna tiene un pendiente de código sin resolver.

---

## 3. Hallazgos de código — ya resueltos, para registro

Estos dos no requieren que se le pregunte nada a Facundo — son bugs de implementación de
METIS, ya corregidos y verificados sin regresión contra las 9 estaciones.

**DECISIÓN023 — `gamma3p.py::mv`, origen en est_04.** El escaneo original (200 puntos
uniformes sobre un dominio de ~394 unidades) podía saltarse la raíz genuina cuando esta vive
en una ventana angosta (en est_04, ~0.26 unidades de ancho cerca del extremo superior del
dominio) — el paso del escaneo (~1.98 unidades) era casi 8 veces más ancho que esa ventana.
Se identificó además una segunda causa concurrente: una singularidad espuria de borde
(S2→~10⁹ cuando x0 se acerca al mínimo de la serie), de la misma naturaleza que la
patología ya vista en Log-Normal 3p (DECISIÓN020), aunque con escala distinta. Corregido
con escaneo denso concentrado hacia el borde superior (espaciado geométrico) más validación
posterior del candidato (signos de α y β, cota de plausibilidad sobre S2). Verificado sin
regresión contra las 9 estaciones: est_01/02/03/05/06 siguen `no_converge` sin ninguna
convergencia espuria nueva; est_07/08/09 no cambiaron (ya convergían bien con el escaneo
anterior). Nota importante: el fix resuelve la convergencia (los parámetros coinciden con
tesis hasta la 3ª cifra decimal), pero **no resuelve la Causa C que persiste en el EEA**
(diff -16.75% en est_04, mismo patrón transversal de todo el proyecto).

**DECISIÓN025 — `lognormal3p.py::mv`, origen en est_09.** La verosimilitud perfilada puede
no tener mínimo finito en absoluto (diverge sin límite acercándose al mínimo muestral —
degeneración clásica de MLE de 3 parámetros), y el optimizador (`minimize_scalar`, Brent
acotado) puede converger a un punto arbitrario sin haber encontrado un óptimo real.
Corregido con un guard que verifica que el escaneo tenga un giro genuino en algún punto
interior antes de aceptar el resultado. Verificado sin regresión contra las 9 estaciones
(parámetros idénticos en las 8 donde ya convergía bien; est_09 ahora da `NO_CONVERGE`,
coincidiendo con la tesis).

---

## 4. La pregunta central sin resolver — Causa C, y por qué se necesita el Excel

En las 9 estaciones, la familia Normal / Log-Normal (2p, 3p) / Gamma (2p, 3p) / Log-Pearson
III muestra el mismo síntoma: los parámetros coinciden casi exacto con la tesis, pero el
EEA/cuantil final no. La evidencia más rigurosa recolectada hasta ahora:

**est_01, Gamma 3p MPP (el modelo que Facundo eligió como ganador en esa estación) —
descarta dos hipótesis alternativas explícitas.** Se aplicó la Ec. IV-144 (ya verificada
fiel a la tesis) con los parámetros exactos que la tesis reporta, y el resultado diverge de
la propia tabla de cuantiles de tesis de forma creciente con T (PASS en T=2, hasta +16% en
T=100). Se probaron dos explicaciones alternativas y ambas se descartaron: (1) que fuera un
problema de aproximación de Wilson-Hilferty vs. la inversa exacta de la CDF — descartado,
los dos métodos coinciden entre sí y ambos divergen igual de la tabla de tesis; (2) que
las columnas α/β estuvieran intercambiadas en la lectura — descartado, empeora el ajuste
desde T=2. No queda ninguna explicación de fórmula, parámetro o método de cálculo del
cuantil que cierre la brecha.

**est_03, Log-Pearson III Indirecto (el modelo ganador en esa estación) — primera
cuantificación exacta de la proporción.** Test de aislamiento con la función real
`logpearson3.cuantil()`, inyectando los parámetros exactos de tesis: el error en T=100 pasa
de +54.13% (parámetros de METIS) a +51.42% (parámetros de tesis) — una diferencia de solo
2.7 puntos porcentuales. ~95% del error es Causa C, ~5% Causa A.

**est_08, Gamma 3p MV — el caso de mayor consecuencia práctica.** Verificado por tres vías
independientes (función real con parámetros propios; función real con parámetros exactos
de tesis; cuantil matemáticamente exacto vía `scipy.stats.gamma.ppf`, sin ninguna
aproximación de METIS) que el EEA diverge -23.96% sin que ninguna de las tres vías se
acerque al valor de tesis. La magnitud alcanza para invertir el primer puesto del ranking
que produciría METIS.

**Contrapeso — est_06, Log-Pearson III MV: el caso más sólido a favor de que METIS puede
ser más riguroso que la herramienta de Facundo, no al revés.** METIS converge a una
solución para este método donde la tesis reporta NO_CONVERGE. Se verificó esa solución con
el sistema literal de la tesis (digamma exacta, sin la sustitución de Thom que usa el
código en producción) y confirma la misma raíz hasta la tercera cifra decimal — no es una
convergencia espuria ni un artefacto de aproximación. A diferencia de los tres ejemplos de
Causa C de arriba (donde ninguna de las dos hipótesis está confirmada), este es un caso
donde hay evidencia concreta y verificada de que METIS encontró una solución genuina que la
herramienta original de Facundo no encontró.

**La pregunta que no puede resolverse sin el Excel:** cuando METIS y la tesis dan
resultados distintos con los mismos parámetros, hay dos explicaciones posibles, y no puede
distinguirse entre ellas solo con la tesis en PDF:

(a) METIS tiene un error de implementación en cómo calcula EEA/cuantiles para estas
    distribuciones específicas, o

(b) El Excel de Facundo (probablemente de 2011) tiene su propia inconsistencia interna —
    una fórmula de EEA que no corresponde exactamente a los parámetros que la misma celda
    reporta, un copy-paste de otra distribución, un redondeo intermedio que se propaga — y
    METIS, construido de forma más rigurosa, simplemente no reproduce ese error.

Se necesita el Excel real (no la ficha PDF, no un resumen — el archivo con las fórmulas
vivas en las celdas) para inspeccionar exactamente qué fórmula se usó en la celda de EEA de
cada método, y compararla contra la fórmula documentada en la tesis escrita. Sin eso,
cualquier clasificación de "Causa C" que se haga es una hipótesis sin cerrar, no una
conclusión.

---

## 5. Hallazgos de calidad de fuente — errores verificables, no ambigüedad de interpretación

Distintos de Causa C: acá no hay una pregunta de fórmula, hay evidencia autocontenida de
que un dato o una celda de la ficha de tesis está mal, verificable sin necesitar el Excel
(aunque el Excel serviría para confirmarlo con certeza total).

- **est_01 — Log-Normal 2p:** µy=3.11 impreso en la tabla de parámetros contradice la
  Suma ln(xi)=183.385 que la misma ficha reporta en la estadística descriptiva (que
  implica µy=4.585). Contradicción interna de la propia fuente, no requiere comparación
  externa para detectarse.
- **est_01 — Gumbel MV/ME:** los parámetros impresos para estos dos métodos (µ=200.14,
  α=20.39) rompen la coherencia con los otros dos métodos de la misma distribución sobre
  la misma serie, mientras que el EEA impreso para esos mismos métodos sí es coherente con
  parámetros "normales" — evidencia cruzada de que la fila de parámetros tiene un error de
  transcripción puntual.
- **est_01 — Log-Normal 3p MV:** x0=38.469 es matemáticamente inválido para este método
  (mayor que el mínimo observado de la serie, 15.0). Ese mismo valor (38.47) aparece
  también en la ficha de est_02 para el mismo método, una serie completamente distinta —
  posible contaminación cruzada. Nota de procedencia: esta coincidencia fue verificada
  contra el PDF original de la tesis en una sesión de contraverificación (Chat, con acceso
  directo al documento), pero no fue reconfirmada de forma independiente en el entorno de
  Code — queda consignada con esa salvedad.
- **est_04 — columnas de cuantiles intercambiadas o mal identificadas:** la columna
  rotulada "LP3 MMI" reproduce los cuantiles de GVE MV (diff ≤0.03% en los 7 T), mientras
  que la columna rotulada "GVE MV" de la misma tabla diverge de ese mismo cálculo entre
  -7.9% y +9.9% — no coincide ni siquiera consigo misma. Consecuencia directa: no existe,
  en la ficha de tesis de est_04, ninguna columna verificable de cuantiles para el modelo
  que Facundo efectivamente seleccionó (LP3 Indirecto).
- **est_06 — Gamma 3 parámetros MV, los parámetros publicados no se derivan de su propio
  x0:** la tesis reporta x0=5.241, α=15.612, β=2.129 para este método. Tomando ese mismo
  x0=5.241 y aplicando las Ecs. IV-140/141 (las que la tesis documenta para este método) se
  obtiene α=14.235, β=2.736 — no los valores publicados. Es el caso más autocontenido del
  proyecto: no depende de EEA, cuantiles, ni ninguna fórmula aguas abajo — es aritmética
  directa de dos ecuaciones a partir de un dato que la propia tesis publicó como suyo. A
  diferencia de est_08 (Sección 4), acá el problema está en la estimación de los parámetros
  en sí, no en el cálculo del EEA una vez que los parámetros ya coinciden.

---

## 6. Preguntas para escalar a Facundo

Redactadas para que cada una tenga una respuesta cerrada — no requieren que Facundo
interprete qué se le quiere decir.

### Prioridad alta

**Q1 — Partición de Cramer (n_w1), regla de redondeo.**
Para la partición de Cramer al 60%, cuando `n × 0.6` no da un número entero: en las
estaciones est_02 y est_05, los resultados de tesis solo se reproducen si ese tamaño de
subgrupo se redondea siempre hacia arriba (`ceil`). En las estaciones est_07 y est_09, los
resultados de tesis solo se reproducen si se redondea al entero más cercano (redondeo
estándar), no hacia arriba. ¿Cuál de las dos reglas se usó — siempre redondeo hacia
arriba, o redondeo estándar — o hay una tercera regla que dependa de algo más (por ejemplo,
el tamaño de la serie)?

**Q2 — Valor crítico de tabla t, una cola vs dos colas.**
En est_08 y est_09, el valor crítico de la distribución t que aparece impreso en la ficha
(1.6829 para GL=41; 2.015 para GL=5) corresponde al percentil de una cola (95%). En las
otras 7 estaciones, el valor crítico impreso corresponde a dos colas (97.5%). ¿El criterio
correcto para Cramer y t-Student es siempre dos colas (y est_08/est_09 tienen un error de
tabla puntual), o el criterio correcto es una cola (y las otras 7 estaciones son las que
tienen el error)?

**Q3 — GVE Momentos-L, fórmulas de α y ν (Ecs. IV-234 a IV-241).**
En las 9 estaciones donde se aplicó este método, el parámetro β siempre coincide casi
exacto con la tesis (diff <1% en todos los casos), pero α y ν divergen sistemáticamente
(entre 10% y 60%, sin una sola excepción en las 9 estaciones). ¿Las ecuaciones que
definen α (IV-240) y ν (IV-241) dentro del bloque de Momentos-L tienen una errata (de
signo, de exponente, o de constante), o falta un paso intermedio que no llegó al
documento final?

**Q3-bis — GVE Momentos (Ecs. IV-203/204), método distinto al anterior.**
Separado de la Q3: en 5 de las 9 estaciones la tesis reporta un valor real (no
NO_CONVERGE) para GVE por el método de Momentos simple — est_04, est_05, est_06 y est_07
de forma limpia, y est_03 con la salvedad de que su propia tabla de EEA marca este mismo
caso como NO_CONVERGE pese a que su tabla de parámetros sí reporta un β (inconsistencia
interna de esa ficha puntual, no de METIS). En las 5, el β que surge del polinomio
IV-203/204 no se reproduce con ningún valor de asimetría (g) probado, ni el que calcula
METIS ni una variante tipo Excel. ¿Hay algún ajuste o tabla adicional para este cálculo
que no llegó al Capítulo IV, o el polinomio tal como está impreso tiene una errata?

**Q4 — Generalizada Exponencial, Momentos (Ec. IV-77).**
Se verificó matemáticamente (con las funciones digamma y trigamma que exige la Ec. IV-77)
que el parámetro α que se reporta en la tesis no reproduce el coeficiente de variación
real de la serie, en ninguna de las 9 estaciones — en cambio, el α que calcula METIS sí lo
reproduce exacto en las 9. La diferencia va de +11% a +54% según la estación. ¿La Ec.
IV-77 tiene una errata, o hay un paso intermedio (por ejemplo, un ajuste sobre los
momentos antes de aplicar la fórmula) que no quedó documentado?

**Q5 — Log-Pearson III Directo, valores fuera del dominio de validez (B ∉ (3,6]).**
En est_07, est_08 y est_09, el estadístico B (Ec. IV-249, sobre momentos crudos de la
serie) cae fuera del rango (3,6] donde se documentaron los polinomios de aproximación
(Ecs. IV-251/252). En esas tres estaciones, la ficha igual reporta valores de α, β, y0
para el método Directo (en est_02, 03, 05 y 06, en cambio, B también cae fuera de rango y
la ficha correctamente marca el método como no aplicable). ¿Se usó una fórmula o
aproximación alternativa para B fuera de ese rango en esas tres estaciones puntuales, o
esos valores deberían considerarse inválidos?

**Q6 — Gamma 3 parámetros, método de Momento de Probabilidad Pesada.**
El Capítulo IV no desarrolla las ecuaciones de este método para Gamma 3p — no es posible
implementarlo sin la fórmula. Esto tiene consecuencia directa en est_01, donde este método
es, además, el modelo que la tesis selecciona como ganador — es decir, la estación queda
sin ningún modelo recomendable por METIS en ese caso. ¿Puede facilitarse la fórmula
completa (o la referencia bibliográfica exacta) usada en el Excel para este método?

**Q6-bis — Gamma 3 parámetros MV en est_06, los parámetros publicados no se derivan del
propio x0 de la tesis. Fácil de autochequear, no requiere el Excel.**
En Las Tapias – Río San Bartolomé (est_06), la tesis reporta x0=5.241, α=15.612, β=2.129
para este método. Tomando ese mismo x0=5.241 y aplicando las Ecs. IV-140 e IV-141 (las
mismas que la tesis documenta para este método) se obtiene α=14.235, β=2.736 — no los
valores publicados. Es un cálculo autocontenido: partiendo del x0 que la propia tesis
publicó como suyo, sus propias ecuaciones no reproducen sus propios α y β. ¿Puede
recalcularse α y β a partir de x0=5.241 con las Ecs. IV-140/141 y confirmarse si el valor
correcto es el publicado (15.612/2.129) o el que surge de aplicar la fórmula directamente
(14.235/2.736)?

**Q7 — Log-Normal 2 parámetros, µy en est_01.**
En Alpa Corral (est_01), la tesis reporta µy=3.11 para Log-Normal 2p. La estadística
descriptiva de la misma ficha reporta Suma ln(xi)=183.385 para n=40, lo que implica
µy=183.385/40=4.585. ¿El valor 3.11 es un error de tipeo (y el valor correcto es 4.58), o
hay un cálculo distinto detrás de ese número puntual?

### Prioridad media

**Q8 — Homogeneidad en est_08, jerarquía de pruebas.**
En est_08, la tesis declara la serie "Homogénea bajo consideraciones especiales", dándole
el rol decisivo a t-Student (con un subgrupo de Cramer como apoyo), pese a que Cramer
rechaza en su subgrupo 2. Esto es lo opuesto a la jerarquía definida para METIS en la
reunión del 14/04 (Cramer como prueba principal — si rechaza, la serie es "crítica" sin
importar qué digan las demás). ¿La jerarquía Cramer-principal es la que siempre se quiso
aplicar, y la tesis de 2019 usó un criterio distinto que se corrigió después? ¿O hay algo
específico de est_08 que justifica tratarla como excepción?

**Q9 — Log-Pearson III Indirecto, valor "0.333" repetido en dos estaciones distintas.**
El parámetro α que se reporta para este método es exactamente 0.333 tanto en est_02
(n=24) como en est_09 (n=7) — dos series sin relación entre sí. Se verificó que 0.333 no
corresponde a la asimetría de los logaritmos (g_y) de ninguna de las dos series. ¿Es una
coincidencia real de la fórmula aplicada a esas dos series puntuales, o hay un error de
transcripción entre esas dos estaciones?

**Q10 — Gumbel MV/ME en est_01, parámetros incoherentes con el resto de la ficha.**
En Alpa Corral (est_01), los parámetros que la tesis reporta para Gumbel por Máxima
Verosimilitud (α=86.40, µ=200.14) y por Máxima Entropía (α=20.39, µ=177.34) no son
coherentes con los otros dos métodos de la misma distribución sobre la misma serie
(Momentos: α=90.32, µ=92.62; ML: α=93.45, µ=90.78). El EEA impreso para esos dos métodos
(29.98 y 27.34) sí es consistente con parámetros del orden de los otros tres. ¿Los
parámetros de MV y ME para Gumbel en esta estación tienen un error de transcripción (y
los valores correctos rondan α≈84-88, µ≈90-93), o el cálculo real produjo esos parámetros
atípicos?

**Q11 — Log-Normal 3p MV en est_01, x0 físicamente inválido y posible contaminación con
est_02.**
El x0 que reporta la tesis para este método en Alpa Corral (est_01) es 38.469 — mayor que
el mínimo observado de la serie (15.0), lo que vuelve indefinido el logaritmo del propio
dato mínimo. El mismo valor (38.47) aparece en la ficha de Vado de Río Seco (est_02) para
el mismo método. ¿Hay una contaminación de datos entre las fichas de est_01 y est_02 en
esta fila específica de la tabla?

**Q12 — Exponencial (x0, β) por Máxima Verosimilitud, divergencia sin patrón conocido en
est_01.**
El β que calcula METIS (132.69) diverge +12% del que reporta la tesis (118.51) en Alpa
Corral (est_01). Es una fórmula cerrada (Ecs. IV-72/73, sin iteración), y la magnitud
excede lo esperable de la discrepancia de datos base ya identificada en esa estación.
¿Hay algún paso adicional en el cálculo de este método específico que no llegó al
Capítulo IV, o el valor de tesis tiene un error puntual?

**Q13 — Generalizada de Pareto, Momentos: ambigüedad de raíz múltiple en est_01.**
Para esta serie, el método de Momentos (Ecs. IV-147 a IV-149) tiene dos raíces
matemáticamente válidas para ε: -0.333 y +0.363. METIS toma la raíz positiva. La tesis
marca este método como no convergente para esta estación. ¿El criterio para descartar la
serie en este método es que ninguna de las dos raíces sea físicamente válida, o hay una
preferencia documentada por una raíz específica que no llegó al Capítulo IV?

**Q14 — Columnas de cuantiles intercambiadas en est_04.**
En Las Tapias – Río Las Tapias (est_04), la columna de la tabla de cuantiles rotulada "LP3
MMI" reproduce los cuantiles de GVE MV (diff ≤0.03% en los 7 períodos de retorno), mientras
que la columna rotulada "GVE MV" de la misma tabla diverge de ese mismo cálculo entre
-7.9% y +9.9%. ¿Las dos columnas de esa tabla están intercambiadas, o corresponden a
corridas distintas que no quedaron correctamente identificadas en el documento final?

**Q15 — Discrepancia de datos base en est_01.**
La media que surge de sumar los 40 valores de la serie transcripta en la ficha de Alpa
Corral (144.375) no coincide con la media que la misma ficha reporta en su propia tabla de
estadística descriptiva (144.725) — una diferencia exacta de 14.0 sobre la suma total, no
explicable por redondeo acumulado. Se probó cambiar el dato de 1940-41 (transcripto como
129.0) por 143.0: esto cierra exactamente la diferencia de media (143-129=14), pero no
mueve ni un punto los resultados de Helmert ni de Wald-Wolfowitz — ambos también divergen
de la tesis, y tanto 129 como 143 quedan del mismo lado de la media en los dos casos, por
lo que ese cambio no altera el patrón de signos que usan esas dos pruebas. Esto indica que
existe al menos un segundo valor de la serie distinto al transcripto, en una posición que
sí cruza esa media, que no puede identificarse sin mirar la fuente de trabajo. ¿Puede
revisarse la serie completa de Alpa Corral contra el archivo de trabajo original (no la
tabla impresa de la tesis) para confirmar si hay valores que difieran de los que aparecen
en el documento final?

### Prioridad baja (no bloquean nada, quedan documentadas por completitud)

**Q16 — Partición de t-Student para n impar.**
En 5 de las 9 estaciones (n impar), los resultados de tesis solo se reproducen con la
partición `n1 = ceil(n/2)` (el subgrupo 1 más grande). METIS usa `n1 = floor(n/2)`. No
cambia ningún veredicto (ambas particiones aprueban o rechazan homogeneidad de la misma
forma en todos los casos vistos). ¿La convención correcta es `ceil` para el primer
subgrupo?

**Q17 — Generalizada de Pareto, Ec. IV-153.**
La expresión matemática de esta ecuación, tal como está impresa en la tesis, tiene una
extensión y dimensión que hace que sus propios términos se solapen entre sí — no entran en
el espacio normal de la página. No es un problema de calidad de escaneo o de tipografía
ilegible: es que, para alguien que no es experto en el dominio específico, no queda
completamente claro cuál es la expresión correcta a partir de cómo está maquetada. ¿Puede
facilitarse una transcripción limpia de la Ec. IV-153 (a mano, o desde el archivo fuente
original), para no tener que inferir el agrupamiento correcto de los términos a partir de
una imagen ambigua?

---

## 7. Materiales necesarios

1. El Excel real de la tesis (todas las estaciones, con las fórmulas vivas en las celdas)
   — imprescindible para resolver la Sección 4 (Causa C). El pedido es específicamente por
   las fórmulas de cálculo (EEA, cuantiles) que usó Facundo, no por los datos crudos de las
   series — esos ya están transcriptos fielmente en los `est_0X-e2e.md` a partir de la
   propia tesis, con la única excepción puntual de est_01 (Q15), que es un caso aislado de
   inconsistencia interna de esa ficha específica, no una duda general sobre las series.
2. Transcripción limpia de la Ec. IV-153 (ver Q17) — necesaria para que la pregunta
   pueda cerrarse con una respuesta concreta en vez de quedar como ambigüedad sin resolver.

---

## 8. Pendientes propios del proyecto (no requieren a Facundo)

- Conteo 34→35 combinaciones distribución×método, corregido a partir de est_08 pero no
  aplicado retroactivamente al texto de est_01 a est_07. Solo afecta la redacción de esos
  documentos, no ningún hallazgo — corregir antes de dar la Fase 4 por completamente
  cerrada en su forma final.
- Gamma 3p MPP y Generalizada de Pareto MPP — ambos con fórmula ausente o con estimador
  mal condicionado (épsilon físicamente implausible en las 9 estaciones donde se corrió) —
  pendiente de código bloqueado por falta de fuente (ver Q6), no resoluble sin la fórmula
  de Facundo.
- Contraverificación de la Q11 (contaminación est_01/est_02) — verificada hasta ahora solo
  con el PDF de la tesis en la sesión de Chat; no reconfirmada de forma independiente por
  Code. Cerrar esa brecha de procedencia cuando se revise el material completo.

---

## 9. Próximos pasos sugeridos

1. Enviar Q6-bis (est_06, Gamma 3p MV) a Facundo por separado y de inmediato — es
   autocontenida, no depende del Excel ni de ningún otro material, y es la más rápida de
   chequear de todo el informe: solo requiere que recalcule dos ecuaciones a partir de un
   dato que ya publicó.
2. Facilitar el Excel de la tesis → cerrar la Sección 4 (Causa C) con evidencia real, no
   hipótesis.
3. Facilitar una transcripción limpia de la Ec. IV-153 → cerrar Q17.
4. Armar el mensaje final a Facundo con el resto de las preguntas de la Sección 6, ya
   redactadas en formato cerrado.
5. Con las respuestas de Facundo, actualizar el archivo de decisión correspondiente en
   `docs/decisiones/` y `pendientes-facundo.md`
   con el estado final de cada punto, y recién ahí dar la Fase 4 por formalmente cerrada.