import numpy as np
import pytest
from scipy.stats import t as t_dist

from metis.core.etapa1.outliers import calcular_chow


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


# ── K_N (Grubbs-Beck, Bulletin 17B Apéndice 4) — DECISIÓN 018 ────────────────


def _k_n_esperado(n: int, alpha: float = 0.10) -> float:
    t_val = t_dist.ppf(1 - alpha / (2 * n), df=n - 2)
    return ((n - 1) / np.sqrt(n)) * np.sqrt(t_val**2 / (n - 2 + t_val**2))


@pytest.mark.unit
def test_valor_critico_es_k_n_no_cuantil_t_crudo(serie_facundo):
    # valor_critico debe ser K_N (transformación geométrica de Grubbs-Beck),
    # no el cuantil t crudo de Bonferroni — son números bien distintos.
    n = len(serie_facundo)
    k_n_esperado = _k_n_esperado(n)
    t_crudo = t_dist.ppf(1 - 0.10 / (2 * n), df=n - 1)

    resultado = calcular_chow(serie_facundo, "caudal_precipitacion")

    assert resultado.valor_critico == pytest.approx(k_n_esperado, abs=1e-9)
    assert resultado.valor_critico != pytest.approx(t_crudo, abs=1e-3)


@pytest.mark.unit
def test_k_n_n30_aproxima_valor_tabla_referencia():
    # Verificación independiente contra la fórmula de Grubbs-Beck para n=30:
    # K_N ≈ 2.745, valor citado como el de la tabla del Apéndice 4 de
    # Bulletin 17B para N=30 (referencia externa, no verificada contra la
    # tabla impresa — ver DECISIÓN 018 para el detalle de esta limitación).
    k_n_30 = _k_n_esperado(30)
    assert k_n_30 == pytest.approx(2.745, abs=1e-2)

    resultado = calcular_chow(SERIE_CON_ATIPICO, "otro")
    assert resultado.valor_critico == pytest.approx(k_n_30, abs=1e-9)
