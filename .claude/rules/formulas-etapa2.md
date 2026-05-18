# Fórmulas de Etapa 2 — Referencias Bibliográficas
# Fuente principal: Tesis Facundo Ganancias Martínez, Capítulo IV

## Regla de uso
Ninguna fórmula de estimación de parámetros se implementa sin
referencia explícita a una ecuación de esta tabla.
Si una entrada dice PENDIENTE, se consulta a Facundo antes de implementar
esa combinación distribución+método.

---

## Probabilidades empíricas — Weibull
T = (n+1)/m,  P = 1 - 1/T
Fuente: Tesis Facundo, Cap. IV sección IV.1

---

## EEA — Error Estándar de Ajuste
EEA = sqrt( sum(QT_obs - QT_est)^2 / (n - mp) )
n  = longitud de la serie
mp = número de parámetros de la distribución ajustada
Fuente: Tesis Facundo, Ecuación IV-263

---

## 1. Distribución Uniforme
Parámetros: α, β

Momentos:
  α̂ = x̄ - √3·S    (IV-58)
  β̂ = x̄ + √3·S    (IV-59)

MV:
  α̂ = min(x)       (IV-60)
  β̂ = max(x)       (IV-61)

Cuantil:
  xT = F(x)·(β - α) + α    (IV-62)

---

## 2. Exponencial β
Parámetros: β

Momentos y MV (coinciden):
  β̂ = 1/x̄    (IV-66)

Cuantil:
  xT = -ln[1 - F(x)] / β    (IV-67)

RESTRICCIÓN: válida para x > 0 (IV-65)
Deshabilitada si algún xi = 0 (confirmado con Facundo)

---

## 3. Exponencial x0 y β
Parámetros: x0, β

Momentos:
  β̂ = S           (IV-70)
  x̂0 = x̄ - S     (IV-71)

MV:
  β̂ = (sum(xi) - n·x1) / (n·(n-1))    (IV-72)
  x̂0 = x1 - β̂/n                        (IV-73)
  x1 = mínimo de la muestra

Cuantil:
  xT = x0 - β·ln[1 - F(x)]    (IV-74)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo

---

## 4. Generalizada Exponencial
Parámetros: α, λ

Momentos:
  α por resolución de IV-77:
    (ψ'(α+1) - ψ'(α)) / (ψ(α+1) - ψ(α)) = x̄/S
  λ por IV-78:
    µ = [ψ(α+1) - ψ(1)] / λ

MV: sistema iterativo IV-79 a IV-82
  LL = n·ln(α) + n·ln(λ) + (α-1)·sum(ln(1-e^(-λ·xi))) - λ·sum(xi)    (IV-79)
  Sistema IV-80 y IV-81 simultáneamente
  α̂(λ) = -n / sum(ln(1 - e^(-λ·xi)))    (IV-82)

ML (Momentos L): IV-83 a IV-88
  α̂ resuelto de: β2/β1 = (ψ(α+1)-ψ(1)) / (ψ'(α)-ψ'(α+1))    (IV-83)
  λ̂ = (ψ(1) + ψ(α̂+1)) / β1                                     (IV-84)
  β1 = M1 (IV-85),  β2 = M2 (IV-86)
  M1 por IV-87,  M2 por IV-88

Cuantil:
  xT = -ln[1 - F(x)^(1/α)] / λ    (IV-89)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo

---

## 5. Normal
Parámetros: µ, σ

Momentos y MV (coinciden):
  µ̂ = x̄                              (IV-92)
  σ̂² = sum(xi - x̄)² / (n-1)         (IV-93)

ML (Momentos L):
  µ̂ = λ1                             (IV-94)
  σ̂ = 1.772·λ2                       (IV-95)
  λ1 = β0                             (IV-96)
  λ2 = 2·β1 - β0                     (IV-97)
  β0 = M(0) (IV-98),  β1 = M(1) (IV-99)
  M(0) = (1/n)·sum(xi)               (IV-100)

Cuantil:
  xT = µ̂ + σ̂·UT                     (IV-101)
  UT por aproximación racional IV-102 a IV-105:
    Para 0 < F(x) ≤ 0.5:
      V = sqrt(ln(1/F(x)²))          (IV-103)
      UT = V - (b0 + b1·V + b2·V²) / (1 + b3·V + b4·V² + b5·V³)    (IV-102)
    Para 0.5 < F(x) ≤ 1: usar 1-F(x) en V y cambiar signo a UT    (IV-105)
    Coeficientes: b0=2.515517, b1=0.802853, b2=0.010328,
                  b3=1.432788, b4=0.189269, b5=0.001308

---

## 6. Log-Normal 2 parámetros
Parámetros: µy, σy
NOTA: Momentos y MV producen los mismos estimadores

Momentos y MV (coinciden):
  µ̂y = (1/n)·sum(ln xi)                     (IV-107)
  σ̂²y = sum((ln xi - µ̂y)²) / (n-1)         (IV-108)

Cuantil:
  xT = exp(µ̂y + UT·σ̂y)                      (IV-109)

RESTRICCIÓN: No Aplicable si algún xi ≤ 0 (confirmado con Facundo)

---

## 7. Log-Normal 3 parámetros
Parámetros: x0, µy, σy

Momentos: sistema IV-111 a IV-116
  nx̂ = x̄/S                                   (IV-112)
  w = (g²/4 + 1)^(1/2) - g/2               (IV-113)
  ẑ = w^(1/3) - w^(-1/3)                    (IV-114)
  µ̂y = ln(Sy/nz) - (1/2)·ln(ẑ²+1)         (IV-115)
  σ̂²y = ln(ẑ²+1)                            (IV-116)
  x̂0 = x̄ - (nx̂/ẑ)                          (IV-111)

MV: sistema iterativo IV-117 a IV-119
  µ̂y = (1/n)·sum(ln(xi - x0))              (IV-117)
  σ̂²y = (1/n)·sum((ln(xi-x0) - µ̂y)²)      (IV-118)
  x0 por resolución iterativa de IV-119

Cuantil:
  xT = x0 + exp(µ̂y + UT·σ̂y)               (IV-120)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo

---

## 8. Gamma 2 parámetros
Parámetros: α, β

Momentos:
  α̂ = (x̄/S)²       (IV-123)
  β̂ = S²/x̄         (IV-124)

MV:
  α̂ = x̄/β̂          (IV-125)
  β̂ = (1 + √(1 + 4C/3)) / (4C)    (IV-126)
  C = ln(x̄) - y      (IV-127)
  y = (1/n)·sum(ln xi)    (IV-128)

ML (Momentos L):
  τ2 = λ2/λ1         (IV-129)
  Para 0 ≤ τ2 < 0.5:
    z = π²·τ2          (IV-131)
    β̂ = (1 - 0.308·z) / (z - 0.05812·z² + 0.01765·z³)    (IV-130)
  Para 0.5 ≤ τ2 < 1:
    z = 1 - τ2         (IV-133)
    β̂ = (0.7213·z - 0.59478·z²) / (1 - 2.1817·z + 1.2113·z²)    (IV-132)
  α̂ = x̄/β̂          (IV-134)

Cuantil: IV-135
  xT = α̂·β̂·(1 - UT/(9β̂) + 1/(9β̂))³... (ver IV-135 para forma exacta)

RESTRICCIÓN: deshabilitada si algún xi = 0 (confirmado con Facundo)

---

## 9. Gamma 3 parámetros
Parámetros: β, α, x0

Momentos:
  β̂ = 4/g²          (IV-137)
  α̂ = S/β̂           (IV-138)
  x̂0 = x̄ - S·β̂     (IV-139)
  g = asimetría no sesgada de la serie

MV: sistema iterativo IV-140 a IV-143
  β̂ por IV-140/IV-141 (iterativo)
  α̂ por IV-141
  x0 por resolución de IV-142
  ψ(β) por aproximación de Thom IV-143:
    ψ(β) ≈ ln(β) - 1/(2β) - 1/(12β²)

MPP (Momentos de Probabilidad Pesada):
  PENDIENTE — confirmar con Facundo qué ecuaciones conectan
  los momentos pesados M0, M1, M2 con los parámetros α, β, x0
  de esta distribución específica. Las ecuaciones generales de MPP
  están en IV-43 a IV-47.

Cuantil: IV-144
  xT = x0 + α̂·β̂·(1 - UT/(9β̂) + 1/(9β̂))³

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo

---

## 10. Generalizada Pareto
Parámetros: µ, σ, ε

Momentos: sistema IV-147 a IV-149
  x̄ = µ + σ/(1+ε)                              (IV-147)
  g = 2·(1-ε)·(1+2ε)^(1/2) / (1+3ε)          (IV-148)
  S² = σ²/((1+ε)²·(1+2ε))                     (IV-149)

MV: sistema iterativo IV-150 a IV-152
  LL = -n·ln(σ) - (1/ε+1)·sum(ln(1-(xi-µ)·ε/σ))    (IV-150)
  Resolver IV-151 y IV-152 simultáneamente
  µ̂ = mínimo de la muestra

MC (Mínimos Cuadrados): sistema IV-153 a IV-155
  ε por resolución de IV-153 (polinomio en z)
  σ̂ por IV-154
  µ̂ por IV-155
  Variables auxiliares x̄, ȳ, z̄ por IV-156 y siguientes

MPP (Momentos de Probabilidad Pesada):
  PENDIENTE — ubicar ecuaciones específicas en tesis
  (sección IV.3.10 continúa más allá de lo disponible)

Cuantil:
  xT = µ + (σ/ε)·(1 - (1-F(x))^ε)    (de IV-145/IV-146 invertida)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo
NOTA: frecuentemente No Converge según resultados de la tesis

---

## 11. Gumbel
Parámetros: µ, α

Momentos:
  µ̂ = x̄ - 0.45·S    (IV-177)
  α̂ = 0.78·S         (IV-178)

MV: sistema iterativo IV-179 a IV-187
  yi = (xi - µ̂) / α̂                              (IV-181)
  P = (1/n)·sum(e^(-yi))                          (IV-179 adaptado)
  R = (1/n)·sum(yi·e^(-yi))                       (IV-180 adaptado)
  Criterios: P/α̂ ≈ 0, R/α̂ - 1 ≈ 0              (IV-182, IV-183)
  δµ = α̂·(1.1·P - 0.26·R·α̂) / n               (IV-184)
  δα = α̂·(0.26·P - 0.61·R·α̂) / n              (IV-185)
  µ̂j+1 = µ̂j + δµj                               (IV-186)
  α̂j+1 = α̂j + δαj                               (IV-187)

ML (Momentos L):
  µ̂ = λ1 - 0.577216·α̂    (IV-188)
  α̂ = λ2 / ln(2)          (IV-189)

ME (Máxima Entropía): sistema iterativo IV-190 a IV-198
  P = (1/n)·sum(yi)           (IV-190)
  R = (1/n)·sum(e^(-yi))     (IV-191)
  yi = (xi - µ̂) / α̂          (IV-192)
  Criterios: 0.577216 - P ≈ 0, 1 - R ≈ 0    (IV-193, IV-194)
  δα = 0.4228 + P + ln(R)    (IV-195)
  δµ = P - 0.577216·δα       (IV-196)
  µ̂j+1 = µ̂j + α̂j·δµj        (IV-197)
  α̂j+1 = α̂j·δαj              (IV-198)

Cuantil:
  xT = µ̂ - α̂·ln{-ln[F(x)]}    (IV-199)

---

## 12. GVE — General de Valores Extremos
Parámetros: α, β, ν

Momentos:
  β̂ por polinomios según rango de g (asimetría):
    Si -11.35 < g < 11.396:
      β̂ = -0.279434 + 0.333535·g - 0.048306·g² + 0.023314·g³ - 0.000376·g⁴ - 0.000263·g⁵    (IV-203)
    Si 11.4 < g < 18.95:
      β̂ = -0.25031 + 0.29219·g - 0.075357·g² + 0.010883·g³ - 0.000904·g⁴ - 0.000043·g⁵    (IV-204)
  A = x̄ + B·E[y],  µ̂ = A - B·E[y]    (IV-205)
  B = sqrt(Var(x)/Var(y))               (IV-206)
  Var(x) = Sx²                          (IV-207)

MV: sistema iterativo IV-220 a IV-233
  Funciones auxiliares a, b, c, f, gs, h como polinomios en β̂:
    a = 0.661437 - 0.562798·β̂ + 0.985803·β̂² - 0.059011·β̂³    (IV-225)
    b = 1.235356 - 0.162161·β̂ - 0.115137·β̂² + 0.009577·β̂³    (IV-226)
    c = 0.4711 - 0.77627·β̂ + 0.295825·β̂² - 0.009645·β̂³       (IV-227)
    f = 0.244435 - 0.10287·β̂ - 0.19583·β̂² - 0.016837·β̂³      (IV-228)
    gs = 0.15373 - 0.411923·β̂ - 0.479209·β̂² - 0.075004·β̂³    (IV-229)
    h = 0.338937 - 1.209555·β̂ - 0.109822·β̂² - 0.019801·β̂³    (IV-230)
  Incrementos δν, δα, δβ por IV-222 a IV-224
  Actualización: ν̂j+1, α̂j+1, β̂j+1 por IV-231, IV-232, IV-233

ML (Momentos L): IV-234 a IV-242
  E = (2·M0 - M1) / (3·M0 - M2)    (IV-234)
  β̂ = 7.859·E + 2.9554·E²          (IV-235)
  A = Γ(1 + β̂)                      (IV-236)
  B = 2^(-β̂) - 1                    (IV-237)
  C = (2·M1 - M0)·β̂                (IV-238)
  D = A^(-1)                         (IV-239)
  α̂ = C/(A·B)                       (IV-240)
  ν̂ = M0 + D·α̂                      (IV-241)
  M0 = (1/n)·sum(xi)                (IV-242)
  M1 por IV-243, M2 por IV-244

Cuantil: IV-245
  xT = ν + α·{1 - [-ln F(x)]^β} / β

NOTA: GVE Momentos frecuentemente No Converge según resultados de la tesis

---

## 13. Log-Pearson III
Trabaja sobre yi = ln(xi). Parámetros: α, β, y0

Momentos Método Directo: IV-247 a IV-254
  µr = (1/n)·sum(xi^r)    (IV-248)
  B = (3·ln(µ1) - ln(µ3)) / (2·ln(µ1) - ln(µ2))    (IV-249)
  C = 1/(B-3)             (IV-250)
  Si 3 < B ≤ 5.3:  A = -0.45157 + 1.99955·C                              (IV-252)
  Si 5.3 < B ≤ 6:  A = -0.23019 + 1.65262·C + 0.20911·C² - 0.04557·C³  (IV-251)
  α̂ = (A+1)^(1/3)    (IV-247)
  β̂ = (ln(µ2) - 2·ln(µ1)) / (ln(µ1·(α-1)) - ln(µ2·(α-2)))    (IV-253)
  ŷ0 = ln(µ1) + β̂·ln(1 - α̂)    (IV-254)

Momentos Método Indirecto: IV-255 a IV-256
  Trabajar sobre serie transformada yi = ln(xi)
  β̂ = 4/gy²    (IV-255)
  α̂ = Sy/β̂    (IV-256)
  gy, Sy = asimetría y desvío estándar de la serie yi = ln(xi)

MV: sistema iterativo IV-257 a IV-259
  β̂ por IV-257 (iterativo sobre y0)
  α̂ por IV-258
  y0 por resolución de IV-259
  NOTA: frecuentemente No Converge — es el comportamiento esperado

Cuantil: IV-260
  xT = exp( y0 + α̂·β̂·(1 - UT/(9β̂) + 1/(9β̂))^3 )

RESTRICCIÓN: No Aplicable si algún xi ≤ 0 (confirmado con Facundo)
NOTA: Método Indirecto produce mejores resultados en la práctica (tesis)

---

## Pendientes — requieren confirmación de Facundo antes de implementar

1. Gamma 3p + MPP: confirmar qué ecuaciones conectan M0, M1, M2
   con los parámetros α, β, x0 de esta distribución específica.

2. Generalizada Pareto + MPP: ubicar ecuaciones específicas en la tesis
   (sección IV.3.10, más allá de lo disponible).

3. Comportamiento ante ceros para estas 5 distribuciones:
   Gamma 3p, Exponencial x0β, Generalizada Pareto,
   Log-Normal 3p, Generalizada Exponencial.

4. ME y MC como métodos generales:
   ME = Máxima Entropía (confirmado para Gumbel, IV-190 a IV-198)
   MC = Mínimos Cuadrados (confirmado para Gen. Pareto, IV-153 a IV-155)
   Confirmar si aplican a otras distribuciones y cuáles.