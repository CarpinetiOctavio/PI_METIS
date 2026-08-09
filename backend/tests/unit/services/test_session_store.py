"""
Tests unitarios de session_store.py (DECISIÓN 053) — SessionState con TTL,
reemplazo de los dos diccionarios sueltos (_store/_decisions) que existían
antes de Etapa 2.
"""

import asyncio

import pytest

from metis.services import session_store


@pytest.fixture(autouse=True)
def _limpiar_sessions():
    """session_store guarda estado en un dict a nivel de módulo — sin este
    fixture, una sesión creada en un test contamina el siguiente."""
    session_store._sessions.clear()
    yield
    session_store._sessions.clear()


@pytest.mark.unit
def test_create_session_registra_sessionstate_con_event_limpio():
    session_store.create_session("s1")

    estado = session_store.get_session("s1")
    assert estado is not None
    assert isinstance(estado.event, asyncio.Event)
    assert not estado.event.is_set()
    assert estado.decision is None
    assert estado.serie is None
    assert estado.tiene_ceros is False
    assert estado.etapa2 is None


@pytest.mark.unit
async def test_resolve_session_guarda_decision_como_dict_no_str():
    session_store.create_session("s1")

    session_store.resolve_session("s1", {"decision": "rechazar"})

    assert session_store.get_decision("s1") == {"decision": "rechazar"}


@pytest.mark.unit
async def test_resolve_session_desbloquea_wait_for_decision():
    session_store.create_session("s1")

    async def resolver_pronto():
        await asyncio.sleep(0)
        session_store.resolve_session("s1", {"decision": "aceptar"})

    resultado, _ = await asyncio.gather(
        session_store.wait_for_decision("s1"), resolver_pronto()
    )

    assert resultado is True


@pytest.mark.unit
async def test_wait_for_decision_sesion_inexistente_retorna_false():
    resultado = await session_store.wait_for_decision("no-existe")

    assert resultado is False


@pytest.mark.unit
def test_get_decision_sesion_inexistente_retorna_none():
    assert session_store.get_decision("no-existe") is None


@pytest.mark.unit
def test_remove_session_limpia_la_entrada():
    session_store.create_session("s1")
    session_store.resolve_session("s1", {"decision": "aceptar"})

    session_store.remove_session("s1")

    assert session_store.get_session("s1") is None
    assert session_store.get_decision("s1") is None


@pytest.mark.unit
def test_session_guarda_serie_tiene_ceros_y_etapa2_antes_de_pausar():
    """DECISIÓN 053 — el stream escribe estos tres campos directo sobre el
    SessionState antes de emitir result_etapa2_ranking, para que
    distribution-decision no tenga que reajustar las 13 distribuciones."""
    session_store.create_session("s1")
    estado = session_store.get_session("s1")

    estado.serie = [10.0, 20.0, 30.0]
    estado.tiene_ceros = False
    estado.etapa2 = "placeholder-etapa2-result"  # tipo real: Etapa2Result

    estado_leido = session_store.get_session("s1")
    assert estado_leido.serie == [10.0, 20.0, 30.0]
    assert estado_leido.etapa2 == "placeholder-etapa2-result"


@pytest.mark.unit
def test_sweep_expired_descarta_sesiones_vencidas_sin_remove_session_explicito():
    session_store.create_session("vieja")
    session_store._sessions["vieja"].created_at -= session_store.SESSION_TIMEOUT + 1

    session_store.create_session("nueva")

    # sweep_expired() corre al principio de create_session("nueva") — la
    # sesión vieja ya debería estar afuera sin que nadie llame remove_session().
    assert session_store.get_session("vieja") is None
    assert session_store.get_session("nueva") is not None


@pytest.mark.unit
def test_sweep_expired_no_descarta_sesiones_recientes():
    session_store.create_session("reciente")

    session_store.sweep_expired()

    assert session_store.get_session("reciente") is not None
