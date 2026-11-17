# DECISIÓN 013 — Fórmula de asimetría no sesgada: ddof=0 (IV-4/IV-5) en todas las distribuciones
**Fecha:** 17 de Junio de 2026
**Estado:** IMPLEMENTADO — propagado a las 5 distribuciones con _skewness interno

### Contexto
Durante los tests de regresión de est_02 se detectó que `descriptive.py` calcula
g=1.6686 (siguiendo IV-4/IV-5) mientras que gamma3p, gve, logpearson3, lognormal3p
y gen_pareto calculaban g≈1.565 internamente con `_skewness` usando `ddof=1`.

### Raíz del problema
Las funciones `_skewness` locales usaban `np.std(x, ddof=1)` en el denominador.
IV-4 requiere `var_sesgada` con ddof=0:

  g_sesg = mean((xi-xbar)³) / (var_sesgada)^(3/2)   [IV-4, ddof=0]
  g_insesg = n²/((n-1)(n-2)) * g_sesg               [IV-5]

El código anterior usaba `S = std(ddof=1)`, que coincide con SKEW() de Excel y
scipy.stats.skew(bias=False), pero difiere de IV-4/IV-5 por un factor √(n/(n-1))
en el denominador.

### Decisión
METIS sigue IV-4/IV-5 como fuente de verdad bibliográfica.
`descriptive.py` ya implementa correctamente — no se modifica.
Las 5 distribuciones con `_skewness` interno se corrigen a ddof=0.

### Consecuencia en tests de regresión (est_02)
- g METIS = 1.6686 (IV-4/IV-5)
- g tesis Facundo = 1.565 (Excel SKEW(), ddof=1)
- diff = 6.62%
Parámetros afectados por g: Gamma 3p momentos (beta=4/g²), Log-Normal 3p momentos
(w=f(g)), GVE momentos (polinomio en g). Diffs en estos parámetros clasifican como
INFO (no bug) — origen trazable a diferencia de fórmula documentada.
LP3 Indirecto usa gy = asimetría de yi=ln(xi), no de la serie original — también afectada.

### Archivos modificados
- `metis/core/etapa2/distributions/gamma3p.py` — _skewness: ddof=1 → ddof=0 (IV-4/IV-5)
- `metis/core/etapa2/distributions/gve.py` — _skewness: ddof=1 → ddof=0 (IV-4/IV-5)
- `metis/core/etapa2/distributions/logpearson3.py` — _skewness: ddof=1 → ddof=0 (IV-4/IV-5)
- `metis/core/etapa2/distributions/lognormal3p.py` — _skewness: ddof=1 → ddof=0 (IV-4/IV-5)
- `metis/core/etapa2/distributions/gen_pareto.py` — _skewness: ddof=1 → ddof=0 (IV-4/IV-5)
