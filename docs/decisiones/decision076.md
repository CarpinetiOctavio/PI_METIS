# DECISIÓN 076: el período de retorno se rotula según la serie que se ajustó: T sigue en años, el texto dice qué se cargó y qué representa el valor de diseño

**Fecha:** 8 de octubre de 2026
**Estado:** Decidida y aplicada (frontend + informe PDF).
**Decide:** Kevin.
**Origen:** observación del director Carlos Catalini (08/10/2026): los cálculos de los eventos de diseño son
correctos, pero el texto se refiere siempre al resultado "en años", sea cual sea el tipo de serie que se
procesó; si la carga es mensual, el resultado debería leerse en relación con esa serie.

### Contexto

Antes de esta decisión, "años" estaba escrito a mano en cinco lugares de la interfaz (rótulo del valor de diseño,
eje X del gráfico de ajuste y del gráfico de eventos, `aria-label` del gráfico de eventos, campo de períodos de
retorno del ranking) y en cuatro del PDF (tabla de eventos, tabla comparada de la simulación y los dos gráficos de
ajuste). Ninguno de esos textos cambiaba con la resolución de la carga.

La pregunta a responder primero era teórica: **¿T debería estar en meses cuando la carga es mensual?**

### Por qué T está en años para las tres resoluciones

El período de retorno sale de la probabilidad de no excedencia de la distribución ajustada, `T = 1 / (1 − F)`
(Weibull, `core/etapa2/design_events.py`). `F` es la probabilidad de que **una observación de la serie
ajustada** no sea superada, así que `T` se mide en la unidad de muestreo de esa serie: si la serie tiene una
observación por año, `T` está en años; si tuviera una por mes, estaría en meses.

En METIS la serie ajustada es siempre la de **máximos anuales** (DECISIÓN 066). Con carga mensual o diaria, el
paso 0 de `ejecutar_etapa1()` la agrega a un máximo por año según `mes_inicio_anio` (DECISIÓN 057 y 065) antes de
validar el contrato, y desde ahí el pipeline la trata como una serie anual (`resolucion_temporal = "anual"`).
Etapa 2 recibe `serie_efectiva`, que es esa serie agregada. Por lo tanto **T está en años en los tres casos** y los
números que se mostraban eran correctos, como había confirmado el director.

Rotular "T = 100 meses" para una carga mensual sería un error, no una corrección: afirmaría que se ajustó la serie
de los valores mensuales, que es exactamente el camino B que DECISIÓN 066 descartó (romper la independencia de la
muestra, F2.1 de DECISIÓN 057). Además, el período de retorno de una serie mensual no se obtiene multiplicando el
anual por 12: con estacionalidad, los meses no son observaciones idénticamente distribuidas.

### Lo que sí faltaba

La observación del director señala un problema real de comunicación, no de cálculo. Con una carga mensual o
diaria, el usuario veía "Valor de diseño · T = 100 años" sin ningún indicio de que:

1. la distribución no se ajustó a los valores que él subió sino a sus máximos anuales,
2. "año" significa el año definido por el mes de inicio elegido (de julio a junio por defecto), no el calendario,
3. el valor de diseño es un máximo mensual, un pico diario o una media diaria, según la carga.

Es información que METIS ya tiene (`etapa1.datos.resolucion_original`, `configuracion.mes_inicio_anio`,
`configuracion.variable_diaria`) y que se perdía en la presentación.

### Alternativas evaluadas

- **Cambiar la unidad de T según la resolución de carga ("meses", "días").** Descartada por lo explicado arriba:
  es teóricamente incorrecta para el dominio de análisis de METIS.
- **Dejar todo igual y explicarlo solo en el manual de usuario.** Descartada: el problema aparece justamente al
  leer el resultado, y el PDF circula sin el manual.
- **Calcular el rótulo en el backend y mandarlo en el payload.** Descartada: es texto de presentación, no un
  resultado; la interfaz y el PDF ya arman sus propios rótulos (`_RESOLUCIONES`, `_TIPOS_VARIABLE` del PDF,
  `i18n/` del frontend), y sumar un campo obligaría a migrar o rellenar los análisis ya persistidos. Los análisis
  viejos ya tienen los tres datos que hacen falta.
- **Rotular según la serie ajustada en cada capa de presentación: elegida.**

### La decisión

T se sigue expresando en años. Lo que cambia es que el texto deja de estar fijo y se deriva de la serie:

| Carga | Eje / encabezado de T | Valor de diseño | Nota |
|---|---|---|---|
| Anual (o desconocida) | `Período de retorno T (años)` | `Valor de diseño` | "La distribución se ajustó a la serie de máximos anuales, por eso T se mide en años: ..." |
| Mensual | `Período de retorno T (años, de julio a junio)` | `Valor de diseño (valor mensual máximo del año)` | "Se cargó una serie mensual. METIS no ajusta la distribución a esos valores: toma el valor mensual máximo de cada año (de julio a junio) y ajusta la serie de esos máximos anuales. Por eso T se mide en años y no en meses: ..." |
| Diaria, picos | `... (años, de julio a junio)` | `Valor de diseño (pico diario máximo del año)` | Igual, con "picos diarios" y "no en días" |
| Diaria, medias | `... (años, de julio a junio)` | `Valor de diseño (media diaria máxima del año)` | Igual, con "medias diarias" y "no en días" |

Todas las notas terminan igual: "el valor de diseño de T años es el que se espera igualar o superar, en promedio,
una vez cada T años (probabilidad 1/T de ser superado en un año cualquiera)". El rango del año sale de
`mes_inicio_anio` ("de enero a diciembre" con 1). Con carga anual no se muestra el rango: la columna X ya trae los
años y el criterio no se aplicó (ConfigPage ya lo dice al configurar). Si un análisis viejo no tiene
`variable_diaria`, se asume `pico`, el mismo default del backend.

**Dónde vive.**

- Frontend: `src/i18n/periodoRetorno.ts` (`unidadPeriodoRetorno`, `rotuloEjePeriodoRetorno`, `rotuloValorDiseno`,
  `notaPeriodoRetorno`). `Etapa2EventosView` recibe un `contextoSerie` opcional y lo pasa a los dos gráficos;
  `Etapa2RankingView` y `Etapa2Explorador` lo usan para el campo de períodos de retorno. Lo arman `StreamPage`
  (resolución del resultado de Etapa 1 y configuración del formulario), `ResultsPage` (router state, que ahora
  también lleva `variableDiaria`) y `HistoryDetailPage` (análisis persistido).
- PDF: `metis/reportes/pdf.py` (`_unidad_periodo_retorno`, `_rotulo_eje_periodo_retorno`, `_rotulo_valor_diseno`,
  `_nota_periodo_retorno`). La nota va debajo de la tabla de eventos de diseño.
- Las dos implementaciones llevan un comentario que apunta a la otra y tests con el mismo texto esperado
  (`periodoRetorno.test.ts`, `test_pdf.py`), para que no se desalineen.

### Qué no cambia

- Ningún cálculo, ningún endpoint, ningún payload, ninguna migración.
- La unidad de T en `api-contracts.md`: `periodo_retorno` sigue siendo un número de años.
- DECISIÓN 066: esta decisión la aplica a la presentación, no la revisa.

### Verificación

- `pytest tests/unit/reportes` (23 tests, 6 de ellos nuevos) y `npx vitest run` (suite completa, 4 tests nuevos de
  componente y 6 del módulo de rótulos).
- PDF generado para las tres cargas y revisado visualmente.
