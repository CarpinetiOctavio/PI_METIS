# DECISIÓN 070 — Umbral de DIST_HIGH_EEA: se mantiene en 5%, configurabilidad diferida a v2

**Fecha:** 9 de septiembre de 2026
**Estado:** CONFIRMADO — sin cambios de código funcional
**Origen:** K-3.13 (`producto-decisiones.md`), reunión directa entre Facundo y Octavio.

### Contexto

`es_high_eea()` (`backend/metis/core/etapa2/eea.py`) marca `DIST_HIGH_EEA` cuando el
error de ajuste supera el 5% de la media. El umbral fue planteado por Facundo en una
reunión directa con Octavio — no surge del texto de la tesis (2010), que no define
ningún mecanismo de advertencia de este tipo, pero sí de una conversación posterior
con su autor.

El relevamiento de pendientes de Kevin (K-3.13) registraba esto como "decisión propia
de METIS, sin relación con Facundo" — ese registro es incorrecto; queda corregido por
este documento.

**Nota de mantenimiento, no bloqueante:** el docstring de `es_high_eea()` dice "no
proviene de la tesis de Facundo" — literalmente cierto (el texto escrito no lo
menciona) pero incompleto al lado de esta decisión, porque puede leerse como que
Facundo no tuvo ninguna injerencia. Ajustar en el próximo commit que toque ese
archivo, no amerita uno propio.

### La decisión

Se mantiene el umbral en 5% de la media, tal como lo planteó Facundo. Sin acción de
código.

Queda abierta, para una versión futura del sistema (fuera del alcance de la versión
que se presenta en 2026), la posibilidad de que el umbral sea configurable por el
usuario en vez de fijo.

### Relación con otras decisiones

- **K-3.13** (`producto-decisiones.md`) — esta decisión resuelve el punto abierto,
  incluida la disputa de origen que dejaba pendiente.