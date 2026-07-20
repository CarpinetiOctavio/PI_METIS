# DECISIÓN 020 — Log-Normal 3p MV: perfil de verosimilitud sobre x0, no resolución directa de IV-119
**Fecha:** 10 de Julio de 2026
**Estado:** DOCUMENTADO — decisión ya implementada, sin entrada previa en este archivo

### Contexto
Auditoría de Fase 1, Bloque 3, sobre `lognormal3p.py::mv`. El código no
resuelve IV-119 (la ecuación implícita que da la tesis para x0) de forma
directa. En su lugar, perfila la verosimilitud: para cada x0 candidato,
calcula µ̂y y σ̂²y analíticamente por IV-117/118, y busca el x0 óptimo
con `minimize_scalar` sobre esa verosimilitud perfilada.

### Por qué es una decisión válida, no una desviación sin fundamento
Se verificó la derivación: perfilando µy y σy en la log-verosimilitud
completa, la función a minimizar se reduce exactamente a
`n/2·ln(σ²) + Σln(xi-x0)`, que es lo que está codeado. Es matemáticamente
equivalente a resolver IV-119 en el óptimo — ambas son la misma condición
de estacionariedad, expresada de forma distinta. Categoría 2 del framework
de ambigüedad del proyecto: sin ambigüedad de fórmula, pero camino
numérico distinto y más estable que resolver la ecuación implícita directo.

### Alcance / bounds
`(min(xi) - 20·S, min(xi) - 1e-9)`. Nota de precaución (no bug): la
estimación MLE de log-normal de 3 parámetros tiene un problema conocido
en la literatura estadística — la verosimilitud puede ser no acotada
cuando x0 se acerca al mínimo de la muestra. El bound mitiga esto sin
eliminarlo en todos los casos.

### Corrección de alcance en [DECISIÓN 010](decision010.md)
Esta distribución estaba listada en el alcance original de [DECISIÓN 010](decision010.md)
como usuaria de scan+brentq. No lo es — ver enmienda en esa entrada.

### Archivos relevantes
- `metis/core/etapa2/distributions/lognormal3p.py` — método `mv`
