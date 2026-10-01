# DECISIÓN 074 — Generalizada de Pareto "pendiente de validación" en V1.0: se calcula y se muestra, pero no se puede elegir y va al final del ranking

**Fecha:** 1 de octubre de 2026
**Estado:** Decidida y aplicada (backend + frontend). Se cierra con un addendum cuando la V2 corrija las fórmulas.
**Decide:** Kevin.
**Origen:** [`hallazgo-gen-pareto-convenciones.md`](../auditoria/hallazgos/hallazgo-gen-pareto-convenciones.md) —
al analizar la serie sintética con negativos del plan de fixes post-verificación (01/10/2026).

### Contexto

La sección IV.3.10 de la tesis tiene tres inconsistencias que `gen_pareto.py` reproduce fielmente: los
estimadores están en la convención de signo de Hosking y la distribución/cuantil (IV-145, IV-146, IV-174) en la de
Coles; IV-167 tiene el signo del numerador cambiado; y Mínimos Cuadrados (IV-153/IV-155) no recupera el
parámetro. Etapa 1 y las otras 12 distribuciones no se ven afectadas, y ningún valor de referencia de la tesis
depende de Pareto (la tesis la marca "No converge" en todas sus tablas).

El problema práctico es est_02: Pareto sale **primera, con la etiqueta "menor EEA"**, y sus eventos de diseño
salen inflados entre un 32 % y un 47 %. Un usuario que confía en el ranking elegiría un resultado que sabemos que
está mal.

### Alternativas evaluadas

- **(a) Corregir las fórmulas ya.** Descartada: es apartarse de la tesis, y la regla del proyecto exige
  referencia bibliográfica explícita y aval del director para cada fórmula (`formulas-etapa2.md`, "Regla de uso").
  Hosking y Wallis (1987) respaldaría los problemas 1 y 2, pero todavía no está en `Bibliografia/` ni verificada;
  el problema 3 necesita la respuesta del autor.
- **(b) Dejarla tal cual y solo documentar.** Descartada: en est_02 lleva "menor EEA" con eventos de diseño
  inflados. Documentar no evita que alguien la elija.
- **(c) Ocultarla.** Descartada por trazabilidad: los métodos que fallan son la mitad de lo que un alumno tiene
  que ver, y esconderla haría desaparecer justo la evidencia de la inconsistencia.
- **(d) Elegida: calcular, mostrar, no permitir elegir, mandar al final y documentar.**

### La decisión

- **`core/` es la fuente de verdad.** `PENDIENTES_VALIDACION: frozenset[str] = frozenset({"gen_pareto"})` en
  `core/etapa2/distributions/__init__.py` (mismo patrón que `DISABLED_WITH_ZEROS`), y
  `DistResult.pendiente_validacion: bool = False`.
- **Orden del ranking.** `pendiente_validacion` entra **primero** en la clave de orden de
  `pipeline_etapa2.py`: `(pendiente_validacion, mejor_eea is None, mejor_eea o inf, n_parametros)`. Pareto queda
  última, después de las sin ajuste; el orden relativo de las otras 12 no cambia.
- **Persistencia.** `_serializar_etapa2()` serializa el campo, así que queda en `analysis_results.etapa2`.
- **No se puede elegir ni explorar.** Código nuevo `DIST_PENDING_VALIDATION` (400), validado en el borde
  (`api/v1/analysis.py::_validar_seleccion_distribucion`, que consulta la constante de `core/`; `api/` ya importaba
  de `core/`) para `POST /analysis/distribution-decision` y `POST /analysis/{id}/design-events`. Se evalúa después
  de la forma del request: un pedido mal formado sigue respondiendo `DIST_SELECTION_INVALID`.
- **Frontend.** `Etapa2RankingView` la atenúa, sin botones para elegir o explorar, con la píldora "pendiente de
  validación" y una línea que explica por qué; la tabla de métodos con sus EEA sigue visible. "menor EEA" pasa a ser
  la primera distribución **no pendiente y con EEA**, no la primera del ranking. Va bajo su propio subtítulo al
  final, después de "Sin ajuste posible con esta serie".
- **Análisis viejos.** Sin backfill (mismo criterio que la DECISIÓN 058 §4): los persistidos antes de esta decisión
  no traen el campo. El frontend usa un respaldo local (`PENDIENTES_VALIDACION_V1`, comentado) para que un análisis
  viejo de una serie como est_02 tampoco muestre "menor EEA". En esos análisis el frontend no reordena: Pareto
  queda donde estaba, solo atenuada.
- **CU-03 (sin implementar).** La selección automática por menor EEA tiene que saltear las distribuciones de
  `PENDIENTES_VALIDACION`. Anotado también en `constraints.md`.

### Consecuencias

- Ningún estadístico, parámetro ni EEA cambia. Verificado contra la línea base de las 9 estaciones (volcado de
  Etapa 1 + Etapa 2 con la herramienta del Apéndice C de `hallazgo-timestamps-desalineados.md`, 36 combinaciones):
  aparece el campo `pendiente_validacion` y Pareto pasa al puesto 13 en est_02 (estaba 1ª), est_03 (10ª) y est_05
  (2ª); nada más cambia. est_09 no entra en esa comparación porque Etapa 1 la rechaza (7 datos).
- La etiqueta "menor EEA" deja de poder caer en una distribución que no se puede elegir.
- El mecanismo queda para futuros casos: cualquier distribución con una inconsistencia conocida en la fuente se
  agrega al conjunto mientras se corrige.

### Condición de cierre

Cuando la V2 corrija las fórmulas siguiendo la guía de §8 del hallazgo: sacar `gen_pareto` de
`PENDIENTES_VALIDACION`, sacar el respaldo del frontend solo si ya no quedan análisis viejos que lo necesiten, y
agregar acá un addendum fechado con qué se corrigió y con qué referencia.

### Relación con otras decisiones

- **DECISIÓN 060** — guard de dominio de Momentos (`µ ≥ min(serie)`) en Pareto; sigue vigente.
- **DECISIÓN 061** — tolerar ceros con advertencia en Pareto; sigue vigente.
- **DECISIÓN 068** — transcripción de IV-153 (Mínimos Cuadrados) corregida contra la tesis. Addendum del
  01/10/2026: la ecuación de la tesis, bien transcrita, no recupera el parámetro.
- **DECISIÓN 058 §4** — criterio de no hacer backfill de análisis ya persistidos.
- **DECISIÓN 062** — "explorar no es decidir": acá tampoco se permite explorar Pareto desde el historial.
