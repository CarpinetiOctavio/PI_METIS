import pandas as pd
import pytest

from metis.core.validacion.aggregation import (
    MOTIVO_EXTREMO_FIN,
    MOTIVO_EXTREMO_INICIO,
    MOTIVO_HUECO_INTERIOR,
    _esperados,
    agregar_a_maximos_anuales,
    agregar_a_maximos_mensuales,
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


def _fechas_diarias(inicio: str, fin: str) -> list[str]:
    """Días consecutivos en ISO ("YYYY-MM-DD"), ambos extremos incluidos."""
    return [d.strftime("%Y-%m-%d") for d in pd.date_range(inicio, fin, freq="D")]


# ─────────────────────────── mensual (no-regresión) ──────────────────────────
# Estos tests son la prueba de no-regresión de R2 (docs/plan-resolucion-diaria.md
# §R5): la firma nueva con defaults (resolucion="mensual",
# cobertura_minima_interior=1.0) tiene que devolver EXACTAMENTE lo mismo que
# antes. El único cambio mecánico es el rename de PeriodoDescartado
# (meses_presentes/faltantes -> unidades_presentes/faltantes/esperadas).


@pytest.mark.unit
def test_dos_anios_completos_sin_recorte():
    timestamps = _fechas_mensuales(2000, 6, 24)
    serie = [100.0 + i for i in range(24)]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=6)

    assert resultado.timestamps == [2000, 2001]
    assert resultado.serie == [111.0, 123.0]
    assert resultado.periodos_descartados == []
    assert resultado.periodos_incompletos_aceptados == []


@pytest.mark.unit
def test_recorte_de_inicio_ejemplo_del_plan():
    timestamps = _fechas_mensuales(2001, 3, 15)  # mar2001 .. may2002
    serie = [float(i) for i in range(15)]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=6)

    assert resultado.timestamps == [2001]
    assert len(resultado.periodos_descartados) == 1
    descartado = resultado.periodos_descartados[0]
    assert descartado.anio == 2000
    assert descartado.motivo == MOTIVO_EXTREMO_INICIO
    assert descartado.unidades_presentes == 3
    assert descartado.unidades_faltantes == 9
    assert descartado.unidades_esperadas == 12


@pytest.mark.unit
def test_recorte_de_fin_ejemplo_del_plan():
    timestamps = _fechas_mensuales(2009, 6, 15)  # jun2009 .. ago2010
    serie = [float(i) for i in range(15)]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=6)

    assert resultado.timestamps == [2009]
    assert len(resultado.periodos_descartados) == 1
    descartado = resultado.periodos_descartados[0]
    assert descartado.anio == 2010
    assert descartado.motivo == MOTIVO_EXTREMO_FIN
    assert descartado.unidades_presentes == 3


@pytest.mark.unit
def test_los_dos_extremos_parciales_a_la_vez():
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
    timestamps = _fechas_mensuales(2000, 12, 24)  # dic2000 .. nov2002
    serie = [float(i) for i in range(24)]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=12)

    assert resultado.timestamps == [2000, 2001]
    assert resultado.periodos_descartados == []
    assert resultado.serie == [11.0, 23.0]


@pytest.mark.unit
def test_hueco_interior_se_descarta_con_motivo_distinto_del_extremo():
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
    assert descartado.unidades_presentes == 9
    assert descartado.unidades_faltantes == 3


@pytest.mark.unit
def test_valor_faltante_rompe_completitud_igual_que_mes_ausente():
    timestamps = _fechas_mensuales(2000, 1, 24)
    serie = [float(i) for i in range(24)]
    serie[5] = None  # jun2000 sin dato

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=1)

    assert resultado.timestamps == [2001]
    assert len(resultado.periodos_descartados) == 1
    assert resultado.periodos_descartados[0].anio == 2000
    assert resultado.periodos_descartados[0].unidades_presentes == 11


@pytest.mark.unit
def test_serie_vacia_si_no_hay_ningun_periodo_completo():
    timestamps = _fechas_mensuales(2000, 1, 5)  # solo 5 meses, ningún año completo
    serie = [float(i) for i in range(5)]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=1)

    assert resultado.serie == []
    assert resultado.timestamps == []
    assert len(resultado.periodos_descartados) == 1


# ────────────────────────────── diaria (R2 / R5) ─────────────────────────────


@pytest.mark.unit
def test_diaria_anio_completo_sin_recorte():
    timestamps = _fechas_diarias("2001-01-01", "2001-12-31")  # 365 días, no bisiesto
    serie = [float(i) for i in range(len(timestamps))]

    resultado = agregar_a_maximos_anuales(
        serie, timestamps, mes_inicio=1, resolucion="diaria"
    )

    assert resultado.timestamps == [2001]
    assert resultado.serie == [364.0]  # el máximo es el último día
    assert resultado.periodos_descartados == []


@pytest.mark.unit
def test_diaria_bisiesto_con_mes_inicio_1():
    # 3 años calendario; a 2000 (bisiesto) se le saca un día -> interior con
    # 365/366 -> incompleto con el default estricto (1.0).
    timestamps = (
        _fechas_diarias("1999-01-01", "1999-12-31")
        + [d for d in _fechas_diarias("2000-01-01", "2000-12-31") if d != "2000-06-15"]
        + _fechas_diarias("2001-01-01", "2001-12-31")
    )
    serie = [float(i) for i in range(len(timestamps))]

    resultado = agregar_a_maximos_anuales(
        serie, timestamps, mes_inicio=1, resolucion="diaria"
    )

    assert resultado.timestamps == [1999, 2001]
    assert len(resultado.periodos_descartados) == 1
    descartado = resultado.periodos_descartados[0]
    assert descartado.anio == 2000
    assert descartado.motivo == MOTIVO_HUECO_INTERIOR
    assert descartado.unidades_esperadas == 366  # bisiesto — el punto del test
    assert descartado.unidades_presentes == 365
    assert descartado.unidades_faltantes == 1


@pytest.mark.unit
def test_esperados_bisiesto_con_mes_inicio_distinto_de_1():
    # El período mes_inicio=3 que arranca en 2015 termina en febrero de 2016
    # (bisiesto) -> espera 366 días. El que arranca en 2014 espera 365.
    # Es el caso que se rompe si alguien reescribe _esperados() con
    # aritmética de calendario a mano.
    assert len(_esperados(2015, 3, "diaria")) == 366
    assert len(_esperados(2014, 3, "diaria")) == 365
    assert len(_esperados(2015, 3, "mensual")) == 12


@pytest.mark.unit
def test_diaria_mes_inicio_3_periodo_incompleto_por_febrero_bisiesto():
    # 365 días cuando el período (mes_inicio=3, arranca 2015) espera 366:
    # falta justo el 29-feb-2016. Único período -> extremo -> descartado.
    # Si _esperados() devolviera 365 (febrero de 28), cobertura daría 1.0 y
    # esto se aceptaría — el assert de unidades_esperadas lo caza.
    timestamps = _fechas_diarias("2015-03-01", "2016-02-28")
    serie = [float(i) for i in range(len(timestamps))]

    resultado = agregar_a_maximos_anuales(
        serie, timestamps, mes_inicio=3, resolucion="diaria"
    )

    assert resultado.serie == []
    assert resultado.periodos_descartados[0].unidades_esperadas == 366
    assert resultado.periodos_descartados[0].unidades_presentes == 365


@pytest.mark.unit
def test_diaria_el_maximo_anual_no_es_el_ultimo_dia_del_mes():
    # Trampa de R2.2: el cuerpo del loop ASIGNA, no maximiza. Con la clave de
    # agrupación en granularidad de mes, el dict se quedaría con el último día
    # de cada mes y descartaría el pico de mitad de mes en silencio.
    timestamps = _fechas_diarias("2001-01-01", "2001-12-31")
    serie = [1.0] * len(timestamps)
    serie[timestamps.index("2001-07-15")] = 999.0  # pico a mitad de mes

    resultado = agregar_a_maximos_anuales(
        serie, timestamps, mes_inicio=1, resolucion="diaria"
    )

    assert resultado.serie == [999.0]  # con el bug de la clave mensual daría 1.0


@pytest.mark.unit
def test_diaria_recorte_de_inicio():
    timestamps = _fechas_diarias("2000-07-01", "2001-12-31")  # arranca a mitad de 2000
    serie = [float(i) for i in range(len(timestamps))]

    resultado = agregar_a_maximos_anuales(
        serie, timestamps, mes_inicio=1, resolucion="diaria"
    )

    assert resultado.timestamps == [2001]
    assert resultado.periodos_descartados[0].anio == 2000
    assert resultado.periodos_descartados[0].motivo == MOTIVO_EXTREMO_INICIO


@pytest.mark.unit
def test_diaria_recorte_de_fin():
    timestamps = _fechas_diarias("2000-01-01", "2001-08-15")  # termina a mitad de 2001
    serie = [float(i) for i in range(len(timestamps))]

    resultado = agregar_a_maximos_anuales(
        serie, timestamps, mes_inicio=1, resolucion="diaria"
    )

    assert resultado.timestamps == [2000]
    assert resultado.periodos_descartados[0].anio == 2001
    assert resultado.periodos_descartados[0].motivo == MOTIVO_EXTREMO_FIN


@pytest.mark.unit
def test_diaria_mes_inicio_1_reproduce_el_anio_calendario():
    timestamps = _fechas_diarias("2000-01-01", "2001-12-31")
    serie = [float(i) for i in range(len(timestamps))]

    resultado = agregar_a_maximos_anuales(
        serie, timestamps, mes_inicio=1, resolucion="diaria"
    )

    assert resultado.timestamps == [2000, 2001]
    # 2000 bisiesto -> índice 365 es el último día de 2000
    assert resultado.serie[0] == 365.0
    assert resultado.periodos_descartados == []


@pytest.mark.unit
def test_diaria_mes_inicio_12_cruza_el_cambio_de_anio():
    # dic2000 .. nov2002 -> dos períodos completos con mes_inicio=12.
    timestamps = _fechas_diarias("2000-12-01", "2002-11-30")
    serie = [float(i) for i in range(len(timestamps))]

    resultado = agregar_a_maximos_anuales(
        serie, timestamps, mes_inicio=12, resolucion="diaria"
    )

    assert resultado.timestamps == [2000, 2001]
    assert resultado.periodos_descartados == []


# ─────────────────── R2.3 — regla asimétrica de cobertura ────────────────────


@pytest.mark.unit
def test_asimetria_interior_al_96_por_ciento_aceptado_con_umbral_0_95():
    # 2001 interior, faltan los últimos 16 días de diciembre -> 349/365 ≈ 0.956.
    timestamps = (
        _fechas_diarias("2000-01-01", "2000-12-31")
        + _fechas_diarias("2001-01-01", "2001-12-15")
        + _fechas_diarias("2002-01-01", "2002-12-31")
    )
    serie = [float(i) for i in range(len(timestamps))]

    resultado = agregar_a_maximos_anuales(
        serie,
        timestamps,
        mes_inicio=1,
        resolucion="diaria",
        cobertura_minima_interior=0.95,
    )

    assert resultado.timestamps == [2000, 2001, 2002]
    assert resultado.periodos_descartados == []
    assert len(resultado.periodos_incompletos_aceptados) == 1
    aceptado = resultado.periodos_incompletos_aceptados[0]
    assert aceptado.anio == 2001
    assert aceptado.unidades_esperadas == 365
    assert aceptado.unidades_faltantes == 16


@pytest.mark.unit
def test_asimetria_mismo_anio_al_96_en_posicion_de_extremo_se_descarta():
    # Idéntico al anterior pero 2001 es el ÚLTIMO año -> extremo -> exige
    # 100 % aunque el umbral interior lo permitiría.
    timestamps = _fechas_diarias("2000-01-01", "2000-12-31") + _fechas_diarias(
        "2001-01-01", "2001-12-15"
    )
    serie = [float(i) for i in range(len(timestamps))]

    resultado = agregar_a_maximos_anuales(
        serie,
        timestamps,
        mes_inicio=1,
        resolucion="diaria",
        cobertura_minima_interior=0.95,
    )

    assert resultado.timestamps == [2000]
    assert resultado.periodos_incompletos_aceptados == []
    assert resultado.periodos_descartados[0].anio == 2001
    assert resultado.periodos_descartados[0].motivo == MOTIVO_EXTREMO_FIN


@pytest.mark.unit
def test_asimetria_interior_al_96_con_umbral_estricto_1_0_se_descarta():
    timestamps = (
        _fechas_diarias("2000-01-01", "2000-12-31")
        + _fechas_diarias("2001-01-01", "2001-12-15")
        + _fechas_diarias("2002-01-01", "2002-12-31")
    )
    serie = [float(i) for i in range(len(timestamps))]

    resultado = agregar_a_maximos_anuales(
        serie, timestamps, mes_inicio=1, resolucion="diaria"
    )  # cobertura_minima_interior=1.0 por default

    assert resultado.timestamps == [2000, 2002]
    assert resultado.periodos_incompletos_aceptados == []
    assert resultado.periodos_descartados[0].anio == 2001
    assert resultado.periodos_descartados[0].motivo == MOTIVO_HUECO_INTERIOR


# ─────────────────── agregar_a_maximos_mensuales (R3.3 opción 2) ─────────────


@pytest.mark.unit
def test_maximos_mensuales_un_valor_por_mes_con_el_pico_del_mes():
    timestamps = _fechas_diarias("2001-01-01", "2001-03-31")
    serie = [1.0] * len(timestamps)
    serie[timestamps.index("2001-02-10")] = 50.0  # pico de febrero

    serie_mensual, ts_mensual = agregar_a_maximos_mensuales(serie, timestamps)

    assert ts_mensual == ["2001-01-01", "2001-02-01", "2001-03-01"]
    assert serie_mensual == [1.0, 50.0, 1.0]


@pytest.mark.unit
def test_maximos_mensuales_ignora_faltantes_y_ordena_cronologicamente():
    timestamps = ["2001-02-01", "2001-01-01", "2001-01-15", "2001-02-20"]
    serie = [3.0, 1.0, None, 9.0]

    serie_mensual, ts_mensual = agregar_a_maximos_mensuales(serie, timestamps)

    assert ts_mensual == ["2001-01-01", "2001-02-01"]
    assert serie_mensual == [1.0, 9.0]


# ──────────── colisión de clave: timestamp duplicado (DECISIÓN 067) ──────────
# CONTRACT_DUPLICATE_TIMESTAMPS es warning NO bloqueante, así que la
# agregación recibe series con timestamps repetidos. La regla es conservar el
# MAYOR, nunca el último del archivo — antes de DECISIÓN 067,
# agregar_a_maximos_anuales() asignaba y el pico real del año podía
# desaparecer sin que nada lo señalara.


@pytest.mark.unit
def test_diaria_timestamp_duplicado_conserva_el_maximo_no_el_ultimo():
    timestamps = _fechas_diarias("2001-01-01", "2001-12-31")
    serie = [1.0] * len(timestamps)
    serie[timestamps.index("2001-06-15")] = 999.0  # pico real del año
    # el archivo repite el 15/06 al final, con un valor mucho menor
    timestamps = [*timestamps, "2001-06-15"]
    serie = [*serie, 0.5]

    resultado = agregar_a_maximos_anuales(
        serie, timestamps, mes_inicio=1, resolucion="diaria"
    )

    assert resultado.serie == [999.0]
    assert resultado.timestamps == [2001]
    # el duplicado no rompe la completitud: sigue siendo el mismo día
    assert resultado.periodos_descartados == []


@pytest.mark.unit
def test_mensual_timestamp_duplicado_conserva_el_maximo_no_el_ultimo():
    timestamps = _fechas_mensuales(2001, 1, 12)
    serie = [1.0] * 12
    serie[5] = 777.0  # pico real: junio
    timestamps = [*timestamps, "2001-06-01"]
    serie = [*serie, 2.0]

    resultado = agregar_a_maximos_anuales(serie, timestamps, mes_inicio=1)

    assert resultado.serie == [777.0]
    assert resultado.periodos_descartados == []


@pytest.mark.unit
def test_maximos_mensuales_duplicado_conserva_el_maximo():
    # misma regla en la otra función del módulo — las dos comparten
    # _acumular_maximo() justamente para no volver a divergir
    serie_mensual, ts_mensual = agregar_a_maximos_mensuales(
        [500.0, 10.0], ["2001-01-15", "2001-01-15"]
    )

    assert ts_mensual == ["2001-01-01"]
    assert serie_mensual == [500.0]
