import pytest

from metis.core.utils import filtrar_numericos_alineados


@pytest.mark.unit
def test_filtrar_alineados_descarta_el_timestamp_de_cada_valor_descartado():
    serie = [1.0, None, 3.0, float("nan"), "abc", 6.0]
    timestamps = [2000, 2001, 2002, 2003, 2004, 2005]

    valores, ts = filtrar_numericos_alineados(serie, timestamps)

    assert valores == [1.0, 3.0, 6.0]
    assert ts == [2000, 2002, 2005]


@pytest.mark.unit
def test_filtrar_alineados_sin_timestamps_devuelve_none():
    valores, ts = filtrar_numericos_alineados([1.0, None, 3.0], None)

    assert valores == [1.0, 3.0]
    assert ts is None


@pytest.mark.unit
def test_filtrar_alineados_con_largos_distintos_conserva_los_timestamps():
    # No hay forma de emparejar por posición: se conserva el comportamiento
    # previo en vez de adivinar cuál timestamp corresponde a cuál valor.
    valores, ts = filtrar_numericos_alineados([1.0, None, 3.0], [2000, 2001])

    assert valores == [1.0, 3.0]
    assert ts == [2000, 2001]


@pytest.mark.unit
def test_filtrar_alineados_no_toca_una_serie_completa():
    valores, ts = filtrar_numericos_alineados([1, 2, 3], [2000, 2001, 2002])

    assert valores == [1.0, 2.0, 3.0]
    assert ts == [2000, 2001, 2002]
