## Estación 4 — Las Tapias – Río Las Tapias

### Serie (Sheet 1)
```python
serie = [
    12.0,   # 42-43
    100.0,  # 43-44
    12.0,   # 44-45
    10.0,   # 45-46
    32.0,   # 46-47
    32.0,   # 47-48
    18.0,   # 48-49
    42.0,   # 49-50
    29.0,   # 50-51
    3.0,    # 51-52
    57.0,   # 52-53
    10.0,   # 53-54
    50.0,   # 54-55
    10.0,   # 55-56
    40.0,   # 56-57
    36.0,   # 57-58
    20.0,   # 58-59
    16.0,   # 59-60
    10.0,   # 60-61
    31.0,   # 61-62
    7.0,    # 62-63
    9.0,    # 63-64
    18.0,   # 64-65
    10.0,   # 65-66
    38.0,   # 66-67
    # 67-68: S/D - Interrupción
    4.0,    # 68-69
    23.0,   # 69-70
    12.0,   # 70-71
    16.0,   # 71-72
    48.0,   # 72-73
    # 73-74: S/D - Interrupción
    23.0,   # 74-75
    2.0,    # 75-76
    11.0,   # 76-77
    45.0,   # 77-78
    21.0,   # 78-79
    8.0,    # 79-80
]
# n=36 (38 años calendario, 2 interrupciones: 67-68 y 73-74)
```

### Estadística descriptiva esperada (Sheet 1)
| Variable                        | Valor esperado |
|---------------------------------|----------------|
| n                               | 36             |
| Media [m³/s]                    | 24.028         |
| Varianza [m³/s]²                | 388.085        |
| Desvío [m³/s]                   | 19.7           |
| Asimetría Sesgada               | 1.698          |
| Asimetría No Sesgada (g)        | 1.849          |
| Curtosis Sesgada                | 6.788          |
| Curtosis No Sesgada (k)         | 8.064          |
| Coeficiente de Variación (CV)   | 0.82           |
| Sumatoria ln(xi)                | 103.022        |
| beta_0 = M0                     | 24.028         |
| beta_1 = M1                     | 17.088         |
| beta_2 = M2                     | 13.604         |
| beta_3 = M3                     | 11.434         |
| Máximo [m³/s]                   | 100.0          |
| Mínimo [m³/s]                   | 2.0            |

---

### Etapa 1 — Homogeneidad (Sheet 2)

#### Helmert
| Parámetro              | Valor esperado |
|------------------------|----------------|
| N° de Series (S)       | 15             |
| N° de Cambios (C)      | 20             |
| Estadístico (S-C)      | -5             |
| n                      | 36             |
| Umbral inferior        | -5.92          |
| Umbral superior        | 5.92           |
| Conclusión individual  | El estadístico (S - C) está comprendido entre -(nj-1)^0.5 y +(nj-1)^0.5. Por lo tanto la serie es Homogénea. |

#### t de Student
| Parámetro              | Valor esperado |
|------------------------|----------------|
| Estadístico t          | 1.63           |
| Grados de libertad     | 34             |
| Valor crítico (tabla)  | 2.0322         |
| Conclusión individual  | El valor absoluto del estadístico t es menor que el valor de tabla de t para 34 grados de libertad (G.L.) y para un nivel de significancia: α = 5%. Por lo tanto la serie es Homogénea. |

#### Cramer
| Parámetro              | Valor esperado |
|------------------------|----------------|
| tau subgrupo 1         | -0.186         |
| tau subgrupo 2         | -0.23676       |
| t calculado sg. 1      | 1.39809        |
| t calculado sg. 2      | 0.92725        |
| Valor crítico (tabla)  | 2.0322         |
| Conclusión individual  | El valor absoluto de ambos tw es menor que el valor de tabla de t para 34 G.L. y para α = 5%. La serie es Homogénea. |

**Veredicto homogeneidad:** Serie Homogénea
**Conclusión:** Aceptación unánime de la hipótesis de homogeneidad en las tres pruebas estadísticas con alpha = 5% para sus 34 G.L. Los estadísticos calculados se mantuvieron dentro de todos los rangos y límites críticos de tabla. La serie es completamente consistente y queda habilitada para la Etapa 2 de ajuste de distribuciones (sujeto a las pruebas de independencia).

---

### Etapa 1 — Independencia (Sheet 2)

#### Anderson
| Parámetro                              | Valor esperado              |
|----------------------------------------|-----------------------------|
| n                                      | 36                          |
| k = n/3                                | 12.0                        |
| k adoptado                             | 12                          |
| Media                                  | 24.03                       |
| N° máximo puntos fuera de bandas       | 1.2 (se redondea a 1)       |
| N° puntos fuera de bandas              | 0                           |
| Conclusión individual                  | Aceptada (0 puntos fuera, comportamiento ideal). Se acepta la hipótesis de que las variables de la serie son Independientes. |

#### Wald-Wolfowitz
| Parámetro                    | Valor esperado        |
|------------------------------|-----------------------|
| n                            | 36                    |
| n1                           | 13                    |
| n2                           | 23                    |
| R (rachas observadas)        | 21                    |
| Media teórica de R           | 17.61                 |
| Varianza teórica de R        | 7.41                  |
| Estadístico Z                | 1.25                  |
| Valor crítico α=0.05         | ± 1.96                |
| Valor crítico α=0.01         | No indica para α = 1% |
| Conclusión individual        | Aceptada (Z=1.25 no supera los valores críticos de tabla para α=5%). La serie se concluye como independiente. |

**Veredicto independencia:** Serie Independiente
**Conclusión:** Aceptación unánime de la hipótesis de independencia. La prueba de Anderson muestra un comportamiento ideal con 0 puntos fuera de las bandas de tolerancia. Por su parte, el test de Wald-Wolfowitz confirma la aleatoriedad de la serie con Z=1.25 que no supera los valores críticos de tabla para α=5%. La serie queda plenamente habilitada para la Etapa 2 de ajuste de distribuciones.

**Veredicto general Etapa 1:** Habilitada para Etapa 2

---

### Etapa 2 — Parámetros (Sheet 3)
| Distribución              | Método                      | Parámetro 1     | Parámetro 2      | Parámetro 3      |
|---------------------------|-----------------------------|-----------------|------------------|------------------|
| Uniforme                  | Momentos                    | alfa = -10.09   | beta = 58.15     |                  |
| Uniforme                  | Máxima Verosimilitud        | alfa = 2.00     | beta = 100.00    |                  |
| Exponencial beta          | Momentos y M. Verosimilitud | beta = 0.042    |                  |                  |
| Exponencial x0 y beta     | Momentos                    | x0 = 4.33       | beta = 19.70     |                  |
| Exponencial x0 y beta     | Máxima Verosimilitud        | x0 = 1.37       | beta = 22.66     |                  |
| Generalizada Exponencial  | Momentos                    | alfa = 1.24     | lambda = 0.0356  |                  |
| Generalizada Exponencial  | Máxima Verosimilitud        | alfa = 1.84     | lambda = 0.0599  |                  |
| Generalizada Exponencial  | Momentos L                  | alfa = 0.80     | lambda = -0.00013|                  |
| Normal                    | Momentos L                  | mu = 24.03      | sigma = 17.9830  |                  |
| Normal                    | Momentos y M. Verosimilitud | mu = 24.03      | sigma = 19.6999  |                  |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | mu_y = 2.86     | sigma_y = 0.856  |                  |
| Log Normal (3 parámetros) | Momentos                    | x0 = -1.25      | mu_y = 3.4275    | sigma_y = 0.5210 |
| Log Normal (3 parámetros) | Máxima Verosimilitud        | x0 = -1.93      | mu_y = 3.0031    | sigma_y = 0.7266 |
| Gamma (2 parámetros)      | Momentos                    | alfa = 16.15    | beta = 1.488     |                  |
| Gamma (2 parámetros)      | Máxima Verosimilitud        | alfa = 13.91    | beta = 1.727     |                  |
| Gamma (2 parámetros)      | Momentos L                  | alfa = 15.84    | beta = 1.517     |                  |
| Gamma (3 parámetros)      | Momentos                    | x0 = 2.724      | alfa = 18.217    | beta = 1.169     |
| Gamma (3 parámetros)      | Máxima Verosimilitud        | x0 = 1.740      | alfa = 17.408    | beta = 1.280     |
| Gamma (3 parámetros)      | Momento Prob. Pesada        | x0 = 2.307      | alfa = 20.545    | beta = 1.057     |
| Gumbel                    | Momentos                    | alfa = 15.366   | mu = 15.163      |                  |
| Gumbel                    | Máxima Verosimilitud        | alfa = 12.648   | mu = 15.953      |                  |
| Gumbel                    | Momentos L                  | alfa = 14.641   | mu = 15.577      |                  |
| Gumbel                    | Máxima Entropía             | alfa = 13.484   | mu = 16.244      |                  |
| GVE (Valores Extremos)    | Momentos                    | alfa = 15.548   | beta = -0.210    | nu = 25.124      |
| GVE (Valores Extremos)    | Máxima Verosimilitud        | alfa = 10.61    | beta = -0.312    | nu = 13.995      |
| GVE (Valores Extremos)    | Momentos L                  | alfa = 14.711   | beta = -0.205    | nu = 29.325      |
| Log Pearson tipo III      | Momentos Método Directo     | alfa = 0.333    | beta = 0.398     | y0 = 3.018       |
| Log Pearson tipo III      | Momentos Método Indirecto   | alfa = 0.180    | beta = 22.708    | y0 = -1.217      |
| Log Pearson tipo III      | Máxima Verosimilitud        | NO_CONVERGE     | NO_CONVERGE      | NO_CONVERGE      |

---

### Etapa 2 — EEA esperados (Sheet 3)
| Distribución              | Método                      | EEA [m³/s]   |
|---------------------------|-----------------------------|--------------|
| GVE (Valores Extremos)    | Máxima Verosimilitud        | 3.9893       |
| Log Pearson tipo III      | Momentos M. Indirecto       | 4.1405       |
| Exponencial x0 y beta     | Máxima Verosimilitud        | 4.2425       |
| Exponencial beta          | Momentos y M. Verosimilitud | 4.4501       |
| Exponencial x0 y beta     | Momentos                    | 4.7691       |
| Gamma (3 parámetros)      | Momento Prob. Pesada        | 5.3833       |
| Generalizada Exponencial  | Máxima Verosimilitud        | 5.4460       |
| Log Normal (3 parámetros) | Máxima Verosimilitud        | 5.5651       |
| Gumbel                    | Momentos                    | 5.7690       |
| Gamma (2 parámetros)      | Momentos                    | 5.8610       |
| Gamma (3 parámetros)      | Momentos                    | 5.9123       |
| Gamma (3 parámetros)      | Máxima Verosimilitud        | 5.9155       |
| Gamma (2 parámetros)      | Momentos L                  | 5.9428       |
| Gumbel                    | Momentos L                  | 6.0139       |
| Log Normal (3 parámetros) | Momentos                    | 6.1954       |
| Gamma (2 parámetros)      | Máxima Verosimilitud        | 6.5165       |
| Gumbel                    | Máxima Entropía             | 6.6116       |
| Gumbel                    | Máxima Verosimilitud        | 7.2679       |
| Normal                    | Momentos y M. Verosimilitud | 8.6648       |
| Normal                    | Momentos L                  | 8.8456       |
| Uniforme                  | Momentos                    | 9.7236       |
| Log Pearson tipo III      | Momentos M. Directo         | 16.4899      |
| GVE (Valores Extremos)    | Momentos L                  | 17.2659      |
| Uniforme                  | Máxima Verosimilitud        | 31.2294      |
| GVE (Valores Extremos)    | Momentos                    | 36.2597      |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | NO_APLICABLE |
| Log Pearson tipo III      | Máxima Verosimilitud        | NO_CONVERGE  |

---

### Etapa 2 — Cuantiles esperados (Sheet 3)
| T [años] | Log Pearson III MMI [m³/s] | GVE MV [m³/s] |
|----------|---------------------------|---------------|
| 2        | 18.11                     | 16.48         |
| 5        | 34.29                     | 34.68         |
| 10       | 48.61                     | 51.85         |
| 20       | 65.88                     | 71.55         |
| 25       | 72.22                     | 78.25         |
| 50       | 94.84                     | 99.44         |
| 100      | 122.78                    | 120.01        |

### Modelo seleccionado por Facundo
Modelo Log Pearson tipo III (Momentos Método Indirecto) seleccionado. Aunque el modelo GVE por máxima verosimilitud arroja el indicador numérico más bajo (EEA=3.9893 m³/s), la verificación visual y el análisis gráfico determinan que la distribución Log Pearson tipo III (Momentos Método Indirecto, EEA=4.1405 m³/s) logra una reproducción más fiel y consistente de los extremos hidrológicos observados de la serie. Los caudales máximos de diseño varían de 18.11 m³/s para eventos bianuales hasta 122.78 m³/s para una recurrencia de 100 años.

---

## Resultados de Regresión METIS --> UNITARIAS

### Estado general: PASS† — FAIL=0 en todos los pasos
†Cuantiles del modelo seleccionado (LP3 MMI) no verificables por error en tabla de referencia de la tesis — columna LP3 MMI contiene cuantiles GVE MV. GVE MV verificado PASS=7/7. Ver pendientes-facundo.md.

### PASO 1 — Estadística descriptiva: PASS
| Variable                      | METIS        | Tesis        | diff%  | Nivel |
|-------------------------------|--------------|--------------|--------|-------|
| n                             | 36           | 36           | 0.000% | PASS  |
| Media                         | 24.028       | 24.028       | 0.000% | PASS  |
| Varianza                      | 388.085      | 388.085      | 0.000% | PASS  |
| Desvío                        | 19.700       | 19.7         | 0.000% | PASS  |
| M0                            | 24.028       | 24.028       | 0.000% | PASS  |
| M1                            | 17.088       | 17.088       | 0.000% | PASS  |
| M2                            | 13.604       | 13.604       | 0.000% | PASS  |
| M3                            | 11.434       | 11.434       | 0.000% | PASS  |
| Sumatoria ln(xi)              | 103.022      | 103.022      | 0.000% | PASS  |
| Máximo                        | 100.0        | 100.0        | 0.000% | PASS  |
| Mínimo                        | 2.0          | 2.0          | 0.000% | PASS  |
| Asimetría sesgada             | 1.771        | 1.698        | +4.3%  | INFO  |
| Asimetría no sesgada (g)      | 1.929        | 1.849        | +4.3%  | INFO  |
| Curtosis sesgada              | 7.181        | 6.788        | +5.8%  | INFO  |
| Curtosis no sesgada           | 8.532        | 8.064        | +5.8%  | INFO  |
| CV                            | 0.820        | 0.82         | 0.0%   | INFO  |

Nota g: METIS sigue IV-4/IV-5 (ddof=0). Excel usa SKEW() (ddof=1). Diferencia trazable — ver DECISIÓN013.

### PASO 2 — Homogeneidad: PASS
| Prueba     | Estadístico METIS | Estadístico Tesis | diff%  | Veredicto | Nivel |
|------------|-------------------|-------------------|--------|-----------|-------|
| Helmert S-C| -5                | -5                | 0.000% | Aprobada  | PASS  |
| t-Student  | 1.6272            | 1.63              | +0.1%  | Aprobada  | PASS  |
| Cramer τ1  | -0.18600          | -0.186            | 0.000% | Aprobada  | PASS  |
| Cramer τ2  | -0.23676          | -0.23676          | 0.000% | Aprobada  | PASS  |
| Veredicto  | homogeneidad_ok   | homogeneidad_ok   | —      | —         | PASS  |

Nota t-Student: usa partición mitad/mitad (n1=18, n2=18, GL=34). diff +0.1% trazable a redondeo en medias (INFO per README).

### PASO 3 — Independencia: PASS
| Prueba          | METIS           | Tesis           | diff%  | Veredicto | Nivel |
|-----------------|-----------------|-----------------|--------|-----------|-------|
| Anderson lags   | 0 fuera         | 0 fuera         | 0.000% | Aprobada  | PASS  |
| Wald-Wolfowitz Z| 1.25            | 1.25            | 0.000% | Aprobada  | PASS  |
| Veredicto       | independiente   | independiente   | —      | —         | PASS  |

Nota Wald: n=36 ≤ 40 → TEST_WARNING_SMALL_SAMPLE emitido (esperado, no bloquea).

### PASO 4 — Veredicto Etapa 1: PASS
Habilitada para Etapa 2. Homogeneidad OK (unanimidad). Independencia OK.

### PASO 5 — Parámetros Etapa 2: PASS (FAIL=0)
| Distribución              | Método          | Param METIS                                          | Param Tesis                                    | Nivel  | Nota               |
|---------------------------|-----------------|------------------------------------------------------|------------------------------------------------|--------|--------------------|
| Uniforme                  | Momentos        | α=-10.0934, β=58.1490                                | α=-10.09, β=58.15                              | PASS   | —                  |
| Uniforme                  | MV              | α=2.0000, β=100.0000                                 | α=2.00, β=100.00                               | PASS   | —                  |
| Exponencial β             | Momentos/MV     | β=0.0416                                             | β=0.042                                        | PASS   | —                  |
| Exponencial x0β           | Momentos        | x0=4.3279, β=19.6999                                 | x0=4.33, β=19.70                               | PASS   | —                  |
| Exponencial x0β           | MV              | x0=1.3706, β=22.6571                                 | x0=1.37, β=22.66                               | PASS   | —                  |
| Gen. Exponencial          | Momentos        | α=1.5857, λ=0.0550                                   | α=1.24, λ=0.0356                               | INFO   | tesis internamente inconsistente: CV(α=1.24)=0.910 ≠ CV_datos=0.820; METIS correcto (ver nota) |
| Gen. Exponencial          | MV              | α=1.8413, λ=0.0599                                   | α=1.84, λ=0.0599                               | PASS   | —                  |
| Gen. Exponencial          | ML              | α=0.3218, λ=-0.0300                                  | α=0.80, λ=-0.00013                             | INFO   | pendiente IV-84 (signo ψ(1)), mismo caso que est_03 |
| Normal                    | Momentos/MV     | µ=24.0278, σ=19.6999                                 | µ=24.03, σ=19.6999                             | PASS   | —                  |
| Normal                    | ML              | µ=24.0278, σ=17.9830                                 | µ=24.03, σ=17.9830                             | PASS   | —                  |
| Log-Normal 2p             | Momentos/MV     | µy=2.8617, σy=0.8559                                 | µy=2.86, σy=0.856                              | PASS   | —                  |
| Log-Normal 3p             | Momentos        | x0=-10.023, µy=3.3835, σy=0.5373                     | x0=-1.25*, µy=3.4275, σy=0.5210               | INFO-A | *x0=-1.25 es typo en tesis (correcto≈-11.26, METIS=-10.02, diff~11% Causa A). µy diff=1.3%, σy diff=3.1%: Causa A g-propagación DECISIÓN013. |
| Log-Normal 3p             | MV              | x0=-1.9285, µy=3.0031, σy=0.7266                     | x0=-1.93, µy=3.0031, σy=0.7266                | PASS   | —                  |
| Gamma (2 parámetros)      | Momentos        | α=16.1515, β=1.4876                                  | α=16.15, β=1.488                               | PASS   | —                  |
| Gamma (2 parámetros)      | MV              | α=13.9143, β=1.7268                                  | α=13.91, β=1.727                               | PASS   | —                  |
| Gamma (2 parámetros)      | ML              | α=15.8352, β=1.5174                                  | α=15.84, β=1.517                               | PASS   | —                  |
| Gamma (3 parámetros)      | Momentos        | NO_APLICABLE (x0=2.724 > min=2.0)                    | x0=2.724, α=18.217, β=1.169                   | INFO   | tesis reporta params pero EEA=NO_APLICABLE; METIS no_aplic desde parámetros (pendiente Facundo) |
| Gamma (3 parámetros)      | MV              | NO_CONVERGE                                          | x0=1.740, α=17.408, β=1.280                   | INFO   | scan bug: root en x0≈1.74 dentro del primer intervalo (deferred) |
| Gamma (3 parámetros)      | MPP             | EXCLUIDO                                             | x0=2.307, α=20.545, β=1.057                   | EXCLUIDO | Cap. IV no desarrolla ecuaciones MPP |
| Gumbel                    | Momentos        | µ=15.1628, α=15.3659                                 | α=15.366, µ=15.163                             | PASS   | —                  |
| Gumbel                    | MV              | µ=15.9532, α=12.6476                                 | α=12.648, µ=15.953                             | PASS   | —                  |
| Gumbel                    | ML              | µ=15.5767, α=14.6411                                 | α=14.641, µ=15.577                             | PASS   | —                  |
| Gumbel                    | ME              | µ=16.2443, α=13.4845                                 | α=13.484, µ=16.244                             | PASS   | —                  |
| GVE                       | Momentos        | ν=298.10, α=13.2101, β=-0.0997                       | α=15.548, β=-0.210, ν=25.124                  | INFO   | Pendiente Facundo: beta no reproducible con IV-203/IV-204. No es Causa A. |
| GVE                       | MV              | ν=13.9953, α=10.6102, β=-0.3118                      | α=10.61, β=-0.312, ν=13.995                   | PASS   | —                  |
| GVE                       | ML              | ν=14.3760, α=11.6484, β=-0.2049                      | α=14.711, β=-0.205, ν=29.325                  | INFO   | B: β PASS (diff=0.2%), α/ν difieren (Causa B — convergencia distinta) |
| Log-Pearson III           | Directo         | NO_APLICABLE (B=2.70 ∉ (3,6])                        | α=0.333, β=0.398, y0=3.018                    | INFO   | METIS aplica restricción IV-249 correctamente |
| Log-Pearson III           | Indirecto       | β=20.8677, α=0.1874, y0=-1.0482                      | α=0.180, β=22.708, y0=-1.217                  | INFO-A | DECISIÓN013: gy_yi usa ddof=0 vs Excel SKEW() |
| Log-Pearson III           | MV              | NO_CONVERGE                                          | NO_CONVERGE                                    | PASS   | —                  |

Nota Gen. Exponencial Momentos: METIS (α=1.5857, λ=0.0550) es internamente consistente — CV(α=1.5857)=0.820=CV_datos ✓; µ_teórico(α=1.5857, λ=0.0550)=24.03=µ_datos ✓. Tesis (α=1.24, λ=0.0356): CV(α=1.24)=0.910≠CV_datos=0.820. Mismo patrón que est_03 — parámetros de tesis internamente inconsistentes.
Nota Gen. Exponencial ML: pendiente IV-84 (signo de ψ(1)). DECISIÓN pendiente Facundo.
Nota Gen. Pareto: no listada en tabla de parámetros de tesis est_04 — todos los métodos SKIP.

### PASO 6 — EEA: PASS (FAIL=0)
| Distribución              | Método          | EEA METIS | EEA Tesis    | diff%   | Nivel  | Causa                  |
|---------------------------|-----------------|-----------|--------------|---------|--------|------------------------|
| GVE                       | MV              | 3.9893    | 3.9893       | 0.0%    | PASS   | —                      |
| LP3                       | Indirecto       | 4.8532    | 4.1405       | +17.2%  | INFO-A | A: g-propagación DECISIÓN013 (gy_yi). EEA mayor es consecuencia aritmética de parámetros distintos por Causa A. |
| Exponencial x0β           | MV              | 4.2425    | 4.2425       | 0.0%    | PASS   | —                      |
| Exponencial β             | Momentos/MV     | 4.4501    | 4.4501       | 0.0%    | PASS   | —                      |
| Exponencial x0β           | Momentos        | 4.7691    | 4.7691       | 0.0%    | PASS   | —                      |
| Gamma (3 parámetros)      | MPP             | EXCLUIDO  | 5.3833       | —       | EXCLUIDO | Cap. IV no desarrolla ecuaciones |
| Gen. Exponencial          | MV              | 5.4460    | 5.4460       | 0.0%    | PASS   | —                      |
| Log-Normal 3p             | MV              | 4.3426    | 5.5651       | -21.9%  | INFO-C | C: EEA distinto con params idénticos (pendiente Facundo) |
| Gumbel                    | Momentos        | 5.7690    | 5.7690       | 0.0%    | PASS   | —                      |
| Gamma (2 parámetros)      | Momentos        | 4.9299    | 5.8610       | -15.9%  | INFO-C | C: EEA distinto con params idénticos |
| Gamma (3 parámetros)      | Momentos        | NO_APLIC  | 5.9123       | —       | INFO   | METIS no_aplic (x0>min); tesis tiene EEA |
| Gamma (3 parámetros)      | MV              | NO_CONV   | 5.9155       | —       | INFO   | scan bug deferred       |
| Gamma (2 parámetros)      | ML              | 5.0101    | 5.9428       | -15.7%  | INFO-C | C: EEA distinto con params idénticos |
| Gumbel                    | ML              | 6.0139    | 6.0139       | 0.0%    | PASS   | —                      |
| Log-Normal 3p             | Momentos        | 5.1530    | 6.1954       | -16.8%  | INFO-A | A: g-propagación DECISIÓN013+DECISIÓN015. EEA menor es consecuencia aritmética. |
| Gamma (2 parámetros)      | MV              | 5.5989    | 6.5165       | -14.1%  | INFO-C | C: EEA distinto con params idénticos |
| Gumbel                    | ME              | 6.6116    | 6.6116       | 0.0%    | PASS   | —                      |
| Gumbel                    | MV              | 7.2679    | 7.2679       | 0.0%    | PASS   | —                      |
| Normal                    | Momentos/MV     | 8.5216    | 8.6648       | -1.7%   | INFO-C | C: EEA distinto con params idénticos |
| Normal                    | ML              | 8.5897    | 8.8456       | -2.9%   | INFO-C | C: EEA distinto con params idénticos |
| Uniforme                  | Momentos        | 9.7236    | 9.7236       | 0.0%    | PASS   | —                      |
| LP3                       | Directo         | NO_APLIC  | 16.4899      | —       | INFO   | METIS aplica restricción B∈(3,6]    |
| GVE                       | ML              | 4.8125    | 17.2659      | -72.1%  | INFO-B | B: convergencia a óptimo distinto (β≈PASS, α/ν difieren) |
| Uniforme                  | MV              | 31.2294   | 31.2294      | 0.0%    | PASS   | —                      |
| GVE                       | Momentos        | 294.9315  | 36.2597      | +713%   | INFO   | Pendiente Facundo: beta no reproducible con IV-203/IV-204. No es Causa A. |
| Log-Normal 2p             | Momentos/MV     | 3.6177    | NO_APLICABLE | —       | INFO   | tesis NO_APLIC (motivo desconocido; serie sin ceros) |
| LP3                       | MV              | NO_CONV   | NO_CONVERGE  | —       | PASS   | —                      |

SKIP (no en tabla tesis): Gen. Exponencial Momentos/ML, Gen. Pareto todos los métodos.

**Conteo: PASS=12, INFO-A=2, INFO-B=1, INFO-C=6, INFO=5, EXCLUIDO=1, SKIP=8, FAIL=0**

### PASO 7 — Cuantiles: PASS (FAIL=0)
Nota: la columna 'LP3 MMI' de la tesis contiene cuantiles GVE MV (verificado al 0.03% para todos los T — ver pendientes-facundo.md). GVE MV METIS se compara contra esa columna. LP3 MMI METIS no tiene referencia válida.

| T [años] | GVE MV METIS | Tesis col. 'LP3 MMI' | diff%   | Nivel | LP3 MMI METIS | Nivel              |
|----------|--------------|----------------------|---------|-------|---------------|--------------------|
| 2        | 18.11        | 18.11                | +0.027% | PASS  | 16.44         | INFO/sin referencia |
| 5        | 34.29        | 34.29                | -0.011% | PASS  | 35.06         | INFO/sin referencia |
| 10       | 48.61        | 48.61                | -0.008% | PASS  | 54.07         | INFO/sin referencia |
| 20       | 65.88        | 65.88                | -0.003% | PASS  | 78.86         | INFO/sin referencia |
| 25       | 72.22        | 72.22                | -0.003% | PASS  | 88.33         | INFO/sin referencia |
| 50       | 94.84        | 94.84                | +0.001% | PASS  | 123.28        | INFO/sin referencia |
| 100      | 122.78       | 122.78               | +0.000% | PASS  | 168.25        | INFO/sin referencia |

**GVE MV: PASS=7/7. LP3 MMI: INFO/sin referencia ×7 — columna LP3 MMI de tesis no contiene cuantiles LP3 MMI (ver pendientes-facundo.md).**

---

## Resultados de Regresión METIS --> PIPELINE COMPLETO (ejecución en vivo, 2026-07-14)

**Qué es esto:** salida real de correr `ejecutar_etapa1()` seguido de
`ejecutar_etapa2()` — el pipeline completo tal como orquesta
`pipeline.py`/`pipeline2.py` hoy — sobre la serie cruda de esta estación
(sin filtrar ni preprocesar). A diferencia de la sección "UNITARIAS" de
arriba (que corre cada prueba/distribución de forma aislada), esto pasa por
el orquestador completo de punta a punta. Mismo formato de tablas que las
secciones de la ficha original (Sheet 1/2/3) y de METIS-unitarias, para que
sea comparable fila por fila. Última de las 5 estaciones del alcance de
Bloque 8 (est_02, est_03, est_04, est_05, est_06).

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
| n | 36 |
| Media [m³/s] | 24.02777777777778 |
| Mediana [m³/s] | 18.0 |
| Varianza (no sesgada) [m³/s]² | 388.08492063492065 |
| Varianza (sesgada) [m³/s]² | 377.3047839506173 |
| Desvío [m³/s] | 19.69987108168276 |
| Asimetría Sesgada | 1.7714930624231697 |
| Asimetría No Sesgada (g) | 1.9292899234457377 |
| Curtosis Sesgada | 7.18110817392331 |
| Curtosis No Sesgada (k) | 8.531748993189863 |
| Coeficiente de Variación (CV) | 0.8198790276769703 |
| Sumatoria ln(xi) | 103.02185185953941 |
| beta_0 = M0 | 24.02777777777778 |
| beta_1 = M1 | 17.08809523809524 |
| beta_2 = M2 | 13.60438842203548 |
| beta_3 = M3 | 11.434284016636958 |
| Máximo [m³/s] | 100.0 |
| Mínimo [m³/s] | 2.0 |
| Rango [m³/s] | 98.0 |

### Etapa 1 — Homogeneidad (pipeline completo — Sheet 2)

#### Helmert
| Parámetro | Valor |
|-----------|-------|
| Estadístico (S-C) | -5.0 |
| Valor crítico (± lim) | 5.916079783099616 |
| Veredicto | aprobada |
| Warning | None |

#### t de Student
| Parámetro | Valor |
|-----------|-------|
| Estadístico t | 1.627202726558698 |
| n1 | 18 |
| n2 | 18 |
| Valor crítico (tabla) | 2.032244509317718 |
| Veredicto | aprobada |

#### Cramer
| Parámetro | Valor |
|-----------|-------|
| Estadístico (t_w1) | 1.398085242360132 |
| n_w1 | 22 |
| n_w2 | 11 |
| Valor crítico (tabla) | 2.032244509317718 |
| Veredicto | aprobada |

**Veredicto homogeneidad (pipeline):** homogeneidad_ok

### Etapa 1 — Independencia (pipeline completo — Sheet 2)

#### Anderson
| Parámetro | Valor |
|-----------|-------|
| Estadístico (máx r_k) | -0.29645988089208464 |
| Valor crítico | 0.29795587741378216 |
| Veredicto | aprobada |

#### Wald-Wolfowitz
| Parámetro | Valor |
|-----------|-------|
| Estadístico Z | 1.2450164884399015 |
| Valor crítico (α=0.05) | ± 1.959963984540054 |
| Veredicto | aprobada |
| Warning | TEST_WARNING_SMALL_SAMPLE |

**Veredicto independencia (pipeline):** independiente

### Etapa 1 — Tendencia y Atípicos (pipeline completo) — sin ficha de Facundo de referencia
Mann-Kendall, Kolmogorov-Smirnov y Chow no están en la tesis de Facundo (los
agregó Carlos) — no hay valor "esperado" ni "METIS unitario" previo contra el
cual comparar estas tres filas en ningún archivo de este repo.

#### Mann-Kendall
| Parámetro | Valor |
|-----------|-------|
| Estadístico | -1.1740500370384932 |
| Valor crítico | 1.959963984540054 |
| Veredicto | aprobada |
| Warning | None |

#### Kolmogorov-Smirnov (tendencia)
| Parámetro | Valor |
|-----------|-------|
| Estadístico (Z tipificado) | 0.8333333333333334 |
| Valor crítico | 1.358 |
| Veredicto | aprobada |

#### Chow
| Parámetro | Valor |
|-----------|-------|
| Estadístico (máx Z_i) | 2.5336171190968115 |
| Valor crítico (K_N) | 2.8236933338407426 |
| Veredicto | aprobada |

**Veredicto general Etapa 1 (pipeline):** nivel_confianza=`con_warnings` — warnings: TEST_WARNING_SMALL_SAMPLE

### Etapa 2 — Parámetros, EEA y Estado (pipeline completo — Sheet 3)
| Distribución | Método | Parámetro 1 | Parámetro 2 | Parámetro 3 | EEA [m³/s] | Status |
|---|---|---|---|---|---|---|
| Uniforme | Momentos | alfa = -10.0934 | beta = 58.1490 |  | 9.7236 | ok |
| Uniforme | Máxima Verosimilitud | alfa = 2.0000 | beta = 100.0000 |  | 31.2294 | ok |
| Exponencial beta | Momentos | beta = 0.041618 |  |  | 4.4501 | ok |
| Exponencial beta | Máxima Verosimilitud | beta = 0.041618 |  |  | 4.4501 | ok |
| Exponencial x0 y beta | Momentos | x0 = 4.3279 | beta = 19.6999 |  | 4.7691 | ok |
| Exponencial x0 y beta | Máxima Verosimilitud | x0 = 1.3706 | beta = 22.6571 |  | 4.2425 | ok |
| Generalizada Exponencial | Momentos | alfa = 1.5857 | lambda = 0.055002 |  | 4.8684 | ok |
| Generalizada Exponencial | Máxima Verosimilitud | alfa = 1.8413 | lambda = 0.059879 |  | 5.4460 | ok |
| Generalizada Exponencial | Momentos L | alfa = 0.321805 | lambda = -0.030047 |  | 54.5268 | ok |
| Normal | Momentos | mu = 24.0278 | sigma = 19.6999 |  | 8.5216 | ok |
| Normal | Máxima Verosimilitud | mu = 24.0278 | sigma = 19.6999 |  | 8.5216 | ok |
| Normal | Momentos L | mu = 24.0278 | sigma = 17.9830 |  | 8.5897 | ok |
| Log Normal (2 parámetros) | Momentos | mu_y = 2.8617 | sigma_y = 0.855919 |  | 3.6177 | ok |
| Log Normal (2 parámetros) | Máxima Verosimilitud | mu_y = 2.8617 | sigma_y = 0.855919 |  | 3.6177 | ok |
| Log Normal (3 parámetros) | Momentos | x0 = -10.0228 | mu_y = 3.3835 | sigma_y = 0.537326 | 5.1530 | ok |
| Log Normal (3 parámetros) | Máxima Verosimilitud | x0 = -1.9285 | mu_y = 3.0031 | sigma_y = 0.726605 | 4.3426 | ok |
| Gamma (2 parámetros) | Momentos | alfa = 16.1515 | beta = 1.4876 |  | 4.9299 | ok |
| Gamma (2 parámetros) | Máxima Verosimilitud | alfa = 13.9143 | beta = 1.7268 |  | 5.5989 | ok |
| Gamma (2 parámetros) | Momentos L | alfa = 15.8352 | beta = 1.5174 |  | 5.0101 | ok |
| Gamma (3 parámetros) | Momentos |  |  |  | — | no_aplicable |
| Gamma (3 parámetros) | Máxima Verosimilitud |  |  |  | — | no_converge |
| Gumbel | Momentos | mu = 15.1628 | alfa = 15.3659 |  | 5.7690 | ok |
| Gumbel | Máxima Verosimilitud | mu = 15.9532 | alfa = 12.6476 |  | 7.2679 | ok |
| Gumbel | Momentos L | mu = 15.5767 | alfa = 14.6411 |  | 6.0139 | ok |
| Gumbel | Máxima Entropía | mu = 16.2443 | alfa = 13.4845 |  | 6.6116 | ok |
| GVE (Valores Extremos) | Momentos | nu = 298.0985 | alfa = 13.2101 | beta = -0.099696 | 294.9315 | ok |
| GVE (Valores Extremos) | Máxima Verosimilitud | nu = 13.9953 | alfa = 10.6102 | beta = -0.311803 | 3.9893 | ok |
| GVE (Valores Extremos) | Momentos L | nu = 14.3760 | alfa = 11.6484 | beta = -0.204892 | 4.8125 | ok |
| Log Pearson tipo III | Momentos Método Directo |  |  |  | — | no_aplicable |
| Log Pearson tipo III | Momentos Método Indirecto | alfa = 0.187368 | beta = 20.8677 | y0 = -1.0482 | 4.8532 | ok |
| Log Pearson tipo III | Máxima Verosimilitud |  |  |  | — | no_converge |
| Generalizada de Pareto | Momentos | mu = 4.0902 | sigma = 20.1797 | epsilon = 0.012141 | 4.4140 | ok |
| Generalizada de Pareto | Máxima Verosimilitud |  |  |  | — | no_converge |
| Generalizada de Pareto | Mínimos Cuadrados |  |  |  | — | no_converge |
| Generalizada de Pareto | Momento Prob. Pesada | mu = -6.9807 | sigma = 364.0250 | epsilon = 4.5342 | 180,416,853.1974 | ok |

### Notas de cableado — Bloque 6/7 (solo señalamiento, sin investigar causa)

**¿Ceros en la serie?** No — mínimo observado = 2.0 (`tiene_ceros=False` pasado a `ejecutar_etapa2()`). La rama `STATUS_DISABLED_ZEROS` sigue sin ejercitarse en ninguna de las 5 estaciones auditadas hasta ahora (est_02 a est_06).

**Cambios de status vs. est_02** (comparando categoría, no valor numérico):
- `logpearson3/mv`: est_02=`ok` -> est_04=`no_converge`
- `gamma3p/momentos`: est_02=`ok` -> est_04=`no_aplicable`
- Mismo patrón ya visto en est_03 (ambos) y est_05 (logpearson3/mv) — no es un caso nuevo aislado de est_04.

**`gamma3p/mv` — resultado real de esta corrida (sin investigar la nota vieja "scan bug: root en x0≈1.74"):**
- status=`no_converge`, parametros=`None`. No converge en la corrida de hoy — no se intentó reproducir ni resolver la nota antigua, queda para que Octavio lo mire aparte.

**GVE / MV — rama de inicialización:**
- MOMENTOS descartado (guard falla, nu0=298.0985325036304, alpha0=13.210140275234929, beta0=-0.09969554155720073) -> fallback ML