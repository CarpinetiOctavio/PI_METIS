# DECISIÓN 081: la cobertura mínima de los años interiores la elige el usuario, entre 50 % y 100 %

**Fecha:** 22 de octubre de 2026
**Estado:** Decidida y aplicada (backend + frontend + PDF) — bloque C de `docs/plan-respuestas-facundo-22-10-2026.md`.
**Decide:** Kevin, a partir de la respuesta de Facundo Ganancias Martínez del 22/10/2026.
**Depende de:** DECISIÓN 057 (agregación mensual a máximos anuales) y DECISIÓN 065 (resolución diaria y regla
asimétrica de cobertura, R2.3). Cierra la pregunta R0.1 que la 065 dejó abierta.

### Problema

Al agregar una carga mensual o diaria a máximos anuales, un año **interior** del registro al que le faltan meses o
días se descarta (`CONTRACT_INCOMPLETE_YEARS_DISCARDED`). La DECISIÓN 065 dejó el umbral cableado como
`cobertura_minima_interior`, con un valor provisorio de 1,0 (estricto: el año tiene que estar completo) mientras se
esperaba la respuesta de Facundo (R0.1). El código ya aceptaba valores menores y el aviso
`CONTRACT_INCOMPLETE_YEARS_ACCEPTED` existía, pero nunca se emitía.

La respuesta del 22/10/2026:

> "En principio, lo dejaría a criterio del operador, porque en general las series de datos pueden tener muchos
> faltantes y no existe otra fuente de información. También existen métodos de relleno de series, y el operador
> podría usarlas por fuera del programa y cargar luego la serie completa."

### La decisión

`cobertura_minima_interior` pasa a ser un **parámetro del análisis**, como `mes_inicio_anio`.

- **Forma:** porcentaje entero entre **50 y 100**, en `POST /analysis/stream` (`Form`, llega como texto). Fuera de
  ese rango o no entero → 400 `CONTRACT_COBERTURA_INVALID`, en el borde, antes de tocar el archivo. `core/` recibe
  la fracción (`/ 100`) y vuelve a validarla (`validar_cobertura_minima_interior()`), como hace con α.
- **Valor por defecto: 100.** Es el comportamiento anterior: un análisis que no lo indica da exactamente lo mismo que
  antes de esta decisión. La constante `COBERTURA_MINIMA_INTERIOR` de `core/validacion/aggregation.py` queda como
  valor por defecto cuando no llega el parámetro.
- **Piso del 50 %.** Facundo dejó el criterio al operador, pero un año con menos de la mitad del período registrado
  no tiene un "máximo anual" con sentido físico: su máximo representa a una fracción menor del año. El piso evita ese
  valor sin restringir los casos razonables.
- **Alcance:** solo tiene efecto con carga mensual o diaria. Con carga anual se acepta y se ignora, igual que
  `mes_inicio_anio`.
- **Convive con la regla asimétrica.** Los años de los **extremos** del registro siguen exigiendo 100 % siempre: ahí
  la parcialidad es la regla (el registro casi nunca empieza o termina en el mes de inicio del año) y se recortan con
  `CONTRACT_PARTIAL_YEARS_TRIMMED`. El parámetro gobierna solo los años interiores.
- **La consecuencia se informa siempre.** Un año interior aceptado incompleto emite
  `CONTRACT_INCOMPLETE_YEARS_ACCEPTED` con cuántos meses o días le faltaron, porque su máximo puede estar sesgado a la
  baja. La segunda pasada de la Etapa 1 tras rechazar atípicos no vuelve a agregar, y el aviso se arrastra de la
  primera como los demás del paso 0.
- **La vista comparativa calendario** (`serie_calendario`, DECISIÓN 058) se agrega con el mismo umbral, para no
  comparar dos series armadas con criterios distintos.
- **Interfaz:** campo "Cobertura mínima de los años interiores (%)" en `ConfigPage`, junto al mes de inicio del año y
  con la misma condición (deshabilitado si la columna X ya son años), con validación en línea. La ayuda remite a la
  recomendación de Facundo: completar la serie con un método de relleno por fuera de METIS y cargarla completa.

### Persistencia y lectura

- Se guarda en `analyses.configuracion.cobertura_minima_interior` (sin migración, JSONB) y viaja en
  `result_etapa1.datos.cobertura_minima_interior` (`null` con carga anual).
- Un análisis anterior a esta decisión no la tiene: `GET /history/{id}` devuelve `100` con
  `cobertura_minima_interior_implicita: true`, sin backfill (mismo criterio que `alfa_implicito`, DECISIÓN 078).
- Resultados, historial y PDF muestran el valor usado cuando la carga fue mensual o diaria; para un análisis anterior,
  "100 % (el único criterio disponible cuando se corrió el análisis)".

### Alternativas descartadas

- **Dejar el 100 % fijo.** Contradice la respuesta de Facundo y descarta años con un solo dato faltante en registros
  donde no hay otra fuente.
- **Sin piso (0 a 100).** Permitiría "máximos anuales" construidos con un solo mes del año.
- **Aplicar el umbral también a los extremos.** Reabre lo que la DECISIÓN 057 resolvió: en los extremos la
  parcialidad es la norma y su máximo está sesgado por construcción.

### Verificación

`backend/tests/unit/casos_dinamicos/test_cobertura_minima_interior.py` (casos VL-11, CE-08 y TD-06 de
`docs/calidad/casos-de-prueba.md`): bordes 49/50/100/101 y valores no enteros; serie mensual con un año interior de
11 meses (se descarta con 100 %, se conserva con 90 % y el aviso dice cuántos meses faltaron); lo mismo con carga
diaria; el extremo se recorta aunque la cobertura sea 50 %; con carga anual no cambia nada; lectura de un análisis
viejo. `tests/integration/test_stream_agregacion_mensual.py`: el aviso sobrevive al rechazo de Chow y la vista
calendario usa el mismo umbral. `tests/integration/db/test_persistencia.py`: persistencia y lectura implícita.

**Ver también:** [DECISIÓN 065](decision065.md) (revisión del 22/10/2026, R0.1 cerrada), [DECISIÓN 057](decision057.md),
[DECISIÓN 078](decision078.md) (el mismo patrón de parámetro validado en el borde y en `core/`, con lectura implícita).
