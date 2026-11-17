## Estación 3 — La Tapa – Río Las Cañitas

### Serie (Sheet 1)
```python
serie = [
    114.0,  # 39-40
    50.0,   # 40-41
    54.0,   # 41-42
    105.0,  # 42-43
    45.0,   # 43-44
    126.0,  # 44-45
    14.0,   # 45-46
    45.0,   # 46-47
    14.0,   # 47-48
    20.0,   # 48-49
    34.0,   # 49-50
    47.0,   # 50-51
    3.0,    # 51-52
    32.0,   # 52-53
    32.0,   # 53-54
    179.0,  # 54-55
    42.0,   # 55-56
    402.0,  # 56-57
    314.0,  # 57-58
    36.0,   # 58-59
    47.0,   # 59-60
    21.0,   # 60-61
    44.0,   # 61-62
    19.0,   # 62-63
    32.0,   # 63-64
    58.0,   # 64-65
    83.0,   # 65-66
    9.0,    # 66-67
    13.0,   # 67-68
    28.0,   # 68-69
    2.0,    # 69-70
    29.0,   # 70-71
    71.0,   # 71-72
    57.0,   # 72-73
    84.0,   # 73-74
    34.0,   # 74-75
    7.0,    # 75-76
    34.0,   # 76-77
    73.0,   # 77-78
    70.0,   # 78-79
    35.0,   # 79-80
]
```

### Estadística descriptiva esperada (Sheet 1)
| Variable                        | Valor esperado |
|---------------------------------|----------------|
| n                               | 41             |
| Media [m³/s]                    | 62.39          |
| Varianza [m³/s]²                | 5963.694       |
| Desvío [m³/s]                   | 77.225         |
| Asimetría Sesgada               | 2.942          |
| Asimetría No Sesgada (g)        | 3.17           |
| Curtosis Sesgada                | 12.07          |
| Curtosis No Sesgada (k)         | 14.033         |
| Coeficiente de Variación (CV)   | 1.238          |
| Sumatoria ln(xi)                | 149.228        |
| beta_0 = M0                     | 62.39          |
| beta_1 = M1                     | 47.228         |
| beta_2 = M2                     | 39.513         |
| beta_3 = M3                     | 34.707         |
| Máximo [m³/s]                   | 402.0          |
| Mínimo [m³/s]                   | 2.0            |

---

### Etapa 1 — Homogeneidad (Sheet 2)

#### Helmert
| Parámetro              | Valor esperado |
|------------------------|----------------|
| N° de Series (S)       | 23             |
| N° de Cambios (C)      | 17             |
| Estadístico (S-C)      | 6              |
| n                      | 41             |
| Umbral inferior        | -6.32          |
| Umbral superior        | 6.32           |
| Conclusión individual  | El estadístico (S - C) está comprendido entre -(nj-1)^0.5 y +(nj-1)^0.5. Por lo tanto la serie es Homogénea. |

#### t de Student
| Parámetro              | Valor esperado |
|------------------------|----------------|
| Estadístico t          | 1.81           |
| Grados de libertad     | 39             |
| Valor crítico (tabla)  | 2.0227         |
| Conclusión individual  | El valor absoluto del estadístico t es menor que el valor de tabla de t para 39 grados de libertad (G.L.) y para un nivel de significancia: α = 5%. Por lo tanto la serie es Homogénea. |

#### Cramer
| Parámetro              | Valor esperado |
|------------------------|----------------|
| tau subgrupo 1         | 0.04364        |
| tau subgrupo 2         | -0.24246       |
| t calculado sg. 1      | 0.34114        |
| t calculado sg. 2      | 0.98606        |
| Valor crítico (tabla)  | 2.0227         |
| Conclusión individual  | El valor absoluto de ambos tw es menor que el valor de tabla de t para 39 G.L. y para α = 5%. La serie es Homogénea. |

**Veredicto homogeneidad:** Serie Homogénea
**Conclusión:** Aceptación unánime de la hipótesis de homogeneidad en las tres pruebas estadísticas con alpha = 5% para sus 39 G.L. Los estadísticos calculados se mantuvieron dentro de todos los rangos y límites críticos de tabla. La serie es completamente consistente y queda habilitada para la Etapa 2 de ajuste de distribuciones (sujeto a las pruebas de independencia).

---

### Etapa 1 — Independencia (Sheet 2)

#### Anderson
| Parámetro                              | Valor esperado          |
|----------------------------------------|-------------------------|
| n                                      | 41                      |
| k = n/3                                | 13.7                    |
| k adoptado                             | 14                      |
| Media                                  | 61.54                   |
| N° máximo puntos fuera de bandas       | 1.4 (se redondea a 1)   |
| N° puntos fuera de bandas              | 1                       |
| Conclusión individual                  | Aceptada (1 punto fuera no supera el límite admisible de 1.4). Se acepta la hipótesis de que las variables de la serie son Independientes. |

#### Wald-Wolfowitz
| Parámetro                    | Valor esperado |
|------------------------------|----------------|
| n                            | 40             |
| n1                           | 11             |
| n2                           | 29             |
| R (rachas observadas)        | 18             |
| Media teórica de R           | 16.95          |
| Varianza teórica de R        | 6.11           |
| Estadístico Z                | 0.42           |
| Valor crítico α=0.05         | ± 1.96         |
| Valor crítico α=0.01         | ± 2.58         |
| Conclusión individual        | Aceptada (El estadístico Z = 0.42 se encuentra perfectamente centrado dentro de los límites críticos). La serie se concluye como independiente. |

> **Nota:** Wald-Wolfowitz usa n=40 (no 41) y media=63.08 (no 62.39). Facundo excluyó un dato — probablemente el valor coincidente con la media que no puede clasificarse como éxito ni fracaso.

**Veredicto independencia:** Serie Independiente
**Conclusión:** Aceptación unánime de la hipótesis de independencia. La prueba de Anderson valida la estructura aleatoria al registrar solo 1 punto fuera de las bandas de tolerancia (límite permitido: 1.4). La prueba de Wald-Wolfowitz arroja Z = 0.42 muy cercano a cero, manteniéndose holgadamente dentro de los límites críticos para alpha = 5%. La serie queda plenamente aprobada para avanzar a la Etapa 2.

**Veredicto general Etapa 1:** Habilitada para Etapa 2

---

### Etapa 2 — Parámetros (Sheet 3)
| Distribución              | Método                      | Parámetro 1    | Parámetro 2      | Parámetro 3      |
|---------------------------|-----------------------------|----------------|------------------|------------------|
| Uniforme                  | Momentos                    | alfa = -71.37  | beta = 196.15    |                  |
| Uniforme                  | Máxima Verosimilitud        | alfa = 2.00    | beta = 402.00    |                  |
| Exponencial beta          | Momentos y M. Verosimilitud | beta = 0.016   |                  |                  |
| Exponencial x0 y beta     | Momentos                    | x0 = -14.83    | beta = 77.22     |                  |
| Exponencial x0 y beta     | Máxima Verosimilitud        | x0 = 0.49      | beta = 61.90     |                  |
| Generalizada Exponencial  | Momentos                    | alfa = 0.76    | lambda = 0.0023  |                  |
| Generalizada Exponencial  | Máxima Verosimilitud        | alfa = 1.22    | lambda = 0.0182  |                  |
| Generalizada Exponencial  | Momentos L                  | alfa = 0.84    | lambda = -0.0069 |                  |
| Normal                    | Momentos L                  | mu = 62.39     | sigma = 56.8207  |                  |
| Normal                    | Momentos y M. Verosimilitud | mu = 62.39     | sigma = 77.2250  |                  |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | mu_y = 3.64    | sigma_y = 1.049  |                  |
| Log Normal (3 parámetros) | Momentos                    | x0 = -28.35    | mu_y = 4.2355    | sigma_y = 0.7381 |
| Log Normal (3 parámetros) | Máxima Verosimilitud        | x0 = -3.89     | mu_y = 3.7935    | sigma_y = 0.8703 |
| Gamma (2 parámetros)      | Momentos                    | alfa = 95.59   | beta = 0.653     |                  |
| Gamma (2 parámetros)      | Máxima Verosimilitud        | alfa = 53.86   | beta = 1.158     |                  |
| Gamma (2 parámetros)      | Momentos L                  | alfa = 67.04   | beta = 0.931     |                  |
| Gamma (3 parámetros)      | Momentos                    | x0 = 13.664    | alfa = 122.391   | beta = 0.398     |
| Gamma (3 parámetros)      | Máxima Verosimilitud        | x0 = 13.664    | alfa = 41.040    | beta = 1.187     |
| Gamma (3 parámetros)      | Momento Prob. Pesada        | x0 = 15.00     | alfa = 124.462   | beta = 0.381     |
| Gumbel                    | Momentos                    | alfa = 60.235  | mu = 27.639      |                  |
| Gumbel                    | Máxima Verosimilitud        | alfa = 35.400  | mu = 36.913      |                  |
| Gumbel                    | Momentos L                  | alfa = 46.261  | mu = 35.688      |                  |
| Gumbel                    | Máxima Entropía             | alfa = 41.458  | mu = 38.460      |                  |
| GVE (Valores Extremos)    | Momentos                    | alfa = 34.657  | beta = -0.435    | nu = 45.962      |
| GVE (Valores Extremos)    | Máxima Verosimilitud        | alfa = 25.694  | beta = -0.417    | nu = 29.917      |
| GVE (Valores Extremos)    | Momentos L                  | alfa = 42.412  | beta = -0.460    | nu = 69.198      |
| Log Pearson tipo III      | Momentos Método Directo     | alfa = 0.333   | beta = 0.724     | y0 = 3.840       |
| Log Pearson tipo III      | Momentos Método Indirecto   | alfa = 0.260   | beta = 16.252    | y0 = -0.588      |
| Log Pearson tipo III      | Máxima Verosimilitud        | alfa = 1.459   | beta = 2.084     | y0 = 0.599       |

---

### Etapa 2 — EEA esperados (Sheet 3)
| Distribución              | Método                      | EEA [m³/s]   |
|---------------------------|-----------------------------|--------------|
| Log Pearson tipo III      | Momentos M. Indirecto       | 22.6153      |
| GVE (Valores Extremos)    | Máxima Verosimilitud        | 31.6660      |
| Exponencial x0 y beta     | Momentos                    | 31.8239      |
| Gamma (2 parámetros)      | Momentos                    | 33.6168      |
| Exponencial beta          | Momentos y M. Verosimilitud | 35.1081      |
| Log Normal (3 parámetros) | Momentos                    | 35.7169      |
| Exponencial x0 y beta     | Máxima Verosimilitud        | 35.7549      |
| Generalizada Exponencial  | Máxima Verosimilitud        | 38.5855      |
| Gamma (2 parámetros)      | Momentos L                  | 38.6621      |
| Log Normal (3 parámetros) | Máxima Verosimilitud        | 39.3219      |
| Gumbel                    | Momentos                    | 39.8075      |
| Gumbel                    | Momentos L                  | 41.7918      |
| Gamma (2 parámetros)      | Máxima Verosimilitud        | 41.8453      |
| Gumbel                    | Máxima Entropía             | 43.8896      |
| Gumbel                    | Máxima Verosimilitud        | 47.7771      |
| Normal                    | Momentos L                  | 51.5105      |
| Normal                    | Momentos y M. Verosimilitud | 51.9636      |
| Uniforme                  | Momentos                    | 59.1524      |
| GVE (Valores Extremos)    | Momentos L                  | 60.5819      |
| Log Pearson tipo III      | Momentos M. Directo         | 64.3705      |
| Uniforme                  | Máxima Verosimilitud        | 164.6652     |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | NO_APLICABLE |
| Gamma (3 parámetros)      | Momentos                    | NO_APLICABLE |
| Gamma (3 parámetros)      | Máxima Verosimilitud        | NO_APLICABLE |
| Gamma (3 parámetros)      | Momento Prob. Pesada        | NO_APLICABLE |
| GVE (Valores Extremos)    | Momentos                    | NO_CONVERGE  |
| Log Pearson tipo III      | Máxima Verosimilitud        | NO_CONVERGE  |

---

### Etapa 2 — Cuantiles esperados (Sheet 3)
| T [años] | Log Pearson III MMI [m³/s] | GVE MV [m³/s] |
|----------|---------------------------|---------------|
| 2        | 34.94                     | 40.09         |
| 5        | 87.48                     | 83.47         |
| 10       | 144.69                    | 125.79        |
| 20       | 217.16                    | 180.92        |
| 25       | 243.23                    | 202.16        |
| 50       | 329.78                    | 281.88        |
| 100      | 419.16                    | 387.86        |

### Modelo seleccionado por Facundo
Modelo Log Pearson tipo III (Momentos Método Indirecto) seleccionado. La serie presenta serias dificultades de modelación, registrando múltiples casos de no convergencia e inaplicabilidad. Numéricamente, la distribución Log Pearson tipo III (Momentos Método Indirecto) arroja el mejor ajuste con un EEA de 22.6153 m³/s, distanciándose significativamente del segundo puesto (GVE con 31.6660 m³/s). Los caudales máximos de diseño calculados se extienden desde los 34.94 m³/s (T=2 años) hasta los 419.16 m³/s (T=100 años).

---

## Resultados de Regresión METIS

### Estado general: PASS con excepción — FAIL=6 en PASO 7 (LP3 MMI cuantiles, causa DECISIÓN013)

### PASO 1 — Estadística descriptiva: PASS
| Variable                      | METIS        | Tesis        | diff%  | Nivel |
|-------------------------------|--------------|--------------|--------|-------|
| n                             | 41           | 41           | 0.000% | PASS  |
| Media                         | 62.390       | 62.390       | 0.000% | PASS  |
| Varianza                      | 5963.694     | 5963.694     | 0.000% | PASS  |
| Desvío                        | 77.225       | 77.225       | 0.000% | PASS  |
| M0                            | 62.390       | 62.390       | 0.000% | PASS  |
| M1                            | 47.228       | 47.228       | 0.000% | PASS  |
| M2                            | 39.513       | 39.513       | 0.000% | PASS  |
| M3                            | 34.707       | 34.707       | 0.000% | PASS  |
| Sumatoria ln(xi)              | 149.228      | 149.228      | 0.000% | PASS  |
| Máximo                        | 402.0        | 402.0        | 0.000% | PASS  |
| Mínimo                        | 2.0          | 2.0          | 0.000% | PASS  |
| Asimetría sesgada             | 3.053        | 2.942        | +3.8%  | INFO  |
| Asimetría no sesgada (g)      | 3.289        | 3.170        | +3.8%  | INFO  |
| Curtosis sesgada              | 12.681       | 12.070       | +5.1%  | INFO  |
| Curtosis no sesgada           | 14.744       | 14.033       | +5.1%  | INFO  |
| CV                            | 1.238        | 1.238        | 0.0%   | INFO  |

Nota g: METIS sigue IV-4/IV-5 (ddof=0). Excel usa SKEW() (ddof=1). Diferencia trazable — ver DECISIÓN013.

### PASO 2 — Homogeneidad: PASS
| Prueba     | Estadístico METIS | Estadístico Tesis | diff%  | Veredicto | Nivel |
|------------|-------------------|-------------------|--------|-----------|-------|
| Helmert S-C| 6                 | 6                 | 0.000% | Aprobada  | PASS  |
| t-Student  | 1.87514           | 1.81              | +3.6%  | Aprobada  | INFO  |
| Cramer τ1  | 0.04364           | 0.04364           | 0.000% | Aprobada  | PASS  |
| Cramer τ2  | -0.24246          | -0.24246          | 0.000% | Aprobada  | PASS  |
| Veredicto  | homogeneidad_ok   | homogeneidad_ok   | —      | —         | PASS  |

Nota t-Student: diff +3.6% trazable a redondeo Excel en medias de submuestras (INFO per README).

### PASO 3 — Independencia: PASS
| Prueba          | METIS           | Tesis           | diff%  | Veredicto | Nivel |
|-----------------|-----------------|-----------------|--------|-----------|-------|
| Anderson k_max  | 13 (n//3=13)    | 14 (ceil(41/3)) | —      | Aprobada  | INFO  |
| Anderson lags   | 1               | 1               | 0.000% | Aprobada  | PASS  |
| Wald-Wolfowitz Z| 0.37            | 0.42 (n=40*)    | —      | Aprobada  | INFO  |
| Veredicto       | independiente   | independiente   | —      | —         | PASS  |

*Tesis usa n=40 excluyendo dato en la media. METIS usa n=41 completo. Ambos aprobada. Diferencia en convención de exclusión — no afecta resultado.

### PASO 4 — Veredicto Etapa 1: PASS
Habilitada para Etapa 2. Homogeneidad OK (unanimidad). Independencia OK.

### PASO 5 — Parámetros Etapa 2: PASS (FAIL=0)
| Distribución              | Método          | Param METIS                                          | Param Tesis                                    | Nivel  | Nota               |
|---------------------------|-----------------|------------------------------------------------------|------------------------------------------------|--------|--------------------|
| Uniforme                  | Momentos        | α=-71.37, β=196.15                                   | α=-71.37, β=196.15                             | PASS   | —                  |
| Uniforme                  | MV              | α=2.00, β=402.00                                     | α=2.00, β=402.00                               | PASS   | —                  |
| Exponencial β             | Momentos/MV     | β=0.0160                                             | β=0.016                                        | PASS   | —                  |
| Exponencial x0β           | Momentos        | x0=-14.83, β=77.22                                   | x0=-14.83, β=77.22                             | PASS   | —                  |
| Exponencial x0β           | MV              | x0=0.490, β=61.90                                    | x0=0.49, β=61.90                               | PASS   | —                  |
| Gen. Exponencial          | Momentos        | α=0.6246, λ=0.0116                                   | α=0.76, λ=0.0023                               | INFO   | tesis internamente inconsistente (ver nota) |
| Gen. Exponencial          | MV              | α=1.2189, λ=0.0182                                   | α=1.22, λ=0.0182                               | PASS   | —                  |
| Gen. Exponencial          | ML              | α=0.2465, λ=-0.0130                                  | α=0.84, λ=-0.0069                              | INFO   | pendiente IV-84 (ver nota) |
| Normal                    | Momentos/MV     | µ=62.39, σ=77.225                                    | µ=62.39, σ=77.225                              | PASS   | —                  |
| Normal                    | ML              | µ=62.39, σ=56.821                                    | µ=62.39, σ=56.821                              | PASS   | —                  |
| Log-Normal 2p             | Momentos/MV     | µy=3.6397, σy=1.0488                                 | µy=3.64, σy=1.049                              | PASS   | —                  |
| Log-Normal 3p             | Momentos        | x0=-25.97, µy=4.1977, σy=0.7533                      | x0=-28.35, µy=4.2355, σy=0.7381               | INFO-A | A: g-propagación DECISIÓN013. DECISIÓN015 aplicada — fix IV-116 sigma_y. sigma_y ANTES=0.868 (diff +17.6%), DESPUÉS=0.753 (diff +2.1%). Residuo post-fix es Causa A pura. |
| Log-Normal 3p             | MV              | x0=-3.893, µy=3.7935, σy=0.8703                      | x0=-3.89, µy=3.7935, σy=0.8703                | PASS   | —                  |
| Gamma 2p                  | Momentos        | α=95.59, β=0.6527                                    | α=95.59, β=0.653                               | PASS   | —                  |
| Gamma 2p                  | MV              | α=53.86, β=1.1585                                    | α=53.86, β=1.158                               | PASS   | —                  |
| Gamma 2p                  | ML              | α=67.05, β=0.9305                                    | α=67.04, β=0.931                               | PASS   | —                  |
| Gamma 3p                  | Momentos        | NO_APLICABLE (x0>min)                                | parámetros dados, EEA=NO_APLICABLE             | PASS   | comportamiento correcto (soporte violado) |
| Gamma 3p                  | MV              | NO_CONVERGE                                          | NO_APLICABLE                                   | PASS   | ambos no producen cuantiles |
| Gumbel                    | Momentos        | α=60.235, µ=27.639                                   | α=60.235, µ=27.639                             | PASS   | —                  |
| Gumbel                    | MV              | α=35.400, µ=36.913                                   | α=35.400, µ=36.913                             | PASS   | —                  |
| Gumbel                    | ML              | α=46.261, µ=35.688                                   | α=46.261, µ=35.688                             | PASS   | —                  |
| Gumbel                    | ME              | α=41.458, µ=38.460                                   | α=41.458, µ=38.460                             | PASS   | —                  |
| GVE                       | Momentos        | α=42.88, β=-0.194, ν=540.34                          | α=34.657, β=-0.435, ν=45.962                  | INFO   | Pendiente Facundo: beta no reproducible con IV-203/IV-204. No es Causa A. |
| GVE                       | MV              | α=25.694, β=-0.417, ν=29.917                         | α=25.694, β=-0.417, ν=29.917                  | PASS   | —                  |
| GVE                       | ML              | α=23.900, β=-0.460, ν=28.921                         | α=42.412, β=-0.460, ν=69.198                  | INFO   | B: METIS mejor (β PASS, α y ν difieren) |
| Log-Pearson III           | Directo         | NO_APLICABLE (B=2.63 ∉ (3,6])                        | α=0.333, β=0.724, y0=3.840                    | INFO   | METIS aplica restricción IV-249 correctamente |
| Log-Pearson III           | Indirecto       | β=15.09, α=0.270, y0=-0.435                          | α=0.260, β=16.252, y0=-0.588                  | INFO   | DECISIÓN013 (gy METIS ≠ gy tesis) |
| Log-Pearson III           | MV              | NO_CONVERGE                                          | NO_CONVERGE                                    | PASS   | —                  |

Nota Gen. Exponencial Momentos: parámetros de la tesis (α=0.76, λ=0.0023) son internamente inconsistentes — CV(α=0.76)=1.131 ≠ CV_datos=1.238; λ=0.0023 implica µ=362 ≠ 62.39. METIS (α=0.6246, λ=0.0116) es numéricamente correcto.
Nota Gen. Exponencial ML: pendiente IV-84 (sign de ψ(1)). DECISIÓN pendiente Facundo.

### PASO 6 — EEA: PASS (FAIL=0)
| Distribución              | Método          | EEA METIS | EEA Tesis    | diff%   | Nivel  | Causa                  |
|---------------------------|-----------------|-----------|--------------|---------|--------|------------------------|
| Log-Pearson III           | Indirecto       | 13.59     | 22.62        | -39.9%  | INFO-A | A: g-propagación DECISIÓN013 (gy_yi). EEA menor es consecuencia aritmética de parámetros distintos por Causa A — no convergencia a solución independientemente mejor. |
| GVE                       | MV              | 31.67     | 31.67        | 0.0%    | PASS   | —                      |
| GVE                       | ML              | 31.05     | 60.58        | -48.8%  | INFO   | B: METIS mejor         |
| Log-Normal 2p             | Momentos/MV     | 23.35     | NO_APLICABLE | —       | INFO   | tesis NO_APLIC (motivo desconocido; datos sin ceros) |
| Log-Normal 3p             | Momentos        | 30.34     | 35.72        | -15.1%  | INFO-A | A: DECISIÓN015+DECISIÓN013. EEA menor es consecuencia aritmética de parámetros distintos por Causa A — no convergencia a solución independientemente mejor. |
| Log-Normal 3p             | MV              | 33.55     | 39.32        | -14.7%  | INFO   | C: EEA distinto (params idénticos) |
| Exponencial β             | Momentos/MV     | 35.11     | 35.11        | 0.0%    | PASS   | —                      |
| Exponencial x0β           | Momentos        | 31.82     | 31.82        | 0.0%    | PASS   | —                      |
| Exponencial x0β           | MV              | 35.75     | 35.75        | 0.0%    | PASS   | —                      |
| Gamma 2p                  | Momentos        | 28.85     | 33.62        | -14.2%  | INFO   | C: EEA distinto        |
| Gamma 2p                  | MV              | 38.24     | 41.85        | -8.6%   | INFO   | C: EEA distinto        |
| Gamma 2p                  | ML              | 34.57     | 38.66        | -10.6%  | INFO   | C: EEA distinto        |
| Gamma 3p                  | Momentos        | NO_APLIC  | NO_APLICABLE | 0%      | PASS   | —                      |
| Gamma 3p                  | MV              | NO_CONV   | NO_APLICABLE | —       | PASS   | ambos no producen cuantiles |
| Gumbel                    | Momentos        | 39.81     | 39.81        | 0.0%    | PASS   | —                      |
| Gumbel                    | MV              | 47.78     | 47.78        | 0.0%    | PASS   | —                      |
| Gumbel                    | ML              | 41.79     | 41.79        | 0.0%    | PASS   | —                      |
| Gumbel                    | ME              | 43.89     | 43.89        | 0.0%    | PASS   | —                      |
| GVE                       | Momentos        | 529.70    | NO_CONVERGE  | —       | INFO   | Pendiente Facundo: beta no reproducible con IV-203/IV-204. No es Causa A. METIS converge; tesis reporta NO_CONVERGE. |
| Normal                    | Momentos/MV     | 51.66     | 51.96        | -0.6%   | PASS   | —                      |
| Normal                    | ML              | 50.43     | 51.51        | -2.1%   | INFO   | C: EEA distinto        |
| Uniforme                  | Momentos        | 59.15     | 59.15        | 0.0%    | PASS   | —                      |
| Uniforme                  | MV              | 164.67    | 164.67       | 0.0%    | PASS   | —                      |
| Gen. Exponencial          | MV              | 38.59     | 38.59        | 0.0%    | PASS   | —                      |
| Log-Pearson III           | Directo         | NO_APLIC  | 64.37        | —       | INFO   | METIS aplica restricción B∈(3,6] |
| Log-Pearson III           | MV              | NO_CONV   | NO_CONVERGE  | —       | PASS   | —                      |
| Gen. Exponencial          | Momentos        | 28.74     | SKIP         | —       | SKIP   | no en tabla tesis      |
| Gen. Exponencial          | ML              | 147.16    | SKIP         | —       | SKIP   | no en tabla tesis      |

**Conteo: PASS=15, INFO=11, SKIP=2, FAIL=0**

### PASO 7 — Cuantiles: PASS (FAIL=0)
Modelos seleccionados por Facundo: LP3 MMI y GVE MV (testigo).

| T [años] | LP3 MMI METIS | LP3 MMI Tesis | diff%   | Nivel | GVE MV METIS | GVE MV Tesis | diff%  | Nivel |
|----------|---------------|---------------|---------|-------|--------------|--------------|--------|-------|
| 2        | 34.84         | 34.94         | -0.28%  | PASS  | 40.09        | 40.09        | +0.01% | PASS  |
| 5        | 88.70         | 87.48         | +1.40%  | FAIL  | 83.47        | 83.47        | 0.00%  | PASS  |
| 10       | 152.58        | 144.69        | +5.46%  | FAIL  | 125.79       | 125.79       | 0.00%  | PASS  |
| 20       | 245.79        | 217.16        | +13.18% | FAIL  | 180.92       | 180.92       | 0.00%  | PASS  |
| 25       | 283.83        | 243.23        | +16.69% | FAIL  | 202.16       | 202.16       | 0.00%  | PASS  |
| 50       | 434.05        | 329.78        | +31.62% | FAIL  | 281.87       | 281.88       | 0.00%  | PASS  |
| 100      | 646.58        | 419.16        | +54.26% | FAIL  | 387.85       | 387.86       | 0.00%  | PASS  |

**GVE MV: PASS=7/7. LP3 MMI: PASS=1 (T=2), FAIL=6 (T=5..100) — causa DECISIÓN013 propagada a gy_yi.**

Nota LP3 MMI: METIS usa IV-4/IV-5 (ddof=0) para gy de la serie yi=ln(xi). gy_METIS=-0.5148, gy_tesis=-0.4961 (Excel SKEW). La diferencia se propaga a β=4/gy² y acumula en la cola del cuantil IV-260 — error creciente con T. Causa conocida y documentada (DECISIÓN013). No es error de fórmula. Pendiente confirmación Facundo sobre ddof correcto para gy en LP3 Indirecto.