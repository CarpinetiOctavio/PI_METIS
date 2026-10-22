"""DECISIÓN 081 — cobertura mínima de los años interiores, a criterio del usuario.

Casos VL-11 (bordes del parámetro), CE-08 (valores no enteros) y TD-06 (cobertura × tipo
de año) de docs/calidad/casos-de-prueba.md. Los ids de parametrize son los IDs del
documento. Facundo (22/10/2026): "lo dejaría a criterio del operador".
"""

import pandas as pd
import pytest
from fastapi import HTTPException

from metis.api.v1.analysis import _validar_cobertura_minima_interior
from metis.core.pipeline.pipeline_etapa1 import ejecutar_etapa1
from metis.services.analysis_service import _configuracion_con_implicitos


def _codigo_400(exc_info) -> str:
    assert exc_info.value.status_code == 400
    return exc_info.value.detail["error"]["codigo"]


# ── VL-11 / CE-08: el parámetro en el borde de la API ───────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    ("valor", "esperado"),
    [("50", 50), ("100", 100), ("90", 90)],
    ids=["VL-11b 50", "VL-11c 100", "VL-11e 90"],
)
def test_cobertura_en_el_rango(valor, esperado):
    assert _validar_cobertura_minima_interior(valor) == esperado


@pytest.mark.unit
@pytest.mark.parametrize(
    "valor",
    ["49", "101", "abc", "90.5", ""],
    ids=["VL-11a 49", "VL-11d 101", "CE-08a abc", "CE-08b 90.5", "CE-08c vacío"],
)
def test_cobertura_fuera_del_rango_o_no_entera_da_400(valor):
    with pytest.raises(HTTPException) as exc_info:
        _validar_cobertura_minima_interior(valor)

    assert _codigo_400(exc_info) == "CONTRACT_COBERTURA_INVALID"


@pytest.mark.unit
@pytest.mark.parametrize("fraccion", [0.49, 1.01])
def test_core_tampoco_acepta_una_cobertura_fuera_del_rango(fraccion):
    # core/ no confía en el borde, mismo criterio que alfa (DECISIÓN 078).
    with pytest.raises(ValueError):
        ejecutar_etapa1(
            [float(i) for i in range(20)],
            "otro",
            resolucion_temporal="anual",
            cobertura_minima_interior=fraccion,
        )


# ── TD-06: cobertura × tipo de año ───────────────────────────────────────────────


def _mensual_sin(anios: int, faltantes: set[str]) -> tuple[list[float], list[str]]:
    """`anios` años completos desde ene2000, sin los meses de `faltantes` ("AAAA-MM")."""
    fechas = [
        d.strftime("%Y-%m-%d")
        for d in pd.date_range("2000-01-01", periods=anios * 12, freq="MS")
        if d.strftime("%Y-%m") not in faltantes
    ]
    return [50.0 + (i * 7) % 40 for i in range(len(fechas))], fechas


def _diaria_sin(anios: int, anio_hueco: int, dias: int) -> tuple[list[float], list[str]]:
    """`anios` años diarios desde 2000, sin los primeros `dias` días de `anio_hueco`."""
    hueco = set(pd.date_range(f"{anio_hueco}-01-01", periods=dias, freq="D"))
    fechas = [
        d.strftime("%Y-%m-%d")
        for d in pd.date_range("2000-01-01", f"{2000 + anios - 1}-12-31", freq="D")
        if d not in hueco
    ]
    return [10.0 + (i * 13) % 97 for i in range(len(fechas))], fechas


def _correr(serie, fechas, resolucion, cobertura):
    return ejecutar_etapa1(
        serie,
        "otro",
        resolucion_temporal=resolucion,
        timestamps=fechas,
        mes_inicio_anio=1,
        cobertura_minima_interior=cobertura,
    )


def _warning(resultado, codigo):
    return next((w for w in resultado.warnings if w.codigo == codigo), None)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("resolucion", "cobertura", "n_anios", "descartado", "aceptado", "detalle"),
    [
        ("mensual", None, 11, True, False, None),
        ("mensual", 1.0, 11, True, False, None),
        ("mensual", 0.9, 12, False, True, "2005 (faltan 1 de 12 meses)"),
        ("diaria", 1.0, 11, True, False, None),
        ("diaria", 0.95, 12, False, True, "2005 (faltan 10 de 365 días)"),
    ],
    ids=[
        "TD-06a mensual, sin indicar",
        "TD-06b mensual, 100 %",
        "TD-06c mensual, 90 %",
        "TD-06d diaria, 100 %",
        "TD-06e diaria, 95 %",
    ],
)
def test_anio_interior_incompleto_segun_la_cobertura(
    resolucion, cobertura, n_anios, descartado, aceptado, detalle
):
    if resolucion == "mensual":
        serie, fechas = _mensual_sin(12, {"2005-03"})  # 2005: 11 de 12 meses
    else:
        serie, fechas = _diaria_sin(12, 2005, 10)  # 2005: 355 de 365 días

    resultado = _correr(serie, fechas, resolucion, cobertura)

    assert len(resultado.serie_efectiva) == n_anios
    assert (2005 in resultado.timestamps_efectivos) is not descartado
    assert (_warning(resultado, "CONTRACT_INCOMPLETE_YEARS_DISCARDED") is not None) is (
        descartado
    )
    aceptado_w = _warning(resultado, "CONTRACT_INCOMPLETE_YEARS_ACCEPTED")
    assert (aceptado_w is not None) is aceptado
    if detalle:
        assert detalle in aceptado_w.descripcion
        assert "sesgado a la baja" in aceptado_w.descripcion


@pytest.mark.unit
def test_td06f_extremo_incompleto_se_recorta_aunque_la_cobertura_sea_baja():
    # La regla asimétrica no cambia: los extremos siempre exigen 100 %.
    serie, fechas = _mensual_sin(12, {"2011-12"})  # último año: 11 de 12 meses

    resultado = _correr(serie, fechas, "mensual", 0.5)

    assert len(resultado.serie_efectiva) == 11
    assert _warning(resultado, "CONTRACT_PARTIAL_YEARS_TRIMMED") is not None
    assert _warning(resultado, "CONTRACT_INCOMPLETE_YEARS_ACCEPTED") is None


@pytest.mark.unit
def test_td06g_con_carga_anual_la_cobertura_no_cambia_nada():
    serie = [50.0 + (i * 7) % 40 for i in range(20)]
    anios = list(range(1990, 2010))

    con_piso = _correr(serie, anios, "anual", 0.5)
    por_defecto = _correr(serie, anios, "anual", None)

    assert con_piso.serie_efectiva == por_defecto.serie_efectiva
    assert con_piso.warnings == por_defecto.warnings
    assert con_piso.nivel_confianza == por_defecto.nivel_confianza


# ── Lectura de un análisis anterior a la DECISIÓN 081 ───────────────────────────


@pytest.mark.unit
def test_analisis_anterior_sin_cobertura_se_lee_como_100_implicito():
    configuracion = _configuracion_con_implicitos({"mes_inicio_anio": 7, "alfa": 0.05})

    assert configuracion["cobertura_minima_interior"] == 100
    assert configuracion["cobertura_minima_interior_implicita"] is True
    assert "alfa_implicito" not in configuracion


@pytest.mark.unit
def test_analisis_con_cobertura_registrada_no_la_marca_implicita():
    configuracion = _configuracion_con_implicitos({"cobertura_minima_interior": 90})

    assert configuracion["cobertura_minima_interior"] == 90
    assert "cobertura_minima_interior_implicita" not in configuracion
