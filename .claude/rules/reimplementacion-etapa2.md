"""
CONTEXTO PARA REIMPLEMENTACIÓN — ETAPA 2 METIS
================================================

FUENTE DE VERDAD: formulas-etapa2.md
Toda implementación debe partir del md, no de código existente.
Si hay discrepancia entre el código y el md, el código está mal.
No corregir código viejo — reescribir desde cero contra el md.

ORIGEN DE LOS ERRORES
---------------------
El md fue auditado fórmula por fórmula contra la tesis de Facundo
Ganancias Martínez (Capítulo IV) con verificación visual de cada
ecuación sobre imagen rasterizada. Se encontraron y corrigieron
errores críticos de transcripción en múltiples distribuciones.

La implementación anterior fue construida antes de esa auditoría,
por lo que puede estar basada en versiones incorrectas del md o
en interpretaciones propias. No es una referencia válida.

CASO CONCRETO: Generalizada Pareto IV-174
-----------------------------------------
La implementación anterior usaba:
    xT = µ + (σ/ε)·(1 - (1-F)^ε)         ← INCORRECTO

El md (verificado contra la tesis) define:
    xT = ((1/(1-F(x)))^ε - 1)·(σ/ε) + µ  ← CORRECTO

Estas son matemáticamente distintas. La del md es la inversa
analítica correcta de la CDF definida en IV-146:
    F(x) = 1 - (1 + ε·(x-µ)/σ)^(-1/ε)

No parchear la implementación anterior. Reescribir desde cero
usando IV-174 del md como única referencia.

DISTRIBUCIONES QUE REQUIEREN REESCRITURA COMPLETA
--------------------------------------------------
Las siguientes tuvieron cambios estructurales en la auditoría.
Borrar implementación existente y escribir desde cero contra el md:

1. Generalizada Exponencial
   - Momentos: IV-77 tenía raíz cuadrada faltante y argumentos
     incorrectos en ψ y ψ'
   - Momentos L: IV-83 tenía numerador/denominador invertidos
     y usaba trigamma donde corresponde digamma

2. Gamma 2 parámetros
   - Momentos: IV-123 y IV-124 tenían α y β intercambiados
   - Momentos L: IV-131 tenía π²·τ2 en lugar de π·τ2²

3. Gamma 3 parámetros
   - IV-138: faltaba raíz cuadrada en denominador (S/β̂ → S/√β̂)
   - IV-140/141: no estaban transcriptas en el md anterior,
     ahora están completas

4. Generalizada Pareto
   - MV completo: IV-150/151/152 tenían coeficiente (1-ε)/ε
     reemplazado incorrectamente por -(1/ε+1), y signo de n/σ
     invertido en IV-152
   - Cuantil IV-174: ver caso concreto arriba

5. Log-Pearson III
   - Método Directo completo: IV-247 era (A+1)^(1/3) en lugar
     de 1/(A+3); IV-251/252 tenían umbral 5.3 en lugar de 3.5
     y ecuaciones asignadas al revés; IV-253 tenía denominador
     completamente incorrecto
   - Método Indirecto IV-256: faltaba raíz cuadrada (Sy/β̂ → Sy/√β̂)

DISTRIBUCIONES CON CORRECCIONES PUNTUALES
------------------------------------------
Estas no requieren reescritura completa pero deben verificarse
contra el md antes de continuar:

- Exponencial x0β: IV-72 denominador era n·(n-1), es (n-1)
- Gumbel MV: IV-183 criterio de convergencia era R/α̂-1≈0, es -R/α̂≈0
- GVE MV: IV-228 coeficiente f era 0.24435, es 0.244435
- Log-Normal 3p: IV-116 define σ̂²y, no σ̂y — ver nota en el md

INSTRUCCIÓN GENERAL
-------------------
Para cada método a implementar:
1. Leer la entrada correspondiente en formulas-etapa2.md
2. Implementar exactamente lo que dice el md
3. Si algo en el md parece inconsistente, reportarlo — no resolverlo
   por cuenta propia ni basarse en la implementación anterior
4. Si una entrada dice PENDIENTE, no implementar esa combinación
"""

## Estado por distribución

### Reescribir desde cero
- gen_exponencial.py
- gamma2p.py
- gamma3p.py
- gen_pareto.py
- logpearson3.py

### Verificar y corregir puntualmente
- exponencial_x0_beta.py — IV-72
- gumbel.py — IV-184
- gve.py — rangos g IV-203/204, cuantil β→0
- lognormal3p.py — IV-116

### No tocar — auditadas y correctas
- normal.py
- lognormal2p.py
- uniforme.py
- exponencial_beta.py