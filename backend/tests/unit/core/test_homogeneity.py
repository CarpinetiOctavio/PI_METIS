import math

import pytest

from metis.core.homogeneity import (
    calcular_cramer,
    determinar_nivel_homogeneidad,
)
from metis.core.types import TestResult


def _make_result(
    prueba: str, veredicto: str, warning_codigo: str | None = None
) -> TestResult:
    return TestResult(
        prueba=prueba,
        estadistico=0.5,
        valor_critico=2.0,
        veredicto=veredicto,
        warning_codigo=warning_codigo,
        warning_nivel="critico"
        if warning_codigo == "TEST_CRITICAL_HOMOGENEITY"
        else ("normal" if warning_codigo else None),
        n1=10,
        n2=5,
    )


# ── determinar_nivel_homogeneidad ─────────────────────────────────────────────


@pytest.mark.unit
def test_cramer_rechaza_nivel_homogeneidad_critica():
    # Cramer manda — aunque Helmert y t-Student aprueben.
    helmert = _make_result("helmert", "aprobada")
    t_student = _make_result("t_student", "aprobada")
    cramer = _make_result("cramer", "rechazada", "TEST_CRITICAL_HOMOGENEITY")

    nivel, warnings = determinar_nivel_homogeneidad(helmert, t_student, cramer)

    assert nivel == "homogeneidad_critica"
    criticos = [w for w in warnings if w.codigo == "TEST_CRITICAL_HOMOGENEITY"]
    assert len(criticos) == 1
    assert criticos[0].nivel == "critico"


@pytest.mark.unit
def test_helmert_rechaza_nivel_homogeneidad_warning():
    helmert = _make_result("helmert", "rechazada", "TEST_WARNING_HOMOGENEITY")
    t_student = _make_result("t_student", "aprobada")
    cramer = _make_result("cramer", "aprobada")

    nivel, warnings = determinar_nivel_homogeneidad(helmert, t_student, cramer)

    assert nivel == "homogeneidad_warning"
    codigos = [w.codigo for w in warnings]
    assert "TEST_WARNING_HOMOGENEITY" in codigos


@pytest.mark.unit
def test_t_student_rechaza_nivel_homogeneidad_warning():
    helmert = _make_result("helmert", "aprobada")
    t_student = _make_result("t_student", "rechazada", "TEST_WARNING_HOMOGENEITY")
    cramer = _make_result("cramer", "aprobada")

    nivel, warnings = determinar_nivel_homogeneidad(helmert, t_student, cramer)

    assert nivel == "homogeneidad_warning"
    codigos = [w.codigo for w in warnings]
    assert "TEST_WARNING_HOMOGENEITY" in codigos


@pytest.mark.unit
def test_todas_aprueban_nivel_homogeneidad_ok():
    helmert = _make_result("helmert", "aprobada")
    t_student = _make_result("t_student", "aprobada")
    cramer = _make_result("cramer", "aprobada")

    nivel, warnings = determinar_nivel_homogeneidad(helmert, t_student, cramer)

    assert nivel == "homogeneidad_ok"
    codigos = [w.codigo for w in warnings]
    assert "TEST_CRITICAL_HOMOGENEITY" not in codigos
    assert "TEST_WARNING_HOMOGENEITY" not in codigos


# ── calcular_cramer ───────────────────────────────────────────────────────────


@pytest.mark.unit
def test_cramer_incluye_n1_y_n2(serie_facundo):
    resultado = calcular_cramer(serie_facundo)
    assert resultado.n1 is not None
    assert resultado.n2 is not None
    assert resultado.n1 > 0
    assert resultado.n2 > 0


@pytest.mark.unit
def test_cramer_particion_custom(serie_facundo):
    particion = {"n1_pct": 70, "n2_pct": 20}
    resultado = calcular_cramer(serie_facundo, particion=particion)

    n = len(serie_facundo)
    n1_esperado = math.ceil(n * 70 / 100)
    n2_esperado = min(math.ceil(n * 20 / 100), n - n1_esperado)

    assert resultado.n1 == n1_esperado
    assert resultado.n2 == n2_esperado
