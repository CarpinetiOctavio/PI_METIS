## Estación 1 — Alpa Corral – Río Barrancas

### Serie (Sheet 1)
serie = [
    207.0,                  # 38-39
    158.0,                  # 39-40
    129.0,                  # 40-41
    258.0,                  # 41-42
    236.0,                  # 42-43
    410.0,                  # 43-44
    245.0,                  # 44-45
    219.0,                  # 45-46
    359.0,                  # 46-47
    118.0,                  # 47-48
    290.0,                  # 48-49
    79.0,                   # 49-50
    126.0,                  # 50-51
    141.0,                  # 51-52
    225.0,                  # 52-53
    235.0,                  # 53-54
    356.0,                  # 54-55
    155.0,                  # 55-56
    356.0,                  # 56-57
    356.0,                  # 57-58
    61.0,                   # 58-59
    58.0,                   # 59-60
    148.0,                  # 60-61
    "(S/D - Interrupción)",  # 61-62
    57.0,                   # 62-63
    62.0,                   # 63-64
    57.0,                   # 64-65
    26.0,                   # 65-66
    47.0,                   # 66-67
    25.0,                   # 67-68
    61.0,                   # 68-69
    37.0,                   # 69-70
    36.0,                   # 70-71
    22.0,                   # 71-72
    43.0,                   # 72-73
    35.0,                   # 73-74
    22.0,                   # 74-75
    15.0,                   # 75-76
    19.0,                   # 76-77
    143.0,                  # 77-78
    "(S/D - Interrupción)",  # 78-79
    143.0,                  # 79-80
]

**Nota:** 2 interrupciones (61-62 y 78-79). n efectivo = 40 sobre 42 años de registro (38-39 a 79-80).

### Estadística descriptiva esperada (Sheet 1)
| Variable                        | Valor esperado |
|---------------------------------|----------------|
| n                                | 40             |
| Media [m³/s]                    | 144.725        |
| Varianza [m³/s]²                | 13408.358      |
| Desvío [m³/s]                   | 115.794        |
| Asimetría Sesgada               | 0.706          |
| Asimetría No Sesgada (g)        | 0.762          |
| Curtosis Sesgada                | 2.269          |
| Curtosis No Sesgada (k)         | 2.649          |
| Coeficiente de Variación (CV)   | 0.8            |
| Sumatoria ln(xi)                | 183.385        |
| beta_0 = M0                     | 144.725        |
| beta_1 = M1                     | 104.751        |
| beta_2 = M2                     | 83.065         |
| beta_3 = M3                     | 69.054         |
| Máximo [m³/s]                   | 410.0          |
| Mínimo [m³/s]                   | 15.0           |

---

### Etapa 1 — Homogeneidad (Sheet 2)

#### Helmert
| Parámetro              | Valor esperado |
|------------------------|----------------|
| N° de Series (S)       | 28             |
| N° de Cambios (C)      | 11             |
| Estadístico (S-C)      | 17             |
| n                      | 40             |
| Umbral inferior        | -6.24          |
| Umbral superior        | 6.24           |
| Conclusión individual  | El estadístico (S - C) no está comprendido entre -(nj-1)^0,5 y +(nj-1)^0,5. Por lo tanto la serie No es Homogénea. Rechazada (17 está fuera del rango). |

#### t de Student
| Parámetro              | Valor esperado |
|------------------------|----------------|
| Estadístico t          | 7.28           |
| Grados de libertad     | 38             |
| Valor crítico (tabla)  | 2.0244         |
| Conclusión individual  | El valor absoluto del estadístico t es mayor que el valor de tabla de t para 38 grados de libertad (G.L.) y para un nivel de significancia: α = 5%. Por lo tanto la serie No es Homogénea. |

#### Cramer
| Parámetro              | Valor esperado |
|------------------------|----------------|
| tau subgrupo 1         | -0.4028        |
| tau subgrupo 2         | -0.80725       |
| t calculado sg. 1      | 3.49608        |
| t calculado sg. 2      | 3.83732        |
| Valor crítico (tabla)  | 2.0244         |
| Conclusión individual  | El valor absoluto de ambos t_w es mayor que el valor de tabla de t para 38 G.L. y para α = 5%. La serie No es Homogénea. |

**Veredicto homogeneidad:** Serie NO Homogénea (Rechazada por unanimidad)
**Conclusión:** Las tres pruebas estadísticas rechazan de manera unánime la hipótesis de homogeneidad con alpha = 5%, evidenciando alteraciones numéricas severas en el registro histórico de Alpa Corral. Bajo el criterio metodológico adoptado, la serie queda descartada para la Etapa 2 de análisis de frecuencia de crecidas (ajuste de distribuciones) debido a la falta de estacionariedad.

---

### Etapa 1 — Independencia (Sheet 2)

#### Anderson
| Parámetro                              | Valor esperado |
|----------------------------------------|----------------|
| n                                      | 40             |
| k = n/3                                | 13.3           |
| k adoptado                             | 14             |
| Media                                  | 144.73         |
| N° máximo puntos fuera de bandas       | 1,4 (se redondea a 1) |
| N° puntos fuera de bandas              | 4              |
| Conclusión individual                  | Rechazada (4 puntos fuera supera el límite admisible de 1). No se acepta la hipótesis de que las variables de la serie son Independientes. |

#### Wald-Wolfowitz
| Parámetro                    | Valor esperado |
|------------------------------|----------------|
| n                            | 40             |
| n1                           | 17             |
| n2                           | 23             |
| R (rachas observadas)        | 12             |
| Media teórica de R           | 20.55          |
| Varianza teórica de R        | 9.3            |
| Estadístico Z                | -2.8           |
| Valor crítico α=0.05         | ± 1.96         |
| Valor crítico α=0.01         | ± 2.58         |
| Conclusión individual        | Los resultados indican que la serie no es independiente. Esta conclusión es obtenida tanto para un nivel de significancia α = 0,05, como para un α = 0,01 el cual amplía el rango de aceptación. |

**Veredicto independencia:** Serie NO Independiente (Rechazada por unanimidad)
**Conclusión:** Tanto la prueba de Anderson como la de Wald-Wolfowitz rechazan de manera unánime la hipótesis de independencia. En Anderson, los coeficientes exceden críticamente el límite permitido (4 puntos fuera de las bandas de aceptación frente a 1 permitido), mientras que en Wald-Wolfowitz el estadístico Z = -2,80 supera holgadamente los valores críticos de tabla, incluso para el nivel más exigente (alpha = 1%). Al haber fallado de forma contundente tanto en homogeneidad como en independencia, los datos carecen de aleatoriedad y representatividad estadística, quedando la serie definitivamente descartada para la Etapa 2 de análisis de frecuencia de crecidas.

**Veredicto general Etapa 1:** Serie NO habilitada para Etapa 2 (rechazo unánime en homogeneidad e independencia — 5 de 5 pruebas)

---

### Nota — Habilitación excepcional para Etapa 2

**Texto literal de la fuente (Sheet 3, celda de nota inicial):** *"La estacion Alpa Corral - Rio Barrancas no esta habilitada para aplicarle un analisis de ajuste de frecuencia teorica, dado que no fue aprobada de manera homogenea. Se proveen los datos de los parametros con fines academicos, para continuar con su ejecucion completa."*

Pese al rechazo unánime de Etapa 1, Facundo aplica igualmente el análisis de frecuencia completo (parámetros, EEA, cuantiles, modelo seleccionado) con fines académicos/demostrativos. Esto coincide con lo ya documentado sobre esta estación. Todo lo que sigue debe leerse bajo esa condición: **no es un resultado válido de diseño hidrológico, es un ejercicio de continuidad metodológica.**

---

### Etapa 2 — Parámetros (Sheet 3)
| Distribución              | Método                    | Parámetro 1        | Parámetro 2          | Parámetro 3          |
|---------------------------|---------------------------|--------------------|----------------------|----------------------|
| Uniforme                  | Momentos                  | alfa = -55.84      | beta = 345.29        |                      |
| Uniforme                  | Máxima Verosimilitud      | alfa = 15.0        | beta = 410.0         |                      |
| Exponencial beta          | Momentos y M. Verosimilitud | beta = 0.007     |                      |                      |
| Exponencial x0 y beta     | Momentos                  | x0 = 28.93         | beta = 115.79        |                      |
| Exponencial x0 y beta     | Máxima Verosimilitud      | x0 = 12.04         | beta = 118.51        |                      |
| Generalizada Exponencial  | Momentos                  | NO_CONVERGE        | NO_CONVERGE          |                      |
| Generalizada Exponencial  | Máxima Verosimilitud      | alfa = 8.97        | lambda = 0.0122      |                      |
| Generalizada Exponencial  | Momentos L                | alfa = 0.79        | lambda = -0.0031     |                      |
| Normal                    | Momentos L                | mu = 144.73        | sigma = 114.7836     |                      |
| Normal                    | Momentos y M. Verosimilitud | mu = 144.73      | sigma = 115.7945     |                      |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | mu_y = 3.11      | sigma_y = 1.69       |                      |
| Log Normal (3 parámetros) | Momentos                  | x0 = -320.499      | mu_y = 6.113         | sigma_y = 0.245      |
| Log Normal (3 parámetros) | Máxima Verosimilitud      | x0 = 38.469        | mu_y = 2.907         | sigma_y = 1.647      |
| Gamma (2 parámetros)      | Momentos                  | alfa = 92.65       | beta = 1.562         |                      |
| Gamma (2 parámetros)      | Máxima Verosimilitud      | alfa = 101.16      | beta = 1.431         |                      |
| Gamma (2 parámetros)      | Momentos L                | alfa = 109.64      | beta = 1.32          |                      |
| Gamma (3 parámetros)      | Momentos                  | x0 = -159.149      | alfa = 44.125        | beta = 6.887         |
| Gamma (3 parámetros)      | Máxima Verosimilitud      | NO_CONVERGE        | NO_CONVERGE          | NO_CONVERGE          |
| Gamma (3 parámetros)      | Momento Prob. Pesada      | x0 = -36.302       | alfa = 87.987        | beta = 2.057         | ← PENDIENTE: fórmula MPP ausente en Cap. IV |
| Gumbel                    | Momentos                  | alfa = 90.32       | mu = 92.617          |                      |
| Gumbel                    | Máxima Verosimilitud      | alfa = 86.404      | mu = 200.143         |                      |
| Gumbel                    | Momentos L                | alfa = 93.452      | mu = 90.783          |                      |
| Gumbel                    | Máxima Entropía           | alfa = 20.394      | mu = 177.338         |                      |
| GVE (Valores Extremos)    | Momentos                  | NO_CONVERGE        | NO_CONVERGE          | NO_CONVERGE          |
| GVE (Valores Extremos)    | Máxima Verosimilitud      | NO_CONVERGE        | NO_CONVERGE          | NO_CONVERGE          |
| GVE (Valores Extremos)    | Momentos L                | alfa = 97.948      | beta = -0.085        | nu = 229.601         |
| Log Pearson tipo III      | Momentos Método Directo   | NO_CONVERGE        | NO_CONVERGE          | NO_CONVERGE          |
| Log Pearson tipo III      | Momentos Método Indirecto | alfa = 0.101       | beta = 35.54         | y0 = 1.611           |
| Log Pearson tipo III      | Máxima Verosimilitud      | alfa = -1.149      | beta = -0,0839 (tesis indica: -.0839) | y0 = 3.577 |

**Nota — encabezado erróneo en la fuente:** el encabezado de sección "VIII.3.5 - Análisis de Frecuencia Puntual" (Sheet 3, fila 86) dice literalmente "Estación Las Tapias – Río San Bartolomé" — es un error de copy-paste de título entre estaciones. Los datos numéricos que siguen (EEA, cuantiles, veredicto, conclusión) sí corresponden a Alpa Corral: se verificó por consistencia interna (el modelo ganador coincide con la fila de EEA más baja, y el veredicto/conclusión nombran expresamente "Alpa Corral" y "Río Barrancas").

**Nota — Gumbel Máxima Entropía:** alfa=20.394 rompe fuertemente el patrón de los otros 3 métodos de Gumbel para esta distribución (todos entre 86 y 93), y mu=200.143 en Gumbel MV también se aparta del resto (~90-93). Se transcribe literal, sin corregir.

---

### Etapa 2 — EEA esperados (Sheet 3)
| Distribución              | Método                    | EEA [m³/s] |
|---------------------------|---------------------------|------------|
| Gamma (3 parámetros)      | Momento de Probabilidad Pesada | 22.3359 |
| Gamma (2 parámetros)      | Momentos L                | 24.1772    |
| Gamma (2 parámetros)      | Máxima Verosimilitud      | 25.4097    |
| Generalizada Exponencial  | Máxima Verosimilitud      | 25.4672    |
| Gumbel                    | Momentos L                | 25.5046    |
| Gumbel                    | Momentos                  | 26.4862    |
| Gamma (2 parámetros)      | Momentos                  | 27.3029    |
| Gumbel                    | Máxima Entropía           | 27.3434    |
| Gamma (3 parámetros)      | Momentos                  | 27.6252    |
| Exponencial x0 y beta     | Máxima Verosimilitud      | 28.2616    |
| Log Normal (3 parámetros) | Momentos                  | 28.4009    |
| Gumbel                    | Máxima Verosimilitud      | 29.977     |
| Exponencial x0 y beta     | Momentos                  | 30.1895    |
| Exponencial beta          | Momentos y M. Verosimilitud | 31.0205  |
| Uniforme                  | Momentos                  | 34.207     |
| Normal                    | Momentos y M. Verosimilitud | 36.1651  |
| Normal                    | Momentos L                | 36.3555    |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | 38.394   |
| Log Normal (3 parámetros) | Máxima Verosimilitud      | 47.8054    |
| Log Pearson tipo III      | Momentos Método Indirecto | 48.808     |
| Uniforme                  | Máxima Verosimilitud      | 77.432     |
| GVE (Valores Extremos)    | Máxima Verosimilitud      | 78.3542    |
| Log Pearson tipo III      | Momentos Método Directo   | 98.0793    |
| GVE (Valores Extremos)    | Momentos L                | 153.5981   |
| Gamma (3 parámetros)      | Máxima Verosimilitud      | NO_CONVERGE |
| Generalizada Pareto       | Momentos                  | NO_CONVERGE |
| Generalizada Pareto       | Mínimos Cuadrados         | NO_CONVERGE |
| Generalizada Pareto       | Momentos de Probabilidad Pesada | NO_CONVERGE |
| GVE (Valores Extremos)    | Momentos                  | NO_CONVERGE |
| Log Pearson tipo III      | Máxima Verosimilitud      | NO_CONVERGE |

**Nota:** aparece por primera vez la distribución **Generalizada Pareto** en la tabla de EEA (3 métodos, todos NO_CONVERGE) — no estaba presente en Est02, Est07 ni Est08. No tiene fila correspondiente en la tabla de Parámetros (Sheet 3, filas 19-79), solo aparece en EEA. Se transcribe tal cual aparece en la fuente.

---

### Etapa 2 — Cuantiles esperados (Sheet 3)
| T [años] | Gamma 3p (MPP) [m³/s] | Gamma 2p (Momentos L) [m³/s] |
|----------|--------------------------|----------------------------------|
| 2        | 116.95                   | 111.17                           |
| 5        | 230.9                    | 223.73                           |
| 10       | 304.19                   | 300.59                           |
| 20       | 368.4                    | 369.9                             |
| 25       | 387.11                   | 390.37                           |
| 50       | 438.92                   | 447.65                           |
| 100      | 481.32                   | 495.11                           |

### Modelo seleccionado por Facundo
Modelo Gamma de 3 parámetros (Momentos de Probabilidad Pesada) Seleccionado. Para la serie histórica de la estación Alpa Corral del Río Barrancas, el análisis de error numérico y la evaluación gráfica coinciden de manera consistente. La distribución Gamma de 3 parámetros (calibrada por Momentos de Probabilidad Pesada) exhibe el menor error relativo con un EEA de 22,3359 m³/s, seguida de cerca por la Gamma de 2 parámetros (EEA = 24,1772 m³/s). En función de la excelente correspondencia de ajuste observada en la Figura VIII-10, se adopta la Gamma 3p (MPP) como distribución gobernante para la estimación de crecidas. Los caudales proyectados oscilan entre los 116,95 m³/s para crecidas regulares bianuales hasta un pico extremo de 481,32 m³/s para el período de retorno de 100 años.

**Recordatorio:** este modelo seleccionado y estos caudales de diseño corresponden a una serie que Etapa 1 rechazó por unanimidad (no homogénea, no independiente). Su validez es exclusivamente académica/demostrativa, según nota explícita de la fuente al inicio de Etapa 2.
---

## Resultados de Regresión METIS --> UNITARIAS

### Estado general: Etapa 1 rechazada por unanimidad en ambos (METIS y tesis coinciden en la decisión) — FAIL=0 en el sentido de que el rechazo se reproduce, con varias anomalías numéricas señaladas en Etapa 2 (ver notas). **Recordatorio: esta estación es de uso exclusivamente académico — Etapa 1 la descarta profesionalmente, tal como documenta la propia fuente.**

### PASO 1 — Estadística descriptiva: PASS con 1 anomalía (media/varianza)
| Variable                      | METIS        | Tesis        | diff%   | Nivel |
|-------------------------------|--------------|--------------|---------|-------|
| n                             | 40           | 40           | 0.000%  | PASS  |
| Media                         | 144.375      | 144.725      | -0.242%  | INFO  |
| Varianza                      | 13404.446     | 13408.358    | -0.029%  | INFO  |
| Desvío                        | 115.778      | 115.794      | -0.014%  | INFO  |
| M0                            | 144.375      | 144.725      | -0.242%  | INFO  |
| M1                            | 104.537      | 104.751      | -0.204%  | INFO  |
| M2                            | 82.937       | 83.065       | -0.155%  | INFO  |
| M3                            | 68.978       | 69.054       | -0.110%  | INFO  |
| Sumatoria ln(xi)              | 183.292     | 183.385      | -0.051%  | PASS  |
| Máximo                        | 410.0        | 410.0        | 0.000%  | PASS  |
| Mínimo                        | 15.0         | 15.0         | 0.000%  | PASS  |
| Asimetría sesgada             | 0.7427       | 0.706        | +5.20%   | INFO  |
| Asimetría no sesgada (g)      | 0.8018       | 0.762        | +5.23%   | INFO  |
| Curtosis sesgada              | 2.3976       | 2.269        | +5.67%   | INFO  |
| Curtosis no sesgada           | 2.7984       | 2.649        | +5.64%   | INFO  |
| CV                            | 0.8019       | 0.8          | +0.24%   | INFO  |

**Nota — anomalía nueva:** a diferencia de las 8 estaciones anteriores (donde media/varianza/M0-M3 coincidían con la tesis a &lt;0.01%), acá la media difiere -0.24% (144.375 vs 144.725) y se propaga a M0 y a la varianza/desvío/M1-M3. La serie transcripta en este archivo coincide, línea por línea, con la de la tabla "Serie (Sheet 1)" de arriba (verificado por comparación directa) — no es un error de transcripción de esta sesión. El máximo, mínimo y suma_log sí coinciden exacto. No se investigó el origen puntual (podría ser una celda distinta en el Excel real de Facundo para esta estación, dado que ya es la novena estación auditada y las primeras 8 nunca mostraron esta clase de diff en media). Dado que esta estación es de uso académico exclusivamente, se señala pero no se escala como bloqueante.

### PASO 2 — Homogeneidad: RECHAZADA (coincide con tesis — unanimidad en ambos)
| Prueba     | Estadístico METIS | Estadístico Tesis | diff%   | Veredicto | Nivel |
|------------|--------------------|--------------------|---------|-----------|-------|
| Helmert S-C| 21                | 17                 | +23.53% | Rechazada | INFO  |
| t-Student  | 7.3529             | 7.28               | +1.00%  | Rechazada | PASS  |
| Cramer (max t_w, n_w1=24/n_w2=12) | 3.8849             | 3.83732 (t_w2 tesis) | +1.24% | Rechazada | PASS |
| Veredicto  | homogeneidad_critica | Serie NO Homogénea | —      | —         | PASS  |

**Veredicto coincide en ambos: la serie NO es homogénea.** Helmert difiere en magnitud (21 vs 17, ambos muy por fuera del umbral ±6.24/±6.25 — el rechazo no cambia). t-Student y Cramer coinciden razonablemente bien (&lt;5%). La divergencia de Helmert es consistente con la anomalía de media/varianza de PASO 1 (Helmert depende de la posición de cada valor respecto a la media, y una media distinta puede cambiar el conteo S/C en los puntos cercanos al promedio) — no investigado más allá de esta observación.

### PASO 3 — Independencia: RECHAZADA (coincide con tesis — unanimidad en ambos)
| Prueba          | Estadístico METIS | Estadístico Tesis | diff%  | Veredicto | Nivel |
|-----------------|--------------------|--------------------|--------|-----------|-------|
| Anderson (k_max=14) | 0.5597 (máx |r_k|, 4+ puntos fuera) | 4 puntos fuera | — | Rechazada | PASS |
| Wald-Wolfowitz Z| -3.4076            | -2.80              | -21.70% | Rechazada | PASS |
| Veredicto       | dependiente         | NO Independiente   | —      | —         | PASS  |

Ambas pruebas rechazan en los dos casos — coincide con la tesis, incluido el mecanismo (Anderson por sí solo ya es suficiente para el veredicto final, sin necesitar la jerarquía de desempate). Wald-Wolfowitz Z coincide muy bien (-3.41 vs -2.80, ambos categóricamente fuera de ±2.58).

**Tendencia y atípicos (sin ficha de tesis — MK/KS/Chow no están en la tesis de Facundo, mismo caso que las 8 estaciones previas):**
Mann-Kendall: Z=-4.8260, crítico=1.9600, veredicto=rechazada (rechaza — tendencia fuerte detectada, consistente con el quiebre de nivel visible en la serie cruda a partir de ~1958-59).
KS: Z=2.6879, crítico=1.358, veredicto=rechazada (rechaza también).
Chow: estadístico=1.9396, K_N=2.8675, veredicto=aprobada (aprobada — no detecta un dato atípico puntual, coherente con que el problema de esta serie es un quiebre de nivel sostenido, no un outlier aislado).

### PASO 4 — Veredicto Etapa 1: RECHAZADA (coincide con tesis)
Serie NO habilitada profesionalmente para Etapa 2 — homogeneidad y independencia
rechazadas en ambos (METIS y tesis). Se continúa con Etapa 2 exclusivamente con
fines académicos, replicando la nota explícita de la fuente ("Se proveen los
datos de los parámetros con fines académicos").
### PASO 5 — Parámetros Etapa 2: ver notas (estación académica — instabilidad alta)
| Distribución              | Método            | diff% (por parámetro)                          | Nivel  | Nota |
|----------------------------|-------------------|--------------------------------------------------|--------|-------|
| Uniforme                  | Momentos          | alpha=-0.57%, beta=-0.11%                         | PASS   | —     |
| Uniforme                  | MV                | alpha=0.00%, beta=0.00%                           | PASS   | —     |
| Exponencial beta          | Momentos/MV       | beta=-1.05%                                       | INFO   | leve  |
| Exponencial x0beta        | Momentos          | x0=-1.15%, beta=-0.01%                            | PASS   | —     |
| Exponencial x0beta        | MV                | x0=-2.97%, beta=+11.97%                           | INFO   | no atribuible a un patrón conocido |
| Gen. Exponencial          | Momentos          | METIS status=ok (alpha=1.6724, lambda=0.00943); tesis=NO_CONVERGE | INFO | **anomalía**: METIS converge donde la tesis no — mismo tipo de caso ya visto en est_08 (gve/momentos), acá con una distribución distinta |
| Gen. Exponencial          | MV                | alpha=-83.82%, lambda=-28.74%                     | INFO   | diferencia grande, no atribuible a un patrón conocido |
| Gen. Exponencial          | ML                | alpha=-62.13%, lambda=-66.98%                     | INFO   | diferencia grande, no atribuible a un patrón conocido |
| Normal                    | Momentos/MV/ML    | mu≈-0.25% (heredado de PASO1), sigma≤0.12%        | INFO   | consecuencia directa de la anomalía de media de PASO1 |
| Log-Normal 2p             | Momentos/MV       | mu_y=+47.34%, sigma_y=-42.82%                     | INFO   | **divergencia fuerte** — la mayor de las 3 estaciones "limpias" no vista, ni siquiera en Causa C |
| Log-Normal 3p             | Momentos          | x0=+6.82%, mu_y=-0.86%, sigma_y=+4.91%            | INFO-A | compatible con g-propagación DECISIÓN013, magnitud algo mayor que en otras estaciones |
| Log-Normal 3p             | MV                | x0=-81.52%, mu_y=+53.13%, sigma_y=-34.25%         | INFO   | **divergencia fuerte** — a diferencia de las 8 estaciones previas donde LN3p MV siempre coincidía &lt;1%, acá diverge fuertemente en los 3 parámetros |
| Gamma 2p                  | Momentos/MV/ML    | todas ≤0.45%                                      | PASS   | —     |
| Gamma 3p                  | Momentos          | x0=+9.27%, alpha=+5.20%, beta=-9.67%              | INFO-A | g-propagación DECISIÓN013 |
| Gamma 3p                  | MV                | METIS status=no_converge, coincide con tesis=NO_CONVERGE | PASS | — |
| Gumbel                    | Momentos          | mu=-0.37%, alpha≈0%                               | PASS   | —     |
| Gumbel                    | MV                | mu=-54.00%, alpha=-2.37%                          | INFO   | mu diverge fuerte — tesis reporta mu=200.14 (fuera del rango 86-93 de los otros 3 métodos, ya señalado como atípico en la propia ficha) |
| Gumbel                    | ML                | mu=-0.32%, alpha=-0.12%                           | PASS   | —     |
| Gumbel                    | ME                | mu=-47.29%, alpha=+332.36%                        | INFO   | **anomalía severa** — coincide con la nota ya presente en la ficha ("Gumbel ME rompe el patrón de los otros 3 métodos"), METIS confirma que ese valor de tesis es efectivamente atípico/no reproducible |
| GVE                       | Momentos          | METIS status=ok (nu=93.04, alpha=94.01, beta=+0.0325); tesis=NO_CONVERGE | INFO | **anomalía**: METIS converge donde tesis no — nota: signo de beta positivo (tipo III), régimen distinto al de otras estaciones donde GVE Momentos sí converge (beta negativo, tipo II) |
| GVE                       | MV                | METIS status=ok (nu=70.89, alpha=62.62, beta=-0.542); tesis=NO_CONVERGE | INFO | **anomalía**: METIS converge donde tesis no — segunda de tres anomalías de este tipo en esta estación |
| GVE                       | ML                | alpha=-12.86%, beta=-5.04%, nu=-62.16%            | INFO-B | mismo patrón de convergencia a óptimo distinto ya visto en otras estaciones, magnitud mayor |
| Log-Pearson III           | Directo           | NO_APLICABLE (B=2.4214 ∉ (3,6]); tesis=NO_CONVERGE | INFO | METIS aplica restricción IV-249 (patrón universal en las 9 estaciones); tesis reporta un status distinto (NO_CONVERGE) para el mismo caso — categorías distintas, mismo resultado práctico (sin parámetros) |
| Log-Pearson III           | Indirecto         | alpha=+36.73%, beta=+37.77%, y0=-235.27%          | INFO   | **divergencia fuerte**, y0 incluso cambia de orden de magnitud relativo — no atribuible limpiamente a g-propagación sola |
| Log-Pearson III           | MV                | METIS status=no_converge; tesis reporta alfa=-1.149, beta≈-0.084, y0=3.577 (parámetros negativos, ya extraños en la propia fuente) | INFO | tesis reporta valores con signos físicamente cuestionables (alpha y beta negativos no tienen sentido para esta parametrización); METIS no converge para el mismo caso |

**Resumen:** de las 30 combinaciones distribución/método con referencia en la tesis, 8 coinciden &lt;1% (PASS), 2 siguen el patrón conocido de g-propagación (INFO-A), 1 el patrón de convergencia a óptimo distinto (INFO-B), y el resto (19) muestra divergencias que no encajan limpiamente en los patrones A/B/C ya establecidos para las estaciones "sanas" — consistente con que esta es la serie más inestable de las 9 auditadas (quiebre de nivel severo, rechazo unánime de Etapa 1). No se investigó el origen de ninguna divergencia individual, más allá de las notas puntuales de arriba.
### PASO 6 — EEA: ver notas
| Distribución | Método | EEA METIS | EEA Tesis | diff% | Nivel |
|---|---|---|---|---|---|
| Gamma 2p           | ML         |    25.2549 |   24.1772 |   +4.46% | PASS |
| Gamma 2p           | MV         |    25.3740 |   25.4097 |   -0.14% | PASS |
| Gen. Exponencial   | MV         |    25.4635 |   25.4672 |   -0.01% | PASS |
| Gumbel             | ML         |    25.6458 |   25.5046 |   +0.55% | PASS |
| Gumbel             | Momentos   |    26.5957 |   26.4862 |   +0.41% | PASS |
| Gamma 2p           | Momentos   |    26.2459 |   27.3029 |   -3.87% | PASS |
| Gumbel             | ME         |    27.5245 |   27.3434 |   +0.66% | PASS |
| Gamma 3p           | Momentos   |    26.5838 |   27.6252 |   -3.77% | PASS |
| Exponencial x0beta | MV         |    28.1006 |   28.2616 |   -0.57% | PASS |
| Log-Normal 3p      | Momentos   |    27.4758 |   28.4009 |   -3.26% | PASS |
| Gumbel             | MV         |    30.2276 |    29.977 |   +0.84% | PASS |
| Exponencial x0beta | Momentos   |    30.0903 |   30.1895 |   -0.33% | PASS |
| Exponencial beta   | Momentos   |    30.7735 |   31.0205 |   -0.80% | PASS |
| Uniforme           | Momentos   |    34.5958 |    34.207 |   +1.14% | PASS |
| Normal             | Momentos   |    36.7760 |   36.1651 |   +1.69% | PASS |
| Normal             | ML         |    36.8504 |   36.3555 |   +1.36% | PASS |
| Log-Normal 2p      | Momentos   |    51.3768 |    38.394 |  +33.81% | INFO |
| Log-Normal 3p      | MV         |    65.5194 |   47.8054 |  +37.05% | INFO |
| Log-Pearson III    | Indirecto  |    67.9087 |    48.808 |  +39.13% | INFO |
| Uniforme           | MV         |    77.9243 |    77.432 |   +0.64% | PASS |
| GVE                | MV         |    78.2992 |   78.3542 |   -0.07% | PASS |
| Log-Pearson III    | Directo    | N/A (no_aplicable) |   98.0793 | —      | INFO |
| GVE                | ML         |    27.0984 |  153.5981 |  -82.36% | INFO |
| GVE                | Momentos   | 26.8364 (METIS status=ok) | NO_CONVERGE | — | INFO |
| GVE                | MV         | 78.2992 (METIS status=ok) | NO_CONVERGE | — | INFO |
| Gen. Exponencial   | Momentos   | 26.7245 (METIS status=ok) | NO_CONVERGE | — | INFO |

**Nota general:** a diferencia de PASO5 (donde muchos parámetros divergían fuerte),
en EEA la mayoría de las filas con parámetros PASS o cercanos también dan EEA
razonablemente cercano (&lt;5%, tolerancia ampliada respecto al ±1% estricto de
estaciones previas, dado el contexto de esta serie). Las excepciones fuertes
(LN2p +33.8%, LN3p MV +37.1%, LP3 Indirecto +39.1%, GVE ML -82.4%) coinciden
exactamente con las mismas filas que ya mostraron divergencia fuerte de
parámetros en PASO5 — consistente, no es un patrón nuevo de EEA aislado del de
parámetros.

**Conteo aproximado: PASS/cercano=15, INFO=8 (incl. 3 filas "METIS converge, tesis NO_CONVERGE"), FAIL=0 (no se aplicó el criterio estricto ±1% dado el carácter académico de esta estación).**

### PASO 7 — Cuantiles: ver nota (modelo seleccionado no reproducible en METIS)
Modelo seleccionado por Facundo: **Gamma 3p (MPP)** — MPP no está implementado
para Gamma 3p en METIS (Cap. IV no desarrolla las ecuaciones, mismo caso que
en las 8 estaciones previas) → **EXCLUIDO, sin columna METIS posible para el
modelo ganador de esta estación**. Se usa Gamma 2p (Momentos L) como testigo
(segunda columna de la tesis) para al menos verificar algo en PASO 7.

| T [años] | Gamma2p ML METIS | Gamma2p ML Tesis | diff%   | Nivel |
|----------|-------------------|-------------------|---------|-------|
|   2      |   110.81     |   111.17    |  -0.33% | PASS  |
|   5      |   225.40     |   223.73    |  +0.74% | PASS  |
|  10      |   308.49     |   300.59    |  +2.63% | PASS  |
|  20      |   390.77     |   369.90    |  +5.64% | INFO  |
|  25      |   417.22     |   390.37    |  +6.88% | INFO  |
|  50      |   499.50     |   447.65    | +11.58% | INFO  |
| 100      |   582.16     |   495.11    | +17.58% | INFO  |

**Gamma2p ML (testigo): 3/7 dentro de ±5%.**
**Gamma3p MPP (modelo seleccionado por Facundo): sin comparación posible — no implementado en METIS.**

**Recordatorio final:** ninguno de estos números — parámetros, EEA o
cuantiles — tiene validez de diseño hidrológico para esta estación. Etapa 1
la rechazó por unanimidad en ambos (METIS y tesis). Todo lo de Etapa 2 es,
por diseño de la propia fuente, un ejercicio académico de continuidad
metodológica.
