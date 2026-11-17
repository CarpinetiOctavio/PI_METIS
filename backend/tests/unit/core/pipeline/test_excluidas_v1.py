"""Generalizada de Pareto fuera del cálculo de la v1 (addendum del 29/10/2026 a la
DECISIÓN 074).

La DECISIÓN 074 la dejaba en el ranking, al final y sin poder elegirse. Con la
respuesta de Facundo del 29/10/2026 sale del cálculo: ejecutar_etapa2() la
saltea. El caso que motivó la 074 es est_02 (Vado de Río Seco), donde gen_pareto
salía primera con eventos de diseño inflados entre un 32 % y un 47 %
(hallazgo-gen-pareto-convenciones.md). Su módulo sigue en el repo para la v2.
"""

import numpy as np
import pytest

from metis.core.etapa2.distributions import (
    EXCLUIDAS_V1,
    PENDIENTES_VALIDACION,
    gen_pareto,
)
from metis.core.pipeline import ejecutar_etapa2

# est_02 tal como la transcribe docs/auditoria/regresion/regresion-pipeline/.
EST_02 = np.array(
    [98.0, 44.0, 97.0, 52.0, 90.0, 247.0, 191.0, 54.0, 112.0, 42.0, 60.0, 157.0,
     61.0, 45.0, 91.0, 257.0, 458.0, 381.0, 251.0, 151.0, 122.0, 58.0, 145.0, 158.0]
)  # fmt: skip


@pytest.mark.unit
def test_gen_pareto_esta_excluida_y_ya_no_pendiente():
    assert EXCLUIDAS_V1 == frozenset({"gen_pareto"})
    assert PENDIENTES_VALIDACION == frozenset()


@pytest.mark.unit
def test_est_02_el_ranking_no_trae_a_gen_pareto():
    ranking = ejecutar_etapa2(EST_02, tiene_ceros=False).ranking

    assert len(ranking) == 12
    assert all(d.distribucion != "gen_pareto" for d in ranking)
    assert all(not d.pendiente_validacion for d in ranking)


@pytest.mark.unit
def test_est_02_el_ranking_de_las_12_sigue_ordenado_por_eea():
    ranking = ejecutar_etapa2(EST_02, tiene_ceros=False).ranking

    con_eea = [d.mejor_eea for d in ranking if d.mejor_eea is not None]
    assert con_eea == sorted(con_eea)
    # las sin ajuste siguen después de las que ajustan
    sin_eea = [i for i, d in enumerate(ranking) if d.mejor_eea is None]
    if sin_eea:
        assert min(sin_eea) == len(con_eea)


@pytest.mark.unit
def test_el_modulo_de_gen_pareto_sigue_disponible_para_la_v2():
    # Sale del pipeline, no del repo: el módulo se puede llamar directo.
    resultado = gen_pareto.ajustar(EST_02, "momentos")
    assert resultado.metodo == "momentos"
