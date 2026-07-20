import pytest


@pytest.fixture
def serie_facundo():
    # Serie real de caudales anuales 1980-2019 provista por Facundo Ganancias.
    # Produce: homogeneidad_ok, sin tendencia, sin atípico,
    # Anderson aprueba (1/13 lags fuera = 7.69% ≤ 10%), Wald con TEST_WARNING_SMALL_SAMPLE.
    # nivel_confianza="con_warnings" por el warning normal de Wald (n=40 ≤ 40).
    # Útil para: tests de homogeneidad, tendencia, Chow, independencia, pipeline.
    # PENDIENTE: resultado de Anderson no validado contra Excel de Facundo.
    return [
        27.5,
        49.4,
        34.8,
        40.9,
        21.1,
        52.1,
        26.0,
        63.9,
        23.8,
        48.2,
        40.6,
        25.9,
        29.3,
        79.4,
        52.2,
        55.9,
        27.1,
        32.6,
        54.0,
        66.7,
        21.2,
        34.2,
        70.2,
        46.7,
        29.5,
        35.4,
        31.9,
        35.9,
        70.9,
        26.3,
        44.9,
        84.6,
        42.9,
        33.6,
        23.1,
        29.3,
        29.1,
        76.3,
        29.3,
        64.0,
    ]


@pytest.fixture
def serie_corta_15():
    # 15 valores — supera mínimo de 10, activa CONTRACT_LENGTH_WARNING.
    return [
        27.5,
        49.4,
        34.8,
        40.9,
        21.1,
        52.1,
        26.0,
        63.9,
        23.8,
        48.2,
        40.6,
        25.9,
        29.3,
        79.4,
        52.2,
    ]
