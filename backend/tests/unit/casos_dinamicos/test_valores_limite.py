"""B8 del TP de Calidad — valores límite (docs/calidad/casos-de-prueba.md, casos VL-xx).

Cada parámetro se prueba a los dos lados de cada borde. Los ids de parametrize son los IDs
del documento, para que un caso se pueda buscar por su ID en la salida de pytest. Los bordes
que ya cubría otro test no se repiten acá: el documento apunta a ese test.
"""

import io

import pytest
from fastapi import HTTPException, UploadFile

from metis.api.v1.analysis import (
    MAX_UPLOAD_BYTES,
    _leer_archivo_limitado,
    _parsear_cramer_particion,
    _validar_mes_inicio,
    _validar_seleccion_distribucion,
)
from metis.core.etapa1.trend import calcular_mann_kendall
from metis.core.validacion.contract import validar_contrato


def _serie_sin_tendencia(n: int) -> list[float]:
    # Valores que suben y bajan sin dirección: Mann-Kendall no detecta tendencia en
    # ningún n de los que se prueban acá, así que el warning que queda es el de tamaño.
    base = [5.0, 3.0, 8.0, 1.0, 9.0, 2.0, 7.0, 4.0, 6.0, 10.0]
    return [base[i % len(base)] + (i // len(base)) * 0.1 for i in range(n)]


def _codigo_400(exc_info) -> str:
    assert exc_info.value.status_code == 400
    return exc_info.value.detail["error"]["codigo"]


# ── VL-01: longitud de la serie (contrato de datos) ─────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    ("n", "bloqueante", "con_length_warning"),
    [
        (9, True, False),
        (10, False, True),
        (29, False, True),
        (30, False, False),
    ],
    ids=["VL-01a n=9", "VL-01b n=10", "VL-01c n=29", "VL-01d n=30"],
)
def test_longitud_de_la_serie(n, bloqueante, con_length_warning):
    result = validar_contrato([float(10 + i) for i in range(n)], "otro", "anual")

    assert result.bloqueante is bloqueante
    if bloqueante:
        assert result.codigo_error == "CONTRACT_SERIES_TOO_SHORT"
    codigos = [w.codigo for w in result.warnings]
    assert ("CONTRACT_LENGTH_WARNING" in codigos) is con_length_warning


# ── VL-02: tamaño del archivo subido (DECISIÓN 050) ──────────────────────────────
# VL-02a (exactamente MAX_UPLOAD_BYTES) ya lo cubre test_upload_limits.py; este es el
# primer byte de más, que allá se prueba con 5 MB de más.


@pytest.mark.unit
async def test_archivo_un_byte_sobre_el_limite_da_400():
    archivo = UploadFile(
        file=io.BytesIO(b"x" * (MAX_UPLOAD_BYTES + 1)), filename="serie.csv"
    )

    with pytest.raises(HTTPException) as exc_info:
        await _leer_archivo_limitado(archivo)
    assert _codigo_400(exc_info) == "PARSE_FILE_TOO_LARGE"


# ── VL-03: mes_inicio_anio ───────────────────────────────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize("mes", [1, 12], ids=["VL-03b mes=1", "VL-03c mes=12"])
def test_mes_inicio_en_el_rango(mes):
    assert _validar_mes_inicio(mes) == mes


@pytest.mark.unit
@pytest.mark.parametrize("mes", [0, 13], ids=["VL-03a mes=0", "VL-03d mes=13"])
def test_mes_inicio_fuera_del_rango(mes):
    with pytest.raises(HTTPException) as exc_info:
        _validar_mes_inicio(mes)
    assert _codigo_400(exc_info) == "CONTRACT_MES_INICIO_INVALID"


# ── VL-04 y VL-05: periodos_retorno (distribution-decision y design-events) ─────


@pytest.mark.unit
@pytest.mark.parametrize(
    "periodos",
    [
        [1.0001],
        [2],
        list(range(2, 22)),  # 20 elementos
    ],
    ids=["VL-04b T=1.0001", "VL-05b 1 elemento", "VL-05c 20 elementos"],
)
def test_periodos_retorno_validos(periodos):
    _validar_seleccion_distribucion("gumbel", "momentos", periodos)


@pytest.mark.unit
@pytest.mark.parametrize(
    "periodos",
    [
        [1.0],
        [],
        list(range(2, 23)),  # 21 elementos
    ],
    ids=["VL-04a T=1", "VL-05a 0 elementos", "VL-05d 21 elementos"],
)
def test_periodos_retorno_invalidos(periodos):
    with pytest.raises(HTTPException) as exc_info:
        _validar_seleccion_distribucion("gumbel", "momentos", periodos)
    assert _codigo_400(exc_info) == "DIST_SELECTION_INVALID"


# ── VL-06: cramer_particion personalizada ───────────────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    ("n1", "n2"),
    [(100, 99), (2, 1)],
    ids=["VL-06b n1=100 n2=99", "VL-06c n1=2 n2=1"],
)
def test_cramer_particion_en_los_bordes_validos(n1, n2):
    assert _parsear_cramer_particion(f'{{"n1_pct": {n1}, "n2_pct": {n2}}}') == {
        "n1_pct": n1,
        "n2_pct": n2,
    }


@pytest.mark.unit
@pytest.mark.parametrize(
    ("n1", "n2"),
    [(100, 100), (1, 1), (60, 0)],
    ids=["VL-06d n1=n2=100", "VL-06e n1=n2=1", "VL-06f n2=0"],
)
def test_cramer_particion_en_los_bordes_invalidos(n1, n2):
    with pytest.raises(HTTPException) as exc_info:
        _parsear_cramer_particion(f'{{"n1_pct": {n1}, "n2_pct": {n2}}}')
    assert _codigo_400(exc_info) == "CONTRACT_CRAMER_PARTICION_INVALID"


# ── VL-08: Mann-Kendall, umbrales de n ──────────────────────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    ("n", "veredicto", "warning"),
    [
        (9, "no_ejecutada", "TEST_NOT_EXECUTED_MIN_SAMPLES"),
        (10, "aprobada", "TEST_WARNING_SMALL_SAMPLE"),
        (30, "aprobada", "TEST_WARNING_SMALL_SAMPLE"),
        (31, "aprobada", None),
    ],
    ids=["VL-08a n=9", "VL-08b n=10", "VL-08c n=30", "VL-08d n=31"],
)
def test_mann_kendall_umbrales_de_n(n, veredicto, warning):
    resultado = calcular_mann_kendall(_serie_sin_tendencia(n))

    assert resultado.veredicto == veredicto
    assert resultado.warning_codigo == warning
