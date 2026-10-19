"""DECISIÓN 078 — el α elegido llega a las ocho pruebas del stream y se conserva en
la segunda pasada de la Etapa 1, la que corre después de rechazar un atípico de
Chow. Esa segunda llamada repite los parámetros a mano, y el mismo defecto ya
ocurrió con `mes_inicio_anio` (hallazgo V2): sin pasarle `alfa`, caía al 5 %.
"""

import numpy as np
import pytest

from metis.core.etapa1.significancia import z_bilateral
from metis.services.analysis_service import registrar_outlier_decision
from tests.integration._sse_helpers import parse_sse, run_stream

GRUPOS = ("independencia", "homogeneidad", "tendencia", "atipicos")


def _csv_con_atipico() -> bytes:
    filas = ["fecha,caudal"]
    for i in range(20):
        valor = "5000" if i == 12 else f"{60 + (i * 7) % 40}"
        filas.append(f"{2000 + i}-01-01,{valor}")
    return ("\n".join(filas) + "\n").encode()


async def _final(alfa: float, decision: str) -> tuple[dict, list[str]]:
    gen, session_id = run_stream(_csv_con_atipico(), alfa=alfa)
    final, tipos = None, []
    async for evento in gen:
        tipo, data = parse_sse(evento)
        tipos.append(tipo)
        if tipo == "outlier_detected":
            await registrar_outlier_decision(
                session_id=session_id, decision=decision, dato_atipico=0, db=None
            )
        elif tipo == "result_etapa1":
            final = data
    return final, tipos


@pytest.mark.integration
@pytest.mark.parametrize("decision", ["rechazar", "aceptar"])
async def test_el_alfa_llega_a_las_ocho_pruebas_y_sobrevive_al_rechazo(decision):
    final, tipos = await _final(0.10, decision)

    assert "outlier_detected" in tipos
    assert final["alfa"] == 0.10
    pruebas = [t for g in GRUPOS for t in final[g]]
    assert len(pruebas) == 8
    for t in pruebas:
        if t["prueba"] == "helmert" or t["explicacion"] is None:
            continue
        assert t["explicacion"]["terminos"]["alfa"] == 0.10, t["prueba"]
    wald = next(t for t in pruebas if t["prueba"] == "wald_wolfowitz")
    assert wald["valor_critico"] == z_bilateral(0.10)


@pytest.mark.integration
async def test_sin_alfa_el_stream_corre_con_5_por_ciento():
    # Serie sin atípicos (la de test_persistencia.py): el stream no pausa.
    serie = np.random.default_rng(seed=9).uniform(10, 100, size=50).tolist()
    filas = [f"{1970 + i},{v}" for i, v in enumerate(serie)]
    contenido = ("anio,caudal\n" + "\n".join(filas) + "\n").encode()
    gen, _ = run_stream(contenido, columna_x="anio")
    final = next(
        d for t, d in [parse_sse(e) async for e in gen] if t == "result_etapa1"
    )

    assert final["alfa"] == 0.05
    wald = next(t for t in final["independencia"] if t["prueba"] == "wald_wolfowitz")
    assert wald["valor_critico"] == z_bilateral(0.05)
