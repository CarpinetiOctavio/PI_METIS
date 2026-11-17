"""No regresión del nivel de significancia configurable (DECISIÓN 078).

Con α = 0,05 la Etapa 1 tiene que dar EXACTAMENTE lo mismo que antes de que α
fuera un parámetro, en las 9 estaciones de la tesis, el caso Las Tapias y las
series de docs/series prueba/. La referencia la generó
`generar_referencia_etapa1.py` con el código previo al cambio.

La comparación es exacta en todo menos los floats: reescribir los valores
críticos en función de α no puede mover ningún número. Solo se toleran claves
NUEVAS dentro de un dict (por ejemplo `alfa` y el cuantil usado en
`explicacion.terminos`): una clave que desaparece o un valor que cambia falla.

Los floats se comparan con tolerancia relativa `_REL_TOL` = 1e-9, no con `==`:
la referencia se generó en otra máquina, y numpy suma con instrucciones
vectoriales distintas según el CPU. En el runner de CI eso movía el último
dígito (diferencias relativas de hasta ~3e-12, amplificadas en Chow cuando el
desvío de los logaritmos es chico, ~0,0023 en la serie diaria). Un cambio real
de valor crítico es varios órdenes mayor: 1,96 contra norm.ppf(0,975) difiere
en 1,8e-5 relativo, y lo sigue detectando.
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

_REL_TOL = 1e-9
# Para los valores que deberían ser 0 (una media de residuos, por ejemplo).
_ABS_TOL = 1e-12


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
        if math.isclose(ref, actual, rel_tol=_REL_TOL, abs_tol=_ABS_TOL):
            return []
        return [f"{ruta}: {ref!r} != {actual!r}"]
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
