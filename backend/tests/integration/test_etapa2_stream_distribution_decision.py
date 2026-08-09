"""
Primer test de tests/integration/ (Bloque A6 del plan de implementación de
Etapa 2 — el directorio existía vacío desde feature/services-sse).

Corre stream_analysis() de punta a punta con etapas=[1, 2] sobre una serie
de fixture, consume los eventos SSE en el orden real, manda la decisión de
distribución a mitad de camino (igual que haría el cliente real vía
POST /analysis/distribution-decision) y verifica que el stream se
desbloquea solo y termina con result_etapa2_eventos + complete.

CU-02 (anónimo, user_id=None): no persiste, así que no necesita una BD de
test real — es la forma más barata de probar el cableado nuevo de punta a
punta. La persistencia real (CU-01) queda para un test de integración
aparte, no es lo que este bloque "estrena".
"""

import json
import uuid

import numpy as np
import pytest

from metis.services import session_store
from metis.services.analysis_service import (
    registrar_distribution_decision,
    stream_analysis,
)

# Misma serie que SERIE_VALIDADA en test_pipeline_etapa1.py/test_full_pipeline.py
# — numpy seed=9, uniform(10, 100), n=50. Todas las pruebas de Etapa 1
# aprueban sin warnings y sin atípico de Chow, así que este test ejercita
# únicamente la pausa nueva de Etapa 2, no la de Chow (ya cubierta en
# tests/unit/services/test_analysis_service.py).
_rng = np.random.default_rng(seed=9)
_SERIE_VALIDADA = _rng.uniform(10, 100, size=50).tolist()


def _csv_de_serie_valida() -> bytes:
    filas = [f"{1970 + i},{valor}" for i, valor in enumerate(_SERIE_VALIDADA)]
    return ("anio,caudal\n" + "\n".join(filas) + "\n").encode()


def _parse_sse(evento: str) -> tuple[str, dict]:
    lineas = evento.strip("\n").split("\n")
    tipo = lineas[0].removeprefix("event: ")
    data = json.loads(lineas[1].removeprefix("data: "))
    return tipo, data


@pytest.fixture(autouse=True)
def _limpiar_sessions():
    session_store._sessions.clear()
    yield
    session_store._sessions.clear()


@pytest.mark.integration
async def test_stream_con_etapas_1_2_pausa_en_ranking_y_termina_con_eventos():
    session_id = str(uuid.uuid4())

    gen = stream_analysis(
        content=_csv_de_serie_valida(),
        filename="serie.csv",
        columna_x="anio",
        columna_y="caudal",
        tipo_variable="otro",
        modo="experto",
        cramer_particion="default",
        etapas=[1, 2],
        session_id=session_id,
        user_id=None,
        db=None,
    )

    tipos_recibidos: list[str] = []
    resultado_decision = None

    async for evento_crudo in gen:
        tipo, data = _parse_sse(evento_crudo)
        tipos_recibidos.append(tipo)

        if tipo == "result_etapa2_ranking":
            # El ranking real ya está serializado acá — elegimos la primera
            # distribución que efectivamente ajustó (mejor_eea no nulo),
            # igual que haría un usuario real desde RankingPage.
            elegida = next(
                d for d in data["ranking"] if d["mejor_eea"] is not None
            )
            resultado_decision = await registrar_distribution_decision(
                session_id=session_id,
                distribucion=elegida["distribucion"],
                metodo=elegida["mejor_metodo"],
                periodos_retorno=[2, 5, 10, 25, 50, 100, 200, 500],
            )

    assert resultado_decision == {"ok": True, "pipeline_continua": True}

    # Secuencia real, en orden: Etapa 1 completa, luego el progress de
    # Etapa 2, el ranking (donde pausó), los eventos de diseño y el cierre.
    assert "result_etapa1" in tipos_recibidos
    assert "result_etapa2_ranking" in tipos_recibidos
    assert "result_etapa2_eventos" in tipos_recibidos
    assert tipos_recibidos[-1] == "complete"
    assert tipos_recibidos.index("result_etapa2_ranking") < tipos_recibidos.index(
        "result_etapa2_eventos"
    )
    assert tipos_recibidos.index("result_etapa1") < tipos_recibidos.index(
        "result_etapa2_ranking"
    )

    # Sesión limpiada al terminar (finally de stream_analysis).
    assert session_store.get_session(session_id) is None


@pytest.mark.integration
async def test_result_etapa2_eventos_trae_los_periodos_retorno_pedidos():
    session_id = str(uuid.uuid4())

    gen = stream_analysis(
        content=_csv_de_serie_valida(),
        filename="serie.csv",
        columna_x="anio",
        columna_y="caudal",
        tipo_variable="otro",
        modo="experto",
        cramer_particion="default",
        etapas=[1, 2],
        session_id=session_id,
        user_id=None,
        db=None,
    )

    periodos_pedidos = [2, 5, 10, 25, 50, 100, 200, 500]
    payload_eventos = None

    async for evento_crudo in gen:
        tipo, data = _parse_sse(evento_crudo)

        if tipo == "result_etapa2_ranking":
            elegida = next(
                d for d in data["ranking"] if d["mejor_eea"] is not None
            )
            await registrar_distribution_decision(
                session_id=session_id,
                distribucion=elegida["distribucion"],
                metodo=elegida["mejor_metodo"],
                periodos_retorno=periodos_pedidos,
            )
        elif tipo == "result_etapa2_eventos":
            payload_eventos = data

    assert payload_eventos is not None
    assert [
        e["periodo_retorno"] for e in payload_eventos["eventos_diseno"]
    ] == periodos_pedidos
    # Serie sin ceros y distribución con parámetros ajustados -> ningún
    # evento debería quedar en None para este fixture.
    assert all(e["valor"] is not None for e in payload_eventos["eventos_diseno"])


@pytest.mark.integration
async def test_etapas_1_solo_no_pausa_en_etapa_2():
    """Con etapas=[1] el comportamiento debe ser exactamente el de antes
    de esta decisión — el criterio de hecho explícito del Bloque A."""
    session_id = str(uuid.uuid4())

    gen = stream_analysis(
        content=_csv_de_serie_valida(),
        filename="serie.csv",
        columna_x="anio",
        columna_y="caudal",
        tipo_variable="otro",
        modo="experto",
        cramer_particion="default",
        etapas=[1],
        session_id=session_id,
        user_id=None,
        db=None,
    )

    tipos_recibidos = [_parse_sse(e)[0] async for e in gen]

    assert "result_etapa1" in tipos_recibidos
    assert "result_etapa2_ranking" not in tipos_recibidos
    assert "result_etapa2_eventos" not in tipos_recibidos
    assert tipos_recibidos[-1] == "complete"
