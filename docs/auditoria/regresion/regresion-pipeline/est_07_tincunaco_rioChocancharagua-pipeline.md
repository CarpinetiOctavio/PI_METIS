## Estación 7 — Tincunaco – Río Chocancharagua

### Serie (Sheet 1)
serie = [
    77.7,   # 61-62
    42.3,   # 62-63
    53.5,   # 63-64
    51.2,   # 64-65
    85.5,   # 65-66
    102.0,  # 66-67
    22.4,   # 67-68
    39.3,   # 68-69
    21.8,   # 69-70
    27.0,   # 70-71
    32.9,   # 71-72
    61.9,   # 72-73
    36.8,   # 73-74
    60.3,   # 74-75
    11.8,   # 75-76
    46.4,   # 76-77
    69.8,   # 77-78
    120.0,  # 78-79
    38.6,   # 79-80
]

### Estadística descriptiva esperada (Sheet 1)
| Variable                        | Valor esperado |
|---------------------------------|----------------|
| n                                | 19             |
| Media [m³/s]                    | 52.695         |
| Varianza [m³/s]²                | 804.199        |
| Desvío [m³/s]                   | 28.358         |
| Asimetría Sesgada               | 0.741          |
| Asimetría No Sesgada (g)        | 0.874          |
| Curtosis Sesgada                | 2.715          |
| Curtosis No Sesgada (k)         | 3.804          |
| Coeficiente de Variación (CV)   | 0.538          |
| Sumatoria ln(xi)                | 72.56          |
| beta_0 = M0                     | 52.695         |
| beta_1 = M1                     | 34.384         |
| beta_2 = M2                     | 26.139         |
| beta_3 = M3                     | 21.337         |
| Máximo [m³/s]                   | 120.0          |
| Mínimo [m³/s]                   | 11.8           |

---

### Etapa 1 — Homogeneidad (Sheet 2)

#### Helmert
| Parámetro              | Valor esperado |
|------------------------|----------------|
| N° de Series (S)       | 7              |
| N° de Cambios (C)      | 11             |
| Estadístico (S-C)      | -4             |
| n                      | 19             |
| Umbral inferior        | -4.24          |
| Umbral superior        | 4.24           |
| Conclusión individual  | El estadístico (S - C) está comprendido entre -(nj-1)^0,5 y +(nj-1)^0,5. Por lo tanto la serie es Homogénea. |

#### t de Student
| Parámetro              | Valor esperado |
|------------------------|----------------|
| Estadístico t          | -0.06          |
| Grados de libertad     | 17             |
| Valor crítico (tabla)  | 2.1098         |
| Conclusión individual  | El valor absoluto del estadístico t es menor que el valor de tabla de t para 17 grados de libertad (G.L.) y para un nivel de significancia: α = 5%. Por lo tanto la serie es Homogénea. |

#### Cramer
| Parámetro              | Valor esperado |
|------------------------|----------------|
| tau subgrupo 1         | -0.16779       |
| tau subgrupo 2         | 0.18061        |
| t calculado sg. 1      | 0.82742        |
| t calculado sg. 2      | 0.50977        |
| Valor crítico (tabla)  | 2.1098         |
| Conclusión individual  | Solo el valor absoluto de ambos t_w es menor que el valor de tabla de t para 17 G.L. y para α = 5%. La serie es Homogénea. |

**Veredicto homogeneidad:** Serie Homogénea
**Conclusión:** Aceptación unánime de la hipótesis de homogeneidad en las tres pruebas estadísticas con alpha = 5% para sus 17 G.L. Todos los estadísticos calculados se mantuvieron holgadamente dentro de los rangos y límites críticos (Helmert = -4 y t = -0,06). La serie cuenta con consistencia numérica perfecta y queda habilitada para la Etapa 2.

---

### Etapa 1 — Independencia (Sheet 2)

#### Anderson
| Parámetro                              | Valor esperado |
|----------------------------------------|----------------|
| n                                      | 19             |
| k = n/3                                | 6.3            |
| k adoptado                             | 7              |
| Media                                  | 52.69          |
| N° máximo puntos fuera de bandas       | 0,7 (se redondea a 1) |
| N° puntos fuera de bandas              | 0              |
| Conclusión individual                  | Aceptada (0 puntos fuera cumple idealmente con el límite admisible de 0,7). Se acepta la hipótesis de que las variables de la serie son Independientes. |

#### Wald-Wolfowitz
| Parámetro                    | Valor esperado |
|------------------------------|----------------|
| n                            | 19             |
| n1                           | 8              |
| n2                           | 11             |
| R (rachas observadas)        | 12             |
| Media teórica de R           | 10.26          |
| Varianza teórica de R        | 4.25           |
| Estadístico Z                | 0.84           |
| Valor crítico α=0.05         | ± 1.96         |
| Valor crítico α=0.01         | No establecido |
| Conclusión individual        | Aceptada (El estadístico Z = 0,84 se encuentra de forma segura dentro de los límites críticos de tabla). La serie se concluye como independiente. |

**Veredicto independencia:** Serie Independiente
**Conclusión:** Aceptación unánime de la hipótesis de independencia. La prueba de Anderson valida la estructura aleatoria con 0 puntos fuera de las bandas de aceptación. Asimismo, el test de Wald-Wolfowitz confirma la aleatoriedad de la serie con un estadístico Z = 0,84 plenamente contenido en los límites críticos para alpha = 5%. Al registrar un comportamiento óptimo y favorable tanto en homogeneidad (por unanimidad) como en independencia, la serie queda completamente aprobada para la Etapa 2.

**Veredicto general Etapa 1:** Habilitada para Etapa 2

---

### Etapa 2 — Parámetros (Sheet 3)

**CORREGIDO.** La versión previa de esta tabla estaba contaminada con los parámetros reales de Est 08 (Ume Pay) — error de la fuente detectado por verificación cruzada. Se releyó el Excel de Tincunaco y se verificó matemáticamente: Normal por Momentos/MV reproduce mu=52.69≈media real (52.695) y sigma=28.3584≈desvío real (28.358); Uniforme por Momentos reproduce media=52.695 y varianza≈804.09≈varianza real (804.199). Confirmado: estos son los parámetros genuinos de Tincunaco.

| Distribución              | Método                    | Parámetro 1        | Parámetro 2          | Parámetro 3          |
|---------------------------|---------------------------|--------------------|----------------------|----------------------|
| Uniforme                  | Momentos                  | alfa = 3.58        | beta = 101.81        |                      |
| Uniforme                  | Máxima Verosimilitud      | alfa = 11.8        | beta = 120.0         |                      |
| Exponencial beta          | Momentos y M. Verosimilitud | beta = 0.019     |                      |                      |
| Exponencial x0 y beta     | Momentos                  | x0 = 24.34         | beta = 28.36         |                      |
| Exponencial x0 y beta     | Máxima Verosimilitud      | x0 = 9.53          | beta = 43.17         |                      |
| Generalizada Exponencial  | Momentos                  | alfa = 2.69        | lambda = -0.125      |                      |
| Generalizada Exponencial  | Máxima Verosimilitud      | alfa = 4.39        | lambda = 0.041       |                      |
| Generalizada Exponencial  | Momentos L                | alfa = 0.76        | lambda = -0.0095     |                      |
| Normal                    | Momentos L                | mu = 52.69         | sigma = 28.4826      |                      |
| Normal                    | Momentos y M. Verosimilitud | mu = 52.69       | sigma = 28.3584      |                      |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | mu_y = 3.82      | sigma_y = 0.578      |                      |
| Log Normal (3 parámetros) | Momentos                  | x0 = -42.79        | mu_y = 4.5663        | sigma_y = 0.2782     |
| Log Normal (3 parámetros) | Máxima Verosimilitud      | x0 = -13.71        | mu_y = 4.111         | sigma_y = 0.415      |
| Gamma (2 parámetros)      | Momentos                  | alfa = 15.26       | beta = 3.453         |                      |
| Gamma (2 parámetros)      | Máxima Verosimilitud      | alfa = 14.66       | beta = 3.594         |                      |
| Gamma (2 parámetros)      | Momentos L                | alfa = 16.67       | beta = 3.162         |                      |
| Gamma (3 parámetros)      | Momentos                  | x0 = -12.218       | alfa = 12.389        | beta = 5.24          |
| Gamma (3 parámetros)      | Máxima Verosimilitud      | x0 = 4.408         | alfa = 16.825        | beta = 2.87          |
| Gamma (3 parámetros)      | Momento Prob. Pesada      | x0 = 2.682         | alfa = 18.8          | beta = 2.66          | ← PENDIENTE: fórmula MPP ausente en Cap. IV |
| Gumbel                    | Momentos                  | alfa = 22.12       | mu = 39.933          |                      |
| Gumbel                    | Máxima Verosimilitud      | alfa = 21.451      | mu = 40.052          |                      |
| Gumbel                    | Momentos L                | alfa = 23.189      | mu = 39.309          |                      |
| Gumbel                    | Máxima Entropía           | alfa = 21.717      | mu = 40.16           |                      |
| GVE (Valores Extremos)    | Momentos                  | alfa = 20.487      | beta = -0.215        | nu = 45.035          |
| GVE (Valores Extremos)    | Máxima Verosimilitud      | alfa = 21.192      | beta = -0.032        | nu = 39.69           |
| GVE (Valores Extremos)    | Momentos L                | alfa = 24.63       | beta = -0.047        | nu = 91.307          |
| Log Pearson tipo III      | Momentos Método Directo   | alfa = 0.359       | beta = 0.158         | y0 = 3.884           |
| Log Pearson tipo III      | Momentos Método Indirecto | alfa = 0.135       | beta = 18.404        | y0 = 1.339           |
| Log Pearson tipo III      | Máxima Verosimilitud      | alfa = 0.677       | beta = 2.121         | y0 = 2.382           |

**Nota — CAMBIO DE ANOMALÍAS respecto a la versión previa (errónea):** con los valores correctos, **ya no hay ningún NO_CONVERGE en Etapa 2 de Tincunaco** — ni en GVE Momentos ni en Log Pearson III Máxima Verosimilitud (esos NO_CONVERGE pertenecían en realidad a Ume Pay). Los tres métodos de GVE y los tres de Log Pearson III convergieron con valores numéricos en Tincunaco.

---

### Etapa 2 — EEA esperados (Sheet 3)
| Distribución              | Método                    | EEA [m³/s] |
|---------------------------|---------------------------|------------|
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | 3.9748   |
| Gumbel                    | Momentos L                | 4.3188     |
| Log Pearson tipo III      | Momentos Método Indirecto | 4.414      |
| Generalizada Exponencial  | Máxima Verosimilitud      | 4.5495     |
| Gamma (3 parámetros)      | Momento de Probabilidad Pesada | 4.7393 |
| Gamma (2 parámetros)      | Momentos L                | 5.154      |
| Gumbel                    | Momentos                  | 5.2438     |
| Gumbel                    | Máxima Entropía           | 5.621      |
| GVE (Valores Extremos)    | Máxima Verosimilitud      | 5.6755     |
| Gumbel                    | Máxima Verosimilitud      | 5.9393     |
| Gamma (2 parámetros)      | Momentos                  | 5.9656     |
| Gamma (3 parámetros)      | Máxima Verosimilitud      | 6.107      |
| Gamma (3 parámetros)      | Momentos                  | 6.1764     |
| Gamma (2 parámetros)      | Máxima Verosimilitud      | 6.3467     |
| Log Normal (3 parámetros) | Máxima Verosimilitud      | 6.3517     |
| Log Normal (3 parámetros) | Momentos                  | 6.3714     |
| Exponencial x0 y beta     | Momentos                  | 6.8458     |
| Normal                    | Momentos                  | 7.7741     |
| Normal                    | Momentos L                | 7.8195     |
| Exponencial x0 y beta     | Máxima Verosimilitud      | 8.485      |
| Uniforme                  | Momentos                  | 8.4927     |
| Exponencial beta          | Momentos y M. Verosimilitud | 15.3565  |
| Uniforme                  | Máxima Verosimilitud      | 16.6835    |
| Log Pearson tipo III      | Momentos Método Directo   | 26.4022    |
| GVE (Valores Extremos)    | Momentos L                | 57.0234    |
| GVE (Valores Extremos)    | Momentos                  | 61.2567    |
| Log Pearson tipo III      | Máxima Verosimilitud      | 77.2356    |

---

### Etapa 2 — Cuantiles esperados (Sheet 3)
| T [años] | Log Normal 2 parámetros (Momentos y M. Verosimilitud) [m³/s] | Gumbel (Momentos L) [m³/s] |
|----------|----------------------------------------------------------------|------------------------------|
| 2        | 45.56                                                           | 47.81                        |
| 5        | 73.56                                                           | 74.09                        |
| 10       | 93.35                                                           | 91.49                        |
| 20       | 111.99                                                          | 108.19                       |
| 25       | 117.66                                                          | 113.48                       |
| 50       | 133.93                                                          | 129.79                       |
| 100      | 147.89                                                          | 145.98                       |

### Modelo seleccionado por Facundo
Modelo Log Normal de 2 parámetros (Momentos y Máxima Verosimilitud) Seleccionado. Para la serie de caudales máximos anuales de la estación Tincunaco en el Río Chocancharagua, la distribución Log Normal de 2 parámetros arrojó el mejor ajuste estadístico con un EEA de 3,9748 m³/s. La evaluación visual de las curvas de ajuste (Figura VIII-7) convalidó este resultado frente al modelo Gumbel por Momentos L (EEA = 4,3188 m³/s). En consecuencia, se adopta la ley Log Normal 2p como base de diseño. Los caudales máximos calculados se proyectan desde los 45,56 m³/s para eventos bianuales ordinarios hasta alcanzar los 147,89 m³/s ante una recurrencia extrema de 100 años.
---

## Resultados de Regresión METIS --> PIPELINE COMPLETO (ejecución en vivo, 2026-07-14)

**Qué es esto:** salida real de correr `ejecutar_etapa1()` seguido de
`ejecutar_etapa2()` — el pipeline completo tal como orquesta
`pipeline.py`/`pipeline2.py` hoy — sobre la serie cruda de esta estación
(sin filtrar ni preprocesar más que el descarte de valores S/D si aplica).
A diferencia de la sección "UNITARIAS" de arriba (que corre cada
prueba/distribución de forma aislada), esto pasa por el orquestador completo
de punta a punta. Se verificó que ambos caminos coinciden bit a bit para esta
estación (ej. gamma2p/momentos EEA idéntico en ambos), consistente con el resto
de la auditoría de cableado.

**Corrección de trazabilidad:** la tabla "Etapa 2 — Parámetros (Sheet 3)" de la
ficha de Facundo, arriba en este mismo archivo, estaba contaminada con los
parámetros reales de est_08 (Ume Pay) — ya corregida en esta sesión (ver nota
"CORREGIDO" en esa sección). Esta corrida en vivo usa la serie genuina de
Tincunaco (n=19) en todo momento — nunca estuvo afectada por la contaminación,
que solo vivía en la tabla de referencia de la tesis, no en el código.

**Contexto — auditoría de cableado (Fase 2, Bloque 6/7):** esta corrida es
un diagnóstico dentro de esa auditoría, no una prueba de cierre. **No
constituye ni forma parte del Bloque 8.** El único propósito acá es tener un
mapa mental actualizado de cómo está operando el pipeline completo — no se
investigan causas más allá de lo ya señalado en la sección UNITARIAS de arriba.

Invocación exacta:
```python
r1 = ejecutar_etapa1(
    serie=serie,  # lista cruda (valores S/D ya descartados si aplica)
    tipo_variable="caudal_precipitacion",
    resolucion_temporal="anual",
    timestamps=None,
    cramer_particion="default",
)
r2 = ejecutar_etapa2(np.array(serie), tiene_ceros=False)
```

### Estadística descriptiva (pipeline completo — Sheet 1)
| Variable | Valor |
|----------|-------|
| n | 19 |
| Media [m³/s] | 52.69473684210526 |
| Mediana [m³/s] | 46.4 |
| Varianza (no sesgada) [m³/s]² | 804.1994152046783 |
| Varianza (sesgada) [m³/s]² | 761.8731301939057 |
| Desvío [m³/s] | 28.358409955508407 |
| Asimetría Sesgada | 0.8031914593601893 |
| Asimetría No Sesgada (g) | 0.9475559373497658 |
| Curtosis Sesgada | 3.0252637054222733 |
| Curtosis No Sesgada (k) | 4.238211551366702 |
| Coeficiente de Variación (CV) | 0.5381639923638232 |
| Sumatoria ln(xi) | 72.56018483823071 |
| beta_0 = M0 | 52.69473684210526 |
| beta_1 = M1 | 34.38421052631578 |
| beta_2 = M2 | 26.138527691778464 |
| beta_3 = M3 | 21.33656475748194 |
| Máximo [m³/s] | 120.0 |
| Mínimo [m³/s] | 11.8 |
| Rango [m³/s] | 108.2 |

### Etapa 1 — Homogeneidad (pipeline completo — Sheet 2)

#### Helmert
| Parámetro | Valor |
|-----------|-------|
| Estadístico (S-C) | -4.0 |
| Valor crítico (± lim) | 4.242640687119285 |
| Veredicto | aprobada |
| Warning | None |

#### t de Student
| Parámetro | Valor |
|-----------|-------|
| Estadístico t | 0.3205850327055102 |
| n1 | 9 |
| n2 | 10 |
| Valor crítico (tabla) | 2.1098155778331806 |
| Veredicto | aprobada |

#### Cramer
| Parámetro | Valor |
|-----------|-------|
| Estadístico (max t_w) | 1.077871120271344 |
| n_w1 | 12 |
| n_w2 | 6 |
| Valor crítico (tabla) | 2.1098155778331806 |
| Veredicto | aprobada |
| Warning | None |

**Veredicto homogeneidad (pipeline):** homogeneidad_ok

### Etapa 1 — Independencia (pipeline completo — Sheet 2)

#### Anderson
| Parámetro | Valor |
|-----------|-------|
| Estadístico (máx r_k) | -0.2797165303292708 |
| Valor crítico | 0.39339658503695013 |
| Veredicto | aprobada |

#### Wald-Wolfowitz
| Parámetro | Valor |
|-----------|-------|
| Estadístico Z | 0.8422558426384459 |
| Valor crítico (α=0.05) | ± 1.959963984540054 |
| Veredicto | aprobada |
| Warning | TEST_WARNING_SMALL_SAMPLE |

**Veredicto independencia (pipeline):** independiente

### Etapa 1 — Tendencia y Atípicos (pipeline completo) — sin ficha de Facundo de referencia
Mann-Kendall, Kolmogorov-Smirnov y Chow no están en la tesis de Facundo (los
agregó Carlos) — no hay valor "esperado" ni "METIS unitario" previo contra el
cual comparar estas tres filas.

#### Mann-Kendall
| Parámetro | Valor |
|-----------|-------|
| Estadístico | -0.20991342856239587 |
| Valor crítico | 1.959963984540054 |
| Veredicto | aprobada |
| Warning | TEST_WARNING_SMALL_SAMPLE |

#### Kolmogorov-Smirnov (tendencia)
| Parámetro | Valor |
|-----------|-------|
| Estadístico (Z tipificado) | 0.604563541758343 |
| Valor crítico | 1.358 |
| Veredicto | aprobada |
| Warning | None |

#### Chow
| Parámetro | Valor |
|-----------|-------|
| Estadístico (máx Z_i) | 2.336734656410077 |
| Valor crítico (K_N) | 2.5311928033065323 |
| Veredicto | aprobada |

**Veredicto general Etapa 1 (pipeline):** nivel_confianza=`con_warnings` — warnings: CONTRACT_LENGTH_WARNING, TEST_WARNING_SMALL_SAMPLE

### Etapa 2 — Parámetros, EEA y Estado (pipeline completo — Sheet 3)
| Distribución | Método | Parámetro 1 | Parámetro 2 | Parámetro 3 | EEA [m³/s] | Status |
|---|---|---|---|---|---|---|
| Uniforme | Momentos | alfa = 3.5765 | beta = 101.8129 |  | 8.4927 | ok |
| Uniforme | Máxima Verosimilitud | alfa = 11.8000 | beta = 120.0000 |  | 16.6835 | ok |
| Exponencial beta | Momentos | beta = 0.018977 |  |  | 15.3565 | ok |
| Exponencial beta | Máxima Verosimilitud | beta = 0.018977 |  |  | 15.3565 | ok |
| Exponencial x0 y beta | Momentos | x0 = 24.3363 | beta = 28.3584 |  | 6.8458 | ok |
| Exponencial x0 y beta | Máxima Verosimilitud | x0 = 9.5281 | beta = 43.1667 |  | 8.4850 | ok |
| Generalizada Exponencial | Momentos | alfa = 4.7776 | lambda = 0.04255 |  | 5.2437 | ok |
| Generalizada Exponencial | Máxima Verosimilitud | alfa = 4.3923 | lambda = 0.041012 |  | 4.5495 | ok |
| Generalizada Exponencial | Momentos L | alfa = 0.442646 | lambda = -0.011306 |  | 131.0245 | ok |
| Normal | Momentos | mu = 52.6947 | sigma = 28.3584 |  | 7.3730 | ok |
| Normal | Máxima Verosimilitud | mu = 52.6947 | sigma = 28.3584 |  | 7.3730 | ok |
| Normal | Momentos L | mu = 52.6947 | sigma = 28.4826 |  | 7.3363 | ok |
| Log Normal (2 parámetros) | Momentos | mu_y = 3.8190 | sigma_y = 0.578096 |  | 2.9653 | ok |
| Log Normal (2 parámetros) | Máxima Verosimilitud | mu_y = 3.8190 | sigma_y = 0.578096 |  | 2.9653 | ok |
| Log Normal (3 parámetros) | Momentos | x0 = -39.8965 | mu_y = 4.4834 | sigma_y = 0.299436 | 5.3395 | ok |
| Log Normal (3 parámetros) | Máxima Verosimilitud | x0 = -13.7086 | mu_y = 4.1110 | sigma_y = 0.414954 | 5.2059 | ok |
| Gamma (2 parámetros) | Momentos | alfa = 15.2615 | beta = 3.4528 |  | 4.9214 | ok |
| Gamma (2 parámetros) | Máxima Verosimilitud | alfa = 14.6605 | beta = 3.5943 |  | 5.3216 | ok |
| Gamma (2 parámetros) | Momentos L | alfa = 16.6652 | beta = 3.1620 |  | 4.0824 | ok |
| Gamma (3 parámetros) | Momentos | x0 = -7.1612 | alfa = 13.4356 | beta = 4.4550 | 5.1136 | ok |
| Gamma (3 parámetros) | Máxima Verosimilitud | x0 = 4.4082 | alfa = 16.8245 | beta = 2.8700 | 5.0036 | ok |
| Gumbel | Momentos | mu = 39.9335 | alfa = 22.1196 |  | 5.2438 | ok |
| Gumbel | Máxima Verosimilitud | mu = 40.0519 | alfa = 21.4510 |  | 5.9393 | ok |
| Gumbel | Momentos L | mu = 39.3094 | alfa = 23.1894 |  | 4.3188 | ok |
| Gumbel | Máxima Entropía | mu = 40.1596 | alfa = 21.7165 |  | 5.6210 | ok |
| GVE (Valores Extremos) | Momentos | nu = 4,325.0696 | alfa = 21.8125 | beta = -0.010242 | 4,668.2873 | ok |
| GVE (Valores Extremos) | Máxima Verosimilitud | nu = 39.6898 | alfa = 21.1922 | beta = -0.031656 | 5.6755 | ok |
| GVE (Valores Extremos) | Momentos L | nu = 38.8249 | alfa = 22.1606 | beta = -0.047059 | 4.3940 | ok |
| Log Pearson tipo III | Momentos Método Directo |  |  |  | — | no_aplicable |
| Log Pearson tipo III | Momentos Método Indirecto | alfa = 0.14614 | beta = 15.6482 | y0 = 1.5321 | 4.4182 | ok |
| Log Pearson tipo III | Máxima Verosimilitud |  |  |  | — | no_converge |
| Generalizada de Pareto | Momentos | mu = 16.9796 | sigma = 46.1820 | epsilon = 0.293067 | 38.5187 | ok |
| Generalizada de Pareto | Máxima Verosimilitud |  |  |  | — | no_converge |
| Generalizada de Pareto | Mínimos Cuadrados | mu = 11.7998 | sigma = 51.1305 | epsilon = 0.268587 | 41.3733 | ok |
| Generalizada de Pareto | Momento Prob. Pesada | mu = -19.8439 | sigma = 774.0210 | epsilon = 5.4603 | 450,462,930.0923 | ok |

### Notas de cableado — Bloque 6/7 (solo señalamiento)

**¿Ceros en la serie?** No — mínimo observado = 11.8. `tiene_ceros=False`. La rama `STATUS_DISABLED_ZEROS` sigue sin ejercitarse en ninguna de las estaciones auditadas hasta ahora.

**Cambios de status vs. est_02** (comparando categoría, no valor numérico):
- `logpearson3/mv`: est_02=`ok` -> est_07=`no_converge`
- Mismo patrón ya visto en est_03/est_05/est_04 para este método.

**GVE / MV — rama de inicialización:**
- MOMENTOS descartado (guard IV-202 falla, nu0=4325.0696, alpha0=21.8125, beta0=-0.0102) -> fallback a ML
