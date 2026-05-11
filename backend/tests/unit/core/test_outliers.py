import pytest

from metis.core.outliers import calcular_chow


# Serie con atípico evidente — verificada con smoke test.
# 29 valores en 50.0 + un valor 100x mayor produce rechazo de Chow.
SERIE_CON_ATIPICO = [50.0] * 29 + [5000.0]
VALOR_ATIPICO_CONOCIDO = 5000.0


# ── Casos no ejecutada ────────────────────────────────────────────────────────


@pytest.mark.unit
def test_cero_en_caudal_no_ejecutada():
    # Cero en caudal_precipitacion tiene código propio — Chow aplica sobre log.
    serie = [0.0] + [10.0] * 14
    resultado = calcular_chow(serie, "caudal_precipitacion")
    assert resultado.veredicto == "no_ejecutada"
    assert resultado.warning_codigo == "TEST_NOT_EXECUTED_ZEROS"
    assert resultado.estadistico is None


@pytest.mark.unit
def test_cero_en_otro_no_ejecutada():
    # En tipo "otro" el cero no es especial — cae en la rama general de valor <= 0.
    serie = [0.0] + [10.0] * 14
    resultado = calcular_chow(serie, "otro")
    assert resultado.veredicto == "no_ejecutada"
    assert resultado.warning_codigo == "TEST_NOT_EXECUTED_CONDITION"
    assert resultado.estadistico is None


@pytest.mark.unit
def test_negativo_no_ejecutada():
    serie = [-5.0] + [10.0] * 14
    resultado = calcular_chow(serie, "otro")
    assert resultado.veredicto == "no_ejecutada"
    assert resultado.warning_codigo == "TEST_NOT_EXECUTED_CONDITION"
    assert resultado.estadistico is None


# ── Sin atípico ───────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_sin_atipico_aprobada(serie_facundo):
    resultado = calcular_chow(serie_facundo, "caudal_precipitacion")
    assert resultado.veredicto == "aprobada"
    assert resultado.warning_codigo is None
    assert resultado.valor_atipico is None


# ── Con atípico ───────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_atipico_detectado_rechazada():
    resultado = calcular_chow(SERIE_CON_ATIPICO, "otro")
    assert resultado.veredicto == "rechazada"
    assert resultado.warning_codigo == "TEST_WARNING_OUTLIER_DETECTED"


@pytest.mark.unit
def test_atipico_warning_nivel_normal():
    # Chow nunca genera warning crítico — siempre normal.
    resultado = calcular_chow(SERIE_CON_ATIPICO, "otro")
    assert resultado.warning_nivel == "normal"


@pytest.mark.unit
def test_atipico_valor_original_en_valor_atipico():
    # valor_atipico es el valor original de la serie, no su logaritmo.
    resultado = calcular_chow(SERIE_CON_ATIPICO, "otro")
    assert resultado.valor_atipico == VALOR_ATIPICO_CONOCIDO
