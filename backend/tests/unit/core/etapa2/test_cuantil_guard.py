"""
Bloque 0.3 del plan de Etapa 2 — vuelve ejecutable la afirmación de que el
guard p ∈ (0, 1) está presente en las 13 distribuciones (Fase 4.5, ver
.claude/rules/sprint.md).

Descubre los módulos recorriendo _DISTRIBUCIONES de pipeline_etapa2.py, no
una lista hardcodeada acá — así una distribución nueva entra al test sola,
sin que la afirmación pueda desincronizarse en silencio como ya pasó una vez.
"""

import pytest

from metis.core.pipeline.pipeline_etapa2 import _DISTRIBUCIONES

VALORES_P_INVALIDOS = [0.0, 1.0, -0.1, 1.1]


@pytest.mark.unit
@pytest.mark.parametrize(
    "nombre,modulo", _DISTRIBUCIONES, ids=[n for n, _ in _DISTRIBUCIONES]
)
@pytest.mark.parametrize("p_invalido", VALORES_P_INVALIDOS)
def test_cuantil_rechaza_p_fuera_de_0_1(nombre, modulo, p_invalido):
    with pytest.raises(ValueError):
        modulo.cuantil(p_invalido, {})
