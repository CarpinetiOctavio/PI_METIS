## Estación 9 — La Suela – Río La Suela

**Nota de encuadre:** serie con n=7, por debajo del umbral mínimo de METIS (n≥10, único caso de bloqueo duro documentado en la arquitectura del sistema — todo lo demás es no-bloqueante). Esta ficha se transcribe con fines de control académico y de verificación de contrato del software (confirmar que METIS efectivamente bloquea en n<10), no como resultado de diseño hidrológico válido. Mismo patrón de excepción que Est 01 (Alpa Corral), aunque la causa de invalidez es distinta: Alpa Corral fue rechazada por criterio estadístico con muestra de tamaño válido (n=40); La Suela no alcanza el piso mínimo de muestra para que las pruebas tengan sentido, independientemente de su resultado.

### Serie (Sheet 1)
serie = [
    24.32,                # 1972-73
    "(S/D - Faltante)",   # 1973-74
    "(S/D - Faltante)",   # 1974-75
    "(S/D - Faltante)",   # 1975-76
    "(S/D - Faltante)",   # 1976-77
    10.99,                # 1977-78
    33.9,                 # 1978-79
    31.91,                # 1979-80
    39.55,                # 1980-81
    22.0,                 # 1981-82
    30.52,                # 1982-83
]

**Nota:** 4 datos faltantes (1973-74 a 1976-77 inclusive). n efectivo = 7 sobre 11 años de registro (1972-73 a 1982-83). Fuente: CRSA (ex CIRSA) / INA, no EVARSA (a diferencia del resto de estaciones transcriptas).

### Estadística descriptiva esperada (Sheet 1)
| Variable                        | Valor esperado |
|---------------------------------|----------------|
| n                                | 7              |
| Media [m³/s]                    | 27.598         |
| Varianza [m³/s]²                | 87.926         |
| Desvío [m³/s]                   | 9.377          |
| Asimetría Sesgada               | -0.473         |
| Asimetría No Sesgada (g)        | -0.773         |
| Curtosis Sesgada                | 1.841          |
| Curtosis No Sesgada (k)         | 5.261          |
| Coeficiente de Variación (CV)   | 0.34           |
| Sumatoria ln(xi)                | 22.761         |
| beta_0 = M0                     | 27.598         |
| beta_1 = M1                     | 16.586         |
| beta_2 = M2                     | 11.805         |
| beta_3 = M3                     | 9.201          |
| Máximo [m³/s]                   | 39.5           |
| Mínimo [m³/s]                   | 11.0           |

**Nota:** Máximo (39.5) y Mínimo (11.0) en esta tabla no coinciden exactamente con el máximo/mínimo de la serie tal como está cargada arriba (39.55 y 10.99). Diferencia menor, posible redondeo de la fuente. Se transcribe literal tal como figura en la celda de estadística descriptiva.

---

### Etapa 1 — Homogeneidad (Sheet 2)

#### Helmert
| Parámetro              | Valor esperado |
|------------------------|----------------|
| N° de Series (S)       | 3              |
| N° de Cambios (C)      | 3              |
| Estadístico (S-C)      | 0              |
| n                      | 7              |
| Umbral inferior        | -2.45          |
| Umbral superior        | 2.45           |
| Conclusión individual  | El estadístico (S - C) está comprendido entre -(nj-1)^0,5 y +(nj-1)^0,5. Por lo tanto la serie es Homogénea. |

**Nota — corrección de fuente:** el Excel traía la frase con error de redacción ("no está comprendido..."). Se corrige con el texto de la tesis (fuente de mayor jerarquía sobre el Excel), coherente con la matemática (S-C=0 está comprendido entre -2.45 y +2.45).

#### t de Student
| Parámetro              | Valor esperado |
|------------------------|----------------|
| Estadístico t          | -0.62          |
| Grados de libertad     | 5              |
| Valor crítico (tabla)  | 2.015          |
| Conclusión individual  | El valor absoluto del estadístico t es menor que el valor de tabla de t para 5 grados de libertad (G.L.) y para un nivel de significancia: α = 5%. Por lo tanto la serie es Homogénea. |

#### Cramer
| Parámetro              | Valor esperado |
|------------------------|----------------|
| tau subgrupo 1         | 0.36219        |
| tau subgrupo 2         | -0.14274       |
| t calculado sg. 1      | 1.02953        |
| t calculado sg. 2      | 0.20275        |
| Valor crítico (tabla)  | 2.015          |
| Conclusión individual  | El valor absoluto de ambos τw es menor que el valor de tabla de t para 5 G.L. y para α = 5%. La serie es Homogénea. |

**Veredicto homogeneidad:** Serie Homogénea

**Nota — conclusión general eliminada:** el párrafo de "Conclusión" que acompañaba este veredicto en el Excel citaba "34 G.L.", un dato que no corresponde a esta estación (arrastre de copy-paste de otra ficha). Por indicación de Octavio, se elimina el párrafo completo en lugar de corregirlo, ya que el error de copy-paste invalida la redacción entera, no solo la cifra.

---

### Etapa 1 — Independencia (Sheet 2)

#### Anderson
| Parámetro                              | Valor esperado |
|----------------------------------------|----------------|
| n                                      | 7              |
| k = n/3                                | 2.3            |
| k adoptado                             | 3              |
| Media                                  | 27.6           |
| N° máximo puntos fuera de bandas       | 0.3            |
| N° puntos fuera de bandas              | 0              |
| Conclusión individual                  | Aceptada (0 puntos fuera cumple idealmente con el límite admisible de 0,3). Se acepta la hipótesis de que las variables de la serie son Independientes. |

#### Wald-Wolfowitz
| Parámetro                    | Valor esperado |
|------------------------------|----------------|
| n                            | 7              |
| n1                           | 4              |
| n2                           | 3              |
| R (rachas observadas)        | 4              |
| Media teórica de R           | 4.429          |
| Varianza teórica de R        | 1.388          |
| Estadístico Z                | -0.364         |
| Valor crítico α=0.05         | ± 1.96         |
| Valor crítico α=0.01         | ± 2.576        |
| Conclusión individual        | Aceptada (El estadístico Z = -0,364 se ubica muy cerca de cero, dentro de los rangos críticos de tabla). La serie se concluye como independiente. |

**Veredicto independencia:** Serie Independiente (Aprobada con reserva por tamaño muestral)
**Conclusión (tesis):** Se acepta la hipótesis de que las variables de la serie son Independientes.
**Detalle:** Aceptación unánime de la hipótesis de independencia. Ambas pruebas validan la estructura aleatoria de la serie con un comportamiento óptimo; Anderson registra cero puntos fuera de las bandas de tolerancia y Wald-Wolfowitz arroja un estadístico Z = -0,364 plenamente contenido en los límites críticos. Tal como se asentó en la fase de homogeneidad, la serie se aprueba bajo la salvedad académica de contar con una muestra reducida (n = 7), quedando habilitada para la Etapa 2 de la tesis.

**Veredicto general Etapa 1:** Habilitada para Etapa 2, con salvedad académica explícita por tamaño muestral (n=7). Es la primera estación donde el propio texto de la fuente reconoce la limitación de n como condición de la aprobación.

---

### Etapa 2 — Parámetros (Sheet 3)
| Distribución              | Método                    | Parámetro 1        | Parámetro 2          | Parámetro 3          |
|---------------------------|---------------------------|--------------------|----------------------|----------------------|
| Uniforme                  | Momentos                  | alfa = 11.36       | beta = 43.83         |                      |
| Uniforme                  | Máxima Verosimilitud      | alfa = 10.99       | beta = 39.55         |                      |
| Exponencial beta          | Momentos y M. Verosimilitud | beta = 0.036     |                      |                      |
| Exponencial x0 y beta     | Momentos                  | x0 = 18.22         | beta = 9.38          |                      |
| Exponencial x0 y beta     | Máxima Verosimilitud      | x0 = 8.22          | beta = 19.38         |                      |
| Generalizada Exponencial  | Momentos                  | alfa = 5.23        | lambda = 0.0511      |                      |
| Generalizada Exponencial  | Máxima Verosimilitud      | alfa = 9.93        | lambda = 0.1037      |                      |
| Generalizada Exponencial  | Momentos L                | alfa = 0.71        | lambda = -0.0198     |                      |
| Normal                    | Momentos L                | mu = 27.6          | sigma = 9.877        |                      |
| Normal                    | Momentos y M. Verosimilitud | mu = 27.6        | sigma = 9.3769       |                      |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | mu_y = 3.25      | sigma_y = 0.426      |                      |
| Log Normal (3 parámetros) | Momentos                  | NO_APLICABLE       | NO_APLICABLE         | NO_APLICABLE         |
| Log Normal (3 parámetros) | Máxima Verosimilitud      | x0 = -25.0         | mu_y = 3.9476        | sigma_y = 0.1785     |
| Gamma (2 parámetros)      | Momentos                  | alfa = 3.19        | beta = 8.662         |                      |
| Gamma (2 parámetros)      | Máxima Verosimilitud      | alfa = 3.57        | beta = 7.726         |                      |
| Gamma (2 parámetros)      | Momentos L                | alfa = 3.66        | beta = 7.548         |                      |
| Gamma (3 parámetros)      | Momentos                  | x0 = 3.446         | alfa = 3.626         | beta = 6.689         |
| Gamma (3 parámetros)      | Máxima Verosimilitud      | x0 = 10.758        | alfa = 15.351        | beta = 1.097         |
| Gamma (3 parámetros)      | Momento Prob. Pesada      | x0 = 37.579        | alfa = -5.008        | beta = 1.993         | ← PENDIENTE: fórmula MPP ausente en Cap. IV |
| Gumbel                    | Momentos                  | alfa = 7.314       | mu = 23.378          |                      |
| Gumbel                    | Máxima Verosimilitud      | alfa = 9.16        | mu = 23.028          |                      |
| Gumbel                    | Momentos L                | alfa = 8.042       | mu = 22.956          |                      |
| Gumbel                    | Máxima Entropía           | alfa = 8.515       | mu = 22.683          |                      |
| GVE (Valores Extremos)    | Momentos                  | NO_CONVERGE        | NO_CONVERGE          | NO_CONVERGE          |
| GVE (Valores Extremos)    | Máxima Verosimilitud      | NO_CONVERGE        | NO_CONVERGE          | NO_CONVERGE          |
| GVE (Valores Extremos)    | Momentos L                | alfa = 10.389      | beta = 0.666         | nu = 26.396          |
| Log Pearson tipo III      | Momentos Método Directo   | alfa = 0.333       | beta = 0.075         | y0 = 3.287           |
| Log Pearson tipo III      | Momentos Método Indirecto | alfa = 0.333       | beta = 1.633         | y0 = 2.707           |
| Log Pearson tipo III      | Máxima Verosimilitud      | alfa = 0.775       | beta = 1.123         | y0 = 2.382           |

**Nota — VERIFICACIÓN CRUZADA:** se verificó matemáticamente que estos parámetros corresponden genuinamente a La Suela (no hay contaminación con otra estación, a diferencia de lo detectado entre Est07/Est08). Normal por Momentos y MV reproduce mu=27.6≈media real (27.598) y sigma=9.3769≈desvío real (9.377). Uniforme por Momentos reproduce media≈27.595 y varianza≈87.858≈varianza real (87.926).

**Nota — Log Normal (3 parámetros) Momentos = NO_APLICABLE:** primera aparición de esta marca en la tabla de Parámetros de Etapa 2 (previamente solo vista para LN2p, según registro de estaciones anteriores). Se transcribe literal sin inferir el criterio, pendiente de confirmación con Facundo.

**Nota — Gamma 3p MPP, parámetro alfa negativo:** alfa=-5.008 es matemáticamente atípico para un parámetro de forma de Gamma (se transcribe literal, sin corregir — coherente con el estado ya documentado de "estimador MPP ill-conditioned, produce valores físicamente implausibles").

---

### Etapa 2 — EEA esperados (Sheet 3)
| Distribución              | Método                    | EEA [m³/s] |
|---------------------------|---------------------------|------------|
| Uniforme                  | Momentos                  | 2.7768     |
| Normal                    | Momentos L                | 2.9141     |
| GVE (Valores Extremos)    | Momentos L                | 3.0643     |
| Normal                    | Momentos y M. Verosimilitud | 3.1667   |
| Gumbel                    | Máxima Verosimilitud      | 3.4206     |
| Gamma (2 parámetros)      | Momentos L                | 3.5        |
| Gamma (2 parámetros)      | Máxima Verosimilitud      | 3.5299     |
| Generalizada Exponencial  | Máxima Verosimilitud      | 3.5647     |
| Gumbel                    | Máxima Entropía           | 3.6581     |
| Log Normal (2 parámetros) | Momentos y M. Verosimilitud | 3.6601   |
| Gamma (2 parámetros)      | Momentos                  | 3.7052     |
| Gumbel                    | Momentos L                | 3.7907     |
| Gumbel                    | Momentos                  | 4.1031     |
| Uniforme                  | Máxima Verosimilitud      | 4.1627     |
| Gamma (3 parámetros)      | Momentos                  | 4.2505     |
| Exponencial x0 y beta     | Momentos                  | 5.2981     |
| Log Pearson tipo III      | Momentos Método Indirecto | 6.1286     |
| Gamma (3 parámetros)      | Máxima Verosimilitud      | 6.3409     |
| Exponencial x0 y beta     | Máxima Verosimilitud      | 7.7298     |
| Log Pearson tipo III      | Momentos Método Directo   | 9.9861     |
| Exponencial beta          | Momentos y M. Verosimilitud | 12.0441  |
| Gamma (3 parámetros)      | Momento de Probabilidad Pesada | 17.4168 |
| Log Normal (3 parámetros) | Momentos                  | NO_CONVERGE |
| Log Normal (3 parámetros) | Máxima Verosimilitud      | NO_CONVERGE |
| Generalizada Pareto       | Momentos                  | NO_CONVERGE |
| Generalizada Pareto       | Mínimos Cuadrados         | NO_CONVERGE |
| Generalizada Pareto       | Momentos de Probabilidad Pesada | NO_CONVERGE |
| GVE (Valores Extremos)    | Momentos                  | NO_CONVERGE |
| GVE (Valores Extremos)    | Máxima Verosimilitud      | NO_CONVERGE |
| Log Pearson tipo III      | Máxima Verosimilitud      | NO_CONVERGE |

**Nota:** en EEA, Log Normal (3p) Momentos aparece como NO_CONVERGE (no NO_APLICABLE, como en la tabla de Parámetros). Es decir, la fuente usa las dos marcas para el mismo caso en las dos tablas — inconsistencia terminológica de la fuente, se transcribe literal en cada tabla tal como figura.

---

### Etapa 2 — Cuantiles esperados (Sheet 3)
| T [años] | Uniforme (Momentos) [m³/s] | Normal (Momentos L) [m³/s] |
|----------|-------------------------------|--------------------------------|
| 2        | 27.6                           | 27.6                            |
| 5        | 37.34                          | 35.78                           |
| 10       | 40.59                          | 39.86                           |
| 20       | 42.21                          | 42.97                           |
| 25       | 42.54                          | 43.81                           |
| 50       | 43.19                          | 46.02                           |
| 100      | 43.51                          | 47.72                           |

### Modelo seleccionado por Facundo
Modelo Uniforme (Momentos) Seleccionado. Para la serie de datos de la Estación La Suela (Río La Suela), el análisis de error numérico arrojó un ajuste óptimo con la distribución Uniforme por momentos (EEA = 2,7768 m³/s), seguida de cerca por la Normal por momentos L (EEA = 2,9141 m³/s). En concordancia con la inspección gráfica (Figura VIII-9) que demuestra una excelente representación de ambas curvas sobre los registros históricos, se adopta la distribución Uniforme como ley representativa de la cuenca. Se deja constancia de que, debido a la corta longitud de registro de esta estación, el análisis de extremos se realiza al solo efecto del desarrollo de la tesis. Los caudales de diseño adoptados para los cálculos se proyectan desde los 27,60 m³/s (T=2 años) hasta una cota de 43,51 m³/s para la recurrencia centenaria.

**Recordatorio:** esta ficha completa (Etapa 1 y Etapa 2) corresponde a una serie con n=7, por debajo del piso mínimo de METIS (n≥10, único caso de bloqueo duro del pipeline). Su función es exclusivamente de control académico/verificación de contrato de software — confirmar que METIS efectivamente bloquea la ejecución para esta estación, no validar los resultados de diseño hidrológico que arroja Facundo bajo su criterio de tesis.
---

## Resultados de Regresión METIS --> UNITARIAS

### Estado general: n=7, por debajo del piso mínimo de METIS (n≥10). Verificación de contrato + reproducción académica de las pruebas aisladas — FAIL=0 en el sentido de que el bloqueo del pipeline real y los cálculos aislados se comportan como se esperaba.

**Nota de encuadre (heredada de la ficha original):** esta corrida NO valida
resultados de diseño hidrológico — su único propósito es de control académico
y de verificación de software: (1) confirmar que `ejecutar_etapa1()` bloquea
efectivamente para n&lt;10 (único caso de bloqueo duro documentado), y (2)
reproducir, llamando a las funciones puras de `core/` de forma aislada (sin
pasar por el contrato), las cifras que Facundo calculó "igual" con fines
académicos — exactamente el mismo patrón dual ya usado en est_01 (Alpa
Corral), donde el pipeline real también se comporta distinto de las funciones
aisladas, aunque por una causa distinta (ahí era rechazo estadístico con
muestra válida; acá es tamaño de muestra insuficiente para que el contrato
deje avanzar).

### PASO 1 — Estadística descriptiva: PASS
| Variable                      | METIS        | Tesis        | diff%   | Nivel |
|-------------------------------|--------------|--------------|---------|-------|
| n                             | 7            | 7            | 0.000%  | PASS  |
| Media                         | 27.599      | 27.598       | +0.0021%  | PASS  |
| Varianza                      | 87.934       | 87.926       | +0.0094%  | PASS  |
| Desvío                        | 9.377       | 9.377        | +0.0035%  | PASS  |
| M0                            | 27.599      | 27.598       | +0.0021%  | PASS  |
| M1                            | 16.587      | 16.586       | +0.0040%  | PASS  |
| M2                            | 11.806      | 11.805       | +0.0052%  | PASS  |
| M3                            | 9.201       | 9.201        | +0.0016%  | PASS  |
| Sumatoria ln(xi)              | 22.762      | 22.761       | +0.0027%  | PASS  |
| Máximo                        | 39.55        | 39.5*        | —       | INFO  |
| Mínimo                        | 10.99        | 11.0*        | —       | INFO  |
| Asimetría sesgada             | -0.5959      | -0.473       | -25.99%   | INFO  |
| Asimetría no sesgada (g)      | -0.9734      | -0.773       | -25.92%   | INFO  |
| Curtosis sesgada              | 2.5042       | 1.841        | +36.03%   | INFO  |
| Curtosis no sesgada           | 7.1580       | 5.261        | +36.06%   | INFO  |
| CV                            | 0.3398       | 0.34         | -0.07%   | INFO  |

*Máximo/Mínimo de la tesis (39.5/11.0) ya venían señalados como discrepantes en
la propia ficha respecto a la serie cargada (39.55/10.99) — nota de redondeo de
la fuente, no de METIS (METIS usa 39.55/10.99 literal, coincide con la serie).
Nota g/k: mismo patrón DECISIÓN013 de las 9 estaciones previas, con magnitud
mayor de lo usual — esperable dado que n=7 amplifica cualquier sensibilidad a
convención de ddof.

### PASO 2 — Homogeneidad: PASS con anomalía de magnitud en t-Student/Cramer (mismo patrón que est_07)
| Prueba     | Estadístico METIS | Estadístico Tesis | diff%   | Veredicto | Nivel |
|------------|--------------------|--------------------|---------|-----------|-------|
| Helmert S-C| 0                  | 0                  | 0.000%  | Aprobada  | PASS  |
| t-Student (n1=3/n2=4, GL=5) | -0.9440            | -0.62              | — (magnitud ~1.5x) | Aprobada  | INFO  |
| Cramer (max t_w, n_w1=5/n_w2=2) | 2.0216             | 1.02953 (t_w1 tesis, mayor de los dos) | — (~2x) | Aprobada  | INFO |
| Veredicto  | homogeneidad_ok    | Serie Homogénea    | —       | —         | PASS  |

Con n=7 cualquier sensibilidad de partición se amplifica — mismo tipo de
anomalía ya visto en est_07 (t-Student/Cramer no coinciden en magnitud con la
tesis pese a que el valor crítico y el veredicto sí). No investigado.

### PASO 3 — Independencia: PASS
| Prueba          | Estadístico METIS | Estadístico Tesis | diff%  | Veredicto | Nivel |
|-----------------|--------------------|--------------------|--------|-----------|-------|
| Anderson (k_max=3) | -0.4460 (máx |r_k|, 0 puntos fuera) | 0 puntos fuera | — | Aprobada | PASS |
| Wald-Wolfowitz Z| -0.3638           | -0.364             | +0.05% | Aprobada | PASS |
| Veredicto       | independiente       | Independiente (con salvedad académica) | — | — | PASS |

Wald-Wolfowitz coincide casi exacto. Veredicto coincide en ambos.

**Tendencia y atípicos (sin ficha de tesis):**
Mann-Kendall: **no_ejecutada** (`TEST_NOT_EXECUTED_MIN_SAMPLES`, n=7&lt;10) — primera vez en las 10 estaciones auditadas que esta rama del código se ejercita en la práctica (formulas-etapa1.md: "Si n &lt; 10 → no_ejecutada").
KS: Z=0.5455, crítico=1.358, veredicto=aprobada.
Chow: estadístico=2.0074, K_N=1.9381, veredicto=**rechazada** — **primera estación de las 10 auditadas donde Chow aislado detecta un atípico** (valor=10.99, índice=1 — el mínimo de la serie, 10.99). No forma parte de la tesis (agregado por Carlos), sin comparación posible, solo se señala como comportamiento nuevo del código.

### PASO 4 — Veredicto Etapa 1 (aislado, bypaseando el contrato): PASS
Con las funciones puras llamadas directamente (sin contrato), Etapa 1
aprobaría homogeneidad e independencia — coincide con la tesis. **Pero el
pipeline real (`ejecutar_etapa1()`) nunca llega a evaluar nada de esto: el
contrato bloquea antes, en el primer paso, por `n=7<10`.** Ver sección
PIPELINE COMPLETO más abajo para la verificación de ese bloqueo.

### PASO 5 — Parámetros Etapa 2 (aislado): PASS mayoritario (FAIL=0)
| Distribución              | Método            | diff% (por parámetro)                          | Nivel  | Causa |
|----------------------------|-------------------|--------------------------------------------------|--------|-------|
| Uniforme                  | Momentos/MV        | ambas ≤0.03%                                     | PASS   | —     |
| Exponencial beta          | Momentos/MV        | beta=+0.65%                                       | PASS   | —     |
| Exponencial x0beta        | Momentos/MV        | ambas ≤0.03%                                      | PASS   | —     |
| Gen. Exponencial          | Momentos           | alpha=+335.66%, lambda=+164.14%                   | INFO   | tesis internamente inconsistente — pendiente IV-77, mismo patrón est_01-08 (magnitud extrema por n pequeño) |
| Gen. Exponencial          | MV                 | alpha=+0.04%, lambda=-0.03%                       | PASS   | —     |
| Gen. Exponencial          | ML                 | alpha=-18.23%, lambda=+14.36%                     | INFO   | pendiente IV-84, mismo patrón previo |
| Normal                    | Momentos/MV/ML     | todas ≤0.01%                                      | PASS   | —     |
| Log-Normal 2p             | Momentos/MV        | mu_y=+0.05%, sigma_y=-0.06%                       | PASS   | —     |
| Log-Normal 3p             | Momentos           | NO_APLICABLE en ambos (METIS y tesis)             | PASS   | coincide — primera vez que esta marca (antes solo vista en LN2p) también coincide en ambos lados |
| Log-Normal 3p             | MV                 | x0=-606.23%, mu_y=+34.71%, sigma_y=-75.83%        | INFO   | **divergencia severa** — mismo tipo de anomalía ya visto en est_08 (LN3p MV con x0 divergente), acá mucho más extrema |
| Gamma 2p                  | Momentos/MV/ML     | todas ≤0.12%                                      | PASS   | —     |
| Gamma 3p                  | Momentos           | x0=+141.75%, alpha=+25.86%, beta=-36.88%          | INFO-A | g-propagación DECISIÓN013, magnitud extrema por n=7 |
| Gamma 3p                  | MV                 | todas ≤0.03%                                      | PASS   | —     |
| Gumbel                    | Momentos/MV/ML/ME  | todas ≤0.01%                                      | PASS   | —     |
| GVE                       | Momentos           | METIS status=ok (nu=26.15, alpha=10.19, beta=+0.675); tesis=NO_CONVERGE | INFO | METIS converge donde tesis no — mismo patrón ya visto en est_01 (2 veces) y est_08 (1 vez), ahora la 4ta ocurrencia |
| GVE                       | MV                 | METIS status=no_converge, coincide con tesis=NO_CONVERGE | PASS | — |
| GVE                       | ML                 | alpha=+7.07%, beta=-0.11%, nu=-1.62%              | PASS   | dentro de tolerancia práctica |
| Log-Pearson III           | Directo            | NO_APLICABLE (B=2.6022 ∉ (3,6]); tesis reporta alfa=0.333, beta=0.075, y0=3.287 | INFO | restricción IV-249 aplicada correctamente — patrón universal en las 10 estaciones |
| Log-Pearson III           | Indirecto          | alpha=+25.99%, beta=-36.94%, y0=+4.16%            | INFO-A | g-propagación DECISIÓN013 (gy de yi=ln(xi)) |
| Log-Pearson III           | MV                 | METIS status=no_converge; tesis reporta alfa=0.775, beta=1.123, y0=2.382 | INFO | tesis converge, METIS no — dirección "clásica" (opuesta a las anomalías GVE de arriba), mismo patrón ya visto en varias estaciones previas |

**Conteo aproximado: PASS=13, INFO-A=2, INFO=6, FAIL=0. Gen. Pareto no está en tabla de tesis (SKIP, patrón universal).**
Nota general: pese a n=7, la mayoría de los parámetros "limpios" (Uniforme,
Exp x0beta, Normal, LN2p, Gamma2p, Gamma3p MV, Gumbel, GVE ML) coinciden con
precisión &lt;1% — mejor de lo esperado para una muestra tan chica. Las
divergencias fuertes se concentran en los mismos casos ya identificados como
frágiles en estaciones anteriores (Gen.Exp Momentos/ML, LN3p MV, Gamma3p
Momentos, LP3 Indirecto, GVE Momentos).
### PASO 6 — EEA (aislado): PASS mayoritario
| Distribución | Método | EEA METIS | EEA Tesis | diff% | Nivel |
|---|---|---|---|---|---|
| Uniforme           | Momentos   |    2.7761 |    2.7768 |   -0.02% | PASS |
| Normal             | ML         |    2.7934 |    2.9141 |   -4.14% | PASS |
| GVE                | ML         |    2.6775 |    3.0643 |  -12.62% | INFO |
| Normal             | Momentos   |    3.0378 |    3.1667 |   -4.07% | PASS |
| Gumbel             | MV         |    3.4197 |    3.4206 |   -0.03% | PASS |
| Gamma 2p           | ML         |    3.4199 |       3.5 |   -2.29% | PASS |
| Gamma 2p           | MV         |    3.4466 |    3.5299 |   -2.36% | PASS |
| Gen. Exponencial   | MV         |    3.5637 |    3.5647 |   -0.03% | PASS |
| Gumbel             | ME         |    3.6575 |    3.6581 |   -0.02% | PASS |
| Log-Normal 2p      | Momentos   |    3.6828 |    3.6601 |   +0.62% | PASS |
| Gamma 2p           | Momentos   |    3.6081 |    3.7052 |   -2.62% | PASS |
| Gumbel             | ML         |    3.7900 |    3.7907 |   -0.02% | PASS |
| Gumbel             | Momentos   |    4.1026 |    4.1031 |   -0.01% | PASS |
| Uniforme           | MV         |    4.1603 |    4.1627 |   -0.06% | PASS |
| Gamma 3p           | Momentos   |    4.3983 |    4.2505 |   +3.48% | PASS |
| Exponencial x0beta | Momentos   |    5.2975 |    5.2981 |   -0.01% | PASS |
| Log-Pearson III    | Indirecto  |    6.6836 |    6.1286 |   +9.06% | INFO |
| Gamma 3p           | MV         |    6.4821 |    6.3409 |   +2.23% | PASS |
| Exponencial x0beta | MV         |    7.7270 |    7.7298 |   -0.04% | PASS |
| Log-Pearson III    | Directo    | N/A (no_aplicable) |    9.9861 | —      | INFO |
| Exponencial beta   | Momentos   |   12.0435 |   12.0441 |   -0.01% | PASS |
| GVE                | Momentos   | 3.2124 (METIS status=ok) | NO_CONVERGE | — | INFO |

**Conteo: PASS=14 (&lt;5%), INFO=7, FAIL=0.** A diferencia de est_01, acá el EEA
sigue de cerca al diff de parámetros en casi todos los casos — no aparece el
patrón "Causa C" (params casi idénticos, EEA muy distinto) con la frecuencia
de las estaciones "sanas" anteriores. Único caso algo más marcado: GVE ML
(-12.6%) y LP3 Indirecto (+9.1%), ambos ya explicados por su diff de
parámetros correspondiente en PASO5.

### PASO 7 — Cuantiles: PASS (FAIL=0)
Modelo seleccionado por Facundo: Uniforme (Momentos). Normal (Momentos L) como testigo.

| T [años] | Uniforme METIS | Uniforme Tesis | diff%  | Nivel | Normal ML METIS | Normal ML Tesis | diff%  | Nivel |
|----------|-----------------|-----------------|--------|-------|-------------------|-------------------|--------|-------|
|   2      |    27.60   |    27.60    |  -0.01% | PASS  |    27.60   |    27.60    |  -0.01% | PASS  |
|   5      |    37.34   |    37.34    |  +0.01% | PASS  |    35.91   |    35.78    |  +0.37% | PASS  |
|  10      |    40.59   |    40.59    |  +0.01% | PASS  |    40.26   |    39.86    |  +1.00% | PASS  |
|  20      |    42.22   |    42.21    |  +0.02% | PASS  |    43.85   |    42.97    |  +2.05% | PASS  |
|  25      |    42.54   |    42.54    |  +0.00% | PASS  |    44.90   |    43.81    |  +2.48% | PASS  |
|  50      |    43.19   |    43.19    |  +0.00% | PASS  |    47.89   |    46.02    |  +4.07% | PASS  |
| 100      |    43.52   |    43.51    |  +0.01% | PASS  |    50.58   |    47.72    |  +6.00% | INFO  |

**Uniforme (modelo seleccionado por Facundo): PASS=7/7, coincide casi exacto en toda la tabla — el mejor resultado de PASO7 de las 10 estaciones auditadas.**
**Normal ML (testigo): PASS=6/7, el error crece con T pero se mantiene &lt;6.1% incluso en T=100 — mucho más contenido que el patrón "Causa C" típico visto en otras estaciones.**
