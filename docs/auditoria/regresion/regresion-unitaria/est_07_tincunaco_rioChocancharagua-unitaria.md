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

## Resultados de Regresión METIS --> UNITARIAS

### Estado general: PASS con 2 anomalías nuevas señaladas (t-Student/Cramer en PASO 2, LP3 MV en PASO 5/6) — FAIL=0

### PASO 1 — Estadística descriptiva: PASS
| Variable                      | METIS        | Tesis        | diff%   | Nivel |
|-------------------------------|--------------|--------------|---------|-------|
| n                             | 19           | 19           | 0.000%  | PASS  |
| Media                         | 52.695       | 52.695       | -0.000%  | PASS  |
| Varianza                      | 804.199      | 804.199      | 0.000%  | PASS  |
| Desvío                        | 28.358       | 28.358       | 0.001%  | PASS  |
| M0                            | 52.695       | 52.695       | -0.000%  | PASS  |
| M1                            | 34.384       | 34.384       | 0.001%  | PASS  |
| M2                            | 26.139       | 26.139       | -0.002%  | PASS  |
| M3                            | 21.337       | 21.337       | -0.002%  | PASS  |
| Sumatoria ln(xi)              | 72.560       | 72.56        | 0.000%  | PASS  |
| Máximo                        | 120.0        | 120.0        | 0.000%  | PASS  |
| Mínimo                        | 11.8         | 11.8         | 0.000%  | PASS  |
| Asimetría sesgada             | 0.8032       | 0.741        | 8.39%   | INFO  |
| Asimetría no sesgada (g)      | 0.9476       | 0.874        | 8.42%   | INFO  |
| Curtosis sesgada              | 3.0253       | 2.715        | 11.43%   | INFO  |
| Curtosis no sesgada           | 4.2382       | 3.804        | 11.41%   | INFO  |
| CV                            | 0.5382       | 0.538        | 0.03%   | INFO  |

Nota g/k: METIS sigue IV-4/IV-5/IV-6/IV-7 (ddof=0). Excel usa SKEW()/KURT() (ddof=1). Diferencia trazable — ver DECISIÓN013. Mismo patrón que las 6 estaciones previas.

### PASO 2 — Homogeneidad: PASS con ANOMALÍA en estadísticos (ver nota)
| Prueba     | Estadístico METIS | Estadístico Tesis | diff%   | Veredicto | Nivel |
|------------|--------------------|--------------------|---------|-----------|-------|
| Helmert S-C| -4                 | -4                 | 0.000%  | Aprobada  | PASS  |
| t-Student  | 0.3206             | -0.06              | — (signo y magnitud distintos) | Aprobada  | INFO  |
| Cramer (t_w1, n_w1=12) | 1.0779 (nota: METIS reporta max(t_w1,t_w2)) | 0.82742 (t_w1 tesis) | — | Aprobada  | INFO  |
| Veredicto  | homogeneidad_ok    | Serie Homogénea    | —       | —         | PASS  |

**Nota — ANOMALÍA no vista en est_02 a est_06:** el estadístico t de Student (partición mitad/mitad, n1=9/n2=10, GL=17 — coincide con el GL=17 de la tesis) da t=0.3206 en METIS contra t=-0.06 en la tesis: no es una diferencia de redondeo, es un cambio de signo y de magnitud (factor ~5x). Reconstruido a mano fuera del código (media s1=55.078, media s2=50.55, Sp²=944.87, t=(x̄1-x̄2)/(Sp·√(1/n1+1/n2))=0.3206) — la fórmula III-8 aplicada literalmente a la partición cronológica mitad/mitad de la serie reproduce el 0.3206 de METIS, no el -0.06 de la tesis. El valor crítico sí coincide exacto (2.1098 en ambos). Cramer también difiere en magnitud del t_w1 de la tesis (1.078 vs 0.827, ~30%), aunque ambos aprueban por debajo del crítico. No se investigó la causa — podría ser una partición distinta a mitad/mitad usada por Facundo, o redondeo acumulado del Excel en las medias de submuestra a esta escala de n=19. Veredicto final (aprobada/Homogénea) coincide en ambos casos pese a la discrepancia numérica.

### PASO 3 — Independencia: PASS
| Prueba          | Estadístico METIS | Estadístico Tesis | diff%  | Veredicto | Nivel |
|-----------------|--------------------|--------------------|--------|-----------|-------|
| Anderson (k_max=7) | -0.2797 (máx |r_k|, dentro de bandas) | 0 puntos fuera | — | Aprobada  | PASS  |
| Wald-Wolfowitz Z| 0.8423             | 0.84               | 0.27% | Aprobada  | PASS  |
| Veredicto       | independiente      | independiente      | —      | —         | PASS  |

### PASO 4 — Veredicto Etapa 1: PASS
Habilitada para Etapa 2. Homogeneidad OK (veredicto coincide con tesis pese a la anomalía numérica de PASO 2). Independencia OK.

### PASO 5 — Parámetros Etapa 2: PASS (FAIL=0)
| Distribución              | Método            | diff% (por parámetro)                          | Nivel  | Causa |
|----------------------------|-------------------|--------------------------------------------------|--------|-------|
| Uniforme                  | Momentos          | alpha=-0.10%, beta=0.00%                          | PASS   | —     |
| Uniforme                  | MV                | alpha=0.00%, beta=0.00%                           | PASS   | —     |
| Exponencial beta          | Momentos/MV       | beta=-0.12%                                       | PASS   | —     |
| Exponencial x0beta        | Momentos          | x0=-0.02%, beta=-0.01%                            | PASS   | —     |
| Exponencial x0beta        | MV                | x0=-0.02%, beta=-0.01%                            | PASS   | —     |
| Gen. Exponencial          | Momentos          | alpha=+77.60%, lambda=+134.04%                    | INFO   | tesis internamente inconsistente — pendiente IV-77, mismo patrón est_02-06 |
| Gen. Exponencial          | MV                | alpha=+0.05%, lambda=+0.03%                       | PASS   | —     |
| Gen. Exponencial          | ML                | alpha=-41.76%, lambda=-19.01%                     | INFO   | pendiente IV-84 (signo ψ(1)), mismo patrón previo |
| Normal                    | Momentos/MV       | mu=+0.01%, sigma=0.00%                            | PASS   | —     |
| Normal                    | ML                | mu=+0.01%, sigma=0.00%                            | PASS   | —     |
| Log-Normal 2p             | Momentos/MV       | mu_y=-0.03%, sigma_y=+0.02%                       | PASS   | —     |
| Log-Normal 3p             | Momentos          | x0=+6.76%, mu_y=-1.82%, sigma_y=+7.63%            | INFO-A | g-propagación DECISIÓN013 |
| Log-Normal 3p             | MV                | x0=+0.01%, mu_y=0.00%, sigma_y=-0.01%             | PASS   | —     |
| Gamma 2p                  | Momentos          | alpha=+0.01%, beta=-0.01%                         | PASS   | —     |
| Gamma 2p                  | MV                | alpha=0.00%, beta=+0.01%                          | PASS   | —     |
| Gamma 2p                  | ML                | alpha=-0.03%, beta=0.00%                          | PASS   | —     |
| Gamma 3p                  | Momentos          | x0=+41.39%, alpha=+8.45%, beta=-14.98%            | INFO-A | g-propagación DECISIÓN013 (beta=4/g²) |
| Gamma 3p                  | MV                | x0=0.00%, alpha=0.00%, beta=0.00%                 | PASS   | —     |
| Gumbel                    | Momentos/MV/ML/ME | todas ≤0.01%                                      | PASS   | —     |
| GVE                       | Momentos          | alpha=+6.47%, beta=+95.24%, nu=+9503.80%          | INFO   | beta no reproducible con IV-203/204, pendiente Facundo. No es Causa A — mismo patrón est_02-06 |
| GVE                       | MV                | alpha=0.00%, beta=+1.08%, nu=0.00%                | PASS   | leve, dentro de tolerancia práctica |
| GVE                       | ML                | alpha=-10.03%, beta=-0.13%, nu=-57.48%            | INFO-B | beta coincide, nu/alpha difieren — convergencia a óptimo distinto |
| Log-Pearson III           | Directo           | NO_APLICABLE (B=2.7302 ∉ (3,6])                   | INFO   | METIS aplica restricción IV-249 correctamente — mismo patrón universal en las 7 estaciones anteriores |
| Log-Pearson III           | Indirecto         | alpha=+8.25%, beta=-14.97%, y0=+14.42%            | INFO-A | g-propagación DECISIÓN013 (gy de yi=ln(xi)) |
| Log-Pearson III           | MV                | METIS status=no_converge; tesis reporta alfa=0.677, beta=2.121, y0=2.382 | INFO | **anomalía nueva** — no vista en est_02-06 con esta dirección para LP3 MV específicamente (ahí fue al revés en est_06). Sin investigar. |

**Conteo: PASS=17, INFO=4, INFO-A=3, INFO-B=1, FAIL=0. Gen. Pareto no está en la tabla de tesis de esta estación (SKIP, mismo patrón que est_02-06).**

### PASO 6 — EEA: PASS (FAIL=0)
| Distribución | Método | EEA METIS | EEA Tesis | diff% | Nivel | Causa |
|---|---|---|---|---|---|---|
| Log-Normal 2p        | Momentos   |           2.9653 |     3.9748 | -25.40% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Log-Normal 2p        | MV         |           2.9653 |     3.9748 | -25.40% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Gumbel               | ML         |           4.3188 |     4.3188 |  +0.00% | PASS   |  |
| Log-Pearson III      | Indirecto  |           4.4182 |      4.414 |  +0.10% | PASS   |  |
| Gen. Exponencial     | MV         |           4.5495 |     4.5495 |  -0.00% | PASS   |  |
| Gamma 2p             | ML         |           4.0824 |      5.154 | -20.79% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Gumbel               | Momentos   |           5.2438 |     5.2438 |  +0.00% | PASS   |  |
| Gumbel               | ME         |           5.6210 |      5.621 |  -0.00% | PASS   |  |
| GVE                  | MV         |           5.6755 |     5.6755 |  +0.00% | PASS   |  |
| Gumbel               | MV         |           5.9393 |     5.9393 |  +0.00% | PASS   |  |
| Gamma 2p             | Momentos   |           4.9214 |     5.9656 | -17.50% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Gamma 3p             | MV         |           5.0036 |      6.107 | -18.07% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Gamma 3p             | Momentos   |           5.1136 |     6.1764 | -17.21% | INFO   | A: g-propagación DECISIÓN013 |
| Gamma 2p             | MV         |           5.3216 |     6.3467 | -16.15% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Log-Normal 3p        | MV         |           5.2059 |     6.3517 | -18.04% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Log-Normal 3p        | Momentos   |           5.3395 |     6.3714 | -16.20% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Exponencial x0beta   | Momentos   |           6.8458 |     6.8458 |  +0.00% | PASS   |  |
| Normal               | Momentos   |           7.3730 |     7.7741 |  -5.16% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Normal               | MV         |           7.3730 |     7.7741 |  -5.16% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Normal               | ML         |           7.3363 |     7.8195 |  -6.18% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Exponencial x0beta   | MV         |           8.4850 |      8.485 |  -0.00% | PASS   |  |
| Uniforme             | Momentos   |           8.4927 |     8.4927 |  -0.00% | PASS   |  |
| Exponencial beta     | Momentos   |          15.3565 |    15.3565 |  +0.00% | PASS   |  |
| Exponencial beta     | MV         |          15.3565 |    15.3565 |  +0.00% | PASS   |  |
| Uniforme             | MV         |          16.6835 |    16.6835 |  -0.00% | PASS   |  |
| Log-Pearson III      | Directo    | N/A (no_aplicable) |    26.4022 | —      | INFO   | status distinto — ver PASO5 |
| GVE                  | ML         |           4.3940 |    57.0234 | -92.29% | INFO   | B: convergencia a óptimo distinto |
| GVE                  | Momentos   |        4668.2873 |    61.2567 | +7520.86% | INFO   | pendiente Facundo — beta no reproducible IV-203/204 |
| Log-Pearson III      | MV         | N/A (no_converge) |    77.2356 | —      | INFO   | status distinto — ver PASO5 |

**Conteo: PASS=12, INFO-C=8, INFO-A=1, INFO-B=1, INFO=2 (GVE momentos + LP3 Directo/MV sin EEA por status distinto), FAIL=0.**

### PASO 7 — Cuantiles: PASS parcial (ver nota)
Modelo seleccionado por Facundo: Log Normal 2p (Momentos/MV). Gumbel ML como testigo (segunda columna de la tesis).

| T [años] | LN2p METIS | LN2p Tesis | diff%   | Nivel | Gumbel ML METIS | Gumbel ML Tesis | diff%  | Nivel |
|----------|------------|------------|---------|-------|------------------|------------------|--------|-------|
|   2      |    45.56   |    45.56    |  -0.01% | PASS  |    47.81   |    47.81    |  -0.00% | PASS  |
|   5      |    74.10   |    73.56    |  +0.73% | PASS  |    74.09   |    74.09    |  +0.00% | PASS  |
|  10      |    95.58   |    93.35    |  +2.38% | INFO  |    91.49   |    91.49    |  +0.00% | PASS  |
|  20      |   117.92   |   111.99    |  +5.30% | INFO  |   108.19   |   108.19    |  -0.00% | PASS  |
|  25      |   125.37   |   117.66    |  +6.55% | INFO  |   113.48   |   113.48    |  +0.00% | PASS  |
|  50      |   149.38   |   133.93    | +11.53% | INFO  |   129.79   |   129.79    |  +0.00% | PASS  |
| 100      |   174.87   |   147.89    | +18.25% | INFO  |   145.98   |   145.98    |  +0.00% | PASS  |

**Gumbel ML: PASS=7/7 (todas <0.01%, coincide casi exacto).**
**LN2p (modelo seleccionado por Facundo): PASS=1/7 (T=2), INFO=6/7 — el error crece con T, mismo patrón de "Causa C" ya visto en PASO6 para esta distribución (params ~idénticos, EEA/cuantiles divergen en la cola). Pendiente Facundo.**
