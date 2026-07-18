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

## Resultados de Regresión METIS --> PIPELINE COMPLETO (ejecución en vivo, 2026-07-14)

**Qué es esto — distinto de las 9 estaciones anteriores:** para esta estación
el objetivo principal de la corrida NO es reproducir los números de Facundo,
es **verificar que el pipeline real bloquea correctamente para n&lt;10**, el único
caso de bloqueo duro documentado en todo METIS (ver CLAUDE.md — "< 10 datos →
error bloqueante. Pipeline se detiene. Único caso.").

### Paso 1 — Confirmación del bloqueo real (`ejecutar_etapa1()`)

Invocación exacta:
```python
serie = [24.32, 10.99, 33.9, 31.91, 39.55, 22.0, 30.52]  # n=7, S/D ya descartados
r1 = ejecutar_etapa1(
    serie=serie,
    tipo_variable="caudal_precipitacion",
    resolucion_temporal="anual",
    timestamps=None,
    cramer_particion="default",
)
```

**Resultado real:**
```python
r1.contract.bloqueante   = True
r1.contract.codigo_error = 'CONTRACT_SERIES_TOO_SHORT'
r1.contract.warnings     = []
r1.descriptive           = None
r1.independencia         = []
r1.homogeneidad          = []
r1.tendencia             = []
r1.atipicos              = []
r1.nivel_independencia   = None
r1.nivel_homogeneidad    = None
r1.nivel_confianza       = 'rechazado'
r1.warnings              = []
```

**Confirmado: el pipeline real bloquea exactamente como especifica la
arquitectura.** Ninguna prueba estadística se ejecuta — el contrato corta la
ejecución en el primer paso, antes de calcular siquiera la estadística
descriptiva. Por diseño (`El pipeline siempre arranca por Etapa 1 — nunca se
puede ejecutar Etapa 2 directamente`, constraints.md), Etapa 2 tampoco corre
en el flujo real para esta estación — no hay ningún camino del producto real
donde n=7 produzca un resultado de Etapa 2.

### Paso 2 — Etapa 2 ejecutada de forma aislada, fuera del flujo real, solo para comparar contra la ficha académica de Facundo

**Esto NO es "el pipeline" — es `ejecutar_etapa2()` invocada manualmente,
saltándose la secuencia real del producto**, únicamente para tener un dato más
de comparación contra los números académicos de la tesis (mismo propósito que
la sección UNITARIAS de arriba, pero pasando por el orquestador de Etapa 2 en
vez de llamar a cada `ajustar()`/`cuantil()` por separado — se verificó que dan
resultados idénticos, como en las 9 estaciones anteriores).

```python
r2 = ejecutar_etapa2(np.array(serie), tiene_ceros=False)  # llamada directa, fuera de secuencia
```

### Etapa 2 — Parámetros, EEA y Estado (ejecución aislada — Sheet 3)
| Distribución | Método | Parámetro 1 | Parámetro 2 | Parámetro 3 | EEA [m³/s] | Status |
|---|---|---|---|---|---|---|
| Uniforme | Momentos | alfa = 11.3566 | beta = 43.8406 |  | 2.7761 | ok |
| Uniforme | Máxima Verosimilitud | alfa = 10.9900 | beta = 39.5500 |  | 4.1603 | ok |
| Exponencial beta | Momentos | beta = 0.036234 |  |  | 12.0435 | ok |
| Exponencial beta | Máxima Verosimilitud | beta = 0.036234 |  |  | 12.0435 | ok |
| Exponencial x0 y beta | Momentos | x0 = 18.2212 | beta = 9.3773 |  | 5.2975 | ok |
| Exponencial x0 y beta | Máxima Verosimilitud | x0 = 8.2219 | beta = 19.3767 |  | 7.7270 | ok |
| Generalizada Exponencial | Momentos | alfa = 22.7850 | lambda = 0.134974 |  | 4.1526 | ok |
| Generalizada Exponencial | Máxima Verosimilitud | alfa = 9.9341 | lambda = 0.103672 |  | 3.5637 | ok |
| Generalizada Exponencial | Momentos L | alfa = 0.58055 | lambda = -0.016957 |  | 83.6703 | ok |
| Normal | Momentos | mu = 27.5986 | sigma = 9.3773 |  | 3.0378 | ok |
| Normal | Máxima Verosimilitud | mu = 27.5986 | sigma = 9.3773 |  | 3.0378 | ok |
| Normal | Momentos L | mu = 27.5986 | sigma = 9.8785 |  | 2.7934 | ok |
| Log Normal (2 parámetros) | Momentos | mu_y = 3.2517 | sigma_y = 0.425751 |  | 3.6828 | ok |
| Log Normal (2 parámetros) | Máxima Verosimilitud | mu_y = 3.2517 | sigma_y = 0.425751 |  | 3.6828 | ok |
| Log Normal (3 parámetros) | Momentos |  |  |  | — | no_aplicable |
| Log Normal (3 parámetros) | Máxima Verosimilitud | x0 = -176.5565 | mu_y = 5.3180 | sigma_y = 0.043142 | 3.8382 | ok |
| Gamma (2 parámetros) | Momentos | alfa = 3.1862 | beta = 8.6619 |  | 3.6081 | ok |
| Gamma (2 parámetros) | Máxima Verosimilitud | alfa = 3.5718 | beta = 7.7268 |  | 3.4466 | ok |
| Gamma (2 parámetros) | Momentos L | alfa = 3.6567 | beta = 7.5474 |  | 3.4199 | ok |
| Gamma (3 parámetros) | Momentos | x0 = 8.3308 | alfa = 4.5638 | beta = 4.2219 | 4.3983 | ok |
| Gamma (3 parámetros) | Máxima Verosimilitud | x0 = 10.7608 | alfa = 15.3488 | beta = 1.0970 | 6.4821 | ok |
| Gumbel | Momentos | mu = 23.3788 | alfa = 7.3143 |  | 4.1026 | ok |
| Gumbel | Máxima Verosimilitud | mu = 23.0286 | alfa = 9.1595 |  | 3.4197 | ok |
| Gumbel | Momentos L | mu = 22.9562 | alfa = 8.0427 |  | 3.7900 | ok |
| Gumbel | Máxima Entropía | mu = 22.6837 | alfa = 8.5148 |  | 3.6575 | ok |
| GVE (Valores Extremos) | Momentos | nu = 26.1507 | alfa = 10.1935 | beta = 0.674959 | 3.2124 | ok |
| GVE (Valores Extremos) | Máxima Verosimilitud |  |  |  | — | no_converge |
| GVE (Valores Extremos) | Momentos L | nu = 25.9685 | alfa = 11.1234 | beta = 0.665242 | 2.6775 | ok |
| Log Pearson tipo III | Momentos Método Directo |  |  |  | — | no_aplicable |
| Log Pearson tipo III | Momentos Método Indirecto | alfa = 0.419549 | beta = 1.0298 | y0 = 2.8196 | 6.6836 | ok |
| Log Pearson tipo III | Máxima Verosimilitud |  |  |  | — | no_converge |
| Generalizada de Pareto | Momentos | mu = 3.6083 | sigma = 90.5042 | epsilon = 2.7725 | 5,229.5463 | ok |
| Generalizada de Pareto | Máxima Verosimilitud |  |  |  | — | no_converge |
| Generalizada de Pareto | Mínimos Cuadrados | mu = 10.9641 | sigma = 60.3964 | epsilon = 1.8816 | 800.2388 | ok |
| Generalizada de Pareto | Momento Prob. Pesada | mu = -34.2412 | sigma = 759.9829 | epsilon = 9.8022 | 27,586,258,543.5005 | ok |

### Notas de cableado — Bloque 6/7 (solo señalamiento)

**¿Ceros en la serie?** No — mínimo observado = 10.99. `tiene_ceros=False`.

**Verificación de arquitectura (el hallazgo principal de esta estación):**
`ejecutar_etapa1()` bloquea correctamente para n=7&lt;10 — comportamiento
esperado, confirmado, sin hallazgos de cableado. Es la primera de las 10
estaciones auditadas donde se ejercita este camino del código (todas las
demás tenían n≥19).

**Cambios de status vs. est_02** (comparando categoría, no valor numérico,
sobre la corrida aislada de Etapa 2 — recordar que en el flujo real esta
estación nunca llega a Etapa 2):
- `gve/momentos`: est_02=`ok` -> est_09=`ok` (sin cambio de categoría, aunque tesis reporta NO_CONVERGE para est_09 — ver UNITARIAS PASO5)
- `logpearson3/mv`: est_02=`ok` -> est_09=`no_converge`
- `lognormal3p/momentos`: est_02=`ok` -> est_09=`no_aplicable`

**GVE / MV — rama de inicialización:**
- MOMENTOS converge — guard IV-202 pasa (g=-0.9734, beta0=0.6750, nu0=26.1507, alpha0=10.1935). Segunda estación (después de est_01) de las 10 donde Momentos pasa el guard sin fallback a ML.
