# Plan de implementación: cambios que surgen de las respuestas de Facundo

**Fecha:** 22 de octubre de 2026
**Autor del plan:** Kevin Massholder (con asistencia)
**Ejecución:** Claude Code, un solo pedido de incorporación desde `staging`, con un commit por bloque
**Base verificada:** `staging` en `0adfdb9` (PR #143, cierre de la revisión manual del 21/10). Antes de empezar, `git fetch` y confirmar contra `origin/staging` las rutas y los números que cita este plan.

---

## 0. Contexto y reglas para quien ejecuta

### Por qué existe este plan

Facundo Ganancias Martínez respondió el documento "Consolidado de pendientes y decisiones de la auditoría del motor estadístico" (versión 3, 9 de septiembre de 2026). La mayoría de las respuestas confirman lo que METIS ya hace o quedan como trabajo futuro. Tres piden cambios en el sistema, y todas hay que dejarlas registradas en la documentación del repositorio.

| Bloque | Respuesta que lo origina | Tamaño |
|---|---|---|
| A. Aviso de longitud mínima recomendable | Mann-Kendall con n = 7 | Muy chico |
| B. Serie diaria de lluvia acumulada | Series diarias: promedio o pico | Chico |
| C. Cobertura mínima de los años interiores, a criterio del usuario | Umbral de completitud de un año interior | Mediano |
| D. Registrar las respuestas en la documentación del repositorio | Todas | Chico (solo documentación) |

### Reglas del repositorio que aplican a todo el plan

- Rama `feature/respuestas-facundo-22-10` desde `staging`, pedido de incorporación a `staging`. Nada directo a `main`.
- **Decisiones:**
  - el bloque C crea la **DECISIÓN 081**;
  - el bloque B es una revisión fechada de la **DECISIÓN 065** (cierra la pregunta R0.2 que esa decisión dejó abierta);
  - antes de numerar, verificar el máximo real en `origin/staging`: al 22/10 la última es la 080, y la 072 y la 035 están reservadas.
- **Código de error nuevo** (bloque C): va al catálogo de `.claude/rules/architecture/api-contracts.md` y a `frontend/src/i18n/errors.es.ts` en el mismo commit, o falla el trabajo `error-catalog`.
- **Bordes nuevos** (bloques B y C): sus casos van a `docs/calidad/casos-de-prueba.md` con el test que los implementa, en `backend/tests/unit/casos_dinamicos/` si no tienen otro lugar natural.
- Umbrales vigentes: 80 % de cobertura del código nuevo, duplicación por debajo del 5 %.
- El pedido toca `frontend/`: recorrer en el navegador los flujos de cada bloque después del último commit y dejar capturas en el pedido.
- Citar la respuesta de Facundo con la fecha en que la envió: **22/10/2026**.

---

## Bloque A. Aviso de longitud mínima recomendable

### Respuesta

Sobre el valor crítico de Mann-Kendall para n = 7: "No lo tengo. De todas maneras, no debiera poder analizarse una serie con tan pocos valores. Debería saltar un cartel de alerta indicando que la longitud mínima recomendable de la serie, para ser representativa, es de 30 valores."

### Situación actual

- Una serie de menos de 10 datos ya se bloquea, así que Mann-Kendall con n = 7 nunca llega a ejecutarse.
- Entre 10 y 29 datos, METIS advierte `CONTRACT_LENGTH_WARNING` con el texto "resultados no certificables". Lo que pide Facundo es cómo se dice, no un comportamiento nuevo.

### Tareas

1. `backend/metis/core/validacion/contract.py`, descripción de `CONTRACT_LENGTH_WARNING`: "Serie con {n} datos. La longitud mínima recomendable para que la serie sea representativa es de 30 valores; con menos, los resultados no son certificables."
2. `frontend/src/i18n/errors.es.ts`: el mismo mensaje para el código.
3. Revisar que la advertencia se vea como banner destacado en Resultados y en el historial. Facundo habla de un "cartel de alerta", así que no debe quedar escondida en una lista.
4. Actualizar los tests que verifican el texto.

### Criterio de aceptación

Una serie de 24 datos muestra el aviso con la redacción nueva, y el análisis sigue.

---

## Bloque B. Serie diaria de lluvia acumulada

### Respuesta

"Depende la serie de datos que estés estudiando. En el caso de registros pluviométricos, los valores corresponden a la lluvia acumulada de un día, desde las 9 de la mañana del día anterior hasta las 9 de la mañana del día que se toma la lectura. Luego el operador debería armar la serie de máximos diarios anuales, por año hidrológico."

### Problema

Con carga diaria, METIS pide declarar si el dato es **pico** o **media** del día (`variable_diaria`). La lluvia diaria no es ninguna de las dos: es un **acumulado**. Si el usuario elige "media", METIS advierte que el máximo anual subestima el pico instantáneo, y eso no aplica a la lluvia. El máximo de los acumulados diarios es exactamente la "serie de máximos diarios anuales" que describe Facundo.

### Tareas

1. `variable_diaria` acepta `"acumulado"` además de `"pico"` y `"media"`:
   - validación en el borde (`api/v1/analysis.py`): sigue el 400 `CONTRACT_VARIABLE_DIARIA_INVALID` para cualquier otro valor;
   - persistencia en `analyses.configuracion` sin cambios de forma.
2. `core/pipeline/pipeline_etapa1.py`, texto de `CONTRACT_DAILY_SERIES_AGGREGATED` para `"acumulado"`: "La serie se agregó a máximos anuales desde valores diarios acumulados (por ejemplo, lluvia de 24 horas): cada valor anual es el máximo acumulado diario del año." Sin advertencia de sesgo.
3. Rótulos de la DECISIÓN 076 (`frontend/src/i18n/periodoRetorno.ts` y `reportes/pdf.py::_contexto_serie`): con `"acumulado"`, el valor de diseño se rotula como máximo diario anual (acumulado de 24 h). Hoy cualquier valor distinto de `"media"` cae en `"pico"`: hacer explícitos los tres casos.
4. `ConfigPage`: la tercera opción, "Acumulado del día (por ejemplo, lluvia de 9 a 9)", con una línea de ayuda que diga cuándo usar cada una.
5. Historial y PDF: mostrar la opción declarada como ya se hace con las otras dos.
6. Tests:
   - borde: los tres valores válidos y uno inválido;
   - texto de la advertencia;
   - rótulos;
   - opción en `ConfigPage`.
7. Revisión fechada de la DECISIÓN 065: R0.2 cerrada con la respuesta de Facundo. Actualizar `api-contracts.md` (`variable_diaria`).

### Criterio de aceptación

La serie diaria de 40 años cargada como "acumulado" corre igual que con "pico": mismos números, advertencia sin sesgo y rótulos de máximo diario anual.

---

## Bloque C. Cobertura mínima de los años interiores, a criterio del usuario (DECISIÓN 081)

### Respuesta

Sobre si descartar siempre un año interior incompleto: "En principio, lo dejaría a criterio del operador, porque en general las series de datos pueden tener muchos faltantes y no existe otra fuente de información. También existen métodos de relleno de series, y el operador podría usarlas por fuera del programa y cargar luego la serie completa."

### Situación actual

- `core/validacion/aggregation.py` tiene `COBERTURA_MINIMA_INTERIOR = {"mensual": 1.0, "diaria": 1.0}`, provisorio a la espera de esta respuesta (R0.1 de la DECISIÓN 065).
- La función ya acepta valores menores, y la advertencia `CONTRACT_INCOMPLETE_YEARS_ACCEPTED` ya existe, con su test, aunque hoy nunca se emite.
- Los años de los extremos siempre exigen 100 %. Eso no cambia.

### Decisión de diseño

- **Parámetro nuevo:** `cobertura_minima_interior`, un porcentaje entero entre 50 y 100, con 100 por defecto. El comportamiento por defecto es el actual, y un análisis que no lo indique da exactamente lo mismo que hoy.
- **Piso del 50 %:** por debajo, el máximo de ese año representa menos de la mitad del período y deja de ser un máximo anual con sentido. Facundo dejó el criterio al operador, pero el piso evita un valor sin sentido físico. Se declara en la decisión.
- **Alcance:** solo tiene efecto con carga mensual o diaria. Con carga anual se acepta y se ignora, como `mes_inicio_anio`.
- **Interfaz:** se informa siempre junto con su consecuencia. Un año aceptado incompleto emite `CONTRACT_INCOMPLETE_YEARS_ACCEPTED` con cuántos meses o días le faltaron, porque su máximo puede estar sesgado hacia abajo.
- **Ayuda:** junto al campo, una línea que remite a la recomendación de Facundo de completar la serie con métodos de relleno por fuera de METIS y cargarla completa.

### Tareas del servidor

1. `POST /analysis/stream`: `cobertura_minima_interior: int = Form(100)`, validado en el borde. Fuera de 50 a 100, o no entero, responde 400 con el código nuevo `CONTRACT_COBERTURA_INVALID` (catálogo y `errors.es.ts` en el mismo commit).
2. Pasarlo de `services/analysis_service.py` a `ejecutar_etapa1()` y de ahí a `agregar_a_maximos_anuales()` como fracción (`/ 100`), en lugar de leer la constante. La constante queda como valor por defecto.
3. `_calcular_serie_calendario()` (la vista comparativa) usa el mismo umbral, para no comparar dos series armadas con criterios distintos.
4. La segunda pasada tras rechazar atípicos no vuelve a agregar, así que no lo necesita. Verificar que los avisos del paso 0 se sigan arrastrando, incluido el nuevo.
5. Persistir en `analyses.configuracion.cobertura_minima_interior`. Al leer análisis anteriores que no lo tienen, el historial y el PDF lo informan como 100 % implícito, igual que `alfa`.
6. PDF: una fila en la configuración del análisis.
7. Tests:
   - borde: 49, 50, 100, 101 y no numérico;
   - una serie mensual con un año interior de 11 meses: se descarta con 100 % y se acepta con 90 %, con `CONTRACT_INCOMPLETE_YEARS_ACCEPTED`;
   - lo mismo con carga diaria;
   - con carga anual el parámetro no cambia nada;
   - lectura de un análisis viejo sin el campo.

### Tareas de la interfaz

1. `ConfigPage`: el campo "Cobertura mínima de los años interiores (%)", junto al mes de inicio del año y con la misma condición de visibilidad. Validación inline de 50 a 100.
2. Resultados, historial y PDF muestran el valor usado cuando la carga fue mensual o diaria.
3. Tests del campo y de su validación.

### Documentación

- `docs/decisiones/decision081.md`: la respuesta de Facundo, el piso del 50 % y su motivo, el valor por defecto y la convivencia con la regla asimétrica de los extremos.
- Revisión fechada de la DECISIÓN 065: R0.1 cerrada, remite a la 081.
- `api-contracts.md`, `constraints.md` (sección "Regla asimétrica de cobertura") y `statistical-pipeline.md` (paso 0): el parámetro reemplaza a la constante provisoria.

### Criterio de aceptación

Con una serie mensual a la que le falta un mes en un año interior:
- con 100 % ese año se descarta;
- con 90 % se conserva con la advertencia que dice cuántos meses faltaron;
- con 49 % el servidor responde 400.

---

## Bloque D. Registrar las respuestas en la documentación del repositorio

Ninguna de estas respuestas cambia el código, pero varias cierran pendientes que hoy figuran como abiertos en `docs/` y en `.claude/rules/`, y esos archivos se cargan en cada sesión.

### Tareas

1. `docs/auditoria/pendientes/pendientes-facundo.md`: marcar cada pregunta respondida con la respuesta textual y la fecha, y mover a "cerradas" las que correspondan:
   - **Cramer, redondeo de la partición:** "Es indistinto, seguir con el redondeo hacia abajo".

     **Decidido por Kevin el 22/10/2026: se mantiene la convención actual** (60 % hacia arriba, 30 % al entero más cercano), que reproduce los valores publicados de las estaciones 2 y 4. Pasar todo a redondeo hacia abajo no cambia ningún veredicto en las nueve estaciones (verificado el 22/10), pero deja de reproducir esos valores, y el autor considera indistinta la elección. **No se toca el código.** Registrar la respuesta, esta verificación y la decisión como revisión fechada de la DECISIÓN 011.
   - **Una o dos colas en Cramer y t de Student:** dos colas; las dos estaciones con valor de una cola fueron un error de transcripción de la tesis. Cerrada, sin cambios.
   - **Mann-Kendall con n = 7:** no tiene la tabla, y una serie tan corta no debería analizarse (bloque A). Cerrada: en METIS ese caso no se alcanza, porque menos de 10 datos bloquea.
   - **Causa C:** no usaba funciones nativas de Excel, atribuye la divergencia a un error de transcripción o a un valor de la ecuación mal escrito, y no conserva las planillas. Queda como explicación reconstruida por la comparación del 08/10 (U_T con F en lugar de 1 − F), no confirmable contra la planilla original. Actualizar `hallazgo-ut-planilla-causa-c.md`.
   - **Log-Pearson III, método directo:** pudo haber usado material que hoy no tiene. Cerrada, se mantiene "no aplicable".
   - **Gamma 3p con el origen por encima del mínimo:** de acuerdo con bloquear todo el cálculo. Cerrada, sin cambios.
   - **Log-Normal 2p no aplicable:** probablemente por valores negativos. Cerrada, coherente con la DECISIÓN 073.
   - **Log-Pearson III por Máxima Verosimilitud:** buscaba la convergencia con el Solver o a mano, y es esperable que METIS converja donde él no lo logró. Cerrada (explica la Causa B).
   - **Mínimos Cuadrados "Estándar" y "Corregidos" y Máxima Entropía o Mínimos Cuadrados en otras distribuciones:** probablemente existan; él no los usó. Pasan a trabajo futuro.
   - **Gamma 3p por MPP:** no contaba con las ecuaciones ni con las tablas, y "si lo consiguen, estaría bueno que esté incluido". Trabajo futuro.
   - **Momentos y MV en Normal y Log-Normal 2p:** no eliminar ningún método aunque converjan al mismo valor; que el usuario elija. Cerrada, sin cambios.
   - **Cobertura de años interiores:** bloque C.
   - **Diaria, promedio o pico:** bloque B.
   - **Diaria a anual directo:** confirmado. Cerrada (DECISIÓN 065).
   - **Agregación para "otro":** podrían analizarse medias o mínimos, aunque lo habitual son extremos. Trabajo futuro.
   - **Mes de inicio en las 9 estaciones:** julio a junio en Córdoba (sur argentino, abril a marzo; regiones muy húmedas, cercano al calendario). Cerrada: confirma el valor por defecto de la DECISIÓN 057.
   - **Caudal y precipitación:** no hay diferencia de tratamiento (también viento, evaporación, alturas de río). Cerrada, sin cambios.
   - **Pareto por Mínimos Cuadrados y Gen. Exponencial por Momentos-L (Parte C):** no tiene el material, "sigan adelante con la decisión tomada". Cerradas (DECISIONES 068 y 069).
2. `docs/pendientes-tecnicos.md`: sumar como trabajo futuro (versión 2):
   - MPP en Gamma 3p;
   - variantes de Mínimos Cuadrados;
   - Máxima Entropía y Mínimos Cuadrados en otras distribuciones;
   - agregación por mínimo o media para la variable "otro".
3. `.claude/rules/core/core-etapa2-implementation.md` y `formulas-etapa2.md`: donde dicen "pendiente de confirmar con Facundo", reemplazar por la respuesta y su destino (cerrado o versión 2).
4. Quedan **abiertas**, para presentarlas en persona la semana próxima:
   - U_T;
   - convenciones de signo de la Generalizada de Pareto;
   - partición de t de Student con n impar;
   - una o dos colas en Mann-Kendall.

   Dejarlas marcadas como "a presentar en reunión" en `pendientes-facundo.md`.

---

## Verificación final del conjunto

1. `scripts/test.sh all` en verde y todos los trabajos de la integración continua en verde.
2. Recorrido en el navegador:
   - serie de 24 datos (aviso nuevo);
   - serie diaria de 40 años como "acumulado";
   - serie mensual con un año interior incompleto, con 100 % y con 90 %;
   - historial y PDF de los tres casos.
3. Actualizar `docs/sprint.md` con el conteo de pruebas.

---

## Impacto en el libro (para el prototipo 7, lo resuelve Kevin con asistencia)

- **Tabla de códigos de error (Anexo B):** sumar `CONTRACT_COBERTURA_INVALID` y actualizar el total.
- **Contrato de datos y agregación temporal (§6.1):** el umbral configurable y la opción "acumulado".
- **Anexo A:** DECISIÓN 081 y la revisión de la 065.
- **Requerimientos:** los que cubren la agregación temporal.
- **Conteo de pruebas y estimación económica:** sumar este pedido.
