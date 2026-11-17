"""
Tests unitarios de POST /auth/forgot-password y /auth/reset-password (DECISIÓN 085).

Mismo patrón que test_router_register.py: se mockea en el borde de la unidad (los helpers de
tokens y el envío del mail) y la sesión de BD; nada abre conexión real. Los nombres se importan
con `from metis.auth.router import ...` por la razón que explica el docstring de ese archivo.
"""

import ssl
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import aiosmtplib
import bcrypt
import pytest
from fastapi import BackgroundTasks, HTTPException
from pydantic import ValidationError

from metis.auth.router import (
    _MENSAJE_FORGOT,
    _mandar_mail_reseteo,
    forgot_password,
    reset_password,
    router,
)
from metis.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest


def _db_con_usuario(user):
    db = MagicMock()
    resultado = MagicMock()
    resultado.scalar_one_or_none.return_value = user
    db.execute = AsyncMock(return_value=resultado)
    db.commit = AsyncMock()
    return db


def _usuario(**kw):
    user = MagicMock()
    user.id = kw.get("id", uuid.uuid4())
    user.email = kw.get("email", "legajo@ucc.edu.ar")
    user.password_hash = "hash-viejo"
    user.email_verified = kw.get("email_verified", False)
    return user


# ---------------------------------------------------------------- forgot-password


@pytest.mark.unit
async def test_forgot_con_cuenta_pide_token_y_encola_el_mail():
    user = _usuario()
    bg = BackgroundTasks()
    with patch(
        "metis.auth.router.issue_reset_token", new_callable=AsyncMock
    ) as mock_issue:
        mock_issue.return_value = "tok-123"
        r = await forgot_password(
            ForgotPasswordRequest(email=user.email), bg, _db_con_usuario(user)
        )

    mock_issue.assert_awaited_once()
    assert mock_issue.call_args.args[1] == user.id
    assert len(bg.tasks) == 1
    assert bg.tasks[0].func is _mandar_mail_reseteo
    assert bg.tasks[0].args == (user.email, "tok-123")
    assert r == {"ok": True, "mensaje": _MENSAJE_FORGOT}


@pytest.mark.unit
async def test_forgot_con_email_inexistente_responde_lo_mismo_y_no_hace_nada():
    bg = BackgroundTasks()
    db = _db_con_usuario(None)
    with patch(
        "metis.auth.router.issue_reset_token", new_callable=AsyncMock
    ) as mock_issue:
        r = await forgot_password(
            ForgotPasswordRequest(email="nadie@ucc.edu.ar"), bg, db
        )

    mock_issue.assert_not_awaited()
    assert bg.tasks == []
    db.commit.assert_not_awaited()
    # Misma respuesta que con una cuenta existente: no filtra qué mails tienen cuenta.
    assert r == {"ok": True, "mensaje": _MENSAJE_FORGOT}


@pytest.mark.unit
async def test_forgot_dentro_del_cooldown_responde_igual_sin_mandar_otro_mail():
    user = _usuario()
    bg = BackgroundTasks()
    with patch(
        "metis.auth.router.issue_reset_token", new_callable=AsyncMock
    ) as mock_issue:
        mock_issue.return_value = None  # ya se pidió uno hace menos de RESET_COOLDOWN
        r = await forgot_password(
            ForgotPasswordRequest(email=user.email), bg, _db_con_usuario(user)
        )

    assert bg.tasks == []
    assert r == {"ok": True, "mensaje": _MENSAJE_FORGOT}


@pytest.mark.unit
async def test_mandar_mail_reseteo_pasa_la_vigencia_en_minutos():
    with patch(
        "metis.auth.router.send_password_reset_email", new_callable=AsyncMock
    ) as mock_send:
        await _mandar_mail_reseteo("legajo@ucc.edu.ar", "tok")

    mock_send.assert_awaited_once_with("legajo@ucc.edu.ar", "tok", 60)


@pytest.mark.unit
@pytest.mark.parametrize(
    "error",
    [
        ssl.SSLCertVerificationError("hostname mismatch"),
        TimeoutError("timed out"),
        aiosmtplib.SMTPConnectError("conexión rechazada"),
        RuntimeError("SMTP sin configurar"),
    ],
    ids=["ssl", "timeout", "smtp", "config"],
)
async def test_mandar_mail_reseteo_traga_los_fallos_de_envio(error):
    # Si el envío fallara como error de la API, la respuesta distinguiría las cuentas que existen
    # de las que no. Solo se registra en el log.
    with patch(
        "metis.auth.router.send_password_reset_email",
        new_callable=AsyncMock,
        side_effect=error,
    ):
        await _mandar_mail_reseteo("legajo@ucc.edu.ar", "tok")  # no lanza


# ---------------------------------------------------------------- reset-password


@pytest.mark.unit
async def test_reset_con_token_valido_cambia_la_clave_verifica_y_cierra_los_links():
    user = _usuario(email_verified=False)
    db = _db_con_usuario(user)
    with (
        patch(
            "metis.auth.router.consume_reset_token", new_callable=AsyncMock
        ) as mock_consume,
        patch(
            "metis.auth.router.invalidate_reset_tokens", new_callable=AsyncMock
        ) as mock_invalidate,
    ):
        mock_consume.return_value = user.id
        r = await reset_password(
            ResetPasswordRequest(token="tok", password="nueva-clave-1"), db
        )

    assert r == {"ok": True}
    assert bcrypt.checkpw(b"nueva-clave-1", user.password_hash.encode())
    assert user.email_verified is True
    mock_invalidate.assert_awaited_once()
    assert mock_invalidate.call_args.args[1] == user.id
    db.commit.assert_awaited_once()


@pytest.mark.unit
async def test_reset_con_token_invalido_responde_400_con_codigo_y_no_toca_nada():
    db = _db_con_usuario(_usuario())
    with patch(
        "metis.auth.router.consume_reset_token", new_callable=AsyncMock
    ) as mock_consume:
        mock_consume.return_value = None
        with pytest.raises(HTTPException) as exc:
            await reset_password(
                ResetPasswordRequest(token="malo", password="nueva-clave-1"), db
            )

    assert exc.value.status_code == 400
    assert exc.value.detail["error"]["codigo"] == "AUTH_RESET_TOKEN_INVALID"
    db.execute.assert_not_awaited()
    db.commit.assert_not_awaited()


@pytest.mark.unit
async def test_reset_con_usuario_borrado_responde_404_sin_commit():
    db = _db_con_usuario(None)
    with patch(
        "metis.auth.router.consume_reset_token", new_callable=AsyncMock
    ) as mock_consume:
        mock_consume.return_value = uuid.uuid4()
        with pytest.raises(HTTPException) as exc:
            await reset_password(
                ResetPasswordRequest(token="tok", password="nueva-clave-1"), db
            )

    assert exc.value.status_code == 404
    assert exc.value.detail["error"]["codigo"] == "AUTH_USER_NOT_FOUND"
    db.commit.assert_not_awaited()


# ---------------------------------------------------------------- schemas y rutas


@pytest.mark.unit
def test_reset_exige_al_menos_8_caracteres_como_el_registro():
    with pytest.raises(ValidationError):
        ResetPasswordRequest(token="tok", password="corta")
    assert ResetPasswordRequest(token="tok", password="12345678").password == "12345678"


@pytest.mark.unit
def test_forgot_rechaza_un_email_mal_formado_pero_acepta_cualquier_dominio():
    with pytest.raises(ValidationError):
        ForgotPasswordRequest(email="no-es-un-mail")
    # No se restringe a @ucc.edu.ar: la respuesta es igual exista o no la cuenta.
    assert ForgotPasswordRequest(email="alguien@gmail.com").email == "alguien@gmail.com"


@pytest.mark.unit
def test_las_rutas_estan_registradas_sin_sesion():
    rutas = {r.path: r for r in router.routes}
    for path in ("/api/v1/auth/forgot-password", "/api/v1/auth/reset-password"):
        assert path in rutas
        assert rutas[path].methods == {"POST"}
        # Sin get_current_user: quien olvidó la clave no tiene sesión.
        assert all(
            d.call.__name__ != "get_current_user"
            for d in rutas[path].dependant.dependencies
        )
