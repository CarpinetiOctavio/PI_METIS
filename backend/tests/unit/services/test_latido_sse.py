"""Latido SSE durante las pausas del stream (DECISIÓN 083, addendum del 04/11/2026).

Un proxy intermedio corta una conexión sin tráfico (Cloudflare, a los 100 s). Mientras el stream espera la
decisión del usuario manda un comentario SSE cada INTERVALO_LATIDO.
"""

import asyncio
import uuid

import pytest

from metis.services import analysis_service, session_store
from metis.services.analysis_service import LATIDO_SSE, _esperar_decision_con_latido

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def intervalo_corto(monkeypatch):
    monkeypatch.setattr(analysis_service, "INTERVALO_LATIDO", 0.05)
    session_store._sessions.clear()
    yield
    session_store._sessions.clear()


async def _consumir(session_id: str) -> list:
    return [item async for item in _esperar_decision_con_latido(session_id)]


async def test_latido_es_un_comentario_sse():
    # Una línea que empieza con ":" y un blank line: ningún cliente SSE la entrega como evento.
    assert LATIDO_SSE.startswith(":")
    assert LATIDO_SSE.endswith("\n\n")
    assert "event:" not in LATIDO_SSE and "data:" not in LATIDO_SSE


async def test_manda_latidos_mientras_espera_y_termina_con_true_al_decidir():
    session_id = str(uuid.uuid4())
    session_store.create_session(session_id)

    async def decidir_tarde():
        await asyncio.sleep(0.18)
        session_store.resolve_session(session_id, {"decision": "aceptar"})

    tarea = asyncio.create_task(decidir_tarde())
    items = await _consumir(session_id)
    await tarea

    assert items[-1] is True
    latidos = items[:-1]
    assert len(latidos) >= 2
    assert all(x == LATIDO_SSE for x in latidos)


async def test_decision_previa_termina_sin_latidos():
    session_id = str(uuid.uuid4())
    session_store.create_session(session_id)
    session_store.resolve_session(session_id, {"decision": "aceptar"})

    assert await _consumir(session_id) == [True]


async def test_sesion_inexistente_termina_con_false_sin_latidos():
    assert await _consumir(str(uuid.uuid4())) == [False]


async def test_timeout_de_la_sesion_termina_con_false_despues_de_los_latidos(
    monkeypatch,
):
    monkeypatch.setattr(session_store, "SESSION_TIMEOUT", 0.17)
    session_id = str(uuid.uuid4())
    session_store.create_session(session_id)

    items = await _consumir(session_id)

    assert items[-1] is False
    assert len(items) >= 2
    assert all(x == LATIDO_SSE for x in items[:-1])


async def test_cerrar_el_generador_cancela_la_espera():
    session_id = str(uuid.uuid4())
    session_store.create_session(session_id)
    tareas_antes = asyncio.all_tasks()

    gen = _esperar_decision_con_latido(session_id)
    assert await gen.__anext__() == LATIDO_SSE
    await gen.aclose()
    await asyncio.sleep(0.05)  # deja correr la cancelación pendiente

    huerfanas = [t for t in asyncio.all_tasks() - tareas_antes if not t.done()]
    assert huerfanas == [], "la espera de la decisión quedó viva tras cerrar el stream"
