"""Revisión del 19/10/2026 de la DECISIÓN 073 (bloque D): excluir los valores
que impidieron Chow y recalcular hace que la prueba se ejecute en la simulación.
"""

import json
from pathlib import Path

import pytest

from metis.core.etapa1.outliers import calcular_chow
from metis.services.analysis_service import simular_exclusion

REFERENCIA = json.loads(
    (
        Path(__file__).parents[1] / "core/pipeline/referencia_etapa1_alfa_005.json"
    ).read_text(encoding="utf-8")
)


@pytest.mark.unit
def test_al_excluir_los_negativos_la_simulacion_ejecuta_chow():
    caso = REFERENCIA["negativos_otro"]["entrada"]
    original = calcular_chow(caso["serie"], caso["tipo_variable"])
    indices = [v["indice"] for v in original.valores_no_validos]

    sim = simular_exclusion(
        serie=caso["serie"],
        anios=caso["timestamps"],
        tipo_variable=caso["tipo_variable"],
        cramer_particion="default",
        indices_excluidos=indices,
        etapas=[1],
    )

    (chow,) = sim["etapa1"]["atipicos"]
    assert chow["veredicto"] in ("aprobada", "rechazada")
    assert chow["valores_no_validos"] is None
    assert chow["explicacion"] is not None
