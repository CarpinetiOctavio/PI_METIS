# DECISIÓN 019 — LP3 MV: guard simétrico de borde superior
**Fecha:** 10 de Julio de 2026
**Estado:** IMPLEMENTADO — verificado contra 6 estaciones, no resuelve est_06

### Contexto
Auditoría de Fase 1, Bloque 3, sobre `logpearson3.py::mv`, detectó que el
guard de falsa convergencia solo protegía el borde inferior del intervalo
de búsqueda (`yi_min - 20σy`). El borde superior (`yi_min - 1e-9`) no
tenía chequeo equivalente. Hallazgo original documentado en la auditoría
de regresión de est_06: METIS converge donde la tesis reporta NO_CONVERGE,
con el mínimo encontrado a 0.22 del borde superior (1.8% del ancho del
intervalo) — muy por encima de la tolerancia 1e-4 del guard existente.

### Corrección aplicada
```python
upper_bound = yi_min - 1e-9
if abs(result.x - lower_bound) < 1e-4 or abs(upper_bound - result.x) < 1e-4:
    return NO_CONVERGE
```

### Verificación
Aplicado y reproducido contra las 6 estaciones del dataset de regresión —
sin cambios de resultado en ninguna (17 tests preexistentes fallando,
no relacionados — propagación de [DECISIÓN 013](decision013.md), documentados aparte).
El guard es correcto como prevención (protege un caso de borde superior
que hoy no está en el dataset pero podría aparecer en otra serie), pero
no cambia el resultado de est_06 — el mínimo ahí está a 0.22 del borde,
muy por encima de cualquier tolerancia razonable de "convergencia de
borde disfrazada".

### Hallazgo posterior — la discrepancia de est_06 no es de guard
Se verificó el sistema **literal** IV-257/258/259 (con `scipy.special.digamma`
exacta, sin la sustitución de Thom que usa `logpearson3.py::mv` — ver
[DECISIÓN 021](decision021.md)) escaneando 5000 puntos en el dominio válido para la serie
de est_06. El sistema literal tiene raíz única en y0=2.42046, β=3.6939,
α=0.3226 — coincide hasta la tercera cifra decimal con el resultado de
METIS usando Thom. No hay raíz espuria introducida por la sustitución:
la solución que encuentra METIS es la solución matemáticamente correcta
y única del sistema tal como está escrito en el Capítulo IV. La tesis
reporta NO_CONVERGE pese a existir una solución alcanzable — la causa
no es un bug de guard, queda documentada en pendientes-facundo.md como
pregunta directa a Facundo.

### Archivos modificados
- `metis/core/etapa2/distributions/logpearson3.py` — método `mv`: guard
  simétrico agregado (borde superior además de inferior)
- `.claude/rules/regression/pendientes-facundo.md` — sección LP3 MV
  actualizada con el hallazgo de la raíz literal verificada
