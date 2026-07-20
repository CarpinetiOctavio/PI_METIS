# DECISIÓN 012 — Criterio de aprobación Anderson: comparación entera vs ratio flotante
**Fecha:** 16 de Junio de 2026
**Estado:** IMPLEMENTADO — verificado contra tesis Facundo est_02

### Contexto
Durante los tests de regresión de est_02 (n=24, k_max=8) se detectó que el criterio
`lags_fuera / k_max <= 0.10` rechazaba la prueba de Anderson cuando la tesis la aprueba.

### Comportamiento anterior
```python
aprobada = (lags_fuera / k_max) <= 0.10
```
Con 1 lag fuera de 8: `1/8 = 0.125 > 0.10` → rechazada.
La tesis reporta "Aceptada (1 punto fuera no supera el límite admisible de 1)".

### Corrección
```python
aprobada = lags_fuera <= math.ceil(k_max * 0.10)
```
Con k_max=8: `ceil(8 × 0.10) = ceil(0.8) = 1`. `1 ≤ 1` → aprobada ✓

### Justificación
La tesis compara el conteo absoluto de lags fuera contra un umbral entero,
no contra un ratio flotante. `ceil` garantiza que con k_max=8 el umbral sea 1
(no 0), reproduciendo exactamente el criterio de Facundo.
El ratio flotante era incorrecto para k_max que no son múltiplos de 10.

### Archivos modificados
- `metis/core/independence.py` — `calcular_anderson`: import math agregado, condición corregida
