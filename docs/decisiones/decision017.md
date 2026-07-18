# DECISIÓN 017 — Wald-Wolfowitz: exclusión de empates con la media
**Fecha:** 9 de Julio de 2026
**Estado:** IMPLEMENTADO — verificado contra los recursos proveidos por Facundo (tesis y Excel)

### Contexto
Se había documentado en pendientes-facundo.md que la
exclusión de valores exactamente iguales a la media (antes de
clasificarlos como éxito/fracaso en el run test) estaba "confirmada"
contra el Excel de Facundo (TP1 Estadística, 2013). Al consultar
puntualmente ese Excel (dataset Despeñaderos, n=40, media=64.902756),
se determinó que ningún valor de esa serie coincide con la media —
el caso de empate nunca se dispara en los datos que Facundo nos
proporcionó. La asignación en su Excel es binaria estricta
(> media → 1, < media → 0), sin manejo visible de igualdad, pero
esto no prueba una convención porque el caso nunca ocurrió ahí.

Se revisó también el único caso de exclusión de dato documentado en
la tesis (est02/La Tapa, n=41→40, valor excluido 35.0 m³/s vs. media
62.39 m³/s) — no corresponde a un empate con la media, es un caso de
causa no determinable ya registrado aparte.

### Conclusión
No existe evidencia, en ningún recurso que Facundo nos
haya dado (ni tesis ni Excel), de que él haya aplicado o necesitado
aplicar esta regla. No es una convención heredada del autor.

### Decisión
Se aplica de todas formas la exclusión de empates con la
media, por fundamento estadístico propio — es el tratamiento estándar
de "ties" en pruebas de corridas (runs test) según literatura
consolidada (Gibbons & Chakraborti, "Nonparametric Statistical
Inference"; también Wald & Wolfowitz, formulación original), donde un
valor exactamente igual a la media no aporta información direccional
y no debe forzarse a ninguna de las dos categorías.

### Implementación
Comparación de igualdad exacta de punto flotante
(arr != media), sin tolerancia ni redondeo. Se evaluó agregar una
tolerancia de redondeo, mismo se descartó: no hay base para elegir
una cantidad de decimales sin introducir arbitrariedad adicional: el
fundamento de la exclusión es conceptual (empate = sin información
direccional), no de precisión de medición, así que no corresponde
ensanchar el criterio más allá de la igualdad exacta.

Esta decisión se clasifica como categoría "criterio matemático propio
ante ausencia de convención confirmable del autor" — distinta de
[DECISIÓN 016](decision016.md) (donde sí existía una convención documentable de
Facundo y se optó por replicarla ante ambigüedad de la tesis) y
distinta de [DECISIÓN 013](decision013.md) (donde la tesis sí fija fórmula explícita y
el Excel de Facundo la contradice).
