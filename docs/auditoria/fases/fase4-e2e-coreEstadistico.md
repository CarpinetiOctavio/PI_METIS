# Auditoría METIS — Fase 4: Regresión E2E (consolidación definitiva)
### Estado — Iniciada 14/07/2026

## Origen y por qué existe esta fase, separada de Fase 2

Durante el cierre de Fase 2 (cableado), las corridas de "pipeline
completo" que se generaron como diagnóstico (comparar unitario vs.
pipeline en vivo, para distinguir ficha desactualizada de bug real)
terminaron siendo, técnicamente, el mismo pipeline íntegro que correría
en producción — `ejecutar_etapa1()` seguido de `ejecutar_etapa2()`, sin
atajos. Se intentó cerrar un "Bloque 8" dentro de `fase2-cableado.md`
usando ese output, sobre 5 de las 9 estaciones existentes, con distinto
nivel de profundidad entre ellas. Fue prematuro en tres sentidos:
alcance incompleto (5 de 9), objetivo mal definido (no es un PASS/FAIL
más de integración), y profundidad desigual entre estaciones. Esta fase
corrige los tres puntos.

## Qué es esta fase y qué NO es

**No es una ejecución distinta de Fase 2.** `ejecutar_etapa1()` +
`ejecutar_etapa2()` de punta a punta es el máximo nivel de integración
posible. Las corridas ya hechas para est_02 a est_06, y las que Code ya
generó de forma independiente para est_01/07/08/09, son el mismo tipo
de artefacto — no se vuelven a ejecutar salvo para re-chequeo puntual
de algo específico.

**Lo que sí es distinto es la pregunta que se le hace a ese resultado.**
Fase 2 pregunta, función por función: "¿el orquestador le pasó a esta
distribución/método el dato correcto?". Esta fase pregunta, sobre las
13 distribuciones ya calculadas y compitiendo entre sí: "¿el ranking
final y el modelo seleccionable coinciden con la referencia de
Facundo, y si no, por qué, y qué hay que hacer al respecto?"

**No se re-audita fidelidad de fórmula (Fase 1) ni cableado general
(Fase 2) acá** salvo sospecha concreta que amerite reabrir — pero sí es
objeto de esta fase confirmar, con el mismo rigor en las 9 estaciones,
que el cableado no tiene sorpresas (ver estándar de profundidad abajo).
Hallazgos de algoritmo/robustez numérica que solo se hacen visibles
corriendo el pipeline completo con datos reales sí son objeto propio de
esta fase (ejemplo ya confirmado: bug de escaneo en `gamma3p.py`/MV).

## Objetivo — la consolidación definitiva

Primera vez, desde que se inició el desarrollo de METIS, que se evalúa
el pipeline íntegro contra el dataset completo de estaciones disponible
— **est_01 a est_09, las 9, sin excepción, con el mismo nivel de
profundidad en cada una.** No hay estaciones prioritarias ni
secundarias en esta fase. El entregable es una clasificación cerrada,
estación por estación y consolidada, en tres categorías — ninguna
estación queda "sin analizar" ni "analizada a medias" al cierre:

1. **Aprobado — operando correctamente.**
2. **Pendiente de código.** Bug real de METIS — se escala a Code con
   fragmento exacto y reproducción numérica. No requiere Facundo.
3. **Pendiente de dominio.** Discrepancia no atribuible a METIS (Causa
   C, Causa D, ambigüedad sin resolver) — se escala a Facundo/Carlos.

## Estándar de profundidad — el mismo para las 9 estaciones

Para que una estación se considere **analizada al 100%** en esta fase,
tiene que tener las cuatro cosas siguientes, sin excepción:

1. **Etapa 1** — veredicto general reproducido y comparado contra la
   tesis (homogeneidad, independencia, veredicto final).
2. **Cableado de las 13 distribuciones** — reconstrucción numérica
   independiente (código real, no solo comparación de tablas) para
   cada distribución/método con `status=ok`, comparada contra la
   corrida en vivo del pipeline. Esto es lo que hoy solo tiene est_02
   completo (28/34 métodos) — est_03/05/06 solo tienen Gamma 2p
   reconstruido en profundidad, el resto verificado únicamente por
   comparación de status/parámetros de tabla. **Eso no alcanza el
   estándar que se fija acá** — queda pendiente llevarlas al mismo
   nivel que est_02, igual que est_01/07/08/09 desde cero.
3. **Selección de modelo** — mínimo EEA de METIS vs. selección de
   Facundo, con el principio de que METIS no decide (expone el
   ranking, el usuario experto decide) siempre presente al comparar.
4. **Cuantiles del modelo seleccionado** — aunque el ranking coincida,
   verificar que los cuantiles de diseño de ese modelo puntual también
   coincidan (caso est_03: ranking correcto, cuantiles con Causa A
   propagada a la cola).

Ninguna fila de la tabla de consolidación se marca "Aprobado" sin las
cuatro verificaciones hechas — un "0 hallazgos" parcial (como el actual
de est_03/05/06) se marca explícitamente como incompleto, no como
aprobado.

## Metodología de trabajo

Sobre el resultado ya generado por el pipeline completo (no volver a
ejecutar salvo verificación puntual): aplicar el estándar de arriba,
punto por punto, documentando cada verificación con el fragmento de
código/valores reales — nunca aceptar un resumen sin reproducir.

**Causa D (definición formal, heredada, no es causa raíz nueva):** se
aplica cuando una discrepancia ya clasificada como Causa A/B/C es de
magnitud suficiente para alterar el orden relativo del ranking que el
pipeline expone al usuario experto.

## Reglas de operación (heredadas de Fase 1/2/3, sin cambios)

- Verificación numérica independiente (reconstrucción con código real)
  antes de aceptar cualquier hallazgo — no aceptar reporte de Code sin
  reproducirlo.
- No confiar en argumentos basados en git log/diff/historial de
  commits, ni de Code ni propios.
- Trazabilidad: nunca sobreescribir ni borrar valores previos en este
  documento — agregar fecha + valores nuevos, dejar lo anterior intacto.
- No clasificar como Causa C sin agotar primero cableado; no clasificar
  Causa D sin que ya exista una A/B/C de base.
- Nada se aplica a código real sin aprobación explícita de Octavio.

## Rol de Octavio

Intermediario entre esta sesión y el chat de Code, que tiene acceso al
repositorio real. Ningún fix se aplica directo desde esta fase.

---

## Tabla de consolidación — las 9 estaciones, mismo criterio, ninguna salteada

| Estación | Etapa 1 | Cableado (profundidad real) | Selección de modelo | Cuantiles del modelo | Clasificación |
|---|---|---|---|---|---|
| est_01 | Reproducido desde cero 14/07/2026, PASS a nivel de veredicto (rechazo unánime coincide); Helmert/Wald con Pendiente de dominio (ver detalle) | 13/13 distribuciones, 34/34 combinaciones método reconstruidas de forma aislada — completo | No coincide — modelo ganador de Facundo (Gamma3p MPP) no implementable en METIS | Testigo (Gamma2p ML) PASS en T bajos, degrada a +17.6% en T=100; modelo ganador sin comparación posible | **Parcial — Etapa 1 y cableado Aprobados; Etapa 2 con 1 Pendiente de código (Gamma3p MPP) y múltiples Pendientes de dominio, ninguno atribuible a METIS. Ver `regresion-e2e/est_01-e2e.md` para el detalle completo.** |
| est_02 | Reproducido desde cero 14/07/2026 — PASS total, sin Pendientes de dominio en Etapa 1 (Wald/Helmert n1/n2/R/S/C coinciden exacto con tesis, a diferencia de est_01) | 13/13 distribuciones, 34/34 combinaciones método reconstruidas de forma aislada — completo (extiende el 28/34 de Fase 2) | Coincide (Exp β) — parámetros y EEA diff ≤0.2% | PASS 7/7, diff ≤0.001% | **Aprobado — ciclo completo (Etapa1→cableado→selección→cuantiles) cierra sin pendientes en la ruta del usuario experto. Testigo (LN3p MV) con Pendiente de dominio — Causa C confirmada con la señal más limpia del proyecto (params idénticos, EEA/cuantiles divergen). Ver `regresion-e2e/est_02-e2e.md`.** |
| est_03 | Reproducido desde cero 14/07/2026 — PASS total, sin Pendientes de dominio nuevos en Etapa 1 (Helmert/Cramer exactos; único pendiente es Wald n1/n2, ya identificado y sin resolver desde DECISIÓN 017) | 13/13 distribuciones, 34/34 combinaciones método reconstruidas de forma aislada — completo (extiende el 3/34 de Fase 2) | Coincide (LP3 Indirecto) — implementado y converge | Modelo seleccionado diverge +54% T=100 — cuantificado con test de aislamiento (función real): Causa C dominante ~95%, Causa A ~5%; testigo (GVE MV) PASS exacto 7/7 | **Parcial — Etapa 1, cableado y selección de modelo Aprobados; cuantiles del modelo seleccionado con Pendiente de dominio (Causa C dominante, mismo patrón sistémico que est_01/02, acá cuantificado con proporción exacta). Ver `regresion-e2e/est_03-e2e.md`.** |
| est_04 | Reproducido desde cero 14/07/2026 — PASS total, sin Pendientes de dominio (la estación más limpia hasta ahora junto con est_02) | 13/13 distribuciones, 34/34 combinaciones método reconstruidas de forma aislada — completo (extiende Gamma 2p de Fase 2) | Coincide con la elección de Facundo (LP3 Indirecto, no el mínimo numérico GVE MV) — sistema funciona como especificado | Sin comparación posible para el modelo seleccionado — la columna "LP3 MMI" de tesis está contaminada con cuantiles de GVE MV (confirmado ≤0.03%, no ≥-7.9%/+9.9% contra su propia columna "GVE MV"); testigo (GVE MV) PASS exacto 7/7 | **Parcial — Etapa 1, selección de modelo y cableado Aprobados. `gamma3p.py::mv` (bug de escaneo, DECISIÓN 023) diagnosticado, corregido y verificado sin regresiones en las 9 estaciones — primer fix de código de todo el proyecto Fase 4 cerrado de punta a punta. Ver `regresion-e2e/est_04-e2e.md`.** |
| est_05 | Reproducido desde cero 14/07/2026 — PASS total; dos pendientes puntuales ya documentados (partición t-Student n impar, n_w2 Cramer) reconfirmados, no nuevos | 13/13 distribuciones, 34/34 combinaciones método reconstruidas de forma aislada — completo (extiende Gamma 2p de Fase 2, corrido con el fix DECISIÓN023 ya aplicado) | No coincide — Causa D confirmada con verificación completa: LN3p MV (elegido por Facundo) params ~0% pero EEA +51.65%, invierte el ranking frente a GVE MV | Modelo seleccionado diverge +38.32% T=100 — cuantificado con test de aislamiento (función real): ~99.8% Causa C, ~0.2% Causa A, EEA con params exactos de tesis (8.79) tampoco cierra el ranking; testigo (GVE MV) PASS exacto 7/7 | **Parcial — Etapa 1 y cableado Aprobados; selección de modelo con Pendiente de dominio (Causa D, la clasificación de mayor severidad práctica del framework). Ver `regresion-e2e/est_05-e2e.md`.** |
| est_06 | Reproducido desde cero 14/07/2026 — PASS total, la más limpia de las 6 (n par, sin ambigüedad de partición) | 13/13 distribuciones, 34/34 combinaciones método reconstruidas de forma aislada — completo (extiende Gamma 2p de Fase 2, con fix DECISIÓN023 ya aplicado) | Coincide exacto (Exp x0β MV) — parámetros y EEA diff ~0% | PASS 7/7, diff ≤0.005% | **Aprobado — segunda estación, junto con est_02, donde el ciclo completo cierra sin ningún pendiente en la ruta del usuario experto. Ver `regresion-e2e/est_06-e2e.md`.** |
| est_07 | Reproducido desde cero 14/07/2026 — PASS total. Hallazgo nuevo: n_w1 de Cramer contradice DECISIÓN011 (contraejemplo real, ver `pendientes-facundo.md`) | 13/13 distribuciones, 34/34 combinaciones método reconstruidas de forma aislada — completo, primera vez para esta estación | Coincide (Log-Normal 2p) — params PASS exacto, EEA diverge -25.40% sin invertir ranking (no es Causa D) | Modelo seleccionado diverge +18.25% T=100 (Causa C, magnitud moderada); testigo (Gumbel MomentosL) PASS exacto 7/7 | **Parcial — Etapa 1, cableado y selección de modelo Aprobados. Hallazgo transversal relevante: n_w1 de Cramer no tiene regla de redondeo universal (DECISIÓN011 contradicha). Ver `regresion-e2e/est_07-e2e.md`.** |
| est_08 | Reproducido desde cero 15/07/2026 — PASS total, sin discrepancias de datos base. Hallazgo nuevo: valor crítico de tabla en Cramer/t-Student usa convención de una cola (1.6829), no dos colas como las 8 estaciones anteriores | 13/13 distribuciones, 35/35 combinaciones método reconstruidas de forma aislada — completo (primera vez, y primera vez que se corrige el conteo real: 35, no 34) | Modelo elegido por Facundo (Gumbel ML) fiel y disponible, PERO el ranking propio de METIS pondría Gamma 3p MV en el #1 por Causa D — el caso de Causa D más severo del proyecto | Gumbel ML (seleccionado) PASS exacto 7/7; Gamma 3p MV (falso #1 del ranking METIS) verificado por 3 vías independientes como Causa C pura | **Parcial — Etapa 1 y cableado Aprobados sin reservas de fondo. Selección de modelo con Pendiente de dominio — Causa D de máxima severidad (cambia el #1 absoluto del ranking, no solo el orden relativo). Ver `regresion-e2e/est_08-e2e.md`.** |
| est_09 | Contrato bloquea correctamente (n=7<10, único caso de bloqueo duro — confirmado). Etapa 1 aislada/académica: PASS total, sin discrepancias de datos base | 13/13 distribuciones, 35/35 combinaciones método reconstruidas de forma aislada — completo | Modelo elegido por Facundo (Uniforme Momentos) fiel, PASS exacto — la mejor reproducción del proyecto | PASS 7/7, diff ≤0.015% — mejor resultado de cuantiles del proyecto. LN3p MV: causa raíz confirmada por verificación cruzada, fix aplicado (DECISIÓN 025), verificado sin regresión contra las 9 estaciones — ahora `NO_CONVERGE`, coincide con la tesis | **Aprobado — bloqueo del contrato Aprobado; Etapa 1/cableado/selección/cuantiles académicos Aprobados sin reservas; el único Pendiente de código de la estación (LN3p MV) quedó resuelto y aplicado (DECISIÓN 025). Sin nada abierto. Ver `regresion-e2e/est_09-e2e.md`.** |

**Lectura honesta de esta tabla:** hoy, 1 de 9 estaciones (est_02)
cumple el estándar completo de esta fase. Las otras 8 tienen trabajo
pendiente — 4 desde cero (est_01/07/08/09) y 3 con cableado incompleto
pese a tener selección de modelo ya resuelta (est_03/05/06). Ninguna se
trata como "cerrada" hasta cumplir las cuatro columnas.

**Actualización 14/07/2026:** est_01 completada con el estándar íntegro
(las cuatro columnas, cableado de las 13 distribuciones con
reconstrucción propia). Queda como la 2da estación en cumplir el
estándar completo, junto con est_02 — con la salvedad de que su
clasificación final es "Parcial" (no "Aprobado" liso) porque Etapa 2
tiene un Pendiente de código real (Gamma3p MPP no implementable) y
varios Pendientes de dominio nuevos, no por trabajo de verificación
faltante. Detalle completo en `regresion-e2e/est_01-e2e.md`.

**Actualización 14/07/2026 (2):** est_02 rehecha íntegra desde cero, sin
asumir la clasificación "Aprobado" heredada de Fase 2 (que solo cubría
28/34 métodos y no las 4 columnas de Fase 4). El resultado confirma
"Aprobado" con la misma sustancia, pero el proceso encontró dos casos
concretos donde `est_02...unitaria.md` (Fase 1/2) ya no coincide con el
código actual — un status (LP3 Directo, antes PASS, ahora correctamente
NO_APLICABLE por el guard B∈(3,6]) y dos valores de EEA (Gamma3p Momentos,
GVE Momentos) que cambiaron por DECISIÓN013 y por cambios sin commitear en
`gve.py`. Ningún hallazgo nuevo requiere tocar código — confirma que
"Aprobado" no se sostenía por inferencia de la ronda anterior, sino que se
reconfirma con evidencia fresca. Detalle completo en
`regresion-e2e/est_02-e2e.md`.

**Actualización 14/07/2026 (3):** est_03 rehecha íntegra desde cero.
Etapa 1 y selección de modelo ya venían resueltas de rondas anteriores y
se reconfirmaron; el cableado se extendió de 3/34 (solo Gamma 2p) a 34/34.
Hallazgo transversal reforzado: GVE Momentos-L muestra el mismo patrón
(β cerca, ν/α lejos) en las **5 estaciones auditadas con Etapa 2 completa
hasta ahora, sin una sola excepción** (est_01/02/03/05/06) — deja de ser
hipótesis, es un patrón sistemático confirmado, prioridad alta para
pregunta directa a Facundo. También se confirmó que el patrón de "la
fórmula documentada no reproduce la cola de la tabla de tesis" (visto en
Gamma3p MPP en est_01 y LN3p MV en est_02) aparece también en el modelo
que Facundo sí seleccionó para est_03 (LP3 Indirecto, +54% en T=100) — acá
sí afecta la ruta del usuario experto, a diferencia de est_01/02. Detalle
completo en `regresion-e2e/est_03-e2e.md`. Quedan 5 estaciones con trabajo
pendiente: est_05/06 (cableado incompleto) y est_07/08/09 (desde cero).

**Actualización 14/07/2026 (4):** a pedido de la sesión de
contraverificación (Chat), se corrió un test de aislamiento Causa A vs
Causa C para LP3 Indirecto/est_03 con la función real
`logpearson3.cuantil()` (no reconstrucción manual) — se inyectaron los
parámetros propios de la tesis (α=0.260, β=16.252, y0=-0.588) en la misma
función que usa el pipeline. Resultado: T=100 diff=+51.42% (vs +54.13%
con los parámetros de METIS) — la diferencia entre usar un juego de
parámetros u otro es de solo 2.7 puntos porcentuales. **Cuantifica que
Causa C explica ~95% del error total y Causa A solo ~5%** — antes era
clasificación cualitativa ("A + componente de C"), ahora es proporción
verificada con la función real. Coincide con la estimación manual previa
de Chat (~+51%), por lo que se descarta que sea un hallazgo de cableado
nuevo en `logpearson3.py::cuantil`. Detalle completo en
`regresion-e2e/est_03-e2e.md`, hallazgo C.

**Actualización 14/07/2026 (5):** est_04 rehecha íntegra desde cero.
Etapa 1 sale como la más limpia de las 4 auditadas hasta ahora (junto con
est_02), sin ningún Pendiente de dominio. Dos hallazgos relevantes:

1. **`gamma3p.py::mv` reconfirmado en vivo como Pendiente de código
   real** — el hallazgo ya anotado en `fase2-cableado.md` (escaneo de 200
   puntos demasiado grueso para encontrar la raíz de IV-142, que vive en
   una ventana angosta cerca del borde superior del dominio) sigue
   presente en el código de hoy, sin fix aplicado. Se verificó con
   escaneo fino (200.000 puntos) que la raíz real existe en x0≈1.73997,
   con parámetros (β=1.2803, α=17.4081) que coinciden con los de la
   propia tesis (x0=1.740, β=1.280, α=17.408) hasta la tercera cifra
   decimal. Es el primer Pendiente de código del proyecto con causa raíz
   y solución completamente caracterizadas — no requiere Facundo, solo
   aprobación de Octavio para tocar el archivo.
2. **La columna "LP3 MMI" de la tabla de cuantiles de tesis para est_04
   no contiene cuantiles de LP3 Indirecto — contiene cuantiles de GVE
   MV**, reconfirmado con reconstrucción independiente (diff ≤0.03%
   contra GVE MV con parámetros propios de METIS, que a su vez ya
   coinciden exacto con los de tesis para ese método). Además se
   encontró que la columna correctamente rotulada "GVE MV" de la propia
   tesis **tampoco** es autoconsistente con ese mismo cálculo (diff
   -7.9% a +9.9%) — amplía la sospecha ya anotada en
   `pendientes-facundo.md` más allá de un simple intercambio de
   columnas. Consecuencia: no existe, en esta estación, ninguna columna
   verificable de cuantiles para el modelo que Facundo efectivamente
   seleccionó.

También reconfirmado, por sexta vez consecutiva y sin una sola excepción
en las 4 estaciones con Etapa 2 completa auditadas en esta ronda (más
est_05/06 de rondas previas): el patrón GVE Momentos-L (β casi exacto,
ν/α muy alejados) — deja de ser "patrón sistemático" para ser
"comportamiento universal confirmado en todo el dataset disponible",
máxima prioridad de consulta a Facundo. Detalle completo en
`regresion-e2e/est_04-e2e.md`. Quedan 4 estaciones con trabajo pendiente:
est_05/06 (cableado incompleto) y est_07/08/09 (desde cero). **Pendiente
de decisión de Octavio: si se aplica el fix propuesto para
`gamma3p.py::mv` (no aplicado en esta ronda).**

**Actualización 14/07/2026 (6):** Octavio aprobó el fix de
`gamma3p.py::mv` con un diagnóstico previo más profundo aportado por la
sesión de contraverificación (Chat) — no era solo densidad de escaneo,
convivían una raíz genuina y una singularidad espuria de borde
(S2=Σ1/zi diverge cerca de x0→min(serie)). Aplicado y verificado por
Code: escaneo denso concentrado hacia el borde + validación
post-convergencia del candidato (β>0, α>0, cota sobre S2 justificada con
los propios números de est_04, sin copiar el margen de LN3p/DECISIÓN020).
est_04 converge ahora a x0=1.739970/α=17.408141/β=1.280309 — coincide con
tesis hasta la 3ª cifra decimal. Verificado sin regresiones en las 9
estaciones del dataset (no solo las 3 mínimas exigidas) y en la suite
completa de tests (109 passed, 1 failed — el pendiente preexistente de
`gen_pareto`/mc, sin relación). Documentado en DECISIÓN 023
(`decisions-log.md`) y en `fase2-cableado.md`. **Primer Pendiente de
código de toda la Fase 4 resuelto de punta a punta.** Nota: el fix no
cierra el EEA del método contra la tesis (4.9251 vs 5.9155, -16.75%) —
mismo patrón de Causa C transversal a todo el proyecto, no específico de
este bug.

**Actualización 14/07/2026 (7):** est_05 rehecha íntegra desde cero, con
el fix de `gamma3p.py::mv` ya aplicado. Etapa 1 y cableado Aprobados sin
reservas nuevas (dos pendientes puntuales ya conocidos, reconfirmados).
`gamma3p`/mv sigue en `no_converge` para esta estación — verificado que
es comportamiento correcto y distinto del bug de est_04 (acá no existe
raíz de IV-142 en el dominio, con o sin escaneo denso; los propios
parámetros de tesis para este método no satisfacen el sistema
IV-140/141). Primera confirmación **completa** (parámetros + EEA + los 7
cuantiles) de un caso de **Causa D** en toda la Fase 4: Log-Normal 3p MV
(el modelo que Facundo eligió) tiene parámetros que coinciden con tesis a
menos de 0.4%, pero el EEA diverge +51.65% — lo suficiente para que el
ranking que produce METIS recomiende GVE MV en su lugar (que sí es PASS
exacto contra tesis, EEA diff ≤0.05%). GVE MV y Gumbel (4 métodos) vuelven
a dar PASS perfecto, tercera estación consecutiva para ambos. GVE
Momentos-L reconfirma el patrón (β cerca, ν/α lejos) por 5ª vez
consecutiva en esta sesión. Detalle completo en
`regresion-e2e/est_05-e2e.md`. Quedan 3 estaciones con trabajo pendiente:
est_06 (cableado incompleto) y est_07/08/09 (desde cero).

**Corrección 14/07/2026:** el párrafo anterior (y `pendientes-facundo.md`)
decían "los propios parámetros de tesis para este método [Gamma3p MV,
est_05] no satisfacen el sistema IV-140/141" — incorrecto, la ficha de
tesis marca esta combinación como NO_APLICABLE sin reportar ningún
x0/α/β, así que no hay parámetros de tesis contra los cuales evaluar
nada. Verificado con escaneo fino de 200.000 puntos sobre todo el
dominio: el residuo de IV-142 es negativo y monótono en todo el rango,
sin raíz interior — la explicación correcta es que el perfil de
verosimilitud no tiene mínimo interior para esta serie, no que una
solución de tesis falle al verificarse. Corregido en
`pendientes-facundo.md` y `regresion-e2e/est_05-e2e.md`.

**Actualización 14/07/2026 (8):** a pedido de la sesión de
contraverificación (Chat), se corrió el mismo test de aislamiento Causa A
vs Causa C que en est_03/LP3, ahora para LN3p MV/est_05, con las
funciones reales `lognormal3p.cuantil()` y `calcular_eea()`. Con los
parámetros propios de la tesis (x0=-2.15, µy=3.3323, σy=1.1137): T=100
diff=+38.40% (vs +38.32% con parámetros de METIS) — diferencia de solo
0.08 puntos porcentuales. **Cuantifica ~99.8% Causa C, ~0.2% Causa A** —
más extremo que el ~95%/5% ya visto en est_03. Adicionalmente, el EEA
calculado con los parámetros exactos de tesis da 8.79 (vs 8.77 con
parámetros de METIS, vs 5.78 que reporta la tesis) — **confirma que el
ranking no se resolvería a favor de LN3p MV ni siquiera con los
parámetros perfectos**, la inversión de Causa D es consecuencia casi pura
del cálculo de EEA/cuantil, no de una diferencia de parámetros. Coincide
con la estimación manual previa de Chat (~+38.33%) — no es un hallazgo de
cableado nuevo. Detalle completo en `regresion-e2e/est_05-e2e.md`,
hallazgo A.

**Actualización 14/07/2026 (9):** est_06 rehecha íntegra desde cero, con
el fix de `gamma3p.py::mv` ya aplicado. **Estación Aprobada sin
reservas — segunda, junto con est_02, donde el ciclo completo (Etapa 1,
cableado, selección de modelo, cuantiles) cierra de punta a punta.** Es
además la más limpia de las 6 en Etapa 1 (n=38 par, sin la ambigüedad de
partición floor/ceil que afecta a est_03/est_05 con n impar). Modelo
seleccionado (Exponencial x0β MV) con PASS exacto en parámetros, EEA y
los 7 cuantiles. GVE MV y Gumbel (4 métodos) vuelven a dar PASS perfecto.
`gamma3p`/mv reverificado con el código corregido — sigue sin raíz
genuina para esta serie (distinto del caso de est_05, acá sí hay
parámetros de tesis reportados y siguen sin satisfacer IV-140/141 al
evaluarlos directo — ver corrección de la ronda anterior en
`pendientes-facundo.md`, que ya dejó esta atribución correcta solo para
est_06). `logpearson3`/mv converge donde tesis no — reconfirmado como
raíz genuina ya verificada (DECISIÓN 019), sin novedad. GVE Momentos-L
reconfirma el patrón (β cerca, ν/α lejos) por **sexta estación
consecutiva sin excepción** (est_01 a est_06) — máxima prioridad de
consulta a Facundo. Detalle completo en `regresion-e2e/est_06-e2e.md`.

**Con est_06 cerrada, 6 de 9 estaciones cumplen el estándar completo de
Fase 4** (est_01, 02, 03, 04, 05, 06). Quedan est_07, est_08 y est_09,
las 3 restantes, ninguna analizada aún con este estándar.

**Actualización 14/07/2026 (10):** est_07 completada desde cero —
primera de las 3 estaciones que nunca habían tenido ninguna ronda de
Fase 2/4 previa. Etapa 1, cableado (34/34, primera vez para esta
estación) y selección de modelo Aprobados. Gumbel (4 métodos) y GVE MV
vuelven a dar PASS perfecto, 5ª y 4ª estación consecutiva
respectivamente. GVE Momentos-L reconfirma su patrón por 7ª estación
consecutiva sin excepción.

**Hallazgo transversal nuevo, el más relevante de esta ronda:** la
convención de redondeo de `n_w1` en la partición de Cramer (DECISIÓN011)
no es universal. est_02 (n=24) necesita específicamente `ceil(n×0.6)=15`
y no `round=14`; est_07 (n=19) necesita específicamente `round/floor
(n×0.6)=11` y no `ceil=12` — las dos estaciones se contradicen entre sí,
y est_04 (el otro respaldo original de DECISIÓN011) nunca pudo
distinguir entre las reglas porque para su n, `ceil` y `round` coinciden.
No cambia ningún veredicto de homogeneidad (Cramer aprueba con cualquier
partición en todos los casos verificados), pero es un dato concreto y
accionable para escalar a Facundo — agregado a `pendientes-facundo.md`
junto al hallazgo ya existente sobre `n_w2` (que tiene la misma
naturaleza de inconsistencia). Detalle completo en
`regresion-e2e/est_07-e2e.md`. Quedan est_08 y est_09.

**Actualización 15/07/2026:** est_08 completada desde cero — segunda de las
3 estaciones sin ninguna ronda previa de Fase 2/4 (junto con est_01, que sí
la tuvo parcialmente vía Bloque 8). Etapa 1 sale limpia, sin discrepancias
de datos base, con un hallazgo nuevo puntual: el valor crítico de tabla que
imprime la tesis para Cramer/t-Student en esta estación (1.6829) corresponde
a la convención de **una cola** al 5%, no a las **dos colas** (α/2=0.025)
que la fórmula documentada (Ec. III-8) exige y que las 8 estaciones
anteriores reproducían sin excepción — verificado con `scipy.stats.t.ppf`
que 1.6829 es exactamente `t.ppf(0.95, df=41)`, no `t.ppf(0.975, df=41)`
(=2.0195, el valor que usa METIS). No cambia ningún veredicto en esta
estación puntual — queda como inconsistencia de la propia fuente entre
estaciones, agregada a `pendientes-facundo.md`.

**Hallazgo de mayor severidad de toda la Fase 4 hasta ahora — Gamma 3p MV,
Causa D extrema.** A diferencia de est_05 (donde Causa D invertía el orden
entre el #1 y el #2 del ranking), en est_08 el ranking propio de METIS ubica
en el **#1 absoluto** a Gamma 3p MV (EEA=8.838) — con parámetros que
coinciden con la tesis a menos de 0.03% pero un EEA que no tiene relación
con el 11.6228 que la tesis reporta para esos mismos parámetros. Verificado
por tres vías independientes (función real con parámetros propios, función
real con parámetros exactos de tesis, y cuantil exacto de la Gamma vía
`scipy.stats.gamma.ppf` sin pasar por la aproximación IV-144) — las tres dan
resultados en el mismo rango (8.6-8.8), ninguna cerca de 11.62. Descarta
tanto error de parámetros como error de aproximación numérica: es Causa C
pura, con la consecuencia práctica más grave documentada — el modelo que
Facundo eligió (Gumbel ML, fiel y disponible en METIS) queda en el puesto
#6 del ranking que METIS expondría, detrás de cuatro distribuciones que ni
siquiera aparecen cerca del top en la tabla original de la tesis. Detalle
completo con las tres verificaciones en `regresion-e2e/est_08-e2e.md`.

**Corrección de conteo, aplica a est_01-08:** el conteo "34/34 combinaciones
distribución×método" usado en los 8 documentos de estación anteriores es un
error heredado — nunca se recontó desde el código. Sumando
`METODOS_APLICABLES` real de las 13 distribuciones, el total es **35**, no
34 (`gen_pareto` tiene 4 métodos —momentos, mv, mc, mpp— y ese +1 respecto
del conteo asumido explica la diferencia). No se corrigió retroactivamente
el texto de est_01-07 en esta sesión — el número real queda documentado acá
y en `regresion-e2e/est_08-e2e.md` para que el informe de consolidación
final use 35, no 34.

GVE Momentos-L reconfirma el patrón (β cerca, ν/α lejos) por **octava
estación consecutiva sin excepción** (est_01 a est_08) — ya no es "patrón
sistemático", es comportamiento universal en todo el dataset auditado con
Etapa 2 completa. Gumbel (4 métodos) y GVE MV vuelven a dar PASS perfecto,
octava y séptima estación consecutiva respectivamente.

**Con est_08 cerrada, 7 de 9 estaciones cumplen el estándar completo de
Fase 4** (est_01 a est_08, salvo est_09 que sigue sin analizar). Queda
únicamente est_09 (La Suela, n=7, caso de bloqueo duro del contrato).

**Actualización 15/07/2026 (final) — est_09 completada, las 9 estaciones
del dataset quedan analizadas con el estándar completo de Fase 4.**
Primera estación donde se verificó en vivo el único caso de bloqueo duro
de todo METIS (n=7<10): `ejecutar_etapa1()` corta la ejecución en el
contrato, sin ejecutar ninguna prueba, exactamente como especifica la
arquitectura — confirmado, no asumido. La reconstrucción académica (fuera
del flujo real, mismo mecanismo que est_01) de Etapa 1 y Etapa 2 resultó
ser una de las más limpias del proyecto: modelo seleccionado (Uniforme
Momentos) con el mejor PASS de cuantiles de las 9 estaciones (diff
≤0.015%), Log-Normal 2p sin Causa C apreciable (caso atípico, el resto del
proyecto muestra -8% a -28%), y GVE Momentos-L con la magnitud de
divergencia más leve del dataset (aunque el patrón cualitativo — β cerca,
ν/α lejos — se confirma sin excepción por novena vez consecutiva, ya
comportamiento universal).

**Hallazgo — causa raíz confirmada por verificación cruzada, diagnóstico
original refutado y corregido.** `lognormal3p.py::mv` converge, para
est_09, a `x0=-176.56` (físicamente implausible, muy por debajo del
mínimo de la serie), donde la tesis reporta NO_CONVERGE. La primera
descripción de este hallazgo (Code) decía que la función objetivo era
monótona hacia `lo` y que ahí estaba el "mínimo genuino" — **incorrecto,
refutado por Octavio evaluando la función directamente muy cerca de
`xi_min`: diverge sin límite a -∞ acercándose a `hi`, no a `lo`**
(degeneración de verosimilitud no acotada, DECISIÓN020, del lado opuesto
al identificado primero). Confirmado por Code instrumentando la llamada
real: con el dominio completo, Brent nunca evalúa ni un punto a menos de
71 unidades de `hi` — converge en una región casi plana cerca de `lo` por
su tolerancia, sin ver nunca la parte relevante del dominio. Conclusión
verificada por ambas partes con la función real: no hay mínimo finito;
`x0=-176.56` no es un óptimo genuino ni una falsa convergencia de borde
al estilo DECISIÓN019 — es un modo de falla distinto (verosimilitud no
acotada + optimizador que no explora la región relevante), sin paralelo
directo con los dos guards ya aplicados en el proyecto. Detalle completo
en `regresion-e2e/est_09-e2e.md`, Hallazgo B.

**RESUELTO — 15/07/2026 (DECISIÓN 025).** Octavio aprobó un prototipo de
guard de "ausencia de óptimo finito" (escaneo grueso, mismo mecanismo de
DECISIÓN023 con criterio distinto: el mínimo del escaneo no debe caer en
el primer ni el último punto finito), tras verificarlo por su cuenta
contra las 9 series. Un primer diseño con margen porcentual fijo se
descartó por dar falsos positivos en 6 de las 8 estaciones buenas — el
criterio final no usa margen, solo exige que exista al menos un punto de
recuperación antes del borde. Aplicado a `lognormal3p.py::mv` y verificado
sin regresión: est_01 a est_08 dan parámetros idénticos a los de antes del
fix; est_09 ahora da `NO_CONVERGE`, coincidiendo con la tesis. `pytest` →
109 passed (mismo failing preexistente sin relación). **Último Pendiente
de código que quedaba abierto en el proyecto — con esto, las 9 estaciones
quedan sin ningún hallazgo de código sin resolver.** Detalle completo en
`decisions-log.md`, DECISIÓN 025, y en `regresion-e2e/est_09-e2e.md`.

**Censo de DECISIÓN011 (n_w1 de Cramer) — ya no es mayoría, es empate.**
Con est_09 (n=7, discrimina, contradice `ceil`), el conteo de estaciones
que discriminan entre `ceil` y `round`/`floor` para n_w1 queda en 4 de 9
(est_02, est_05, est_07, est_09) — 2 confirman `ceil` (est_02, est_05) y 2
lo contradicen (est_07, est_09). Ya no es "regla mayoritaria con una
excepción" (como se documentó al cerrar est_07) — es un empate real.
Actualizado en `pendientes-facundo.md`.

**Valor crítico de tabla — una cola vs. dos colas, segunda confirmación.**
est_09 repite exactamente el patrón encontrado por primera vez en est_08:
el valor crítico que imprime la tesis para Cramer/t-Student (2.015, GL=5)
corresponde a `t.ppf(0.95, 5)` (una cola), no a `t.ppf(0.975, 5)=2.5706`
(dos colas, Ec. III-8) que aplica METIS de forma consistente. Ya son 2 de
9 estaciones con esta desviación — deja de ser un caso aislado de est_08.

## Pendientes transversales (no ligados a una estación puntual)

- **`gen_pareto`/MPP:** epsilon mal condicionado sin guard de
  plausibilidad — decisión de diseño de Octavio/Carlos, no verificado
  para ninguna de las 9.
- **DECISIÓN 016 (título vs. n real):** nunca se hizo el cruce formal
  para ninguna de las 9 estaciones.
- **Conteo real de combinaciones distribución×método: 35, no 34**
  (hallazgo est_08, 15/07/2026) — corregir en el informe de consolidación
  final; no se tocó retroactivamente el texto de est_01-07.

## Próximo paso

Llevar cada estacion al nivel de cableado maximo, donde se checkee al 100% la integridad del pipeline y funcionamiento optimo/acorde
(13 distribuciones, reconstrucción propia completa)  mismo estándar, con maxima rigurosidad posible, llegando a las conclusiones de "Aprobado" o "Pendiente de código/dominio" sin ninguna casilla en blanco. 

# Fundamental:

Se trata de el 1er analisis e2e del desarrollo, por lo que lo mas importante es obtener conclusiones e informacion respecto a ello, para saber en que posicion estoy parado, saber que esta pendiente para escalar a los directores, que esta por implementarse apropiadamente (como IV-153 por ejemplo), donde hay errores y fallas, que queda pendiente para implementar que se sabe (como Gamma 3p MPP que no aparece la formula en tesis), que es lo que esta operando correctamete, en donde puede inferirse que los resultados de Facundo no pueden alcanzarse, ya sea que no se entiende como llego a dichos resultados, que casos comprenden a propias limitaciones de excel, ya sea redondeo, etc. y demas informacion relevante para tener un informe integral y profesional, lo mas estricto para dicha tesis en cuestion.

---

## est_01 — detalle completo movido a archivo por estación (14/07/2026)

El análisis E2E completo de est_01 (Alpa Corral – Río Barrancas) —
Etapa 1 reconstruida estadístico por estadístico, cableado de las 13
distribuciones (34/34), comparación completa de parámetros/EEA/cuantiles
contra la tesis, y los 9 hallazgos (A-I) con su clasificación de causa —
vive ahora en `regresion-e2e/est_01-e2e.md`, mismo patrón de organización
que `regresion-pipeline/` y `regresion-unitaria/` para las fases previas.
Se movió el detalle fuera de este archivo para que `fase4-e2e.md` quede
como metodología + tabla de consolidación + patrones transversales entre
estaciones, sin crecer sin límite a medida que se completan las 9.

Ese archivo incluye, además del análisis primario, una contraverificación
independiente (sesión aparte, mismo día) que confirmó los puntos centrales
y aportó dos elementos: (1) doble método de reconstrucción de cuantiles
que descarta dos hipótesis alternativas antes de confirmar Causa C, y (2)
una cita de fuente primaria (PDF de la tesis) para la contaminación cruzada
de x0 entre est_01 y est_02 en Log-Normal 3p MV — atribuida explícitamente
a esa sesión, no verificada de forma independiente en este entorno.

Resumen (ver detalle completo en el archivo por estación):
- Etapa 1: Aprobado a nivel de veredicto (rechazo unánime coincide con la
  tesis). Estadísticos puntuales de Helmert/Wald-Wolfowitz con Pendiente de
  dominio — discrepancia de datos base (diff de suma exacta de 14.0 sobre
  n=40, no explicable por redondeo).
- Cableado: Aprobado, 34/34 combinaciones distribución×método.
- Selección de modelo: Pendiente de código — Gamma 3p MPP (modelo ganador
  de Facundo) no implementable por ausencia de fórmula fuente.
- Cuantiles: Pendiente de dominio — Causa C confirmada por doble método
  (la propia fórmula de la tesis, con los propios parámetros de la tesis,
  no reproduce la propia tabla de cuantiles de la tesis).
- Clasificación general: **Parcial** — Etapa 1 y cableado Aprobados sin
  reservas; Etapa 2 con 1 Pendiente de código y múltiples Pendientes de
  dominio, ninguno atribuible a error de METIS.
