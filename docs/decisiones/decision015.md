# DECISIÓN 015 — Log-Normal 3p Momentos: IV-116 σ̂y vs σ̂²y
**Fecha:** 22 de Junio de 2026
**Estado:** IMPLEMENTADO — verificado numéricamente con est_04

### Bug raíz — exponente incorrecto en IV-116
La nota en formulas-etapa2.md decía "IV-116 define σ̂²y (varianza), no σ̂y" y
la implementación calculaba:
```python
sigma_y = (log(nz²+1)) ** 0.25   # sqrt(sqrt(...)) ← incorrecto
```
Rasterización de pág. 70 de la tesis a 250 DPI muestra que el RHS de IV-116
es usado directamente como σ̂y. Verificación numérica con est_04 (n=36):
- nz=0.5568 (con g_tesis=1.849)
- [ln(nz²+1)]^(1/2) = 0.5209 = valor tesis ✓
- [ln(nz²+1)]^(1/4) = 0.7217 ✗ (implementación anterior)

### Corrección
```python
sigma_y = (log(nz²+1)) ** 0.5   # exponente 1/2 ← correcto
```

### Impacto
Antes del fix: sigma_y METIS = 0.733 vs tesis 0.521 → diff 40.8% (no era g-propagación)
Después del fix: sigma_y METIS = 0.537 vs tesis 0.521 → diff 3.1% (puramente g-propagación)

Con g_tesis=1.849: sigma_y = 0.5209 ≈ 0.5210 ✓, mu_y = 3.4278 ≈ 3.4275 ✓

### Nota sobre x0=-1.25 en est_04
La tesis reporta x0=-1.25 para LN3p momentos en est_04. Con g=1.849 la fórmula IV-111
da x0=-11.26. El valor -1.25 es un typo en la tabla (decimal mal ubicado o transcripción).
x0_formula_g_tesis = -11.256, x0_METIS = -10.023 (diff 11%, Causa A g-propagación).

### Archivos modificados
- `metis/core/etapa2/distributions/lognormal3p.py` — línea sigma_y: exponente 1/4 → 1/2
- `.claude/rules/formulas-etapa2.md` — IV-116: nota corregida, exponente 1/2 es σ̂y
