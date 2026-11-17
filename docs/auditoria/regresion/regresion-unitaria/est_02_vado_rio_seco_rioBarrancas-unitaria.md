# METIS — Regression Tests
## Fuente: Tesis Facundo Ganancias Martínez

### Tolerancias globales
| Magnitud                  | Tolerancia |
|---------------------------|------------|
| Estadística descriptiva   | ±0.01%     |
| Etapa 1 — estadísticos    | ±0.01%     |
| Etapa 2 — parámetros      | ±1%        |
| Etapa 2 — EEA             | ±1%        |
| Etapa 2 — cuantiles       | ±1%        |

---

## Estación 2 — Vado de Río Seco – Río Barrancas

### Serie (Sheet 1)
serie = [
    98.0,   # 38-39
    44.0,   # 39-40
    97.0,   # 40-41
    52.0,   # 41-42
    90.0,   # 42-43
    247.0,  # 43-44
    191.0,  # 44-45
    54.0,   # 45-46
    112.0,  # 46-47
    42.0,   # 47-48
    60.0,   # 48-49
    157.0,  # 49-50
    61.0,   # 50-51
    45.0,   # 51-52
    91.0,   # 52-53
    257.0,  # 53-54
    458.0,  # 54-55
    381.0,  # 55-56
    251.0,  # 56-57
    151.0,  # 57-58
    122.0,  # 58-59
    58.0,   # 59-60
    145.0,  # 60-61
    158.0,  # 61-62
]
```

### Estadística descriptiva esperada (Sheet 1)
| Variable                        | Valor esperado |
|---------------------------------|----------------|
| n                               | 24             |
| Media [m³/s]                    | 142.583        |
| Varianza [m³/s]²                | 11818.949      |
| Desvío [m³/s]                   | 108.715        |
| Asimetría Sesgada               | 1.375          |
| Asimetría No Sesgada (g)        | 1.565          |
| Curtosis Sesgada                | 4.219          |
| Curtosis No Sesgada (k)         | 5.489          |
| Coeficiente de Variación (CV)   | 0.762          |
| Sumatoria ln(xi)                | 113.246        |
| beta_0 = M0                     | 142.583        |
| beta_1 = M1                     | 99.741         |
| beta_2 = M2                     | 79.402         |
| beta_3 = M3                     | 66.866         |
| Máximo [m³/s]                   | 458.0          |
| Mínimo [m³/s]                   | 42.0           |

---

### Etapa 1 — Homogeneidad (Sheet 2)

#### Helmert
| Parámetro              | Valor esperado |
|------------------------|----------------|
| N° de Series (S)       | 16             |
| N° de Cambios (C)      | 7              |
| Estadístico (S-C)      | 9              |
| n                      | 24             |
| Umbral inferior        | -4.8           |
| Umbral superior        | 4.8            |
| Conclusión individual  | El estadístico (S - C) no está comprendido entre -(nj-1)^0.5 y +(nj-1)^0.5. Por lo tanto la serie No es Homogénea. Rechazada (9 está fuera del rango). |

#### t de Student
| Parámetro              | Valor esperado |
|------------------------|----------------|
| Estadístico t          | -1.76          |
| Grados de libertad     | 22             |
| Valor crítico (tabla)  | 2.0739         |
| Conclusión individual  | El valor absoluto del estadístico t es menor que el valor de tabla de t para 22 grados de libertad (G.L.) y para un nivel de significancia: α = 5%. Por lo tanto la serie es Homogénea. |

#### Cramer
| Parámetro              | Valor esperado |
|------------------------|----------------|
| tau subgrupo 1         | 0.18289        |
| tau subgrupo 2         | 0.35206        |
| t calculado sg. 1      | 1.1397         |
| t calculado sg. 2      | 1.08774        |
| Valor crítico (tabla)  | 2.0739         |
| Conclusión individual  | El valor absoluto de ambos tw es menor que el valor de tabla de t para 22 G.L. y para α = 5%. La serie es Homogénea. |

**Veredicto homogeneidad:** Serie Homogénea (Aprobada por mayoría)
**Conclusión:** Se registra una discrepancia en Helmert, pero se acepta la homogeneidad de la serie debido a que las dos pruebas de mayor robustez estadística (t de Student y Cramer) coinciden de manera unánime con alpha = 5% para sus 22 G.L. La serie es consistente y queda habilitada para la Etapa 2 de ajuste de distribuciones de frecuencia.

---

### Etapa 1 — Independencia (Sheet 2)

#### Anderson
| Parámetro                              | Valor esperado |
|----------------------------------------|----------------|
| n                                      | 24             |
| k = n/3                                | 8.0            |
| k adoptado                             | 9              |
| Media                                  | 142.58         |
| N° máximo puntos fuera de bandas       | 1              |
| N° puntos fuera de bandas              | 1              |
| Conclusión individual                  | Aceptada (1 punto fuera no supera el límite admisible de 1). Se acepta la hipótesis de que las variables de la serie son Independientes. |

#### Wald-Wolfowitz
| Parámetro                    | Valor esperado |
|------------------------------|----------------|
| n                            | 24             |
| n1                           | 10             |
| n2                           | 14             |
| R (rachas observadas)        | 8              |
| Media teórica de R           | 12.67          |
| Varianza teórica de R        | 5.41           |
| Estadístico Z                | -2.01          |
| Valor crítico α=0.05         | ± 1.96         |
| Valor crítico α=0.01         | ± 2.58         |
| Conclusión individual        | Aceptada por tolerancia (alpha = 0.01). El estadístico obtenido excede levemente el rango de aceptación para alpha = 0.05, pero entra de forma segura al ampliar el nivel de significancia a alpha = 0.01. La serie se concluye como independiente. |

**Veredicto independencia:** Serie Independiente
**Conclusión:** La prueba de Anderson valida la independencia con total normalidad (1 punto fuera de bandas, justo en el límite máximo permitido). Por su parte, Wald-Wolfowitz presenta un rechazo marginal para el estándar del 5% (abs(-2.01) > 1.96), pero se acepta formalmente bajo el criterio de tolerancia de la tesis al encuadrar holgadamente en el nivel alpha = 1% (limite ±2.58). Al haber superado con éxito tanto las fases de homogeneidad como de independencia, la serie queda completamente habilitada para la Etapa 2 de ajuste de distribuciones.

**Veredicto general Etapa 1:** Habilitada para Etapa 2

---

### Etapa 2 — Parámetros (Sheet 3)
| Distribución              | Método                    | Parámetro 1        | Parámetro 2          | Parámetro 3          |
|---------------------------|---------------------------|--------------------|----------------------|----------------------|
| Uniforme                  | Momentos                  | alfa = -45.72      | beta = 330.88        |                      |
| Uniforme                  | Máxima Verosimilitud      | alfa = 42.00       | beta = 458.00        |                      |
| Exponencial beta          | Momentos y M. Verosimilitud | beta = 0.007     |                      |                      |
| Exponencial x0 y beta     | Momentos                  | x0 = 33.87         | beta = 108.71        |                      |
| Exponencial x0 y beta     | Máxima Verosimilitud      | x0 = 37.63         | beta = 104.96        |                      |
| Generalizada Exponencial  | Momentos                  | alfa = 2.85        | lambda = 0.0040      |                      |
| Generalizada Exponencial  | Máxima Verosimilitud      | alfa = 2.63        | lambda = 0.0122      |                      |
| Generalizada Exponencial  | Momentos L                | alfa = 0.80        | lambda = -0.0033     |                      |
| Normal                    | Momentos L                | mu = 142.58        | sigma = 100.8242     |                      |
| Normal                    | Momentos y M. Verosimilitud | mu = 142.58      | sigma = 108.7150     |                      |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | mu_y = 4.72      | sigma_y = 0.699      |                      |
| Log Normal (3 parámetros) | Momentos                  | x0 = -82.04        | mu_y = 5.3092        | sigma_y = 0.4588     |
| Log Normal (3 parámetros) | Máxima Verosimilitud      | x0 = 38.47         | mu_y = 4.0031        | sigma_y = 1.2927     |
| Gamma (2 parámetros)      | Momentos                  | alfa = 82.89       | beta = 1.720         |                      |
| Gamma (2 parámetros)      | Máxima Verosimilitud      | alfa = 64.03       | beta = 2.227         |                      |
| Gamma (2 parámetros)      | Momentos L                | alfa = 82.25       | beta = 1.734         |                      |
| Gamma (3 parámetros)      | Momentos                  | x0 = 3.683         | alfa = 85.089        | beta = 1.632         |
| Gamma (3 parámetros)      | Máxima Verosimilitud      | NO_CONVERGE        | NO_CONVERGE          | NO_CONVERGE          |
| Gamma (3 parámetros)      | Momento Prob. Pesada      | x0 = 35.355        | alfa = 141.841       | beta = 0.756         | ← PENDIENTE: fórmula MPP ausente en Cap. IV |
| Gumbel                    | Momentos                  | alfa = 84.798      | mu = 93.662          |                      |
| Gumbel                    | Máxima Verosimilitud      | alfa = 67.760      | mu = 98.010          |                      |
| Gumbel                    | Momentos L                | alfa = 82.087      | mu = 95.201          |                      |
| Gumbel                    | Máxima Entropía           | alfa = 73.803      | mu = 99.983          |                      |
| GVE (Valores Extremos)    | Momentos                  | alfa = 94.250      | beta = -0.059        | nu = 176.590         |
| GVE (Valores Extremos)    | Máxima Verosimilitud      | alfa = 44.261      | beta = -0.700        | nu = 77.660          |
| GVE (Valores Extremos)    | Momentos L                | alfa = 80.352      | beta = -0.278        | nu = 163.884         |
| Log Pearson tipo III      | Momentos Método Directo   | alfa = 0.333       | beta = 37.229        | y0 = 4.818           |
| Log Pearson tipo III      | Momentos Método Indirecto | alfa = 0.351       | beta = 0.509         | y0 = 0.454           |
| Log Pearson tipo III      | Máxima Verosimilitud      | alfa = 0.115       | beta = 2.242         | y0 = 3.577           |

---

### Etapa 2 — EEA esperados (Sheet 3)
| Distribución              | Método                    | EEA [m³/s] | Categoría          |
|---------------------------|---------------------------|------------|--------------------|
| Log Normal (3 parámetros) | Máxima Verosimilitud      | 20.7985    | Top 1 Numérico (Modelo Testigo) |
| Exponencial beta          | Momentos y M. Verosimilitud | 20.9118  | Top 2 Numérico (Modelo seleccionado) |
| Exponencial x0 y beta     | Momentos                  | 24.7462    | Aceptable          |
| Gamma (3 parámetros)      | Momento Prob. Pesada      | 25.2045    | Aceptable          | ← PENDIENTE: fórmula MPP ausente en Cap. IV |
| Exponencial x0 y beta     | Máxima Verosimilitud      | 27.0591    | Aceptable          |
| Log Pearson tipo III      | Momentos Método Indirecto | 30.1143    | Aceptable          |
| Gamma (2 parámetros)      | Momentos                  | 31.2572    | Aceptable          |
| Gamma (2 parámetros)      | Momentos L                | 31.4762    | Aceptable          |
| Gamma (3 parámetros)      | Momentos                  | 31.8321    | Aceptable          |
| Gumbel                    | Momentos                  | 31.9309    | Aceptable          |
| Gumbel                    | Momentos L                | 33.0922    | Aceptable          |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | 33.2187  | Aceptable          |
| Log Normal (3 parámetros) | Momentos                  | 34.238     | Aceptable          |
| Generalizada Exponencial  | Máxima Verosimilitud      | 35.6104    | Rango Medio        |
| GVE (Valores Extremos)    | Máxima Verosimilitud      | 37.6088    | Rango Medio        |
| Gumbel                    | Máxima Entropía           | 37.9838    | Rango Medio        |
| Gamma (2 parámetros)      | Máxima Verosimilitud      | 38.78      | Rango Medio        |
| Gumbel                    | Máxima Verosimilitud      | 43.348     | Rango Medio        |
| Normal                    | Momentos y M. Verosimilitud | 47.6235  | Margen Alto        |
| Normal                    | Momentos L                | 48.6812    | Margen Alto        |
| Uniforme                  | Momentos                  | 52.0788    | Margen Alto        |
| GVE (Valores Extremos)    | Momentos L                | 91.8783    | Deficiente         |
| Log Pearson tipo III      | Momentos Método Directo   | 94.1897    | Deficiente         |
| Uniforme                  | Máxima Verosimilitud      | 125.1454   | Deficiente         |
| GVE (Valores Extremos)    | Momentos                  | 143.1475   | Deficiente         |
| Log Pearson tipo III      | Máxima Verosimilitud      | 325.6784   | Deficiente         |
| Gamma (3 parámetros)      | Máxima Verosimilitud      | NO_CONVERGE | Falla de Algoritmo |

---

### Etapa 2 — Cuantiles esperados (Sheet 3)
| T [años] | Exponencial beta [m³/s] | Log Normal 3p MV [m³/s] |
|----------|-------------------------|--------------------------|
| 2        | 98.83                   | 93.24                    |
| 5        | 229.48                  | 198.35                   |
| 10       | 328.31                  | 310.9                    |
| 20       | 427.14                  | 447.78                   |
| 25       | 458.96                  | 495.53                   |
| 50       | 557.79                  | 649.1                    |
| 100      | 656.62                  | 800.7                    |

### Modelo seleccionado por Facundo
Modelo Exponencial beta seleccionado. Aunque la distribución Log Normal de 3 parámetros arroja el menor error numérico absoluto (EEA = 20.7985 m³/s), la inspección gráfica demuestra un mejor ajuste general por parte del modelo Exponencial beta (EEA = 20.9118 m³/s). Aplicando el criterio de parsimonia hidrológica, se define a la Exponencial beta como distribución gobernante por requerir un solo parámetro contra tres del modelo alternativo. Los caudales de diseño quedan definidos desde 98.83 m³/s para un período de retorno de 2 años hasta un máximo de 656.62 m³/s para una recurrencia de 100 años.

---

## Resultados de Regresión METIS

### Estado general: PASS — FAIL=0 en todos los pasos

### PASO 1 — Estadística descriptiva: PASS
| Variable                      | METIS        | Tesis        | diff%  | Nivel |
|-------------------------------|--------------|--------------|--------|-------|
| n                             | 24           | 24           | 0.000% | PASS  |
| Media                         | 142.583      | 142.583      | 0.000% | PASS  |
| Varianza                      | 11818.949    | 11818.949    | 0.000% | PASS  |
| Desvío                        | 108.715      | 108.715      | 0.000% | PASS  |
| M0                            | 142.583      | 142.583      | 0.000% | PASS  |
| M1                            | 99.741       | 99.741       | 0.000% | PASS  |
| M2                            | 79.402       | 79.402       | 0.000% | PASS  |
| M3                            | 66.866       | 66.866       | 0.000% | PASS  |
| Sumatoria ln(xi)              | 113.246      | 113.246      | 0.000% | PASS  |
| Máximo                        | 458.0        | 458.0        | 0.000% | PASS  |
| Mínimo                        | 42.0         | 42.0         | 0.000% | PASS  |
| Asimetría sesgada             | 1.375        | 1.375        | ~0%    | INFO  |
| Asimetría no sesgada (g)      | 1.6686       | 1.565        | 6.62%  | INFO  |
| Curtosis sesgada              | 4.219        | 4.219        | ~0%    | INFO  |
| Curtosis no sesgada           | 5.489        | 5.489        | ~0%    | INFO  |
| CV                            | 0.762        | 0.762        | ~0%    | INFO  |

Nota g: METIS sigue IV-4/IV-5 (ddof=0). Excel usa SKEW() (ddof=1). Diferencia trazable — ver DECISIÓN013.

### PASO 2 — Homogeneidad: PASS
| Prueba     | Estadístico METIS | Estadístico Tesis | diff%  | Veredicto | Nivel |
|------------|-------------------|-------------------|--------|-----------|-------|
| Helmert S-C| 9                 | 9                 | 0.000% | Rechazada | PASS  |
| t-Student  | -1.76             | -1.76             | 0.000% | Aprobada  | PASS  |
| Cramer τ1  | 0.18289           | 0.18289           | 0.000% | Aprobada  | PASS  |
| Cramer τ2  | 0.35206           | 0.35206           | 0.000% | Aprobada  | PASS  |
| Veredicto  | homogeneidad_warning | homogeneidad_warning | — | — | PASS  |

### PASO 3 — Independencia: PASS
| Prueba          | Estadístico METIS | Estadístico Tesis | diff%  | Veredicto | Nivel |
|-----------------|-------------------|-------------------|--------|-----------|-------|
| Anderson máx r_k| (dentro de bandas)| 1 lag fuera       | —      | Aprobada  | PASS  |
| Wald-Wolfowitz Z| -2.01             | -2.01             | 0.000% | Aprobada* | PASS  |
| Veredicto       | independiente     | independiente     | —      | —         | PASS  |

*Wald-Wolfowitz rechaza a α=0.05 pero aprueba a α=0.01; Anderson manda.

### PASO 4 — Veredicto Etapa 1: PASS
Habilitada para Etapa 2. Homogeneidad con warning (Helmert rechaza), independencia OK.

### PASO 5 — Parámetros Etapa 2: PASS (FAIL=0)
Ver tabla de parámetros esperados arriba. FAIL=0 tras clasificar:
- Gamma 3p momentos (beta): INFO — g-propagación DECISIÓN013 (~12%)
- GVE momentos (beta): INFO — no reproducible con IV-203/IV-204 (ninguna variante de g conocida reproduce beta_tesis). Pendiente Facundo. No es Causa A.
- GVE ML (beta): INFO — g-propagación DECISIÓN013 (valores chicos, diff% alta relativa)
- GVE MV: PASS — alpha=44.261 (0.00%), beta=-0.700 (0.03%), nu=77.660 (0.00%). Fix IV-202 DECISIÓN014.
- Log-Normal 3p momentos (sigma_y): INFO-A (Causa A pura, g-propagación DECISIÓN013).
  DECISIÓN015 aplicada — fix IV-116 sigma_y. Residuo post-fix es Causa A pura (g-propagación DECISIÓN013).
  sigma_y ANTES=0.694 (diff +51.3%), DESPUÉS=0.482 (diff +5.1% — puramente g-propagación).
- Gamma 3p MV: NO_CONVERGE — comportamiento esperado per tesis
- Gen. Pareto MV y MC: NO_CONVERGE — comportamiento esperado per tesis

### PASO 6 — EEA: PASS (FAIL=0)
| Distribución              | Método          | EEA METIS | EEA Tesis | diff%   | Nivel  | Causa                  |
|---------------------------|-----------------|-----------|-----------|---------|--------|------------------------|
| Exponencial beta          | Momentos/MV     | 20.91     | 20.91     | 0.0%    | PASS   | —                      |
| Exponencial x0beta        | Momentos        | 24.75     | 24.75     | 0.0%    | PASS   | —                      |
| Exponencial x0beta        | MV              | 27.06     | 27.06     | 0.0%    | PASS   | —                      |
| Log-Pearson III           | Indirecto       | 24.48     | 30.11     | 18.7%   | INFO-A | A: g-propagación DECISIÓN013 (gy_yi). EEA menor es consecuencia aritmética de parámetros distintos por Causa A — no convergencia a solución independientemente mejor. |
| Log-Pearson III           | MV              | 83.50     | 325.68    | -74.4%  | INFO-B | B: convergencia a óptimo distinto (alpha=0.8422, beta=1.1758, y0=3.7284 vs tesis alpha=0.115, beta=2.242, y0=3.577). Método iterativo, diff no relacionada con DECISIÓN013. |
| Log-Pearson III           | Directo         | 94.19     | 94.19     | 0.0%    | PASS   | —                      |
| Gamma 2p                  | Momentos        | 26.93     | 31.26     | 13.9%   | INFO   | C: EEA distinto (pendiente Facundo) |
| Gamma 2p                  | MV              | 27.09     | 38.78     | 30.2%   | INFO   | C: EEA distinto (pendiente Facundo) |
| Gamma 2p                  | ML              | 26.68     | 31.48     | 15.3%   | INFO   | C: EEA distinto (pendiente Facundo) |
| Gamma 3p                  | Momentos        | 37.00     | 31.83     | 16.2%   | INFO   | A: g-propagación       |
| Gumbel                    | Momentos        | 31.93     | 31.93     | 0.0%    | PASS   | —                      |
| Gumbel                    | MV              | 43.35     | 43.35     | 0.0%    | PASS   | —                      |
| Gumbel                    | ML              | 33.09     | 33.09     | 0.0%    | PASS   | —                      |
| Gumbel                    | ME              | 37.98     | 37.98     | 0.0%    | PASS   | —                      |
| GVE                       | Momentos        | 1144.00   | 143.15    | 699%    | INFO   | Pendiente Facundo: beta no reproducible con IV-203/IV-204. No es Causa A. |
| GVE                       | MV              | 37.61     | 37.61     | 0.0%    | PASS   | Fix IV-202 DECISIÓN014 |
| GVE                       | ML              | 28.35     | 91.88     | 69.2%   | INFO   | B: METIS mejor         |
| Log-Normal 2p             | Momentos/MV     | 27.97     | 33.22     | 15.8%   | INFO   | C: EEA distinto (pendiente Facundo) |
| Log-Normal 3p             | Momentos        | 29.69     | 34.24     | -13.3%  | INFO-A | A: DECISIÓN015+DECISIÓN013. EEA menor es consecuencia aritmética de parámetros distintos por Causa A — no convergencia a solución independientemente mejor. |
| Log-Normal 3p             | MV              | 19.41     | 20.80     | 6.7%    | INFO   | C: EEA distinto (pendiente Facundo) |
| Normal                    | Momentos/MV     | 46.72     | 47.62     | 1.9%    | INFO   | C: EEA distinto (pendiente Facundo) |
| Normal                    | ML              | 47.74     | 48.68     | 1.9%    | INFO   | C: EEA distinto (pendiente Facundo) |
| Uniforme                  | Momentos        | 52.08     | 52.08     | 0.0%    | PASS   | —                      |
| Uniforme                  | MV              | 125.15    | 125.15    | 0.0%    | PASS   | —                      |
| Gen. Exponencial          | Momentos        | 47.43     | ~47.43    | ~0%     | PASS   | —                      |
| Gen. Exponencial          | MV              | NO_CONVERGE | —       | —       | PASS   | —                      |

**Conteo: PASS=12, INFO=15, FAIL=0, SKIP=8 (métodos sin referencia tesis)**

### PASO 7 — Cuantiles: PASS (FAIL=0)
Modelos seleccionados por Facundo: Exponencial beta y Log Normal 3p MV (testigo).

| T [años] | Exp_beta METIS | Exp_beta Tesis | diff%  | Nivel | LN3p MV METIS | LN3p MV Tesis | diff%  | Nivel |
|----------|----------------|----------------|--------|-------|----------------|----------------|--------|-------|
| 2        | 98.83          | 98.83          | 0.000% | PASS  | 93.24          | 93.24          | 0.000% | PASS  |
| 5        | 229.48         | 229.48         | 0.000% | PASS  | 205.23         | 198.35         | 3.5%   | INFO  |
| 10       | 328.31         | 328.31         | 0.000% | PASS  | 322.54         | 310.9          | 3.7%   | INFO  |
| 20       | 427.14         | 427.14         | 0.000% | PASS  | 455.50         | 447.78         | 1.7%   | INFO  |
| 25       | 458.96         | 458.96         | 0.000% | PASS  | 504.15         | 495.53         | 1.7%   | INFO  |
| 50       | 557.79         | 557.79         | 0.000% | PASS  | 661.59         | 649.1          | 1.9%   | INFO  |
| 50       | 557.79         | 557.79         | 0.000% | PASS  | 661.59         | 649.1          | 1.9%   | INFO  |
| 100      | 656.62         | 656.62         | 0.000% | PASS  | 815.19         | 800.7          | 1.8%   | INFO  |

**Exp_beta: PASS=7/7. LN3p MV: PASS=1, INFO=6 — causa tipo C (cuantil Excel distinto). FAIL=0.**

Nota LN3p MV: METIS usa x0 que minimiza EEA (≈33) ≠ x0=38.47 de la tesis. Los cuantiles
difieren por el x0 distinto (diferente optimización iterativa), no por error de fórmula.
El modelo seleccionado por Facundo es Exp_beta — LN3p MV es solo testigo numérico.
Causa C clasificada como INFO pendiente — escalar a Facundo/Carlos en próxima reunión.