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
Fuente: Tesis Facundo, Ecuación IV-263 (bloque descriptivo), sección IV.4.5
Nota: La fórmula no aparece desarrollada en IV.1. IV.1 solo menciona
      "siguiendo la ley de Weibull" sin expresión explícita.
      La expresión formal está en IV.4.5 como parte de la definición
      de los Q_T observados para el cálculo del EEA.

---

## EEA — Error Estándar de Ajuste
EEA = sqrt( sum(QT_est - QT_obs)^2 / (n - mp) )
n  = longitud en años del registro analizado (n_j en la tesis)
mp = número de parámetros de la distribución ajustada
Fuente: Tesis Facundo, Ecuación IV-263, sección IV.4.5
Nota: El orden de la diferencia en la fuente es (Q̂_T − Q_T),
      es decir estimado menos observado. No afecta el resultado
      (se eleva al cuadrado) pero se respeta el orden de la fuente.


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
  xT = -ln[1 - F(x)] / β


RESTRICCIÓN: válida para x > 0 (IV-65)
Deshabilitada si algún xi = 0 (confirmado con Facundo)

---

## 3. Exponencial x0 y β
Parámetros: x0, β

Momentos:
  β̂ = S           (IV-70)
  x̂0 = x̄ - S     (IV-71)

MV:
  β̂ = sum(xi - x1) / (n-1)    (IV-72)
  x̂0 = x1 - β̂/n               (IV-73)
  x1 = mínimo de la muestra

Cuantil:
  xT = x0 - β·ln[1 - F(x)]    (IV-74)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo

---

## 4. Generalizada Exponencial
Parámetros: α, λ

Momentos:
  α por resolución de IV-77:
    S/x̄ = √(ψ'(1) - ψ'(α+1)) / (ψ(α+1) - ψ(1))
  Nota: ψ = digamma, ψ' = trigamma. La raíz cuadrada aplica
        solo al numerador.
  λ por IV-78:
    µ = [ψ(α+1) - ψ(1)] / λ

MV: sistema iterativo IV-79 a IV-82
  LL = n·ln(α) + n·ln(λ) + (α-1)·sum(ln(1-e^(-λ·xi))) - λ·sum(xi)    (IV-79)
  Sistema IV-80 y IV-81 simultáneamente
  α̂(λ) = -n / sum(ln(1 - e^(-λ·xi)))    (IV-82)

ML (Momentos L): IV-83 a IV-88
  α̂ resuelto de: β2/β1 = (ψ(2·α+1) - ψ(α+1)) / (ψ(α+1) - ψ(1))    (IV-83)
  Nota: todos los términos usan ψ (digamma), no ψ' (trigamma).
  λ̂ = (ψ(α̂+1) + ψ(1)) / β1                                           (IV-84)
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
      F(x) = 1 - 1/T                 (IV-104)
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
  n̂x = S/x̄                                   (IV-112)
  w = ((g² + 4)^(1/2) - g) / 2               (IV-113)
  n̂z = (1 - w^(2/3)) / w^(1/3)              (IV-114)
  µ̂y = ln(S/n̂z) - (1/2)·ln(n̂z²+1)          (IV-115)
  σ̂²y = [ln(n̂z²+1)]^(1/2)                   (IV-116)
  Nota: IV-116 define σ̂²y (varianza), no σ̂y (desvío).
        En implementación: σ̂y = sqrt(σ̂²y) = [ln(n̂z²+1)]^(1/4)
  x̂0 = x̄·(1 - n̂x/n̂z)                        (IV-111)

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
  α̂ = S²/x̄         (IV-123)
  β̂ = (x̄/S)²       (IV-124)

MV:
  α̂ = x̄/β̂          (IV-125)
  β̂ = (1 + √(1 + 4C/3)) / (4C)    (IV-126)
  C = ln(x̄) - ȳ     (IV-127)
  ȳ = (1/n)·sum(ln xi)    (IV-128)

ML (Momentos L):
  τ2 = λ2/λ1         (IV-129)
  Para 0 ≤ τ2 < 0.5:
    z = π·τ2²          (IV-131)
    β̂ = (1 - 0.308·z) / (z - 0.05812·z² + 0.01765·z³)    (IV-130)
  Para 0.5 ≤ τ2 < 1:
    z = 1 - τ2         (IV-133)
    β̂ = (0.7213·z - 0.59478·z²) / (1 - 2.1817·z + 1.2113·z²)    (IV-132)
  α̂ = x̄/β̂          (IV-134)

Cuantil:
  xT = α̂·β̂·(1 - 1/(9·β̂) + UT·sqrt(1/(9·β̂)))³    (IV-135)

RESTRICCIÓN: deshabilitada si algún xi = 0 (confirmado con Facundo)

---

## 9. Gamma 3 parámetros
Parámetros: β, α, x0

Momentos:
  β̂ = 4/g²              (IV-137)
  α̂ = S/√β̂             (IV-138)
  x̂0 = x̄ - S·√β̂       (IV-139)
  g = asimetría no sesgada de la serie

MV: sistema iterativo IV-140 a IV-143
  β̂ = 1 / (1 - n² / (sum(xi-x0) · sum(1/(xi-x0))))    (IV-140)
  α̂ = (1/n)·sum(xi-x0) - n/sum(1/(xi-x0))             (IV-141)
  x0 por resolución de IV-142:
    F(x0) = sum(ln(xi-x̂0)) - n·ln(α̂) - n·ψ(β̂) = 0
  ψ(β) por aproximación de Thom IV-143:
    ψ(β) ≈ ln(β) - 1/(2β) - 1/(12β²)

MPP (Momentos de Probabilidad Pesada):
  PENDIENTE — Tabla IV-1 de la tesis indica "Sí" para este método,
  pero el capítulo IV no desarrolla las ecuaciones correspondientes.
  Inconsistencia interna de la tesis. Escalar a Facundo antes
  de implementar.

Cuantil:
  xT = x̂0 + α̂·β̂·(1 - 1/(9·β̂) + UT·√(1/(9·β̂)))³    (IV-144)

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo

---

## 10. Generalizada Pareto
Parámetros: µ, σ, ε

Momentos: sistema IV-147 a IV-149
  x̄ = µ + σ/(1+ε)                              (IV-147)
  g = 2·(1-ε)·(1+2ε)^(1/2) / (1+3ε)           (IV-148)
  S² = σ²/((1+2ε)·(1+ε)²)                      (IV-149)

MV: sistema iterativo IV-150 a IV-152
  LL = -n·ln(σ) + ((1-ε)/ε)·sum(ln(1-(ε/σ)·(xi-µ)))    (IV-150)
  Nota: el coeficiente de la sumatoria es (1-ε)/ε, no -(1/ε+1).

  Resolver simultáneamente IV-151 y IV-152:

  IV-151 (∂L/∂ε = 0):
    sum(ln[1-(ε·(xi-µ)/σ)]) / ε²
    + ((1-ε)/ε) · sum((xi-µ)/σ · 1/(1-ε·(xi-µ)/σ)) = 0

  IV-152 (∂L/∂σ = 0):
    n/σ + ((1-ε)/ε) · sum(ε·(xi-µ)/σ² · 1/(1-ε·(xi-µ)/σ)) = 0
  Nota: el primer término es +n/σ, no -n/σ.

  µ̂ = mínimo de la muestra (fijo antes de resolver IV-151/IV-152)

MC (Mínimos Cuadrados): sistema IV-153 a IV-166
  Serie ordenada de menor a mayor.

  Posición de ploteo Cunnane (IV-165):
    fi = (i - 0.4) / (n + 0.2)

  Variables auxiliares (IV-163/IV-164):
    zi = (1 - fi)^ε
    yi = ln(1 - fi)

  Promedios (IV-156 a IV-162):
    x̄   = (1/n)·sum(xi)          (IV-156)
    z̄   = (1/n)·sum(zi)          (IV-157)
    z̄2  = (1/n)·sum(zi²)         (IV-158)
    xz̄  = (1/n)·sum(xi·zi)       (IV-159)
    zȳ  = (1/n)·sum(zi·yi)       (IV-160)
    z2ȳ = (1/n)·sum(zi²·yi)      (IV-161)
    xyz̄ = (1/n)·sum(xi·yi·zi)    (IV-162)

  ε por resolución numérica de IV-153
  σ̂ por IV-154:
    σ̂ = (ε·(x̄-xz̄) + ε·x1·(z̄-1)) / (z̄2-z̄ - z1·(z̄-1))
  µ̂ por IV-155:
    µ̂ = x1 - (ε/µ)·(1-z1)
    Nota: IV-155 es implícita — µ aparece en ambos lados.
          En implementación resolver como ecuación en µ.

  Valor inicial de µ según asimetría (IV-166):
    g > 0 → µ = 0.3
    g < 0 → µ = 0.6

  NOTA: zi depende de ε — el sistema es implícito.
  Resolver iterativamente: dado ε inicial, calcular zi,
  luego los promedios, luego ε nuevo por IV-153.

MPP (Momentos de Probabilidad Pesada): IV-167 a IV-173
  Serie ordenada de menor a mayor. x1 = mínimo de la serie.

  Pi = (i - 0.35) / n                              (IV-173)
  M̂(0) = (1/n)·sum(xi) = x̄                       (IV-172, k=0)
  M̂(1) = (1/n)·sum((1-Pi)·xi)                     (IV-172, k=1)

  I1 = M̂(0) - x1                                  (IV-170)
  I2 = M̂(0) - 2·M̂(1)                             (IV-171)

  ε̂ = (n·I1 + 2·I2·(n-1)) / (I2·(n-1) - I1)     (IV-167)
  σ̂ = (1+ε̂)·(2+ε̂)·I2                            (IV-168)
  µ̂ = x1 - σ̂/(n+ε̂)                               (IV-169)

  Guard: denominador de IV-167 = 0 → STATUS_NO_APLICABLE

Cuantil: IV-174
  xT = ((1/(1-F(x)))^ε - 1)·(σ/ε) + µ   (IV-174)

  Guard: |ε| < _DENOM_GUARD → límite ε→0:
    xT = µ - σ·ln(1-F(x))

RESTRICCIÓN: comportamiento ante ceros PENDIENTE confirmación Facundo
NOTA: MV y MC frecuentemente No Converge según resultados de la tesis

---

## 11. Gumbel
Parámetros: µ, α

Momentos:
  µ̂ = x̄ - 0.45·S    (IV-177)
  α̂ = 0.78·S         (IV-178)

MV: sistema iterativo IV-179 a IV-187
  yi = (xi - µ̂) / α̂                              (IV-181)
  P = n - sum(e^(-yi))                             (IV-179)
  R = n - sum(yi) + sum(yi·e^(-yi))               (IV-180)
  Criterios: P/α̂ ≈ 0, -R/α̂ ≈ 0                 (IV-182, IV-183)
  δµ = α̂j·(1.11·P - 0.26·R) / n                 (IV-184)
  δα = α̂j·(0.26·P - 0.61·R) / n                 (IV-185)
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
Parámetros: α (escala), β (forma), ν (posición)

Momentos: IV-203 a IV-215
  g = asimetría no sesgada de la serie

  β̂ por polinomios según rango de g:
    Si -11.35 < g < 1.1396:
      β̂ = 0.279434 - 0.333535·g + 0.048306·g² - 0.023314·g³ + 0.00376·g⁴ - 0.000263·g⁵    (IV-203)
    Si 1.14 < g < 18.95:
      β̂ = 0.25031 - 0.29219·g + 0.075357·g² - 0.010883·g³ + 0.000904·g⁴ - 0.000043·g⁵    (IV-204)
    Fuera de esos rangos → STATUS_NO_APLICABLE

  Â = x̄ + B̂·E[y]                              (IV-205)
  B̂ = [Var(x)/Var(y)]^(1/2)                    (IV-206)
  Var(x) = Sx²                                  (IV-207)
  E[y] = Γ(1 + β̂)                              (IV-208)
  Var(y) = Γ(1 + 2·β̂) - Γ²(1 + β̂)            (IV-209)

  Según signo de β̂:
    Si β̂ < 0 (tipo II):
      α̂ = -β̂·B̂    (IV-210)
      ν̂ = Â + B̂    (IV-211)
    Si β̂ > 0 (tipo III):
      α̂ = β̂·B̂     (IV-212)
      ν̂ = Â - B̂    (IV-213)
    Si β̂ = 0 (tipo I — Gumbel):
      α̂ = (√6/π)·S = 0.78·S    (IV-214)
      ν̂ = x̄ - 0.45·S           (IV-215)

MV: sistema iterativo IV-216 a IV-233
  Variable reducida: yi = -(1/β̂)·ln(1 - (xi-ν̂)/α̂·β̂)    (IV-202)
  Guard: 1 - (xi-ν̂)/α̂·β̂ > 0 para todo xi → si falla STATUS_NO_CONVERGE

  Auxiliares en cada iteración:
    P = n - sum(e^(-yi))                                    (IV-216)
    Q = sum(e^((β-1)·yi)) - (1-β)·sum(e^(β·yi))           (IV-217)
    R = n - sum(yi) + sum(yi·e^(-yi))                      (IV-218)

  Criterios de convergencia:
    Q/α̂ = 0                                                (IV-219)
    (1/α̂)·(P+Q)/β̂ = 0                                    (IV-220)
    (1/β̂)·[R - (P+Q)/β̂] = 0                              (IV-221)

  Funciones auxiliares polinomios en β̂:
    a = 0.661437 - 0.562798·β̂ + 0.985803·β̂² - 0.059011·β̂³    (IV-225)
    b = 1.235356 - 0.162161·β̂ - 0.115137·β̂² + 0.009577·β̂³    (IV-226)
    c = 0.4711 - 0.77627·β̂ + 0.295825·β̂² - 0.009645·β̂³       (IV-227)
    f = 0.244435 - 0.10287·β̂ - 0.19583·β̂² - 0.016837·β̂³      (IV-228)
    gs = 0.15373 - 0.411923·β̂ - 0.479209·β̂² - 0.075004·β̂³    (IV-229)
    h = 0.338937 - 1.209555·β̂ - 0.109822·β̂² - 0.019801·β̂³    (IV-230)

  Incrementos (IV-222 a IV-224):
    δν = -(α̂/n)·{b·Q + h·(P+Q)/β̂ + (f/β̂)·[R - (P+Q)/β̂]}
    δα = -(α̂/n)·{h·Q + a·(P+Q)/β̂ + (gs/β̂)·[R - (P+Q)/β̂]}
    δβ = -(1/n)·{f·Q + gs·(P+Q)/β̂ + (c/β̂)·[R - (P+Q)/β̂]}

  Actualización:
    ν̂j+1 = ν̂j + δνj    (IV-231)
    α̂j+1 = α̂j + δαj    (IV-232)
    β̂j+1 = β̂j + δβj    (IV-233)

  Convergencia: max(|δν|, |δα|, |δβ|) < CONVERGENCIA = 1×10⁻⁷

ML (Momentos L): IV-234 a IV-244
  CRÍTICO: la serie debe ordenarse DE MAYOR A MENOR antes
  de calcular M̂(1) y M̂(2). Con ese orden, los pesos (n-i)
  son descendentes y (2·M̂(1) - M̂(0)) resulta positivo,
  garantizando α̂ > 0. Fuente: tesis Facundo p.81.

  E = {(2·M̂(1) - M̂(0)) / (3·M̂(2) - M̂(0))} - ln(2)/ln(3)    (IV-234)
  β̂ = 7.859·E + 2.9554·E²                                       (IV-235)
  A = Γ(1 + β̂)                                                   (IV-236)
  B = 1 - 2^(-β̂)                                                 (IV-237)
  C = (2·M̂(1) - M̂(0))·β̂                                        (IV-238)
  D = (A - 1) / β̂                                                (IV-239)
  α̂ = C / (A·B)                                                  (IV-240)
  ν̂ = M̂(0) + D·α̂                                               (IV-241)
  M̂(0) = (1/n)·sum(xi)                                          (IV-242)
  M̂(1) = (1/(n·(n-1)))·sum(xi·(n-i))  i=1..n-1  (serie desc.)  (IV-243)
  M̂(2) = (1/(n·(n-1)·(n-2)))·sum(xi·(n-i)·(n-i-1))  i=1..n-2  (IV-244)

Cuantil: IV-245
  xT = ν + (α/β)·{1 - [-ln(F(x))]^β}

  Guard: |β| < 1e-10 → límite β→0 (Gumbel):
    xT = ν - α·ln(-ln(F(x)))

NOTA: GVE Momentos frecuentemente No Converge según resultados de la tesis.
NOTA: GVE MV también puede No Converge — comportamiento esperado.
NOTA: GVE ML requiere serie ordenada descendentemente para IV-243/244.
      Bug corregido — implementación anterior usaba orden ascendente.
---

## 13. Log-Pearson III
Trabaja sobre yi = ln(xi). Parámetros: α, β, y0

Momentos Método Directo: IV-247 a IV-254
  µr = (1/n)·sum(xi^r)    (IV-248)
  B = (ln(µ3) - 3·ln(µ1)) / (ln(µ2) - 2·ln(µ1))    (IV-249)
  C = 1/(B-3)             (IV-250)
  Si 3.5 < B ≤ 6:  A = -0.23019 + 1.65262·C + 0.20911·C² - 0.04557·C³  (IV-251)
  Si 3 < B ≤ 3.5:  A = -0.45157 + 1.99955·C                              (IV-252)
  α̂ = 1/(A+3)            (IV-247)
  β̂ = (ln(µ2) - 2·ln(µ1)) / (ln(1-α̂)² - ln(1-2·α̂))    (IV-253)
  ŷ0 = ln(µ1) + β̂·ln(1-α̂)    (IV-254)
  NOTA: aplica solo cuando B ∈ (3,6]. Para series con B fuera de ese rango
        el método retorna STATUS_NO_APLICABLE. El método indirecto (IV-255/256)
        no tiene esta restricción y es el preferido en la práctica según la tesis.

Momentos Método Indirecto: IV-255 a IV-256
  Trabajar sobre serie transformada yi = ln(xi)
  β̂ = 4/gy²      (IV-255)
  α̂ = Sy/√β̂     (IV-256)
  gy, Sy = asimetría y desvío estándar de la serie yi = ln(xi)

MV: sistema iterativo IV-257 a IV-259
  β̂ por IV-257 (iterativo sobre y0)
  α̂ por IV-258
  y0 por resolución de IV-259
  NOTA: frecuentemente No Converge — es el comportamiento esperado

Cuantil: IV-260
  xT = exp( Y0 + β·α·(1 - 1/(9·β) + UT·sqrt(1/(9·β)))³ )

RESTRICCIÓN: No Aplicable si algún xi ≤ 0 (confirmado con Facundo)
NOTA: Método Indirecto produce mejores resultados en la práctica (tesis)

---

## Pendientes — requieren confirmación de Facundo antes de implementar

1. Gamma 3p + MPP: confirmar qué ecuaciones conectan M0, M1, M2
   con los parámetros α, β, x0 de esta distribución específica.

2. Gamma 3p + MPP: Tabla IV-1 indica "Sí" para este método pero el
   capítulo IV no desarrolla las ecuaciones. Inconsistencia interna
   de la tesis. Escalar a Facundo antes de implementar.

3. Comportamiento ante ceros para estas 5 distribuciones:
   Gamma 3p, Exponencial x0β, Generalizada Pareto,
   Log-Normal 3p, Generalizada Exponencial.

4. ME y MC como métodos generales:
   ME = Máxima Entropía (confirmado para Gumbel, IV-190 a IV-198)
   MC = Mínimos Cuadrados (confirmado para Gen. Pareto, IV-153 a IV-155)
   Confirmar si aplican a otras distribuciones y cuáles.