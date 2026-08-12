import pytest

from metis.core.validacion.aggregation import (
    MOTIVO_EXTREMO_FIN,
    MOTIVO_EXTREMO_INICIO,
    MOTIVO_HUECO_INTERIOR,
    agregar_a_maximos_anuales,
)


def _fechas_mensuales(anio_inicio: int, mes_inicio: int, cantidad: int) -> list[str]:
    """cantidad meses consecutivos en ISO ("YYYY-MM-01"), arrancando en
    (anio_inicio, mes_inicio)."""
    fechas = []
    anio, mes = anio_inicio, mes_inicio
    for _ in range(cantidad):
        fechas.append(f"{anio:04d}-{mes:02d}-01")
        mes += 1
        if mes > 12:
            mes = 1
            anio += 1
    return fechas


@pytest.mark.unit
def test_dos_anios_completos_sin_recorte():
    # mes_inicio=6: 24 meses exactos, jun2000-may2002 — dos períodos
    # completos, sin descartes.
    timestamps = _fechas_mensuales(2000, 6, 24)
    serie = [100.0 + i for i in range(24)]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=6)

    assert resultado.timestamps == [2000, 2001]
    assert resultado.serie == [111.0, 123.0]  # último mes de cada período
    assert resultado.periodos_descartados == []


@pytest.mark.unit
def test_recorte_de_inicio_ejemplo_del_plan():
    # Ejemplo literal del plan (F4): mes_inicio=6, registro arranca en
    # marzo — marzo-mayo 2001 no forman un año completo, se descartan. El
    # primer año del análisis es junio2001-mayo2002.
    timestamps = _fechas_mensuales(2001, 3, 15)  # mar2001 .. may2002
    serie = [float(i) for i in range(15)]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=6)

    assert resultado.timestamps == [2001]
    assert len(resultado.periodos_descartados) == 1
    descartado = resultado.periodos_descartados[0]
    assert descartado.anio == 2000
    assert descartado.motivo == MOTIVO_EXTREMO_INICIO
    assert descartado.meses_presentes == 3
    assert descartado.meses_faltantes == 9


@pytest.mark.unit
def test_recorte_de_fin_ejemplo_del_plan():
    # Ejemplo literal del plan (F4): mismo registro pero termina en
    # agosto — junio-agosto no llegan a cerrar el año, se descartan. El
    # último año del análisis es junio2009-mayo2010.
    timestamps = _fechas_mensuales(2009, 6, 15)  # jun2009 .. ago2010
    serie = [float(i) for i in range(15)]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=6)

    assert resultado.timestamps == [2009]
    assert len(resultado.periodos_descartados) == 1
    descartado = resultado.periodos_descartados[0]
    assert descartado.anio == 2010
    assert descartado.motivo == MOTIVO_EXTREMO_FIN
    assert descartado.meses_presentes == 3


@pytest.mark.unit
def test_los_dos_extremos_parciales_a_la_vez():
    # mar2001 .. ago2002: extremo de inicio (2000, parcial) + un año
    # completo (2001) + extremo de fin (2002, parcial).
    timestamps = _fechas_mensuales(2001, 3, 18)
    serie = [float(i) for i in range(18)]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=6)

    assert resultado.timestamps == [2001]
    motivos = {p.anio: p.motivo for p in resultado.periodos_descartados}
    assert motivos == {2000: MOTIVO_EXTREMO_INICIO, 2002: MOTIVO_EXTREMO_FIN}


@pytest.mark.unit
def test_mes_inicio_1_reproduce_el_anio_calendario():
    timestamps = _fechas_mensuales(2000, 1, 24)  # ene2000 .. dic2001
    serie = [float(i) for i in range(24)]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=1)

    assert resultado.timestamps == [2000, 2001]
    assert resultado.serie == [11.0, 23.0]
    assert resultado.periodos_descartados == []


@pytest.mark.unit
def test_mes_inicio_12_cruza_el_cambio_de_anio_calendario():
    # Caso borde del plan: con mes_inicio=12, un período tiene un solo mes
    # del lado "viejo" (diciembre) y once del lado nuevo.
    timestamps = _fechas_mensuales(2000, 12, 24)  # dic2000 .. nov2002
    serie = [float(i) for i in range(24)]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=12)

    assert resultado.timestamps == [2000, 2001]
    assert resultado.periodos_descartados == []
    # período 2000 = dic2000 (i=0) .. nov2001 (i=11) -> máximo i=11
    # período 2001 = dic2001 (i=12) .. nov2002 (i=23) -> máximo i=23
    assert resultado.serie == [11.0, 23.0]


@pytest.mark.unit
def test_hueco_interior_se_descarta_con_motivo_distinto_del_extremo():
    # Tres años calendario (mes_inicio=1); al del medio le faltan 3 meses
    # -> se descarta como hueco interior, no como extremo, aunque 2000 y
    # 2002 sí queden completos.
    timestamps = (
        _fechas_mensuales(2000, 1, 12)
        + _fechas_mensuales(2001, 1, 9)  # falta oct/nov/dic 2001
        + _fechas_mensuales(2002, 1, 12)
    )
    serie = [float(i) for i in range(len(timestamps))]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=1)

    assert resultado.timestamps == [2000, 2002]
    assert len(resultado.periodos_descartados) == 1
    descartado = resultado.periodos_descartados[0]
    assert descartado.anio == 2001
    assert descartado.motivo == MOTIVO_HUECO_INTERIOR
    assert descartado.meses_presentes == 9
    assert descartado.meses_faltantes == 3


@pytest.mark.unit
def test_valor_faltante_rompe_completitud_igual_que_mes_ausente():
    # El mes está en timestamps pero el valor es None — tiene que contar
    # como si ese mes no estuviera, igual que si faltara directamente.
    timestamps = _fechas_mensuales(2000, 1, 24)
    serie = [float(i) for i in range(24)]
    serie[5] = None  # jun2000 sin dato

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=1)

    assert resultado.timestamps == [2001]  # 2000 se descarta, 2001 sigue completo
    assert len(resultado.periodos_descartados) == 1
    assert resultado.periodos_descartados[0].anio == 2000
    assert resultado.periodos_descartados[0].meses_presentes == 11


@pytest.mark.unit
def test_serie_vacia_si_no_hay_ningun_periodo_completo():
    timestamps = _fechas_mensuales(2000, 1, 5)  # solo 5 meses, ningún año completo
    serie = [float(i) for i in range(5)]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=1)

    assert resultado.serie == []
    assert resultado.timestamps == []
    assert len(resultado.periodos_descartados) == 1
