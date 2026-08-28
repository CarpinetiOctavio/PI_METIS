"""Helpers compartidos de los tests de integración de stream.

Extraídos para no repetir el mismo boilerplate (parseo de eventos SSE y
los kwargs fijos de `stream_analysis()`) en cada archivo — la duplicación
entre `test_stream_agregacion_diaria.py` y su espejo mensual disparaba el
quality gate de SonarCloud (PR #78, `new_duplicated_lines_density`).

No es un `conftest.py`: son funciones normales que los tests importan
explícitamente. La única pieza que va en `conftest.py` (por ser fixture)
es la limpieza de `session_store`.
"""

import json
import uuid

from metis.services.analysis_service import stream_analysis

_KWARGS_BASE = {
    "filename": "serie.csv",
    "columna_x": "fecha",
    "columna_y": "caudal",
    "tipo_variable": "otro",
    "modo": "experto",
    "cramer_particion": "default",
    "etapas": [1],
    "user_id": None,
    "db": None,
}


def parse_sse(evento: str) -> tuple[str, dict]:
    """`"event: X\\ndata: {...}\\n\\n"` -> `("X", {...})`."""
    lineas = evento.strip("\n").split("\n")
    tipo = lineas[0].removeprefix("event: ")
    data = json.loads(lineas[1].removeprefix("data: "))
    return tipo, data


def run_stream(content: bytes, **overrides):
    """`stream_analysis()` con los kwargs que todos los tests de integración
    comparten. `overrides` pisa cualquiera (`columna_x`, `etapas`,
    `mes_inicio_anio`, ...). Devuelve `(generator, session_id)` — el
    `session_id` para mandar decisiones a mitad de stream.
    """
    session_id = overrides.pop("session_id", str(uuid.uuid4()))
    kwargs = {**_KWARGS_BASE, "content": content, **overrides}
    return stream_analysis(session_id=session_id, **kwargs), session_id
