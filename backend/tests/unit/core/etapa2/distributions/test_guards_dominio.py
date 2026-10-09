"""
Guards de dominio de las 13 distribuciones de Etapa 2 (B2 del plan del TP de Calidad).

Cada `ajustar()` tiene ramas que devuelven `no_aplicable` o `no_converge` en lugar de un ajuste:
método inexistente, serie degenerada (sin dispersión), valores fuera del dominio. Antes de este
archivo casi ninguna estaba ejercitada (cobertura de decisión del backend en 76,7 %). La propiedad
que se prueba es la de `statistical-pipeline.md`, "Casos especiales de Etapa 2": **ningún caso
especial detiene el pipeline**. Ante una entrada que no admite ajuste, la distribución responde un
estado no-OK con `parametros=None`, nunca una excepción ni un ajuste con números inválidos.

Técnica: clases de equivalencia sobre la serie de entrada (válida, constante, con no positivos) y
sobre el método (aplicable, inexistente). Estructura Arrange-Act-Assert explícita.
"""

import importlib
import math

import numpy as np
import pytest

from metis.core.etapa2.eea import calcular_eea
from metis.core.etapa2.types import STATUS_NO_APLICABLE, STATUS_OK

MODULOS = [
    "uniforme",
    "normal",
    "gumbel",
    "gve",
    "lognormal2p",
    "lognormal3p",
    "logpearson3",
    "gamma2p",
    "gamma3p",
    "exponencial_beta",
    "exponencial_x0_beta",
    "gen_pareto",
    "gen_exponencial",
]

SERIE_CONSTANTE = np.full(20, 50.0)
SERIE_CON_NO_POSITIVOS = np.array(
    [-3.0, 0.0, 12.0, 15.0, 18.0, 22.0, 30.0, 41.0, 55.0, 70.0]
)

# Las que no admiten valores <= 0 por definición (DISABLED_WITH_ZEROS/NEGATIVES en
# distributions/__init__.py). Su ajustar() lo chequea por su cuenta, además del pipeline.
NO_ADMITEN_NO_POSITIVOS = ["lognormal2p", "logpearson3", "gamma2p", "exponencial_beta"]


def _modulo(nombre):
    return importlib.import_module(f"metis.core.etapa2.distributions.{nombre}")


def _metodos(nombre):
    return [
        pytest.param(nombre, m, id=f"{nombre}-{m}")
        for m in _modulo(nombre).METODOS_APLICABLES
    ]


def _assert_sin_ajuste_invalido(resultado):
    """Un estado no-OK no lleva parámetros; uno OK los lleva todos finitos."""
    if resultado.status == STATUS_OK:
        assert resultado.parametros
        assert all(math.isfinite(v) for v in resultado.parametros.values())
    else:
        assert resultado.parametros is None


@pytest.mark.unit
@pytest.mark.parametrize("nombre", MODULOS)
def test_metodo_inexistente_responde_no_aplicable(nombre):
    # Arrange
    serie = np.linspace(40.0, 160.0, 25)

    # Act
    resultado = _modulo(nombre).ajustar(serie, "metodo_que_no_existe")

    # Assert
    assert resultado.status == STATUS_NO_APLICABLE
    assert resultado.parametros is None


@pytest.mark.unit
@pytest.mark.parametrize(
    ("nombre", "metodo"), [p for n in MODULOS for p in _metodos(n)]
)
def test_serie_constante_no_lanza_ni_devuelve_parametros_invalidos(nombre, metodo):
    # Arrange: sin dispersión, S = 0 — divide por cero en casi todas las fórmulas

    # Act
    with np.errstate(all="ignore"):
        resultado = _modulo(nombre).ajustar(SERIE_CONSTANTE.copy(), metodo)

    # Assert
    _assert_sin_ajuste_invalido(resultado)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("nombre", "metodo"), [p for n in NO_ADMITEN_NO_POSITIVOS for p in _metodos(n)]
)
def test_serie_con_no_positivos_responde_no_aplicable(nombre, metodo):
    # Arrange
    serie = SERIE_CON_NO_POSITIVOS.copy()

    # Act
    resultado = _modulo(nombre).ajustar(serie, metodo)

    # Assert
    assert resultado.status == STATUS_NO_APLICABLE
    assert resultado.parametros is None


@pytest.mark.unit
@pytest.mark.parametrize(
    ("nombre", "metodo"), [p for n in MODULOS for p in _metodos(n)]
)
def test_serie_con_no_positivos_nunca_lanza(nombre, metodo):
    # Arrange: las de 3 parámetros deciden por su cuenta (x0 >= min(serie), DECISIÓN 073)
    serie = SERIE_CON_NO_POSITIVOS.copy()

    # Act
    with np.errstate(all="ignore"):
        resultado = _modulo(nombre).ajustar(serie, metodo)

    # Assert
    _assert_sin_ajuste_invalido(resultado)


@pytest.mark.unit
def test_gamma2p_momentos_l_con_cv_l_alto_usa_la_rama_de_tau2_mayor_a_un_medio():
    # Arrange: casi todos los valores chicos y uno enorme → τ2 = λ2/λ1 ≥ 0,5 (IV-132/133)
    serie = np.array([1.0] * 19 + [5000.0])

    # Act
    resultado = _modulo("gamma2p").ajustar(serie, "ml")

    # Assert
    _assert_sin_ajuste_invalido(resultado)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("n", "mp"),
    [pytest.param(2, 2, id="n-igual-a-mp"), pytest.param(2, 3, id="n-menor-a-mp")],
)
def test_calcular_eea_con_n_no_mayor_que_los_parametros_es_infinito(n, mp):
    # Arrange: el denominador n − mp de IV-263 no es positivo
    observados = np.arange(1.0, n + 1)
    estimados = observados + 1.0

    # Act
    eea = calcular_eea(observados, estimados, mp)

    # Assert
    assert eea == float("inf")
