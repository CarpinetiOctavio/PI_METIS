"""
Carga ANUAL con una celda de valor vacía + atípico de Chow rechazado por el
usuario (docs/auditoria/hallazgos/hallazgo-timestamps-desalineados.md).

Antes del fix, `serie_efectiva` salía sin el faltante y `timestamps_efectivos`
con todas las fechas: el índice de Chow (calculado sobre la serie sin el hueco)
se aplicaba a timestamps que ya no le correspondían, así que rechazar el
atípico borraba el valor correcto con el AÑO equivocado, y todas las etiquetas
posteriores al faltante quedaban corridas un año.
"""

import pytest

from metis.services.analysis_service import registrar_outlier_decision
from tests.integration._sse_helpers import parse_sse, run_stream


def _csv_anual_con_celda_vacia() -> bytes:
    filas = ["fecha,caudal"]
    for i in range(15):
        anio = 2000 + i
        if anio == 2003:
            valor = ""  # celda vacía
        elif anio == 2010:
            valor = "5000"  # atípico
        else:
            valor = f"{60 + (i * 7) % 40}"
        filas.append(f"{anio}-01-01,{valor}")
    return ("\n".join(filas) + "\n").encode()


@pytest.mark.integration
async def test_rechazar_atipico_con_celda_vacia_borra_el_anio_correcto():
    gen, session_id = run_stream(_csv_anual_con_celda_vacia())

    primer_resultado = None
    payload_final = None
    async for evento_crudo in gen:
        tipo, data = parse_sse(evento_crudo)
        if tipo == "outlier_detected":
            await registrar_outlier_decision(
                session_id=session_id,
                decision="rechazar",
                dato_atipico=data["valor_atipico"],
                db=None,
            )
        elif tipo == "result_etapa1":
            if primer_resultado is None:
                primer_resultado = data
            payload_final = data

    assert payload_final is not None
    datos = payload_final["datos"]

    # 15 años - 1 celda vacía (2003) - 1 atípico rechazado (2010) = 13.
    assert len(datos["serie_efectiva"]) == len(datos["timestamps_efectivos"]) == 13
    anios = [t["anio"] for t in datos["timestamps_efectivos"]]
    assert anios == [a for a in range(2000, 2015) if a not in (2003, 2010)]
    # Se borró el atípico, no otro valor.
    assert max(datos["serie_efectiva"]) < 1000.0
