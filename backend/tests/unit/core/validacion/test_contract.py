import pytest

from metis.core.validacion.contract import validar_contrato


@pytest.mark.unit
def test_menos_de_10_datos_es_bloqueante():
    serie = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]
    result = validar_contrato(serie, "otro", "anual")
    assert result.bloqueante is True
    assert result.codigo_error == "CONTRACT_SERIES_TOO_SHORT"


@pytest.mark.unit
def test_sin_resolucion_temporal_es_bloqueante():
    serie = [float(i) for i in range(10, 20)]
    result = validar_contrato(serie, "otro", resolucion_temporal=None)
    assert result.bloqueante is True
    assert result.codigo_error == "CONTRACT_NO_TEMPORAL_RESOLUTION"


@pytest.mark.unit
def test_strings_no_cuentan_para_minimo():
    # 5 numéricos + 5 strings = 10 elementos, pero solo 5 numéricos válidos.
    # El bloqueante CONTRACT_SERIES_TOO_SHORT debe ganar — CONTRACT_NON_NUMERIC_VALUES no aparece.
    serie = [10.0, 20.0, 30.0, 40.0, 50.0, "a", "b", "c", "d", "e"]
    result = validar_contrato(serie, "otro", "anual")
    assert result.bloqueante is True
    assert result.codigo_error == "CONTRACT_SERIES_TOO_SHORT"
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_NON_NUMERIC_VALUES" not in codigos


@pytest.mark.unit
def test_entre_10_y_29_activa_length_warning(serie_corta_15):
    result = validar_contrato(serie_corta_15, "otro", "anual")
    assert result.bloqueante is False
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_LENGTH_WARNING" in codigos


@pytest.mark.unit
def test_30_o_mas_sin_length_warning():
    serie = [float(i) for i in range(30, 60)]
    result = validar_contrato(serie, "otro", "anual")
    assert result.bloqueante is False
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_LENGTH_WARNING" not in codigos


@pytest.mark.unit
def test_negativos_en_caudal_activa_warning():
    serie = [10.0, -5.0] + [float(i) for i in range(20, 38)]
    result = validar_contrato(serie, "caudal_precipitacion", "anual")
    assert result.bloqueante is False
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_NEGATIVE_VALUES" in codigos


@pytest.mark.unit
def test_negativos_en_tipo_otro_sin_warning():
    serie = [10.0, -5.0] + [float(i) for i in range(20, 38)]
    result = validar_contrato(serie, "otro", "anual")
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_NEGATIVE_VALUES" not in codigos


@pytest.mark.unit
def test_none_activa_missing_values():
    serie = [10.0, None] + [float(i) for i in range(20, 49)]
    result = validar_contrato(serie, "otro", "anual")
    assert result.bloqueante is False
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_MISSING_VALUES" in codigos


@pytest.mark.unit
def test_nan_activa_missing_values():
    serie = [10.0, float("nan")] + [float(i) for i in range(20, 49)]
    result = validar_contrato(serie, "otro", "anual")
    assert result.bloqueante is False
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_MISSING_VALUES" in codigos


@pytest.mark.unit
def test_strings_mezclados_activa_non_numeric():
    # 30 numéricos + strings — supera el mínimo, solo avisa de no numéricos.
    serie = [float(i) for i in range(30)] + ["x", "y"]
    result = validar_contrato(serie, "otro", "anual")
    assert result.bloqueante is False
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_NON_NUMERIC_VALUES" in codigos


@pytest.mark.unit
def test_timestamps_duplicados():
    serie = [float(i) for i in range(30)]
    timestamps = list(range(1980, 2009)) + [2008]  # 2008 duplicado
    result = validar_contrato(serie, "otro", "anual", timestamps=timestamps)
    assert result.bloqueante is False
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_DUPLICATE_TIMESTAMPS" in codigos


@pytest.mark.unit
def test_timestamps_desordenados():
    serie = [float(i) for i in range(30)]
    timestamps = list(range(1980, 2010))
    timestamps[5], timestamps[6] = timestamps[6], timestamps[5]  # swap dos años
    result = validar_contrato(serie, "otro", "anual", timestamps=timestamps)
    assert result.bloqueante is False
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_WRONG_ORDER" in codigos


@pytest.mark.unit
def test_timestamps_espaciado_irregular():
    serie = [float(i) for i in range(30)]
    timestamps = list(range(1980, 2010))
    timestamps[10] = timestamps[10] + 1  # rompe la regularidad anual
    result = validar_contrato(serie, "otro", "anual", timestamps=timestamps)
    assert result.bloqueante is False
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_IRREGULAR_SPACING" in codigos


@pytest.mark.unit
def test_serie_mensual_real_no_dispara_espaciado_irregular():
    # F2.2 (Bloque F) — 12 meses consecutivos reales (28/29/30/31 días según
    # el mes) no deben marcarse como espaciado irregular cuando
    # resolucion_temporal="mensual": la comparación tiene que ser por mes
    # (ordinal de período), no por cantidad exacta de días.
    serie = [float(i) for i in range(30, 42)]
    timestamps = [
        "2000-01-01",
        "2000-02-01",
        "2000-03-01",
        "2000-04-01",
        "2000-05-01",
        "2000-06-01",
        "2000-07-01",
        "2000-08-01",
        "2000-09-01",
        "2000-10-01",
        "2000-11-01",
        "2000-12-01",
    ]
    result = validar_contrato(serie, "otro", "mensual", timestamps=timestamps)
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_IRREGULAR_SPACING" not in codigos


@pytest.mark.unit
def test_serie_mensual_con_mes_salteado_si_dispara_espaciado_irregular():
    # Contraprueba de la anterior — un mes realmente salteado (marzo directo
    # a mayo) tiene que seguir marcándose irregular bajo la nueva lógica por
    # ordinal de mes, igual que lo hacía (por casualidad) la lógica vieja.
    serie = [float(i) for i in range(30, 42)]
    timestamps = [
        "2000-01-01",
        "2000-02-01",
        "2000-05-01",  # salta marzo y abril
        "2000-06-01",
        "2000-07-01",
        "2000-08-01",
        "2000-09-01",
        "2000-10-01",
        "2000-11-01",
        "2000-12-01",
        "2001-01-01",
        "2001-02-01",
    ]
    result = validar_contrato(serie, "otro", "mensual", timestamps=timestamps)
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_IRREGULAR_SPACING" in codigos


@pytest.mark.unit
def test_multiples_warnings_se_acumulan():
    # 30 numéricos + negativos + None + strings — todos los warnings no bloqueantes.
    serie = [-5.0, None] + [float(i) for i in range(1, 29)] + ["z"]
    result = validar_contrato(serie, "caudal_precipitacion", "anual")
    assert result.bloqueante is False
    codigos = [w.codigo for w in result.warnings]
    assert "CONTRACT_NEGATIVE_VALUES" in codigos
    assert "CONTRACT_MISSING_VALUES" in codigos
    assert "CONTRACT_NON_NUMERIC_VALUES" in codigos
