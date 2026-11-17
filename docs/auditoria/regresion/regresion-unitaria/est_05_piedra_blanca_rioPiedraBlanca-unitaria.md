## Estación 5 — Piedra Blanca – Río Piedra Blanca

### Serie (Sheet 1)
```python
serie = [
    7.0,    # 39-40
    104.0,  # 40-41
    17.0,   # 41-42
    90.0,   # 42-43
    9.2,    # 43-44
    149.0,  # 44-45
    26.0,   # 45-46
    41.6,   # 46-47
    4.0,    # 47-48
    # 48-49: S/D - Interrupción
    # 49-50: S/D - Interrupción
    34.0,   # 50-51
    59.0,   # 51-52
    30.0,   # 52-53
    215.0,  # 53-54
    1.7,    # 54-55
    57.0,   # 55-56
    125.0,  # 56-57
    30.0,   # 57-58
    64.0,   # 58-59
    40.0,   # 59-60
    78.0,   # 60-61
    89.0,   # 61-62
    2.8,    # 62-63
    3.4,    # 63-64
    26.0,   # 64-65
    31.0,   # 65-66
    24.0,   # 66-67
    18.0,   # 67-68
    14.0,   # 68-69
    0.9,    # 69-70
    31.0,   # 70-71
    9.0,    # 71-72
    57.0,   # 72-73
    1.3,    # 73-74
    2.3,    # 74-75
    19.0,   # 75-76
    33.0,   # 76-77
    45.0,   # 77-78
    89.0,   # 78-79
    57.0,   # 79-80
]
# n=39 (41 años calendario, 2 interrupciones: 48-49 y 49-50)
```

### Estadística descriptiva esperada (Sheet 1)
| Variable                        | Valor esperado |
|---------------------------------|----------------|
| n                               | 39             |
| Media [m³/s]                    | 44.466         |
| Varianza [m³/s]²                | 2099.627       |
| Desvío [m³/s]                   | 45.822         |
| Asimetría Sesgada               | 1.699          |
| Asimetría No Sesgada (g)        | 1.838          |
| Curtosis Sesgada                | 6.186          |
| Curtosis No Sesgada (k)         | 7.25           |
| Coeficiente de Variación (CV)   | 1.03           |
| Sumatoria ln(xi)                | 122.485        |
| beta_0 = M0                     | 44.466         |
| beta_1 = M1                     | 33.925         |
| beta_2 = M2                     | 27.853         |
| beta_3 = M3                     | 23.871         |
| Máximo [m³/s]                   | 215.0          |
| Mínimo [m³/s]                   | 1.0            |

---

### Etapa 1 — Homogeneidad (Sheet 2)

#### Helmert
| Parámetro              | Valor esperado |
|------------------------|----------------|
| N° de Series (S)       | 19             |
| N° de Cambios (C)      | 19             |
| Estadístico (S-C)      | 0              |
| n                      | 39             |
| Umbral inferior        | -6.16          |
| Umbral superior        | 6.16           |
| Conclusión individual  | El estadístico (S - C) está comprendido entre -(nj-1)^0.5 y +(nj-1)^0.5. Por lo tanto la serie es Homogénea. |

#### t de Student
| Parámetro              | Valor esperado |
|------------------------|----------------|
| Estadístico t          | 2.08           |
| Grados de libertad     | 37             |
| Valor crítico (tabla)  | 2.0262         |
| Conclusión individual  | El valor absoluto del estadístico t es mayor que el valor de tabla de t para 37 grados de libertad y para un nivel de significancia del 5%. Por lo tanto la serie No es Homogénea. |

#### Cramer
| Parámetro              | Valor esperado |
|------------------------|----------------|
| tau subgrupo 1         | -0.16143       |
| tau subgrupo 2         | -0.33835       |
| t calculado sg. 1      | 1.2688         |
| t calculado sg. 2      | 1.49884        |
| Valor crítico (tabla)  | 2.0262         |
| Conclusión individual  | El valor absoluto de ambos tw es menor que el valor de tabla de t para 37 G.L. y para α = 5%. La serie es Homogénea. |

**Veredicto homogeneidad:** Serie Homogénea (Aprobada por desempate)
**Conclusión:** Se registra un rechazo marginal en la prueba t de Student (2.08 > 2.0262). Sin embargo, bajo el criterio metodológico de la tesis, se aprueba la homogeneidad de la serie debido al resultado favorable de Cramer y al voto dirimente de Helmert (estadístico = 0 dentro del rango). La serie cuenta con consistencia numérica para la Etapa 2 para sus 37 G.L. con alpha = 5%.

---

### Etapa 1 — Independencia (Sheet 2)

#### Anderson
| Parámetro                              | Valor esperado            |
|----------------------------------------|---------------------------|
| n                                      | 39                        |
| k = n/3                                | 13.0                      |
| k adoptado                             | 14                        |
| Media                                  | 44.47                     |
| N° máximo puntos fuera de bandas       | 1.4 (se redondea a 1)     |
| N° puntos fuera de bandas              | 0                         |
| Conclusión individual                  | Aceptada (0 puntos fuera, comportamiento óptimo). Se acepta la hipótesis de que las variables de la serie son Independientes. |

#### Wald-Wolfowitz
| Parámetro                    | Valor esperado |
|------------------------------|----------------|
| n                            | 39             |
| n1                           | 14             |
| n2                           | 25             |
| R (rachas observadas)        | 20             |
| Media teórica de R           | 18.95          |
| Varianza teórica de R        | 8.01           |
| Estadístico Z                | 0.37           |
| Valor crítico α=0.05         | ± 1.96         |
| Valor crítico α=0.01         | ± 2.58         |
| Conclusión individual        | Aceptada (Z=0.37 muy cercano a cero, dentro de los rangos críticos para α=5% y α=1%). La serie se concluye como independiente. |

**Veredicto independencia:** Serie Independiente
**Conclusión:** Aceptación unánime de la hipótesis de independencia. La prueba de Anderson exhibe un comportamiento óptimo con 0 puntos fuera de las bandas de aceptación (límite permitido: 1.4). El test de Wald-Wolfowitz convalida la aleatoriedad con Z=0.37, manteniéndose seguro dentro de los rangos críticos para ambos niveles de significancia. La serie queda plenamente habilitada para la Etapa 2.

**Veredicto general Etapa 1:** Habilitada para Etapa 2

---

### Etapa 2 — Parámetros (Sheet 3)
| Distribución              | Método                      | Parámetro 1     | Parámetro 2      | Parámetro 3      |
|---------------------------|-----------------------------|-----------------|------------------|------------------|
| Uniforme                  | Momentos                    | alfa = -34.90   | beta = 123.83    |                  |
| Uniforme                  | Máxima Verosimilitud        | alfa = 0.91     | beta = 215.00    |                  |
| Exponencial beta          | Momentos y M. Verosimilitud | beta = 0.022    |                  |                  |
| Exponencial x0 y beta     | Momentos                    | x0 = -1.36      | beta = 45.82     |                  |
| Exponencial x0 y beta     | Máxima Verosimilitud        | x0 = -0.24      | beta = 44.70     |                  |
| Generalizada Exponencial  | Momentos                    | alfa = 0.91     | lambda = 0.0301  |                  |
| Generalizada Exponencial  | Máxima Verosimilitud        | alfa = 0.89     | lambda = 0.0208  |                  |
| Generalizada Exponencial  | Momentos L                  | alfa = 0.82     | lambda = -0.0097 |                  |
| Normal                    | Momentos L                  | mu = 44.47      | sigma = 41.4363  |                  |
| Normal                    | Momentos y M. Verosimilitud | mu = 44.47      | sigma = 45.8217  |                  |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | mu_y = 3.14     | sigma_y = 1.380  |                  |
| Log Normal (3 parámetros) | Momentos                    | x0 = -38.01     | mu_y = 4.2780    | sigma_y = 0.5187 |
| Log Normal (3 parámetros) | Máxima Verosimilitud        | x0 = -2.15      | mu_y = 3.3323    | sigma_y = 1.1137 |
| Gamma (2 parámetros)      | Momentos                    | alfa = 47.22    | beta = 0.942     |                  |
| Gamma (2 parámetros)      | Máxima Verosimilitud        | alfa = 49.12    | beta = 0.905     |                  |
| Gamma (2 parámetros)      | Momentos L                  | alfa = 50.79    | beta = 0.876     |                  |
| Gamma (3 parámetros)      | Momentos                    | x0 = -5.387     | alfa = 42.117    | beta = 1.184     |
| Gamma (3 parámetros)      | Máxima Verosimilitud        | NO_APLICABLE    | NO_APLICABLE     | NO_APLICABLE     |
| Gamma (3 parámetros)      | Momento Prob. Pesada        | x0 = -1.368     | alfa = 54.585    | beta = 0.840     |
| Gumbel                    | Momentos                    | alfa = 35.741   | mu = 23.846      |                  |
| Gumbel                    | Máxima Verosimilitud        | alfa = 28.399   | mu = 25.931      |                  |
| Gumbel                    | Momentos L                  | alfa = 33.736   | mu = 24.993      |                  |
| Gumbel                    | Máxima Entropía             | alfa = 30.757   | mu = 26.713      |                  |
| GVE (Valores Extremos)    | Momentos                    | alfa = 20.529   | beta = -0.032    | nu = 25.367      |
| GVE (Valores Extremos)    | Máxima Verosimilitud        | alfa = 21.386   | beta = -0.478    | nu = 19.578      |
| GVE (Valores Extremos)    | Momentos L                  | alfa = 33.307   | beta = -0.254    | nu = 54.129      |
| Log Pearson tipo III      | Momentos Método Directo     | alfa = 0.333    | beta = 0.562     | y0 = 3.567       |
| Log Pearson tipo III      | Momentos Método Indirecto   | alfa = 0.536    | beta = 6.639     | y0 = -0.415      |
| Log Pearson tipo III      | Máxima Verosimilitud        | NO_CONVERGE     | NO_CONVERGE      | NO_CONVERGE      |

---

### Etapa 2 — EEA esperados (Sheet 3)
| Distribución              | Método                      | EEA [m³/s]   |
|---------------------------|-----------------------------|--------------|
| Log Normal (3 parámetros) | Máxima Verosimilitud        | 5.7842       |
| GVE (Valores Extremos)    | Máxima Verosimilitud        | 6.3279       |
| Generalizada Exponencial  | Máxima Verosimilitud        | 8.1179       |
| Exponencial x0 y beta     | Momentos                    | 8.7670       |
| Exponencial x0 y beta     | Máxima Verosimilitud        | 9.4085       |
| Exponencial beta          | Momentos y M. Verosimilitud | 9.4250       |
| Gamma (3 parámetros)      | Momento Prob. Pesada        | 10.2359      |
| Gamma (2 parámetros)      | Momentos L                  | 11.2310      |
| Gamma (2 parámetros)      | Máxima Verosimilitud        | 11.6154      |
| Gamma (2 parámetros)      | Momentos                    | 12.0855      |
| Gamma (3 parámetros)      | Momentos                    | 12.3058      |
| Gumbel                    | Momentos                    | 12.7525      |
| Log Normal (3 parámetros) | Momentos                    | 13.3677      |
| Gumbel                    | Momentos L                  | 13.4880      |
| Gumbel                    | Máxima Entropía             | 15.1950      |
| Gumbel                    | Máxima Verosimilitud        | 17.2068      |
| Normal                    | Momentos y M. Verosimilitud | 20.5769      |
| Normal                    | Momentos L                  | 20.9960      |
| Uniforme                  | Momentos                    | 23.2824      |
| Log Pearson tipo III      | Momentos M. Indirecto       | 36.5529      |
| Log Pearson tipo III      | Momentos M. Directo         | 37.7133      |
| GVE (Valores Extremos)    | Momentos L                  | 38.2840      |
| GVE (Valores Extremos)    | Momentos                    | 41.3296      |
| Uniforme                  | Máxima Verosimilitud        | 72.2272      |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | NO_APLICABLE |
| Gamma (3 parámetros)      | Máxima Verosimilitud        | NO_APLICABLE |
| Log Pearson tipo III      | Máxima Verosimilitud        | NO_CONVERGE  |

---

### Etapa 2 — Cuantiles esperados (Sheet 3)
| T [años] | Log Normal 3p MV [m³/s] | GVE MV [m³/s] |
|----------|-------------------------|---------------|
| 2        | 25.85                   | 28.14         |
| 5        | 68.33                   | 66.47         |
| 10       | 109.40                  | 105.99        |
| 20       | 156.26                  | 159.83        |
| 25       | 172.05                  | 181.15        |
| 50       | 221.43                  | 263.57        |
| 100      | 268.51                  | 377.90        |

### Modelo seleccionado por Facundo
Modelo Log Normal de 3 parámetros (Máxima Verosimilitud) seleccionado. Tanto el análisis numérico como la inspección visual coinciden plenamente. La distribución Log Normal de 3 parámetros registra el menor error con un EEA de 5.7842 m³/s, seguida de cerca por la GVE MV (EEA=6.3279 m³/s). Al no presentar discrepancias entre la estadística y la gráfica, se adopta la Log Normal 3p como ley de distribución gobernante. Los caudales de diseño se proyectan desde los 25.85 m³/s (T=2 años) hasta los 268.51 m³/s (T=100 años).

---

## Resultados de Regresión METIS

### Estado general: PASS* — FAIL=0 en PASOS 1–6; PASO 7 LN3p MV FAIL=6 (Causa C — cuantiles no reproducibles con IV-120, ver pendientes-facundo.md)

### PASO 1 — Estadística descriptiva: PASS
| Variable                      | METIS        | Tesis        | diff%   | Nivel |
|-------------------------------|--------------|--------------|---------|-------|
| n                             | 39           | 39           | 0.000%  | PASS  |
| Media                         | 44.467       | 44.466       | +0.002% | PASS  |
| Varianza                      | 2099.584     | 2099.627     | -0.002% | PASS  |
| Desvío                        | 45.821       | 45.822       | -0.002% | PASS  |
| M0                            | 44.467       | 44.466       | +0.002% | PASS  |
| M1                            | 33.925       | 33.925       | 0.000%  | PASS  |
| M2                            | 27.853       | 27.853       | 0.000%  | PASS  |
| M3                            | 23.871       | 23.871       | 0.000%  | PASS  |
| Sumatoria ln(xi)              | 122.487      | 122.485      | +0.002% | PASS  |
| Máximo                        | 215.0        | 215.0        | 0.000%  | PASS  |
| Mínimo                        | 0.9          | 1.0          | —       | INFO  |
| Asimetría sesgada             | 1.767        | 1.699        | +4.0%   | INFO  |
| Asimetría no sesgada (g)      | 1.911        | 1.838        | +3.97%  | INFO  |
| Curtosis sesgada              | 6.517        | 6.186        | +5.3%   | INFO  |
| Curtosis no sesgada           | 7.637        | 7.25         | +5.3%   | INFO  |
| CV                            | 1.030        | 1.03         | 0.000%  | INFO  |

Nota mínimo: serie tiene 0.9 (año 69-70); tesis muestra 1.0 (redondeo de display). Verificado: media y suma_ln coinciden a <0.002% usando 0.9.
Nota g: METIS sigue IV-4/IV-5 (ddof=0). Excel usa SKEW() (ddof=1). Diferencia trazable — ver DECISIÓN013.

### PASO 2 — Homogeneidad: PASS (con INFO)
| Prueba       | Estadístico METIS                   | Estadístico Tesis | diff%   | Veredicto METIS | Nivel |
|--------------|-------------------------------------|-------------------|---------|-----------------|-------|
| Helmert S-C  | 0                                   | 0                 | 0.000%  | Aprobada        | PASS  |
| t-Student    | 1.818 (n1=19, n2=20)                | 2.08 (n1=20,n2=19)| -12.6%  | Aprobada        | INFO  |
| Cramer τ1    | -0.16141                            | -0.16143          | -0.01%  | Aprobada        | PASS  |
| Cramer tw1   | 1.26861                             | 1.2688            | -0.01%  | Aprobada        | PASS  |
| Cramer τ2    | -0.31845 (n_w2=12)                  | -0.33835 (n_w2=13)| -5.9%   | Aprobada        | INFO  |
| Cramer tw2   | 1.32149 (n_w2=12)                   | 1.49884 (n_w2=13) | -11.8%  | Aprobada        | INFO  |
| Veredicto    | homogeneidad_ok                     | homogeneidad_warning | —    | —               | INFO  |

Nota t-Student: para n=39 impar, METIS usa n1=floor(n/2)=19; tesis usa n1=ceil(n/2)=20. METIS aprueba (1.818<2.026), tesis rechaza (2.08>2.026). Pendiente confirmar convención de partición para n impar.
Nota Cramer τ2: DECISIÓN011 — METIS usa round(39×0.30)=12; tesis usa 13 (=n/3=13.0 exacto). Ambas tw<vc=2.0262; veredicto aprobada en los dos casos.
Nota veredicto: tesis=homogeneidad_warning (t-Student rechaza); METIS=homogeneidad_ok (todas aprueban). Pipeline continúa en ambos casos.

### PASO 3 — Independencia: PASS
| Prueba           | METIS           | Tesis           | diff%  | Veredicto | Nivel |
|------------------|-----------------|-----------------|--------|-----------|-------|
| Anderson lags    | 0 fuera (k=13)  | 0 fuera (k=14)  | —      | Aprobada  | PASS  |
| Wald-Wolfowitz Z | 0.37            | 0.37            | 0.000% | Aprobada  | PASS  |
| Veredicto        | independiente   | independiente   | —      | —         | PASS  |

Nota Anderson: tesis usa k_adoptado=14 (= n/3+1 para n=39), METIS usa k_max=n//3=13. 0 lags fuera en ambos — veredicto idéntico.

### PASO 4 — Veredicto Etapa 1: PASS
Habilitada para Etapa 2. Homogeneidad OK (Cramer aprueba en ambos; diferencia en t-Student no bloqueante). Independencia OK.

### PASO 5 — Parámetros Etapa 2: PASS (FAIL=0)
| Distribución              | Método          | Param METIS                                              | Param Tesis                                      | Nivel  | Nota               |
|---------------------------|-----------------|----------------------------------------------------------|--------------------------------------------------|--------|--------------------|
| Uniforme                  | Momentos        | α=-34.8980, β=123.8313                                   | α=-34.90, β=123.83                               | PASS   | —                  |
| Uniforme                  | MV              | α=0.9000, β=215.0000                                     | α=0.91, β=215.00                                 | INFO   | α=min(serie)=0.9; tesis muestra 0.91 (posible error tipográfico de display) |
| Exponencial β             | Momentos/MV     | β=0.0225                                                 | β=0.022                                          | PASS   | 1/44.467=0.02249 → 0.022 a 3 dec / 0.0225 a 4 dec |
| Exponencial x0β           | Momentos        | x0=-1.3545, β=45.8212                                    | x0=-1.36, β=45.82                                | PASS   | —                  |
| Exponencial x0β           | MV              | x0=-0.2465, β=44.7131                                    | x0=-0.24, β=44.70                                | INFO   | x0: tesis usó x_min=0.91 (redondeo) → x0=-0.236≈-0.24; METIS usa x_min=0.9 → x0=-0.247. β PASS. |
| Gen. Exponencial          | Momentos        | α=0.9347, λ=0.0215                                       | α=0.91, λ=0.0301                                 | INFO   | tesis internamente inconsistente: CV(α=0.91)=1.043≠CV_datos=1.030; METIS correcto (CV_METIS=1.030, µ_METIS=44.51) |
| Gen. Exponencial          | MV              | α=0.8880, λ=0.0208                                       | α=0.89, λ=0.0208                                 | PASS   | —                  |
| Gen. Exponencial          | ML              | α=0.2377, λ=-0.0184                                      | α=0.82, λ=-0.0097                                | INFO   | pendiente IV-84 (signo ψ(1)) — mismo patrón est_03/est_04 |
| Normal                    | Momentos/MV     | µ=44.4667, σ=45.8212                                     | µ=44.47, σ=45.8217                               | PASS   | —                  |
| Normal                    | ML              | µ=44.4667, σ=41.4356                                     | µ=44.47, σ=41.4363                               | PASS   | —                  |
| Log-Normal 2p             | Momentos/MV     | µy=3.1407, σy=1.3799                                     | µy=3.14, σy=1.380                                | PASS   | —                  |
| Log-Normal 3p             | Momentos        | x0=-35.3524, µy=4.2373, σy=0.5337                        | x0=-38.01, µy=4.2780, σy=0.5187                  | INFO-A | A: g-propagación DECISIÓN013. x0 diff=-7.0%, σy diff=+2.9%, µy diff=-0.95%. |
| Log-Normal 3p             | MV              | x0=-2.1576, µy=3.3327, σy=1.1133                         | x0=-2.15, µy=3.3323, σy=1.1137                   | PASS   | —                  |
| Gamma (2 parámetros)      | Momentos        | α=47.2170, β=0.9418                                      | α=47.22, β=0.942                                 | PASS   | —                  |
| Gamma (2 parámetros)      | MV              | α=49.1217, β=0.9052                                      | α=49.12, β=0.905                                 | PASS   | —                  |
| Gamma (2 parámetros)      | ML              | α=50.7864, β=0.8756                                      | α=50.79, β=0.876                                 | PASS   | —                  |
| Gamma (3 parámetros)      | Momentos        | β=1.0949, α=43.7907, x0=-3.4792                          | x0=-5.387, α=42.117, β=1.184                     | INFO-A | A: β=4/g² → g_METIS=1.911→β=1.095, g_tesis=1.838→β=1.184. Causa A pura. |
| Gamma (3 parámetros)      | MV              | NO_CONVERGE                                              | NO_APLICABLE                                     | PASS   | ambos sin EEA — funcionalmente equivalentes |
| Gamma (3 parámetros)      | MPP             | EXCLUIDO                                                 | x0=-1.368, α=54.585, β=0.840                     | EXCLUIDO | Cap. IV no desarrolla ecuaciones MPP |
| Gumbel                    | Momentos        | µ=23.8471, α=35.7405                                     | α=35.741, µ=23.846                               | PASS   | —                  |
| Gumbel                    | MV              | µ=25.9320, α=28.3984                                     | α=28.399, µ=25.931                               | PASS   | —                  |
| Gumbel                    | ML              | µ=24.9941, α=33.7353                                     | α=33.736, µ=24.993                               | PASS   | —                  |
| Gumbel                    | ME              | µ=26.7138, α=30.7561                                     | α=30.757, µ=26.713                               | PASS   | —                  |
| GVE (Valores Extremos)    | Momentos        | ν=695.2446, α=30.8225, β=-0.0979                         | α=20.529, β=-0.032, ν=25.367                     | INFO   | Pendiente Facundo: β no reproducible con IV-203/IV-204. No es Causa A. |
| GVE (Valores Extremos)    | MV              | ν=19.5791, α=21.3856, β=-0.4777                          | α=21.386, β=-0.478, ν=19.578                     | PASS   | —                  |
| GVE (Valores Extremos)    | ML              | ν=21.6878, α=25.0565, β=-0.2543                          | α=33.307, β=-0.254, ν=54.129                     | INFO   | B: β PASS (diff=+0.12%), α/ν difieren (Causa B — convergencia distinta) |
| Log Pearson III           | Directo         | NO_APLICABLE (B=2.51 ∉ (3,6])                            | α=0.333, β=0.562, y0=3.567                       | INFO   | METIS aplica restricción IV-249 correctamente |
| Log Pearson III           | Indirecto       | β=6.1327, α=0.5572, y0=-0.2765                           | α=0.536, β=6.639, y0=-0.415                      | INFO-A | A: DECISIÓN013 — gy_yi usa ddof=0 vs SKEW() Excel. α diff=+3.96%, β diff=-7.62% |
| Log Pearson III           | MV              | NO_CONVERGE                                              | NO_CONVERGE                                      | PASS   | —                  |

### PASO 6 — EEA: PASS (FAIL=0)
| Distribución              | Método          | EEA METIS  | EEA Tesis    | diff%    | Nivel    | Causa                    |
|---------------------------|-----------------|------------|--------------|----------|----------|--------------------------|
| Log-Normal 3p             | MV              | 8.7739     | 5.7842       | +51.6%   | INFO-C   | C: EEA distinto con params idénticos (diff<0.1%). Causa desconocida — pendiente Facundo |
| GVE                       | MV              | 6.3250     | 6.3279       | -0.046%  | PASS     | —                        |
| Gen. Exponencial          | MV              | 8.1182     | 8.1179       | +0.004%  | PASS     | —                        |
| Exponencial x0β           | Momentos        | 8.7670     | 8.7670       | 0.000%   | PASS     | —                        |
| Exponencial x0β           | MV              | 9.4018     | 9.4085       | -0.071%  | PASS     | —                        |
| Exponencial β             | Momentos/MV     | 9.4244     | 9.4250       | -0.006%  | PASS     | —                        |
| Gamma (3 parámetros)      | MPP             | EXCLUIDO   | 10.2359      | —        | EXCLUIDO | Cap. IV no desarrolla ecuaciones |
| Gamma (2 parámetros)      | ML              | 8.0077     | 11.2310      | -28.7%   | INFO-C   | C: EEA distinto con params idénticos |
| Gamma (2 parámetros)      | MV              | 8.4314     | 11.6154      | -27.4%   | INFO-C   | C: EEA distinto con params idénticos |
| Gamma (2 parámetros)      | Momentos        | 8.9581     | 12.0855      | -25.9%   | INFO-C   | C: EEA distinto con params idénticos |
| Gamma (3 parámetros)      | Momentos        | 9.2217     | 12.3058      | -25.1%   | INFO-A   | A: g-propagación DECISIÓN013 (β=4/g²). EEA menor es consecuencia aritmética de parámetros distintos. |
| Gumbel                    | Momentos        | 12.7527    | 12.7525      | +0.002%  | PASS     | —                        |
| Log-Normal 3p             | Momentos        | 10.4932    | 13.3677      | -21.5%   | INFO-A   | A: g-propagación DECISIÓN013. EEA menor es consecuencia aritmética de parámetros distintos. |
| Gumbel                    | ML              | 13.4882    | 13.4880      | +0.001%  | PASS     | —                        |
| Gumbel                    | ME              | 15.1952    | 15.1950      | +0.001%  | PASS     | —                        |
| Gumbel                    | MV              | 17.2072    | 17.2068      | +0.002%  | PASS     | —                        |
| Normal                    | Momentos/MV     | 20.2873    | 20.5769      | -1.4%    | INFO-C   | C: EEA distinto con params idénticos |
| Normal                    | ML              | 20.4142    | 20.9960      | -2.8%    | INFO-C   | C: EEA distinto con params idénticos |
| Uniforme                  | Momentos        | 23.2826    | 23.2824      | +0.001%  | PASS     | —                        |
| Log Pearson III           | Indirecto       | 64.6816    | 36.5529      | +76.9%   | INFO-A   | A: g-propagación DECISIÓN013 (gy_yi ddof=0 vs Excel SKEW()). EEA mayor es consecuencia aritmética. |
| Log Pearson III           | Directo         | NO_APLIC   | 37.7133      | —        | INFO     | METIS aplica restricción B∈(3,6] (B=2.51) |
| GVE                       | ML              | 9.0127     | 38.2840      | -76.4%   | INFO-B   | B: convergencia a óptimo distinto (β≈PASS, α/ν difieren) |
| GVE                       | Momentos        | 697.5427   | 41.3296      | +1588%   | INFO     | Pendiente Facundo: β no reproducible con IV-203/IV-204. No es Causa A. |
| Uniforme                  | MV              | 72.2232    | 72.2272      | -0.006%  | PASS     | —                        |
| Log-Normal 2p             | Momentos/MV     | 27.1902    | NO_APLICABLE | —        | INFO     | tesis NO_APLIC (motivo desconocido; serie sin ceros) |
| Gamma (3 parámetros)      | MV              | NO_CONV    | NO_APLICABLE | —        | PASS     | ambos sin EEA — funcionalmente equivalentes |
| Log Pearson III           | MV              | NO_CONV    | NO_CONVERGE  | —        | PASS     | —                        |
| Gen. Exponencial          | Momentos        | 8.7103     | SKIP         | —        | SKIP     | no en tabla tesis        |
| Gen. Exponencial          | ML              | 96.2218    | SKIP         | —        | SKIP     | no en tabla tesis        |

**Conteo: PASS=13, INFO-A=3, INFO-B=1, INFO-C=5, INFO=3, EXCLUIDO=1, SKIP=2, FAIL=0**

### PASO 7 — Cuantiles: FAIL (LN3p MV)
Modelos: LN3p MV (seleccionado) y GVE MV (testigo).

| T [años] | LN3p MV METIS | LN3p MV Tesis | diff%    | Nivel | GVE MV METIS | GVE MV Tesis | diff%   | Nivel |
|----------|---------------|---------------|----------|-------|--------------|--------------|---------|-------|
| 2        | 25.86         | 25.85         | +0.03%   | PASS  | 28.15        | 28.14        | +0.02%  | PASS  |
| 5        | 69.33         | 68.33         | +1.46%   | FAIL  | 66.47        | 66.47        | -0.01%  | PASS  |
| 10       | 114.55        | 109.40        | +4.70%   | FAIL  | 105.98       | 105.99       | -0.01%  | PASS  |
| 20       | 172.76        | 156.26        | +10.56%  | FAIL  | 159.82       | 159.83       | -0.01%  | PASS  |
| 25       | 194.63        | 172.05        | +13.13%  | FAIL  | 181.14       | 181.15       | -0.01%  | PASS  |
| 50       | 273.62        | 221.43        | +23.57%  | FAIL  | 263.54       | 263.57       | -0.01%  | PASS  |
| 100      | 371.40        | 268.51        | +38.32%  | FAIL  | 377.85       | 377.90       | -0.01%  | PASS  |

**LN3p MV: PASS=1/7, FAIL=6/7. GVE MV: PASS=7/7.**

Nota LN3p MV: IV-120 con los parámetros METIS (x0=-2.158, µy=3.3327, σy=1.1133) produce xT≈371 para T=100. Los parámetros tesis (x0=-2.15, µy=3.3323, σy=1.1137) producen el mismo resultado (~371). La referencia de la tesis es 268.51. La discrepancia no es atribuible a diferencia de parámetros — Causa C (pendiente Facundo). Ver pendientes-facundo.md.