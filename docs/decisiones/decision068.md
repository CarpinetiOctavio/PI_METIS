# DECISIÓN 068 — Corrección de fórmula IV-153 (Generalizada de Pareto, Mínimos Cuadrados)
**Fecha:** 4 de Septiembre de 2026
**Estado:** APLICADA (backend) — commit en rama `fix/etapa2-gen-pareto-mc-iv153`, pendiente de PR
**Origen:** confirmación de Carlos Catalini sobre la forma correcta de la ecuación (07/08/2026, ver
`docs/auditoria/pendientes/pendientes-facundo.md`), verificada contra rasterización directa de la
tesis (p.74, 600 DPI) en sesión de auditoría del 03-04/09/2026, cruzada de forma independiente
entre Chat y Code.

### Contexto

`gen_pareto.py::ajustar(metodo="mc")` implementaba, hasta esta decisión, la siguiente ecuación
para `_iv153()`:

```python
lhs = (xbar * zybar - xyzbar) * (z2bar - zbar**2)
rhs = (xzbar - xbar * zbar) * (zbar * zybar - z2ybar)
return lhs - rhs
```

Esta ecuación es estructuralmente distinta de IV-153 tal como aparece en la tesis (p.74): no
depende de `z1`/`x1` (primer valor ordenado de `z` y de `x`) y no trae ningún factor `ε²` externo
— ambos presentes en la fórmula real.

### La fórmula real de IV-153

Verificada por transcripción manual independiente (Octavio) y rasterización directa a 600 DPI de
la tesis (Chat), coincidentes término por término. Notación consistente con IV-156 a IV-162 de
`formulas-etapa2.md` — `xz̄` es la media del producto (`xzbar`), no el producto de las medias;
`z̄2` es la media de `z²` (`z2bar`), no el cuadrado de la media:

```
ε² · [ x̄·z1·z̄y − x̄·z̄2y − xz̄·z1·z̄y + xz̄·z̄2y
       − z̄·x1·z̄2y + x1·z̄2y + z̄2·x1·z̄y − z̄·x1·z̄y ]
  − xz̄y · [ z̄2 − z̄ − z1·z̄ + z1 ]
  = 0
```

El segundo corchete, `z̄2 − z̄ − z1·z̄ + z1`, es idéntico al `denom_sigma` ya calculado en el código
para IV-154 (σ̂) — señal de consistencia interna con el resto del sistema de ecuaciones, no una
fórmula aislada.

### Genealogía del bug — por qué la ecuación vieja no era arbitraria

Code demostró algebraicamente (teorema de la envolvente sobre `S(ε) = Σ(xi − a0 − a1·zi(ε))²`,
con `a0`,`a1` concentrados por OLS libre para cada ε) que la ecuación vieja es, término por
término, la condición de optimalidad de una **regresión de mínimos cuadrados sin restricciones de
xi sobre zi(ε)** — un método estadísticamente legítimo, solo que no es el que instancia la tesis
para este caso. Confirmado numéricamente sobre las 9 estaciones reales del dataset de referencia:
el argmin de `S(ε)` sin restricciones coincide con una raíz de la ecuación vieja hasta 9 cifras
significativas (verificado con root-finding de precisión ajustada, `xtol=1e-14` — no una
coincidencia aproximada de un scan grueso).

Esto explica por qué el bug pasó desapercibido tanto tiempo: no era una fórmula rota o
inconsistente, era una fórmula *correcta para un modelo distinto* del que pide la tesis.

### Por qué no se detectó en la auditoría original (relación con DECISIÓN 010)

La ENMIENDA del 20/07/2026 a [DECISIÓN 010](decision010.md) documentó una raíz espuria de la
ecuación vieja cerca de ε≈0 que pasaba los guards existentes (`sigma > 0`, `_DENOM_GUARD`) por
cancelación catastrófica, y decidió no tocar el código hasta confirmar la formulación exacta con
Facundo — de ahí el `skip` de `test_gen_pareto_mc_q100_serie_facundo`. Esa decisión fue correcta
con la información disponible en ese momento: sin la fórmula confirmada, cambiar el criterio de
selección de raíz hubiese sido una suposición no verificada más, apilada sobre otra. Con la
fórmula real ahora confirmada, el diagnóstico de la ENMIENDA sigue siendo válido como historia (la
raíz espuria existía, en esa ecuación), pero deja de aplicar como bloqueo — la ecuación que la
generaba ya no es la que está en el código.

### Validación adoptada — sin número de tesis disponible

Generalizada de Pareto por Mínimos Cuadrados nunca aparece como método testigo en ninguna de las 9
estaciones de la tesis — no existe un ε de referencia contra el cual comparar directamente. Se
evaluaron tres modelos distintos de mínimos cuadrados candidatos a ser el que instancia la tesis
para este caso (ajuste directo de la cuantil IV-174; regresión anclada en `(z1,x1)`; regresión
libre), evaluados en total cuatro veces entre los dos —la anclada en `(z1,x1)` la probaron Chat y
Code de forma independiente, con resultado coincidente en ε≈0.33— y ninguno de los tres reproduce
la raíz de la ecuación confirmada como óptimo (la regresión libre resultó ser, en cambio, la
ecuación *vieja* — ver genealogía arriba). La sección general del método (IV.2.5, tesis p.61,
Ecuaciones IV-25 a IV-33) describe el método en abstracto sin instanciarlo para ninguna
distribución puntual, así que no hay más vía textual disponible para resolver esto.

**Se adopta validación por consistencia interna**, verificada sobre las 9 estaciones reales:

| Estación | n | ε̂ | σ̂ | µ̂ | min(serie) |
|---|---|---|---|---|---|
| est_01 | 40 | 0.94464 | 286.77 | 14.9991 | 15.0 |
| est_02 | 24 | 0.92765 | 233.06 | 41.9995 | 42.0 |
| est_03 | 41 | 0.87254 | 132.12 | 1.9944 | 2.0 |
| est_04 | 36 | 0.93497 | 47.42 | 1.9927 | 2.0 |
| est_05 | 39 | 0.90718 | 97.13 | 0.8858 | 0.9 |
| est_06 | 38 | 0.94615 | 67.00 | 13.9990 | 14.0 |
| est_07 | 19 | 0.97529 | 87.36 | 11.7975 | 11.8 |
| est_08 | 43 | 0.96469 | 248.80 | 39.1997 | 39.2 |
| est_09 | 7 | 1.01885 | 37.69 | 10.9821 | 10.99 |

Nueve de nueve estaciones: raíz única y limpia dentro de `[-0.49, 50]` (sin la ambigüedad de
raíces múltiples de la ecuación vieja), `denom_sigma` siempre lejos del guard (0.29–0.32), σ̂>0 en
todos los casos, y µ̂ cae sistemáticamente apenas por debajo de `min(serie)` — físicamente
coherente con el soporte de la distribución (`x ≥ µ`) y con que IV-155 ancla la iteración de punto
fijo cerca de `x1`.

### Cambio aplicado

`_iv153()` reemplazada por la fórmula transcripta arriba. Guard `abs(eps_val) < _DENOM_GUARD` al
inicio de la función conservado — no por necesidad de la fórmula nueva (no tiene división
explícita por ε), sino por higiene numérica: tanto el corchete de 8 términos como `denom_sigma`
decaen como O(ε²) cerca de ε=0 (cero doble verificado numéricamente), lo que implica riesgo de
cancelación catastrófica al evaluar ahí aunque no cause un cruce de signo falso en el dataset de
referencia.

No se modificó nada de `momentos`, `mv`, `mpp`, `_avgs()` ni el bloque de selección de raíz de
`ajustar(metodo="mc")` — la revisión de ese criterio (relacionado con el cierre formal de
DECISIÓN 010 para este método) se aborda por separado, dado que la ausencia de ambigüedad de
raíces en las 9 estaciones de referencia no garantiza el mismo comportamiento con series de
usuario arbitrarias.

### Escalamiento a Facundo

No se agrega como pregunta al documento de escalamiento formal (Parte A, Sí/No) — no hay forma de
plantear "¿qué modelo de mínimos cuadrados usaste?" como pregunta cerrada, y la fórmula en sí ya
está confirmada por Carlos. Se comunica como nota informativa aparte, no bloqueante, por fuera del
documento numerado.
