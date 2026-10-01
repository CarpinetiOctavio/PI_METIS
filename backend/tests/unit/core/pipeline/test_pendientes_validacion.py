"""DECISIÓN 074 — distribuciones pendientes de validación (hoy, gen_pareto).

Se calculan igual que antes (ningún EEA ni parámetro cambia), pero van al final
del ranking: aunque tengan el menor EEA, no pueden encabezarlo. El caso que lo
motiva es est_02 (Vado de Río Seco), donde gen_pareto salía primera con eventos de
diseño inflados entre un 32 % y un 47 % (hallazgo-gen-pareto-convenciones.md).
"""

import numpy as np
import pytest

from metis.core.etapa2.distributions import PENDIENTES_VALIDACION
from metis.core.pipeline import ejecutar_etapa2

# est_02 tal como la transcribe docs/auditoria/regresion/regresion-pipeline/.
EST_02 = np.array(
    [98.0, 44.0, 97.0, 52.0, 90.0, 247.0, 191.0, 54.0, 112.0, 42.0, 60.0, 157.0,
     61.0, 45.0, 91.0, 257.0, 458.0, 381.0, 251.0, 151.0, 122.0, 58.0, 145.0, 158.0]
)  # fmt: skip


@pytest.mark.unit
def test_gen_pareto_esta_marcada_como_pendiente():
    assert PENDIENTES_VALIDACION == frozenset({"gen_pareto"})


@pytest.mark.unit
def test_est_02_gen_pareto_tiene_el_menor_eea_pero_queda_ultima():
    ranking = ejecutar_etapa2(EST_02, tiene_ceros=False).ranking
    pareto = next(d for d in ranking if d.distribucion == "gen_pareto")

    # sin la regla, encabezaría el ranking: su EEA es el menor de las 13
    menor = min(d.mejor_eea for d in ranking if d.mejor_eea is not None)
    assert pareto.mejor_eea == menor

    assert ranking[-1] is pareto
    assert pareto.pendiente_validacion is True
    assert all(not d.pendiente_validacion for d in ranking[:-1])


@pytest.mark.unit
def test_est_02_el_orden_relativo_de_las_otras_12_no_cambia():
    ranking = ejecutar_etapa2(EST_02, tiene_ceros=False).ranking
    otras = [d for d in ranking if not d.pendiente_validacion]

    assert len(otras) == 12
    con_eea = [d.mejor_eea for d in otras if d.mejor_eea is not None]
    assert con_eea == sorted(con_eea)
    # las sin ajuste siguen después de las que ajustan
    sin_eea = [i for i, d in enumerate(otras) if d.mejor_eea is None]
    if sin_eea:
        assert min(sin_eea) == len(con_eea)
