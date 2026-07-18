import numpy as np
import pytest

from metis.core.pipeline import ejecutar_pipeline_completo

# Misma serie que SERIE_VALIDADA en test_pipeline_etapa1.py — numpy seed=9,
# uniform(10, 100), n=50. Todas las pruebas de Etapa 1 aprueban sin warnings.
_rng = np.random.default_rng(seed=9)
SERIE_VALIDADA = _rng.uniform(10, 100, size=50).tolist()

# Serie estrictamente creciente — autocorrelación ≈ 1 en todos los lags.
# Produce nivel_confianza="con_warnings" con warnings CRÍTICOS reales
# (Anderson rechaza -> TEST_CRITICAL_INDEPENDENCE; Cramer rechaza ->
# TEST_CRITICAL_HOMOGENEITY). Sirve para probar que un warning crítico
# no bloquea Etapa 2 — solo "rechazado" lo hace. Verificada con smoke test.
SERIE_CON_WARNINGS_CRITICO = [float(i) for i in range(1, 51)]

# n=8 < 10 -> bloqueante por contrato -> nivel_confianza="rechazado".
SERIE_RECHAZADA = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]


@pytest.mark.unit
def test_validado_corre_etapa2():
    resultado = ejecutar_pipeline_completo(SERIE_VALIDADA, "otro", "anual")
    assert resultado.etapa1.nivel_confianza == "validado"
    assert resultado.etapa2 is not None
    assert len(resultado.etapa2.ranking) == 13


@pytest.mark.unit
def test_con_warnings_critico_corre_etapa2_igual():
    resultado = ejecutar_pipeline_completo(SERIE_CON_WARNINGS_CRITICO, "otro", "anual")
    assert resultado.etapa1.nivel_confianza == "con_warnings"
    assert any(w.nivel == "critico" for w in resultado.etapa1.warnings)
    # RF-GEN-P-03: ningún nivel de warning bloquea el pipeline completo —
    # solo "rechazado" lo hace. Etapa 2 debe correr igual.
    assert resultado.etapa2 is not None
    assert len(resultado.etapa2.ranking) == 13


@pytest.mark.unit
def test_rechazado_no_corre_etapa2():
    resultado = ejecutar_pipeline_completo(SERIE_RECHAZADA, "otro", "anual")
    assert resultado.etapa1.nivel_confianza == "rechazado"
    assert resultado.etapa2 is None


@pytest.mark.unit
def test_tiene_ceros_se_deriva_de_la_serie_filtrada():
    # Ceros en caudal_precipitacion -> Chow no_ejecutada, pero el pipeline
    # continúa (con_warnings) y Etapa 2 debe recibir tiene_ceros=True,
    # deshabilitando las distribuciones marcadas (ver DISABLED_WITH_ZEROS).
    serie = [0.0, 5.0] + [float(i) for i in range(10, 59)]
    resultado = ejecutar_pipeline_completo(serie, "caudal_precipitacion", "anual")

    assert resultado.etapa1.nivel_confianza == "con_warnings"
    assert resultado.etapa2 is not None

    from metis.core.etapa2.distributions import DISABLED_WITH_ZEROS
    from metis.core.etapa2.types import STATUS_DISABLED_ZEROS

    deshabilitadas = [
        d for d in resultado.etapa2.ranking if d.distribucion in DISABLED_WITH_ZEROS
    ]
    assert len(deshabilitadas) == len(DISABLED_WITH_ZEROS)
    for dist in deshabilitadas:
        assert all(m.status == STATUS_DISABLED_ZEROS for m in dist.metodos)


@pytest.mark.unit
def test_strings_no_numericos_no_rompen_derivacion_de_ceros():
    # valores_numericos debe filtrarse antes de convertir a np.ndarray para
    # Etapa 2 — igual que ya hace ejecutar_etapa1 internamente para sus
    # propias pruebas (ver DECISIÓN documentada en pipeline_etapa1.py).
    serie = [float(i) for i in range(10, 40)] + ["x", "y", "z"]
    resultado = ejecutar_pipeline_completo(serie, "otro", "anual")
    assert resultado.etapa2 is not None
    assert len(resultado.etapa2.ranking) == 13
