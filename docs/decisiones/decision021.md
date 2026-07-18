# DECISIÓN 021 — Log Pearson III MV: sustitución de Thom (IV-126) para β dentro del perfil, no resolución directa de IV-257/258/259
**Fecha:** 10 de Julio de 2026
**Estado:** DOCUMENTADO — decisión ya implementada, sin entrada previa en este archivo

### Contexto
Auditoría de Fase 1, Bloque 3, sobre `logpearson3.py::mv`. El código no
resuelve el sistema IV-257/258/259 tal como está en la tesis. En su lugar,
perfila la verosimilitud sobre y0 y, dentro de ese perfil, usa la
aproximación de Thom (IV-126, la misma que usa `gamma3p.py` para β) en
vez de resolver la ecuación de β vía digamma exacta.

### Por qué es una decisión válida
Mismo patrón que [DECISIÓN 020](decision020.md): Categoría 2, sin ambigüedad de fórmula,
método numérico distinto. Reforzado por el hallazgo de est_06 (ver
[DECISIÓN 019](decision019.md) y pendientes-facundo.md): la raíz del sistema literal con
digamma exacta coincide, hasta la tercera cifra decimal, con el resultado
que da la sustitución de Thom — la aproximación no introduce una raíz
espuria ni se aparta de la solución matemáticamente correcta.

### Corrección de alcance en [DECISIÓN 010](decision010.md)
Esta distribución estaba listada en el alcance original de [DECISIÓN 010](decision010.md)
como usuaria de scan+brentq. No lo es — ver enmienda en esa entrada.

### Archivos relevantes
- `metis/core/etapa2/distributions/logpearson3.py` — método `mv`
