"""B8 del TP de Calidad — tablas de decisión (docs/calidad/casos-de-prueba.md, casos TD-xx).

Un caso por columna de cada tabla: la combinación de condiciones y la acción esperada. Las
reglas salen de statistical-pipeline.md ("Jerarquía", "Niveles de homogeneidad", "Estado de
confianza global", "Condiciones para entrar a Etapa 2").
"""

import numpy as np
import pytest

from metis.core.etapa1.homogeneity import determinar_nivel_homogeneidad
from metis.core.etapa1.independence import determinar_nivel_independencia
from metis.core.etapa2.distributions import DISABLED_WITH_NEGATIVES, DISABLED_WITH_ZEROS
from metis.core.etapa2.types import STATUS_DISABLED_NEGATIVES, STATUS_DISABLED_ZEROS
from metis.core.pipeline import ejecutar_etapa1, ejecutar_etapa2
from metis.core.types import TestResult
from metis.services.analysis_service import simular_exclusion


def _resultado(
    prueba: str, veredicto: str, warning_codigo: str | None = None
) -> TestResult:
    return TestResult(
        prueba=prueba,
        estadistico=0.5,
        valor_critico=2.0,
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel="normal" if warning_codigo else None,
    )


A, R = "aprobada", "rechazada"


# ── TD-01: independencia (Anderson manda, Wald-Wolfowitz verifica) ──────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    ("anderson", "wald", "nivel", "critico"),
    [
        (A, A, "independiente", False),
        (A, R, "independiente", False),
        (R, A, "dependiente", True),
        (R, R, "dependiente", True),
    ],
    ids=["TD-01 c1 A+ W+", "TD-01 c2 A+ W-", "TD-01 c3 A- W+", "TD-01 c4 A- W-"],
)
def test_tabla_independencia(anderson, wald, nivel, critico):
    obtenido, warnings = determinar_nivel_independencia(
        _resultado("anderson", anderson), _resultado("wald_wolfowitz", wald)
    )

    assert obtenido == nivel
    assert ("TEST_CRITICAL_INDEPENDENCE" in [w.codigo for w in warnings]) is critico


# ── TD-02: homogeneidad (Cramer manda; Helmert y t de Student degradan a warning) ─


@pytest.mark.unit
@pytest.mark.parametrize(
    ("cramer", "helmert", "t_student", "nivel", "codigo"),
    [
        (A, A, A, "homogeneidad_ok", None),
        (A, R, A, "homogeneidad_warning", "TEST_WARNING_HOMOGENEITY"),
        (A, A, R, "homogeneidad_warning", "TEST_WARNING_HOMOGENEITY"),
        (A, R, R, "homogeneidad_warning", "TEST_WARNING_HOMOGENEITY"),
        (R, A, A, "homogeneidad_critica", "TEST_CRITICAL_HOMOGENEITY"),
        (R, R, A, "homogeneidad_critica", "TEST_CRITICAL_HOMOGENEITY"),
        (R, A, R, "homogeneidad_critica", "TEST_CRITICAL_HOMOGENEITY"),
        (R, R, R, "homogeneidad_critica", "TEST_CRITICAL_HOMOGENEITY"),
    ],
    ids=[f"TD-02 c{i}" for i in range(1, 9)],
)
def test_tabla_homogeneidad(cramer, helmert, t_student, nivel, codigo):
    obtenido, warnings = determinar_nivel_homogeneidad(
        _resultado("helmert", helmert),
        _resultado("t_student", t_student),
        _resultado("cramer", cramer),
    )

    assert obtenido == nivel
    assert [w.codigo for w in warnings] == ([codigo] if codigo else [])


# ── TD-03: nivel de confianza global ─────────────────────────────────────────────
# Columnas c1 (bloqueante → rechazado), c2 (crítico → con_warnings) y c4 (sin warnings →
# validado) las cubren tests existentes (ver el documento). Falta la c3: solo warnings normales.


@pytest.mark.unit
def test_tabla_confianza_c3_solo_warnings_normales_da_con_warnings():
    # serie_corta_15 de tests/unit/core/conftest.py: longitud, muestra chica y homogeneidad,
    # los tres de nivel normal; Anderson y Cramer aprueban.
    serie = [
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

    result = ejecutar_etapa1(
        serie=serie, tipo_variable="otro", resolucion_temporal="anual"
    )

    assert result.warnings, "el caso necesita al menos un warning"
    assert all(w.nivel == "normal" for w in result.warnings)
    assert result.nivel_confianza == "con_warnings"


# ── TD-04: entrada a Etapa 2 (etapas × resultado de Etapa 1) ────────────────────

# 12 años: excluir 3 deja 9 datos y Etapa 1 queda rechazada (< 10).
SERIE = [60.0 + (i * 7) % 40 for i in range(12)]
ANIOS = list(range(2000, 2012))


@pytest.mark.unit
@pytest.mark.parametrize(
    ("etapas", "excluidos", "rechazado", "corre_etapa2"),
    [
        ([1], [], False, False),
        ([1, 2], [], False, True),
        ([1], [0, 1, 2], True, False),
        ([1, 2], [0, 1, 2], True, False),
    ],
    ids=[
        "TD-04 c1 etapas=1 ok",
        "TD-04 c2 etapas=1,2 ok",
        "TD-04 c3 etapas=1 rechazado",
        "TD-04 c4 etapas=1,2 rechazado",
    ],
)
def test_tabla_entrada_a_etapa2(etapas, excluidos, rechazado, corre_etapa2):
    resultado = simular_exclusion(
        serie=SERIE,
        anios=ANIOS,
        tipo_variable="caudal_precipitacion",
        cramer_particion="default",
        indices_excluidos=excluidos,
        etapas=etapas,
    )

    assert (resultado["etapa1"]["nivel_confianza"] == "rechazado") is rechazado
    assert (resultado["etapa2"] is not None) is corre_etapa2


# ── TD-05: estado de las distribuciones ante ceros y negativos ──────────────────
# Columnas c2 (solo ceros), c3 (solo negativos) y c4 (ambos) las cubre
# tests/unit/core/pipeline/test_disabled_negatives.py. Falta la c1: sin ceros ni negativos,
# ninguna de las deshabilitables queda deshabilitada.


@pytest.mark.unit
def test_tabla_distribuciones_c1_sin_ceros_ni_negativos_no_deshabilita_ninguna():
    serie = np.array([60.0 + (i * 7) % 40 for i in range(30)])

    ranking = {d.distribucion: d for d in ejecutar_etapa2(serie).ranking}

    for nombre in DISABLED_WITH_ZEROS | DISABLED_WITH_NEGATIVES:
        estados = {m.status for m in ranking[nombre].metodos}
        assert not estados & {STATUS_DISABLED_ZEROS, STATUS_DISABLED_NEGATIVES}, nombre
