"""
Tests unitarios de core/etapa2/design_events.py (Bloque A4 del plan de
implementación de Etapa 2).
"""

import pytest

from metis.core.etapa2.design_events import calcular_eventos_diseno
from metis.core.etapa2.distributions import gumbel


@pytest.mark.unit
def test_calcular_eventos_diseno_gumbel_verificado_a_mano():
    # xT = mu - alpha*ln(-ln(F)), F = 1 - 1/T — Ec. IV-199, calculado a mano
    # (ver comentario del comando usado, no repetido acá para no duplicar
    # la fuente de verdad: es exactamente la fórmula del docstring de
    # gumbel.cuantil()).
    parametros = {"mu": 100.0, "alpha": 20.0}
    periodos_retorno = [2, 10, 100]

    eventos = calcular_eventos_diseno(gumbel, parametros, periodos_retorno)

    esperados = [107.33025841163328, 145.00734654624893, 192.0029845355316]
    assert [e.periodo_retorno for e in eventos] == periodos_retorno
    for evento, esperado in zip(eventos, esperados, strict=True):
        assert evento.valor == pytest.approx(esperado, rel=1e-9)


@pytest.mark.unit
def test_calcular_eventos_diseno_respeta_orden_de_periodos_retorno():
    parametros = {"mu": 50.0, "alpha": 10.0}
    periodos_retorno = [500, 2, 100, 5]

    eventos = calcular_eventos_diseno(gumbel, parametros, periodos_retorno)

    assert [e.periodo_retorno for e in eventos] == periodos_retorno


class _ModuloQueFallaParaUnT:
    """Stub — falla para un T puntual (F=0.5), simulando una distribución
    cuyo cuantil() no puede resolver un período de retorno particular sin
    afectar al resto. No usa ninguna distribución real: aísla la lógica de
    resiliencia de calcular_eventos_diseno() del comportamiento numérico
    real de las 13 distribuciones (ya cubierto por sus propios tests)."""

    @staticmethod
    def cuantil(p: float, parametros: dict) -> float:
        if p == 0.5:
            raise ValueError("simulado: no converge para este T")
        return p * 1000  # valor arbitrario, solo importa que no explote


@pytest.mark.unit
def test_un_periodo_que_falla_no_tumba_el_resto():
    periodos_retorno = [2, 10, 100]  # T=2 -> F=0.5, el que falla

    eventos = calcular_eventos_diseno(
        _ModuloQueFallaParaUnT, parametros={}, periodos_retorno=periodos_retorno
    )

    assert len(eventos) == 3
    assert eventos[0].periodo_retorno == 2
    assert eventos[0].valor is None
    assert eventos[1].valor == pytest.approx(0.9 * 1000)
    assert eventos[2].valor == pytest.approx(0.99 * 1000)


@pytest.mark.unit
def test_f_se_calcula_como_1_menos_1_sobre_t():
    valores_f_recibidos = []

    class _ModuloQueRegistraF:
        @staticmethod
        def cuantil(p: float, parametros: dict) -> float:
            valores_f_recibidos.append(p)
            return 0.0

    calcular_eventos_diseno(_ModuloQueRegistraF, {}, [2, 4, 5])

    assert valores_f_recibidos == pytest.approx([0.5, 0.75, 0.8])


@pytest.mark.unit
def test_lista_vacia_de_periodos_retorno_no_falla():
    assert calcular_eventos_diseno(gumbel, {"mu": 0.0, "alpha": 1.0}, []) == []
