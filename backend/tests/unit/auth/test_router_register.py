"""
Tests unitarios de POST /auth/register — orquestación en router.py.

Patrón de mocking — precedente de repo, status pendiente de confirmar como
vinculante fuera de auth (ver decisions-log.md): mockear en el borde de la
unidad bajo test, no un nivel más abajo. Acá la unidad es register(), así
que se mockea metis.auth.router.send_verification_email directamente (no
aiosmtplib.send) — un cambio interno a cómo email.py arma el mensaje no
debe poder romper estos tests sin que haya un bug real de orquestación.
La sesión de BD (db: AsyncSession) también se mockea — estos tests no
abren conexión real, no son de integración.

NOTA: se importan nombres puntuales de metis.auth.router (register,
_pending_tokens) con `from metis.auth.router import ...`, nunca
`import metis.auth.router as router_module` ni `from metis.auth import
router`. metis/auth/__init__.py hace `from metis.auth.router import
router` (el APIRouter), lo que sobreescribe el atributo `router` del
paquete `metis.auth` con esa instancia — cualquier acceso vía atributo
de paquete (`metis.auth.router`) devuelve el APIRouter, no el submódulo.
Solo `from metis.auth.router import <nombre>` resuelve correctamente
contra sys.modules. Confirmado empíricamente durante el desarrollo de
este archivo — no es una suposición.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import aiosmtplib
import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from metis.auth.router import _pending_tokens, register
from metis.schemas.auth import RegisterRequest


def _body(email="legajo@ucc.edu.ar", password="password123", nombre="Test"):
    return RegisterRequest(email=email, password=password, nombre=nombre)


def _mock_db(commit_side_effect=None):
    """AsyncSession mockeada: pre-check SELECT no encuentra usuario existente."""
    db = MagicMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=result)
    db.add = MagicMock()
    db.commit = AsyncMock(side_effect=commit_side_effect)
    db.rollback = AsyncMock()
    return db


@pytest.fixture(autouse=True)
def _pending_tokens_aislado():
    # _pending_tokens es el mismo dict en memoria que muta router.py (ver
    # su comentario "LIMITACIÓN: dict en memoria de proceso") — se limpia
    # in-place antes y después de cada test para que no haya fugas entre
    # tests. No se reemplaza el dict (rebind), porque register()/verify()
    # capturaron la referencia original al importarla.
    _pending_tokens.clear()
    yield _pending_tokens
    _pending_tokens.clear()


@pytest.mark.unit
async def test_register_manda_mail_antes_que_add_y_commit():
    call_order = []
    db = _mock_db()
    db.add.side_effect = lambda *a, **k: call_order.append("add")
    db.commit.side_effect = lambda: call_order.append("commit")

    async def _fake_send(email, token):
        call_order.append("send_mail")

    with patch(
        "metis.auth.router.send_verification_email",
        new_callable=AsyncMock,
        side_effect=_fake_send,
    ):
        await register(_body(), db=db)

    assert call_order == ["send_mail", "add", "commit"]


@pytest.mark.unit
async def test_register_ok_registra_token_solo_tras_commit_exitoso():
    db = _mock_db()

    with patch(
        "metis.auth.router.send_verification_email", new_callable=AsyncMock
    ) as mock_send:
        response = await register(_body(), db=db)

    assert response == {
        "ok": True,
        "mensaje": "Cuenta creada. Revisá tu mail para verificar la dirección.",
    }
    mock_send.assert_awaited_once()
    token_enviado = mock_send.call_args[0][1]
    assert _pending_tokens == {token_enviado: "legajo@ucc.edu.ar"}
    db.add.assert_called_once()
    db.commit.assert_awaited_once()


@pytest.mark.unit
async def test_register_falla_smtpexception_no_toca_bd():
    db = _mock_db()

    with patch(
        "metis.auth.router.send_verification_email",
        new_callable=AsyncMock,
        side_effect=aiosmtplib.SMTPConnectError("conexión rechazada"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await register(_body(), db=db)

    assert exc_info.value.status_code == 500
    assert (
        exc_info.value.detail["error"]["codigo"] == "AUTH_VERIFICATION_EMAIL_FAILED"
    )
    db.add.assert_not_called()
    db.commit.assert_not_awaited()
    assert _pending_tokens == {}


@pytest.mark.unit
async def test_register_falla_runtimeerror_config_no_toca_bd():
    db = _mock_db()

    with patch(
        "metis.auth.router.send_verification_email",
        new_callable=AsyncMock,
        side_effect=RuntimeError("SMTP_HOST no configurado"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await register(_body(), db=db)

    assert exc_info.value.status_code == 500
    assert (
        exc_info.value.detail["error"]["codigo"] == "AUTH_VERIFICATION_EMAIL_FAILED"
    )
    db.add.assert_not_called()
    db.commit.assert_not_awaited()


@pytest.mark.unit
async def test_register_integrityerror_en_commit_mapea_a_email_already_registered():
    db = _mock_db(
        commit_side_effect=IntegrityError(None, None, Exception("duplicate key"))
    )

    with patch("metis.auth.router.send_verification_email", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc_info:
            await register(_body(), db=db)

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail["error"]["codigo"] == "AUTH_EMAIL_ALREADY_REGISTERED"
    )
    db.rollback.assert_awaited_once()
    assert _pending_tokens == {}


@pytest.mark.unit
async def test_register_race_concurrente_segundo_commit_falla_sin_excepcion_sin_capturar():
    """
    Dos registros concurrentes con el mismo email: ambos pasan el SELECT de
    pre-chequeo (ninguno ve al otro todavía) y ambos intentan mandar mail.
    Simulado como secuencia, no con asyncio real — alcanza para confirmar
    que la rama de excepción del segundo commit() responde como se espera,
    sin lock adicional (descartado por sobre-ingeniería para el volumen
    actual, ver docs/decisiones/).
    """
    db_primero = _mock_db()
    db_segundo = _mock_db(
        commit_side_effect=IntegrityError(None, None, Exception("duplicate key"))
    )

    with patch("metis.auth.router.send_verification_email", new_callable=AsyncMock):
        respuesta_primero = await register(_body(), db=db_primero)

        with pytest.raises(HTTPException) as exc_info:
            await register(_body(), db=db_segundo)

    assert respuesta_primero["ok"] is True
    assert len(_pending_tokens) == 1

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail["error"]["codigo"] == "AUTH_EMAIL_ALREADY_REGISTERED"
    )
    db_segundo.rollback.assert_awaited_once()
    db_primero.commit.assert_awaited_once()
