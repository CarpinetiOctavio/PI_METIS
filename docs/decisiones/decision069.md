# DECISIÓN 069 — GenExp/Momentos-L: corrección del desfasaje M̂0/M̂1/M̂2 (IV-83/84) y guard λ ≤ 0

**Fecha:** 9 de Septiembre de 2026
**Estado:** APLICADA (backend) — commits en rama `fix/etapa2-genexp-momentos-l`, pendiente de PR
**Origen:** relevamiento de pendientes del 02-03/09/2026 (`docs/auditoria/pendientes/pendientes-facundo.md`,
sección "Gen. Exponencial — Método Momentos L (IV-83/84)"). Se iba a aplicar un guard trivial
(`λ < 0 → NO_APLICABLE`, borrador de `decisiones-code.md`); al verificarlo contra el código real
apareció un problema más grande. Cross-verificado de forma independiente entre Chat y Code, ambos
rasterizando la p.67 de la tesis (dos fuentes de archivo distintas).

### Contexto

`gen_exponencial.py::ajustar(metodo="ml")` implementaba, hasta esta decisión:

```python
xs = np.sort(serie)[::-1]
beta1 = float(np.mean(xs))                                    # <- media (M̂0), no M̂1
weights = np.arange(n - 1, 0, -1, dtype=float)
beta2 = float(np.dot(xs[:n-1], weights) / (n * (n - 1)))      # <- fórmula IV-87 = M̂1, mal etiquetada
ratio = beta2 / beta1                                         # <- M̂1/M̂0, no M̂2/M̂1
# ... resuelve por brentq: (ψ(2α+1)-ψ(α+1))/(ψ(α+1)-ψ(1)) == ratio   (IV-83, RHS)
lam = (digamma(alpha+1) + digamma(1)) / beta1                 # <- IV-84 sobre M̂0
```

### El bug real — no es de signo, es de índice

IV-83/IV-84 están transcriptas **verbatim** en el código, fieles a la tesis p.67 (confirmado por
rasterización directa, dos fuentes). El `+ψ(1)` de IV-84 **no es un bug** — es la forma impresa, y
con `ψ(1) = −γ ≈ −0.5772` es además la forma correcta. La nota que decía *"se implementa −ψ(1)
(forma correcta)"* (`sprint.md`) era falsa en los dos sentidos.

El bug es un **desfasaje de índice**. La tesis define (IV-85 a IV-88):

```
β1 = M̂(1) = 1/(n(n-1))·Σ_{i=1}^{n-1} x_(i)·(n-i)                (IV-87)   [serie desc.]
β2 = M̂(2) = 1/(n(n-1)(n-2))·Σ_{i=1}^{n-2} x_(i)·(n-i)·(n-i-1)   (IV-88)   [serie desc.]
```

El código usaba la **media** donde IV-83 pide `M̂(1)`, y la fórmula de `M̂(1)` (IV-87) donde pide
`M̂(2)` — y **nunca calculaba `M̂(2)`** (IV-88 no aparece en ningún lado del módulo). Además
resolvía la RHS ψ de IV-83 como ecuación, cuando la tesis usa la LHS (`α = β2/β1`) como estimador
directo.

`gve.py::_momentos_L()` ya implementa `M̂(0)/M̂(1)/M̂(2)` correctamente (IV-243/244, estructura
idéntica a IV-87/88) — es el único lugar del repo con esta terna bien calculada. `normal.py`,
`gamma2p.py` y `gumbel.py` solo necesitan `M̂(0)/M̂(1)` y los calculan bien; el desfasaje es
aislado de `gen_exponencial.py`.

### Verificación — 9 estaciones de la tesis

Anclada en los `M̂(1)/M̂(2)` de la ficha de la tesis, que la capa `regresion-unitaria/` ya marca
`PASS 0%` (METIS los reproduce exacto). `α̂ = M̂(2)/M̂(1)` usado directo:

| est | M̂(1) tesis | M̂(2) tesis | α̂ = M̂(2)/M̂(1) | α tesis | diff | λ̂ (IV-84) | λ tesis |
|---|---|---|---|---|---|---|---|
| est_01 | 104.751 | 83.065 | 0.7930 | 0.79 | +0.38% | −0.00284 | −0.0031 |
| est_02 | 99.741 | 79.402 | 0.7961 | 0.80 | −0.49% | −0.00296 | −0.0033 |
| est_03 | 47.228 | 39.513 | 0.8366 | 0.84 | −0.40% | −0.00562 | −0.0069 |
| est_04 | 17.088 | 13.604 | 0.7961 | 0.80 | −0.49% | −0.01727 | −0.00013 |
| est_05 | 33.925 | 27.853 | 0.8210 | 0.82 | +0.12% | −0.00816 | −0.0097 |
| est_06 | 29.619 | 23.023 | 0.7773 | 0.78 | −0.35% | −0.01044 | −0.0111 |
| est_07 | 34.384 | 26.139 | 0.7602 | 0.76 | +0.03% | −0.00936 | −0.0095 |
| est_08 | 102.898 | 78.539 | 0.7633 | 0.76 | +0.43% | −0.00311 | −0.0032 |
| est_09 | 16.586 | 11.805 | 0.7117 | 0.71 | +0.25% | −0.02167 | −0.0198 |

- **α: `< 0.5%` en las 9** (banda de parámetros del audit es `±1%`). La implementación corregida
  ejecuta fielmente el método de la tesis — el desfasaje de índice era el único problema.
- **λ: signo negativo en las 9**, igual que la tesis. Magnitud diverge 1–18% (est_04 es
  `λ_tesis ≈ 0`, hipersensible al %); sin el Excel de Facundo la divergencia de magnitud no es
  determinable — candidato: redondeo del α o del `M̂(1)` en su cálculo. No afecta la conclusión.

### La decisión

1. **`α̂ = M̂(2)/M̂(1)`** (LHS de IV-83 como estimador directo). La RHS ψ **no** se resuelve:
   evaluada en el α publicado da ≈0.54 contra un `M̂(2)/M̂(1)` de 0.71–0.84; resuelta como
   ecuación da α de 0.14–0.32, sin relación con la tesis. Misma clase de decisión que
   DECISIÓN 068 para IV-153 (se prioriza la práctica numérica reproducible de la fuente sobre el
   texto de la ecuación). Ver nota no cerrada abajo.
2. **`λ̂` por IV-84 verbatim** (`(ψ(α̂+1) + ψ(1)) / M̂(1)`, con `ψ(1) = −γ`), sobre el `M̂(1)`
   correcto — no la media.
3. **Guard `λ̂ ≤ 0 → NO_APLICABLE`**. Con `α̂ = M̂(2)/M̂(1) < 1` para toda muestra no degenerada
   (el peso de `x_(i)` en `M̂(2)` relativo a `M̂(1)` es `(i−2)/(n−2) ≤ 1`), el numerador de
   IV-84 es `ψ(α̂+1) − γ ≤ ψ(2) − γ = −0.1544 < 0` **siempre**. Con `λ < 0`,
   `F(x) = (1 − e^{−λx})^α` no es real para `x > 0` (base negativa elevada a exponente no entero)
   — distribución degenerada, sin cuantil válido. Mismo eje que DECISIÓN 060 (restricción
   matemática forzosa, no inferencia por ausencia de nota en el capítulo IV). **En la práctica el
   método queda `NO_APLICABLE` para toda serie hidrológica real** — la tesis reporta `λ < 0` en
   sus 9 estaciones de referencia.

Se implementa un helper local `_momentos_l()` (idéntico a `gve.py::_momentos_L`) con
`# TODO K-4.1 / DECISIÓN 022` para la consolidación pendiente — no se hace ahora porque
consolidar es el alcance explícito de ese ítem asignado aparte.

### Consecuencias

- **Impacto en el ranking de Etapa 2: cero** en las 9 estaciones + `serie_facundo` (verificado
  estación por estación, read-only). GenExp/Momentos-L era el peor método de su propia
  distribución en 9/9 (EEA 54–395 vs. Momentos/MV 3–36); `mejor_eea` nunca salía de él; el orden
  de distribuciones y el top-3 no cambian.
- **Fan-out de regresión** (precedente DECISIÓN 060): subsección "DECISIÓN 069" en
  `docs/auditoria/regresion/README.md` + fila de GenExp/ML corregida en los 9
  `regresion-e2e-coreEstadistico/est_0X-e2e.md`. Las capas `regresion-unitaria/` y
  `regresion-pipeline/` no se editan una por una — su ficha de tesis (M̂1/M̂2, α, λ) no cambia, y
  su sección de salida en vivo de METIS lleva fecha 2026-07-14, anterior a este fix.
- **Tests**: `test_gen_exponencial_ml_tolera_cero` → `test_gen_exponencial_ml_no_aplicable_con_cero`
  (su premisa "ML tolera ceros" dejó de existir); tests nuevos de `_momentos_l` (valores a mano,
  n<3, equivalencia con `gve._momentos_L`) y de `ajustar(ml) → NO_APLICABLE`.
- **DECISIÓN 061**: GenExp/ML sale del alcance de "tolera ceros con advertencia" — es
  `NO_APLICABLE` con o sin ceros. Addendum de referencia cruzada en `decision061.md`.

### Nota no cerrada — posible errata de transcripción en IV-83

La RHS ψ que imprime IV-83 no reproduce el cociente `M̂(2)/M̂(1)` bajo ninguna interpretación
razonable (ver arriba). Se sospecha una divergencia de transcripción en la propia tesis, no en
METIS. **No bloquea nada** — se usa el cociente directo, validado contra las 9 estaciones.
Escalado de forma no bloqueante en el documento de escalamiento a Facundo/Carlos (Parte C — no
requiere respuesta para avanzar).

### Archivos modificados

- `backend/metis/core/etapa2/distributions/gen_exponencial.py` — helper `_momentos_l()`, rama
  `ml` reescrita, docstring, comentario de `PENDING_ZEROS_CONFIRMATION`
- `backend/tests/unit/core/etapa2/distributions/test_gen_exponencial.py`
- `.claude/rules/core/formulas-etapa2.md` — §4, bloque ML
- `.claude/rules/sprint.md` — corrección de la nota falsa de IV-84 (tachado + nota fechada)
- `docs/auditoria/pendientes/pendientes-facundo.md` — ADDENDUM 09/09/2026
- `docs/auditoria/regresion/README.md` — subsección DECISIÓN 069, "Exclusiones globales"
- `docs/auditoria/regresion/regresion-e2e-coreEstadistico/est_0{1..9}-e2e.md` — fila GenExp/ML

### Relación con otras decisiones

- **DECISIÓN 060** — mismo eje para el guard (restricción matemática forzosa, decisión de diseño
  propio de METIS).
- **DECISIÓN 061** — GenExp/ML deja de ser un caso de tolerancia a ceros.
- **DECISIÓN 068** — mismo criterio de "práctica numérica reproducible de la fuente sobre el texto
  de la ecuación" aplicado a IV-153.
- **K-4.1 / DECISIÓN 022** — consolidación de `_momentos_l` con `gve._momentos_L`, pendiente.
