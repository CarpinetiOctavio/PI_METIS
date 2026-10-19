"""No regresión del nivel de significancia configurable (DECISIÓN 078).

Con α = 0,05 la Etapa 1 tiene que dar EXACTAMENTE lo mismo que antes de que α
fuera un parámetro, en las 9 estaciones de la tesis, el caso Las Tapias y las
series de docs/series prueba/. La referencia la generó
`generar_referencia_etapa1.py` con el código previo al cambio.

La comparación es exacta, también en los floats: reescribir los valores críticos
en función de α no puede mover ningún número. Solo se toleran claves NUEVAS
dentro de un dict (por ejemplo `alfa` y el cuantil usado en
`explicacion.terminos`): una clave que desaparece o un valor que cambia falla.
"""

import dataclasses
import json
import math
from pathlib import Path

import pytest

from metis.core.pipeline.pipeline_etapa1 import ejecutar_etapa1

REFERENCIA = json.loads(
    Path(__file__)
    .with_name("referencia_etapa1_alfa_005.json")
    .read_text(encoding="utf-8")
)


def _diferencias(ref, actual, ruta="") -> list[str]:
    if isinstance(ref, dict):
        if not isinstance(actual, dict):
            return [f"{ruta}: esperaba un dict, hay {type(actual).__name__}"]
        out = []
        for clave, valor in ref.items():
            if clave not in actual:
                out.append(f"{ruta}.{clave}: falta")
            else:
                out += _diferencias(valor, actual[clave], f"{ruta}.{clave}")
        return out
    if isinstance(ref, list):
        if not isinstance(actual, list) or len(ref) != len(actual):
            return [f"{ruta}: lista distinta ({ref!r:.80} vs {actual!r:.80})"]
        out = []
        for i, (a, b) in enumerate(zip(ref, actual, strict=True)):
            out += _diferencias(a, b, f"{ruta}[{i}]")
        return out
    if isinstance(ref, float) and isinstance(actual, float):
        if math.isnan(ref) and math.isnan(actual):
            return []
    if ref != actual:
        return [f"{ruta}: {ref!r} != {actual!r}"]
    return []


@pytest.mark.unit
@pytest.mark.parametrize("clave", sorted(REFERENCIA))
def test_alfa_005_da_lo_mismo_que_antes_de_ser_configurable(clave):
    caso = REFERENCIA[clave]["entrada"]
    resultado = ejecutar_etapa1(
        caso["serie"], caso["tipo_variable"], "anual", caso["timestamps"], alfa=0.05
    )
    # Ida y vuelta por JSON, igual que la referencia (tuplas -> listas, etc.).
    actual = json.loads(json.dumps(dataclasses.asdict(resultado), default=str))

    diferencias = _diferencias(REFERENCIA[clave]["resultado"], actual)
    assert diferencias == [], "\n".join(diferencias[:20])
