import numpy as np
import pytest

from metis.core.pipeline import ejecutar_etapa1


# Serie que produce nivel_confianza="validado" — todas las pruebas aprueban.
# numpy seed=9, uniform(10, 100), n=50. Seed 1 fue descartada (Helmert rechaza
# con criterio directo |S-C| ≤ √(n-1): margen=0). Seed 9: margen=6 (holgado).
# n=50 > 40 evita TEST_WARNING_SMALL_SAMPLE de Wald-Wolfowitz.
# Verificada con smoke test antes de incorporar como constante.
_rng = np.random.default_rng(seed=9)
SERIE_VALIDADA = _rng.uniform(10, 100, size=50).tolist()


# ── Pipeline bloqueante ───────────────────────────────────────────────────────


@pytest.mark.unit
def test_serie_bloqueante_detiene_pipeline():
    serie = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]
    resultado = ejecutar_etapa1(serie, "otro", "anual")
    assert resultado.nivel_confianza == "rechazado"
    assert resultado.descriptive is None
    assert resultado.independencia == []
    assert resultado.homogeneidad == []
    assert resultado.tendencia == []
    assert resultado.atipicos == []


@pytest.mark.unit
def test_sin_resolucion_temporal_detiene_pipeline():
    serie = [float(i) for i in range(10, 20)]
    resultado = ejecutar_etapa1(serie, "otro", resolucion_temporal=None)
    assert resultado.nivel_confianza == "rechazado"
    assert resultado.independencia == []
    assert resultado.homogeneidad == []
    assert resultado.tendencia == []
    assert resultado.atipicos == []


@pytest.mark.unit
def test_strings_con_menos_de_10_numericos_bloqueante():
    # 5 floats + 5 strings — el filtrado ocurre antes de validar el mínimo de 10.
    serie = [10.0, 20.0, 30.0, 40.0, 50.0, "a", "b", "c", "d", "e"]
    resultado = ejecutar_etapa1(serie, "otro", "anual")
    assert resultado.nivel_confianza == "rechazado"
    assert resultado.independencia == []


# ── Pipeline completo ─────────────────────────────────────────────────────────


@pytest.mark.unit
def test_serie_valida_nivel_confianza_validado():
    # SERIE_VALIDADA: numpy seed=1, n=50 — todas las pruebas aprueban sin warnings.
    # serie_facundo no sirve para este caso: Anderson rechaza (dependiente).
    resultado = ejecutar_etapa1(SERIE_VALIDADA, "otro", "anual")
    assert resultado.nivel_confianza == "validado"
    assert resultado.independencia[0].prueba == "anderson"
    assert resultado.independencia[0].veredicto == "aprobada"
    assert resultado.homogeneidad[0].prueba == "helmert"
    assert resultado.homogeneidad[0].veredicto == "aprobada"
    assert resultado.tendencia[0].prueba == "mann_kendall"
    assert resultado.tendencia[0].veredicto == "aprobada"
    assert resultado.atipicos[0].prueba == "chow"
    assert resultado.atipicos[0].veredicto == "aprobada"
    assert resultado.descriptive is not None


@pytest.mark.unit
def test_warning_critico_produce_con_warnings(serie_facundo):
    # serie_facundo: Wald n=40 ≤ 40 → TEST_WARNING_SMALL_SAMPLE → con_warnings.
    resultado = ejecutar_etapa1(serie_facundo, "caudal_precipitacion", "anual")
    assert resultado.nivel_confianza == "con_warnings"


# ── Comportamientos específicos ───────────────────────────────────────────────


@pytest.mark.unit
def test_ceros_en_caudal_chow_no_ejecutada_pipeline_continua():
    # Ceros en caudal_precipitacion → Chow no ejecutada, pero el pipeline continúa.
    serie = [0.0, 5.0] + [float(i) for i in range(10, 59)]
    resultado = ejecutar_etapa1(serie, "caudal_precipitacion", "anual")
    assert resultado.nivel_confianza == "con_warnings"
    assert len(resultado.atipicos) == 1
    assert resultado.atipicos[0].veredicto == "no_ejecutada"
    assert resultado.atipicos[0].warning_codigo == "TEST_NOT_EXECUTED_ZEROS"


@pytest.mark.unit
def test_strings_filtrados_antes_de_pruebas():
    # 30 floats + strings mezclados — pruebas reciben solo los numéricos.
    serie = [float(i) for i in range(10, 40)] + ["x", "y", "z"]
    resultado = ejecutar_etapa1(serie, "otro", "anual")
    codigos = [w.codigo for w in resultado.warnings]
    assert "CONTRACT_NON_NUMERIC_VALUES" in codigos
    assert resultado.independencia[0].prueba == "anderson"
    assert resultado.independencia[0].estadistico is not None
    assert resultado.homogeneidad[0].prueba == "helmert"
    assert resultado.homogeneidad[0].estadistico is not None


@pytest.mark.unit
def test_cramer_siempre_incluye_n1_y_n2(serie_facundo):
    resultado = ejecutar_etapa1(serie_facundo, "caudal_precipitacion", "anual")
    cramer = next(t for t in resultado.homogeneidad if t.prueba == "cramer")
    assert cramer.n1 is not None
    assert cramer.n2 is not None
    assert cramer.n1 > 0
    assert cramer.n2 > 0


@pytest.mark.unit
def test_t_student_usa_particion_mitad_mitad_no_particion_cramer():
    # Regresión de cableado: t-Student exige n1=n2=n/2 (III-8), independiente
    # de la partición 60%/30% que usa Cramer (cramer_particion). Antes del fix,
    # pipeline.py reutilizaba por error la partición de Cramer (n1=14, n2=7
    # para esta serie) como argumento de calcular_t_student.
    # Serie real est_02 (Vado de Río Seco — Río Barrancas, n=24), tesis Facundo:
    # t esperado=-1.76, GL=22, valor_critico=2.0739, veredicto="aprobada".
    serie_est02 = [
        98.0, 44.0, 97.0, 52.0, 90.0, 247.0, 191.0, 54.0, 112.0, 42.0,
        60.0, 157.0, 61.0, 45.0, 91.0, 257.0, 458.0, 381.0, 251.0, 151.0,
        122.0, 58.0, 145.0, 158.0,
    ]
    resultado = ejecutar_etapa1(serie_est02, "otro", "anual")
    t_student = next(t for t in resultado.homogeneidad if t.prueba == "t_student")

    assert t_student.n1 == 12
    assert t_student.n2 == 12
    assert t_student.estadistico == pytest.approx(-1.7643, abs=1e-3)
    assert t_student.valor_critico == pytest.approx(2.0739, abs=1e-3)
    assert t_student.veredicto == "aprobada"
