"""DECISIÓN 071 — aplicar_exclusiones(): eliminar los puntos excluidos con su año."""

import pytest

from metis.core.pipeline.exclusiones import (
    ExclusionInvalidaError,
    aplicar_exclusiones,
)

SERIE = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
ANIOS = [2000, 2001, 2002, 2003, 2004, 2005]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("indices", "serie", "anios"),
    [
        ([0], [20.0, 30.0, 40.0, 50.0, 60.0], [2001, 2002, 2003, 2004, 2005]),
        ([5], [10.0, 20.0, 30.0, 40.0, 50.0], [2000, 2001, 2002, 2003, 2004]),
        ([2], [10.0, 20.0, 40.0, 50.0, 60.0], [2000, 2001, 2003, 2004, 2005]),
        ([4, 0, 2], [20.0, 40.0, 60.0], [2001, 2003, 2005]),
        ([0, 1, 2, 3, 4, 5], [], []),
        ([], SERIE, ANIOS),
    ],
    ids=["primero", "ultimo", "interior", "varios-desordenados", "todos", "ninguno"],
)
def test_elimina_valor_y_anio_por_indice(indices, serie, anios):
    r = aplicar_exclusiones(SERIE, ANIOS, indices)

    assert r.serie == serie
    assert r.anios == anios
    assert len(r.serie) == len(r.anios)
    assert [e.indice for e in r.excluidos] == sorted(indices)


@pytest.mark.unit
def test_excluidos_traen_periodo_y_valor_original():
    r = aplicar_exclusiones(SERIE, ANIOS, [3, 1])
    assert [(e.indice, e.periodo, e.valor_original) for e in r.excluidos] == [
        (1, 2001, 20.0),
        (3, 2003, 40.0),
    ]


@pytest.mark.unit
def test_no_modifica_la_entrada():
    serie, anios = list(SERIE), list(ANIOS)
    aplicar_exclusiones(serie, anios, [1, 2])
    assert serie == SERIE and anios == ANIOS


@pytest.mark.unit
@pytest.mark.parametrize(
    ("anios", "indices", "tratamiento"),
    [
        (ANIOS, [1, 1], "eliminar"),
        (ANIOS, [6], "eliminar"),
        (ANIOS, [-1], "eliminar"),
        (ANIOS[:-1], [0], "eliminar"),
        (ANIOS, [0], "media"),
    ],
    ids=["repetido", "fuera-arriba", "negativo", "largos-distintos", "tratamiento-inexistente"],
)
def test_pedidos_invalidos_levantan_error(anios, indices, tratamiento):
    with pytest.raises(ExclusionInvalidaError):
        aplicar_exclusiones(SERIE, anios, indices, tratamiento)
