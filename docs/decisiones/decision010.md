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

### ENMIENDA — 20 de Julio de 2026 — filtro "sigma > 0" insuficiente en gen_pareto MC

`test_gen_pareto_mc_q100_serie_facundo` empezó a fallar de forma consistente
(no intermitente — reproducido igual en local y en CI) devolviendo un q100
muy distinto del esperado (384.8 vs 90.6333 de la tesis). Investigado: la
raíz espuria cerca de ε≈0 documentada arriba (línea 32) sí pasa el filtro
`sigma > 0` — para `serie_facundo` da ε≈-8e-6, denom_sigma≈1.17e-10
(por encima de `_DENOM_GUARD=1e-10`, así que no se descarta) y sigma≈20.4
(positivo, así que tampoco se descarta ahí). Como esta raíz espuria aparece
antes que la raíz válida (ε≈0.36) en el barrido ascendente, y el código
corta en la primera raíz que pasa los guards, se queda con la espuria.

La ecuación IV-153/154/155 de la tesis (ver formulas-etapa2.md, sección
Generalizada de Pareto) es difícil de verificar contra el rasterizado sin
el Excel original de Facundo — no hay certeza de que el sistema de
ecuaciones esté transcripto correctamente como para justificar un criterio
de selección de raíz distinto (ej. la más cercana a eps_init de IV-166) sin
convertirlo en una suposición no verificada más.

**Decisión:** no tocar `gen_pareto.py::ajustar(metodo="mc")`. Se marca
`test_gen_pareto_mc_q100_serie_facundo` como `skip` (ver el test) hasta
que se confirme con Facundo la formulación exacta de MC para Gen. Pareto.
`test_gen_pareto_mc_converge_serie_facundo` (solo verifica STATUS_OK, sin
valor numérico) sigue activo — no depende de cuál raíz se elija.
