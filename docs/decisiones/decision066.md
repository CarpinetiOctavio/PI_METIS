# DECISIÓN 066 — El dominio de análisis de METIS es la serie de máximos anuales

**Fecha:** 28 de Agosto de 2026
**Estado:** Decidida (no requiere implementación — es una decisión de
alcance)

### Qué se decide

**El dominio de análisis de METIS es la serie de máximos anuales,
cualquiera sea la resolución de entrada.** METIS acepta el registro en la
resolución en que existe (anual, mensual — DECISIÓN 057 — o diaria —
DECISIÓN 065) y construye la serie de máximos anuales con una regla
explícita, auditable y configurable. **Lo que METIS no hace, y no va a
hacer en V1.0, es correr Etapa 1 o Etapa 2 sobre los valores mensuales o
diarios sin agregar** — el "camino B" del
[informe de viabilidad](../informe-viabilidad-resoluciones-temporales.md).

Esta decisión no depende de que DECISIÓN 065 (aceptar diaria) se
implemente: vale por sí sola. Es la que se defiende ante el tribunal.

### Por qué — resolución de entrada ≠ dominio de análisis

METIS no es un analizador de series temporales genérico: es un motor de
**análisis de frecuencia de eventos extremos hidrológicos**. Su unidad de
análisis es la serie de máximos anuales, y eso no es una limitación de
implementación — es lo que hace que el resultado (el evento de diseño de
T = 100 años) signifique algo. La resolución del archivo que sube el
usuario es otra cosa: es el formato en que el registro existe en la
realidad. Un limnígrafo entrega datos diarios; la serie de máximos anuales
es un **derivado** de ese registro, no un archivo distinto.

Automatizar esa derivación (hoy la hace Facundo a mano en Excel) **mejora**
la propuesta de valor original del proyecto. Correr la batería estadística
sobre los valores sub-anuales crudos la **rompe**.

### Qué se rompe en el camino B — resumen

El detalle completo, prueba por prueba, está en la sección 4 del informe de
viabilidad. En síntesis:

**Etapa 1.**
- **Independencia (Anderson, Wald-Wolfowitz).** En una serie diaria o
  mensual de caudales la autocorrelación no es una hipótesis a testear: es
  una certeza física (recesión del hidrograma + estacionalidad). El test
  no está mal calculado — está mal aplicado: responde con un "sí" de
  antemano y el usuario recibe un warning crítico que no informa nada.
- **Homogeneidad (Helmert, t de Student, Cramer).** Cramer particiona el
  último 60 %/30 % de la serie; sobre datos sub-anuales esas particiones
  cortan a mitad de temporada. Helmert cuenta cambios de signo respecto de
  la media: sobre datos diarios cuenta ciclos estacionales, no cambios de
  régimen. t de Student asume normalidad e independencia de las
  submuestras — ambas violadas de forma masiva.
- **Tendencia (Mann-Kendall, Kolmogorov-Smirnov).** La varianza del
  estadístico S de Mann-Kendall asume observaciones independientes; con
  autocorrelación positiva la varianza queda subestimada y el test rechaza
  "sin tendencia" mucho más de lo que corresponde — el error de tipo I
  real supera al α = 5 % nominal. Corregirlo (varianza modificada,
  *pre-whitening*, Seasonal Mann-Kendall) es **agregar una prueba nueva al
  motor**, con su propia entrada en `formulas-etapa1.md`, su propia fuente
  y su propia regresión. No es un ajuste.
- **Atípicos (Chow / Grubbs-Beck).** La prueba supone una muestra i.i.d.
  y el Bulletin 17B la define específicamente para series de picos
  anuales. Sobre una serie diaria cada crecida es un "atípico" — el test
  marcaría cientos de puntos, y rompe la UX del pipeline (que pausa
  esperando una decisión del usuario **por un atípico**, no por
  trescientos).

**Etapa 2 — se rompe el marco completo, no una fórmula.**
- **El período de retorno cambia de unidad, en silencio.** `empirical.py`
  usa Weibull, `T = (n+1)/m`, en unidades del intervalo de muestreo. Con
  máximos anuales, T = 100 significa 100 años; con una serie diaria, 100
  días. El número seguiría siendo aritméticamente correcto y el rótulo de
  la interfaz seguiría diciendo "años" — un resultado plausible, bien
  formateado y equivocado por un factor de 365.
- **Las 13 distribuciones dejan de ser un modelo de valores extremos.** El
  teorema de Fisher–Tippett–Gnedenko justifica ajustar GVE/Gumbel a
  **máximos de bloque**. Ajustar Gumbel a una serie diaria cruda es
  ajustar una distribución a la curva de duración de caudales completa,
  donde dominan los caudales bajos.
- El marco que sí existe para eventos sub-anuales es otro —**series de
  duración parcial / peaks-over-threshold**, con Poisson-GPD, criterios de
  independencia entre picos, selección de umbral, y una relación para
  convertir el T de la serie parcial al T anual—, y **no es la teoría de
  la tesis de Facundo**. Implementar el camino B *bien* significa
  construir un segundo motor de Etapa 2 con su propio marco teórico, su
  propia bibliografía y su propia auditoría de regresión. No es una
  feature: es la mitad de otro proyecto integrador.

### El riesgo académico es el argumento decisivo

Todo el aparato de trazabilidad de METIS —`formulas-etapa1.md`,
`formulas-etapa2.md`, la regla de que ninguna fórmula se implementa sin
referencia explícita, las 9 estaciones de regresión, `pendientes-facundo.md`—
está construido sobre **una** fuente primaria, que trabaja con series
anuales de máximos.

- El **camino A no toca nada de eso.** Amplía el formato de entrada y deja
  el motor intacto. Se defiende en una frase: *"METIS analiza series de
  máximos anuales; acepta el registro en la resolución en que existe y
  construye la serie de máximos con una regla explícita, auditable y
  configurable."*
- El **camino B rompe la trazabilidad:** cada prueba de Etapa 1
  necesitaría una variante documentada con fuente propia, y Etapa 2
  necesitaría un marco teórico que la tesis no cubre.
- Hay un tercer camino, el peor y el más fácil de tomar por inercia:
  habilitar la entrada sub-anual **sin agregar y sin advertir**. El
  sistema devolvería resultados con la forma correcta y sin sentido —
  exactamente el bug F2.1, ahora como feature declarada. Eso sí sería un
  hallazgo grave en la defensa.

### Extensión segura, si se quiere valor visible del dato sub-anual

**Descriptiva, no inferencial.** El boxplot mensual y una eventual curva de
duración a partir del registro diario no tocan ninguna prueba de
hipótesis, no tocan Etapa 2 y no requieren fórmula nueva de la tesis. Es la
única forma de "mostrar la serie diaria" sin comprometer nada. (El boxplot
mensual desde carga diaria ya existe — DECISIÓN 065, punto 3 — rotulado
explícitamente como máximos mensuales agregados.)

### Advertencia de rigor sobre las referencias

Las referencias bibliográficas que respaldan la sección de "qué se rompe"
—Hamed & Rao (1998) para la varianza modificada de Mann-Kendall; Hirsch,
Slack & Smith (1982) para el Seasonal Mann-Kendall; von Storch (1995) para
el *pre-whitening*; Langbein (1949) y Cunnane (1973) para series de
duración parcial; Coles (2001) para valores extremos— provienen del
conocimiento general del área y **no fueron verificadas contra los
originales**. Antes de que cualquiera de ellas entre a `formulas-etapa1.md`,
a otra decisión numerada o al documento de tesis, hay que chequearlas
contra la fuente, siguiendo la regla del proyecto de no aceptar
afirmaciones sin verificación cruzada. El argumento de esta decisión no
depende de esas citas puntuales — se sostiene sobre las propiedades
estructurales (autocorrelación garantizada, unidad del período de retorno,
Fisher-Tippett sobre máximos de bloque), que sí son verificables desde el
propio código de METIS y desde la tesis.

**Ver también:** [DECISIÓN 065](decision065.md) (el "sí" al camino A para
diaria), [DECISIÓN 057](decision057.md) (camino A para mensual, y el bug
F2.1 que este camino B reabriría),
`docs/informe-viabilidad-resoluciones-temporales.md` §4-§5 (el detalle
prueba por prueba y el análisis de riesgo académico).
