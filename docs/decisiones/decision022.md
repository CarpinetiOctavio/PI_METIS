# DECISIÓN 022 — Cierre de la 2da auditoría de fidelidad a la tesis (Bloque 3) — pendiente: análisis de cableado
**Fecha:** 10 de Julio de 2026
**Estado:** PENDIENTE DE IMPLEMENTAR — auditoría de fórmulas cerrada, refactor de cableado no iniciado

### Contexto
Al día de la fecha se completó una segunda auditoría de código de punta a
punta ("Auditoría Código II"), continuación de la que ya había cerrado
Bloque 1 y 2 (Etapa 1) en una sesión anterior. Esta ronda cubrió Bloque 3
completo: los métodos genéricos de estimación (IV.2, ecuaciones IV-1 a
IV-55) y las 13 distribuciones de Etapa 2 (Uniforme, Exponencial β,
Exponencial x0β, Generalizada Exponencial, Normal, LogNormal 2p y 3p,
Gamma 2p y 3p, Generalizada Pareto, Gumbel, GVE, Log-Pearson III),
verificadas formula por fórmula contra rasterizado de la tesis a 250 DPI
(y 600 DPI en los casos de mayor densidad tipográfica).

**El objetivo de esa auditoría — fidelidad de la implementación a la
tesis — queda cerrado para Bloque 3.** Se corrigieron dos docstrings
desactualizados (rangos de `gve.py`, coeficiente de `gumbel.py`), se
aplicó el guard simétrico de `logpearson3.py::mv` ([DECISIÓN 019](decision019.md)), y se
formalizaron dos decisiones de método ya implementadas pero sin registro
([DECISIÓN 020](decision020.md), [DECISIÓN 021](decision021.md)). Ningún archivo de distribución tiene, a la
fecha, una fórmula que no coincida con la tesis.

### Lo que queda pendiente — no es fidelidad a la tesis, es estructura de código
Durante el barrido de Bloque 3 se identificó un patrón recurrente de
duplicación que no afecta la corrección numérica (verificado en cada
caso — las copias son matemáticamente equivalentes a la fuente ya
auditada) pero sí la mantenibilidad:

- `_skewness` (g, IV-4/IV-5) reimplementada de forma privada en al menos
  cinco archivos de distribución (`gve.py`, `lognormal3p.py`,
  `logpearson3.py`, `gamma3p.py`, `gen_pareto.py`) en vez de importar la
  ya verificada de `descriptive.py`.
- Los momentos de probabilidad pesada genéricos (M̂0, M̂1, M̂2 — IV-21 a
  IV-24) reimplementados con al menos tres estilos de indexado distintos
  (`gve.py`, `gamma2p.py`, `gumbel.py`), cada uno verificado por separado
  como algebraicamente correcto, pero sin una sola fuente compartida.

Ninguna de estas duplicaciones es, hoy, un bug — cada una fue verificada
numéricamente contra la versión de referencia de `descriptive.py` (ver
auditoría de `gve.py`, 2000 pruebas aleatorias, diferencia máxima 0.0).
El riesgo es a futuro: si `descriptive.py` recibe una corrección para
algún caso borde, las copias privadas no la heredan automáticamente.

### Qué queda por hacer
Un análisis de cableado dedicado — no una repetición de la auditoría de
fórmulas — que cubra al menos:
1. Consolidar `_skewness` en una única función importada desde
   `descriptive.py` en los cinco archivos identificados.
2. Consolidar los distintos estilos de M̂0/M̂1/M̂2 en una única función
   compartida.
3. Cualquier otro caso de lógica genérica de Etapa 1 reimplementada
   localmente en Etapa 2 que no se haya relevado explícitamente durante
   esta auditoría (el barrido de Bloque 3 se enfocó en fidelidad a la
   tesis, no en un inventario exhaustivo de duplicación — no está
   garantizado que estos sean los únicos casos).
4. Los tres puntos de cableado de Fase 1 ya documentados en
   `pendientes-cableado-fase2.md` desde la auditoría anterior (orden de
   `arr` en Cramer, asimetría `t_student`/`Cramer`, partición fija en
   `KS-tendencia`) — siguen sin resolverse y quedan dentro del mismo
   alcance de trabajo.

No se define todavía quién ni cuándo aborda este punto — queda registrado
como pendiente explícito, no como tarea en curso.


## --- ADEMAS... ---

**Ver también:** `docs/auditoria/fases/pendientes-cableado-fase2.md`
centraliza este pendiente junto con el de [DECISIÓN 030](decision030.md)
(riesgo de corrección en calcular_cramer) — punto único de referencia
para la próxima sesión dedicada a core/.
