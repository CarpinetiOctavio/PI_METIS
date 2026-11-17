"""Nivel de significancia configurable de la Etapa 1 — DECISIÓN 078.

Valores críticos contra tabla para α = 0,01, 0,05 y 0,10, la verificación
externa de K_N contra Bulletin 17B, y la monotonía: lo que se rechaza con 1 %
se rechaza también con 5 % y con 10 %, nunca al revés. Que α = 0,05 dé lo mismo
que antes lo cubre tests/unit/core/pipeline/test_no_regresion_alfa.py.
"""

import numpy as np
import pytest
from scipy.stats import t as t_dist

from metis.core.etapa1.homogeneity import (
    calcular_cramer,
    calcular_helmert,
    calcular_t_student,
)
from metis.core.etapa1.independence import calcular_anderson, calcular_wald_wolfowitz
from metis.core.etapa1.outliers import calcular_chow
from metis.core.etapa1.significancia import NIVELES_ALFA, validar_alfa, z_bilateral
from metis.core.etapa1.trend import calcular_ks_tendencia, calcular_mann_kendall
from metis.core.pipeline.pipeline_etapa1 import ejecutar_etapa1

Z_TABLA = {0.01: 2.576, 0.05: 1.960, 0.10: 1.645}
KS_TABLA = {0.01: 1.628, 0.05: 1.358, 0.10: 1.224}


def _serie(semilla: int, n: int = 40) -> list[float]:
    return list(np.random.default_rng(semilla).lognormal(4.5, 0.4, n))


@pytest.mark.unit
@pytest.mark.parametrize("alfa", NIVELES_ALFA)
def test_z_bilateral_contra_tabla_normal(alfa):
    assert z_bilateral(alfa) == pytest.approx(Z_TABLA[alfa], abs=5e-4)


@pytest.mark.unit
@pytest.mark.parametrize("alfa", NIVELES_ALFA)
def test_wald_wolfowitz_y_mann_kendall_usan_z_de_alfa(alfa):
    serie = _serie(1)
    ww = calcular_wald_wolfowitz(serie, alfa=alfa)
    mk = calcular_mann_kendall(serie, alfa=alfa)
    assert ww.valor_critico == pytest.approx(Z_TABLA[alfa], abs=5e-4)
    assert mk.valor_critico == pytest.approx(Z_TABLA[alfa], abs=5e-4)
    assert ww.explicacion.terminos["alfa"] == alfa
    assert mk.explicacion.terminos["z_critico"] == mk.valor_critico


@pytest.mark.unit
@pytest.mark.parametrize("alfa", NIVELES_ALFA)
def test_anderson_bandas_con_z_de_alfa(alfa):
    serie = _serie(2)
    r = calcular_anderson(serie, alfa=alfa)
    n = len(serie)
    z = Z_TABLA[alfa]
    for fila in r.explicacion.desglose:
        k = fila["k"]
        assert fila["banda_sup"] == pytest.approx(
            (-1 + z * np.sqrt(n - k - 1)) / (n - k), abs=1e-4
        )
        assert fila["banda_inf"] == pytest.approx(
            (-1 - z * np.sqrt(n - k - 1)) / (n - k), abs=1e-4
        )
    # La tolerancia de lags fuera no depende de α (DECISIONES 012 y 016).
    assert (
        r.explicacion.terminos["tolerancia"]
        == calcular_anderson(serie).explicacion.terminos["tolerancia"]
    )


@pytest.mark.unit
@pytest.mark.parametrize("alfa", NIVELES_ALFA)
def test_t_student_y_cramer_usan_t_de_alfa(alfa):
    serie = _serie(3)
    n = len(serie)
    ts = calcular_t_student(serie, n1=n // 2, n2=n - n // 2, alfa=alfa)
    cr = calcular_cramer(serie, alfa=alfa)
    assert ts.valor_critico == pytest.approx(t_dist.ppf(1 - alfa / 2, df=n - 2))
    assert cr.explicacion.terminos["vc_w1"] == pytest.approx(
        t_dist.ppf(1 - alfa / 2, df=n - 2)
    )
    assert ts.explicacion.terminos["t_critico"] == ts.valor_critico


@pytest.mark.unit
@pytest.mark.parametrize("alfa", NIVELES_ALFA)
def test_ks_contra_tabla(alfa):
    r = calcular_ks_tendencia(_serie(4), alfa=alfa)
    assert r.valor_critico == KS_TABLA[alfa]


@pytest.mark.unit
def test_helmert_no_depende_de_alfa():
    # Ec. III-7: |S − C| ≤ √(n − 1). Ni siquiera recibe α.
    r = calcular_helmert(_serie(5))
    assert r.valor_critico == pytest.approx(np.sqrt(39))


@pytest.mark.unit
@pytest.mark.parametrize(
    ("alfa", "esperado"),
    [(0.05, 2.745), (0.10, 2.563)],  # Bulletin 17B, Apéndice 4, n = 30
)
def test_k_n_de_chow_contra_bulletin_17b(alfa, esperado):
    r = calcular_chow(_serie(6, n=30), "caudal_precipitacion", alfa=alfa)
    assert r.valor_critico == pytest.approx(esperado, abs=5e-3)
    assert r.explicacion.terminos["alfa"] == alfa


def _rechazos(serie: list[float], alfa: float) -> dict[str, bool]:
    r = ejecutar_etapa1(
        serie, "caudal_precipitacion", "anual", list(range(len(serie))), alfa=alfa
    )
    pruebas = r.independencia + r.homogeneidad + r.tendencia + r.atipicos
    return {p.prueba: p.veredicto == "rechazada" for p in pruebas}


@pytest.mark.unit
@pytest.mark.parametrize("semilla", range(40))
def test_monotonia_un_rechazo_con_menor_alfa_se_mantiene_con_mayor(semilla):
    rng = np.random.default_rng(semilla)
    n = int(rng.integers(15, 60))
    # Series con algo de tendencia, persistencia y algún extremo, para que haya
    # rechazos que comparar en los tres niveles.
    base = rng.lognormal(4.5, 0.5, n) * (1 + rng.uniform(-0.02, 0.02) * np.arange(n))
    base = np.convolve(base, [1, rng.uniform(0, 0.8)], mode="same")
    if rng.random() < 0.3:
        base[int(rng.integers(0, n))] *= 4
    serie = [float(v) for v in base]

    r01, r05, r10 = (_rechazos(serie, a) for a in NIVELES_ALFA)
    for prueba in r01:
        if r01[prueba]:
            assert r05[prueba], f"{prueba}: rechaza con 1 % y no con 5 %"
        if r05[prueba]:
            assert r10[prueba], f"{prueba}: rechaza con 5 % y no con 10 %"


@pytest.mark.unit
@pytest.mark.parametrize("alfa", [0.2, 0.0, 0.025, 1])
def test_alfa_fuera_del_conjunto_se_rechaza_en_el_nucleo(alfa):
    with pytest.raises(ValueError):
        validar_alfa(alfa)
    with pytest.raises(ValueError):
        ejecutar_etapa1(
            _serie(7), "caudal_precipitacion", "anual", list(range(40)), alfa=alfa
        )


@pytest.mark.unit
def test_el_resultado_registra_el_alfa_con_que_corrio():
    r = ejecutar_etapa1(
        _serie(8), "caudal_precipitacion", "anual", list(range(40)), alfa=0.10
    )
    assert r.alfa == 0.10
    assert all(
        p.explicacion is None
        or p.prueba == "helmert"
        or p.explicacion.terminos["alfa"] == 0.10
        for p in r.independencia + r.homogeneidad + r.tendencia + r.atipicos
    )
