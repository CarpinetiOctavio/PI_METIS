"""Addendum 01/10/2026 a la DECISIÓN 064 — `Explicacion.desglose` de Anderson y Chow.

El desglose son los valores intermedios que la prueba ya calcula para decidir: tiene
que ser coherente con lo que la prueba reporta (estadístico, lag, conteo de lags fuera
de banda), porque el frontend lo dibuja tal cual sin recalcular nada.
"""

import numpy as np
import pytest

from metis.core.etapa1.independence import Z_CRIT, calcular_anderson
from metis.core.etapa1.outliers import calcular_chow


def _series(serie_facundo):
    rng = np.random.default_rng(7)
    return {
        "facundo": list(serie_facundo),
        "normal_n30": list(rng.normal(100, 20, 30)),
        "autocorrelada_n45": list(np.cumsum(rng.normal(0, 1, 45)) + 50),
    }


@pytest.mark.unit
@pytest.mark.parametrize("nombre", ["facundo", "normal_n30", "autocorrelada_n45"])
def test_anderson_desglose_coherente_con_lo_reportado(serie_facundo, nombre):
    serie = _series(serie_facundo)[nombre]
    resultado = calcular_anderson(serie)
    terminos = resultado.explicacion.terminos
    filas = resultado.explicacion.desglose
    n = len(serie)

    assert [f["k"] for f in filas] == list(range(1, terminos["k_max"] + 1))
    assert set(filas[0]) == {"k", "numerador", "r_k", "banda_inf", "banda_sup", "fuera"}

    # la fila del lag reportado es la del estadístico
    reportada = filas[terminos["k"] - 1]
    assert reportada["r_k"] == resultado.estadistico
    assert reportada["numerador"] == terminos["numerador"]

    # el conteo de la regla del 10 % sale de las mismas filas
    assert sum(f["fuera"] for f in filas) == terminos["lags_fuera"]

    # bandas de la Ec. III-3, y la más restrictiva es el valor crítico reportado
    for f in filas:
        k = f["k"]
        assert f["banda_sup"] == pytest.approx((-1 + Z_CRIT * np.sqrt(n - k - 1)) / (n - k))
        assert f["banda_inf"] == pytest.approx((-1 - Z_CRIT * np.sqrt(n - k - 1)) / (n - k))
        assert f["fuera"] == (f["r_k"] > f["banda_sup"] or f["r_k"] < f["banda_inf"])
    assert min(f["banda_sup"] for f in filas) == resultado.valor_critico


@pytest.mark.unit
@pytest.mark.parametrize(
    "serie",
    [[50.0] * 29 + [5000.0], [12.0, 15.0, 9.0, 30.0, 11.0, 14.0, 13.0, 10.0, 16.0, 12.5]],
    ids=["con-atipico", "sin-atipico"],
)
def test_chow_desglose_una_fila_por_observacion(serie):
    resultado = calcular_chow(serie, "caudal_precipitacion")
    filas = resultado.explicacion.desglose

    # mismas claves que lee frontend/src/routes/results/Etapa1Desglose.tsx
    assert set(filas[0]) == {"i", "x_i", "ln_x_i", "z_i"}
    assert [f["i"] for f in filas] == list(range(1, len(serie) + 1))
    assert [f["x_i"] for f in filas] == serie
    assert all(f["ln_x_i"] == pytest.approx(np.log(f["x_i"])) for f in filas)
    assert max(f["z_i"] for f in filas) == resultado.estadistico


@pytest.mark.unit
def test_chow_no_ejecutada_sin_explicacion():
    assert calcular_chow([0.0] + [10.0] * 14, "caudal_precipitacion").explicacion is None
