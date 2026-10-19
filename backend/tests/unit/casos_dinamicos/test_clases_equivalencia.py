"""B8 del TP de Calidad — clases de equivalencia (docs/calidad/casos-de-prueba.md, casos CE-xx).

Un representante por clase. Solo está acá lo que no cubría otro test: el resto de las clases
apunta, en el documento, al test que ya existía.
"""

import io

import pandas as pd
import pytest
from fastapi import HTTPException

from metis.api.v1.analysis import _validar_alfa
from metis.core.validacion.parser import leer_columnas_preview

FILAS = [(1980, 94.71), (1981, 89.83), (1982, 105.13)]


def _excel() -> bytes:
    buffer = io.BytesIO()
    pd.DataFrame(FILAS, columns=["anio", "caudal"]).to_excel(buffer, index=False)
    return buffer.getvalue()


def _csv() -> bytes:
    return ("anio,caudal\n" + "".join(f"{a},{v}\n" for a, v in FILAS)).encode()


# ── CE-03: formato del archivo subido ───────────────────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    ("contenido", "nombre"),
    [(_csv(), "serie.csv"), (_excel(), "serie.xlsx")],
    ids=["CE-03a CSV válido", "CE-03b Excel válido"],
)
def test_formatos_validos_dan_las_mismas_columnas(contenido, nombre):
    columnas, filas = leer_columnas_preview(contenido, nombre)

    assert filas == 3
    assert [c["nombre"] for c in columnas] == ["anio", "caudal"]
    caudal = next(c for c in columnas if c["nombre"] == "caudal")
    assert caudal["muestra"] == ["94.71", "89.83", "105.13"]


@pytest.mark.unit
def test_excel_con_extension_pero_contenido_csv_no_se_parsea():
    # La clase "ilegible" también incluye un archivo cuyo contenido no coincide con la
    # extensión: el endpoint lo mapea a PARSE_ERROR (test_analysis_preview_columns.py).
    with pytest.raises(Exception):  # noqa: B017 — cualquier excepción del lector de Excel
        leer_columnas_preview(_csv(), "serie.xlsx")


# ── CE-06: nivel de significancia (DECISIÓN 078) ────────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    ("entrada", "esperado"),
    [("0.01", 0.01), ("0.05", 0.05), ("0.10", 0.10)],
    ids=["CE-06a alfa=0.01", "CE-06a alfa=0.05", "CE-06a alfa=0.10"],
)
def test_alfa_de_los_tres_niveles_es_valido(entrada, esperado):
    assert _validar_alfa(entrada) == esperado


@pytest.mark.unit
@pytest.mark.parametrize(
    "entrada",
    ["0.2", "0.025", "abc", ""],
    ids=["CE-06b alfa=0.2", "CE-06b alfa=0.025", "CE-06c no numérico", "CE-06c vacío"],
)
def test_alfa_fuera_del_conjunto_da_400(entrada):
    with pytest.raises(HTTPException) as exc_info:
        _validar_alfa(entrada)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["codigo"] == "CONTRACT_ALFA_INVALID"
