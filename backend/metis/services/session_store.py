import asyncio
import time
from dataclasses import dataclass, field

from metis.core.etapa2.types import Etapa2Result

SESSION_TIMEOUT = 300  # segundos


@dataclass
class SessionState:
    """Estado de una sesión de análisis activa (DECISIÓN 053).

    `decision` es un payload de dict, no un string: Chow manda
    {"decision": "rechazar"|"aceptar"}, la selección de distribución manda
    el payload completo de distribution-decision. Un solo mecanismo para
    las dos pausas del stream.

    `serie`, `tiene_ceros` y `etapa2` se guardan antes de pausar en
    result_etapa2_ranking, para que distribution-decision no tenga que
    reajustar las 13 distribuciones de nuevo.
    """

    event: asyncio.Event
    decision: dict | None = None
    serie: list[float] | None = None
    tiene_ceros: bool = False
    etapa2: Etapa2Result | None = None
    created_at: float = field(default_factory=time.monotonic)


_sessions: dict[str, SessionState] = {}


def sweep_expired() -> None:
    """Descarta sesiones que superaron SESSION_TIMEOUT.

    Barrido perezoso, sin tarea de fondo: se llama al principio de
    create_session(), no en un asyncio.create_task() que podría quedar
    colgado si el proceso se reinicia a mitad de una tarea programada.
    Antes de DECISIÓN 053 una sesión sin `finally` que corriera quedaba
    para siempre; ahora cada entrada carga la serie completa y un
    Etapa2Result de 13 distribuciones, así que el costo de no limpiarla ya
    no es despreciable.
    """
    ahora = time.monotonic()
    vencidas = [
        session_id
        for session_id, estado in _sessions.items()
        if ahora - estado.created_at > SESSION_TIMEOUT
    ]
    for session_id in vencidas:
        _sessions.pop(session_id, None)


def create_session(session_id: str) -> None:
    sweep_expired()
    _sessions[session_id] = SessionState(event=asyncio.Event())


def get_session(session_id: str) -> SessionState | None:
    return _sessions.get(session_id)


async def wait_for_decision(session_id: str) -> bool:
    """Espera hasta que el usuario tome una decisión o se agote el timeout.

    Returns:
        True si se recibió una decisión dentro del timeout.
        False si se agotó el timeout.
    """
    estado = _sessions.get(session_id)
    if estado is None:
        return False
    try:
        await asyncio.wait_for(estado.event.wait(), timeout=SESSION_TIMEOUT)
        return True
    except asyncio.TimeoutError:
        return False


def resolve_session(session_id: str, decision: dict) -> None:
    """Registra la decisión y desbloquea el stream en espera."""
    estado = _sessions.get(session_id)
    if estado is not None:
        estado.decision = decision
        estado.event.set()


def get_decision(session_id: str) -> dict | None:
    estado = _sessions.get(session_id)
    return estado.decision if estado else None


def remove_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
