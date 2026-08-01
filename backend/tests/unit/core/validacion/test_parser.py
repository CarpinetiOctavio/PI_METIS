import pandas as pd
import pytest

from metis.core.validacion.parser import leer_columnas_preview


@pytest.mark.unit
def test_columnas_y_filas_de_un_csv_valido():
    csv = b"anio,caudal\n1980,94.71\n1981,89.83\n1982,105.13\n"
    columnas, filas = leer_columnas_preview(csv, "serie.csv")

    assert filas == 3
    assert [c["nombre"] for c in columnas] == ["anio", "caudal"]
    assert [c["indice"] for c in columnas] == [0, 1]


@pytest.mark.unit
def test_muestra_limitada_a_5_valores_aunque_el_archivo_tenga_mas():
    filas_csv = "\n".join(f"{1980 + i},{100 + i}" for i in range(20))
    csv = f"anio,caudal\n{filas_csv}\n".encode()

    columnas, filas = leer_columnas_preview(csv, "serie.csv")

    assert filas == 20
    for col in columnas:
        assert len(col["muestra"]) <= 5


@pytest.mark.unit
def test_muestra_son_strings_y_excluye_valores_faltantes():
    csv = b"anio,caudal\n1980,94.71\n1981,\n1982,105.13\n"

    columnas, _ = leer_columnas_preview(csv, "serie.csv")

    caudal = next(c for c in columnas if c["nombre"] == "caudal")
    assert caudal["muestra"] == ["94.71", "105.13"]
    assert all(isinstance(v, str) for v in caudal["muestra"])


@pytest.mark.unit
def test_archivo_vacio_levanta_empty_data_error():
    # No hay una guarda explícita de "sin columnas" en leer_columnas_preview —
    # pandas ya levanta antes de devolver un DataFrame (ver docstring de la
    # función). EmptyDataError es subclase de ValueError, así que el endpoint
    # lo mapea a PARSE_ERROR igual que cualquier otro archivo no parseable.
    csv = b""

    with pytest.raises(pd.errors.EmptyDataError):
        leer_columnas_preview(csv, "vacio.csv")
    with pytest.raises(ValueError):
        leer_columnas_preview(csv, "vacio.csv")


@pytest.mark.unit
def test_archivo_no_parseable_propaga_la_excepcion_de_pandas():
    contenido_binario_no_csv = bytes(range(256))

    with pytest.raises(Exception):  # noqa: B017 — cualquier excepción de pandas, el endpoint la mapea a PARSE_ERROR
        leer_columnas_preview(contenido_binario_no_csv, "corrupto.csv")
