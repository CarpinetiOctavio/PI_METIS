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

## Resultados de Regresión METIS --> PIPELINE COMPLETO (ejecución en vivo, 2026-07-14)

**Qué es esto:** salida real de correr `ejecutar_etapa1()` seguido de
`ejecutar_etapa2()` — el pipeline completo tal como orquesta
`pipeline.py`/`pipeline2.py` hoy — sobre la serie cruda de esta estación
(n=40 efectivo, 2 interrupciones descartadas). Mismo formato que las 8
estaciones anteriores.

**Estación de uso exclusivamente académico:** Etapa 1 la rechaza por
unanimidad en METIS (igual que en la tesis) — `contract.bloqueante=False`
(no bloquea por tamaño de muestra, n=40≥30) pero homogeneidad e
independencia rechazan. El pipeline avanza igual a Etapa 2 porque METIS
**detecta y advierte, no bloquea** (principio de negocio central del
proyecto — ver CLAUDE.md) excepto por el único caso absoluto de n&lt;10. Todo
lo de Etapa 2 de esta sección hereda la misma advertencia académica que ya
consta en la ficha de Facundo arriba en este archivo.

**Contexto — auditoría de cableado (Fase 2, Bloque 6/7):** diagnóstico,
no prueba de cierre. **No forma parte del Bloque 8.**

Invocación exacta:
```python
r1 = ejecutar_etapa1(
    serie=serie,  # lista cruda, 2 interrupciones ya descartadas -> n=40
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
| n | 40 |
| Media [m³/s] | 144.375 |
| Mediana [m³/s] | 127.5 |
| Varianza (no sesgada) [m³/s]² | 13404.445512820514 |
| Varianza (sesgada) [m³/s]² | 13069.334375 |
| Desvío [m³/s] | 115.77756912640943 |
| Asimetría Sesgada | 0.7427133361398364 |
| Asimetría No Sesgada (g) | 0.8018497556165575 |
| Curtosis Sesgada | 2.3976341884094556 |
| Curtosis No Sesgada (k) | 2.7984204701135273 |
| Coeficiente de Variación (CV) | 0.801922556719719 |
| Sumatoria ln(xi) | 183.29169380597537 |
| beta_0 = M0 | 144.375 |
| beta_1 = M1 | 104.53717948717949 |
| beta_2 = M2 | 82.9365721997301 |
| beta_3 = M3 | 68.97796804902067 |
| Máximo [m³/s] | 410.0 |
| Mínimo [m³/s] | 15.0 |
| Rango [m³/s] | 395.0 |

### Etapa 1 — Homogeneidad (pipeline completo — Sheet 2)

#### Helmert
| Parámetro | Valor |
|-----------|-------|
| Estadístico (S-C) | 21.0 |
| Valor crítico (± lim) | 6.244997998398398 |
| Veredicto | rechazada |
| Warning | TEST_WARNING_HOMOGENEITY |

#### t de Student
| Parámetro | Valor |
|-----------|-------|
| Estadístico t | 7.352894418371756 |
| n1 | 20 |
| n2 | 20 |
| Valor crítico (tabla) | 2.024394163911969 |
| Veredicto | rechazada |
| Warning | TEST_WARNING_HOMOGENEITY |

#### Cramer
| Parámetro | Valor |
|-----------|-------|
| Estadístico (max t_w) | 3.8848628024442884 |
| n_w1 | 24 |
| n_w2 | 12 |
| Valor crítico (tabla) | 2.024394163911969 |
| Veredicto | rechazada |
| Warning | TEST_CRITICAL_HOMOGENEITY (critico) |

**Veredicto homogeneidad (pipeline):** homogeneidad_critica

### Etapa 1 — Independencia (pipeline completo — Sheet 2)

#### Anderson
| Parámetro | Valor |
|-----------|-------|
| Estadístico (máx r_k) | 0.5597152279417443 |
| Valor crítico | 0.28415460081060456 |
| Veredicto | rechazada |
| Warning | TEST_CRITICAL_INDEPENDENCE (critico) |

#### Wald-Wolfowitz
| Parámetro | Valor |
|-----------|-------|
| Estadístico Z | -3.40758083438341 |
| Valor crítico (α=0.05) | ± 1.959963984540054 |
| Veredicto | rechazada |
| Warning | TEST_WARNING_SMALL_SAMPLE |

**Veredicto independencia (pipeline):** dependiente

### Etapa 1 — Tendencia y Atípicos (pipeline completo) — sin ficha de Facundo de referencia

#### Mann-Kendall
| Parámetro | Valor |
|-----------|-------|
| Estadístico | -4.826040249776023 |
| Valor crítico | 1.959963984540054 |
| Veredicto | rechazada |
| Warning | TEST_WARNING_TREND |

#### Kolmogorov-Smirnov (tendencia)
| Parámetro | Valor |
|-----------|-------|
| Estadístico (Z tipificado) | 2.6879360111431225 |
| Valor crítico | 1.358 |
| Veredicto | rechazada |
| Warning | TEST_WARNING_TREND |

#### Chow
| Parámetro | Valor |
|-----------|-------|
| Estadístico (máx Z_i) | 1.9396094601634535 |
| Valor crítico (K_N) | 2.867542487054772 |
| Veredicto | aprobada |

**Veredicto general Etapa 1 (pipeline):** nivel_confianza=`con_warnings` — warnings: TEST_CRITICAL_INDEPENDENCE, TEST_WARNING_SMALL_SAMPLE, TEST_CRITICAL_HOMOGENEITY, TEST_WARNING_TREND

### Etapa 2 — Parámetros, EEA y Estado (pipeline completo — Sheet 3)
| Distribución | Método | Parámetro 1 | Parámetro 2 | Parámetro 3 | EEA [m³/s] | Status |
|---|---|---|---|---|---|---|
| Uniforme | Momentos | alfa = -56.1576 | beta = 344.9076 |  | 34.5958 | ok |
| Uniforme | Máxima Verosimilitud | alfa = 15.0000 | beta = 410.0000 |  | 77.9243 | ok |
| Exponencial beta | Momentos | beta = 0.006926 |  |  | 30.7735 | ok |
| Exponencial beta | Máxima Verosimilitud | beta = 0.006926 |  |  | 30.7735 | ok |
| Exponencial x0 y beta | Momentos | x0 = 28.5974 | beta = 115.7776 |  | 30.0903 | ok |
| Exponencial x0 y beta | Máxima Verosimilitud | x0 = 11.6827 | beta = 132.6923 |  | 28.1006 | ok |
| Generalizada Exponencial | Momentos | alfa = 1.6724 | lambda = 0.009431 |  | 26.7245 | ok |
| Generalizada Exponencial | Máxima Verosimilitud | alfa = 1.4512 | lambda = 0.008694 |  | 25.4635 | ok |
| Generalizada Exponencial | Momentos L | alfa = 0.299165 | lambda = -0.005176 |  | 313.2509 | ok |
| Normal | Momentos | mu = 144.3750 | sigma = 115.7776 |  | 36.7760 | ok |
| Normal | Máxima Verosimilitud | mu = 144.3750 | sigma = 115.7776 |  | 36.7760 | ok |
| Normal | Momentos L | mu = 144.3750 | sigma = 114.6473 |  | 36.8504 | ok |
| Log Normal (2 parámetros) | Momentos | mu_y = 4.5823 | sigma_y = 0.966299 |  | 51.3768 | ok |
| Log Normal (2 parámetros) | Máxima Verosimilitud | mu_y = 4.5823 | sigma_y = 0.966299 |  | 51.3768 | ok |
| Log Normal (3 parámetros) | Momentos | x0 = -298.6504 | mu_y = 6.0606 | sigma_y = 0.25703 | 27.4758 | ok |
| Log Normal (3 parámetros) | Máxima Verosimilitud | x0 = 7.1097 | mu_y = 4.4516 | sigma_y = 1.0829 | 65.5194 | ok |
| Gamma (2 parámetros) | Momentos | alfa = 92.8446 | beta = 1.5550 |  | 26.2459 | ok |
| Gamma (2 parámetros) | Máxima Verosimilitud | alfa = 100.8959 | beta = 1.4309 |  | 25.3740 | ok |
| Gamma (2 parámetros) | Momentos L | alfa = 109.7051 | beta = 1.3160 |  | 25.2549 | ok |
| Gamma (3 parámetros) | Momentos | x0 = -144.4012 | alfa = 46.4181 | beta = 6.2212 | 26.5838 | ok |
| Gamma (3 parámetros) | Máxima Verosimilitud |  |  |  | — | no_converge |
| Gumbel | Momentos | mu = 92.2751 | alfa = 90.3065 |  | 26.5957 | ok |
| Gumbel | Máxima Verosimilitud | mu = 92.0667 | alfa = 84.3594 |  | 30.2276 | ok |
| Gumbel | Momentos L | mu = 90.4968 | alfa = 93.3414 |  | 25.6458 | ok |
| Gumbel | Máxima Entropía | mu = 93.4792 | alfa = 88.1746 |  | 27.5245 | ok |
| GVE (Valores Extremos) | Momentos | nu = 93.0441 | alfa = 94.0124 | beta = 0.032495 | 26.8364 | ok |
| GVE (Valores Extremos) | Máxima Verosimilitud | nu = 70.8880 | alfa = 62.6195 | beta = -0.542196 | 78.2992 | ok |
| GVE (Valores Extremos) | Momentos L | nu = 86.8893 | alfa = 85.3501 | beta = -0.089287 | 27.0984 | ok |
| Log Pearson tipo III | Momentos Método Directo |  |  |  | — | no_aplicable |
| Log Pearson tipo III | Momentos Método Indirecto | alfa = 0.138096 | beta = 48.9619 | y0 = -2.1792 | 67.9087 | ok |
| Log Pearson tipo III | Máxima Verosimilitud |  |  |  | — | no_converge |
| Generalizada de Pareto | Momentos | mu = -7.7019 | sigma = 207.2315 | epsilon = 0.362676 | 279.5396 | ok |
| Generalizada de Pareto | Máxima Verosimilitud |  |  |  | — | no_converge |
| Generalizada de Pareto | Mínimos Cuadrados | mu = 15.0000 | sigma = 126.1010 | epsilon = 0.000011 | 29.2186 | ok |
| Generalizada de Pareto | Momento Prob. Pesada | mu = -33.2020 | sigma = 2,134.8564 | epsilon = 4.2898 | 679,050,372.6477 | ok |

### Notas de cableado — Bloque 6/7 (solo señalamiento)

**¿Ceros en la serie?** No — mínimo observado = 15.0. `tiene_ceros=False`. La rama `STATUS_DISABLED_ZEROS` sigue sin ejercitarse en ninguna estación auditada hasta ahora.

**Cambios de status vs. est_02** (comparando categoría, no valor numérico):
- `gen_exponencial/momentos`: est_02=`ok` -> est_01=`ok` (sin cambio de categoría, aunque tesis reporta NO_CONVERGE para est_01 — ver UNITARIAS PASO5)
- `logpearson3/mv`: est_02=`ok` -> est_01=`no_converge`
- `gamma3p/momentos`: est_02=`ok` -> est_01=`ok` (sin cambio de categoría; sí converge acá, a diferencia de est_03/est_04)
- `gamma3p/mv`: est_02=`no_converge` -> est_01=`no_converge` (sin cambio)
- Esta es la primera estación con **3 distribuciones** donde METIS converge (`ok`) pero la tesis reporta `NO_CONVERGE`: `gen_exponencial/momentos`, `gve/momentos`, `gve/mv` — ver detalle y valores en UNITARIAS PASO5. No investigado.

**GVE / MV — rama de inicialización:**
- MOMENTOS converge — guard IV-202 pasa (g=0.8018, beta0=0.0325, nu0=93.0441, alpha0=94.0124). **Primera estación de las 9 auditadas donde la condición inicial de Momentos pasa el guard sin necesitar el fallback a ML.**
