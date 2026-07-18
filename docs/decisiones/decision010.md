# DECISIÓN 010 — Estrategia de root-finding para métodos iterativos
**Fecha:** 19 de Mayo de 2026
**Estado:** ESTABLECIDA — aplicar en todas las distribuciones

### Contexto
Durante el smoke test de Gen. Pareto MC (Fase 4 de feature/core-etapa2) se detectó
que `fsolve` reportaba `ier=1` ("solución convergida") con residual=0.007 — sin moverse
del valor inicial ε=0.3. El verdadero root de IV-153 estaba en ε≈0.51.

`fsolve` declara convergencia cuando el **paso de Newton es pequeño**, no cuando el
**residual es pequeño**. Para funciones casi planas cerca del punto inicial puede
reportar convergencia falsa con residual alto. No es un bug de scipy — es el criterio
de convergencia por defecto de MINPACK.

### Estrategia adoptada en METIS

**Para ecuaciones unidimensionales: scan + brentq**

Evaluar la función en N puntos del dominio para detectar cambios de signo,
luego aplicar `brentq` en el intervalo con cambio de signo.
Garantiza residual ≤ CONVERGENCIA = 1e-7.

```python
_scan = np.linspace(lo, hi, N)
_vals = np.array([f(e) for e in _scan])
_idx = np.where(np.diff(np.sign(_vals)) != 0)[0]
eps = float(brentq(f, float(_scan[_idx[0]]), float(_scan[_idx[0]+1]), xtol=CONVERGENCIA))
```

Puede haber múltiples raíces (incluso espurias). En ese caso, iterar sobre todos
los brackets hasta encontrar parámetros que pasen todos los guards de validez.
Ejemplo en `gen_pareto.py` método MC: la ecuación IV-153 tiene una raíz espuria
cerca de ε=0 (produce denom_b≈0) y la raíz válida en ε≈0.51. Se itera hasta
encontrar la primera que da sigma > 0.

**Para sistemas multidimensionales (MV): fsolve con verificación explícita de residual**

`fsolve` es necesario para sistemas (N ecuaciones, N incógnitas). Después de
obtener la solución, verificar el residual explícitamente antes de aceptarla.
Si residual > umbral → STATUS_NO_CONVERGE.

```python
sol, info, ier, _ = fsolve(system, x0, full_output=True)
if ier != 1 or np.max(np.abs(info["fvec"])) > RESIDUAL_UMBRAL:
    return MetodoResult(..., status=STATUS_NO_CONVERGE)
```

### Alcance
Revisar todos los usos de `fsolve` en el codebase y agregar verificación de residual
donde corresponda. Distribuciones afectadas: gen_pareto MV, gen_exponencial MV,
logpearson3 MV, lognormal3p MV, gamma3p MV, gve MV.

### ENMIENDA — 10 de Julio de 2026 — alcance corregido para lognormal3p MV y logpearson3 MV
Auditoría de Fase 1, Bloque 3, detectó que el alcance de arriba está
desactualizado para estas dos distribuciones: ninguna de las dos usa
scan+brentq. Ambas resuelven el parámetro de posición (x0 en lognormal3p,
y0 en logpearson3) mediante perfil de verosimilitud con `minimize_scalar`
(Brent acotado), no mediante barrido de signo + raíz. Ver [DECISIÓN 020](decision020.md) y
[DECISIÓN 021](decision021.md) (más abajo) para el detalle de cada una — quedan documentadas
ahí en vez de forzarlas dentro de esta entrada.

El resto del alcance de DECISIÓN 010 permanece sin cambios: gen_pareto MV,
gen_exponencial MV, gamma3p MV y gve MV sí usan la estrategia scan+brentq
tal como está descripta arriba (gamma3p MV y gve MV verificados por
auditoría de código el 10/07/2026, sin hallazgos).
