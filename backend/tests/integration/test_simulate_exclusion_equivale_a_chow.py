"""DECISIÓN 071 — regresión 2: excluir el atípico de Chow con simulate-exclusion da
el mismo resultado de Etapa 1 que rechazarlo en el flujo de Chow del stream.

Prueba que no hay dos criterios para "sacar un punto" sin refactorizar el flujo de
Chow (decisión de Kevin del 20/09: ese flujo no se toca). Se comparan estadísticos,
veredictos, niveles y nivel_confianza, NO los warnings: el flujo de Chow arrastra
desde la primera pasada los warnings de agregación (CODIGOS_WARNING_AGREGACION) y
un endpoint sin estado no los tiene.
"""

import pytest

from metis.core.pipeline import ejecutar_etapa1
from metis.core.validacion.parser import parse_file, parsear_timestamps
from metis.services.analysis_service import (
    _extraer_indice_atipico,
    registrar_outlier_decision,
    simular_exclusion,
)
from tests.integration._sse_helpers import parse_sse, run_stream

GRUPOS = ("independencia", "homogeneidad", "tendencia", "atipicos")
CAMPOS = ("prueba", "estadistico", "valor_critico", "veredicto", "n1", "n2")
NIVELES = ("nivel_independencia", "nivel_homogeneidad", "nivel_confianza")


def _csv(celda_vacia: bool) -> bytes:
    filas = ["fecha,caudal"]
    for i in range(20):
        anio = 2000 + i
        if celda_vacia and anio == 2004:
            valor = ""
        elif anio == 2012:
            valor = "5000"  # atípico
        else:
            valor = f"{60 + (i * 7) % 40}"
        filas.append(f"{anio}-01-01,{valor}")
    return ("\n".join(filas) + "\n").encode()


def _resumen(etapa1: dict) -> dict:
    return {
        "pruebas": [{c: t[c] for c in CAMPOS} for g in GRUPOS for t in etapa1[g]],
        **{n: etapa1[n] for n in NIVELES},
    }


@pytest.mark.integration
@pytest.mark.parametrize("celda_vacia", [False, True], ids=["completa", "con-celda-vacia"])
async def test_excluir_el_atipico_equivale_a_rechazarlo_en_el_flujo_de_chow(celda_vacia):
    contenido = _csv(celda_vacia)

    # Primera pasada, igual que la hace el stream antes de pausar (el evento
    # result_etapa1 sale una sola vez, al final, ya sin el atípico).
    parsed = parse_file(contenido, "serie.csv", "fecha", "caudal")
    primera = ejecutar_etapa1(
        serie=parsed.serie,
        tipo_variable="otro",
        resolucion_temporal=parsed.resolucion_temporal,
        timestamps=parsed.timestamps,
    )
    indice = _extraer_indice_atipico(primera)
    assert indice is not None

    gen, session_id = run_stream(contenido)
    final = None
    async for evento in gen:
        tipo, data = parse_sse(evento)
        if tipo == "outlier_detected":
            await registrar_outlier_decision(
                session_id=session_id,
                decision="rechazar",
                dato_atipico=data["valor_atipico"],
                db=None,
            )
        elif tipo == "result_etapa1":
            final = data

    assert final["datos"]["indice_atipico"] is None  # se rechazó: ya no está

    simulado = simular_exclusion(
        serie=list(primera.serie_efectiva),
        anios=[ts.year for ts in parsear_timestamps(primera.timestamps_efectivos)],
        tipo_variable="otro",
        cramer_particion="default",
        indices_excluidos=[indice],
        etapas=[1],
    )

    assert _resumen(simulado["etapa1"]) == _resumen(final)
    assert simulado["etapa1"]["datos"]["serie_efectiva"] == final["datos"]["serie_efectiva"]
