# Regression Tests — METIS
# Fuente: Tesis Facundo Ganancias Martínez

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

## Estaciones
| Archivo                              | Estación                         | Etapa 1 | Etapa 2 | Estado    |
|--------------------------------------|----------------------------------|---------|---------|-----------|
| est_01_xxx.md                        | Por completar                    | FALLA   | N/A     | Pendiente |
| est_02_vado_rio_seco_rioBarrancas.md | Vado de Río Seco – Río Barrancas | PASA    | PASA    | PASS      |
| est_03 a est_09                      | Por completar                    | —       | —       | Pendiente |

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
  B) METIS encontró mejor solución (EEA METIS < EEA tesis):
     lp3/indirecto, lp3/mv, gve/ml.
  C) Cuantil Excel distinto al de METIS (mismos parámetros, EEA distinto):
     gamma2p momentos/mv/ml, lognormal2p/momentos, lognormal3p/mv,
     normal momentos/ml. Facundo usó aproximación numérica distinta
     en Excel para calcular los cuantiles en el EEA. METIS da EEA menor.
     En todos los casos el modelo óptimo (Exp_beta EEA=20.91) no cambia.

Paso 7 — Cuantiles:
  Calcular para T=2,5,10,20,25,50,100 años sobre los modelos
  seleccionados por Facundo.
  Comparar contra esperados. Tolerancia ±1%.

## Reporte por paso
Para cada paso reportar tabla:
  variable | valor_metis | valor_tesis | diff% | PASS/FAIL/INFO

## Formato de archivo por estación
Cada est_XX.md contiene:
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
NO commitear feature/core-etapa2 hasta que todas las estaciones
disponibles estén en estado PASS en todos los pasos.