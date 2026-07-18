# DECISIÓN 024 — `exponencial_x0_beta.py`: docstring de cabecera corregido (IV-72), sin efecto en comportamiento
**Fecha:** 14 de Julio de 2026
**Estado:** APLICADA
**Origen:** Auditoría Fase 4 (E2E), est_06 — contraverificación Chat, reconstrucción independiente del modelo seleccionado (Exponencial x0β MV)

### Contexto
Al reconstruir desde cero el modelo ganador de est_06 (Exponencial x0β
MV) sin mirar el código, Chat encontró que la fórmula de MV coincide
exacto — verificado también contra est_04 — con
β̂ = [n/(n-1)]·(x̄-x1), x0=x1-β̂/n. Al confirmar contra el código real
(Code), se vio que la lógica ya era correcta (`beta = (sum(serie) -
n*x1) / (n - 1)`, línea 71) pero el **docstring de cabecera** del
archivo (línea 15) seguía mostrando el denominador viejo,
`(n·(n-1))`, en vez de `(n-1)`.

Esto no era un bug de código — la corrección de IV-72 (denominador
`n(n-1)` → `(n-1)`) ya está registrada en `reimplementacion-etapa2.md`
("Exponencial x0β: IV-72 denominador era n·(n-1), es (n-1)", listada
bajo "Verificar y corregir puntualmente") y ya estaba aplicada en la
lógica del archivo. Solo el comentario de cabecera no se había
actualizado para reflejar esa corrección — mismo patrón de "comentario
desactualizado, lógica correcta" ya visto en `gve.py` y `gumbel.py`
durante Fase 1.

### Decisión
Corregido el docstring de cabecera de `exponencial_x0_beta.py` (línea
15): `β̂ = (sum(xi) - n·x1) / (n·(n-1))` → `β̂ = (sum(xi) - n·x1) / (n-1)`.
**Cambio puramente de comentario — cero cambio de lógica, cero riesgo.**
No amerita coordinación aparte ni verificación extensa; se documenta
igual que cualquier otro cambio de código, por trazabilidad, no por
magnitud del cambio.

### Verificación
- `ruff check metis/core/etapa2/distributions/exponencial_x0_beta.py` →
  All checks passed.
- `pytest tests/ -k exponencial_x0` → 3 passed (sin cambios respecto de
  antes del fix — la lógica no se tocó).
- Fórmula reconfirmada exacta contra el código real en est_04 y est_06
  (ver `regresion-e2e/est_04-e2e.md` y `regresion-e2e/est_06-e2e.md`).

### Archivos modificados
- `metis/core/etapa2/distributions/exponencial_x0_beta.py` — docstring
  de cabecera, línea 15 (comentario únicamente, sin cambio de lógica)
