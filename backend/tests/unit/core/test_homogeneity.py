import math

import numpy as np
import pytest

from metis.core.homogeneity import (
    _cramer_bloque,
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


@pytest.mark.unit
def test_cramer_tau_y_t_intermedios_ec_iii15(serie_facundo):
    # Verifica valores intermedios contra cálculo manual con serie_facundo (n=40).
    # n_w1=ceil(40*0.60)=24, n_w2=min(ceil(40*0.30),16)=12.
    # tau_w = (x̄_w - x̄_global) / S_global  (Ec. III-13/14)
    # t_w = sqrt(n_w*(n-2)/denom) * |tau_w|  (Ec. III-15), denom = n - n_w*(1+tau_w²)
    arr = np.array(serie_facundo, dtype=float)
    n = len(arr)
    media_global = float(np.mean(arr))
    s_global = float(np.std(arr, ddof=1))

    n_w1, n_w2 = 24, 12
    bloque1 = _cramer_bloque(arr, n_w1, media_global, s_global)
    bloque2 = _cramer_bloque(arr, n_w2, media_global, s_global)

    assert bloque1 is not None
    assert bloque2 is not None

    tau_w1, t_w1 = bloque1
    tau_w2, t_w2 = bloque2

    assert tau_w1 == pytest.approx(0.031216, abs=1e-4)
    assert tau_w2 == pytest.approx(0.193171, abs=1e-4)
    assert t_w1 == pytest.approx(0.2358, abs=1e-3)
    assert t_w2 == pytest.approx(0.7859, abs=1e-3)


@pytest.mark.unit
def test_cramer_estadistico_es_t_w2_binding(serie_facundo):
    # t_w2 > t_w1 en términos de ratio t/vc → t_w2 es el estadístico reportado.
    resultado = calcular_cramer(serie_facundo)

    assert resultado.estadistico == pytest.approx(0.7859, abs=1e-3)
    assert resultado.veredicto == "aprobada"
    assert resultado.n1 == 24
    assert resultado.n2 == 12
