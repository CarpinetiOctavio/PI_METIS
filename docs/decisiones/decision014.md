# DECISIÓN 014 — GVE MV: corrección IV-202 + condiciones iniciales ML como fallback
**Fecha:** 20 de Junio de 2026
**Estado:** IMPLEMENTADO — verificado contra est_02 y est_03

### Bug raíz — fórmula IV-202 mal transcripta
La variable reducida del método MV (IV-202) estaba implementada como:
```
arg_log = 1 - (xi - ν) / (α·β)    ← incorrecto
```
La fórmula verificada en pág. 78 de la tesis a 250 DPI es:
```
yi = -(1/β)·ln(1 - β·(xi-ν)/α)   ← correcto
```
El factor es `β·(x-ν)/α`, no `(x-ν)/(α·β)`. La diferencia es un factor β².
Con la fórmula incorrecta, para parámetros donde ν < min(xi) y β < 0 (tipo
Weibull), el término `(xi-nu)/(alpha*beta)` resultaba positivo y > 1 para
xi pequeños, haciendo arg_log negativo e impidiendo que la iteración arranque.

### Bug secundario — condiciones iniciales de momentos inválidas cuando g es grande
Cuando g es grande (est_03: g=3.29), los momentos dan nu0 >> min(xi) = 2, y
arg_log sigue siendo negativo incluso con la fórmula corregida (porque β·(xi-nu)/α
con xi=2 y nu=540 también da > 1 con el signo correcto).

### Solución implementada
1. Corrección de IV-202 en `gve.py`: `arg_log = 1.0 - beta * (serie - nu) / alpha`
2. Condiciones iniciales: intenta primero momentos con el guard corregido. Si
   el guard falla, calcula ML (Momentos-L) como fallback — ML es una solución
   cerrada más cercana al óptimo MV cuando g es alto.

### Verificación
- est_02 GVE MV: alpha=44.261 (0.00%), beta=-0.700 (0.03%), nu=77.660 (0.00%), EEA=37.61 (0.00%) ✓
- est_03 GVE MV: alpha=25.694 (0.00%), beta=-0.417 (0.00%), nu=29.917 (0.00%), EEA=31.67 (0.00%) ✓

### Archivos modificados
- `metis/core/etapa2/distributions/gve.py` — método mv: arg_log corregido + fallback ML
- `.claude/rules/formulas-etapa2.md` — IV-202 actualizado con fórmula correcta
