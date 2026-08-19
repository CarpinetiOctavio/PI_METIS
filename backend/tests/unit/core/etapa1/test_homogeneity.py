import math

import numpy as np
import pytest

from metis.core.etapa1.homogeneity import (
    _cramer_bloque,
    calcular_cramer,
    calcular_helmert,
    calcular_t_student,
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
def test_cramer_particion_custom_bloque_chico_no_ejecutada(serie_facundo):
    # Bloque H1 (plan post-avance, DECISIÓN 036) — con n=40 y n2_pct=2,
    # n_w2 = round(40*0.02) = 1: un solo dato no mide nada (tau_w es la
    # diferencia contra un único valor). Antes de este guard dependía de
    # que _cramer_bloque() tropezara con denom≤0 para no seguir — acá se
    # verifica el guard explícito, no el efecto secundario incidental.
    particion = {"n1_pct": 60, "n2_pct": 2}
    resultado = calcular_cramer(serie_facundo, particion=particion)

    assert resultado.veredicto == "no_ejecutada"
    assert resultado.warning_codigo == "TEST_NOT_EXECUTED_CONDITION"
    assert resultado.estadistico is None
    assert (
        resultado.n2 == 1
    )  # round(40*0.02) — confirma que sí se disparó el guard nuevo, no otra rama


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


# ── explicacion (Bloque D, plan post-avance — DECISIÓN 064) ─────────────────


@pytest.mark.unit
def test_helmert_explicacion_terminos_reproducen_diferencia(serie_facundo):
    resultado = calcular_helmert(serie_facundo)

    assert resultado.explicacion is not None
    assert resultado.explicacion.ecuacion == "III-7"
    terminos = resultado.explicacion.terminos
    assert terminos["s"] - terminos["c"] == pytest.approx(
        resultado.estadistico, abs=1e-9
    )
    assert terminos["s"] + terminos["c"] == terminos["n"] - 1


@pytest.mark.unit
def test_t_student_explicacion_terminos_reproducen_el_estadistico(serie_facundo):
    n1, n2 = 20, 20
    resultado = calcular_t_student(serie_facundo, n1=n1, n2=n2)

    assert resultado.explicacion is not None
    assert resultado.explicacion.ecuacion == "III-8"
    terminos = resultado.explicacion.terminos
    denom = terminos["sp"] * math.sqrt(1 / terminos["n1"] + 1 / terminos["n2"])
    t_reconstruido = (terminos["x1_barra"] - terminos["x2_barra"]) / denom
    assert t_reconstruido == pytest.approx(resultado.estadistico, abs=1e-9)
    assert terminos["nu"] == n1 + n2 - 2


@pytest.mark.unit
def test_cramer_explicacion_incluye_ambos_bloques(serie_facundo):
    resultado = calcular_cramer(serie_facundo)

    assert resultado.explicacion is not None
    assert resultado.explicacion.ecuacion == "III-15"
    terminos = resultado.explicacion.terminos
    # Los dos bloques (60%/30%) viajan siempre, no solo el "binding" que
    # quedó en estadistico/valor_critico — el docente necesita ver por qué
    # aprobada exige que los dos, no solo el reportado, aprueben.
    assert terminos["t_w1"] == pytest.approx(0.2358, abs=1e-3)
    assert terminos["t_w2"] == pytest.approx(0.7859, abs=1e-3)
    assert terminos["t_w2"] == pytest.approx(resultado.estadistico, abs=1e-9)
    assert terminos["n_w1"] == resultado.n1
    assert terminos["n_w2"] == resultado.n2


@pytest.mark.unit
def test_cramer_s_global_cero_sin_explicacion():
    # Serie constante — s_global=0, calcular_cramer retorna no_ejecutada
    # antes de tener ningún término que sustituir.
    resultado = calcular_cramer([50.0] * 20)
    assert resultado.veredicto == "no_ejecutada"
    assert resultado.explicacion is None
