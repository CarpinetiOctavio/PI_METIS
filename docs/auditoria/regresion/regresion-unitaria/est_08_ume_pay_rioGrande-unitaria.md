## Estación 8 — Ume Pay – Río Grande

### Serie (Sheet 1)
serie = [
    295.92,               # 57-58
    250.07,               # 58-59
    191.15,               # 59-60
    165.3,                # 60-61
    333.7,                # 61-62
    "(S/D - Faltante)",   # 62-63
    "(S/D - Faltante)",   # 63-64
    328.0,                # 64-65
    159.8,                # 65-66
    100.0,                # 66-67
    61.7,                 # 67-68
    39.2,                 # 68-69
    75.5,                 # 69-70
    180.6,                # 70-71
    121.6,                # 71-72
    115.7,                # 72-73
    111.82,               # 73-74
    253.5,                # 74-75
    115.7,                # 75-76
    114.7,                # 76-77
    165.8,                # 77-78
    233.9,                # 78-79
    205.6,                # 79-80
    256.54,               # 80-81
    160.04,               # 81-82
    224.96,               # 82-83
    407.9,                # 83-84
    141.4,                # 84-85
    105.8,                # 85-86
    75.2,                 # 86-87
    122.5,                # 87-88
    195.86,               # 88-89
    88.65,                # 89-90
    202.28,               # 90-91
    292.3,                # 91-92
    "(S/D - Faltante)",   # 92-93
    86.0,                 # 93-94
    84.4,                 # 94-95
    81.2,                 # 95-96
    44.1,                 # 96-97
    138.2,                # 97-98
    47.2,                 # 98-99
    71.6,                 # 99-2000
    84.3,                 # 2000-01
    142.5,                # 2001-02
    64.3,                 # 2002-03
]

**Nota:** 3 datos faltantes (S/D) en 62-63, 63-64 y 92-93. n efectivo = 43 sobre 46 años de registro (57-58 a 2002-03).

### Estadística descriptiva esperada (Sheet 1)
| Variable                        | Valor esperado |
|---------------------------------|----------------|
| n                                | 43             |
| Media [m³/s]                    | 156.657        |
| Varianza [m³/s]²                | 7775.688       |
| Desvío [m³/s]                   | 88.18          |
| Asimetría Sesgada               | 0.855          |
| Asimetría No Sesgada (g)        | 0.918          |
| Curtosis Sesgada                | 3.012          |
| Curtosis No Sesgada (k)         | 3.477          |
| Coeficiente de Variación (CV)   | 0.563          |
| Sumatoria ln(xi)                | 210.578        |
| beta_0 = M0                     | 156.657        |
| beta_1 = M1                     | 102.898        |
| beta_2 = M2                     | 78.539         |
| beta_3 = M3                     | 64.145         |
| Máximo [m³/s]                   | 407.86         |
| Mínimo [m³/s]                   | 39.2           |

---

### Etapa 1 — Homogeneidad (Sheet 2)

#### Helmert
| Parámetro              | Valor esperado |
|------------------------|----------------|
| N° de Series (S)       | 31             |
| N° de Cambios (C)      | 11             |
| Estadístico (S-C)      | 20             |
| n                      | 43             |
| Umbral inferior        | -6.48          |
| Umbral superior        | 6.48           |
| Conclusión individual  | El estadístico (S - C) no está comprendido entre -(nj-1)^0,5 y +(nj-1)^0,5. Por lo tanto la serie No es Homogénea. |

#### t de Student
| Parámetro              | Valor esperado |
|------------------------|----------------|
| Estadístico t          | 1.47           |
| Grados de libertad     | 41             |
| Valor crítico (tabla)  | 1.6829         |
| Conclusión individual  | El valor absoluto del estadístico t es menor que el valor de tabla de t para 41 grados de libertad (G.L.) y para un nivel de significancia: α = 5%. Por lo tanto la serie es Homogénea. |

#### Cramer
| Parámetro              | Valor esperado |
|------------------------|----------------|
| tau subgrupo 1         | -0.10293       |
| tau subgrupo 2         | -0.53174       |
| t calculado sg. 1      | 0.82176        |
| t calculado sg. 2      | 2.3927         |
| Valor crítico (tabla)  | 1.6829         |
| Conclusión individual  | Solo el valor absoluto del estadístico t (subgrupo 1) es mayor que... [texto de la celda con orden invertido, ver nota] el valor de tabla de t para 41 G.L. y para α = 5%. La serie es Homogénea. |

**Veredicto homogeneidad:** Serie Homogénea (Aprobada bajo consideraciones especiales)
**Conclusión:** Se registraron resultados dispares: Helmert rechaza (20 fuera de ±6,48) y Cramer presenta un comportamiento mixto. Sin embargo, bajo el criterio metodológico de la tesis, se acepta la homogeneidad de la serie debido a que la prueba t de Student es completamente favorable y uno de los subgrupos de Cramer ratifica la estabilidad con alpha = 5% para sus 41 G.L. La serie es consistente para la Etapa 2.

**Nota — ANOMALÍA:** Helmert rechaza (S-C=20, fuera de ±6.48) y Cramer es mixto (t_w2=2.3927 supera el crítico 1.6829, t_w1=0.82176 no lo supera). Veredicto final homogéneo por desempate favorable de t de Student + un subgrupo de Cramer, no por unanimidad ni mayoría simple de las 3 pruebas — criterio "consideraciones especiales" explícito de la tesis.

---

### Etapa 1 — Independencia (Sheet 2)

#### Anderson
| Parámetro                              | Valor esperado |
|----------------------------------------|----------------|
| n                                      | 43             |
| k = n/3                                | 14.3           |
| k adoptado                             | 15             |
| Media                                  | 156.66         |
| N° máximo puntos fuera de bandas       | 1,5 (se redondea a 1) |
| N° puntos fuera de bandas              | 1              |
| Conclusión individual                  | Aceptada (1 punto fuera no supera el límite admisible de 1,5). Se acepta la hipótesis de que las variables de la serie son Independientes. |

#### Wald-Wolfowitz
| Parámetro                    | Valor esperado |
|------------------------------|----------------|
| n                            | 43             |
| n1                           | 19             |
| n2                           | 24             |
| R (rachas observadas)        | 12             |
| Media teórica de R           | 22.21          |
| Varianza teórica de R        | 10.21          |
| Estadístico Z                | -3.2           |
| Valor crítico α=0.05         | ± 1.96         |
| Valor crítico α=0.01         | ± 2.58         |
| Conclusión individual        | Rechazada. El estadístico Z = -3,20 se encuentra fuera de los rangos críticos para ambos niveles de significancia (alpha = 0,05 y alpha = 0,01). Sin embargo, se supedita al criterio de aceptación general de la Tesis. |

**Veredicto independencia:** Serie Independiente (Aprobada bajo criterio especial)
**Conclusión:** Se registra un rechazo crítico en la prueba de Wald-Wolfowitz (Z = -3,20 fuera de los límites de tabla). No obstante, aplicando el criterio de aceptación jerárquico establecido en la metodología de la tesis, la serie se declara independiente debido al resultado favorable y prioritario de la prueba de Anderson (1 punto fuera de bandas, bajo el límite de 1,5). Al haber superado las fases de homogeneidad e independencia, la serie queda habilitada para la Etapa 2.

**Nota — ANOMALÍA:** Wald-Wolfowitz rechaza de forma dura (Z=-3.20, fuera de ±1.96 y de ±2.58) y aun así el veredicto final es "Independiente", apoyado únicamente en Anderson. Es la anomalía más fuerte vista hasta ahora en las estaciones transcriptas — no es un caso de tolerancia marginal (como Est02 o Est06), es un rechazo categórico subordinado por jerarquía de criterio de la tesis.

**Veredicto general Etapa 1:** Habilitada para Etapa 2 (bajo criterios especiales en ambas pruebas — Homogeneidad e Independencia)

---

### Etapa 2 — Parámetros (Sheet 3)
| Distribución              | Método                    | Parámetro 1        | Parámetro 2          | Parámetro 3          |
|---------------------------|---------------------------|--------------------|----------------------|----------------------|
| Uniforme                  | Momentos                  | alfa = 3.92        | beta = 309.39        |                      |
| Uniforme                  | Máxima Verosimilitud      | alfa = 39.2         | beta = 407.86        |                      |
| Exponencial beta          | Momentos y M. Verosimilitud | beta = 0.006     |                      |                      |
| Exponencial x0 y beta     | Momentos                  | x0 = 68.48         | beta = 88.18         |                      |
| Exponencial x0 y beta     | Máxima Verosimilitud      | x0 = 36.4          | beta = 120.25        |                      |
| Generalizada Exponencial  | Momentos                  | alfa = 2.26        | lambda = 0.0121      |                      |
| Generalizada Exponencial  | Máxima Verosimilitud      | alfa = 4.14        | lambda = 0.0135      |                      |
| Generalizada Exponencial  | Momentos L                | alfa = 0.76        | lambda = -0.0032     |                      |
| Normal                    | Momentos L                | mu = 156.66        | sigma = 87.0747      |                      |
| Normal                    | Momentos y M. Verosimilitud | mu = 156.66      | sigma = 88.1799      |                      |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | mu_y = 4.9       | sigma_y = 0.58       |                      |
| Log Normal (3 parámetros) | Momentos                  | x0 = -140.11       | mu_y = 5.6506        | sigma_y = 0.2909     |
| Log Normal (3 parámetros) | Máxima Verosimilitud      | x0 = -0.51         | mu_y = 4.9016        | sigma_y = 0.5704     |
| Gamma (2 parámetros)      | Momentos                  | alfa = 49.64       | beta = 3.156         |                      |
| Gamma (2 parámetros)      | Máxima Verosimilitud      | alfa = 46.82       | beta = 3.346         |                      |
| Gamma (2 parámetros)      | Momentos L                | alfa = 52.65       | beta = 2.976         |                      |
| Gamma (3 parámetros)      | Momentos                  | x0 = -35.53        | alfa = 40.459        | beta = 4.75          |
| Gamma (3 parámetros)      | Máxima Verosimilitud      | x0 = 34.351        | alfa = 72.623        | beta = 1.684         |
| Gamma (3 parámetros)      | Momento Prob. Pesada      | x0 = 12.529        | alfa = 62.359        | beta = 2.311         | ← PENDIENTE: fórmula MPP ausente en Cap. IV |
| Gumbel                    | Momentos                  | alfa = 68.78       | mu = 116.976         |                      |
| Gumbel                    | Máxima Verosimilitud      | alfa = 65.111      | mu = 117.156         |                      |
| Gumbel                    | Momentos L                | alfa = 70.893      | mu = 115.736         |                      |
| Gumbel                    | Máxima Entropía           | alfa = 67.104      | mu = 117.923         |                      |
| GVE (Valores Extremos)    | Momentos                  | NO_CONVERGE        | NO_CONVERGE          | NO_CONVERGE          |
| GVE (Valores Extremos)    | Máxima Verosimilitud      | alfa = 60.806      | beta = -0.146        | nu = 112.214         |
| GVE (Valores Extremos)    | Momentos L                | alfa = 74.766      | beta = -0.067        | nu = 238.514         |
| Log Pearson tipo III      | Momentos Método Directo   | alfa = 0.036       | beta = 157.69        | y0 = 4.967           |
| Log Pearson tipo III      | Momentos Método Indirecto | alfa = 0.043       | beta = 184.2         | y0 = -2.971          |
| Log Pearson tipo III      | Máxima Verosimilitud      | NO_CONVERGE        | NO_CONVERGE          | NO_CONVERGE          |

**Nota — VERIFICACIÓN CRUZADA:** Esta tabla de parámetros es numéricamente idéntica a la transcripta para Est 07 (Tincunaco). Se verificó matemáticamente contra los momentos reales de la serie de Ume Pay (n=43, media=156.657, varianza=7775.688): Normal por Momentos reproduce la media exacta (156.66) y Uniforme por Momentos reproduce media≈156.655 y varianza≈7776 — consistentes con Ume Pay, no con Tincunaco (n=19, media=52.695). **Conclusión: estos parámetros pertenecen genuinamente a Ume Pay. La misma tabla en el MD de Est 07 (Tincunaco) está contaminada con estos valores y debe corregirse — pendiente de re-transcripción desde el Excel original de Tincunaco.**

---

### Etapa 2 — EEA esperados (Sheet 3)
| Distribución              | Método                    | EEA [m³/s] |
|---------------------------|---------------------------|------------|
| Gamma (3 parámetros)      | Momento de Probabilidad Pesada | 10.599 |
| Gumbel                    | Momentos L                | 10.9182    |
| Generalizada Exponencial  | Máxima Verosimilitud      | 11.367     |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | 11.4193  |
| Log Pearson tipo III      | Momentos Método Indirecto | 11.5388    |
| Gamma (3 parámetros)      | Máxima Verosimilitud      | 11.6228    |
| GVE (Valores Extremos)    | Máxima Verosimilitud      | 11.9944    |
| Gumbel                    | Momentos                  | 12.3281    |
| Log Normal (3 parámetros) | Máxima Verosimilitud      | 12.6072    |
| Gamma (2 parámetros)      | Momentos L                | 12.9186    |
| Gumbel                    | Máxima Entropía           | 13.6727    |
| Gamma (2 parámetros)      | Momentos                  | 14.6747    |
| Gamma (3 parámetros)      | Momentos                  | 15.5852    |
| Gumbel                    | Máxima Verosimilitud      | 15.8341    |
| Log Normal (3 parámetros) | Momentos                  | 16.3745    |
| Gamma (2 parámetros)      | Máxima Verosimilitud      | 16.474     |
| Exponencial x0 y beta     | Momentos                  | 16.5277    |
| Exponencial x0 y beta     | Máxima Verosimilitud      | 23.0883    |
| Normal                    | Momentos y M. Verosimilitud | 24.4824  |
| Normal                    | Momentos L                | 24.7527    |
| Uniforme                  | Momentos                  | 26.8838    |
| Exponencial beta          | Momentos y M. Verosimilitud | 52.3217  |
| Log Pearson tipo III      | Momentos Método Directo   | 76.4185    |
| Uniforme                  | Máxima Verosimilitud      | 76.5387    |
| GVE (Valores Extremos)    | Momentos L                | 131.9477   |
| GVE (Valores Extremos)    | Momentos                  | NO_CONVERGE |
| Log Pearson tipo III      | Máxima Verosimilitud      | NO_CONVERGE |

---

### Etapa 2 — Cuantiles esperados (Sheet 3)
| T [años] | Gumbel (Momentos L) [m³/s] | Gamma 3 parámetros (MPP) [m³/s] |
|----------|------------------------------|-------------------------------------|
| 2        | 141.72                       | 136.85                              |
| 5        | 222.07                       | 222.5                               |
| 10       | 275.27                       | 276.84                              |
| 20       | 326.3                         | 324.14                              |
| 25       | 342.49                       | 337.87                              |
| 50       | 392.36                       | 375.81                              |
| 100      | 441.85                       | 406.77                              |

### Modelo seleccionado por Facundo
Modelo Gumbel (Momentos L) Seleccionado. Para la estación Ume Pay en el Río Grande se presenta un caso de discrepancia menor entre el ajuste numérico y el gráfico. Si bien la distribución Gamma de 3 parámetros (Momentos de Probabilidad Pesada) arrojó el EEA más bajo (10,5990 m³/s), la verificación visual en la Figura VIII-8 demostró un comportamiento superior de la curva Gumbel (Momentos L, EEA = 10,9182 m³/s). En virtud de la calidad gráfica y bajo el principio de parsimonia (menor número de parámetros), se seleccionó a Gumbel como ley de distribución. Los caudales máximos de diseño se estiman desde los 141,72 m³/s (T=2 años) hasta los 441,85 m³/s para una recurrencia extrema centenaria.
---

## Resultados de Regresión METIS --> UNITARIAS

### Estado general: PASS con 3 anomalías nuevas señaladas (valor crítico Cramer/t-Student en PASO 2, veredicto homogeneidad en PASO 2/4, GVE Momentos convergiendo donde tesis no en PASO 5/6) — FAIL=0

### PASO 1 — Estadística descriptiva: PASS
| Variable                      | METIS        | Tesis        | diff%   | Nivel |
|-------------------------------|--------------|--------------|---------|-------|
| n                             | 43           | 43           | 0.000%  | PASS  |
| Media                         | 156.663      | 156.657      | 0.0035%  | PASS  |
| Varianza                      | 7776.114     | 7775.688     | 0.0055%  | PASS  |
| Desvío                        | 88.182       | 88.18        | 0.0026%  | PASS  |
| M0                            | 156.663      | 156.657      | 0.0035%  | PASS  |
| M1                            | 102.901      | 102.898      | 0.0031%  | PASS  |
| M2                            | 78.542       | 78.539       | 0.0033%  | PASS  |
| M3                            | 64.148       | 64.145       | 0.0041%  | PASS  |
| Sumatoria ln(xi)              | 210.581      | 210.578      | 0.0013%  | PASS  |
| Máximo                        | 407.9        | 407.86       | 0.010%  | INFO (ver nota) |
| Mínimo                        | 39.2         | 39.2         | 0.000%  | PASS  |
| Asimetría sesgada             | 0.8854       | 0.855        | 3.56%   | INFO  |
| Asimetría no sesgada (g)      | 0.9507       | 0.918        | 3.57%   | INFO  |
| Curtosis sesgada              | 3.1576       | 3.012        | 4.83%   | INFO  |
| Curtosis no sesgada           | 3.6447       | 3.477        | 4.82%   | INFO  |
| CV                            | 0.5629       | 0.563        | -0.02%   | INFO  |

Nota g/k: mismo patrón DECISIÓN013 (ddof=0 vs Excel SKEW/KURT ddof=1) de las 7 estaciones previas.
Nota Máximo: la serie cruda (dato 83-84) es 407.9, no 407.86 como figura en la tabla de la tesis — diferencia de 0.01%, probablemente un redondeo/transcripción menor de la tesis, no del código (METIS toma el máximo literal de la serie transcripta). No investigado más allá de esto.

### PASO 2 — Homogeneidad: PASS con ANOMALÍA en valor crítico de tabla (ver nota)
| Prueba     | Estadístico METIS | Estadístico Tesis | diff%   | Veredicto | Nivel |
|------------|--------------------|--------------------|---------|-----------|-------|
| Helmert S-C| 20                | 20                 | 0.000%  | Rechazada | PASS  |
| t-Student  | 1.1167             | 1.47               | -24.03%  | Aprobada  | INFO  |
| Cramer (max t_w, n_w1=26/n_w2=13) | 2.3927             | 2.3927 (t_w2 tesis) | 0.00% | Rechazada | INFO |
| Veredicto  | homogeneidad_critica | Homogénea (consideraciones especiales) | — | — | INFO |

**Nota — dos anomalías:**
1. **Valor crítico de tabla:** METIS calcula el crítico de Cramer/t-Student con
   `scipy.stats.t.ppf(0.975, df=41)` = 2.0195 (ν=n-2=41, dos colas, α/2=0.025 —
   Ec. III-8 tal como está documentada). La tesis imprime **1.6829** para esta
   estación en ambas pruebas — ese valor coincide con el crítico de **una
   cola** al 5% para df=41 (`t.ppf(0.95,41)`≈1.6829), no con el de dos colas
   al 2.5%. Es la primera vez que se observa esta discrepancia de convención
   en las 8 estaciones auditadas — en todas las anteriores el crítico de la
   tesis coincidía con el de dos colas de METIS. No investigado más allá de
   señalarlo.
2. **Veredicto de homogeneidad:** con `t_w2=2.3927` (nombrado "max t_w" en el
   campo `estadistico` de `calcular_cramer`, no aparece τ1/τ2 por separado)
   superando el crítico de METIS (2.0195), Cramer rechaza → jerarquía interna
   de METIS (`Cramer rechaza → homogeneidad_critica`, ver constraints.md)
   produce **`homogeneidad_critica`** automáticamente. La tesis, en cambio,
   narra un veredicto "Homogénea bajo consideraciones especiales" — una
   excepción manual explícita del autor que no está codificada en la jerarquía
   simple de METIS. No es un bug: METIS aplica su propia regla documentada de
   forma consistente; la tesis aplica un criterio narrativo más flexible para
   este caso puntual. Ver también nota de PIPELINE COMPLETO más abajo.

### PASO 3 — Independencia: PASS
| Prueba          | Estadístico METIS | Estadístico Tesis | diff%  | Veredicto | Nivel |
|-----------------|--------------------|--------------------|--------|-----------|-------|
| Anderson (k_max=15) | 0.3973 (máx |r_k|, 1 punto fuera) | 1 punto fuera | — | Aprobada | PASS |
| Wald-Wolfowitz Z| -3.1958            | -3.20              | 0.13% | Rechazada | PASS |
| Veredicto       | independiente      | independiente (criterio especial) | — | — | PASS |

Nota: acá sí coincide el mecanismo — Wald-Wolfowitz rechaza con dureza en ambos (Z≈-3.20 en los dos), y el veredicto final "independiente" surge en METIS automáticamente de la jerarquía ya documentada (Anderson manda, ver constraints.md), sin necesitar ninguna excepción narrativa adicional como sí hizo falta en homogeneidad.

### PASO 4 — Veredicto Etapa 1: PASS con divergencia de veredicto en homogeneidad (ver PASO 2)
Habilitada para Etapa 2 en ambos (METIS y tesis coinciden en habilitar). METIS reporta
`nivel_homogeneidad=homogeneidad_critica` (warning crítico) donde la tesis narra
"Homogénea bajo consideraciones especiales" — divergencia de clasificación,
no de la decisión de avanzar a Etapa 2 (ambos avanzan). Independencia OK en
ambos, mismo mecanismo (Anderson manda).

### PASO 5 — Parámetros Etapa 2: PASS (FAIL=0)
| Distribución              | Método            | diff% (por parámetro)                          | Nivel  | Causa |
|----------------------------|-------------------|--------------------------------------------------|--------|-------|
| Uniforme                  | Momentos          | alpha=+0.16%, beta=0.00%                          | PASS   | —     |
| Uniforme                  | MV                | alpha=0.00%, beta=+0.01% (usa max real=407.9)     | PASS   | —     |
| Exponencial beta          | Momentos/MV       | beta=+6.39%                                       | INFO   | tesis usa beta=0.006 redondeado a 1 cifra sig. — diff pequeña en términos absolutos (0.0064 vs 0.006) |
| Exponencial x0beta        | Momentos          | x0=0.00%, beta=0.00%                              | PASS   | —     |
| Exponencial x0beta        | MV                | x0=+0.01%, beta=+0.01%                            | PASS   | —     |
| Gen. Exponencial          | Momentos          | alpha=+85.85%, lambda=+12.19%                     | INFO   | tesis internamente inconsistente — pendiente IV-77, mismo patrón est_02-07 |
| Gen. Exponencial          | MV                | alpha=+0.07%, lambda=+0.15%                       | PASS   | —     |
| Gen. Exponencial          | ML                | alpha=-43.08%, lambda=-20.82%                     | INFO   | pendiente IV-84 (signo ψ(1)), mismo patrón previo |
| Normal                    | Momentos/MV/ML    | todas ≤0.01%                                      | PASS   | —     |
| Log-Normal 2p             | Momentos/MV       | mu_y=-0.06%, sigma_y=-0.05%                       | PASS   | —     |
| Log-Normal 3p             | Momentos          | x0=+6.97%, mu_y=-0.64%, sigma_y=+3.25%            | INFO-A | g-propagación DECISIÓN013 |
| Log-Normal 3p             | MV                | x0=+7.54%, mu_y=0.00%, sigma_y=+0.02%             | INFO   | x0 diverge (7.5%) pese a mu_y/sigma_y casi exactos — anomalía puntual del parámetro de posición, no vista con esta magnitud en MV en otras estaciones (MV normalmente coincide <1% en las 3). No investigado |
| Gamma 2p                  | Momentos/MV/ML    | todas ≤0.01%                                      | PASS   | —     |
| Gamma 3p                  | Momentos          | x0=+18.83%, alpha=+3.61%, beta=-6.84%             | INFO-A | g-propagación DECISIÓN013 (beta=4/g²) |
| Gamma 3p                  | MV                | METIS status=no_converge; tesis x0=34.351, alpha=72.623, beta=1.684 | INFO | mismo patrón ya documentado en est_02 (nota "scan bug" histórica) |
| Gumbel                    | Momentos/MV/ML/ME | todas ≤0.01%                                      | PASS   | —     |
| GVE                       | Momentos          | METIS status=ok (nu=12319.96, alpha=67.74, beta=-0.0112); tesis=NO_CONVERGE | INFO | **anomalía nueva** — dirección opuesta a lo usual (normalmente METIS no converge donde la tesis sí reporta). Ver nota en PIPELINE COMPLETO |
| GVE                       | MV                | alpha=-0.01%, beta=-0.03%, nu=0.00%               | PASS   | —     |
| GVE                       | ML                | alpha=-11.26%, beta=-0.65%, nu=-52.35%            | INFO-B | beta prácticamente coincide, nu/alpha difieren — convergencia a óptimo distinto, mismo patrón est_02-07 |
| Log-Pearson III           | Directo           | NO_APLICABLE (B=2.7178 ∉ (3,6])                   | INFO   | METIS aplica restricción IV-249 correctamente — patrón universal en las 8 estaciones |
| Log-Pearson III           | Indirecto         | alpha=+2.68%, beta=-6.42%, y0=+8.66%              | INFO-A | g-propagación DECISIÓN013 (gy de yi=ln(xi)) |
| Log-Pearson III           | MV                | METIS status=no_converge; tesis=NO_CONVERGE       | PASS   | coincide — sin anomalía |

**Conteo: PASS=15, INFO=6, INFO-A=3, INFO-B=1, FAIL=0. Gen. Pareto no está en la tabla de tesis (SKIP, mismo patrón que est_02-07).**
### PASO 6 — EEA: PASS (FAIL=0)
| Distribución | Método | EEA METIS | EEA Tesis | diff% | Nivel | Causa |
|---|---|---|---|---|---|---|
| Gumbel             | ML         |      10.9252 |   10.9182 |   +0.06% | PASS   |  |
| Gen. Exponencial   | MV         |      11.3754 |    11.367 |   +0.07% | PASS   |  |
| Log-Normal 2p      | Momentos   |      10.4100 |   11.4193 |   -8.84% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Log-Normal 2p      | MV         |      10.4100 |   11.4193 |   -8.84% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Log-Pearson III    | Indirecto  |      12.6822 |   11.5388 |   +9.91% | INFO-A | g-propagación DECISIÓN013 (gy de yi=ln(xi)) |
| Gamma 3p           | MV         | N/A (no_converge) |   11.6228 | —      | INFO   | status distinto — ver PASO5 |
| GVE                | MV         |      12.0014 |   11.9944 |   +0.06% | PASS   |  |
| Gumbel             | Momentos   |      12.3337 |   12.3281 |   +0.05% | PASS   |  |
| Log-Normal 3p      | MV         |      10.7733 |   12.6072 |  -14.55% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Gamma 2p           | ML         |       9.3833 |   12.9186 |  -27.37% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Gumbel             | ME         |      13.6791 |   13.6727 |   +0.05% | PASS   |  |
| Gamma 2p           | Momentos   |      10.9492 |   14.6747 |  -25.39% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Gamma 3p           | Momentos   |      12.0018 |   15.5852 |  -22.99% | INFO   | A: g-propagación DECISIÓN013 |
| Gumbel             | MV         |      15.8411 |   15.8341 |   +0.04% | PASS   |  |
| Log-Normal 3p      | Momentos   |      12.9488 |   16.3745 |  -20.92% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Gamma 2p           | MV         |      12.7008 |    16.474 |  -22.90% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Exponencial x0beta | Momentos   |      16.5295 |   16.5277 |   +0.01% | PASS   |  |
| Exponencial x0beta | MV         |      23.0922 |   23.0883 |   +0.02% | PASS   |  |
| Normal             | Momentos   |      23.7603 |   24.4824 |   -2.95% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Normal             | MV         |      23.7603 |   24.4824 |   -2.95% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Normal             | ML         |      23.8953 |   24.7527 |   -3.46% | INFO   | C: EEA distinto con params casi idénticos (pendiente Facundo) |
| Uniforme           | Momentos   |      26.8884 |   26.8838 |   +0.02% | PASS   |  |
| Exponencial beta   | Momentos   |      52.3252 |   52.3217 |   +0.01% | PASS   |  |
| Exponencial beta   | MV         |      52.3252 |   52.3217 |   +0.01% | PASS   |  |
| Log-Pearson III    | Directo    | N/A (no_aplicable) |   76.4185 | —      | INFO   | status distinto — ver PASO5 |
| Uniforme           | MV         |      76.5562 |   76.5387 |   +0.02% | PASS   |  |
| GVE                | ML         |      10.4742 |  131.9477 |  -92.06% | INFO-B | beta coincide, nu/alpha difieren — convergencia a óptimo distinto |
| Gamma 3p           | MPP        | EXCLUIDO (MPP no implementado, Cap. IV no desarrolla ecuaciones) | 10.599 | — | EXCLUIDO | mismo patrón que las 8 estaciones — MPP para Gamma3p no está implementado en METIS |
| GVE                | Momentos   | 12650.1186 (METIS status=ok) | NO_CONVERGE | — | INFO | ver nota de anomalía en PASO5 |

**Conteo: PASS=15, INFO-C=6, INFO-A=1, INFO=3 (Gen.Exp momentos/ML no están en esta lista de EEA por no estar en tabla tesis — ver PASO5; LP3 Directo/MV sin EEA por status; GVE Momentos anomalía nueva), EXCLUIDO=1, FAIL=0.**

### PASO 7 — Cuantiles: PASS (FAIL=0)
Modelo seleccionado por Facundo: Gumbel (Momentos L). Gamma 3p MPP figura como
testigo en la tesis pero MPP no está implementado en METIS para Gamma 3p
(Cap. IV no desarrolla las ecuaciones) — EXCLUIDO, sin columna METIS posible.

| T [años] | Gumbel ML METIS | Gumbel ML Tesis | diff%   | Nivel |
|----------|------------------|------------------|---------|-------|
|   2      |   141.72     |   141.72    | +0.004% | PASS  |
|   5      |   222.08     |   222.07    | +0.004% | PASS  |
|  10      |   275.28     |   275.27    | +0.003% | PASS  |
|  20      |   326.31     |   326.30    | +0.003% | PASS  |
|  25      |   342.50     |   342.49    | +0.002% | PASS  |
|  50      |   392.37     |   392.36    | +0.001% | PASS  |
| 100      |   441.86     |   441.85    | +0.003% | PASS  |

**Gumbel ML (modelo seleccionado por Facundo): PASS=7/7 — coincide casi exacto en toda la tabla, mismo comportamiento que el testigo Gumbel ML de est_07.**
**Gamma 3p MPP: EXCLUIDO — no implementado en METIS, sin comparación posible.**
