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

**Estación nueva (no forma parte de las 5 de Bloque 8 original est_02-06).**
n=43 efectivo sobre 46 años de registro — 3 valores "(S/D - Faltante)"
descartados por `filtrar_numericos()` antes de llegar a las pruebas
estadísticas, mismo mecanismo ya usado para otras estaciones con datos
faltantes. Ver también: la tabla de parámetros de esta estación en la ficha
de Facundo (arriba) es la que estaba (correctamente) duplicada en la vieja
ficha de est_07 antes de la corrección de esta sesión.

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
| n | 43 |
| Media [m³/s] | 156.66255813953487 |
| Mediana [m³/s] | 138.2 |
| Varianza (no sesgada) [m³/s]² | 7776.1139337763 |
| Varianza (sesgada) [m³/s]² | 7595.27407485127 |
| Desvío [m³/s] | 88.18227675545863 |
| Asimetría Sesgada | 0.8854396467464469 |
| Asimetría No Sesgada (g) | 0.9507421061754822 |
| Curtosis Sesgada | 3.1575598640186344 |
| Curtosis No Sesgada (k) | 3.6447170747463637 |
| Coeficiente de Variación (CV) | 0.5628803576468935 |
| Sumatoria ln(xi) | 210.58065102124252 |
| beta_0 = M0 | 156.6625581395349 |
| beta_1 = M1 | 102.9012292358804 |
| beta_2 = M2 | 78.54160629878724 |
| beta_3 = M3 | 64.14761423304432 |
| Máximo [m³/s] | 407.9 |
| Mínimo [m³/s] | 39.2 |
| Rango [m³/s] | 368.7 |

### Etapa 1 — Homogeneidad (pipeline completo — Sheet 2)

#### Helmert
| Parámetro | Valor |
|-----------|-------|
| Estadístico (S-C) | 20.0 |
| Valor crítico (± lim) | 6.48074069840786 |
| Veredicto | rechazada |
| Warning | TEST_WARNING_HOMOGENEITY |

#### t de Student
| Parámetro | Valor |
|-----------|-------|
| Estadístico t | 1.1167184494081261 |
| n1 | 21 |
| n2 | 22 |
| Valor crítico (tabla) | 2.019540970441376 |
| Veredicto | aprobada |

#### Cramer
| Parámetro | Valor |
|-----------|-------|
| Estadístico (max t_w) | 2.392736952358205 |
| n_w1 | 26 |
| n_w2 | 13 |
| Valor crítico (tabla) | 2.019540970441376 |
| Veredicto | rechazada |
| Warning | TEST_CRITICAL_HOMOGENEITY |

**Veredicto homogeneidad (pipeline):** homogeneidad_critica

### Etapa 1 — Independencia (pipeline completo — Sheet 2)

#### Anderson
| Parámetro | Valor |
|-----------|-------|
| Estadístico (máx r_k) | 0.39728244753529035 |
| Valor crítico | 0.2749974498548543 |
| Veredicto | aprobada |

#### Wald-Wolfowitz
| Parámetro | Valor |
|-----------|-------|
| Estadístico Z | -3.1958166719691237 |
| Valor crítico (α=0.05) | ± 1.959963984540054 |
| Veredicto | rechazada |
| Warning | None |

**Veredicto independencia (pipeline):** independiente

### Etapa 1 — Tendencia y Atípicos (pipeline completo) — sin ficha de Facundo de referencia
Mann-Kendall, Kolmogorov-Smirnov y Chow no están en la tesis de Facundo (los
agregó Carlos) — no hay valor "esperado" ni "METIS unitario" previo contra el
cual comparar estas tres filas.

#### Mann-Kendall
| Parámetro | Valor |
|-----------|-------|
| Estadístico | -2.6269644113314934 |
| Valor crítico | 1.959963984540054 |
| Veredicto | rechazada |
| Warning | TEST_WARNING_TREND |

#### Kolmogorov-Smirnov (tendencia)
| Parámetro | Valor |
|-----------|-------|
| Estadístico (Z tipificado) | 1.021662084980371 |
| Valor crítico | 1.358 |
| Veredicto | aprobada |
| Warning | None |

#### Chow
| Parámetro | Valor |
|-----------|-------|
| Estadístico (máx Z_i) | 2.119311285762318 |
| Valor crítico (K_N) | 2.8970234886236836 |
| Veredicto | aprobada |

**Veredicto general Etapa 1 (pipeline):** nivel_confianza=`con_warnings` — warnings: TEST_CRITICAL_HOMOGENEITY, TEST_WARNING_TREND

### Etapa 2 — Parámetros, EEA y Estado (pipeline completo — Sheet 3)
| Distribución | Método | Parámetro 1 | Parámetro 2 | Parámetro 3 | EEA [m³/s] | Status |
|---|---|---|---|---|---|---|
| Uniforme | Momentos | alfa = 3.9264 | beta = 309.3987 |  | 26.8884 | ok |
| Uniforme | Máxima Verosimilitud | alfa = 39.2000 | beta = 407.9000 |  | 76.5562 | ok |
| Exponencial beta | Momentos | beta = 0.006383 |  |  | 52.3252 | ok |
| Exponencial beta | Máxima Verosimilitud | beta = 0.006383 |  |  | 52.3252 | ok |
| Exponencial x0 y beta | Momentos | x0 = 68.4803 | beta = 88.1823 |  | 16.5295 | ok |
| Exponencial x0 y beta | Máxima Verosimilitud | x0 = 36.4033 | beta = 120.2593 |  | 23.0922 | ok |
| Generalizada Exponencial | Momentos | alfa = 4.2001 | lambda = 0.013575 |  | 11.4949 | ok |
| Generalizada Exponencial | Máxima Verosimilitud | alfa = 4.1430 | lambda = 0.01352 |  | 11.3754 | ok |
| Generalizada Exponencial | Momentos L | alfa = 0.432607 | lambda = -0.003866 |  | 394.9707 | ok |
| Normal | Momentos | mu = 156.6626 | sigma = 88.1823 |  | 23.7603 | ok |
| Normal | Máxima Verosimilitud | mu = 156.6626 | sigma = 88.1823 |  | 23.7603 | ok |
| Normal | Momentos L | mu = 156.6626 | sigma = 87.0759 |  | 23.8953 | ok |
| Log Normal (2 parámetros) | Momentos | mu_y = 4.8972 | sigma_y = 0.579692 |  | 10.4100 | ok |
| Log Normal (2 parámetros) | Máxima Verosimilitud | mu_y = 4.8972 | sigma_y = 0.579692 |  | 10.4100 | ok |
| Log Normal (3 parámetros) | Momentos | x0 = -130.3461 | mu_y = 5.6144 | sigma_y = 0.300344 | 12.9488 | ok |
| Log Normal (3 parámetros) | Máxima Verosimilitud | x0 = -0.471535 | mu_y = 4.9014 | sigma_y = 0.570542 | 10.7733 | ok |
| Gamma (2 parámetros) | Momentos | alfa = 49.6361 | beta = 3.1562 |  | 10.9492 | ok |
| Gamma (2 parámetros) | Máxima Verosimilitud | alfa = 46.8192 | beta = 3.3461 |  | 12.7008 | ok |
| Gamma (2 parámetros) | Momentos L | alfa = 52.6469 | beta = 2.9757 |  | 9.3833 | ok |
| Gamma (3 parámetros) | Momentos | x0 = -28.8394 | alfa = 41.9193 | beta = 4.4252 | 12.0018 | ok |
| Gamma (3 parámetros) | Máxima Verosimilitud |  |  |  | — | no_converge |
| Gumbel | Momentos | mu = 116.9805 | alfa = 68.7822 |  | 12.3337 | ok |
| Gumbel | Máxima Verosimilitud | mu = 117.1609 | alfa = 65.1101 |  | 15.8411 | ok |
| Gumbel | Momentos L | mu = 115.7415 | alfa = 70.8939 |  | 10.9252 | ok |
| Gumbel | Máxima Entropía | mu = 117.9291 | alfa = 67.1039 |  | 13.6791 | ok |
| GVE (Valores Extremos) | Momentos | nu = 12,319.9595 | alfa = 67.7419 | beta = -0.011175 | 12,650.1186 | ok |
| GVE (Valores Extremos) | Máxima Verosimilitud | nu = 112.2155 | alfa = 60.8007 | beta = -0.14604 | 12.0014 | ok |
| GVE (Valores Extremos) | Momentos L | nu = 113.6444 | alfa = 66.3490 | beta = -0.067434 | 10.4742 | ok |
| Log Pearson tipo III | Momentos Método Directo |  |  |  | — | no_aplicable |
| Log Pearson tipo III | Momentos Método Indirecto | alfa = 0.044152 | beta = 172.3810 | y0 = -2.7138 | 12.6822 | ok |
| Log Pearson tipo III | Máxima Verosimilitud |  |  |  | — | no_converge |
| Generalizada de Pareto | Momentos | mu = 45.7030 | sigma = 143.3217 | epsilon = 0.291657 | 148.2107 | ok |
| Generalizada de Pareto | Máxima Verosimilitud |  |  |  | — | no_converge |
| Generalizada de Pareto | Mínimos Cuadrados | mu = 39.2000 | sigma = 106.9483 | epsilon = 0.000008 | 21.3019 | ok |
| Generalizada de Pareto | Momento Prob. Pesada | mu = -0.325151 | sigma = 1,886.0845 | epsilon = 4.7186 | 3,595,997,671.0360 | ok |

### Notas de cableado — Bloque 6/7 (solo señalamiento)

**¿Ceros en la serie?** No — mínimo observado = 39.2. `tiene_ceros=False`. La rama `STATUS_DISABLED_ZEROS` sigue sin ejercitarse en ninguna de las estaciones auditadas hasta ahora.

**Cambios de status vs. est_02** (comparando categoría, no valor numérico):
- `gve/momentos`: METIS status=`ok` (con params degenerados, nu/alpha/beta ver tabla) vs tesis=`NO_CONVERGE` — dirección opuesta a lo usual (normalmente es METIS el que no converge donde la tesis sí). No investigado.
- `logpearson3/mv`: METIS status=`no_converge`, coincide con tesis=`NO_CONVERGE` — sin cambio.
- `nivel_homogeneidad` = `homogeneidad_critica` (Cramer rechaza, jerarquía METIS es absoluta) mientras que la tesis narra "Homogénea bajo consideraciones especiales" — ver nota completa en UNITARIAS PASO 2.

**GVE / MV — rama de inicialización:**
- MOMENTOS descartado (guard IV-202 falla, nu0=12319.9595, alpha0=67.7419, beta0=-0.0112) -> fallback a ML
