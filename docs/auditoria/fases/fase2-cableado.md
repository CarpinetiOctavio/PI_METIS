# Auditoría de Funcionamiento METIS — Fase 2: Cableado e Integración
### Estado - Incompleto al 12/07/2026 - Queda completar auditoria de Testing para desbloquear Bloques 6 en adelante.

## Estado
Fase 1 (unitarias, archivo por archivo, fidelidad a la tesis) completada.
Ver `rules/auditoria/fase1-unitarias.md` — sección "Insumos para Fase 2"
para la lista de archivos y funciones confirmados como CERRADO — FIEL A
LA TESIS. Esta fase solo trabaja sobre esos archivos. Si algún archivo
no aparece en esa lista como cerrado, no se audita su cableado todavía —
se vuelve a Fase 1 primero.

Cierre formal de Fase 1 documentado en DECISIÓN 022 (decisions-log.md,
10/07/2026). Esa misma decisión deja pendiente un análisis de
DUPLICACIÓN de código (`_skewness` y M̂0/M̂1/M̂2 reimplementados en
varios archivos de distribución en vez de importarse de
`descriptive.py`) — es un tipo de hallazgo DISTINTO al que busca esta
fase (acá se busca argumento mal pasado por el orquestador, no lógica
duplicada dentro de un módulo) y no se resuelve acá. Si en el Bloque 6
aparece una oportunidad natural de señalarlo al pasar, documentarlo,
pero el refactor en sí no es objetivo de esta fase.

## Qué es esta fase y qué NO es

Fase 1 verificó el "qué": ¿la fórmula implementada coincide con la
ecuación de la tesis? Esta fase verifica el "cómo se conecta": ¿el
orquestador (pipeline.py para Etapa 1, el módulo equivalente de
Etapa 2) le pasa a cada función el argumento correcto, con la
semántica correcta — no solo el tipo?

No se re-audita ninguna fórmula acá. Si en el camino aparece una
sospecha de que una fórmula está mal (no solo mal cableada), se
detiene el análisis de esa función, se documenta la sospecha, y se
deriva a la sesión de Fase 1 — no se resuelve acá.

## Origen de esta fase — bug ya confirmado como caso de referencia

En `pipeline.py`, dentro de `ejecutar_etapa1()`, se calculaba una
partición de datos (60%/30%, vía `int(n_total*0.60)` / `int(n_total*0.30)`)
pensada para `calcular_cramer()`, y esa misma partición se pasaba por
error como `n1`/`n2` a `calcular_t_student()`. Según la tesis (III-8),
t-Student debe usar partición mitad/mitad (`n1=n//2`, `n2=n-n//2`).
`calcular_t_student()` en sí es fiel a la tesis — el error no estaba en
la función sino en qué le pasaba el orquestador.

Verificado numéricamente con la serie real de est_02 (n=24):
- Partición mitad/mitad (12/12): t=-1.7643, GL=22 → coincide con la
  tesis (t=-1.76, GL=22).
- Partición real que produce pipeline.py (14/7): t=-3.2445, GL=19 →
  no coincide, y el veredicto de homogeneidad se invierte.

Corrida de `ejecutar_etapa1()` end-to-end hoy sobre est_02 a est_06:
ninguna de las 5 reproduce el t-Student documentado en su MD. En
est_02 y est_06 se invierte hasta el veredicto. Esto confirma que las
auditorías de regresión previas (Fase 1 / auditoría de regresión
anterior) verificaron funciones aisladas, nunca el pipeline integrado.

Fix aprobado (pendiente de aplicar y re-verificar en esta fase):
eliminar el bloque de partición 60/30 en `pipeline.py` (código muerto
para Cramer, que resuelve su propia partición internamente vía
`particion="default"` con `ceil`/`round`, DECISIÓN 011) y pasar a
`calcular_t_student()`: `n1 = n // 2`, `n2 = n - n // 2`.

## Qué buscar — patrón de bug

Por cada función confirmada fiel a la tesis en Fase 1, y por cada
llamada que le hace un orquestador:

1. Tomar la firma real de la función (parámetros, qué representa cada
   uno según su implementación y su verificación en Fase 1).
2. Tomar el fragmento exacto del orquestador donde se arma el
   argumento y se invoca la función.
3. Preguntar: ¿el valor que recibe el parámetro tiene el mismo
   SIGNIFICADO que la función espera, no solo el mismo tipo? El
   patrón ya confirmado es: una variable calculada para un propósito
   (partición de Cramer), reutilizada como argumento de otra función
   con propósito distinto (partición de t-Student).
4. Señalar también variables que el orquestador calcula pero que
   ninguna función usa (código muerto), y parámetros con default que
   se están sobreescribiendo sin necesidad.

## Orden de barrido

No avanzar de bloque sin cerrar el anterior. Dentro de cada bloque,
recorrer solo los archivos/funciones que Fase 1 marcó como cerrados;
si falta alguno, señalarlo y saltarlo (no inventar su estado).

1. **Estadística descriptiva** — verificar qué serie recibe
   `calcular_descriptiva()` desde el orquestador (filtrada vs. cruda,
   orden, tipo de dato) y si hay algún parámetro con semántica
   ambigua.
2. **Etapa 1 — Independencia** (Anderson, Wald-Wolfowitz) — mismo
   chequeo de firma vs. argumento real que se hizo para t-Student.
3. **Etapa 1 — Homogeneidad** (Helmert, t-Student, Cramer) — aplicar
   y re-verificar el fix ya aprobado (ver arriba). Confirmar que
   `calcular_cramer()` no recibe nada distinto de `"default"` en
   ningún flujo real sin que se haya decidido explícitamente.
4. **Etapa 1 — Tendencia y atípicos** (Mann-Kendall, KS, Chow) —
   solo si Fase 1 ya las cerró; si no, quedan pendientes de Fase 1
   primero.
5. **Veredicto y nivel de confianza global de Etapa 1**
   (`determinar_nivel_homogeneidad`, `determinar_nivel_independencia`,
   lógica de `nivel_confianza` en `ejecutar_etapa1()`) — revisar como
   lógica de agregación: ¿usa los resultados correctos de cada test,
   o hay algún resultado desincronizado/recalculado?
6. **Etapa 2 — Parámetros por distribución** — por familia
   (Uniforme, Exponencial, GVE, Normal, LogNormal 2p/3p, Gamma 2p/3p,
   Gumbel, LP3): ¿el orquestador de Etapa 2 le pasa a cada método de
   estimación los datos y la serie correctos?
7. **Etapa 2 — EEA y cuantiles** — verificar que el cálculo de EEA y
   de cuantiles usa los parámetros que efectivamente estimó el paso
   anterior para esa distribución/método, y no un valor recalculado
   o de otra combinación distribución-método por error de índice o
   de variable.

PRIORIDAD — casos ya identificados en Bloque 3 con esta firma
exacta (parámetros ~idénticos, EEA muy distinto), pendientes de
verificar contra el orquestador real, no reproducidos aún en
Fase 1 por estar fuera de su alcance (ver DECISIÓN 022 y
pendientes-facundo.md, sección "Causa C"):
- Gamma 2p — Momentos, MV y ML (est_02, est_03, est_05, est_06)
- LogNormal 3p — MV (est_05, est_06)
- Normal — Momentos/MV y ML (est_02, est_03)
- LogNormal 2p — Momentos/MV (est_06, con la salvedad de que en
    est_02/03/05 la tesis marca NO_APLICABLE por motivo desconocido
    — ver pendientes-facundo.md)
Empezar el barrido de este bloque por estos cuatro casos antes de
generalizar al resto de las distribuciones.

8. **Prueba end-to-end** — recién al cerrar los bloques 1 a 7: correr
   el pipeline completo (Etapa 1 + Etapa 2) sobre est_02 a est_06 y
   comparar contra los MDs existentes de cada estación. Este resultado
   reemplaza el "PASS" anterior (válido solo para funciones aisladas)
   por un PASS real de integración.

Antes de comparar contra un MD de estación, confirmar que el título
del archivo coincide con el n real de la serie (cruzar contra la
tabla de DECISIÓN 016) — se encontraron títulos de estación
incorrectos durante la auditoría de Bloque 3

## Reglas de operación

- Verificación numérica independiente antes de aprobar cualquier
  hallazgo — no aceptar lo que reporte Code sin reproducirlo con la
  serie real correspondiente.
- No clasificar ninguna discrepancia como Causa C sin agotar primero
  la hipótesis de bug de cableado.
- No aprobar ningún fix de código sin ver el fragmento exacto (el
  código real, no una descripción de Code).
- Si aparece una sospecha de error de fórmula (no de cableado), no se
  resuelve acá — se documenta y se deriva a Fase 1.
- Cada hallazgo se documenta con: archivo, función, línea, qué recibe
  hoy, qué debería recibir según Fase 1, fix propuesto. Nada se aplica
  sin aprobación explícita de Octavio.

## Rol de Octavio

Intermediario entre esta sesión y el chat de Code, que tiene acceso
al repositorio real. Ningún fix se aplica directo desde esta sesión.


-----------------------------------------------------------------------
## HALLAZGOS PENDIENTES DE CIERRE
-----------------------------------------------------------------------

## Pendiente — Implementación de RF-CU01-05 / RF-CU02-05 (decisión de
usuario ante valores faltantes en la serie Y)

Origen: surgió durante Fix 1 de Fase 2 (crash en contract.py por
timestamps faltantes), al distinguir que "valores faltantes" en
RF-GEN-P-02 se refiere a la serie Y (dato medido), no a la columna de
tiempo (que en METIS siempre está determinada, series anuales).

Estado actual del código: contract.py solo DETECTA valores faltantes
en la serie (CONTRACT_MISSING_VALUES) — no implementa el flujo de
decisión del usuario que exige RF-CU01-05 (CU-01, persiste la
decisión) ni RF-CU02-05 (CU-02, no persiste). No existe ningún
mecanismo de "completar con la media / eliminar registro" en ningún
archivo auditado hasta ahora.

Lo que falta construir (comparable en alcance a lo que ya existe para
Chow — session_store, evento SSE outlier_detected, wait_for_decision):
- Detectar el faltante (ya existe).
- Pausar y presentar al usuario las dos opciones (completar con
  media / eliminar registro).
- Esperar la decisión (mecanismo análogo a wait_for_decision de Chow).
- Aplicar la decisión: completar con la media de la serie (con
  advertencia estadística explícita, por RF-CU01-05) o eliminar el
  registro (dato + timestamp correspondiente).
- Re-ejecutar el pipeline con la serie corregida.
- Persistir la decisión (CU-01) o no persistirla (CU-02), según
  RF-CU01-02/RF-CU02-05.

No es parte del alcance de la auditoría de cableado (Fase 2) — es una
feature nueva, no una corrección de wiring existente. Queda pendiente
para tratarse en una sesión/sprint propio.

## Pendiente — Validación de contrato: valor Y sin fecha X

Origen: surgió al cerrar Fix 1 de Fase 2 (crash en contract.py por
timestamps faltantes). Al descartar que el caso real fuera "año
completo faltante" (eso ya lo maneja _espaciado_regular() sin cambios),
apareció un gap real y distinto: hoy es posible que una fila tenga
valor de la serie Y sin que tenga fecha X correspondiente, y nada en
el código lo detecta ni lo impide.

Regla definida por Octavio (13/07, sesión de auditoría Fase 2): un
valor Y no puede existir sin su fecha X. La inversa sí es válida — una
fecha X puede existir sin valor Y (ese es el caso ya cubierto por
RF-CU01-05/CU02-05, valores faltantes, con su propio pendiente de
implementación ya registrado aparte).

No está en ningún RF existente (RF-GEN-P-01, RF-GEN-P-02, RF-CU03-03
revisados, no aparece) — es una regla nueva, no una corrección de algo
ya documentado.

Comportamiento definido: NO bloqueante. Se descarta automáticamente la
fila con Y sin X, se genera un warning informando cuántos registros
fueron descartados por este motivo, y el pipeline continúa con el
resto de la serie. Coherente con el principio general de "detecta e
informa, no bloquea salvo n<10" que ya rige el resto del contrato.

Estado actual del código: parser.py arma serie y timestamps en
paralelo, cada uno preservando None de forma completamente
independiente — no hay ningún cruce posicional entre las dos listas,
ni en parser.py ni en contract.py.

Lo que falta construir: comparación índice por índice entre serie y
timestamps (hoy no existe esa correlación en ningún punto del código),
filtrado de las filas que violan la regla antes de que la serie entre
al resto del contrato, y el warning correspondiente con el conteo de
filas descartadas.

Fuera del alcance de esta auditoría de cableado (Fase 2) — es una
validación nueva de contrato, no una corrección de wiring existente.
No se envía a Code todavía. Queda pendiente para tratarse aparte.

## Actualización 13/07/2026 — Metodología de verificación profunda: unitario vs. pipeline (no solo contra ficha)

**Motivo:** comparar un valor de `est_XX.md` contra una corrida del pipeline en vivo mezcla dos preguntas distintas — "¿la ficha está desactualizada?" y "¿hay un bug de cableado real?" — y no permite distinguir una de la otra. Si el pipeline en vivo difiere de la ficha, no se puede concluir cableado: puede ser simplemente que la ficha se generó en otro momento, con otro código o con otro método de comparación (regresión unitaria, no e2e).

**Método adoptado para aislar cableado de forma inequívoca:** para una distribución y método dados, correr dos cosas con el código de **hoy**, y comparar una contra la otra — nunca contra la ficha:

1. **Llamada aislada ("unitaria"):** `modulo.ajustar(serie, metodo)` → si `status=="ok"`, `modulo.cuantil(p, parametros)` para las probabilidades de `probabilidades_weibull(serie)` → `calcular_eea()`. Reproduce a mano la misma secuencia que hace `pipeline2.py` internamente, pero fuera del loop del orquestador.
2. **Corrida real:** `ejecutar_etapa2(serie)`, tomando el `MetodoResult` correspondiente del ranking.

Si (1) y (2) coinciden, el cableado de esa distribución/método está confirmado correcto, sin importar lo que diga cualquier ficha — ambas corridas son de hoy, con el mismo código, no hay margen para "desactualizado". Si difieren, es un hallazgo de cableado real y se documenta con el fragmento exacto (archivo, función, línea).

Este método pasa a ser el estándar de verificación para el resto de Bloque 6/7 (las 9 distribuciones aún no revisadas), en lugar de comparar directamente contra `est_XX.md`.

**Resultados ya obtenidos con este método (est_02, n=24):**

| Distribución/método | (1) Unitario | (2) Pipeline en vivo | ¿Coinciden? | vs. ficha est_02.md |
|---|---|---|---|---|
| Gamma 2p / MV | α=64.031, β=2.227, EEA=34.8765 | α=64.031, β=2.227, EEA=34.8765 | **Sí** | Ficha decía EEA=27.09 — desactualizada, no cableado |
| Log-Normal 3p / MV | x0=38.469, µy=4.0031, σy=1.2927 | (mismo) | **Sí** | Ficha (nota PASO7) decía x0≈33 — nota incorrecta, no cableado. Cuantiles de diseño (T=2..100) recalculados con estos parámetros divergen fuerte de la tesis en T altos (+43% en T=100) pese a parámetros casi idénticos — Causa C, pendiente Facundo, no cableado |

**Pendiente:** aplicar este mismo método a las 9 distribuciones restantes (Uniforme, Exponencial β, Exponencial x0/β, Gen. Exponencial, Normal, LogNormal 2p, Gamma 3p, Gumbel, GVE, Log-Pearson III, Gen. Pareto) antes de dar Bloque 6/7 por cerrado. Pedido a Code en curso.

## Actualización 13/07/2026 (cierre) — Bloque 6 y Bloque 7: CERRADOS

**Alcance cubierto:** las 13 distribuciones de Etapa 2, verificadas mediante el método unitario-vs-pipeline establecido en la actualización anterior, sobre las 4 estaciones prioritarias (est_02, est_03, est_05, est_06).

- **est_02:** cobertura completa — 28 de 34 métodos verificados con reconstrucción independiente (código real, no resumen). 0 hallazgos de cableado.
- **est_03, est_05, est_06:** Gamma 2p (3 métodos) verificado con reconstrucción independiente en cada una — 0 hallazgos. Las 13 distribuciones corridas vía pipeline completo, con foco en detectar ramas de código no ejercitadas por est_02 y cambios de `status` entre estaciones.

**Resultado: 0 hallazgos de cableado en las 4 estaciones.**

### Ramas nuevas ejercitadas (no vistas en est_02) — todas verificadas, sin hallazgo

| Rama | Dónde se ejercitó | Verificación |
|---|---|---|
| GVE/MV — fallback a Momentos-L (guard IV-202 falla con la condición inicial de Momentos) | Las 4 estaciones (incluida est_02) | Guard falla matemáticamente por diseño cuando `nu` de Momentos está muy alejado de la escala de los datos — confirmado a mano en est_05/06. Fallback funciona como está previsto. |
| LogPearson3/MV — NO_CONVERGE por borde inferior (no superior) | est_03 | Reconstruido: `y0` converge a distancia 0.000000 del borde inferior — falsa convergencia de borde genuina, el guard simétrico dispara correctamente. |
| Gamma3p/Momentos — NO_APLICABLE por violación de soporte (`x0 ≥ min(serie)`) | est_03 | Reconstruido: x0=15.4355 ≥ min=2.0 — confirmado, comportamiento correcto (ya anotado como tal en la ficha vieja de est_03). |
| Gen.Pareto/MC — converge en vez de NO_CONVERGE | est_03, est_06 | epsilon lejos de la zona de fragilidad conocida (ε≈0) en ambos casos — no reconstruido en detalle por falta de código fuente de este método puntual, sin señal de alarma. |

**Rama aún sin ejercitar en ninguna estación:** `STATUS_DISABLED_ZEROS` — ninguna de las 4 series tiene ceros (mínimos: 42.0 / 2.0 / 0.9 / 14.0). Si alguna estación fuera de esta lista prioritaria tiene ceros, esa rama sigue sin verificación real.

### Hallazgo de diseño (no bug, no cableado) — Gen. Pareto / MPP, confirmado en las 4 estaciones

El mismo patrón de est_02 (epsilon mal condicionado, EEA sin sentido físico) se repite en las 4: est_03 (eps=4.1475, EEA=212 millones), est_05 (eps=4.1386, EEA=125 millones), est_06 (eps=4.2996, EEA=136 millones). Confirma que no es un caso aislado de una serie particular — es una fragilidad sistemática del estimador MPP para esta distribución. Sigue pendiente la decisión de diseño (guard de plausibilidad de epsilon), no resuelta en esta auditoría.

### Cierre formal

**Bloque 6 y Bloque 7: CERRADOS.** Sin hallazgos de cableado en ningún punto verificado, en ninguna de las 4 estaciones. Insumo de Causa C consolidado por separado en `pendientes-facundo.md` (actualización de hoy).

**Pendiente explícito, no resuelto acá:** Bloque 8 (prueba end-to-end, est_02 a est_06 completas contra sus MDs) sigue sin iniciarse — las corridas de "pipeline completo" documentadas en cada `est_0X-pipeline.md` fueron diagnósticas para esta auditoría de cableado, no constituyen ese cierre.

## Actualización 14/07/2026 — Hallazgo durante Bloque 8 (e2e): pendiente de reapertura de Fase 1 en `gamma3p.py`/MV

**Origen:** surgió al correr el pipeline completo de est_04 para Bloque 8 (prueba end-to-end). No es un hallazgo de cableado — no hay nada mal pasado por el orquestador — es un problema dentro de la propia función `ajustar()` de `gamma3p.py`, método `mv`. Se documenta acá porque es donde se encontró, tal como indica la nota general de esta fase para hallazgos de fórmula que aparecen en el camino: se señala y se deriva, no se resuelve en Bloque 6/7/8.

**Qué se encontró:** el escaneo de 200 puntos uniformes entre `lo=xi_min-20·S` y `hi=xi_min-1e-9` (usado para localizar cambios de signo de IV-142 antes de aplicar `brentq`) no detecta la raíz cuando esta vive en una ventana angosta cerca de `hi`, si `S` es grande respecto al ancho de esa ventana.

**Verificado numéricamente en est_04 (n=36, xi_min=2.0, S=19.70):**
- Dominio de búsqueda: `lo=-391.997`, `hi=2.000000` (~394 unidades de ancho).
- Escaneo actual (200 puntos): paso ≈1.98 unidades entre puntos consecutivos.
- Existe una raíz genuina de IV-142 en **x0≈1.7401** — evaluando la función punto por punto: IV-142(1.70)=-0.174, IV-142(1.74)=+0.000142 (prácticamente cero), IV-142(1.76)=+0.098. Cruce de signo real y localizado.
- Este x0 coincide, hasta la tercera cifra decimal, con el **x0=1.740 que reporta la propia tesis** como su solución MV para esta estación (alfa=17.408, beta=1.280).
- El escaneo de 200 puntos no encuentra ningún cambio de signo en todo el dominio (confirmado programáticamente) — la ventana donde vive la raíz (~1.70 a ~1.99, un ancho de ~0.3 unidades) es más angosta que el paso del escaneo (~1.98 unidades), así que ningún par de puntos consecutivos cae a ambos lados del cruce. El método concluye `NO_CONVERGE` con una solución válida y encontrable existiendo.

**Alcance verificado — no es un problema generalizado, acotado a est_04 entre las estaciones con dato de referencia:**
- **est_02:** `NO_CONVERGE` genuino — sin raíz en todo el dominio ni con escaneo fino de 20.000 puntos. Coincide además con que la propia tesis reporta `NO_CONVERGE` para este caso. Sin acción.
- **est_03:** `NO_CONVERGE` genuino — sin raíz ni con 20.000 puntos. La tesis reporta x0=13.664 como su propia solución, pero ese valor es **mayor que el mínimo de la serie (2.0)** — viola la restricción de soporte de la fórmula (zi=xi-x0>0 para todo i). Es el mismo patrón ya documentado para est_06 (parámetros de tesis que no satisfacen IV-140/141 al evaluarlos directamente) — pendiente Facundo ya existente, no este bug de escaneo.
- **est_05:** tesis marca `NO_APLICABLE`, sin x0 de referencia contra el cual testear si el escaneo se pierde algo — queda como ya estaba clasificado (funcionalmente equivalente a `NO_CONVERGE` de METIS).
- **est_06:** ya confirmado por separado en la sesión anterior (escaneo de 5000 puntos) que no hay raíz en el dominio — pendiente distinto, ya cerrado como tal.

**No resuelto acá — pendiente de reapertura de Fase 1 para `gamma3p.py`/MV, con este hallazgo como insumo. No requiere consulta a Facundo — es un problema de implementación de METIS, no de interpretación de la tesis.**

**Fix propuesto (no aplicado, requiere aprobación explícita antes de tocar código):** reemplazar el escaneo uniforme por uno más denso hacia el borde superior del dominio (espaciado geométrico/logarítmico decreciente hacia `hi`, o aumentar sustancialmente la cantidad de puntos). No aceptar ningún fix de Code sin ver el fragmento real y reproducirlo contra est_04 (y de paso re-confirmar que no rompe est_02/03/05/06, que hoy están bien clasificados como `NO_CONVERGE` genuino o pendiente de otra naturaleza).

**RESUELTO — 14 de Julio de 2026 (Fase 4, DECISIÓN 023 en decisions-log.md).**
Diagnóstico ampliado: no era solo un problema de densidad de escaneo — el
mapeo fino del intervalo reveló una raíz genuina en x0≈1.7315–1.7651
(coincide con tesis) **y además** una singularidad espuria de borde
(S2=Σ1/zi diverge cuando x0→min(serie), mismo tipo de patología que
LN3p/DECISIÓN020, pero con escala distinta — no se reutilizó el margen de
LN3p). Fix aplicado: escaneo denso concentrado hacia `hi` (geométrico) +
validación post-`brentq` del candidato (β>0, α>0, cota de plausibilidad
sobre S2) en vez de tomar el primer bracket sin validar. Verificado:
est_04 converge a x0=1.739970/α=17.408141/β=1.280309 (coincide con tesis
hasta la 3ª cifra decimal); est_01/02/03/05/06 sin cambios (siguen
`no_converge`, sin convergencias espurias nuevas); est_07/08/09 sin
cambios en sus valores ya correctos. Suite completa: 109 passed, 1 failed
(el pendiente preexistente de `gen_pareto`/mc, sin relación). Detalle
completo de la verificación en DECISIÓN 023, `decisions-log.md`.


## Actualización 14/07/2026 — Cierre de Bloque 8 (prueba end-to-end, est_02 a est_06)

**Salvedad de alcance, no resuelta:** el documento rector pide cruzar título de estación contra n real (DECISIÓN 016) antes de comparar contra cualquier MD. No se hizo ese cruce formal en esta ronda — se asumió consistencia (Vado de Río Seco n=24, La Tapa n=41, Las Tapias-Río Las Tapias n=36, Piedra Blanca n=39, Las Tapias-Río San Bartolomé n=38) por uso repetido y coincidente a lo largo de toda la sesión, no por verificación contra la tabla de esa decisión. Pendiente confirmar en otro momento si hace falta.

### Etapa 1 — veredicto de punta a punta, las 5 estaciones

El pipeline completo reproduce el veredicto general de Facundo ("Habilitada para Etapa 2") en las 5 estaciones, sin excepción. Discrepancias menores, todas ya conocidas y no bloqueantes:
- Convención de partición t-Student para n impar (est_03, est_05): METIS usa `floor(n/2)`, tesis usa `ceil(n/2)` — no cambia el veredicto en ningún caso.
- k_max de Anderson (`n//3` vs `ceil(n/3)`): nunca cambia el veredicto en las 5 estaciones.
- Exclusión de empates con la media en Wald-Wolfowitz (est_03): diferencia de n, no cambia veredicto.

Sin hallazgos nuevos en Etapa 1 durante Bloque 8.

### Etapa 2 — comparación de resultado final por estación

**Aclaración de principio, aplicable a las 5 filas:** METIS no decide ni recomienda un modelo — calcula y expone el ranking completo por EEA ascendente; la elección final es del usuario experto (requerimiento del sistema, ver docstring de `es_high_eea`). Lo que se evalúa acá es si **la información numérica que el pipeline expondría** al experto coincide con la de la tesis, no si "el software elige bien".

| Estación | Selección de Facundo | ¿Fue la de menor EEA en su propia tabla? | ¿METIS coincide en parámetros/EEA de esa distribución? | Consecuencia |
|---|---|---|---|---|
| est_02 | Exponencial β (20.91) | Sí (empate técnico con LN3p MV, gana por parsimonia) | Sí — PASS exacto, cuantiles 7/7 | Sin divergencia |
| est_03 | LP3 Indirecto (22.62) | Sí | Parámetros con Causa A (g-propagación); EEA de METIS también da LP3 Indirecto como mejor, pero los **cuantiles de diseño de ese mismo modelo fallan hasta +54% en T=100** por la misma Causa A propagándose a la cola | Modelo "correcto" preservado en el ranking, pero el caudal de diseño resultante sí diverge fuerte — consecuencia práctica real pese a que la posición en el ranking no cambia |
| est_04 | LP3 Indirecto (4.14) — **no** es el de menor EEA (GVE MV=3.99 es menor) | No — la propia tesis dice explícitamente que descartó el mínimo numérico por criterio gráfico | GVE MV (el mínimo numérico) coincide exacto con METIS (0% diff, PASS) | Sin divergencia atribuible a METIS — el experto aplicó juicio propio por encima del número, tal como el sistema está diseñado para permitir |
| est_05 | Log-Normal 3p MV (5.78) | Sí, por margen estrecho sobre GVE MV (6.33) | **No** — Causa C infla el EEA de LN3p MV en METIS (8.77) lo suficiente para que GVE MV (6.33, sin cambios) pase a verse como el mejor en el ranking que METIS expondría | **Causa D** — Causa C con impacto en el ranking informado (ver clasificación abajo) |
| est_06 | Exponencial x0β MV (5.74) | Sí | Sí — PASS exacto, cuantiles 7/7 | Sin divergencia |

**Causa D (definición formal, no es causa raíz nueva):** se aplica cuando una discrepancia ya clasificada como Causa A/B/C es de magnitud suficiente para alterar el orden relativo entre distribuciones en el ranking que el pipeline expone — a diferencia de la mayoría de los casos de Causa C en esta auditoría (Gamma 2p, GVE Momentos, etc.), donde la distribución afectada nunca estuvo cerca del primer puesto y el error, aunque real, no llega a afectar la información que vería el experto en la práctica. Único caso confirmado: **est_05, Log-Normal 3p MV** (Causa C de base ya documentada en `pendientes-facundo.md`).

### Hallazgo nuevo durante Bloque 8 — no de modelo, de código

Ver actualización anterior (misma fecha) en este documento: bug de resolución de escaneo en `gamma3p.py`/MV, confirmado en est_04, acotado (no reproducido en est_02/03/05/06) — pendiente de reapertura de Fase 1, no de consulta a Facundo.

### Cierre formal

**Bloque 8: CERRADO**, con las salvedades explícitas de arriba (cruce DECISIÓN 016 no verificado formalmente; est_04 sin necesidad de investigación adicional por tratarse de override de criterio experto, no de discrepancia numérica). Resultado consolidado: sin hallazgos de cableado nuevos; un hallazgo de algoritmo/fórmula acotado a est_04 (pendiente Fase 1); un caso de Causa D (est_05) que amerita prioridad alta en la próxima consulta a Facundo, por tener consecuencia directa sobre qué modelo vería el experto como mejor ajuste numérico.

**Estado general de la auditoría de esta sesión: Fase 2 (Bloque 6, 7 y 8) — CERRADA.**

------------------------------------------------------------------------------------------------
## Actualización 14/07/2026 (corrección) — Bloque 8 NO estaba cerrado; se separa como Fase 4
------------------------------------------------------------------------------------------------

**Corrección al cierre anterior de esta misma fecha:** la actualización previa declaró "Bloque 8: CERRADO" y "Estado general de la auditoría de esta sesión: Fase 2 (Bloque 6, 7 y 8) — CERRADA". Eso fue prematuro en dos sentidos, y se corrige acá sin borrar el registro anterior (queda arriba, con su valor histórico intacto: refleja bien el análisis hecho hasta ese momento sobre 5 estaciones).

**1. Alcance incompleto.** El cierre se basó en est_02 a est_06 (5 estaciones). El repositorio real de datos de Facundo tiene est_01 a est_09 (9 estaciones) — quedan est_01, est_07, est_08 y est_09 sin analizar bajo el mismo criterio. No corresponde declarar cerrado un bloque cuyo objetivo es "verificar el comportamiento del sistema en producción" habiendo cubierto poco más de la mitad del dataset real disponible.

**2. Objetivo mal definido — se redefine acá.** El documento rector original describe el Bloque 8 como "correr el pipeline completo... y comparar contra los MDs existentes... reemplaza el PASS anterior por un PASS real de integración". Esa definición quedó corta frente a lo que realmente hace falta en esta instancia del proyecto: no es un PASS/FAIL más — es la **primera consolidación definitiva desde que empezó el desarrollo** de tres categorías, sobre el sistema corriendo de punta a punta tal como operaría en producción:
   - Qué está **aprobado y operando correctamente** (cerrado, sin acción).
   - Qué es un **pendiente de código** — bug real de METIS, para escalar a Code/sesión de fix (ejemplo ya encontrado: resolución de escaneo en `gamma3p.py`/MV).
   - Qué es un **pendiente de dominio** — para escalar a Facundo/Carlos (Causa C consolidada, Causa D, ambigüedades de fórmula sin resolver).

**Distinción real con Bloque 6/7, para que quede explícita:** no es una ejecución distinta — `ejecutar_etapa1()`+`ejecutar_etapa2()` de punta a punta es el mismo pipeline completo que ya se corrió como diagnóstico en Bloque 6/7. La diferencia es la pregunta que se le hace al mismo resultado: Bloque 6/7 pregunta por función/distribución aislada ("¿le llegó el dato correcto?"); esto pregunta por el sistema completo compitiendo consigo mismo ("¿el ranking final y la selección de modelo resultante coinciden con el de referencia, y si no, por qué, y qué hay que hacer al respecto?"). Es un nivel de análisis distinto sobre el mismo output, no una corrida nueva.

**Decisión de estructura:** dado que es una pregunta de sistema, no de cableado, este análisis deja de vivir dentro de Fase 2 (cableado) y pasa a **Fase 4 — Regresión E2E**, documento propio (`fase4-e2e-regresion.md`), que reutiliza el trabajo ya hecho para est_02-06 en las actualizaciones de arriba (nada se repite, se migra como insumo) y lo extiende a est_01/07/08/09.

**Estado real de Fase 2, corregido:** Bloque 6 y Bloque 7 (cableado de Etapa 2) — **CERRADOS**, sin cambios, ese resultado se sostiene. Bloque 8 **se retira de esta fase** — continúa en `fase4-e2e-regresion.md`, no cerrado, pendiente est_01/07/08/09.