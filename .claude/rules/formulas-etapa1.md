# Fórmulas de Etapa 1 — Implementación Real
Fuente: metis/core/*.py — generado para verificación contra tesis de Facundo, Caamaño Nelli & Dasso, y Chow (Bulletin 17B).

## Regla de uso
Este archivo DOCUMENTABA las fórmulas tal como eran implementadas en el código. 
Actualmente se modifico en funcion de como deben ser empleadas las mismas, referenciandose con la bilbiografia apropiada.
Sirve para verificar que coincidan con las fuentes bibliográficas.
Fuentes primarias: Tesis Facundo Ganancias Martínez; Caamaño Nelli & Dasso — Apéndice; Bulletin 17B (Chow).

α = 0.05 fijo en toda la Etapa 1. Z_crit = 1.96 (normal estándar, two-tailed).

---

## 1. Estadística Descriptiva
Archivo: `metis/core/descriptive.py`
Fuente: Tesis Facundo — Sección IV.2.2, Ecuaciones IV-1 a IV-9.
        MPP: Greenwood et al. (1979) apud Escalante Sandoval y Reyes Chávez (2005),
        Tesis Facundo — Sección IV.2.4, Ecuaciones IV-21 a IV-24.

```
n    = longitud de la serie
```

### Media — Ec. IV-1
```
x̄ = (1/n) · Σ xi                                          # (np.mean)
```

### Varianza sesgada — Ec. IV-2
```
S²_sesg = (1/n) · Σ(xi - x̄)²
```

### Varianza no sesgada — Ec. IV-3
```
S²_insesg = (1/(n-1)) · Σ(xi - x̄)²                       # (np.var, ddof=1)
```

### Desvío estándar (no sesgado) — Ec. IV-8
```
S = √S²_insesg                                             # (np.std, ddof=1)
```

### Coeficiente de variación — Ec. IV-9
```
CV = S / x̄
```

### Asimetría sesgada — Ec. IV-4
```
g_sesg = [(1/n) · Σ(xi - x̄)³] / (S²_sesg)^(3/2)         # (scipy.stats.skew, bias=True)
```

### Asimetría no sesgada — Ec. IV-5
```
g_insesg = n² / [(n-1)(n-2)] · g_sesg                     # (scipy.stats.skew, bias=False)
```

### Curtosis sesgada — Ec. IV-6
```
k_sesg = [(1/n) · Σ(xi - x̄)⁴] / (S²_sesg)²
```

### Curtosis no sesgada — Ec. IV-7
```
k_insesg = n³ / [(n-1)(n-2)(n-3)] · k_sesg
```

ATENCIÓN: scipy.stats.kurtosis devuelve excess kurtosis (k - 3) con bias=False.
La implementación debe sumar +3, o calcular k_insesg directamente desde la fórmula.

mín = min(xi)
máx = max(xi)

### Sumatoria de logaritmos naturales (insumo para MV en distribuciones log)
```
Σln = Σ ln(xi)
```

### Momentos de Probabilidad Pesada — Ec. IV-21 a IV-24
ORDENAMIENTO: xi ordenados de MAYOR a menor (i=1 es el valor más grande).
Los pesos (n-i) son decrecientes: el mayor valor recibe el peso más alto.
Fuente: Tesis Facundo p.60 — "valores ordenados de mayor o menor"; 
    convención estándar MPP (Greenwood et al., 1979).

```
M̂₀ = (1/n) · Σ xi                                         # Ec. IV-21

M̂₁ = 1/[n(n-1)] · Σ_{i=1}^{n-1} (n-i) · x_i             # Ec. IV-22

M̂₂ = 1/[n(n-1)(n-2)] · Σ_{i=1}^{n-2} (n-i)(n-i-1) · x_i            # Ec. IV-23

M̂₃ = 1/[n(n-1)(n-2)(n-3)] · Σ_{i=1}^{n-3} (n-i)(n-i-1)(n-i-2) · x_i  # Ec. IV-24

```

---

## 2. Independencia — Anderson
Archivo: `metis/core/independence.py`
Fuente: tesis Facundo - Sección III.3.1, Ecuaciones III-1 y III-3.

### Coeficiente de autocorrelación serial de lag k
```
r_k = Σ_{i=1}^{n-k} (x_i - x̄)(x_{i+k} - x̄)  /  Σ_{i=1}^{n} (x_i - x̄)²  # [Ec. III-1]
```
k varía de 1 a k_max = n // 3

### Valor crítico por lag k (two-tailed, α=5%)
```
r_crit_upper(k) = (-1 + 1.96 · √(n-k-1)) / (n-k)                    # [Ec. III-3]
r_crit_lower(k) = (-1 - 1.96 · √(n-k-1)) / (n-k)                    # [Ec. III-3]
```

### Veredicto
```
lags_fuera = count( r_k > r_crit_upper(k) OR r_k < r_crit_lower(k) )
aprobada   = (lags_fuera / k_max) ≤ 0.10
```
Nota: La prueba es global y permite una tolerancia del 10%. El veredicto NO falla si un solo lag aislado se desvía, sino únicamente si la cantidad de lags fuera de las bandas supera el 10% del total de lags calculados.

### Lo que se reporta
```
estadístico  = r_k con mayor |r_k| entre todos los lags calculados
valor_critico = min( r_crit_upper(k) ) sobre todos los k
```
Nota de UI: Al no existir un único valor crítico (varía según el lag k), se reporta por diseño el mínimo del upper bound por ser el límite más restrictivo de la serie. En los gráficos de la interfaz se deben dibujar las bandas dinámicas lag por lag.

---

## 3. Independencia — Wald-Wolfowitz
Archivo: `metis/core/independence.py`
Fuente: Tesis Facundo — Sección III.3.2, Ecuaciones III-4, III-5 y III-6.

### Rachas
```
signo_i = (xi > x̄)                    — True/False
R       = número de rachas (bloques de signos consecutivos iguales)
n1      = count(xi > x̄)
n2      = n - n1
```
Si n1=0 o n2=0 → no_ejecutada (todos los valores iguales o todos del mismo lado)

### Estadístico Z
```
µ_R  = (2 · n1 · n2 / n) + 1                        # [Ecuación III-5]
σ_R  = √[ (µ_R - 1) · (µ_R - 2) / (n - 1) ]         # [Ecuación III-6]
Z    = (R - µ_R) / σ_R                             # Ec. III-4 — la tesis imprime σ²_R en el denominador, pero los resultados numéricos
```
Nota: # Ec. III-4 — σ²_R es la varianza de R; σ_R definida en Ec. III-6 como √[(µ_R-1)(µ_R-2)/(n-1)]
de la tesis (Tabla IV-4: Z=0.37) confirman que el divisor correcto es σ_R (desvío).
Es un error de notación en la ecuación original.

### Veredicto
```
valor_critico = 1.96  (siempre — normal estándar)
aprobada      = |Z| ≤ 1.96
```
Si n ≤ 40 → agrega warning TEST_WARNING_SMALL_SAMPLE (pero ejecuta igual)

### Jerarquía Anderson–Wald
Anderson manda en el veredicto de independencia.
Si Anderson aprueba → INDEPENDIENTE, aunque Wald rechace.
Si Anderson rechaza → DEPENDIENTE (warning CRÍTICO), independientemente de Wald.

---

## 4. Homogeneidad — Helmert
Archivo: metis/core/homogeneity.py
Fuente: tesis Facundo, Cap. III

### Secuencias y cambios de signo
```
signo_i  = (xi > x̄)
S        = count( signo_i == signo_{i-1} )   para i=2..n   (Secuencias)
C        = count( signo_i ≠ signo_{i-1} )    para i=2..n   (Cambios)
```

### Estadístico y Veredicto 
```
diferencia = S - C                             # [Ec. III-7]
limite     = √(n - 1)                          # [Ec. III-7]
aprobada   = |diferencia| ≤ limite             # [Ec. III-7]
```

---

## 5. Homogeneidad — t de Student
Archivo: `metis/core/homogeneity.py`
Fuente: Tesis Facundo — Sección III.4.2, Ecuación III-8.

### Partición
```
s1 = serie[:n1]       (primeros n1 datos)
s2 = serie[n1:n1+n2]  (siguientes n2 datos)
```

### Estadístico t
```
x̄1, x̄2     = medias de s1 y s2
Var1, Var2  = varianzas muestrales (ddof=1)
ν           = n1 + n2 - 2                        # [Ec. III-8] (Grados de libertad)
Sp²         = [n1·Var1 + n2·Var2] / ν             # [Ec. III-8] exacta — confirmado Facundo est_02
                                                   # NOTA: usa n·Var, no (n-1)·Var
t           = (x̄1 - x̄2) / (Sp · √(1/n1 + 1/n2))  # [Ec. III-8] (Estadístico t)
```

### Veredicto
```
valor_critico = t_{ν, α/2=0.025}   (scipy.stats.t.ppf)
aprobada      = |t| ≤ valor_critico              # según texto p.50, Tesis Facundo
```

Nota: Sp² es la varianza pooled, álgebraicamente equivalente a la expresión III-8 de la tesis. El valor crítico se obtiene de la distribución t de Student con ν grados de libertad, y el veredicto se basa en comparar el valor absoluto del estadístico t contra el valor crítico bilateral.

---

## 6. Homogeneidad — Cramer (prueba principal)
Archivo: `metis/core/homogeneity.py`
Fuente: Tesis Facundo — Sección III.4.3, Ecuaciones III-9 a III-15.

### Partición (default)
```
x̄_global  = media de la serie completa
S_global  = desvío estándar de la serie completa (np.std, ddof=1)

# Lógica de tamaños — verificado numéricamente contra tesis Facundo est_02 (n=24)
n_w1      = ceil(n · 0.60)   → para n=24: n_w1=15  (reproduce tau_w1=0.18289)
n_w2      = floor(n · 0.30)  → para n=24: n_w2=7   (reproduce tau_w2=0.35206)
# ceil para n_w2 da n_w2=8 → tau_w2=0.67071 (incorrecto). Ver DECISIÓN 011.

# Slicing: últimos n_w datos cronológicos del registro
s_w1      = serie[-n_w1:]
s_w2      = serie[-n_w2:]

x̄_w1      = media de s_w1
x̄_w2      = media de s_w2
```
NOTA DE ARQUITECTURA: Aunque el usuario personalice los tamaños de los bloques (CU-01/02/03), el principio de Cramer exige que se extraigan los últimos datos del registro y se calculen sus medias de forma independiente.


### Indicadores tau (Estadísticos intermedios)
```
tau_w1 = (x̄_w1 - x̄_global) / S_global                     # [Ec. III-13] (Submuestra de 60%)
tau_w2 = (x̄_w2 - x̄_global) / S_global                     # [Ec. III-14] (Submuestra de 30%)
```

### Indicadores de Prueba t_w (Estadístico Final) — Ec. III-15
```
t_w = √[ (n_w · (n - 2)) / (n - n_w · (1 + tau_w²)) ] · |tau_w|

t_w1   verificado: √[(15·22)/(24-15·(1+0.18289²))]·0.18289 = 1.13970  ✓
t_w2   verificado: √[(7·22) /(24-7 ·(1+0.35206²))]·0.35206 = 1.08774  ✓
```

### Grados de libertad y valor crítico
```
ν = n - 2    (para n=24: ν=22, crit=2.0739)

DECISIÓN: ν = n - 2, no ν = n + n_w - 2.
Justificación: reproduce exactamente los resultados numéricos de Facundo.
La tesis escribe "ν = n₁ + n₂ - 2" en p.51 pero la práctica numérica
del autor es consistente con ν = n - 2 para ambos subgrupos.
Ante discrepancia texto/práctica, se prioriza la práctica numérica
de la fuente bibliográfica primaria. PENDIENTE confirmación formal Facundo.
Ver decisions-log.md — DECISIÓN 011.
```

Nota: Cada bloque se compara individualmente contra la media macro (x̄_global) y el desvío macro (S_global) de toda la serie, nunca entre sí.

### Veredicto
```
valor_critico_w1 = t_{ν_w1, α/2=0.025}   (scipy.stats.t.ppf)
valor_critico_w2 = t_{ν_w2, α/2=0.025}   (scipy.stats.t.ppf)

aprobada         = (t_w1 ≤ valor_critico_w1) AND (t_w2 ≤ valor_critico_w2)  # Según texto p.51, Tesis Facundo
```
Nota: Para que la serie sea homogénea, ambas submuestras (configuradas o por default) deben aprobar simultáneamente sus respectivos límites críticos de la t de Student. Cramer rechaza → homogeneidad_critica (warning CRÍTICO).

### Jerarquía de homogeneidad
```
Cramer rechaza              → homogeneidad_critica  (CRÍTICO)
Cramer aprueba, Helmert o
  t de Student rechazan    → homogeneidad_warning   (normal)
Todos aprueban              → homogeneidad_ok
```

---

## 7. Tendencia — Mann-Kendall
Archivo: metis/core/trend.py
Fuente: Caamaño Nelli & Colladon — Apéndice A.5.1, Ec. A.51–A.55 (método base);
        implementación vía pymannkendall (Mann & Kendall, 1945/1975) con
        corrección por empates según Kendall (1975).
        Valor crítico: Z = 1.96 (normal estándar bilateral, α=0.05).

### Control de Umbrales de Serie
Si n < 10  → no_ejecutada, TEST_NOT_EXECUTED_MIN_SAMPLES
Si n ≥ 10 AND n ≤ 30 → ejecuta con warning TEST_WARNING_SMALL_SAMPLE
Si n > 30  → ejecuta (Rango Óptimo)

Nota de lógica: Las muestras menores a 10 observaciones se bloquean por completo
en el sistema. Las series de entre 10 y 30 datos disparan una advertencia en la
interfaz indicando que los resultados estadísticos no son garantizables debido al
tamaño de la muestra.

### Para n ≥ 10 (fórmula analítica vía pymannkendall)
S   = Σ_{i<j} sgn(xj - xi)                             # Estadístico S de Kendall (Ec. A.51–A.53)
Z   = estadístico normalizado (aproximación normal con corrección por empates)  # Ec. A.55
valor_critico = 1.96                                    # Normal estándar bilateral, α=0.05
aprobada = not resultado.h                              # h=True significa tendencia detectada

Nota: La aproximación normal con corrección por varianza ante empates se delega al
paquete nativo pymannkendall, contrastando el estadístico Z tipificado contra el
valor crítico bilateral de la distribución normal estándar. El estadístico S es
equivalente al índice I = VS − VI de Caamaño (Ec. A.53).

---

## 8. Tendencia — Kolmogorov-Smirnov
Archivo: metis/core/trend.py
Fuente: Caamaño Nelli & Colladon — Apéndice A.5.2, Ec. A.56–A.57, Tabla A.5 (método base);
        implementación vía scipy.stats.ks_2samp (two-sided).
        Equivalencia: scipy calcula p-valor exacto en lugar de contrastar D·√(nm/(n+m))
        contra Z_crit = 1.358 (Tabla A.5, α=0.05). El criterio aprobada = p_valor > 0.05
        es matemáticamente equivalente.

### Partición
primera = serie[:n//2]
segunda = serie[n//2:]
n = len(primera),  m = len(segunda)

Para n_total impar: segunda tiene un dato más que primera.

### Estadístico
D, p_valor = scipy.stats.ks_2samp(primera, segunda, alternative='two-sided')  # Ec. A.56–A.57

### Veredicto
estadístico   = D                      # Distancia máxima vertical entre CDFs empíricas
valor_critico = 1.358                  # Tabla A.5, Caamaño, α=0.05 (referencia)
aprobada      = p_valor > 0.05         # Equivalente vía p-valor exacto de scipy

Nota: scipy.stats.ks_2samp calcula el p-valor exacto en lugar de tipificar D manualmente.
El criterio p_valor > 0.05 es matemáticamente equivalente a contrastar Z = D·√(nm/(n+m))
contra Z_crit = 1.358 de Tabla A.5. Se preserva el valor crítico de referencia para
trazabilidad bibliográfica.

### Lógica OR de tendencia
TEST_WARNING_TREND se emite si Mann-Kendall rechaza OR KS rechaza.

---

## 9. Atípicos — Chow
Archivo: metis/core/outliers.py
Fuente: Chow (Bulletin 17B) — Sección 9, Ecuaciones 7 y 8a, Apéndice 4 (método base);
        umbral crítico vía corrección de Bonferroni con distribución t, según
        implementación de referencia del co-director Mgter. Ing. Carlos Catalini.

### Condiciones previas
tipo_variable == "caudal_precipitacion" AND any(xi == 0)
  → no_ejecutada, TEST_NOT_EXECUTED_ZEROS

any(xi ≤ 0)
  → no_ejecutada, TEST_NOT_EXECUTED_CONDITION
  (log no definido para xi ≤ 0)

### Chow aplica sobre logaritmos
yi  = ln(xi)          para todos los xi
ȳ   = media(yi)
S_y = std(yi, ddof=1)
Z_i = |yi - ȳ| / S_y  para cada i       # Estadístico estandarizado por observación

### Estadístico y valor crítico
estadístico   = max(Z_i)                              # Ec. 7 / 8a — Chow
ν             = n - 1                                 # Grados de libertad
prob_cuantil  = 1 - (0.05 / (2 · n))                 # Corrección de Bonferroni
valor_critico = t_{ν, prob_cuantil}   (scipy.stats.t.ppf)

Nota: Chow define los umbrales X_H = X̄ + K_N·S y X_L = X̄ - K_N·S con K_N de tabla
(Apéndice 4, 10% significancia). La implementación reemplaza K_N por el cuantil t
con corrección de Bonferroni (1 - α/2n), que es estadísticamente equivalente y
elimina la dependencia de la tabla hardcodeada.

### Veredicto
atipico_detectado = estadístico > valor_critico
veredicto         = "rechazada" si atípico detectado, "aprobada" si no
warning_nivel     = siempre "normal" (Chow nunca genera warning CRÍTICO)
valor_atipico     = xi original (no el logaritmo) con mayor Z_i

---