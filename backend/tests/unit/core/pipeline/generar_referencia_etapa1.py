"""Genera `referencia_etapa1_alfa_005.json`: el resultado de la Etapa 1 de las
series de referencia, tal como lo calculaba METIS ANTES de que el nivel de
significancia fuera configurable (DECISIÓN 078, plan del 18/10/2026, bloque B).

`test_no_regresion_alfa.py` lo compara contra el resultado actual con α = 0,05:
tiene que ser idéntico. No se regenera para "arreglar" una diferencia — una
diferencia es una regresión.

Correr desde la raíz del repositorio (lee docs/):

    python backend/tests/unit/core/pipeline/generar_referencia_etapa1.py

Series: las 9 estaciones de la tesis (docs/auditoria/regresion/regresion-pipeline/),
Las Tapias del caso del libro (1942-1979, n = 36) y las de docs/series prueba/.
La diaria se guarda ya agregada a máximos anuales (mes_inicio_anio = 7): la
batería, que es lo que depende de α, corre sobre esa serie.
"""

import dataclasses
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(RAIZ / "backend"))
sys.path.insert(0, str(RAIZ / "docs/auditoria/comparacion-herramientas/scripts"))

from metis.core.pipeline.pipeline_etapa1 import ejecutar_etapa1  # noqa: E402
from metis.core.validacion.parser import parse_file  # noqa: E402
from series import estaciones  # noqa: E402

SALIDA = Path(__file__).with_name("referencia_etapa1_alfa_005.json")
SERIES_PRUEBA = RAIZ / "docs/series prueba"

# Caso Las Tapias del libro: dos años sin dato (1967 y 1973).
LAS_TAPIAS = [
    12,
    100,
    12,
    10,
    32,
    32,
    18,
    42,
    29,
    3,
    57,
    10,
    50,
    10,
    40,
    36,
    20,
    16,
    10,
]
LAS_TAPIAS += [
    31,
    7,
    9,
    18,
    10,
    38,
    None,
    4,
    23,
    12,
    16,
    48,
    None,
    23,
    2,
    11,
    45,
    21,
    8,
]


def _caso(serie, timestamps, tipo_variable):
    return {"serie": serie, "timestamps": timestamps, "tipo_variable": tipo_variable}


def _desde_archivo(nombre, col_x, col_y):
    datos = parse_file((SERIES_PRUEBA / nombre).read_bytes(), nombre, col_x, col_y)
    return datos


def casos() -> dict:
    out = {}
    for e in estaciones():
        n = len(e["serie"])
        out[e["clave"]] = _caso(
            e["serie"], list(range(1950, 1950 + n)), "caudal_precipitacion"
        )

    anios = list(range(1942, 1980))
    out["las_tapias"] = _caso(
        [float(v) for v in LAS_TAPIAS if v is not None],
        [a for a, v in zip(anios, LAS_TAPIAS, strict=True) if v is not None],
        "caudal_precipitacion",
    )

    for clave, archivo, col_y, tipo in [
        (
            "serie_con_atipico",
            "serie_con_atipico.csv",
            "caudal",
            "caudal_precipitacion",
        ),
        ("negativos_otro", "serie_con_negativos_otro.csv", "nivel_m", "otro"),
        (
            "negativos_caudal",
            "serie_con_negativos_otro.csv",
            "nivel_m",
            "caudal_precipitacion",
        ),
        ("mini_serie", "mini_serie.csv", "caudal", "caudal_precipitacion"),
    ]:
        d = _desde_archivo(archivo, "anio", col_y)
        out[clave] = _caso(d.serie, d.timestamps, tipo)

    d = _desde_archivo("serie_diaria_40anios.csv", "fecha", "caudal")
    agregada = ejecutar_etapa1(
        d.serie, "caudal_precipitacion", d.resolucion_temporal, d.timestamps
    )
    out["diaria_40anios_agregada"] = _caso(
        agregada.serie_efectiva, agregada.timestamps_efectivos, "caudal_precipitacion"
    )
    return out


def resultado(caso: dict) -> dict:
    r = ejecutar_etapa1(
        caso["serie"], caso["tipo_variable"], "anual", caso["timestamps"]
    )
    return dataclasses.asdict(r)


if __name__ == "__main__":
    salida = {}
    for clave, caso in casos().items():
        salida[clave] = {"entrada": caso, "resultado": resultado(caso)}
    SALIDA.write_text(json.dumps(salida, indent=1, default=str), encoding="utf-8")
    print(f"{len(salida)} series -> {SALIDA}")
