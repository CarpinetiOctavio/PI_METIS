"""
Tests unitarios de _serializar_etapa2() (Bloque A5, DECISIÓN 055) —
hermana exacta de _serializar_etapa1(): serializa la grilla completa, sin
aplanar a un top-3.
"""

import pytest

from metis.core.etapa2.types import DistResult, Etapa2Result, MetodoResult, PuntoEmpirico
from metis.core.types import WarningItem
from metis.services.analysis_service import _serializar_etapa2


def _etapa2_result_de_ejemplo() -> Etapa2Result:
    return Etapa2Result(
        puntos_empiricos=[
            PuntoEmpirico(valor=142.5, periodo_retorno=41.0, probabilidad=0.9756),
            PuntoEmpirico(valor=98.1, periodo_retorno=20.5, probabilidad=0.9512),
        ],
        ranking=[
            DistResult(
                distribucion="gumbel",
                n_parametros=2,
                metodos=[
                    MetodoResult(
                        metodo="momentos",
                        parametros={"mu": 100.0, "alpha": 20.0},
                        eea=12.5,
                        status="ok",
                    ),
                    MetodoResult(
                        metodo="mv", parametros=None, eea=None, status="no_converge"
                    ),
                ],
                mejor_eea=12.5,
                mejor_metodo="momentos",
            ),
            DistResult(
                distribucion="gen_pareto",
                n_parametros=3,
                metodos=[
                    MetodoResult(
                        metodo="momentos",
                        parametros=None,
                        eea=None,
                        status="no_aplicable",
                    ),
                ],
                mejor_eea=None,
                mejor_metodo=None,
            ),
        ],
        warnings=[
            WarningItem(
                codigo="DIST_HIGH_EEA",
                nivel="normal",
                descripcion="gumbel/momentos: EEA supera el 5% de la media",
            )
        ],
    )


@pytest.mark.unit
def test_serializar_etapa2_incluye_las_13_distribuciones_sin_aplanar():
    # No aplana a top-3 — acá con 2 para simplificar el fixture, pero el
    # contrato es "todas las que traiga el ranking", sin recortar.
    resultado = _serializar_etapa2(_etapa2_result_de_ejemplo())

    assert len(resultado["ranking"]) == 2
    assert [d["distribucion"] for d in resultado["ranking"]] == ["gumbel", "gen_pareto"]


@pytest.mark.unit
def test_serializar_etapa2_incluye_metodos_que_fallaron_no_los_oculta():
    resultado = _serializar_etapa2(_etapa2_result_de_ejemplo())

    gumbel_dict = resultado["ranking"][0]
    assert len(gumbel_dict["metodos"]) == 2
    metodo_fallido = next(m for m in gumbel_dict["metodos"] if m["metodo"] == "mv")
    assert metodo_fallido["status"] == "no_converge"
    assert metodo_fallido["parametros"] is None
    assert metodo_fallido["eea"] is None


@pytest.mark.unit
def test_serializar_etapa2_expone_mejor_eea_y_mejor_metodo():
    resultado = _serializar_etapa2(_etapa2_result_de_ejemplo())

    gumbel_dict = resultado["ranking"][0]
    assert gumbel_dict["mejor_eea"] == 12.5
    assert gumbel_dict["mejor_metodo"] == "momentos"

    gen_pareto_dict = resultado["ranking"][1]
    assert gen_pareto_dict["mejor_eea"] is None
    assert gen_pareto_dict["mejor_metodo"] is None


@pytest.mark.unit
def test_serializar_etapa2_incluye_warnings():
    resultado = _serializar_etapa2(_etapa2_result_de_ejemplo())

    assert resultado["warnings"] == [
        {
            "codigo": "DIST_HIGH_EEA",
            "nivel": "normal",
            "descripcion": "gumbel/momentos: EEA supera el 5% de la media",
        }
    ]


@pytest.mark.unit
def test_serializar_etapa2_sin_warnings_da_lista_vacia():
    resultado = _serializar_etapa2(Etapa2Result(ranking=[]))

    assert resultado == {
        "ranking": [],
        "warnings": [],
        "puntos_empiricos": [],
        "seleccion": None,
    }


@pytest.mark.unit
def test_serializar_etapa2_incluye_puntos_empiricos():
    resultado = _serializar_etapa2(_etapa2_result_de_ejemplo())

    assert resultado["puntos_empiricos"] == [
        {"valor": 142.5, "periodo_retorno": 41.0, "probabilidad": 0.9756},
        {"valor": 98.1, "periodo_retorno": 20.5, "probabilidad": 0.9512},
    ]
