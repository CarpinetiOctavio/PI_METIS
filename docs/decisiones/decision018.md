# DECISIÓN 018 — Chow: K_N vía Grubbs-Beck (Bulletin 17B), no cuantil t crudo
**Fecha:** 10 de Julio de 2026
**Estado:** IMPLEMENTADO — PROVISORIO, pendiente de confirmación de Facundo/Carlos

### Contexto
Durante la Auditoría Fase 1, Bloque 2.3, se detectó que `calcular_chow`
comparaba el estadístico de Grubbs (`max(Z_i)`, desvío estandarizado
máximo sobre logaritmos) contra un cuantil t crudo con corrección de
Bonferroni (`t.ppf(1-α/(2n), df=n-1)`), en vez de contra K_N — el valor
crítico real de la tabla del Apéndice 4 de Bulletin 17B, que requiere
una transformación geométrica adicional (test de Grubbs-Beck).

`formulas-etapa1.md` ya reconocía esta discrepancia en su propio texto,
sin resolverla: citaba "Chow (Bulletin 17B)... Apéndice 4, 10%
significancia" pero documentaba una nota de "equivalencia estadística"
entre el cuantil t crudo y K_N que nunca fue verificada. Verificado
ahora que es **falsa**: la diferencia entre ambos valores es de 12% a
61% según n (n=10 a n=50), consistente en una sola dirección (el
cuantil t crudo siempre sobreestima el umbral real, haciendo el test
menos sensible a atípicos reales de lo que debería ser).

### Confusión de fuentes durante la investigación
El repo tenía dos citas no reconciliadas para Chow: `formulas-etapa1.md`
decía "Bulletin 17B"; `statistical-pipeline.md` y `core-implementation.md`
decían "Escalante Sandoval & Reyes Chávez (2005)". Se investigó si
Escalante especifica una fórmula distinta de Grubbs-Beck (confirmado por
Octavio: sí, son formulaciones distintas). Caamaño Nelli & Dasso
("Lluvias de Diseño" — fuente que dio Carlos Catalini) cita a Chow por
nombre pero no desarrolla su fórmula original, y tampoco resuelve cuál
de las dos (Escalante o Grubbs-Beck) es la que corresponde replicar.
Sin la fórmula exacta de Escalante disponible, y necesitando cerrar
este punto sin esperar respuesta de Facundo/Carlos, se optó por
implementar Grubbs-Beck/Bulletin 17B — la fuente pública, verificable y
más rigurosa de las dos, ya citada (aunque de forma incompleta) en
`formulas-etapa1.md` desde antes de esta auditoría.

### Fórmula implementada
```
Z_i = |yi - ȳ| / S_y                    (sin cambios — estadístico de Grubbs)
estadístico = max(Z_i)                   (sin cambios)

K_N = (n-1)/√n · √(t² / (n-2+t²))       (nuevo — antes: K_N = t crudo)
t = t_{n-2, 1-α/(2n)}                    (ν=n-2, no n-1 — antes: ν=n-1)
α = 0.10                                 (nuevo — antes: 0.05, heredado
                                           del ALPHA global de Etapa 1
                                           sin ajustar a la convención de
                                           la tabla de Bulletin 17B)

aprobada = estadístico ≤ K_N
```

### Verificación
Para n=30: K_N calculado = 2.7451 — coincide con el valor citado como
el de la tabla de Bulletin 17B Apéndice 4 para N=30 (referencia externa,
no verificada contra la tabla impresa — ver limitación abajo).
Tests agregados: `test_valor_critico_es_k_n_no_cuantil_t_crudo`,
`test_k_n_n30_aproxima_valor_tabla_referencia` (tests/unit/core/test_outliers.py).
69/69 tests de Etapa 1 pasando, ruff limpio.

### Limitación explícita de esta decisión
No se verificó contra la tabla impresa real del Apéndice 4 de Bulletin
17B, ni contra el paper de Escalante Sandoval & Reyes Chávez (2005), ni
contra "Lluvias de Diseño" de Caamaño Nelli & Dasso directamente — estos
últimos dos solo fueron consultados indirectamente (Octavio reporta que
Caamaño-Dasso cita a Chow sin desarrollar la fórmula). La fórmula de
Grubbs-Beck implementada es material estadístico estándar (Grubbs 1969,
extendido a dos colas; base documentada de la tabla K_N de Bulletin 17B)
verificable en literatura general de detección de atípicos — no es
específica a hidrología ni a la cátedra de Facundo.

**Esta decisión es explícitamente revisable**: si Facundo o Carlos
confirman que METIS debe usar la fórmula de Escalante Sandoval & Reyes
Chávez (2005) en su lugar (o cualquier otra), se reemplaza sin
problema — se elige Grubbs-Beck ahora por ser la opción pública,
citable y más rigurosa disponible, no por ser la confirmada.

### Archivos modificados
- `metis/core/etapa1/outliers.py` — `calcular_chow`: `ALPHA` → `ALPHA_CHOW = 0.10`;
  valor_critico: cuantil t crudo (ν=n-1) → K_N con transformación de
  Grubbs-Beck (ν=n-2)
- `tests/unit/core/test_outliers.py` — 2 tests nuevos (ver arriba)
- `.claude/rules/formulas-etapa1.md` — Sección 9 actualizada con la
  fórmula K_N completa y la limitación explícita de esta decisión
