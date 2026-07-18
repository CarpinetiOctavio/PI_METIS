## Estación 6 — Las Tapias – Río San Bartolomé

### Serie (Sheet 1)
```python
serie = [
    30.0,   # 42-43
    18.0,   # 43-44
    36.0,   # 44-45
    29.0,   # 45-46
    103.0,  # 46-47
    96.0,   # 47-48
    63.0,   # 48-49
    23.0,   # 49-50
    21.0,   # 50-51
    16.0,   # 51-52
    25.0,   # 52-53
    51.0,   # 53-54
    21.0,   # 54-55
    109.0,  # 55-56
    64.0,   # 56-57
    70.0,   # 57-58
    36.0,   # 58-59
    54.0,   # 59-60
    46.0,   # 60-61
    72.0,   # 61-62
    47.0,   # 62-63
    99.0,   # 63-64
    21.0,   # 64-65
    18.0,   # 65-66
    24.0,   # 66-67
    19.0,   # 67-68
    43.0,   # 68-69
    26.0,   # 69-70
    20.0,   # 70-71
    23.0,   # 71-72
    55.0,   # 72-73
    48.0,   # 73-74
    32.0,   # 74-75
    26.0,   # 75-76
    14.0,   # 76-77
    104.0,  # 77-78
    50.0,   # 78-79
    27.0,   # 79-80
]
# n=38 (sin interrupciones)
```

### Estadística descriptiva esperada (Sheet 1)
| Variable                        | Valor esperado |
|---------------------------------|----------------|
| n                               | 38             |
| Media [m³/s]                    | 44.184         |
| Varianza [m³/s]²                | 775.344        |
| Desvío [m³/s]                   | 27.845         |
| Asimetría Sesgada               | 1.019          |
| Asimetría No Sesgada (g)        | 1.104          |
| Curtosis Sesgada                | 2.852          |
| Curtosis No Sesgada (k)         | 3.357          |
| Coeficiente de Variación (CV)   | 0.63           |
| Sumatoria ln(xi)                | 137.256        |
| beta_0 = M0                     | 44.184         |
| beta_1 = M1                     | 29.619         |
| beta_2 = M2                     | 23.023         |
| beta_3 = M3                     | 19.035         |
| Máximo [m³/s]                   | 109.0          |
| Mínimo [m³/s]                   | 14.0           |

---

### Etapa 1 — Homogeneidad (Sheet 2)

#### Helmert
| Parámetro              | Valor esperado |
|------------------------|----------------|
| N° de Series (S)       | 25             |
| N° de Cambios (C)      | 12             |
| Estadístico (S-C)      | 13             |
| n                      | 38             |
| Umbral inferior        | -6.08          |
| Umbral superior        | 6.08           |
| Conclusión individual  | El estadístico (S - C) no está comprendido entre -(nj-1)^0.5 y +(nj-1)^0.5. Por lo tanto la serie No es Homogénea. |

#### t de Student
| Parámetro              | Valor esperado |
|------------------------|----------------|
| Estadístico t          | 0.81           |
| Grados de libertad     | 36             |
| Valor crítico (tabla)  | 2.0281         |
| Conclusión individual  | El valor absoluto del estadístico t es menor que el valor de tabla t para 36 grados de libertad y para un nivel de significancia del 5%. Por lo tanto la serie es Homogénea. |

#### Cramer
| Parámetro              | Valor esperado |
|------------------------|----------------|
| tau subgrupo 1         | -0.06595       |
| tau subgrupo 2         | -0.19924       |
| t calculado sg. 1      | 0.49163        |
| t calculado sg. 2      | 0.76928        |
| Valor crítico (tabla)  | 2.0281         |
| Conclusión individual  | El valor absoluto de ambos estadísticos tw es menor que el valor de tabla de t para 36 G.L. y para α = 5%. La serie es Homogénea. |

**Veredicto homogeneidad:** Serie Homogénea (Aprobada por mayoría)
**Conclusión:** A pesar del rechazo registrado en la prueba de Helmert (13 fuera de ±6.08), se aprueba la homogeneidad de la serie debido a la coincidencia unánime de las dos pruebas de mayor peso estadístico (t de Student y Cramer) con alpha = 5% para sus 36 G.L. La serie posee consistencia numérica y queda habilitada para la Etapa 2.

---

### Etapa 1 — Independencia (Sheet 2)

#### Anderson
| Parámetro                              | Valor esperado              |
|----------------------------------------|-----------------------------|
| n                                      | 38                          |
| k = n/3                                | 12.7                        |
| k adoptado                             | 13                          |
| Media                                  | 44.18                       |
| N° máximo puntos fuera de bandas       | 1.3 (se redondea a 1)       |
| N° puntos fuera de bandas              | 0                           |
| Conclusión individual                  | Aceptada (0 puntos fuera cumple idealmente con el límite admisible de 1.3). Se acepta la hipótesis de que las variables de la serie son Independientes. |

#### Wald-Wolfowitz
| Parámetro                    | Valor esperado |
|------------------------------|----------------|
| n                            | 38             |
| n1                           | 16             |
| n2                           | 22             |
| R (rachas observadas)        | 13             |
| Media teórica de R           | 19.53          |
| Varianza teórica de R        | 8.78           |
| Estadístico Z                | -2.20          |
| Valor crítico α=0.05         | ± 1.96         |
| Valor crítico α=0.01         | ± 2.58         |
| Conclusión individual        | Aceptada por tolerancia (alpha = 0.01). El estadístico obtenido (Z = -2.20) excede el rango crítico para alpha = 0.05 (± 1.96), pero es aceptado formalmente al ampliar el nivel de significancia a alpha = 0.01 (± 2.58). |

**Veredicto independencia:** Serie Independiente
**Conclusión:** Aceptación de la hipótesis de independencia. La prueba de Anderson valida la estructura aleatoria al registrar 0 puntos fuera de las bandas de tolerancia (límite permitido: 1.3). La prueba de Wald-Wolfowitz presenta rechazo marginal para alpha = 0.05 (Z = -2.20 > 1.96) pero se acepta bajo el criterio de tolerancia al nivel alpha = 0.01 (límite ±2.58). La serie queda habilitada para avanzar a la Etapa 2.

**Veredicto general Etapa 1:** Habilitada para Etapa 2

---

### Etapa 2 — Parámetros (Sheet 3)
| Distribución              | Método                      | Parámetro 1     | Parámetro 2      | Parámetro 3      |
|---------------------------|-----------------------------|-----------------|------------------|------------------|
| Uniforme                  | Momentos                    | alfa = -4.04    | beta = 92.41     |                  |
| Uniforme                  | Máxima Verosimilitud        | alfa = 14.00    | beta = 109.00    |                  |
| Exponencial beta          | Momentos y M. Verosimilitud | beta = 0.023    |                  |                  |
| Exponencial x0 y beta     | Momentos                    | x0 = 16.34      | beta = 27.84     |                  |
| Exponencial x0 y beta     | Máxima Verosimilitud        | x0 = 13.18      | beta = 31.00     |                  |
| Generalizada Exponencial  | Momentos                    | alfa = 2.15     | lambda = 0.0128  |                  |
| Generalizada Exponencial  | Máxima Verosimilitud        | alfa = 3.86     | lambda = 0.0469  |                  |
| Generalizada Exponencial  | Momentos L                  | alfa = 0.78     | lambda = -0.0111 |                  |
| Normal                    | Momentos L                  | mu = 44.18      | sigma = 26.6745  |                  |
| Normal                    | Momentos y M. Verosimilitud | mu = 44.18      | sigma = 27.845   |                  |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | mu_y = 3.61     | sigma_y = 0.593  |                  |
| Log Normal (3 parámetros) | Momentos                    | x0 = -34.62     | mu_y = 4.3081    | sigma_y = 0.343  |
| Log Normal (3 parámetros) | Máxima Verosimilitud        | x0 = 11.65      | mu_y = 3.0942    | sigma_y = 0.9308 |
| Gamma (2 parámetros)      | Momentos                    | alfa = 17.55    | beta = 2.518     |                  |
| Gamma (2 parámetros)      | Máxima Verosimilitud        | alfa = 14.76    | beta = 2.993     |                  |
| Gamma (2 parámetros)      | Momentos L                  | alfa = 17.81    | beta = 2.481     |                  |
| Gamma (3 parámetros)      | Momentos                    | x0 = -6.25      | alfa = 15.373    | beta = 3.281     |
| Gamma (3 parámetros)      | Máxima Verosimilitud        | x0 = 5.241      | alfa = 15.612    | beta = 2.129     |
| Gamma (3 parámetros)      | Momento Prob. Pesada        | x0 = 11.81      | alfa = 30.244    | beta = 1.07      |
| Gumbel                    | Momentos                    | alfa = 21.719   | mu = 31.654      |                  |
| Gumbel                    | Máxima Verosimilitud        | alfa = 18.65    | mu = 32.14       |                  |
| Gumbel                    | Momentos L                  | alfa = 21.717   | mu = 31.649      |                  |
| Gumbel                    | Máxima Entropía             | alfa = 20.044   | mu = 32.615      |                  |
| GVE (Valores Extremos)    | Momentos                    | alfa = 17.943   | beta = -0.416    | nu = 35.214      |
| GVE (Valores Extremos)    | Máxima Verosimilitud        | alfa = 13.505   | beta = -0.531    | nu = 27.675      |
| GVE (Valores Extremos)    | Momentos L                  | alfa = 21.841   | beta = -0.202    | nu = 52.147      |
| Log Pearson tipo III      | Momentos Método Directo     | alfa = 0.333    | beta = 0.259     | y0 = 3.683       |
| Log Pearson tipo III      | Momentos Método Indirecto   | alfa = 0.1      | beta = 34.943    | y0 = 0.105       |
| Log Pearson tipo III      | Máxima Verosimilitud        | NO_CONVERGE     | NO_CONVERGE      | NO_CONVERGE      |

---

### Etapa 2 — EEA esperados (Sheet 3)
| Distribución              | Método                      | EEA [m³/s]  |
|---------------------------|-----------------------------|-------------|
| Exponencial x0 y beta     | Máxima Verosimilitud        | 5.7364      |
| Gamma (3 parámetros)      | Momento Prob. Pesada        | 5.7459      |
| Exponencial x0 y beta     | Momentos                    | 6.4958      |
| Gamma (2 parámetros)      | Momentos L                  | 6.8694      |
| Gamma (2 parámetros)      | Momentos                    | 6.9649      |
| Gumbel                    | Momentos                    | 7.1371      |
| Gumbel                    | Momentos L                  | 7.1384      |
| Log Normal (3 parámetros) | Máxima Verosimilitud        | 7.2038      |
| Log Pearson tipo III      | Momentos M. Indirecto       | 7.2097      |
| Gamma (3 parámetros)      | Momentos                    | 7.2912      |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | 7.4379      |
| Log Normal (3 parámetros) | Momentos                    | 7.6639      |
| Generalizada Exponencial  | Máxima Verosimilitud        | 7.7134      |
| Gumbel                    | Máxima Entropía             | 7.9158      |
| Gamma (2 parámetros)      | Máxima Verosimilitud        | 8.1993      |
| Gumbel                    | Máxima Verosimilitud        | 9.04        |
| Normal                    | Momentos y M. Verosimilitud | 10.5        |
| Normal                    | Momentos L                  | 10.6605     |
| Gamma (3 parámetros)      | Máxima Verosimilitud        | 10.6842     |
| Uniforme                  | Momentos                    | 10.92       |
| Exponencial beta          | Momentos y M. Verosimilitud | 12.5535     |
| GVE (Valores Extremos)    | Máxima Verosimilitud        | 13.5981     |
| Uniforme                  | Máxima Verosimilitud        | 20.8429     |
| Log Pearson tipo III      | Momentos M. Directo         | 23.9915     |
| GVE (Valores Extremos)    | Momentos L                  | 26.2049     |
| GVE (Valores Extremos)    | Momentos                    | 26.8594     |
| Log Pearson tipo III      | Máxima Verosimilitud        | NO_CONVERGE |

---

### Etapa 2 — Cuantiles esperados (Sheet 3)
| T [años] | Exp x0β MV [m³/s] | Gamma 3p MPP [m³/s] |
|----------|-------------------|---------------------|
| 2        | 34.67             | 35.11               |
| 5        | 63.08             | 62.76               |
| 10       | 84.56             | 82.29               |
| 20       | 106.05            | 100.17              |
| 25       | 112.97            | 105.49              |
| 50       | 134.46            | 120.46              |
| 100      | 155.94            | 132.94              |

### Modelo seleccionado por Facundo
Modelo Exponencial de parámetros x0 y beta (Máxima Verosimilitud) seleccionado. La distribución Exponencial x0β calibrada por MV obtiene el menor EEA (5.7364 m³/s). La inspección gráfica ratificó el criterio numérico sobre la distribución Gamma de 3 parámetros MPP, que actuó como modelo testigo (EEA = 5.7459 m³/s). Los caudales de diseño se establecen desde los 34.67 m³/s para crecidas ordinarias (T=2 años) hasta un máximo extremo de 155.94 m³/s para la recurrencia límite de 100 años.

---

## Resultados de Regresión METIS --> UNITARIAS

### Estado general: PASS — FAIL=0 en todos los pasos

### PASO 1 — Estadística descriptiva: PASS
| Variable                      | METIS        | Tesis        | diff%   | Nivel |
|-------------------------------|--------------|--------------|---------|-------|
| n                             | 38           | 38           | 0.000%  | PASS  |
| Media                         | 44.18421     | 44.184       | +0.0005%| PASS  |
| Varianza                      | 775.34353    | 775.344      | -0.0001%| PASS  |
| Desvío                        | 27.84499     | 27.845       | -0.0000%| PASS  |
| M0                            | 44.18421     | 44.184       | +0.0005%| PASS  |
| M1                            | 29.61878     | 29.619       | -0.0008%| PASS  |
| M2                            | 23.02292     | 23.023       | -0.0004%| PASS  |
| M3                            | 19.03548     | 19.035       | +0.0025%| PASS  |
| Sumatoria ln(xi)              | 137.25581    | 137.256      | -0.0001%| PASS  |
| Máximo                        | 109.0        | 109.0        | 0.000%  | PASS  |
| Mínimo                        | 14.0         | 14.0         | 0.000%  | PASS  |
| Asimetría sesgada             | 1.06013      | 1.019        | +4.04%  | INFO  |
| Asimetría no sesgada (g)      | 1.14927      | 1.104        | +4.10%  | INFO  |
| Curtosis sesgada              | 3.00822      | 2.852        | +5.48%  | INFO  |
| Curtosis no sesgada           | 3.54070      | 3.357        | +5.47%  | INFO  |
| CV                            | 0.63020      | 0.63         | +0.03%  | INFO  |

Nota g: METIS sigue IV-4/IV-5 (ddof=0). Excel usa SKEW() (ddof=1). Diferencia trazable — ver DECISIÓN013.

### PASO 2 — Homogeneidad: PASS
| Prueba       | Estadístico METIS | Estadístico Tesis | diff%   | Veredicto | Nivel |
|--------------|--------------------|--------------------|---------|-----------|-------|
| Helmert S-C  | 13.0               | 13                 | 0.000%  | Rechazada | PASS  |
| t-Student    | 0.80746 (n1=19,n2=19) | 0.81            | -0.314% | Aprobada  | INFO  |
| Cramer τ_w1 (n_w1=23) | -0.06595  | -0.06595           | +0.0004%| Aprobada  | PASS  |
| Cramer τ_w2 (n_w2=11) | -0.19924  | -0.19924           | +0.0002%| Aprobada  | PASS  |
| Cramer t_w1  | 0.49163            | 0.49163            | +0.0002%| —         | PASS  |
| Cramer t_w2  | 0.76928            | 0.76928            | -0.0002%| —         | PASS  |
| Veredicto    | homogeneidad_warning | Serie Homogénea (mayoría) | — | — | PASS  |

Nota t-Student: diff -0.31% trazable a redondeo Excel en medias de submuestras (INFO per README).
Nota veredicto: Cramer y t-Student aprueban unánimemente; Helmert rechaza con warning normal (no crítico) — pipeline continúa. Coincide funcionalmente con la tesis ("Aprobada por mayoría").

### PASO 3 — Independencia: PASS
| Prueba              | METIS               | Tesis                | diff%   | Veredicto | Nivel |
|----------------------|----------------------|-----------------------|---------|-----------|-------|
| Anderson k_max       | 12 (n//3)            | 13 (ceil(n/3))        | —       | —         | INFO  |
| Anderson lags fuera  | 0                     | 0                     | 0.000%  | Aprobada  | PASS  |
| Wald-Wolfowitz n1,n2,R | 16, 22, 13          | 16, 22, 13            | 0.000%  | —         | PASS  |
| Wald-Wolfowitz Z     | -2.20307              | -2.20                 | +0.140% | Rechazada (α=0.05) | PASS |
| Veredicto            | independiente         | independiente         | —       | —         | PASS  |

Nota Anderson: k_max METIS=12 (n//3) vs tesis=13 (ceil(n/3)) — verificado que el lag 13 también cae dentro de banda (r_13=-0.14190, banda ±0.344/-0.424); no cambia el veredicto.
Nota Wald: rechaza a α=0.05 (|Z|=2.203>1.96), TEST_WARNING_SMALL_SAMPLE emitido (n≤40). Jerarquía Anderson-manda produce veredicto final independiente pese al rechazo de Wald — consistente con constraints.md.

### PASO 4 — Veredicto Etapa 1: PASS
Habilitada para Etapa 2. Homogeneidad OK con warning (Helmert rechaza, Cramer/t-Student aprueban). Independencia OK (Anderson aprueba, jerarquía manda sobre Wald).

### PASO 5 — Parámetros Etapa 2: PASS (FAIL=0)
| Distribución       | Método    | Param METIS                                    | Param Tesis                          | Nivel  | Nota |
|---------------------|-----------|-------------------------------------------------|----------------------------------------|--------|------|
| Uniforme            | Momentos  | α=-4.0447, β=92.4131                            | α=-4.04, β=92.41                      | PASS   | — |
| Uniforme            | MV        | α=14.00, β=109.00                               | α=14.00, β=109.00                     | PASS   | — |
| Exponencial β       | Mom/MV    | β=0.02263                                        | β=0.023                               | PASS   | redondeo 3 decimales sobre valor pequeño |
| Exponencial x0β     | Momentos  | x0=16.339, β=27.845                             | x0=16.34, β=27.84                     | PASS   | — |
| Exponencial x0β     | MV        | x0=13.184, β=31.00                              | x0=13.18, β=31.00                     | PASS   | — |
| Gen. Exponencial    | Momentos  | α=3.0788, λ=0.04199                             | α=2.15, λ=0.0128                      | INFO   | pendiente IV-77 — no investigado (patrón conocido) |
| Gen. Exponencial    | MV        | α=3.8569, λ=0.04692                             | α=3.86, λ=0.0469                      | PASS   | — |
| Gen. Exponencial    | ML        | α=0.4025, λ=-0.01440                            | α=0.78, λ=-0.0111                     | INFO   | pendiente IV-84 — no investigado; signo λ coincide |
| Normal              | Mom/MV    | µ=44.184, σ=27.845                              | µ=44.18, σ=27.845                     | PASS   | — |
| Normal              | ML        | µ=44.184, σ=26.6745                             | µ=44.18, σ=26.6745                    | PASS   | — |
| Log-Normal 2p       | Mom/MV    | µy=3.6120, σy=0.5932                            | µy=3.61, σy=0.593                     | PASS   | — |
| Log-Normal 3p       | Momentos  | x0=-31.758, µy=4.2669, σy=0.35516               | x0=-34.62, µy=4.3081, σy=0.343        | INFO-A | g-propagación DECISIÓN013+DECISIÓN015 |
| Log-Normal 3p       | MV        | x0=11.654, µy=3.0942, σy=0.9308                 | x0=11.65, µy=3.0942, σy=0.9308        | PASS   | — |
| Gamma 2p            | Momentos  | α=17.548, β=2.5179                              | α=17.55, β=2.518                      | PASS   | — |
| Gamma 2p            | MV        | α=14.764, β=2.9928                              | α=14.76, β=2.993                      | PASS   | — |
| Gamma 2p            | ML        | α=17.808, β=2.4811                              | α=17.81, β=2.481                      | PASS   | — |
| Gamma 3p            | Momentos  | β=3.0284, α=16.001, x0=-4.273                   | β=3.281, α=15.373, x0=-6.25           | INFO-A | verificado exacto: β=4/g² reproduce ambos lados con g respectivo — Causa A pura |
| Gamma 3p            | MV        | NO_CONVERGE                                      | x0=5.241, α=15.612, β=2.129           | INFO   | IV-142 sin raíz en todo el dominio (verificado, scan 5000 pts); params de tesis no autoconsistentes con IV-140/141 evaluados directamente — pendiente Facundo |
| Gamma 3p            | MPP       | EXCLUIDO (no implementado)                       | x0=11.81, α=30.244, β=1.07            | EXCLUIDO | Cap. IV no desarrolla ecuaciones MPP |
| Gumbel              | Momentos  | µ=31.654, α=21.719                              | µ=31.654, α=21.719                    | PASS   | — |
| Gumbel              | MV        | µ=32.140, α=18.650                              | µ=32.14, α=18.65                      | PASS   | — |
| Gumbel              | ML        | µ=31.649, α=21.717                              | µ=31.649, α=21.717                    | PASS   | — |
| Gumbel              | ME        | µ=32.615, α=20.044                              | µ=32.615, α=20.044                    | PASS   | — |
| GVE                 | Momentos  | ν=43794.15, α=21.682, β=-0.00099                | ν=35.214, α=17.943, β=-0.416          | INFO   | pendiente Facundo — β no reproducible con IV-203/204 (patrón conocido) |
| GVE                 | MV        | ν=27.675, α=13.505, β=-0.5307                   | ν=27.675, α=13.505, β=-0.531          | PASS   | — |
| GVE                 | ML        | ν=29.886, α=17.337, β=-0.2024                   | ν=52.147, α=21.841, β=-0.202          | INFO-B | β coincide, ν/α difieren — convergencia a óptimo distinto |
| Log-Pearson III     | Directo   | NO_APLICABLE (B=2.697 ∉ (3,6])                   | α=0.333, β=0.259, y0=3.683            | INFO   | restricción IV-249 aplicada correctamente |
| Log-Pearson III     | Indirecto | β=32.257, α=0.10445, y0=0.2427                  | β=34.943, α=0.10, y0=0.105            | INFO-A | verificado exacto: gy implícito tesis=0.3383 vs gy_METIS=0.3521 (diff +4.08%) reproduce params tesis — Causa A pura |
| Log-Pearson III     | MV        | β=3.695, α=0.3225, y0=2.4205                    | NO_CONVERGE                            | INFO   | METIS converge — verificado mínimo interior genuino (no falsa convergencia de borde); ver nota PASO 6 |
| Gen. Pareto         | todos     | (calculados)                                     | no listada en tabla tesis             | SKIP   | mismo patrón est_02-05 |

### PASO 6 — EEA: PASS (FAIL=0)
| Distribución       | Método    | EEA METIS   | EEA Tesis | diff%       | Nivel  | Causa |
|---------------------|-----------|-------------|-----------|-------------|--------|-------|
| Exponencial x0β     | MV        | 5.7364      | 5.7364    | +0.000%     | PASS   | — |
| Gamma 3p            | MPP       | N/A         | 5.7459    | —           | INFO   | EXCLUIDO — Cap. IV no desarrolla ecuaciones MPP |
| Exponencial x0β     | Momentos  | 6.4958      | 6.4958    | +0.000%     | PASS   | — |
| Gamma 2p            | ML        | 6.3883      | 6.8694    | -7.004%     | INFO-C | EEA distinto con params casi idénticos — pendiente Facundo |
| Gamma 2p            | Momentos  | 6.4601      | 6.9649    | -7.248%     | INFO-C | ídem |
| Gumbel              | Momentos  | 7.1371      | 7.1371    | +0.000%     | PASS   | — |
| Gumbel              | ML        | 7.1384      | 7.1384    | +0.000%     | PASS   | — |
| Log-Normal 3p       | MV        | 8.7361      | 7.2038    | +21.271%    | INFO-C | params casi idénticos pero EEA diverge — Causa C, pendiente Facundo |
| Log-Pearson III     | Indirecto | 7.2840      | 7.2097    | +1.031%     | INFO-A | g-propagación DECISIÓN013 — consecuencia aritmética menor |
| Gamma 3p            | Momentos  | 6.7370      | 7.2912    | -7.601%     | INFO-A | g-propagación DECISIÓN013 |
| Log-Normal 2p       | Mom/MV    | 6.9098      | 7.4379    | -7.100%     | INFO-C | tesis no marca NO_APLICABLE en est_06 (rompe patrón est_02/03/05); causa EEA pendiente Facundo |
| Log-Normal 3p       | Momentos  | 7.1582      | 7.6639    | -6.598%     | INFO-A | g-propagación DECISIÓN013+DECISIÓN015 |
| Gen. Exponencial    | MV        | 7.7134      | 7.7134    | +0.000%     | PASS   | — |
| Gumbel              | ME        | 7.9158      | 7.9158    | +0.000%     | PASS   | — |
| Gamma 2p            | MV        | 7.5201      | 8.1993    | -8.284%     | INFO-C | ídem Gamma2p momentos/ml |
| Gumbel              | MV        | 9.0400      | 9.0400    | +0.000%     | PASS   | — |
| Normal              | Mom/MV    | 10.5274     | 10.5000   | +0.261%     | PASS   | — |
| Normal              | ML        | 10.5791     | 10.6605   | -0.764%     | PASS   | — |
| Gamma 3p            | MV        | N/A (NO_CONVERGE) | 10.6842 | —         | INFO   | tesis reporta EEA pese a que IV-142 no tiene raíz (verificado) |
| Uniforme            | Momentos  | 10.9200     | 10.9200   | +0.000%     | PASS   | — |
| Exponencial β       | Mom/MV    | 12.5535     | 12.5535   | +0.000%     | PASS   | — |
| GVE                 | MV        | 13.5981     | 13.5981   | +0.000%     | PASS   | — |
| Uniforme            | MV        | 20.8429     | 20.8429   | +0.000%     | PASS   | — |
| Log-Pearson III     | Directo   | N/A (NO_APLICABLE) | 23.9915 | —         | INFO   | B=2.697 ∉ (3,6] — restricción aplicada correctamente |
| GVE                 | ML        | 7.2873      | 26.2049   | -72.191%    | INFO-B | β coincide, ν/α difieren — convergencia a óptimo distinto |
| GVE                 | Momentos  | 45598.6928  | 26.8594   | +169668.099%| INFO   | β degenerado (≈-0.001) — no reproducible con IV-203/204, pendiente Facundo |
| Log-Pearson III     | MV        | 10.9881     | N/A (NO_CONVERGE) | —   | INFO   | METIS converge (mínimo interior genuino, verificado); tesis NO_CONVERGE — ver corrección pendiente en pendientes-facundo.md (guard borde superior) |
| Gen. Pareto         | Momentos  | 28.4285     | no listada | —          | SKIP   | — |
| Gen. Pareto         | MV        | N/A (NO_CONVERGE) | no listada | —    | SKIP   | — |
| Gen. Pareto         | MC        | 5.9663      | no listada | —          | SKIP   | — |
| Gen. Pareto         | MPP       | 136724332.72 | no listada | —         | SKIP   | degenerado, sin referencia |
| Gen. Exponencial    | Momentos  | 6.4508      | no listada | —          | SKIP   | solo MV tiene referencia en tesis |
| Gen. Exponencial    | ML        | 107.5180    | no listada | —          | SKIP   | — |

**Conteo: PASS=16, INFO-A=3, INFO-B=1, INFO-C=4, INFO=6, SKIP=6, FAIL=0**

### PASO 7 — Cuantiles: PASS (FAIL=0)
Modelo seleccionado: Exponencial x0β MV. Gamma 3p MPP como testigo de tesis, sin referencia en METIS (EXCLUIDO).

| T [años] | Exp x0β MV METIS | Exp x0β MV Tesis | diff%    | Nivel | Gamma 3p MPP Tesis | METIS | Nivel |
|----------|-------------------|--------------------|----------|-------|---------------------|-------|-------|
| 2        | 34.6718           | 34.67              | +0.0051% | PASS  | 35.11               | N/A   | INFO/sin referencia |
| 5        | 63.0768           | 63.08               | -0.0051% | PASS  | 62.76               | N/A   | INFO/sin referencia |
| 10       | 84.5643           | 84.56               | +0.0051% | PASS  | 82.29               | N/A   | INFO/sin referencia |
| 20       | 106.0519          | 106.05              | +0.0018% | PASS  | 100.17               | N/A   | INFO/sin referencia |
| 25       | 112.9694          | 112.97              | -0.0006% | PASS  | 105.49               | N/A   | INFO/sin referencia |
| 50       | 134.4569          | 134.46              | -0.0023% | PASS  | 120.46               | N/A   | INFO/sin referencia |
| 100      | 155.9445          | 155.94              | +0.0029% | PASS  | 132.94               | N/A   | INFO/sin referencia |

**Exp x0β MV: PASS=7/7. Gamma 3p MPP: INFO/sin referencia ×7 — Cap. IV no desarrolla ecuaciones MPP — EXCLUIDO. Tesis reporta cuantiles pero METIS no puede calcularlos.**

### Hallazgos nuevos de esta auditoría (no presentes en est_02-05)
1. **Gamma 3p MV**: METIS NO_CONVERGE; tesis reporta parámetros y EEA. Verificado que IV-142 no tiene raíz en todo el dominio válido y que los propios parámetros de la tesis no satisfacen IV-140/141 al evaluarlos directamente. Pendiente Facundo — posible método/tabla adicional no documentada en Cap. IV.
2. **Log-Pearson III MV**: METIS converge (β=3.695, α=0.322, y0=2.420, EEA=10.9881); tesis reporta NO_CONVERGE. Verificado que `result.x` no es falsa convergencia de borde (mínimo interior genuino, perfil tabulado). Se detectó que el guard de convergencia actual solo protege el borde inferior del intervalo de búsqueda — corrección de guard simétrico documentada como pendiente en `pendientes-facundo.md`.
3. **Log-Normal 2p**: a diferencia de est_02/03/05 (donde la tesis marca NO_APLICABLE sin explicación), en est_06 la tesis sí reporta EEA=7.4379 — el patrón NO_APLICABLE no es universal.

---

## Resultados de Regresión METIS --> PIPELINE COMPLETO (ejecución en vivo, 2026-07-13)

**Qué es esto:** salida real de correr `ejecutar_etapa1()` seguido de
`ejecutar_etapa2()` — el pipeline completo tal como orquesta
`pipeline.py`/`pipeline2.py` hoy — sobre la serie cruda de esta estación
(sin filtrar ni preprocesar). A diferencia de la sección "UNITARIAS" de
arriba (que corre cada prueba/distribución de forma aislada), esto pasa por
el orquestador completo de punta a punta. Mismo formato de tablas que las
secciones de la ficha original (Sheet 1/2/3) y de METIS-unitarias, para que
sea comparable fila por fila.

**Contexto — auditoría de cableado (Fase 2, Bloque 6/7):** esta corrida es
un diagnóstico dentro de esa auditoría, no una prueba de cierre. **No
constituye ni forma parte del Bloque 8** (la prueba end-to-end final, que se
hace después de cerrar Bloque 6/7 para las 13 distribuciones, contra est_02 a
est_06 completas). El único propósito acá es tener un mapa mental actualizado
de cómo está operando el pipeline completo en este momento — no se saca
ninguna conclusión de cableado ni se investiga causa de ningún valor en esta
sección (eso lo hace Octavio aparte, sobre lo que aparezca señalado).

Invocación exacta:
```python
r1 = ejecutar_etapa1(
    serie=serie,  # lista cruda, sin modificar
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
| n | 38 |
| Media [m³/s] | 44.18421052631579 |
| Mediana [m³/s] | 34.0 |
| Varianza (no sesgada) [m³/s]² | 775.3435277382647 |
| Varianza (sesgada) [m³/s]² | 754.9397506925209 |
| Desvío [m³/s] | 27.844991070895762 |
| Asimetría Sesgada | 1.0601306781250086 |
| Asimetría No Sesgada (g) | 1.149270795204589 |
| Curtosis Sesgada | 3.008222803242971 |
| Curtosis No Sesgada (k) | 3.5406950162923274 |
| Coeficiente de Variación (CV) | 0.630202299400857 |
| Sumatoria ln(xi) | 137.2558141307894 |
| beta_0 = M0 | 44.18421052631579 |
| beta_1 = M1 | 29.618776671408252 |
| beta_2 = M2 | 23.022917654496602 |
| beta_3 = M3 | 19.03548059337533 |
| Máximo [m³/s] | 109.0 |
| Mínimo [m³/s] | 14.0 |
| Rango [m³/s] | 95.0 |

### Etapa 1 — Homogeneidad (pipeline completo — Sheet 2)

#### Helmert
| Parámetro | Valor |
|-----------|-------|
| Estadístico (S-C) | 13.0 |
| Valor crítico (± lim) | 6.082762530298219 |
| Veredicto | rechazada |
| Warning | TEST_WARNING_HOMOGENEITY |

#### t de Student
| Parámetro | Valor |
|-----------|-------|
| Estadístico t | 0.8074562305513303 |
| n1 | 19 |
| n2 | 19 |
| Valor crítico (tabla) | 2.0280940009804502 |
| Veredicto | aprobada |

#### Cramer
| Parámetro | Valor |
|-----------|-------|
| Estadístico (t_w1) | 0.769278632339561 |
| n_w1 | 23 |
| n_w2 | 11 |
| Valor crítico (tabla) | 2.0280940009804502 |
| Veredicto | aprobada |

**Veredicto homogeneidad (pipeline):** homogeneidad_warning

### Etapa 1 — Independencia (pipeline completo — Sheet 2)

#### Anderson
| Parámetro | Valor |
|-----------|-------|
| Estadístico (máx r_k) | -0.24659364354721178 |
| Valor crítico | 0.2908049704659547 |
| Veredicto | aprobada |

#### Wald-Wolfowitz
| Parámetro | Valor |
|-----------|-------|
| Estadístico Z | -2.2030740690079744 |
| Valor crítico (α=0.05) | ± 1.959963984540054 |
| Veredicto | rechazada |
| Warning | TEST_WARNING_SMALL_SAMPLE |

**Veredicto independencia (pipeline):** independiente

### Etapa 1 — Tendencia y Atípicos (pipeline completo) — sin ficha de Facundo de referencia
Mann-Kendall, Kolmogorov-Smirnov y Chow no están en la tesis de Facundo (los
agregó Carlos) — no hay valor "esperado" ni "METIS unitario" previo contra el
cual comparar estas tres filas en ningún archivo de este repo.

#### Mann-Kendall
| Parámetro | Valor |
|-----------|-------|
| Estadístico | -0.36480633028194265 |
| Valor crítico | 1.959963984540054 |
| Veredicto | aprobada |
| Warning | None |

#### Kolmogorov-Smirnov (tendencia)
| Parámetro | Valor |
|-----------|-------|
| Estadístico (Z tipificado) | 0.6488856845230501 |
| Valor crítico | 1.358 |
| Veredicto | aprobada |

#### Chow
| Parámetro | Valor |
|-----------|-------|
| Estadístico (máx Z_i) | 1.8194456219608204 |
| Valor crítico (K_N) | 2.8463312393601883 |
| Veredicto | aprobada |

**Veredicto general Etapa 1 (pipeline):** nivel_confianza=`con_warnings` — warnings: TEST_WARNING_SMALL_SAMPLE, TEST_WARNING_HOMOGENEITY

### Etapa 2 — Parámetros, EEA y Estado (pipeline completo — Sheet 3)
| Distribución | Método | Parámetro 1 | Parámetro 2 | Parámetro 3 | EEA [m³/s] | Status |
|---|---|---|---|---|---|---|
| Uniforme | Momentos | alfa = -4.0447 | beta = 92.4131 |  | 10.9200 | ok |
| Uniforme | Máxima Verosimilitud | alfa = 14.0000 | beta = 109.0000 |  | 20.8429 | ok |
| Exponencial beta | Momentos | beta = 0.022633 |  |  | 12.5535 | ok |
| Exponencial beta | Máxima Verosimilitud | beta = 0.022633 |  |  | 12.5535 | ok |
| Exponencial x0 y beta | Momentos | x0 = 16.3392 | beta = 27.8450 |  | 6.4958 | ok |
| Exponencial x0 y beta | Máxima Verosimilitud | x0 = 13.1842 | beta = 31.0000 |  | 5.7364 | ok |
| Generalizada Exponencial | Momentos | alfa = 3.0788 | lambda = 0.041993 |  | 6.4508 | ok |
| Generalizada Exponencial | Máxima Verosimilitud | alfa = 3.8569 | lambda = 0.046915 |  | 7.7134 | ok |
| Generalizada Exponencial | Momentos L | alfa = 0.402465 | lambda = -0.014396 |  | 107.5180 | ok |
| Normal | Momentos | mu = 44.1842 | sigma = 27.8450 |  | 10.5274 | ok |
| Normal | Máxima Verosimilitud | mu = 44.1842 | sigma = 27.8450 |  | 10.5274 | ok |
| Normal | Momentos L | mu = 44.1842 | sigma = 26.6745 |  | 10.5791 | ok |
| Log Normal (2 parámetros) | Momentos | mu_y = 3.6120 | sigma_y = 0.593232 |  | 6.9098 | ok |
| Log Normal (2 parámetros) | Máxima Verosimilitud | mu_y = 3.6120 | sigma_y = 0.593232 |  | 6.9098 | ok |
| Log Normal (3 parámetros) | Momentos | x0 = -31.7582 | mu_y = 4.2669 | sigma_y = 0.355159 | 7.1582 | ok |
| Log Normal (3 parámetros) | Máxima Verosimilitud | x0 = 11.6541 | mu_y = 3.0942 | sigma_y = 0.930815 | 8.7361 | ok |
| Gamma (2 parámetros) | Momentos | alfa = 17.5480 | beta = 2.5179 |  | 6.4601 | ok |
| Gamma (2 parámetros) | Máxima Verosimilitud | alfa = 14.7636 | beta = 2.9928 |  | 7.5201 | ok |
| Gamma (2 parámetros) | Momentos L | alfa = 17.8084 | beta = 2.4811 |  | 6.3883 | ok |
| Gamma (3 parámetros) | Momentos | x0 = -4.2726 | alfa = 16.0007 | beta = 3.0284 | 6.7370 | ok |
| Gamma (3 parámetros) | Máxima Verosimilitud |  |  |  | — | no_converge |
| Gumbel | Momentos | mu = 31.6540 | alfa = 21.7191 |  | 7.1371 | ok |
| Gumbel | Máxima Verosimilitud | mu = 32.1397 | alfa = 18.6502 |  | 9.0400 | ok |
| Gumbel | Momentos L | mu = 31.6486 | alfa = 21.7174 |  | 7.1384 | ok |
| Gumbel | Máxima Entropía | mu = 32.6146 | alfa = 20.0439 |  | 7.9158 | ok |
| GVE (Valores Extremos) | Momentos | nu = 43,794.1498 | alfa = 21.6825 | beta = -0.000991 | 45,598.6928 | ok |
| GVE (Valores Extremos) | Máxima Verosimilitud | nu = 27.6751 | alfa = 13.5053 | beta = -0.530713 | 13.5981 | ok |
| GVE (Valores Extremos) | Momentos L | nu = 29.8863 | alfa = 17.3367 | beta = -0.202354 | 7.2873 | ok |
| Log Pearson tipo III | Momentos Método Directo |  |  |  | — | no_aplicable |
| Log Pearson tipo III | Momentos Método Indirecto | alfa = 0.104452 | beta = 32.2566 | y0 = 0.242743 | 7.2840 | ok |
| Log Pearson tipo III | Máxima Verosimilitud | alfa = 0.322475 | beta = 3.6950 | y0 = 2.4205 | 10.9881 | ok |
| Generalizada de Pareto | Momentos | mu = 10.9540 | sigma = 40.2784 | epsilon = 0.212101 | 28.4285 | ok |
| Generalizada de Pareto | Máxima Verosimilitud |  |  |  | — | no_converge |
| Generalizada de Pareto | Mínimos Cuadrados | mu = 14.0000 | sigma = 30.0257 | epsilon = 0.0000142 | 5.9663 | ok |
| Generalizada de Pareto | Momento Prob. Pesada | mu = 2.1564 | sigma = 500.9780 | epsilon = 4.2996 | 136,724,332.7244 | ok |

### Notas de cableado — Bloque 6/7 (solo señalamiento, sin investigar causa)

**¿Ceros en la serie?** No — mínimo observado = 14.0 (`tiene_ceros=False` pasado a `ejecutar_etapa2()`). La rama `STATUS_DISABLED_ZEROS` no se ejercita en ninguna de las 4 estaciones auditadas hasta ahora (est_02, est_03, est_05, est_06) — sigue sin verificar en el pipeline real.

**Cambios de status vs. est_02** (comparando categoría, no valor numérico):
- `gen_pareto/mc`: est_02=`no_converge` -> est_06=`ok`

**GVE / MV — rama de inicialización:**
- Descartada (guard IV-202 falla con nu0=43794.1498, alpha0=21.6825, beta0 derivado de g). Fallback activo: Momentos-L (ML) como condición inicial para MV.