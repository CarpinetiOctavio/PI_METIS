import pandas as pd
import pytest

from metis.core.validacion.parser import leer_columnas_preview, parse_file


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


@pytest.mark.unit
def test_columna_de_anio_puro_infiere_resolucion_anual():
    # Bug encontrado en verificación manual (05/08/2026): pd.to_datetime()
    # sin `format` interpreta enteros como nanosegundos desde epoch, no como
    # años — este es el caso MÁS común del dominio (series anuales con una
    # columna "anio" de 4 dígitos, exactamente el formato de la tesis de
    # Facundo) y antes de este fix bloqueaba TODO el pipeline con
    # CONTRACT_NO_TEMPORAL_RESOLUTION.
    filas_csv = "\n".join(f"{1980 + i},{100 + i}.5" for i in range(40))
    csv = f"anio,caudal\n{filas_csv}\n".encode()

    resultado = parse_file(csv, "serie.csv", columna_x="anio", columna_y="caudal")

    assert resultado.resolucion_temporal == "anual"
    assert len(resultado.serie) == 40


@pytest.mark.unit
def test_columna_de_anio_puro_con_pocos_anios_no_confunde_con_mensual():
    # Guarda de no-regresión: con años consecutivos el delta real es de un
    # año (>=300 días), nunca debería caer en la rama "mensual" (25-299 días).
    csv = b"anio,caudal\n1980,94.71\n1981,89.83\n1982,105.13\n"

    resultado = parse_file(csv, "serie.csv", columna_x="anio", columna_y="caudal")

    assert resultado.resolucion_temporal == "anual"


@pytest.mark.unit
def test_columna_de_fechas_reales_sigue_funcionando():
    # No-regresión: el camino de fechas ISO reales (no años puros) no debe
    # verse afectado por la detección de años puros.
    csv = (
        b"fecha,caudal\n"
        b"1980-01-01,94.71\n1981-01-01,89.83\n1982-01-01,105.13\n"
        b"1983-01-01,110.2\n1984-01-01,120.4\n"
    )

    resultado = parse_file(csv, "serie.csv", columna_x="fecha", columna_y="caudal")

    assert resultado.resolucion_temporal == "anual"


@pytest.mark.unit
def test_hueco_largo_no_hace_confundir_mensual_con_anual():
    # F2.3 (Bloque F, plan §7) — un hueco largo en una serie mayormente
    # mensual no debe empujar el PROMEDIO de deltas por encima del umbral de
    # "anual". Cinco pasos mensuales reales (31, 29, 31, 30, 31 días — 31 es
    # mayoría real, no un empate de moda) seguidos de un hueco de ~3 años y
    # medio: bajo el promedio viejo, ese único hueco domina el promedio de
    # los 6 deltas y cruza el umbral de 300 días -> "anual" (mal). Bajo la
    # moda, 31 sigue siendo el valor dominante -> "mensual" (correcto).
    csv = (
        b"fecha,caudal\n"
        b"2000-01-01,94.71\n2000-02-01,89.83\n2000-03-01,105.13\n"
        b"2000-04-01,110.2\n2000-05-01,120.4\n2000-06-01,98.1\n"
        b"2003-10-01,102.3\n"
    )

    resultado = parse_file(csv, "serie.csv", columna_x="fecha", columna_y="caudal")

    assert resultado.resolucion_temporal == "mensual"


@pytest.mark.unit
def test_columna_de_anio_y_mes_como_fecha_sigue_siendo_mensual():
    # No-regresión: fechas mensuales en formato ISO (no años puros de 4
    # dígitos como valor completo) deben seguir infiriendo "mensual".
    fechas = pd.date_range("1980-01-01", periods=24, freq="MS")
    filas_csv = "\n".join(
        f"{fecha.date()},{100 + i}" for i, fecha in enumerate(fechas)
    )
    csv = f"fecha,caudal\n{filas_csv}\n".encode()

    resultado = parse_file(csv, "serie.csv", columna_x="fecha", columna_y="caudal")

    assert resultado.resolucion_temporal == "mensual"
