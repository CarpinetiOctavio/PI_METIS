# DECISIÓN 053 — `session_store` pasa a un estado con TTL, no dos diccionarios sueltos
**Fecha:** 09 de Agosto de 2026
**Estado:** Decidida — implementación en curso (Bloque A del [plan de implementación de Etapa 2](../plan-etapa2-implementacion.md))

### Contexto

`metis/services/session_store.py` hoy es dos diccionarios en memoria de proceso:

```python
_store: dict[str, asyncio.Event] = {}
_decisions: dict[str, str] = {}
```

Diseñado para un único punto de pausa (Chow): `_decisions` guarda un `str`
(`"aceptar"`/`"rechazar"`), y la única forma de que una entrada se limpie es
que el `finally` de `stream_etapa1()` corra hasta el final y llame
`remove_session()`.

[DECISIÓN 052](decision052.md) agrega un segundo punto de pausa
(`result_etapa2_ranking`, resuelto por `distribution-decision`) que necesita
guardar más que una decisión de dos valores: necesita los parámetros ya
ajustados de las 13 distribuciones para no recalcularlos, y la serie original
para poder construir los eventos de diseño sin volver a tocar el archivo
subido.

### Diagnóstico

Tres problemas concretos con la estructura actual, si se la deja como está y
se le agrega Etapa 2 encima:

1. **`decision: str` no alcanza.** La selección de distribución+método+períodos
   de retorno es un payload estructurado, no un string de dos valores. Forzarlo
   a string obligaría a serializar/deserializar a mano en cada consumidor.
2. **Sin lugar para guardar los ajustes de Etapa 2.** Un
   `distribution-decision` con `session_id` no tendría de dónde sacar los
   parámetros ya calculados — habría que reajustar las 13 distribuciones de
   nuevo, tirando el trabajo que `ejecutar_etapa2()` ya hizo antes de pausar.
3. **Sin límite de vida real.** Hoy una sesión solo se limpia si el `finally`
   de `stream_etapa1()` corre. Si el cliente corta la conexión de una forma que
   no dispara ese `finally`, la entrada queda para siempre. Es tolerable con un
   `asyncio.Event` vacío; deja de serlo en cuanto cada entrada carga la serie
   completa y un `Etapa2Result` de 13 distribuciones.

### Opciones evaluadas

1. **Agregar campos sueltos a los diccionarios existentes** (un tercer/cuarto
   dict paralelo por campo). Descartada: multiplica el problema de
   sincronización que ya existe entre `_store` y `_decisions` (dos dicts que
   deben tener las mismas claves) a cuatro o cinco dicts en vez de dos.
2. **Persistir el estado de sesión en Postgres**, indexado por `analysis_id`.
   Descartada: `analysis_id` solo existe para CU-01 (usuarios autenticados que
   persisten) — CU-02 (anónimo) nunca tiene uno. Esta opción excluiría a CU-02
   del mismo mecanismo que CU-01, contradiciendo la razón por la que
   `session_store` es en memoria de proceso desde el principio
   ([DECISIÓN 005](decision005.md)).
3. **Una sola `dataclass` con todo el estado de la sesión, indexada por
   `session_id`, con barrido perezoso por TTL.** Elegida.

### Decisión

`session_store.py` pasa a un único diccionario de `SessionState`:

```python
@dataclass
class SessionState:
    event: asyncio.Event
    decision: dict | None = None        # antes str — ahora payload completo
    serie: list[float] | None = None
    tiene_ceros: bool = False
    etapa2: Etapa2Result | None = None
    created_at: float = field(default_factory=time.monotonic)
```

**La interfaz pública no cambia** — `create_session`, `wait_for_decision`,
`resolve_session`, `get_decision`, `remove_session` conservan su firma, así el
camino de Chow no se toca en absoluto.

Tres cambios de comportamiento, dentro de esa interfaz estable:

- **`decision` pasa de `str` a `dict`.** Chow manda `{"decision": "rechazar"}`;
  la selección de distribución manda el payload completo de
  `distribution-decision`. Un solo mecanismo para las dos pausas — cada
  consumidor lee la clave que le corresponde del dict.
- **El stream guarda `serie`, `tiene_ceros` y el `Etapa2Result`** antes de
  pausar en `result_etapa2_ranking`. Sin esto, `distribution-decision` no
  tendría los parámetros ajustados y habría que recalcular todo de nuevo.
- **Barrido por TTL, perezoso.** Se agrega `sweep_expired()`, llamado al
  principio de `create_session()` — recorre las entradas existentes y descarta
  las que superan `SESSION_TIMEOUT` (300s, la misma constante ya usada para el
  timeout de `wait_for_decision`). Sin tarea de fondo, sin
  `asyncio.create_task`, sin nada que pueda quedar colgado si el proceso se
  reinicia a mitad de una tarea programada. Suficiente para el volumen real de
  este sistema — un TP de grado, no un servicio con miles de sesiones
  concurrentes.

`SessionState` **no persiste nada en base de datos**. Es la razón concreta por
la que se descartó la opción 2: con esta forma, **CU-01 y CU-02 usan
exactamente el mismo camino** de principio a fin, igual que ya ocurre con el
resto del stream ([architecture.md](../../.claude/rules/architecture/architecture.md#mismo-endpoint-analysisstream-para-cu-01-y-cu-02) —
"Mismo endpoint /analysis/stream para CU-01 y CU-02").

### Criterio de hecho

- `session_store.py` expone `SessionState` y un único diccionario; la firma de
  las cinco funciones públicas no cambió.
- `tests/unit/services/test_session_store.py` cubre: `decision` como dict,
  presencia de `serie`/`etapa2` tras guardarlos, y `sweep_expired()` limpiando
  una entrada vieja sin que nadie llame `remove_session()` explícitamente.
- El camino de Chow (`outlier-decision`) sigue pasando sus tests existentes sin
  modificación de aserciones.
- `docker exec <backend> pytest -m "unit or integration" -v` en verde.

**Ver también:** [DECISIÓN 052](decision052.md) — el contrato SSE que motiva
este cambio. [DECISIÓN 005](decision005.md) — por qué el almacenamiento en
memoria de proceso (no BD) ya era la decisión vigente para tokens/sesiones
efímeras antes de esta pasada.
