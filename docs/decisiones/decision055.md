# DECISIÓN 055 — `full_pipeline.py` no se usa desde `services/`, y para qué queda
**Fecha:** 09 de Agosto de 2026
**Estado:** Decidida — implementación en curso (Bloque A del [plan de implementación de Etapa 2](../plan-etapa2-implementacion.md))

### Contexto

`core/pipeline/full_pipeline.py::ejecutar_pipeline_completo()` encadena
`ejecutar_etapa1()` y `ejecutar_etapa2()` de punta a punta, código puro sin
streaming — coherente con la restricción de aislamiento de `core/`
(`architecture.md` — "core/ completamente aislado"). Con
[DECISIÓN 052](decision052.md) cableando Etapa 2 al stream SSE,
`analysis_service.py` gana una necesidad real de correr las dos etapas en una
misma sesión de análisis — la pregunta obvia es si debería llamar a
`ejecutar_pipeline_completo()` para eso.

### Por qué `services/` no la usa

`ejecutar_pipeline_completo()` corre las dos etapas de un tirón: no hay ningún
punto donde el llamador pueda observar el progreso intermedio ni pausar. El
stream necesita exactamente lo contrario — emitir cada prueba de Etapa 1 a
medida que se calcula (`test_result`), pausar en Chow si hay atípico, y solo
después de que el usuario resuelve esa pausa (y de que Etapa 1 termina)
empezar Etapa 2, con su propia pausa en la selección de distribución. Ningún
punto de `ejecutar_pipeline_completo()` expone ese nivel de granularidad —
haría falta reescribirla para aceptar callbacks o convertirla en generador, lo
que la convertiría en una segunda implementación del mismo bucle de
re-ejecución por Chow que `analysis_service.py` ya tiene, mantenida en
paralelo.

Es deliberado, no un descuido: `analysis_service.py` sigue llamando
`ejecutar_etapa1()` directo (con su bucle de re-ejecución por Chow, como hoy)
y, si `etapas == [1, 2]` y `nivel_confianza != "rechazado"`, llama
`ejecutar_etapa2()` directo después — las mismas dos funciones que
`full_pipeline.py` encadena, pero orquestadas por `services/` con la
granularidad que el streaming exige, no delegadas a una función de `core/`
que no puede ofrecerla.

### Para qué queda

`full_pipeline.py` **no se borra**: es exactamente lo que necesitan los tests
de regresión matemática del Bloque D — comparar contra las 9 estaciones de la
tesis de Facundo no requiere streaming, requiere las dos etapas encadenadas de
principio a fin sobre una serie de fixture, que es lo que esta función ya
hace sin modificar nada. `tests/regression/test_etapa2_estaciones.py`
consume `ejecutar_pipeline_completo()` directamente.

Se agrega al docstring de `full_pipeline.py` una nota explícita de por qué
`services/` no la llama — sin esa nota, el próximo que la lea (encuentra una
función que hace exactamente lo que el stream necesita, y no está cableada) va
a asumir que es un olvido y va a intentar cablearla, reintroduciendo el
problema de granularidad de arriba.

### Opciones evaluadas

1. **Cablear `services/` a `ejecutar_pipeline_completo()` y agregarle
   soporte de streaming.** Descartada por lo dicho arriba: duplica en `core/`
   la orquestación que `services/` ya resuelve, violando la separación de
   responsabilidades documentada en `architecture.md`
   ("Separación de responsabilidades — flujo de datos": `services/` orquesta,
   `core/` calcula).
2. **Borrar `full_pipeline.py`** ya que `services/` no la usa. Descartada: le
   quita al Bloque D su forma más simple de correr las dos etapas sin
   streaming, obligando a los tests de regresión a reimplementar la misma
   orquestación de dos líneas que esta función ya ofrece.
3. **Mantenerla, sin usarla desde `services/`, documentando explícitamente el
   porqué.** Elegida.

### Criterio de hecho

- `analysis_service.py` llama `ejecutar_etapa1()` y `ejecutar_etapa2()` por
  separado, nunca `ejecutar_pipeline_completo()`.
- `full_pipeline.py` docstring incluye la nota de por qué `services/` no la
  usa, citando esta decisión.
- `tests/regression/test_etapa2_estaciones.py` (Bloque D) consume
  `ejecutar_pipeline_completo()` sin modificarla.
- `grep -rn "ejecutar_pipeline_completo" backend/metis/services` no devuelve
  nada.

**Ver también:** [DECISIÓN 052](decision052.md) — el contrato de streaming que
motiva esta separación. `.claude/rules/architecture/architecture.md`, sección
"Separación de responsabilidades — flujo de datos".
