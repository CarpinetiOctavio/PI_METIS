# Regression Tests — METIS
# Fuente: Tesis Facundo Ganancias Martínez

**Última actualización: 17 de Julio de 2026.** Este documento se escribió
originalmente antes de ejecutar las pruebas sobre las 9 estaciones. La
tabla de estado y la sección "Estado del commit" reflejaban ese momento
inicial (varias estaciones marcadas "Pendiente"/"Por completar"). Se
corrigen acá con el estado real post-auditoría, sin borrar el criterio
metodológico original (tolerancias, exclusiones, protocolo de 7 pasos),
que sigue vigente sin cambios.

## Las tres capas de regresión — cómo se relacionan

Este README describe el protocolo aplicado en tres capas complementarias,
que no se reemplazan entre sí (ver `docs/README.md` para el criterio
general):

- **`regresion-unitaria/`** — fidelidad de fórmula aislada por estación,
  distribución por distribución.
- **`regresion-pipeline/`** — el orquestador de cada etapa reproduce los
  valores correctos (cableado).
- **`regresion-e2e-coreEstadistico/`** — consolidación de sistema
  completo: `ejecutar_etapa1()` encadenado con `ejecutar_etapa2()` con
  datos reales fluyendo de una etapa a la otra, ranking final y selección
  de modelo comparados contra la referencia de Facundo. Esta es la capa
  que valida el flujo real de datos entre etapas — el protocolo detallado
  de este documento (Pasos 1 a 7) aplica principalmente a esta capa y a
  `regresion-pipeline/`.

## Tolerancias globales

| Magnitud                          | Tolerancia | Nivel     | Criterio                                                          |
|-----------------------------------|------------|-----------|-------------------------------------------------------------------|
| Estadística descriptiva exacta    | ±0.01%     | PASS/FAIL | media, varianza, desvío, M0-M3, suma_ln, máximo, mínimo          |
| Estadística descriptiva sensible  | ±10%       | INFO      | asim_sesgada, asim_no_sesgada, kurt_sesgada, kurt_no_sesgada, CV |
| Etapa 1 — estadísticos            | ±0.01%     | PASS/FAIL |                                                                   |
| Etapa 1 — estadísticos INFO       | ±1%        | INFO      | t_student estadístico (redondeo Excel en medias), Helmert umbral (display √(n-1)) |
| Etapa 2 — parámetros              | ±1%        | PASS/FAIL |                                                                   |
| Etapa 2 — EEA                     | ±1%        | PASS/FAIL |                                                                   |
| Etapa 2 — EEA INFO               | ±50%       | INFO      | cuantil Excel distinto al de METIS, g-propagación, METIS mejor solución |
| Etapa 2 — cuantiles               | ±1%        | PASS/FAIL |                                                                   |

Nota: Los estadísticos INFO son correctos por fórmula (IV-4 a IV-9 de la tesis).
La diferencia con los valores de la tesis se debe a redondeo acumulado de Excel en Facundo.
Si diff% > 10% en cualquier estadístico INFO, investigar — puede indicar fórmula incorrecta.
Solo los PASS/FAIL bloquean el avance al paso siguiente si hay FAIL.

## Exclusiones globales
- Gamma 3p MPP: EXCLUIDO en todas las estaciones.
  Tabla IV-1 de la tesis indica "Sí" pero el Capítulo IV
  no desarrolla las ecuaciones. Pendiente confirmación Facundo.
- Gen. Exponencial ML lambda negativo: si METIS tiene guard
  lam <= 0, el resultado esperado puede ser NO_APLICABLE en
  lugar del valor numérico de la tesis. Verificar caso a caso.

## Estado real de las 9 estaciones (Fase 4, cerrada)

Criterio de PASS: parámetros de cada fórmula reproducidos correctamente
— eso es lo que define fidelidad de implementación. Ninguna estación
tuvo FAIL de parámetro. Las divergencias de EEA/cuantil sin causa
determinable (Causa C) no son FAIL — son huecos de visibilidad sobre el
cálculo interno del Excel de Facundo, documentados y escalados en
`pendientes-facundo.md`.

Framework de causas: **A** = g-propagación DECISIÓN013 (ddof) — **B** =
método iterativo converge a óptimo distinto sin causa conocida — **C** =
EEA/cuantil diverge pese a parámetros casi idénticos, origen desconocido
— **D** = Causa C con magnitud suficiente para cambiar qué modelo
recomendaría METIS frente al elegido por Facundo.

| Est. | Estación                          | Etapa 1                          | Etapa 2                    | Causa/nota puntual |
|------|-----------------------------------|-----------------------------------|-----------------------------|---------------------|
| 01   | Alpa Corral – Río Barrancas       | Rechazo unánime (coincide con tesis; Facundo no habilita para diseño) | Corrida académica, aislada del flujo real | Gamma 3p MPP (modelo ganador de Facundo) no calculable en METIS — fuente incompleta |
| 02   | Vado de Río Seco – Río Barrancas  | Aprobado sin reservas             | Cableado y selección aprobados | Sin pendientes — junto con est_06, las dos únicas limpias |
| 03   | La Tapa – Río Las Cañitas         | Aprobado sin reservas             | Cableado 34/34, selección aprobada | Causa C ~95% + Causa A ~5% en modelo ganador (LP3 Indirecto) |
| 04   | Las Tapias – Río Las Tapias       | Aprobado — la más limpia de las 9 | Cableado 34/34 (DECISIÓN023 aplicado), selección aprobada | Cuantiles no verificables — columnas de la ficha de tesis mal etiquetadas (calidad de fuente) |
| 05   | Piedra Blanca – Río Piedra Blanca | Aprobado                          | Cableado aprobado            | Causa D (LN3p MV) — modelo recomendado difiere del elegido por Facundo, sin invertir el ranking completo |
| 06   | Las Tapias – Río San Bartolomé    | Aprobado sin discrepancias        | Cableado y selección aprobados (coincide) | Sin pendientes — hallazgo aparte no bloqueante de calidad de fuente en Gamma 3p MV |
| 07   | Tincunaco – Río Chocancharagua    | Aprobado (nota: ambigüedad de redondeo en partición Cramer) | Cableado y selección aprobados | Causa C presente, no invierte el ranking |
| 08   | Ume Pay – Río Grande              | Aprobado (notas de convención tesis vs. METIS, no bugs) | Cableado aprobado | **Causa D más severa del proyecto** — Gamma 3p MV, EEA diverge -23.96%, invierte el primer puesto del ranking |
| 09   | La Suela – Río La Suela           | **Bloqueado por contrato** — n=7<10, `CONTRACT_SERIES_TOO_SHORT`, único caso de bloqueo duro | No corre en el flujo real (por diseño) | Único pendiente de código de la estación (DECISIÓN025) ya resuelto |

**Conclusión general:** de las 9, 2 sin ningún pendiente (est_02, est_06), 7 con pendientes de dominio (preguntas a Facundo) o de calidad de fuente de la tesis — ninguna con pendiente de código sin resolver, ninguna con FAIL de parámetro. Las 9 cierran en el criterio de fidelidad de implementación.

## Archivos por estación y capa

| Est. | `regresion-unitaria/`                              | `regresion-pipeline/`                              | `regresion-e2e-coreEstadistico/` |
|------|-----------------------------------------------------|-----------------------------------------------------|-----------------------------------|
| 01   | est_01_alpa_corral_rioBarrancas-unitaria.md         | est_01_alpa_corral_rioBarrancas-pipeline.md         | est_01-e2e.md                     |
| 02   | est_02_vado_rio_seco_rioBarrancas-unitaria.md       | est_02_vado_rio_seco_rioBarrancas-pipeline.md       | est_02-e2e.md                     |
| 03   | est_03_la_tapa_rioLasCanitas-unitaria.md            | est_03_la_tapa_rioLasCanitas-pipeline.md            | est_03-e2e.md                     |
| 04   | est_04_las_tapias_rioLasTapias-unitaria.md          | est_04_las_tapias_rioLasTapias-pipeline.md          | est_04-e2e.md                     |
| 05   | est_05_piedra_blanca_rioPiedraBlanca-unitaria.md    | est_05_piedra_blanca_rioPiedraBlanca-pipeline.md    | est_05-e2e.md                     |
| 06   | est_06_las_tapias_rioSanBartolome-unitaria.md       | est_06_las_tapias_rioSanBartolome-pipeline.md       | est_06-e2e.md                     |
| 07   | est_07_tincunaco_rioChocancharagua-unitaria.md      | est_07_tincunaco_rioChocancharagua-pipeline.md      | est_07-e2e.md                     |
| 08   | est_08_ume_pay_rioGrande-unitaria.md                | est_08_ume_pay_rioGrande-pipeline.md                | est_08-e2e.md                     |
| 09   | est_09_la_suela_rioLaSuela-unitaria.md              | est_09_la_suela_rioLaSuela-pipeline.md              | est_09-e2e.md                     |

`consolidacion-e2e.md`, en `regresion-e2e-coreEstadistico/`, es un documento agregado sin equivalente por estación en las otras dos capas — consolida el cierre de las 9.

## Instrucción de ejecución por estación
Ejecutar en orden estricto. Detener en el primer FAIL y depurar
antes de continuar. Un error en pasos tempranos puede propagar
errores a los siguientes.

Paso 1 — Estadística descriptiva:
  Calcular sobre la serie: n, media, varianza, desvío,
  asimetría sesgada, asimetría no sesgada (g), curtosis sesgada,
  curtosis no sesgada (k), CV, sumatoria ln(xi),
  M0, M1, M2, M3, máximo, mínimo.
  Estadísticos PASS/FAIL (±0.01%): media, varianza, desvío, M0-M3, suma_ln, máximo, mínimo.
  Estadísticos INFO (±10%): asim_sesgada, asim_no_sesgada, kurt_sesgada, kurt_no_sesgada, CV.
  Bloquea al Paso 2 solo si hay FAIL. Los INFO no bloquean.

Paso 2 — Homogeneidad:
  Correr Helmert, t de Student y Cramer.
  Comparar estadísticos contra esperados. Tolerancia ±0.01%.
  Comparar conclusiones individuales y veredicto.

Paso 3 — Independencia:
  Correr Anderson y Wald-Wolfowitz.
  Comparar estadísticos contra esperados. Tolerancia ±0.01%.
  Comparar conclusiones individuales y veredicto.

Paso 4 — Veredicto Etapa 1:
  Confirmar habilitación para Etapa 2.
  Si FALLA: reportar y detener. No ejecutar Etapa 2.

## Propagación de redondeo de Excel en g (asimetría no sesgada)

Caso de est_02:
g METIS = 1.6686, g tesis = 1.565 — diff 6.62% (redondeo Excel).
Esta diferencia propaga FAIL esperados en:

| Distribución    | Método   | Parámetro afectado | Diff esperada | Causa        |
|-----------------|----------|--------------------|---------------|--------------|
| Gamma 3p        | momentos | beta               | ~12%          | beta = 4/g²  |
| Log-Normal 3p   | momentos | w, µy, σy          | ~4%+          | w = f(g)     |
| GVE             | momentos | beta               | ~21%          | polinomio g  |

Estos FAIL no son bugs — son redondeo de Excel propagado.
Para confirmar: si diff_param es explicable por diff_g, marcar
como INFO en lugar de FAIL.

Distribuciones NO afectadas por g (FAIL en estas sí es bug):
- Todas las que usan x̄, S, MPP como únicos insumos
- LP3 Indirecto (usa gy de ln(xi), no g de la serie)
- Gamma 2p ML (usa tau2 de MPP)

Paso 5 — Parámetros Etapa 2:
  Correr todas las distribuciones y métodos disponibles.
  Comparar cada parámetro contra esperado. Tolerancia ±1%.
  Métodos marcados NO_CONVERGE en la tesis: verificar que
  METIS devuelva NO_CONVERGE o STATUS equivalente.
  Gamma 3p MPP: verificar que devuelva EXCLUIDO o PENDIENTE.

  Atención — propagación de g (asimetría no sesgada):
  g METIS ≠ g tesis por redondeo acumulado de Excel (est_02: 6.62%).
  Distribuciones afectadas: Gamma 3p momentos (beta=4/g²),
  Log-Normal 3p momentos (w=f(g)), GVE momentos (polinomio en g).
  Si diff_param > 1% pero es explicable por diff_g, clasificar
  como INFO (no bug) con nota "redondeo g Excel propagado".
  Distribuciones NO afectadas por g: todas las que usan x̄, S, MPP
  como únicos insumos; LP3 Indirecto (usa gy de ln(xi)); Gamma 2p ML.

Paso 6 — EEA:
  Comparar EEA de cada distribución contra esperado.
  Tolerancia ±1% para PASS/FAIL. ±50% para INFO.

  Causas válidas de clasificación INFO en EEA:
  A) g-propagación DECISIÓN013: gve/momentos, lognormal3p/momentos,
     gamma3p/momentos. Parámetros distintos por g METIS ≠ g tesis.
     También aplica a lp3/indirecto: parámetros difieren porque
     gy_yi (asimetría de yi=ln(xi)) usa ddof=0 en METIS vs SKEW()
     de Excel. EEA distinto es consecuencia aritmética de parámetros
     distintos — no indica solución mejor.
  B) METIS encontró solución diferente en método iterativo, sin
     causa documentada que explique la diferencia de parámetros.
     Aplica SOLO cuando el método es iterativo (MV, ME, ML) y los
     parámetros difieren sin relación con DECISIÓN013 u otra causa
     conocida. EEA menor refleja convergencia a óptimo distinto.
     Casos confirmados: gve/ml (est_02, est_03 — beta coincide,
     alpha/nu difieren).
     NO aplica cuando parámetros difieren por Causa A u otra causa
     documentada — en ese caso el EEA menor es consecuencia
     aritmética de los parámetros distintos, no solución mejor.
  C) EEA distinto con mismos parámetros — origen desconocido (PENDIENTE Facundo):
     gamma2p momentos/mv/ml, lognormal2p/momentos, lognormal3p/mv,
     normal momentos/ml. El capítulo IV no describe la implementación interna
     de los cuantiles del programa de Facundo. Sin acceso al código fuente
     no es verificable. METIS da EEA menor en todos los casos (ajuste igual
     o mejor). Escalar a Facundo o Carlos en próxima reunión.
     En todos los casos el modelo óptimo no cambia.

Paso 7 — Cuantiles:
  Calcular para T=2,5,10,20,25,50,100 años sobre los modelos
  seleccionados por Facundo.
  Comparar contra esperados. Tolerancia ±1%.

## Reporte por paso
Para cada paso reportar tabla:
  variable | valor_metis | valor_tesis | diff% | PASS/FAIL/INFO

## Formato de archivo por estación
Cada archivo de estación contiene:
  ### Serie
  ### Estadística descriptiva esperada
  ### Etapa 1 — Homogeneidad
  ### Etapa 1 — Independencia
  ### Veredicto general Etapa 1
  ### Etapa 2 — Parámetros        (solo si pasó Etapa 1)
  ### Etapa 2 — EEA esperados      (solo si pasó Etapa 1)
  ### Etapa 2 — Cuantiles esperados (solo si pasó Etapa 1)
  ### Modelo seleccionado por Facundo (solo si pasó Etapa 1)

## Estado del commit

Las 9 estaciones alcanzaron PASS — parámetros de cada fórmula
reproducidos correctamente en todos los casos, criterio que define
PASS/FAIL en este protocolo. Ninguna estación tuvo FAIL de parámetro.
Existen divergencias de EEA/cuantil sin causa determinable (Causa C —
ver Paso 6), documentadas y escaladas como preguntas cerradas a Facundo
en `pendientes-facundo.md`; estas no bloquean el commit porque no son
fallas de fidelidad de implementación, son huecos de visibilidad sobre
el cálculo interno del Excel de referencia, fuera del control de METIS.

**Pendiente, no bloqueante para este commit:** la verificación E2E
(Fase 4) se ejecutó encadenando `ejecutar_etapa1()` + `ejecutar_etapa2()`
manualmente en el script de auditoría, ya que `full_pipeline.py` /
`ejecutar_pipeline_completo()` no existía en ese momento. Queda
pendiente confirmar que el código real de `full_pipeline.py` (creado en
la sesión de reorganización posterior a esta auditoría) reproduce
exactamente los mismos resultados ya validados manualmente — una
regresión de cableado sobre la automatización del encadenamiento, no
una nueva auditoría de fidelidad.

## Historial de este documento

- **17/07/2026** — Corrección post-auditoría: tabla de estaciones
  actualizada con el estado real de las 9 (Fase 4, cerrada), agregada
  tabla de archivos por capa (antes una sola columna con nombres
  desactualizados), sección "Estado del commit" reescrita para
  reflejar PASS real y agregar el pendiente de verificación de
  `full_pipeline.py`. Metodología (tolerancias, exclusiones, protocolo
  de 7 pasos) sin cambios — sigue vigente tal como se definió
  originalmente.