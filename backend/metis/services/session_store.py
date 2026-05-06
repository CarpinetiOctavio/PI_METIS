import asyncio

_store: dict[str, asyncio.Event] = {}
_decisions: dict[str, str] = {}

SESSION_TIMEOUT = 300  # segundos


def create_session(session_id: str) -> None:
    _store[session_id] = asyncio.Event()


async def wait_for_decision(session_id: str) -> bool:
    """Espera hasta que el usuario tome una decisión o se agote el timeout.

    Returns:
        True si se recibió una decisión dentro del timeout.
        False si se agotó el timeout.
    """
    event = _store.get(session_id)
    if event is None:
        return False
    try:
        await asyncio.wait_for(event.wait(), timeout=SESSION_TIMEOUT)
        return True
    except asyncio.TimeoutError:
        return False


def resolve_session(session_id: str, decision: str) -> None:
    """Registra la decisión y desbloquea el stream en espera."""
    _decisions[session_id] = decision
    event = _store.get(session_id)
    if event is not None:
        event.set()


def get_decision(session_id: str) -> str | None:
    return _decisions.get(session_id)


def remove_session(session_id: str) -> None:
    _store.pop(session_id, None)
    _decisions.pop(session_id, None)
